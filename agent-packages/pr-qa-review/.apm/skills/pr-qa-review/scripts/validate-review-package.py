#!/usr/bin/env python3
"""Validate the durable state and artifacts produced by pr-qa-review."""

import argparse
import json
import re
import struct
import sys
from pathlib import Path, PurePosixPath


OID_PATTERN = re.compile(r"^[0-9a-fA-F]{40,64}$")
TERMINAL_CHECK_STATUSES = {"satisfied", "denied", "unavailable", "not_applicable"}
TERMINAL_REVIEW_STATUSES = {"complete", "limited"}
DISCOVERY_GATE_STATES = {"AWAIT_ACCESS_PERMISSION", "AWAIT_CAPABILITY_INSTALL_PERMISSION"}
CAPABILITY_DISCOVERY_SOURCES = {
    "repository-native",
    "harness-tools",
    "local-executables",
    "local-runtimes",
}
EXECUTION_SURFACES = {
    "static-read",
    "shell",
    "network",
    "browser",
    "scanner",
    "runtime",
    "deployment",
    "mutation",
}
OWNER_BOUNDARIES = {"main-thread", "enforced", "inherited"}
EVIDENCE_PROFILES = {
    "web-ui": {
        "entry-wide",
        "changed-wide",
        "entry-narrow",
        "changed-narrow",
        "console",
        "network",
        "accessibility",
        "keyboard",
    }
}


def validate_owner_binding(check, errors):
    check_id = check.get("id", "<unnamed>")
    execution_surface = check.get("execution_surface")
    owner_boundary = check.get("owner_boundary")
    owner = check.get("owner")

    if execution_surface not in EXECUTION_SURFACES:
        errors.append(f"check {check_id} has invalid execution surface: {execution_surface!r}")
    if owner_boundary not in OWNER_BOUNDARIES:
        errors.append(f"check {check_id} has invalid owner boundary: {owner_boundary!r}")
        return
    if owner == "root":
        if owner_boundary != "main-thread":
            errors.append(f"root-owned check {check_id} must use the main-thread boundary")
        return
    if owner_boundary == "main-thread":
        errors.append(f"leaf-owned check {check_id} cannot use the main-thread boundary")
    if execution_surface != "static-read" and owner_boundary != "enforced":
        errors.append(f"check {check_id} requires an enforced leaf boundary or main-thread ownership")


