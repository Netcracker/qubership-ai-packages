---
name: values-schema-generator
description: >
  Generate a strict values.schema.json for a Helm chart. Triggers when the user says:
  "generate schema", "create schema.json", "values schema", "schema for my chart",
  "validate helm values", or points at a chart directory and asks for schema generation.
  Always use this skill for schema generation tasks — do not write ad-hoc schema logic inline.
---

# Helm values.schema.json Generator

Generates a strict, validated `values.schema.json` for one Helm chart at a time.
Schema lives next to `values.yaml` in the chart directory.

This skill is fully generic — it discovers all field names, types, and enum values
from the repo's own sources (values.yaml, Go types, installation guide, templates).
It never assumes field names or enum values specific to any one service.

**Default behavior: discover everything, ask nothing.**
Every field in values.yaml or templates gets a type — always via the priority rules
or safe fallback below. Only ask when a field's default VALUE itself cannot be
validated by any safe fallback type. When in doubt, write the schema and fix
failures in the validation loop rather than asking upfront.

---

## How to invoke

If the user has not specified which chart to work on, use `AskUserQuestion` to present
all discovered charts as selectable options (one option per chart, label = chart directory
path relative to repo root). Let the user pick with up/down arrow keys. Do NOT proceed
until a chart is selected. Process one chart per invocation. After completing, offer to
do the next chart via another `AskUserQuestion`.

---

## Step 1 — Locate sources

```bash
# Chart directories
find <repo_root> -name "Chart.yaml" | sort

# values.yaml candidates
find <repo_root> -name "values.yaml" | sort

# Go type files
find <repo_root> -name "*_types.go" | sort

# go.mod — find external package versions for shared types
find <chart_dir>/.. -name "go.mod" -maxdepth 3 | head -5

# CRD yamls
find <repo_root> -name "*.yaml" | xargs grep -l "openAPIV3Schema" 2>/dev/null | sort

# Installation guide (any .md with a Parameters section)
find <repo_root>/docs -name "*.md" 2>/dev/null | xargs grep -l "## Parameters\|# Parameters" 2>/dev/null
find <repo_root> -name "*.md" | xargs grep -l "## Parameters\|# Parameters" 2>/dev/null | sort

# Override / deployment values files — scan both in-repo and any user-provided path
# In-repo: test values, named overrides
find <repo_root> \( -path "*/tests/values/*.yaml" -o -path "*/tests/values/*.yml" \
  -o -name "*-values.yaml" -o -name "values-*.yaml" \) 2>/dev/null | sort
# If the user mentioned an external override directory, list it now too:
# find <external_override_dir> \( -name "*.yml" -o -name "*.yaml" \) 2>/dev/null | sort
```

Print all found paths before proceeding.

**If the user provided an external override directory** (e.g. a pipeline/infra repo path),
collect all `.yaml`/`.yml` files from it now and include them in the field-discovery step
below — treat every key path in those files as a real field the schema must accept.
Do not wait until Step 7D to discover those fields; discover them here so the schema is
built correctly from the start.

---

## Step 2 — Read all sources in parallel

Read ALL of these before writing a single line of schema:

1. **`values.yaml`** — full file, all keys and defaults.

2. **Installation guide** — locate the `## Parameters` section (or `# Parameters`).
   Each parameter table row gives: key path, type, default, description, mandatory flag.
   Read every subsection in the guide that covers this chart's parameters.
   If no guide exists, proceed without it.

