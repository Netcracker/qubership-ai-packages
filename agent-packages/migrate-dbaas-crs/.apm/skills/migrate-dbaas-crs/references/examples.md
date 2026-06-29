# DBaaS Migration Examples

## JSON DatabaseDeclaration To InternalDatabase

Before:

```json
{
  "apiVersion": "nc.core.dbaas/v3",
  "kind": "DatabaseDeclaration",
  "declarations": [
    {
      "classifierConfig": {
        "classifier": {
          "scope": "service",
          "microserviceName": "{{$SERVICE_NAME}}",
          "customKeys": {
            "logicalDBName": "configs"
          }
        }
      },
      "type": "postgresql",
      "versioningConfig": {
        "approach": "clone"
      }
    }
  ]
}
```

After:

```yaml
apiVersion: dbaas.netcracker.com/v1
kind: InternalDatabase
metadata:
  name: configs-db
  namespace: "{{ .Values.NAMESPACE }}"
spec:
  classifier:
    scope: service
    microserviceName: "{{ .Values.SERVICE_NAME }}"
    customKeys:
      logicalDBName: configs
  type: postgresql
  versioningConfig:
    approach: clone
```

## Generic YAML DatabaseDeclaration To InternalDatabase

Before:

```yaml
apiVersion: core.netcracker.com/v1
kind: DBaaS
subKind: DatabaseDeclaration
metadata:
  name: db-declaration-1
  namespace: "{{ .Values.NAMESPACE }}"
  labels:
    app.kubernetes.io/instance: "{{ .Values.SERVICE_NAME }}"
spec:
  classifierConfig:
    classifier:
      scope: service
      microserviceName: "{{ .Values.SERVICE_NAME }}"
  lazy: false
  type: postgresql
  initialInstantiation:
    approach: clone
    sourceClassifier:
      scope: service
      microserviceName: source-microservice
```

After:

```yaml
apiVersion: dbaas.netcracker.com/v1
kind: InternalDatabase
metadata:
  name: db-declaration-1
  namespace: "{{ .Values.NAMESPACE }}"
spec:
  classifier:
    scope: service
    microserviceName: "{{ .Values.SERVICE_NAME }}"
  type: postgresql
  initialInstantiation:
    approach: clone
    sourceClassifier:
      scope: service
      microserviceName: source-microservice
```

## Extra Classifier Keys

Before:

```json
{
  "classifierConfig": {
    "classifier": {
      "scope": "service",
      "microserviceName": "dbaas-spring-service",
      "transactional": true
    }
  },
  "type": "postgresql"
}
```

After:

```yaml
apiVersion: dbaas.netcracker.com/v1
kind: InternalDatabase
metadata:
  name: service-db
spec:
  classifier:
    scope: service
    microserviceName: dbaas-spring-service
    extraKeys:
      transactional: true
  type: postgresql
```

## JSON DbPolicy To DatabaseAccessPolicy

Before:

```json
{
  "apiVersion": "nc.core.dbaas/v3",
  "kind": "DbPolicy",
  "services": [
    {
      "name": "externalService",
      "roles": ["ro"]
    }
  ],
  "policy": [
    {
      "type": "postgresql",
      "defaultRole": "admin",
      "additionalRole": ["rw", "ro"]
    }
  ],
  "disableGlobalPermissions": "false"
}
```

After:

```yaml
apiVersion: dbaas.netcracker.com/v1
kind: DatabaseAccessPolicy
metadata:
  name: database-access-policy
  namespace: "{{ .Values.NAMESPACE }}"
spec:
  microserviceName: "{{ .Values.SERVICE_NAME }}"
  services:
    - name: externalService
      roles:
        - ro
  policy:
    - type: postgresql
      defaultRole: admin
      additionalRole:
        - rw
        - ro
  disableGlobalPermissions: false
```

## Split Database Declaration

Before JSON with two `declarations[]` entries must become two `InternalDatabase` resources:

```yaml
apiVersion: dbaas.netcracker.com/v1
kind: InternalDatabase
metadata:
  name: transactional-db
  namespace: "{{ .Values.NAMESPACE }}"
spec:
  classifier:
    scope: service
    microserviceName: "{{ .Values.SERVICE_NAME }}"
  type: postgresql
---
apiVersion: dbaas.netcracker.com/v1
kind: InternalDatabase
metadata:
  name: configs-db
  namespace: "{{ .Values.NAMESPACE }}"
spec:
  classifier:
    scope: service
    microserviceName: "{{ .Values.SERVICE_NAME }}"
    customKeys:
      logicalDBName: configs
  type: postgresql
  versioningConfig:
    approach: new
```
