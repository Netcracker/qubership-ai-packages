#!/usr/bin/env python3
"""Validate DBaaS declarative resources against a datasource inventory."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable

try:
    import yaml
except ImportError as exc:  # pragma: no cover - exercised only without the pinned dependency
    raise SystemExit(
        "PyYAML is required; run with: uv run --with-requirements scripts/requirements.txt "
        "scripts/validate_generated.py ..."
    ) from exc


DNS_LABEL = re.compile(r"^[a-z0-9](?:[-a-z0-9]*[a-z0-9])?$")
RESERVED_EXTRA_KEYS = {"microserviceName", "scope", "namespace", "tenantId", "customKeys"}
WORKLOAD_KINDS = {"Deployment", "StatefulSet"}


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def database_key(classifier: dict[str, Any], db_type: str) -> str:
    return f"{canonical(classifier)}|{db_type.lower()}"


def claim_key(classifier: dict[str, Any], db_type: str, role: str) -> str:
    return f"{database_key(classifier, db_type)}|{role.strip()}"


def manifest_files(paths: Iterable[Path]) -> list[Path]:
    result: list[Path] = []
    for path in paths:
        if path.is_dir():
            result.extend(sorted(path.rglob("*.yaml")))
            result.extend(sorted(path.rglob("*.yml")))
        elif path.is_file():
            result.append(path)
        else:
            raise ValueError(f"manifest path does not exist: {path}")
    return result


def load_objects(paths: list[Path]) -> list[dict[str, Any]]:
    objects: list[dict[str, Any]] = []
    for path in manifest_files(paths):
        with path.open(encoding="utf-8") as stream:
            for index, document in enumerate(yaml.safe_load_all(stream), start=1):
                if document is None:
                    continue
                if not isinstance(document, dict):
                    raise ValueError(f"{path}:{index}: manifest document must be a mapping")
                document["__source"] = f"{path}:{index}"
                objects.append(document)
    return objects


def object_identity(obj: dict[str, Any]) -> str:
    metadata = obj.get("metadata") or {}
    return f"{obj.get('kind', '<missing>')}/{metadata.get('namespace', 'default')}/{metadata.get('name', '<missing>')}"


def check_name(name: Any, what: str, errors: list[str]) -> None:
    if not isinstance(name, str) or not name:
        errors.append(f"{what}: name is required")
    elif len(name) > 63 or DNS_LABEL.fullmatch(name) is None:
        errors.append(f"{what}: {name!r} is not a DNS-1123 label of at most 63 characters")


def effective_classifier(obj: dict[str, Any], errors: list[str]) -> dict[str, Any] | None:
    spec = obj.get("spec") or {}
    classifier = spec.get("classifier")
    identity = object_identity(obj)
    if not isinstance(classifier, dict):
        errors.append(f"{identity}: spec.classifier must be a mapping")
        return None

    metadata = obj.get("metadata") or {}
    namespace = metadata.get("namespace", "default")
    classifier = dict(classifier)
    classifier_namespace = classifier.get("namespace")
    if classifier_namespace not in (None, "", namespace):
        errors.append(
            f"{identity}: classifier namespace {classifier_namespace!r} does not match metadata namespace {namespace!r}"
        )
    classifier["namespace"] = namespace if not classifier_namespace else classifier_namespace

    extra_keys = classifier.get("extraKeys")
    if extra_keys is None:
        extra_keys = {}
    if not isinstance(extra_keys, dict):
        errors.append(f"{identity}: classifier.extraKeys must be a mapping")
    else:
        reserved = sorted(RESERVED_EXTRA_KEYS.intersection(extra_keys))
        if reserved:
            errors.append(f"{identity}: classifier.extraKeys contains reserved keys: {', '.join(reserved)}")

    return classifier


def validate_inventory(
    inventory_path: Path,
    internals: dict[str, dict[str, Any]],
    claims: dict[str, dict[str, Any]],
    errors: list[str],
) -> None:
    with inventory_path.open(encoding="utf-8") as stream:
        inventory = json.load(stream)

    expected_databases: set[str] = set()
    expected_claims: set[str] = set()
    for datasource in inventory.get("datasources", []):
        if datasource.get("migrationFeasibility") != "SUPPORTED":
            continue
        classifier = datasource.get("classifier")
        db_type = datasource.get("type")
        if not isinstance(classifier, dict) or not isinstance(db_type, str) or not db_type:
            errors.append(f"inventory datasource {datasource.get('id', '<unknown>')}: classifier and type are required")
            continue
        db_key = database_key(classifier, db_type)
        expected_databases.add(db_key)
        roles = datasource.get("requestedRoles", [""])
        if not isinstance(roles, list) or not all(isinstance(role, str) for role in roles):
            errors.append(f"inventory datasource {datasource.get('id', '<unknown>')}: requestedRoles must be strings")
            continue
        expected_claims.update(claim_key(classifier, db_type, role) for role in roles)

    missing_databases = expected_databases - set(internals)
    extra_databases = set(internals) - expected_databases
    missing_claims = expected_claims - set(claims)
    extra_claims = set(claims) - expected_claims
    if missing_databases:
        errors.append(f"missing InternalDatabase identities: {len(missing_databases)}")
    if extra_databases:
        errors.append(f"unexpected InternalDatabase identities: {len(extra_databases)}")
    if missing_claims:
        errors.append(f"missing DatabaseSecretClaim identities: {len(missing_claims)}")
    if extra_claims:
        errors.append(f"unexpected DatabaseSecretClaim identities: {len(extra_claims)}")


def validate(paths: list[Path], inventory: Path | None) -> list[str]:
    errors: list[str] = []
    objects = load_objects(paths)
    seen_objects: set[str] = set()
    internals: dict[str, dict[str, Any]] = {}
    claims: dict[str, dict[str, Any]] = {}
    secret_claims: dict[tuple[str, str], str] = {}

    for obj in objects:
        identity = object_identity(obj)
        if identity in seen_objects:
            errors.append(f"duplicate object identity: {identity}")
        seen_objects.add(identity)
        metadata = obj.get("metadata") or {}
        check_name(metadata.get("name"), identity, errors)

        kind = obj.get("kind")
        if kind not in {"InternalDatabase", "DatabaseSecretClaim"}:
            continue
        classifier = effective_classifier(obj, errors)
        spec = obj.get("spec") or {}
        db_type = spec.get("type")
        if classifier is None or not isinstance(db_type, str) or not db_type:
            errors.append(f"{identity}: spec.type is required")
            continue
        db_key = database_key(classifier, db_type)

        if kind == "InternalDatabase":
            settings = spec.get("settings")
            if settings is None:
                settings = {}
            if not isinstance(settings, dict) or any(not isinstance(value, str) for value in settings.values()):
                errors.append(f"{identity}: spec.settings values must be strings")
            if db_key in internals:
                errors.append(f"duplicate InternalDatabase identity: {identity} and {object_identity(internals[db_key])}")
            internals[db_key] = obj
            continue

        labels = metadata.get("labels") or {}
        if not isinstance(labels, dict) or not labels.get("app.kubernetes.io/name"):
            errors.append(f"{identity}: non-empty app.kubernetes.io/name label is required")
        role = spec.get("userRole", "")
        if not isinstance(role, str):
            errors.append(f"{identity}: spec.userRole must be a string")
            role = ""
        key = claim_key(classifier, db_type, role)
        if key in claims:
            errors.append(f"duplicate DatabaseSecretClaim lookup identity: {identity} and {object_identity(claims[key])}")
        claims[key] = obj
        secret_name = spec.get("secretName")
        check_name(secret_name, f"{identity} spec.secretName", errors)
        namespace = metadata.get("namespace", "default")
        secret_key = (namespace, secret_name)
        if secret_key in secret_claims:
            errors.append(f"{identity}: Secret {namespace}/{secret_name} is also claimed by {secret_claims[secret_key]}")
        secret_claims[secret_key] = identity

    for key, claim in claims.items():
        db_key = key.rsplit("|", 1)[0]
        if db_key not in internals:
            errors.append(f"{object_identity(claim)}: no InternalDatabase has the same classifier and type")

    mount_occurrences: dict[tuple[str, str], list[tuple[str, Any, Any]]] = {}
    for obj in objects:
        if obj.get("kind") not in WORKLOAD_KINDS:
            continue
        metadata = obj.get("metadata") or {}
        namespace = metadata.get("namespace", "default")
        pod_spec = (((obj.get("spec") or {}).get("template") or {}).get("spec") or {})
        volume_secrets: dict[str, str] = {}
        seen_volume_names: set[str] = set()
        for volume in pod_spec.get("volumes") or []:
            if not isinstance(volume, dict):
                continue
            volume_name = volume.get("name")
            if volume_name in seen_volume_names:
                errors.append(f"{object_identity(obj)}: duplicate volume name {volume_name!r}")
            seen_volume_names.add(volume_name)
            secret = volume.get("secret") or {}
            if secret.get("secretName"):
                volume_secrets[volume_name] = secret["secretName"]
        for container in pod_spec.get("containers") or []:
            for mount in container.get("volumeMounts") or []:
                secret_name = volume_secrets.get(mount.get("name"))
                if not secret_name:
                    continue
                secret_key = (namespace, secret_name)
                mount_occurrences.setdefault(secret_key, []).append(
                    (
                        f"{object_identity(obj)} container {container.get('name', '<missing>')}",
                        mount.get("mountPath"),
                        mount.get("readOnly"),
                    )
                )

    for secret_key, claim_identity in secret_claims.items():
        occurrences = mount_occurrences.get(secret_key, [])
        if len(occurrences) != 1:
            errors.append(
                f"{claim_identity}: Secret {secret_key[0]}/{secret_key[1]} must have exactly one consuming volumeMount; "
                f"found {len(occurrences)}"
            )
            continue
        location, mount_path, read_only = occurrences[0]
        expected_path = f"/etc/secrets/dbaas-secrets/{secret_key[1]}"
        if mount_path != expected_path or read_only is not True:
            errors.append(
                f"{claim_identity}: mount in {location} must use path {expected_path!r} with readOnly: true"
            )

    if inventory is not None:
        validate_inventory(inventory, internals, claims, errors)
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifests", nargs="+", type=Path)
    parser.add_argument("--inventory", type=Path)
    args = parser.parse_args()
    try:
        errors = validate(args.manifests, args.inventory)
    except (OSError, ValueError, json.JSONDecodeError, yaml.YAMLError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if errors:
        for error in errors:
            print(f"error: {error}", file=sys.stderr)
        return 1
    print("ok: generated DBaaS resources match the inventory and workload mounts")
    return 0


if __name__ == "__main__":
    sys.exit(main())