3. **Go `*_types.go`** — the main `Spec` struct and every struct it references.
   This is authoritative for field types.
   Do not assume which struct is the entry point; grep for it:

   ```bash
   grep -rn "type.*Spec struct" <repo_root> --include="*_types.go"
   ```

   Also grep for `const` blocks to find enum values:

   ```bash
   grep -B2 -A 20 "^const (" <types_file>
   ```

   **Read ALL `*_types.go` files in the repo — not just the one nearest to the chart.**
   A superset chart (one that deploys an operator AND creates CRs consumed by that
   operator) will have values that map to types defined in sibling modules. The chart's
   own types file may contain a simplified version of a struct while another module in
   the repo contains the full version with more fields.

   For any struct name defined in more than one `*_types.go` file across the repo,
   take the **union of all fields** across every definition. The richer definition
   extends the simpler one — never let a shorter definition truncate fields that exist
   in another file.

   Detection — scan ALL struct names, not just \*Spec:

   ```bash
   # Step A: collect every struct name defined in the chart's own types file
   sed -n 's/^type \([A-Za-z0-9_]*\) struct/\1/p' <chart_types_file>

   # Step B: for EACH struct name found above, find every other *_types.go in the
   # repo that also defines it — these files contain the richer union definition
   for s in $(sed -n 's/^type \([A-Za-z0-9_]*\) struct/\1/p' <chart_types_file>); do
     grep -rn "type $s struct" <repo_root> --include="*_types.go" \
       | grep -v "<chart_types_file>"
   done
   ```

   Read every file that produces output in Step B.
   Apply the field union (all fields from all definitions) before resolving types.

   **Why this matters**: a services chart and its sibling operator chart often share
   struct names (e.g. domain objects, nested config structs). The services module
   carries a minimal version of these structs (only the fields it reads), while the
   operator module owns the CRD and carries the full definition with more fields.
   Limiting detection to `*Spec struct` silently drops any fields that only appear in
   the operator's richer definition. Scanning all struct names catches these gaps
   regardless of naming convention.

   **MANDATORY — produce a union field table before writing any schema.**
   For every struct that appears in more than one `*_types.go`, run this script to
   extract every json tag from every definition and merge them:

   ```bash
   python3 - <<'EOF'
   import re, sys
   from pathlib import Path
   from collections import defaultdict

   repo_root = "<repo_root>"
   files = list(Path(repo_root).rglob("*_types.go"))

   # parse: struct name → {file → {json_tag: go_type}}
   structs = defaultdict(dict)
   for f in files:
       src = f.read_text()
       for m in re.finditer(r'type (\w+) struct \{([^}]+)\}', src, re.S):
           sname, body = m.group(1), m.group(2)
           fields = {}
           for line in body.splitlines():
               tm = re.search(r'json:"([^,"]+)', line)
               gm = re.search(r'^\s+\w+\s+([\w\[\]*./]+)', line)
               if tm:
                   fields[tm.group(1)] = gm.group(1) if gm else "?"
           if fields:
               structs[sname][str(f)] = fields

   # print structs defined in more than one file
   for sname, fdefs in structs.items():
       if len(fdefs) > 1:
           union = {}
           for fpath, fields in fdefs.items():
               for tag, gotype in fields.items():
                   if tag not in union:
                       union[tag] = (gotype, fpath)
                   # keep entry from richer file (more fields wins)
           print(f"\n=== {sname} UNION ({len(union)} fields from {len(fdefs)} files) ===")
           for tag, (gotype, src) in sorted(union.items()):
               print(f"  {tag:30s} {gotype:30s}  ({Path(src).name})")
   EOF
   ```

   **Do not write a single `$defs` entry until this table is produced.**
   Every field in the union table must appear in the schema. Missing fields = schema gap.
   A field seen in ANY definition of a struct is a valid field for that struct's $def.

   **After writing the schema in Step 6, a mandatory cross-check (Step 6B) verifies
   that every union-table field was actually written. Do not skip Step 6B.**

   **External packages**: if a struct field references a type from an external package
   (e.g. `types.StorageRequirements`, `types.Recycler`), read `go.mod` to find the
   package version, then read that package's types file from the Go module cache:

   ```bash
   find $GOPATH/pkg/mod -path "*<package-name>@<version>*" -name "*.go" | head -5
   ```

   Read every relevant external type file before writing the schema.

4. **CRD yaml** — for k8s complex types (Affinity, Tolerations, etc.).
   Read the `openAPIV3Schema` section. Do not copy the full CRD — extract only
   property shapes needed.