def load_state(root, errors):
    state_path = root / "review-state.json"
    if not state_path.is_file():
        errors.append("missing review state: review-state.json")
        return {}
    try:
        return json.loads(state_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        errors.append(f"invalid review state: {error}")
        return {}


def validate_target(state, errors):
    target = state.get("target", {})
    for field in ("initial_base_oid", "initial_head_oid", "final_head_oid"):
        value = target.get(field, "")
        if not isinstance(value, str) or not OID_PATTERN.fullmatch(value):
            errors.append(f"target.{field} must be a complete hexadecimal OID")
    if target.get("status") not in {"current", "updated_and_delta_reviewed"}:
        errors.append("target status must prove that the final target was reviewed")


def validate_permissions(state, errors):
    permissions = {}
    for permission in state.get("permissions", []):
        permission_id = permission.get("id")
        if not permission_id or permission_id in permissions:
            errors.append(f"invalid or duplicate permission id: {permission_id!r}")
            continue
        permissions[permission_id] = permission
        if permission.get("status") == "unresolved":
            errors.append(f"unresolved permission: {permission_id}")
        elif permission.get("status") not in {"approved", "denied"}:
            errors.append(f"invalid permission status: {permission_id}")
        elif permission.get("decision_source") != "user" or not permission.get("decision_evidence"):
            errors.append(f"permission {permission_id} lacks user decision evidence")

    for action in state.get("actions", []):
        action_id = action.get("id", "<unnamed>")
        permission = permissions.get(action.get("permission_id"))
        if not permission or permission.get("status") != "approved":
            errors.append(f"action {action_id} has no approved permission")
            continue
        for field in ("implementation", "target", "access_mode"):
            if action.get(field) != permission.get(field):
                errors.append(f"action {action_id} exceeds permission {field}")
        if action.get("action") not in permission.get("allowed_actions", []):
            errors.append(f"action {action_id} is outside permission budget")
    return permissions


def safe_artifact(root, relative, errors):
    if not isinstance(relative, str):
        errors.append(f"artifact path must be a string: {relative!r}")
        return None
    path = PurePosixPath(relative)
    if path.is_absolute() or ".." in path.parts:
        errors.append(f"artifact path must be relative to the review package: {relative}")
        return None
    artifact = root.joinpath(*path.parts)
    if not artifact.is_file():
        errors.append(f"missing artifact: {relative}")
        return None
    if artifact.stat().st_size == 0:
        errors.append(f"empty artifact: {relative}")
        return None
    return artifact


def validate_png(path, relative, errors):
    if path.suffix.lower() != ".png":
        return
    content = path.read_bytes()[:24]
    if len(content) < 24 or content[:8] != b"\x89PNG\r\n\x1a\n" or content[12:16] != b"IHDR":
        errors.append(f"invalid PNG artifact: {relative}")
        return
    width, height = struct.unpack(">II", content[16:24])
    if width == 0 or height == 0:
        errors.append(f"PNG has invalid dimensions: {relative}")


def validate_checks(state, root, permissions, errors):
    coverage = {row.get("id"): row for row in state.get("coverage", []) if row.get("id")}
    checks_by_coverage = {coverage_id: [] for coverage_id in coverage}

    for check in state.get("checks", []):
        check_id = check.get("id", "<unnamed>")
        validate_owner_binding(check, errors)
        coverage_id = check.get("coverage_id")
        if coverage_id not in coverage:
            errors.append(f"check {check_id} names unknown coverage: {coverage_id}")
            continue
        checks_by_coverage[coverage_id].append(check)
        status = check.get("status")
        if check.get("required") and status not in TERMINAL_CHECK_STATUSES:
            errors.append(f"non-terminal required check: {check_id}")
        if status == "not_applicable" and not check.get("reason"):
            errors.append(f"not_applicable check lacks reason: {check_id}")
        if status in {"denied", "unavailable"} and not check.get("impact"):
            errors.append(f"limited check lacks impact: {check_id}")
        if status == "satisfied":
            permission = permissions.get(check.get("permission_id"))
            if not permission or permission.get("status") != "approved":
                errors.append(f"satisfied check {check_id} has no approved permission")
            elif check.get("implementation") != permission.get("implementation"):
                errors.append(f"check {check_id} does not use its approved implementation")
            if not check.get("owner_can_invoke"):
                errors.append(f"owner {check.get('owner')} cannot invoke implementation for check {check_id}")
            if not check.get("artifacts"):
                errors.append(f"satisfied check lacks artifacts: {check_id}")
            for relative in check.get("artifacts", []):
                artifact = safe_artifact(root, relative, errors)
                if artifact:
                    validate_png(artifact, relative, errors)

    for coverage_id, row in coverage.items():
        row_checks = checks_by_coverage[coverage_id]
        slots = {check.get("slot") for check in row_checks}
        for slot in row.get("required_slots", []):
            if slot not in slots:
                errors.append(f"coverage {coverage_id} is missing required slot: {slot}")
        required_checks = [check for check in row_checks if check.get("required")]
        limited = any(check.get("status") in {"denied", "unavailable"} for check in required_checks)
        open_check = any(check.get("status") not in TERMINAL_CHECK_STATUSES for check in required_checks)
        expected = "blocked" if open_check else "limited" if limited else "complete"
        if row.get("required") and row.get("status") != expected:
            errors.append(
                f"coverage {coverage_id} status {row.get('status')!r} does not match derived status {expected!r}"
            )
        if expected == "limited" and not row.get("impact"):
            errors.append(f"limited coverage lacks impact: {coverage_id}")


def validate_evidence_profiles(state, errors):
    for row in state.get("coverage", []):
        profile = row.get("evidence_profile")
        if not profile:
            continue
        required = EVIDENCE_PROFILES.get(profile)
        if required is None:
            errors.append(f"unknown evidence profile: {profile}")
            continue
        slots = set(row.get("required_slots", []))
        for slot in sorted(required - slots):
            errors.append(f"{profile} profile is missing required slot: {slot}")


def validate_package(root):
    errors = []
    state = load_state(root, errors)
    if not state:
        return errors
    if state.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if state.get("review_status") not in TERMINAL_REVIEW_STATUSES:
        errors.append("review_status must be complete or limited")
    if not (root / "report.md").is_file():
        errors.append("missing report: report.md")
    validate_target(state, errors)
    permissions = validate_permissions(state, errors)
    validate_checks(state, root, permissions, errors)
    validate_evidence_profiles(state, errors)

    coverage_statuses = {row.get("status") for row in state.get("coverage", []) if row.get("required")}
    if not coverage_statuses:
        errors.append("review has no required coverage")
    if state.get("review_status") == "complete" and coverage_statuses - {"complete"}:
        errors.append("complete review contains non-complete required coverage")
    if state.get("review_status") == "limited" and not coverage_statuses.intersection({"limited"}):
        errors.append("limited review has no limited required coverage")
    return errors


def validate_discovery_permissions(state, errors):
    permissions = {}
    required_fields = ("implementation", "target", "access_mode", "allowed_actions")
    for permission in state.get("permissions", []):
        permission_id = permission.get("id")
        if not permission_id or permission_id in permissions:
            errors.append(f"invalid or duplicate candidate permission id: {permission_id!r}")
            continue
        permissions[permission_id] = permission
        if permission.get("status") != "unresolved":
            errors.append(f"candidate permission must remain unresolved: {permission_id}")
        for field in required_fields:
            if not permission.get(field):
                errors.append(f"candidate permission {permission_id} lacks {field}")
    return permissions


def validate_discovery_checks(state, permissions, errors):
    coverage = {row.get("id"): row for row in state.get("coverage", []) if row.get("id")}
    checks_by_coverage = {coverage_id: [] for coverage_id in coverage}
    for check in state.get("checks", []):
        check_id = check.get("id", "<unnamed>")
        validate_owner_binding(check, errors)
        coverage_id = check.get("coverage_id")
        if coverage_id not in coverage:
            errors.append(f"check {check_id} names unknown coverage: {coverage_id}")
            continue
        checks_by_coverage[coverage_id].append(check)
        if check.get("required") and check.get("status") != "planned":
            errors.append(f"discovery check must be planned: {check_id}")
        permission = permissions.get(check.get("permission_id"))
        if not permission:
            errors.append(f"check {check_id} has no candidate permission")
        elif check.get("implementation") != permission.get("implementation"):
            errors.append(f"check {check_id} does not name its candidate implementation")
        if not check.get("owner") or not isinstance(check.get("owner_can_invoke"), bool):
            errors.append(f"check {check_id} lacks an owner binding")

    for coverage_id, row in coverage.items():
        if row.get("required") and row.get("status") != "blocked":
            errors.append(f"discovery coverage must be blocked: {coverage_id}")
        slots = {check.get("slot") for check in checks_by_coverage[coverage_id]}
        for slot in row.get("required_slots", []):
            if slot not in slots:
                errors.append(f"coverage {coverage_id} is missing required slot: {slot}")

    if not any(row.get("required") for row in coverage.values()):
        errors.append("discovery ledger has no required coverage")


def validate_capability_discovery(state, errors):
    sources = {}
    for record in state.get("capability_discovery", []):
        source = record.get("source")
        if source not in CAPABILITY_DISCOVERY_SOURCES or source in sources:
            errors.append(f"invalid or duplicate capability discovery source: {source!r}")
            continue
        sources[source] = record
        if record.get("status") not in {"inspected", "unavailable"}:
            errors.append(f"invalid capability discovery status: {source}")
        if not record.get("evidence"):
            errors.append(f"capability discovery source lacks evidence: {source}")
    for source in sorted(CAPABILITY_DISCOVERY_SOURCES - sources.keys()):
        errors.append(f"missing capability discovery source: {source}")


def validate_discovery_gate(root):
    errors = []
    state = load_state(root, errors)
    if not state:
        return errors
    if state.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if state.get("review_status") != "blocked":
        errors.append("discovery review_status must be blocked")
    if state.get("workflow_state") not in DISCOVERY_GATE_STATES:
        errors.append("workflow_state must name the next permission gate")
    target = state.get("target", {})
    for field in ("initial_base_oid", "initial_head_oid", "final_head_oid"):
        value = target.get(field, "")
        if not isinstance(value, str) or not OID_PATTERN.fullmatch(value):
            errors.append(f"target.{field} must be a complete hexadecimal OID")
    if target.get("status") != "preliminary":
        errors.append("discovery target status must be preliminary")
    if state.get("actions"):
        errors.append("discovery ledger must not contain actions")
    if not (root / "report.md").is_file():
        errors.append("missing report: report.md")
    permissions = validate_discovery_permissions(state, errors)
    validate_discovery_checks(state, permissions, errors)
    validate_evidence_profiles(state, errors)
    validate_capability_discovery(state, errors)
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gate", choices=("final", "discovery"), default="final")
    parser.add_argument("review_package", type=Path)
    args = parser.parse_args()
    root = args.review_package.resolve()
    errors = validate_discovery_gate(root) if args.gate == "discovery" else validate_package(root)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    label = "discovery gate valid" if args.gate == "discovery" else "review package valid"
    print(f"{label}: {root}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
