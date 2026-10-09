---
name: values-schema-generator
description: Generate or update a strict values.schema.json for one Helm chart, with field names, types, and enum values taken from the repository's own values.yaml, Go API types, templates, installation guide, and override files, then validate it through helm lint against every deployment's ordered values stack. Use only when the user asks to generate, create, or update a values schema for a Helm chart, or to validate Helm values against one.
---

# Helm values schema generator

Generate a strict, validated `values.schema.json` for one Helm chart at a time. The schema sits next to the chart's
`values.yaml`.

Every field name, type, and enum value comes from the repository: `values.yaml`, Go `*_types.go`, CRDs, templates, the
installation guide, and the override files. Never assume a field or an enum value that the repository does not show.

Discover everything and ask almost nothing. Every field gets a type from the priority rules in step 4 or from the safe
fallback. Ask only when a default value in `values.yaml` fails every fallback type (step 5). When in doubt, write the
schema and let the validation loop in step 8 expose the gap.

## Requirements

- `helm` on the `PATH`. Step 8 validates through `helm lint`, because Helm's own value coalescing (defaults, then each
  `-f` file in order, with `null` deleting a key) is what the schema is checked against at install time. If `helm` is
  missing, stop and tell the user; do not substitute a hand-written merge.
- `python3` with PyYAML for the extraction scripts. If PyYAML is missing, ask the user to install it.

## Pick the chart

If the user has not named a chart, list every directory that holds a `Chart.yaml` (path relative to the repository
root) and ask the user to pick one. Do not start until a chart is chosen. Process one chart per invocation; when it is
done, offer to continue with the next one.

## Step 1. Locate the sources

```bash
# Charts and their values files
find <repo_root> -name Chart.yaml | sort
find <repo_root> -name values.yaml | sort

# Go API types and the module that pins their external packages
find <repo_root> -name '*_types.go' -not -path '*/vendor/*' | sort
find <repo_root> -maxdepth 3 -name go.mod | sort

# CRDs
grep -rl --include='*.yaml' --include='*.yml' 'openAPIV3Schema' <repo_root> | sort

# Installation guides with a parameters section
grep -rlE --include='*.md' '^#{1,3} .*Parameters' <repo_root> | sort

# Override files: test values and named overrides; never files under templates/
find <repo_root> \( -path '*/tests/values/*.yaml' -o -path '*/tests/values/*.yml' \
  -o -name '*-values.yaml' -o -name 'values-*.yaml' \) -not -path '*/templates/*' | sort
```

If the user named an external override directory (a pipeline or infrastructure repository), list its files too:

```bash
find <external_override_dir> \( -name '*.yaml' -o -name '*.yml' \) -not -path '*/templates/*' | sort
```

Print every path found before you continue.

### Find each deployment's values stack

Override files are layers, not complete deployments. A production deployment can take `values-common.yaml` and then
`values-prod.yaml`, and only the two together are valid. Record, for each deployment, the ordered list of files Helm
receives:

```bash
grep -rnE --include='*.yml' --include='*.yaml' --include='*.sh' --include='Makefile' --include='*.mk' \
  -e '(-f|--values)[ =][^ ]+\.ya?ml' <repo_root> <external_override_dir> 2>/dev/null
grep -rnE --include='helmfile*.yaml' --include='*application*.yaml' \
  -e 'valueFiles:|values:' <repo_root> <external_override_dir> 2>/dev/null
```

These cover `helm install|upgrade|template` calls in CI and scripts, `helmfile` releases, and Argo CD `valueFiles`.
If the order of an override file cannot be found, ask the user once, in a single batch, which files each deployment
stacks and in what order. A file the user calls standalone is a one-file stack.

Every key path in every override file is a real field that the schema must accept. Collect them in step 2 so the
schema is built with them from the start, not patched in step 8.

## Step 2. Read all sources

Read all of these before you write any schema.

1. **`values.yaml`**: the whole file, every key and default.
1. **Installation guide**: the parameters section. Each table row gives the key path, type, default, description, and
   whether it is mandatory. Read every subsection that covers this chart. If there is no guide, continue without one.