5. **All template `.Values` references** — scan every template file including helpers:

   ```bash
   grep -rho '\.Values\.[a-zA-Z0-9_.]*' \
     --include="*.yaml" --include="*.tpl" \
     <chart_dir>/templates/ \
     <chart_dir>/tests/ \
     2>/dev/null \
     | sed 's/^\.Values\.//' \
     | sort -u
   ```

   The `-o` flag extracts ALL matches including multiple per line (e.g. `{{ printf "%s:%s"
   .Values.image.repository .Values.image.tag }}` yields both `image.repository` and `image.tag`).

   Helper files (`_helper.tpl`, `_helpers.tpl`) often reference fields not in values.yaml
   or the guide. These refs are real and must be included.

   Also extract enum candidates from templates:

   ```bash
   grep -rho '\.Values\.[a-zA-Z0-9_.]* *"[^"]*"' \
     --include="*.yaml" --include="*.tpl" \
     <chart_dir>/templates/ 2>/dev/null \
     | sort -u
   ```

   The `-o` flag ensures multiple enum checks per line (e.g. `{{- if or (eq .Values.mode "foo")
   (eq .Values.mode "bar") }}`) all get extracted.

   Also check template fail messages for enum lists:

   ```bash
   grep -rho '"[^"]\+"' \
     --include="*.yaml" --include="*.tpl" \
     <chart_dir>/templates/ 2>/dev/null \
     | grep -E 'fail|assert' \
     | sort -u | head -30
   ```

6. **Override/deployment files — extract ALL key paths before writing schema.**
   Run this script over every override file collected in Step 1 (in-repo and external):

   ```python
   import yaml, glob
   from pathlib import Path

   override_files = [
       # add paths from Step 1 here
   ]

   def extract_paths(obj, prefix=""):
       paths = set()
       if isinstance(obj, dict):
           for k, v in obj.items():
               full = f"{prefix}.{k}" if prefix else k
               paths.add(full)
               paths |= extract_paths(v, full)
       elif isinstance(obj, list):
           for item in obj:
               paths |= extract_paths(item, prefix)
       return paths

   all_paths = set()
   for fpath in override_files:
       data = yaml.safe_load(open(fpath)) or {}
       all_paths |= extract_paths(data)

   # Print paths not already in values.yaml to surface schema gaps early
   base = yaml.safe_load(open("values.yaml")) or {}
   base_paths = extract_paths(base)
   extra = sorted(all_paths - base_paths)
   print(f"{len(extra)} key paths in overrides not in values.yaml:")
   for p in extra:
       print(f"  {p}")
   ```

   Every key path in the output is a field the schema MUST accept. Resolve its type
   using the same priority rules (Go struct union → guide → infer from value → fallback).
   Do NOT skip or ignore any path — "Additional properties not allowed" failures in Step 7D
   mean a path was missed here.

---

## Step 3 — Classify ALL_CAPS keys

Before resolving types, classify every ALL_CAPS (or mixed-case flat) key found in
templates and values.yaml. Apply these rules silently — never ask:

**Include as schema field** (regardless of casing):

- Key is present in `values.yaml` (any casing) → include with correct type from values.yaml default
- Key uses dot-notation (`.Values.foo.bar`) → always a real field

**Skip (deploy-time injection)**:

- Flat ALL*CAPS key NOT present in values.yaml: `[A-Z]A-Z0-9*]+`with no dots
  (e.g.`NAMESPACE`, `DB_PASSWORD`, `CLOUD_HOST`)
- `deployDescriptor`, `deployDescriptorBase64`
- CamelCase flat keys that shadow a dot-notation sub-field already included
  (e.g. `fooImage` if `foo.image` is already in schema)

**Rule of thumb**: if the key is in `values.yaml` → include, regardless of name format.
If it's only in templates and is flat ALL_CAPS → skip.

---

## Step 4 — Resolve types (strict priority order)

For every field, resolve type by stopping at the first matching rule.
**Never ask the user if any rule resolves the type.**

### Priority 1 — Go struct (most authoritative for types) + guide (authoritative for field set)

**Critical rule — Go struct defines types; the union of Go struct AND guide defines the
complete field set for each object.** The Go struct only models the operator's CR spec.
The Helm chart values.yaml may carry additional deployment parameters (e.g. `mongodb.storage`,
`mongodb.dataResources`) that flow to a different CR and are documented only in the guide.
If the guide lists sub-fields for `foo.*` beyond what the Go struct has, include ALL of them.
Never let the Go struct alone truncate an object's field list.

Map Go types to JSON Schema:

