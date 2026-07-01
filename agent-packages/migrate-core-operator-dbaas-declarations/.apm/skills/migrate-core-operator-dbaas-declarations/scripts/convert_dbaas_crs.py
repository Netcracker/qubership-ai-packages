#!/usr/bin/env python3
"""Convert legacy DBaaS declarations to dedicated dbaas-operator CRDs.

The converter is intentionally conservative. It supports common legacy JSON
inputs with the Python standard library. If PyYAML is installed, it also reads
legacy YAML and uses PyYAML for output formatting.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path
from typing import Any

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    yaml = None


RESERVED_CLASSIFIER_KEYS = {
    "microserviceName",
    "scope",
    "namespace",
    "tenantId",
    "customKeys",
}
DATABASE_DECLARATION_FIELDS = {
    "classifierConfig",
    "type",
    "lazy",
    "settings",
    "namePrefix",
    "versioningConfig",
    "initialInstantiation",
}
DB_POLICY_FIELDS = {
    "apiVersion",
    "kind",
    "metadata",
    "microserviceName",
    "services",
    "policy",
    "disableGlobalPermissions",
}
PRESERVED_METADATA_FIELDS = {"name", "namespace"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Legacy JSON/YAML file")
    parser.add_argument("--output", required=True, help="Output YAML file")
    parser.add_argument("--service-name")
    parser.add_argument("--namespace", default="{{ .Values.NAMESPACE }}")
    parser.add_argument("--name-prefix", default="")
    args = parser.parse_args()
    args.service_name_explicit = args.service_name is not None
    args.service_name = args.service_name or "{{ .Values.SERVICE_NAME }}"

    source = Path(args.input)
    warnings: list[str] = []
    docs = load_documents(source, warnings)
    resources: list[dict[str, Any]] = []

    for doc_index, doc in enumerate(docs, start=1):
        if doc is None:
            continue
        for item_index, item in enumerate(as_legacy_items(doc), start=1):
            resources.extend(convert_item(item, doc_index, item_index, args, warnings))

    if not resources:
        raise SystemExit("No supported DBaaS declarations found")

    warn_duplicate_resources(resources, warnings)
    Path(args.output).write_text(dump_yaml_documents(resources), encoding="utf-8")
    for warning in warnings:
        print(f"WARNING: {warning}", file=sys.stderr)
    print(f"Wrote {len(resources)} resource(s) to {args.output}", file=sys.stderr)
    return 0


def load_documents(path: Path, warnings: list[str]) -> list[Any]:
    text = path.read_text(encoding="utf-8-sig")
    suffix = path.suffix.lower()
    if suffix == ".json":
        data = json.loads(text)
        return data if isinstance(data, list) else [data]
    if yaml is None:
        raise SystemExit("YAML input requires PyYAML. Install PyYAML or convert the source to JSON first.")
    try:
        return list(yaml.safe_load_all(text))
    except yaml.YAMLError:
        warnings.append(
            "YAML required Helm-template sanitization; standalone template actions were commented and "
            "conditional semantics must be reviewed manually"
        )
        return list(yaml.safe_load_all(sanitize_helm_yaml(text)))


def sanitize_helm_yaml(text: str) -> str:
    """Make common Helm-template YAML parseable enough for migration.

    Comment standalone template actions and quote scalar template expressions.
    This makes common chart declarations parseable, but can remove conditional
    semantics; load_documents emits a warning whenever this fallback is used.
    """

    sanitized: list[str] = []
    scalar_with_template = re.compile(r"^(\s*[^#\n][^:]*:\s*)(.*\{\{.*\}\}.*)$")
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("{{") and ":" not in stripped:
            sanitized.append(f"{line[: len(line) - len(line.lstrip())]}# {stripped}")
            continue
        match = scalar_with_template.match(line)
        if match:
            prefix, value = match.groups()
            bare_value = value.strip()
            if not (bare_value.startswith("'") and bare_value.endswith("'")):
                escaped = bare_value.strip('"').replace("'", "''")
                sanitized.append(f"{prefix}'{escaped}'")
                continue
        sanitized.append(line)
    return "\n".join(sanitized) + "\n"


def as_legacy_items(doc: Any) -> list[dict[str, Any]]:
    if isinstance(doc, list):
        return [item for item in doc if isinstance(item, dict)]
    if isinstance(doc, dict):
        return [doc]
    return []


def convert_item(
    item: dict[str, Any],
    doc_index: int,
    item_index: int,
    args: argparse.Namespace,
    warnings: list[str],
) -> list[dict[str, Any]]:
    kind = str(item.get("kind", ""))
    sub_kind = str(item.get("subKind", ""))
    legacy_kind = sub_kind or kind
    legacy_kind_lower = legacy_kind.lower()

    if kind == "DBaaS":
        body = dict(item.get("spec") or {})
        metadata = dict(item.get("metadata") or {})
    else:
        body = dict(item)
        metadata = dict(item.get("metadata") or {})

    warn_dropped_metadata(metadata, f"Document {doc_index}", warnings)

    if legacy_kind_lower == "databasedeclaration":
        declarations = body.get("declarations")
        if declarations is None:
            declarations = [body]
        if not isinstance(declarations, list):
            warnings.append(f"Document {doc_index}: DatabaseDeclaration.declarations is not a list")
            return []
        resources = []
        for declaration_index, declaration in enumerate(declarations, start=1):
            if not isinstance(declaration, dict):
                warnings.append(f"Document {doc_index}: skipped non-object declaration #{declaration_index}")
                continue
            resources.append(
                convert_database_declaration(
                    declaration,
                    metadata,
                    doc_index,
                    declaration_index,
                    args,
                    warnings,
                )
            )
        return resources

    if legacy_kind_lower == "dbpolicy":
        return [convert_db_policy(body, metadata, doc_index, item_index, args, warnings)]

    warnings.append(f"Document {doc_index}: skipped unsupported kind/subKind {legacy_kind!r}")
    return []


def convert_database_declaration(
    declaration: dict[str, Any],
    old_metadata: dict[str, Any],
    doc_index: int,
    declaration_index: int,
    args: argparse.Namespace,
    warnings: list[str],
) -> dict[str, Any]:
    warn_unknown_fields(
        declaration,
        DATABASE_DECLARATION_FIELDS,
        f"DatabaseDeclaration #{declaration_index}",
        warnings,
    )
    classifier_config = declaration.get("classifierConfig") or {}
    classifier = classifier_config.get("classifier") if isinstance(classifier_config, dict) else None
    if not isinstance(classifier, dict):
        classifier = {}
        warnings.append(f"DatabaseDeclaration #{declaration_index}: missing classifierConfig.classifier")
    default_name = database_name_hint(declaration, classifier, doc_index, declaration_index)
    metadata = target_metadata(old_metadata, args, default_name, doc_index, declaration_index)
    target_classifier = convert_classifier(classifier, args.service_name)
    legacy_namespace = target_classifier.pop("namespace", None)
    if legacy_namespace not in (None, "", metadata["namespace"]):
        warnings.append(
            f"InternalDatabase {metadata['name']} classifier.namespace {legacy_namespace!r} differs from "
            f"metadata.namespace {metadata['namespace']!r}; omitted classifier.namespace so the operator derives it"
        )

    spec: dict[str, Any] = {
        "classifier": target_classifier,
    }

    for field in ("type", "lazy", "namePrefix", "versioningConfig", "initialInstantiation"):
        if field in declaration:
            spec[field] = convert_nested_classifiers(declaration[field], args.service_name)

    if "settings" in declaration:
        settings = declaration["settings"]
        spec["settings"] = settings
        if not isinstance(settings, dict):
            warnings.append(
                f"InternalDatabase {resource_name(old_metadata, args, default_name, doc_index, declaration_index)} "
                "has non-object settings; verify target CRD schema before applying"
            )
        else:
            for key, value in settings.items():
                if not isinstance(value, str):
                    warnings.append(
                        f"InternalDatabase {resource_name(old_metadata, args, default_name, doc_index, declaration_index)} "
                        f"has non-string settings.{key}; verify target CRD schema before applying"
                    )

    target_classifier = spec["classifier"]
    for required_key in ("microserviceName", "scope"):
        if not target_classifier.get(required_key):
            warnings.append(f"InternalDatabase {default_name} is missing classifier.{required_key}")
    if not spec.get("type"):
        warnings.append(f"InternalDatabase {default_name} is missing type")

    if spec.get("lazy") is True:
        initial = spec.get("initialInstantiation")
        if isinstance(initial, dict) and initial.get("approach") == "clone":
            warnings.append("lazy=true with initialInstantiation.approach=clone is invalid")
    initial = spec.get("initialInstantiation")
    if isinstance(initial, dict) and initial.get("approach") == "clone" and "sourceClassifier" not in initial:
        warnings.append("initialInstantiation.approach=clone requires sourceClassifier")
    validate_source_classifier_owner(spec, default_name, warnings)

    return {
        "apiVersion": "dbaas.netcracker.com/v1",
        "kind": "InternalDatabase",
        "metadata": metadata,
        "spec": spec,
    }


def validate_source_classifier_owner(
    spec: dict[str, Any],
    resource_name_hint: str,
    warnings: list[str],
) -> None:
    initial = spec.get("initialInstantiation")
    if not isinstance(initial, dict):
        return
    source_classifier = initial.get("sourceClassifier")
    if not isinstance(source_classifier, dict):
        return

    target_classifier = spec.get("classifier")
    if not isinstance(target_classifier, dict):
        return
    target_owner = target_classifier.get("microserviceName")
    source_owner = source_classifier.get("microserviceName")
    if not source_owner and target_owner:
        source_classifier["microserviceName"] = target_owner
        warnings.append(
            f"InternalDatabase {resource_name_hint} sourceClassifier.microserviceName was missing; "
            "filled it from classifier.microserviceName"
        )
    elif target_owner and source_owner != target_owner:
        warnings.append(
            f"InternalDatabase {resource_name_hint} sourceClassifier.microserviceName must match "
            "classifier.microserviceName; cross-service clones are invalid"
        )


def database_name_hint(
    declaration: dict[str, Any],
    classifier: dict[str, Any],
    doc_index: int,
    declaration_index: int,
) -> str:
    scope = str(classifier.get("scope") or "db")
    custom_keys = classifier.get("customKeys")
    logical_name = None
    if isinstance(custom_keys, dict):
        logical_name = (
            custom_keys.get("logicalDbName")
            or custom_keys.get("logicalDBName")
            or custom_keys.get("logicalDBname")
        )
    if logical_name:
        return f"{scope}-{logical_name}-db"
    if classifier.get("transactional") is True:
        return f"{scope}-transactional-db"
    db_type = declaration.get("type")
    if db_type:
        return f"{scope}-{db_type}-db"
    return f"internaldatabase-{doc_index}-{declaration_index}"


def convert_db_policy(
    body: dict[str, Any],
    old_metadata: dict[str, Any],
    doc_index: int,
    item_index: int,
    args: argparse.Namespace,
    warnings: list[str],
) -> dict[str, Any]:
    warn_unknown_fields(body, DB_POLICY_FIELDS, "DatabaseAccessPolicy", warnings)
    source_microservice_name = body.get("microserviceName") or label_value(
        old_metadata, "app.kubernetes.io/instance"
    )
    if getattr(args, "service_name_explicit", False):
        microservice_name = args.service_name
    else:
        microservice_name = source_microservice_name or args.service_name
    if not source_microservice_name and not getattr(args, "service_name_explicit", False):
        warnings.append(
            "DatabaseAccessPolicy.spec.microserviceName uses the --service-name fallback; "
            "verify it against the owning service"
        )
    if not microservice_name:
        microservice_name = "TODO-service-name"
        warnings.append("DatabaseAccessPolicy.spec.microserviceName could not be derived")

    spec: dict[str, Any] = {"microserviceName": normalize_service_template(str(microservice_name), args.service_name)}
    for field in ("services", "policy"):
        if field in body:
            spec[field] = body[field]
    if "disableGlobalPermissions" in body:
        spec["disableGlobalPermissions"] = coerce_bool(body["disableGlobalPermissions"])

    if "services" not in spec and "policy" not in spec:
        warnings.append("DatabaseAccessPolicy has neither services nor policy")

    return {
        "apiVersion": "dbaas.netcracker.com/v1",
        "kind": "DatabaseAccessPolicy",
        "metadata": target_metadata(old_metadata, args, "database-access-policy", doc_index, item_index),
        "spec": spec,
    }


def convert_nested_classifiers(value: Any, service_name: str) -> Any:
    if isinstance(value, dict):
        converted = {}
        for key, nested in value.items():
            if key == "sourceClassifier" and isinstance(nested, dict):
                converted[key] = convert_classifier(nested, service_name)
            else:
                converted[key] = convert_nested_classifiers(nested, service_name)
        return converted
    if isinstance(value, list):
        return [convert_nested_classifiers(item, service_name) for item in value]
    return value


def convert_classifier(classifier: dict[str, Any], service_name: str) -> dict[str, Any]:
    converted: dict[str, Any] = {}
    extra_keys: dict[str, Any] = {}
    for key, value in classifier.items():
        if key in RESERVED_CLASSIFIER_KEYS:
            if key == "microserviceName" and isinstance(value, str):
                converted[key] = normalize_service_template(value, service_name)
            else:
                converted[key] = value
        else:
            extra_keys[key] = value
    if extra_keys:
        converted["extraKeys"] = extra_keys
    return converted


def normalize_service_template(value: str, service_name: str) -> str:
    if value.strip() in {"{{$SERVICE_NAME}}", "{{ $SERVICE_NAME }}", "${SERVICE_NAME}"}:
        return service_name
    return value


def coerce_bool(value: Any) -> Any:
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered == "true":
            return True
        if lowered == "false":
            return False
    return value


def target_metadata(
    old_metadata: dict[str, Any],
    args: argparse.Namespace,
    default_prefix: str,
    doc_index: int,
    item_index: int,
) -> dict[str, Any]:
    return {
        "name": resource_name(old_metadata, args, default_prefix, doc_index, item_index),
        "namespace": old_metadata.get("namespace") or args.namespace,
    }


def resource_name(
    old_metadata: dict[str, Any],
    args: argparse.Namespace,
    default_prefix: str,
    doc_index: int,
    item_index: int,
) -> str:
    old_name = old_metadata.get("name")
    if old_name:
        return sanitize_name(str(old_name))
    prefix = args.name_prefix or default_prefix
    return sanitize_name(f"{prefix}-{doc_index}-{item_index}")


def label_value(metadata: dict[str, Any], key: str) -> Any:
    labels = metadata.get("labels")
    if isinstance(labels, dict):
        return labels.get(key)
    return None


def warn_unknown_fields(
    source: dict[str, Any],
    known_fields: set[str],
    context: str,
    warnings: list[str],
) -> None:
    unknown = sorted(set(source) - known_fields)
    if unknown:
        warnings.append(f"{context} has unsupported fields that were dropped: {', '.join(unknown)}")


def warn_dropped_metadata(metadata: dict[str, Any], context: str, warnings: list[str]) -> None:
    dropped = sorted(set(metadata) - PRESERVED_METADATA_FIELDS)
    if dropped:
        warnings.append(f"{context} metadata fields were dropped: {', '.join(dropped)}")


def warn_duplicate_resources(resources: list[dict[str, Any]], warnings: list[str]) -> None:
    seen: set[tuple[str, str, str]] = set()
    for resource in resources:
        metadata = resource.get("metadata") or {}
        identity = (
            str(resource.get("kind") or ""),
            str(metadata.get("namespace") or ""),
            str(metadata.get("name") or ""),
        )
        if identity in seen:
            warnings.append(
                f"Duplicate generated resource kind={identity[0]} namespace={identity[1]} name={identity[2]}"
            )
        seen.add(identity)


def sanitize_name(value: str) -> str:
    if "{{" in value or "}}" in value:
        return value
    value = value.lower()
    value = re.sub(r"[^a-z0-9-]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value or "dbaas-resource"


def dump_yaml_documents(resources: list[dict[str, Any]]) -> str:
    if yaml is not None:
        return "---\n" + "---\n".join(
            yaml.safe_dump(resource, sort_keys=False, allow_unicode=False) for resource in resources
        )
    return "---\n" + "---\n".join(dump_yaml(resource) for resource in resources)


def dump_yaml(value: Any, indent: int = 0) -> str:
    spaces = " " * indent
    if isinstance(value, dict):
        lines: list[str] = []
        for key, nested in value.items():
            formatted_key = json.dumps(str(key))
            if isinstance(nested, (dict, list)):
                if nested:
                    lines.append(f"{spaces}{formatted_key}:")
                    lines.append(dump_yaml(nested, indent + 2).rstrip("\n"))
                else:
                    empty_value = "{}" if isinstance(nested, dict) else "[]"
                    lines.append(f"{spaces}{formatted_key}: {empty_value}")
            else:
                lines.append(f"{spaces}{formatted_key}: {format_scalar(nested)}")
        return "\n".join(lines) + "\n"
    if isinstance(value, list):
        lines = []
        for item in value:
            if isinstance(item, (dict, list)):
                if item:
                    lines.append(f"{spaces}-")
                    lines.append(dump_yaml(item, indent + 2).rstrip("\n"))
                else:
                    empty_value = "{}" if isinstance(item, dict) else "[]"
                    lines.append(f"{spaces}- {empty_value}")
            else:
                lines.append(f"{spaces}- {format_scalar(item)}")
        return "\n".join(lines) + "\n"
    return f"{spaces}{format_scalar(value)}\n"


def format_scalar(value: Any) -> str:
    if value is True:
        return "true"
    if value is False:
        return "false"
    if value is None:
        return "null"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        if math.isnan(value):
            return ".nan"
        if math.isinf(value):
            return ".inf" if value > 0 else "-.inf"
        text = repr(value)
        if "e" in text.lower():
            mantissa, exponent = re.split(r"[eE]", text, maxsplit=1)
            if "." not in mantissa:
                mantissa += ".0"
            return f"{mantissa}e{exponent}"
        return text
    return json.dumps(str(value))


if __name__ == "__main__":
    raise SystemExit(main())