1. **Go types**: the authoritative source of field types. Read every `*_types.go` in the repository, not only the one
   nearest to the chart. A chart that deploys an operator and also creates the CRs it consumes maps values to types
   in sibling modules, and the chart's own types file often carries a shorter copy of a struct that another module
   defines in full.

   A Go type is identified by its package directory and its name, such as `operator/api/v1.FooSpec`. Two structs
   with the same name in different packages are different types unless you verify otherwise: `first.Config` and
   `second.Config` can be unrelated. Combine definitions only when they are the same logical type, such as a services
   module carrying a shorter copy of the struct the operator's CRD defines in full.

   Save this script in a scratch directory outside the repository (`mktemp -d`), as `<scratch>/go_structs.py`, and
   run it with the repository root. It prints every struct with its JSON fields, then a verdict for each name that
   several packages define:

   ```python
   """List Go structs by package and check schema definitions against them.

   Usage:
     go_structs.py <repo_root>                          list structs and same-name groups
     go_structs.py <repo_root> <schema.json> <map.txt>  check each mapped $defs entry
   map.txt holds one line per $defs entry: <$defs key> = <type> [<type> ...],
   with each <type> written as <package dir>.<StructName>, as the first form prints it.
   """
   import json
   import re
   import sys
   from collections import defaultdict
   from pathlib import Path

   STRUCT_START = re.compile(r"^type (\w+) struct \{")
   FIELD = re.compile(r'^\s*\w+\s+([\w\[\]*.]+)\s+`[^`]*json:"([^,"]+)')
   ANONYMOUS_END = re.compile(r'^\s*\}()\s*`[^`]*json:"([^,"]+)')  # tag of an inline struct field

   repo_root = Path(sys.argv[1]).resolve()
   types = {}  # "<package dir>.<StructName>" -> {json name: Go type}
   for path in sorted(repo_root.rglob("*_types.go")):
       if "vendor" in path.parts:
           continue
       package = path.parent.relative_to(repo_root).as_posix()
       name, depth, fields = None, 0, {}
       for line in path.read_text(encoding="utf-8").splitlines():
           if name is None:
               start = STRUCT_START.match(line)
               if start:
                   name, depth, fields = start.group(1), 1, {}
               continue
           field = None
           if depth == 1:
               field = FIELD.match(line)
           elif depth == 2:
               field = ANONYMOUS_END.match(line)
           if field and field.group(2) != "-":
               fields[field.group(2)] = field.group(1) or "struct"
           depth += line.count("{") - line.count("}")
           if depth <= 0:
               if fields:
                   types[f"{package}.{name}"] = fields
               name = None

   def base_type(go_type):
       return re.sub(r"\w+\.", "", go_type.replace("*", ""))

   if len(sys.argv) == 2:
       groups = defaultdict(list)
       for type_id, fields in sorted(types.items()):
           print(f"{type_id}: {', '.join(sorted(fields))}")
           groups[type_id.rsplit(".", 1)[1]].append(type_id)
       for name, members in sorted(groups.items()):
           if len(members) < 2:
               continue
           sets = sorted((set(types[m]) for m in members), key=len)
           shared = set.intersection(*sets)
           conflicts = sorted(f for f in shared if len({base_type(types[m][f]) for m in members}) > 1)
           if not shared or conflicts:
               verdict = "DIFFERENT"
           elif all(a <= b for a, b in zip(sets, sets[1:])):
               verdict = "SAME"
           else:
               verdict = "UNCERTAIN"
           print(f"=== {name}: {verdict}; shared {sorted(shared)}; conflicting types {conflicts}")
           for member in members:
               print(f"  {member}")
       sys.exit(0)

   def properties(node):
       found = set(node.get("properties", {}))
       for key in ("oneOf", "anyOf", "allOf"):
           for branch in node.get(key, []):
               found |= properties(branch)
       return found

   defs = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8")).get("$defs", {})
   failed = False
   for line in Path(sys.argv[3]).read_text(encoding="utf-8").splitlines():
       if not line.strip() or line.lstrip().startswith("#"):
           continue
       key, _, refs = (part.strip() for part in line.partition("="))
       unknown = [ref for ref in refs.split() if ref not in types]
       if key not in defs or unknown or not refs:
           failed = True
           print(f"FAIL {key}: missing $defs entry or unknown types {unknown}")
           continue
       missing = sorted(set().union(*(types[ref] for ref in refs.split())) - properties(defs[key]))
       if missing:
           failed = True
           print(f"FAIL $defs/{key} ({refs}): missing {missing}")
   print("FAIL" if failed else "PASS")
   ```

   Decide which types to combine from the verdicts:

   - `DIFFERENT`: the definitions share no field, or a shared field has a different Go type. Never combine them.
   - `SAME`: each definition's fields are a subset of the next, with matching Go types. Combine them only after you
     confirm both are behind the same chart value: the chart's templates render a resource whose `kind` is the CRD
     that the other package defines, or the chart's types file imports that package. Otherwise keep them separate.
   - `UNCERTAIN`: the definitions overlap without one containing the other. Add the group to the step 5 batch of
     questions; until the user answers, use only the definition in the package the chart's own values map to.

   Then write `<scratch>/defs-map.txt`, one line per `$defs` entry backed by Go types, listing the type or the
   combined types it represents:

   ```text
   foo = operator/api/v1.FooSpec services/api.FooSpec
   storage = operator/api/v1.StorageSpec
   ```

   Every field of the mapped types appears in that `$defs` entry. Do not write a `$defs` entry before the map exists.

   Find enum values in `const` blocks:

   ```bash
   grep -n -A 20 '^const (' <types_file>
   ```

   For a field whose type comes from an external package (such as `types.StorageRequirements`), read the package
   version from `go.mod`, then read the type from the module cache:

   ```bash
   find "$(go env GOMODCACHE)" -path '*<module-path>@<version>*' -name '*.go' | head
   ```

1. **CRDs**: for complex Kubernetes types (affinity, tolerations), read only the `openAPIV3Schema` property shapes
   you need. Do not copy a whole CRD.
1. **Template references**: every `.Values` path in the templates and helpers, including several on one line:

   ```bash
   grep -rhoE --include='*.yaml' --include='*.yml' --include='*.tpl' \
     '\.Values(\.[A-Za-z0-9_]+)+' <chart_dir>/templates <chart_dir>/tests 2>/dev/null \
     | sed 's/^\.Values\.//' | sort -u
   ```

   Helpers (`_helpers.tpl`) often reference fields that neither `values.yaml` nor the guide lists. They are real
   fields. Look up `index .Values "<key>"` calls by hand; the pattern above does not match them.

   Enum candidates from comparisons, in either argument order:

   ```bash
   grep -rhoE --include='*.yaml' --include='*.yml' --include='*.tpl' \
     'eq \.Values(\.[A-Za-z0-9_]+)+ "[^"]*"|eq "[^"]*" \.Values(\.[A-Za-z0-9_]+)+' \
     <chart_dir>/templates 2>/dev/null | sort -u
   ```

   Enum lists in `fail` and `required` messages. Filter the calls first, then extract their strings:

   ```bash
   grep -rhwE --include='*.yaml' --include='*.yml' --include='*.tpl' 'fail|required' \
     <chart_dir>/templates 2>/dev/null | grep -oE '"[^"]+"' | sort -u
   ```

1. **Override files**: every key path in every file from step 1, compared with `values.yaml`:

   ```python
   import sys
   import yaml

   def paths(node, prefix=""):
       found = set()
       if isinstance(node, dict):
           for key, value in node.items():
               full = f"{prefix}.{key}" if prefix else str(key)
               found.add(full)
               found |= paths(value, full)
       elif isinstance(node, list):
           for item in node:
               found |= paths(item, prefix)
       return found

   def load(path):
       with open(path, encoding="utf-8") as stream:
           return yaml.safe_load(stream) or {}

   chart_values, *override_files = sys.argv[1:]
   extra = set().union(*(paths(load(f)) for f in override_files)) - paths(load(chart_values))
   print(f"{len(extra)} key paths in overrides are not in values.yaml:")
   for path in sorted(extra):
       print(f"  {path}")
   ```

   Run it as `python3 <script> <chart_dir>/values.yaml <override files...>`. Resolve the type of every printed path
   with the step 4 priorities. A path missed here shows up in step 8 as `additional properties ... not allowed`.

## Step 3. Classify flat upper-case keys

Before you resolve types, classify every flat key in upper case or mixed case found in the templates or in
`values.yaml`. Apply these rules without asking.

Include as a schema field:

- any key present in `values.yaml`, whatever its case;
- any dot-notation path (`.Values.foo.bar`).

Skip, because the deployer injects them at deploy time:

- a flat upper-case key (`^[A-Z][A-Z0-9_]*$`, no dots) that is not in `values.yaml`, such as `NAMESPACE`,
  `DB_PASSWORD`, or `CLOUD_HOST`;
- `deployDescriptor` and `deployDescriptorBase64`;
- a flat camel-case key that shadows a dot-notation field already in the schema, such as `fooImage` when `foo.image`
  exists.

## Step 4. Resolve types

For every field, stop at the first rule that resolves its type. Never ask when a rule resolves it.

### Priority 1: Go struct for types, Go struct plus guide for the field set

The Go struct defines field types. The field set of an object is the union of the Go struct and the guide: a chart's
`values.yaml` can carry deployment parameters (such as `<component>.storage` or `<component>.resources`) that feed a
different resource and appear only in the guide. Never let the Go struct alone truncate an object's fields.

| Go type | JSON Schema |
| --- | --- |
| `string` | `"string"` |
| `bool` | `"boolean"` |
| `int`, `int32`, `int64` | `"integer"` |
| `float32`, `float64` | `"number"` |
| `[]string` | `array`, `items: {type: string}` |
| `[]SomeStruct` | `array`; if an override sets it as a single object, `oneOf: [{$ref}, {type: array, items: {$ref}}]` |
| `map[string]string` | `object`, `additionalProperties: {type: string}` |
| `map[string]SomeStruct` | `object`, `additionalProperties: true` |
| `*v1.ResourceRequirements` | the `resourceRequirements` definition below |
| `*v1.Affinity` | the `affinity` definition below |
| any other pointer `*T` | the type of `T`, nullable: `["<T>", "null"]` |

A map type whose default is absent or `null` is `["object", "null"]`; with a non-null default it is `"object"`.

A `[]string` field whose `values.yaml` default is a scalar string (`''`, `"5Gi"`) accepts both forms:

```json
"oneOf": [{ "type": "string" }, { "type": "array", "items": { "type": "string" } }]
```

### Priority 2: the guide's type column

Use it for a field the Go struct does not have. When the type column and the default disagree, trust the default.
After resolving types from the Go struct, also scan every guide row under the same object prefix and add the fields
the struct missed.

### Priority 3: the default in `values.yaml`

| Default | JSON Schema |
| --- | --- |
| `true`, `false`, `yes`, `no` | `"boolean"` |
| integer literal | `"integer"` |
| float literal | `"number"` |
| quoted string | `"string"` |
| `[]` | `"array"` |
| `{}` | `"object"` |
| `null` or absent | `["string", "null"]` |

YAML 1.1 `yes` and `no` are booleans; keep them `"boolean"`.

### Priority 4: safe fallback

| Situation | Type |
| --- | --- |
| Dot-notation field only in templates, no type information anywhere | `["string", "null"]` |
| Enum-like field (`mode`, `type`, `state`) with no values found | `"string"`, no `enum` |
| Field only in the guide, with no type column and no default | `"string"` |
| Field not in the guide, the Go struct, or `values.yaml` | skip |

### Enum values

Take enum values from the first source that has them:

1. the Go `const` block for the field's type;
1. template comparisons (`eq .Values.foo "value"`);
1. template `fail` or `required` messages that list the valid values;
1. the guide's "Possible values" or "One of" text.

If no source lists values, use `"string"` without `enum`.

## Step 5. Ask only when stuck

Ask only when the step 4 rules resolve no type and every fallback type would make `values.yaml` fail validation, or
when step 2 marks a group of same-named Go types `UNCERTAIN`. Ask once, in one batch, after reading every source; for
an `UNCERTAIN` group, ask whether its types are one logical type and list the package of each:

```text
Unable to resolve the type of N fields; all other fields were resolved automatically.

| Field | Value in values.yaml | Checked | Question |
| --- | --- | --- | --- |
| foo.bar | "xyz" | Go: not found; guide: not found | Which type? |

Answer per field, or reply "skip" to leave a field out of the schema.
```

Do not ask about fields with any Go, guide, or default information; standard Kubernetes types; YAML booleans; enum
values the repository lists; or upper-case keys that step 3 classifies. When you apply a fallback, list it at the end of
the report as `Auto-resolved with fallback: <field> -> <type>`. A well-formed chart needs no questions.

## Step 6. Write `values.schema.json`

### Updating an existing schema

If the chart already has a `values.schema.json`, do not rewrite it. Build the new schema in memory from steps 1 to 5,
compare it with the existing file key by key, and edit only the nodes that differ: add a missing property to its
`$defs` entry, change one field's type, extend one `enum`. Keep the existing key order, formatting, and placement of
`$defs`; reformatting unchanged nodes hides the real change in the diff. If nothing differs, report that the schema is
up to date and stop.

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
    "topLevelKey": { "type": "object", "additionalProperties": false, "properties": {} }
  }
}
```

Every top-level object key gets its own `$defs` entry. Scalar top-level keys can be inlined in `properties`.

### Rules

- The root object has `additionalProperties: true`, so deploy-time keys pass. Known top-level keys are still checked
  through their `$defs` entries.
- Every object inside `$defs` has `additionalProperties: false`.
- Use `additionalProperties: true` only for open-ended Kubernetes types: affinity terms, `seLinuxOptions`, and any
  struct the CRD marks `x-kubernetes-preserve-unknown-fields`.
- A `map[string]string` field has `additionalProperties: {type: string}`.
- `default` comes only from `values.yaml`.
- `description` comes from the guide; without one, derive it from the field name.
- `required` only where the guide marks the field mandatory. Helm checks `required` against the merged values, so a
  key that `values.yaml` supplies never fails it.

### Kubernetes type definitions

`resourceRequirements`, for `*v1.ResourceRequirements`:

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

`affinity`, for `*v1.Affinity`. `nodeAffinity.requiredDuringSchedulingIgnoredDuringExecution` is an object; every other
term is an array:

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

`tolerations`, for `[]v1.Toleration`:

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

`storageRequirements`, for `*types.StorageRequirements` or an equivalent struct. External packages differ, so check
every field name against the struct the repository's `go.mod` pins:

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

- `matchLabelSelectors` is `[]map[string]string`: an array, not an object.
- `size` is `[]string`, but YAML also accepts a scalar such as `"5Gi"`, hence the `oneOf`.
- `mountSettings` is `*v1.VolumeMount`: an open object.

TLS certificate keys (such as `tls_key`, `tls_crt`, `ca_crt`) come from the Go struct or the guide; each one is
`["string", "null"]`.

## Step 7. Cross-check the Go fields

Run this step right after writing the schema, before step 8. Run the step 2 script again with the schema and the map:

```bash
python3 <scratch>/go_structs.py <repo_root> <chart_dir>/values.schema.json <scratch>/defs-map.txt
```

On any `FAIL` line, add the missing fields to that `$defs` entry, or correct the map if it names the wrong type, and
run the script again until it prints `PASS`. This catches fields that a mapped type has but that were dropped while
writing the schema. List the map, and every combined group, in the final report.

## Step 8. Validate through Helm

Validate with `helm lint`. It merges the chart's `values.yaml` with each `-f` file in order, deletes keys set to
`null`, and checks the schema against the result, which is what `helm install` does. If `Chart.yaml` declares
dependencies and `<chart_dir>/charts/` is missing them, run `helm dependency build <chart_dir>` first, or ask the user
when it needs credentials.

Read only the schema errors. Helm prints them as `values don't meet the specifications of the schema(s)`, followed by
one line per violation with its path. Report any other lint error to the user, but do not change the schema for it.