| Go type                    | JSON Schema type                                                                                                     |
| -------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| `string`                   | `"string"`                                                                                                           |
| `bool`                     | `"boolean"`                                                                                                          |
| `int`, `int32`, `int64`    | `"integer"`                                                                                                          |
| `float32`, `float64`       | `"number"`                                                                                                           |
| `[]string`                 | `array`, `items: {type: string}`                                                                                     |
| `[]SomeStruct`             | normally `array`, but if override files set it as plain object → use `oneOf: [{$ref}, {type: array, items: {$ref}}]` |
| `map[string]string`        | `object`, `additionalProperties: {type: string}`                                                                     |
| `map[string]SomeStruct`    | `object`, `additionalProperties: true`                                                                               |
| `*v1.ResourceRequirements` | use `resourceRequirements` $def                                                                                      |
| `*v1.Affinity`             | use `affinity` $def                                                                                                  |
| Any other pointer `*T`     | base type is nullable → `["<T>", "null"]`                                                                            |

**Nullability for map types**: absent/null default in values.yaml → `["object", "null"]`.
Non-null default → plain `"object"`.

**`[]string` with scalar default in values.yaml**: if Go type is `[]string` but
values.yaml sets default to a scalar string (e.g. `''`, `"5Gi"`, any string), both
string and array are valid → use:

```json
"oneOf": [{ "type": "string" }, { "type": "array", "items": { "type": "string" } }]
```

### Priority 2 — Installation guide type column

Use if field not in Go struct. Trust default value over type column when they conflict.
**Also use for completeness**: after resolving types from Go struct, scan every guide
table row whose key path starts with the same object prefix (e.g. `mongodb.*`) and add
any fields the struct missed.

### Priority 3 — Infer from values.yaml default

| Default in values.yaml          | JSON Schema type     |
| ------------------------------- | -------------------- |
| `true` / `false` / `yes` / `no` | `"boolean"`          |
| Integer literal                 | `"integer"`          |
| Float literal                   | `"number"`           |
| Quoted string                   | `"string"`           |
| `[]`                            | `"array"`            |
| `{}`                            | `"object"`           |
| `null` or absent                | `["string", "null"]` |

YAML `yes`/`no` → `"boolean"`. Never change.

### Priority 4 — Safe fallback (no ask)

| Situation                                                                       | Fallback             |
| ------------------------------------------------------------------------------- | -------------------- |
| Dot-notation field in templates only, no type info anywhere                     | `["string", "null"]` |
| Enum-like field (mode/type/state) but no values found in templates/guide/consts | plain `"string"`     |
| Field only in guide, no type column, no default                                 | `"string"`           |
| Field not in guide, not in Go struct, not in values.yaml                        | skip                 |

Only escalate to Step 5 (ask) if the fallback would cause `values.yaml` validation FAIL.

### Enum detection — use what repo provides, never ask

Discover valid enum values in this priority order (stop at first hit):

1. Go `const` block for the field's custom type
2. Template `if eq .Values.foo "val1"` comparisons
3. Template `fail` / `assert` messages listing valid values
4. Guide "Possible values" / "One of" text

Use whatever is found. If nothing found → use plain `"string"` (no enum). Never ask.

---

## Step 5 — Ask only when truly stuck

**Ask only when ALL of the following are true:**

1. Type cannot be resolved by Steps 3-4 priorities
2. Safe fallback would cause `values.yaml` validation to FAIL
3. No inference possible from field name + context

Collect all such fields, ask in ONE batch after reading all sources:

```
Unable to resolve type for N fields — all others resolved automatically:

| Field | Value in values.yaml | Checked | Question |
|---|---|---|---|
| foo.bar | "xyz" | Go: not found, guide: not found | What type? |

Please clarify, or say "skip" to exclude.
```

**Never ask about:**

- Fields with any type info from Go/guide/default
- k8s standard types — patterns are known and built into this skill
- YAML `yes`/`no` booleans
- Enum values already found in templates/guide/consts
- Whether discovered enum values are "correct" — trust the repo
- Whether to skip ALL_CAPS deploy injections — classify per Step 3
- Anything in values.yaml — always has enough info for a type

**Default bias: apply fallback, never ask.**
If you feel the urge to ask about a field, stop — apply the fallback type instead
and note it at the end of the output as "Auto-resolved with fallback: field → type".
Asking is a last resort only when `values.yaml` itself fails validation against every
possible fallback type. In practice, this should be zero questions for any well-formed
Helm chart.

---

## Step 6 — Write values.schema.json

### Idempotency — re-run safety

If `values.schema.json` already exists for the chart, **do not rewrite it from scratch**.
Instead, diff what changed:

1. Load the existing schema into memory.
2. Compute the new schema from sources (steps 1–5) as a Python dict.
3. Compare with `deepdiff` or manual key-by-key comparison:
   ```bash
   pip install deepdiff --quiet --break-system-packages 2>/dev/null
   ```
   ```python
   from deepdiff import DeepDiff
   diff = DeepDiff(existing, new, ignore_order=True)
   print(diff)
   ```
4. Apply **only the changes** using targeted `Edit` tool calls (never full rewrite).
   - New field added → add only that property to the right `$defs` block.
   - Type changed → edit only that field's type.
   - Enum value added → edit only that enum array.
5. If diff is empty → schema is already up to date, report that and stop.

**Never reorder or reformat unchanged content.** Cosmetic churn (key reordering,
whitespace, moving `$defs` around) makes diffs unreadable and hides real changes.
Preserve the existing file's structure and ordering exactly; only append/modify
the specific JSON nodes that changed.

### Structure

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "<chart-name> values",
  "type": "object",
  "additionalProperties": true,
  "properties": {
    "topLevelKey": { "$ref": "#/$defs/topLevelKey" }
  },
  "$defs": {
    "topLevelKey": { "type": "object", ... }
  }
}
```

Every top-level key that is an object gets its own `$defs` block.
Scalar top-level keys (string/boolean/integer) can be inlined in `properties`.

### Rules

- Root object uses `additionalProperties: true` — unknown top-level keys (deploy-time
  injections, tooling flags) are allowed without validation. Known top-level keys are
  still strictly validated via their `$defs` entries.
- `additionalProperties: false` on every object inside `$defs` (strict for known fields)
- `additionalProperties: true` only for k8s open-ended types (affinity sub-terms,
  seLinuxOptions, any Go struct the CRD marks as x-kubernetes-preserve-unknown-fields)
- `additionalProperties: {type: string}` for `map[string]string` fields
- `"default"`: only from values.yaml. Do not invent.
- `"description"`: from guide. If absent, derive from field name.
- `"required"`: only when guide explicitly says Mandatory.

### Schema Patterns for k8s standard types

**`resourceRequirements`** — for `*v1.ResourceRequirements`:

```json
{
  "type": "object",
  "additionalProperties": false,
  "properties": {
    "requests": { "type": "object", "additionalProperties": { "type": "string" } },
    "limits": { "type": "object", "additionalProperties": { "type": "string" } },
    "claims": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["name"],
        "properties": {
          "name": { "type": "string" },
          "request": { "type": "string" }
        }
      }
    }
  }
}
```

**`affinity`** — for `*v1.Affinity`:

```json
{
  "type": ["object", "null"],
  "additionalProperties": false,
  "properties": {
    "nodeAffinity": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "preferredDuringSchedulingIgnoredDuringExecution": {
          "type": "array",
          "items": { "type": "object", "additionalProperties": true }
        },
        "requiredDuringSchedulingIgnoredDuringExecution": { "type": "object", "additionalProperties": true }
      }
    },
    "podAffinity": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "preferredDuringSchedulingIgnoredDuringExecution": {
          "type": "array",
          "items": { "type": "object", "additionalProperties": true }
        },
        "requiredDuringSchedulingIgnoredDuringExecution": {
          "type": "array",
          "items": { "type": "object", "additionalProperties": true }
        }
      }
    },
    "podAntiAffinity": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "preferredDuringSchedulingIgnoredDuringExecution": {
          "type": "array",
          "items": { "type": "object", "additionalProperties": true }
        },
        "requiredDuringSchedulingIgnoredDuringExecution": {
          "type": "array",
          "items": { "type": "object", "additionalProperties": true }
        }
      }
    }
  }
}
```

`nodeAffinity.requiredDuring...` is **object**; `podAffinity`/`podAntiAffinity` both use **arrays** for both preferred and required.

**`tolerations`** — for `[]v1.Toleration`:

```json
{
  "type": "array",
  "items": {
    "type": "object",
    "additionalProperties": false,
    "properties": {
      "key": { "type": "string" },
      "operator": { "type": "string", "enum": ["Equal", "Exists"] },
      "value": { "type": "string" },
      "effect": { "type": "string", "enum": ["NoSchedule", "PreferNoSchedule", "NoExecute"] },
      "tolerationSeconds": { "type": "integer" }
    }
  }
}
```

**`storageRequirements`** — for `*types.StorageRequirements` or equivalent:
Always verify field names against the actual Go struct (external packages can differ).
Standard shape (verify field names against the actual Go struct — external packages vary):

```json
{
  "type": "object",
  "additionalProperties": false,
  "properties": {
    "emptyDir": { "type": "boolean" },
    "waitPvcBound": { "type": "boolean" },
    "size": { "oneOf": [{ "type": "string" }, { "type": "array", "items": { "type": "string" } }] },
    "volumes": { "type": "array", "items": { "type": "string" } },
    "storageClasses": { "type": "array", "items": { "type": "string" } },
    "nodeLabels": { "type": "array", "items": { "type": "object", "additionalProperties": { "type": "string" } } },
    "matchLabelSelectors": {
      "type": "array",
      "items": { "type": "object", "additionalProperties": { "type": "string" } }
    },
    "mountSettings": { "type": "object", "additionalProperties": true }
  }
}
```

`matchLabelSelectors` is `[]map[string]string` — **array**, NOT object.
`size` is `[]string` but YAML accepts scalar `"5Gi"` → oneOf string/array.
`mountSettings` is `*v1.VolumeMount` → open object.

**TLS certificates block**:
Keys (e.g. `tls_key`, `tls_crt`, `ca_crt`) come from Go struct or guide. All `["string","null"]`.

---

## Step 6B — Cross-check union fields against written schema

**MANDATORY. Run immediately after writing values.schema.json, before Step 7.**

For every struct that appeared in the union table, verify the written `$defs` entry
contains every field from the union. Run this script:

```python
import re, json
from pathlib import Path
from collections import defaultdict