Write edge-case files to the scratch directory, never into the chart.

### 8A. The chart defaults pass

```bash
helm lint <chart_dir>
```

### 8B. Valid edge cases pass

Write each case as a small override file and lint it alone on top of the defaults (`helm lint <chart_dir> -f <case>`):

- an empty file;
- every enum field set to each value the repository lists;
- `null` for each nullable field;
- several items in each array field;
- an affinity with all three term types;
- `resources` with a non-standard resource name;
- each `oneOf` field in both forms.

### 8C. Invalid values fail

Each case must make `helm lint` fail with a schema error:

- an unknown key inside a strict object (an unknown top-level key passes, because the root allows additional keys);
- a value outside an enum;
- a value of the wrong type;
- a plain object for a `[]map[string]string` field.

### 8D. Every deployment's values stack passes

Lint each stack recorded in step 1 with its files in deployment order:

```bash
helm lint <chart_dir> -f <first layer> -f <second layer>
```

Lint an override file that belongs to no known stack on its own (`-f <file>`). If it fails only on a value that
another layer would supply, such as a field required once a feature is turned on, ask the user which files the
deployment stacks. Do not weaken the schema to make a partial layer pass.

An `additional properties ... not allowed` error on a nested object is a gap in the schema: add the field with its
type from the Go struct or the guide. A wrong type or an invalid enum value is an error in the override file; report
it to the user. Fix every schema gap before you report the work as done.

## Step 9. Fix loop

| Failure | Fix |
| --- | --- |
| Additional property `X` not allowed on a nested object | Add `X` to that `$defs` entry; it is a real field the schema missed |
| `null` where a string is expected | Change the type to `["string", "null"]` |
| Object where an array is expected, on a `[]Struct` field | `oneOf: [{$ref: <def>}, {type: array, items: {$ref: <def>}}]`; overrides often set a single item as an object |
| String where an array is expected, on a `[]string` field | `oneOf: [{type: string}, {type: array, items: {type: string}}]` |
| Value not in `enum` | Check the templates, consts, and guide again for valid values |
| String where a boolean is expected | YAML `yes`/`no` is a boolean in `values.yaml`; keep `"boolean"` and report the quoted value in the override |
| Missing required property | Check that the guide marks it mandatory and that a layer of the deployment supplies it |

## Output

The only file you write is `<chart_dir>/values.schema.json`. Never modify `values.yaml`, and never add test files to
the repository; edge-case files live in the scratch directory and are deleted at the end.