repo_root = "<repo_root>"
schema_path = "<chart_dir>/values.schema.json"

# Re-extract union table (same logic as Step 2 script)
files = list(Path(repo_root).rglob("*_types.go"))
structs = defaultdict(dict)
for f in files:
    src = f.read_text()
    for m in re.finditer(r'type (\w+) struct \{([^}]+)\}', src, re.S):
        sname, body = m.group(1), m.group(2)
        fields = {}
        for line in body.splitlines():
            tm = re.search(r'json:"([^,"]+)', line)
            gm = re.search(r'^\s+\w+\s+([\w\[\]*./]+)', line)
            if tm:
                fields[tm.group(1)] = gm.group(1) if gm else "?"
        if fields:
            structs[sname][str(f)] = fields

union_tables = {}
for sname, fdefs in structs.items():
    if len(fdefs) > 1:
        union = {}
        for fpath, fields in fdefs.items():
            for tag, gotype in fields.items():
                if tag not in union:
                    union[tag] = gotype
        union_tables[sname] = union

# Load written schema and collect all property keys per $def
schema = json.load(open(schema_path))
defs = schema.get("$defs", {})

def collect_props(defn):
    props = set(defn.get("properties", {}).keys())
    # also check oneOf/anyOf branches
    for branch_key in ("oneOf", "anyOf", "allOf"):
        for branch in defn.get(branch_key, []):
            props |= collect_props(branch)
    return props

failures = []
for sname, union in union_tables.items():
    # find matching $def by struct name lowercased or camelCase match
    def_key = None
    sname_lower = sname.lower()
    for k in defs:
        if k.lower() == sname_lower or k.lower() == sname_lower.replace("spec", ""):
            def_key = k
            break
    if def_key is None:
        # struct may map to a nested property — skip if not a top-level $def
        continue
    written = collect_props(defs[def_key])
    missing = set(union.keys()) - written
    if missing:
        failures.append((sname, def_key, sorted(missing)))

if not failures:
    print("Union cross-check: PASS — all union fields present in schema")
else:
    for sname, def_key, missing in failures:
        print(f"CROSS-CHECK FAIL: {sname} -> $defs/{def_key}")
        print(f"  Missing fields: {missing}")
        print(f"  Fix: add these to the $defs/{def_key} properties block before proceeding.")
```

**If any CROSS-CHECK FAIL is printed: stop, add the missing fields to the schema, re-run
this script until it prints PASS. Only then proceed to Step 7.**

This catches the exact failure mode where the union table was produced but fields were
silently dropped when writing the schema.

---

## Step 7 — Validate schema

```bash
pip install jsonschema pyyaml --quiet --break-system-packages 2>/dev/null
```

### 7A. values.yaml must pass

```python
import yaml, json, jsonschema
schema = json.load(open("values.schema.json"))
data = yaml.safe_load(open("values.yaml")) or {}
jsonschema.validate(instance=data, schema=schema)
```

### 7B. Valid edge cases must pass

- `{}` — empty override
- Each enum with every valid value from the repo
- `null` for all nullable fields
- Arrays with multiple items for every array field
- Affinity with all three sub-types
- resourceRequirements with non-standard resource key
- oneOf fields with both variants

### 7C. Invalid values must be rejected

- Unknown top-level key — NOTE: root `additionalProperties: true`, so only nested unknown keys fail
- Invalid enum value
- Wrong type
- Unknown nested field in strict object
- `[]map[string]string` field set to plain object

### 7D. Validate override/deployment files

After values.yaml passes, scan the repo for real deployment override files and validate
each. These files expose fields that values.yaml defaults leave empty.

**IMPORTANT:** Exclude template files - they contain `{{ }}` syntax that breaks yaml.safe_load.
Only validate actual values override files:

```bash
find <repo_root> \
  \( -name "*-values.yaml" -o -name "values-*.yaml" \) \
  ! -path "*/templates/*" \
  2>/dev/null | sort
```

If the user provides an external override directory (e.g. a separate pipeline/infra
repo), include all `.yml` / `.yaml` files from that path in the same validation loop:

```bash
find <external_override_dir> \( -name "*.yml" -o -name "*.yaml" \) 2>/dev/null | sort
```

```python
import os, yaml, json, jsonschema
from copy import deepcopy

schema = json.load(open("values.schema.json"))
defaults = yaml.safe_load(open("values.yaml")) or {}
failures = []

def merge_dicts(base, override):
    """Deep merge override into base (Helm's merge behavior)."""
    result = deepcopy(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value
    return result

for fpath in override_files:
    override = yaml.safe_load(open(fpath)) or {}
    # Merge override with defaults BEFORE validation (matches Helm behavior)
    merged = merge_dicts(defaults, override)
    try:
        jsonschema.validate(instance=merged, schema=schema)
    except jsonschema.ValidationError as e:
        path = " -> ".join(str(p) for p in e.absolute_path)
        failures.append((fpath, path, e.message))
        print(f"FAIL {fpath}: [{path}] {e.message}")
if not failures:
    print("All override files pass")
```

**CRITICAL:** Override files are validated AFTER merging with `values.yaml` defaults, matching
Helm's behavior. A partial override like `replicaCount: 2` passes validation because the schema
is applied to the merged result (with `image` from defaults), not to the override in isolation.

`Additional properties are not allowed` on nested objects = **schema gap** (missing field).
Add the field using guide/Go type. Only wrong types and invalid enums are errors in the
override file itself.

Fix all failures before reporting done.

---

## Step 8 — Fix loop

| Failure pattern                                           | Fix                                                                                                                                        |
| --------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| `Additional properties not allowed: 'X'` on nested object | Add `X` to that $def — it is a real field the schema missed                                                                                |
| `None is not of type 'string'`                            | Change to `["string", "null"]`                                                                                                             |
| `'val' is not of type 'array'` on a `[]Struct` field      | Use `oneOf: [{$ref: structDef}, {type: array, items: {$ref: structDef}}]` — override files often set single-element lists as plain objects |
| `'val' is not of type 'array'` on a `[]string` field      | Use `oneOf: [{type: string}, {type: array, items: {type: string}}]`                                                                        |
| `'val' is not one of [enum]`                              | Re-check guide/templates for valid values                                                                                                  |
| `'val' is not of type 'boolean'`                          | YAML `yes`/`no` → schema type `"boolean"` is correct, do not change                                                                        |
| Key missing under `additionalProperties: false`           | Add the missing key                                                                                                                        |

---

## Output

Single file: `<chart_dir>/values.schema.json`
Never modify `values.yaml`.
Never create test files — run validation inline with Python.
