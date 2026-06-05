---
name: kubernetes
description: |
  Kubernetes 배포 설정, Helm 차트를 구현합니다.
metadata:
  category: "💻 개발"
  version: "1.0.0"
---
# Kubernetes Skill

Kubernetes 배포 설정, Helm 차트를 구현합니다.

## Triggers

- "kubernetes", "k8s", "helm", "쿠버네티스", "배포"

---

## Input

| 항목 | 필수 | 설명 |
|------|------|------|
| `projectPath` | ✅ | 프로젝트 경로 |

---

## Output

### Directory Structure

```
k8s/
├── base/
│   ├── kustomization.yaml
│   ├── namespace.yaml
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── configmap.yaml
│   ├── secret.yaml
│   ├── hpa.yaml
│   └── ingress.yaml
├── overlays/
│   ├── development/
│   │   ├── kustomization.yaml
│   │   └── patches/
│   ├── staging/
│   │   ├── kustomization.yaml
│   │   └── patches/
│   └── production/
│       ├── kustomization.yaml
│       └── patches/
└── helm/
    └── fastapi-app/
        ├── Chart.yaml
        ├── values.yaml
        └── templates/
```

### Namespace

```yaml
# k8s/base/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: fastapi-app
  labels:
    app: fastapi-app
    environment: production
```

### Deployment

```yaml
# k8s/base/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fastapi-app
  labels:
    app: fastapi-app
    component: api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: fastapi-app
      component: api
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  template:
    metadata:
      labels:
        app: fastapi-app
        component: api
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "8000"
        prometheus.io/path: "/metrics"
    spec:
      serviceAccountName: fastapi-app
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 1000
      containers:
        - name: api
          image: myregistry/fastapi-app:latest
          imagePullPolicy: Always
          ports:
            - name: http
              containerPort: 8000
              protocol: TCP
          env:
            - name: ENVIRONMENT
              value: "production"
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: fastapi-app-secrets
                  key: database-url
            - name: REDIS_URL
              valueFrom:
                secretKeyRef:
                  name: fastapi-app-secrets
                  key: redis-url
            - name: SECRET_KEY
              valueFrom:
                secretKeyRef:
                  name: fastapi-app-secrets
                  key: secret-key
          envFrom:
            - configMapRef:
                name: fastapi-app-config
          resources:
            requests:
              cpu: "100m"
              memory: "256Mi"
            limits:
              cpu: "500m"
              memory: "512Mi"
          livenessProbe:
            httpGet:
              path: /health
              port: http
            initialDelaySeconds: 10
            periodSeconds: 10
            timeoutSeconds: 5
            failureThreshold: 3
          readinessProbe:
            httpGet:
              path: /health/ready
              port: http
            initialDelaySeconds: 5
            periodSeconds: 5
            timeoutSeconds: 3
            failureThreshold: 3
          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            capabilities:
              drop:
                - ALL
          volumeMounts:
            - name: tmp
              mountPath: /tmp
      volumes:
        - name: tmp
          emptyDir: {}
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
            - weight: 100
              podAffinityTerm:
                labelSelector:
                  matchExpressions:
                    - key: app
                      operator: In
                      values:
                        - fastapi-app
                topologyKey: kubernetes.io/hostname
      topologySpreadConstraints:
        - maxSkew: 1
          topologyKey: topology.kubernetes.io/zone
          whenUnsatisfiable: ScheduleAnyway
          labelSelector:
            matchLabels:
              app: fastapi-app
```

### Service

```yaml
# k8s/base/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: fastapi-app
  labels:
    app: fastapi-app
spec:
  type: ClusterIP
  ports:
    - port: 80
      targetPort: http
      protocol: TCP
      name: http
  selector:
    app: fastapi-app
    component: api
```

### ConfigMap

```yaml
# k8s/base/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: fastapi-app-config
data:
  LOG_LEVEL: "INFO"
  CORS_ORIGINS: "https://app.example.com"
  MAX_CONNECTIONS: "100"
  REQUEST_TIMEOUT: "30"
```

### Secret (Sealed Secret)

```yaml
# k8s/base/secret.yaml
apiVersion: bitnami.com/v1alpha1
kind: SealedSecret
metadata:
  name: fastapi-app-secrets
spec:
  encryptedData:
    database-url: AgBy3i... # Encrypted value
    redis-url: AgCtr8...    # Encrypted value
    secret-key: AgDwe1...   # Encrypted value
```

### HPA (Horizontal Pod Autoscaler)

```yaml
# k8s/base/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: fastapi-app
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: fastapi-app
  minReplicas: 3
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
    - type: Pods
      pods:
        metric:
          name: http_requests_per_second
        target:
          type: AverageValue
          averageValue: "100"
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
        - type: Percent
          value: 10
          periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
        - type: Percent
          value: 100
          periodSeconds: 15
        - type: Pods
          value: 4
          periodSeconds: 15
      selectPolicy: Max
```

### Ingress

```yaml
# k8s/base/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: fastapi-app
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/proxy-body-size: "10m"
    nginx.ingress.kubernetes.io/rate-limit: "100"
    nginx.ingress.kubernetes.io/rate-limit-window: "1m"
spec:
  tls:
    - hosts:
        - api.example.com
      secretName: fastapi-app-tls
  rules:
    - host: api.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: fastapi-app
                port:
                  number: 80
```

### PodDisruptionBudget

```yaml
# k8s/base/pdb.yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: fastapi-app
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app: fastapi-app
```

### ServiceAccount

```yaml
# k8s/base/serviceaccount.yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: fastapi-app
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: fastapi-app
rules:
  - apiGroups: [""]
    resources: ["configmaps", "secrets"]
    verbs: ["get", "list", "watch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: fastapi-app
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: fastapi-app
subjects:
  - kind: ServiceAccount
    name: fastapi-app
```

### NetworkPolicy

```yaml
# k8s/base/networkpolicy.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: fastapi-app
spec:
  podSelector:
    matchLabels:
      app: fastapi-app
  policyTypes:
    - Ingress
    - Egress
  ingress:
    # Allow traffic from ingress controller
    - from:
        - namespaceSelector:
            matchLabels:
              name: ingress-nginx
          podSelector:
            matchLabels:
              app.kubernetes.io/name: ingress-nginx
      ports:
        - protocol: TCP
          port: 8000
    # Allow traffic from Prometheus for scraping
    - from:
        - namespaceSelector:
            matchLabels:
              name: monitoring
      ports:
        - protocol: TCP
          port: 8000
  egress:
    # Allow DNS resolution
    - to:
        - namespaceSelector: {}
          podSelector:
            matchLabels:
              k8s-app: kube-dns
      ports:
        - protocol: UDP
          port: 53
    # Allow traffic to PostgreSQL
    - to:
        - namespaceSelector:
            matchLabels:
              name: database
      ports:
        - protocol: TCP
          port: 5432
    # Allow traffic to Redis
    - to:
        - namespaceSelector:
            matchLabels:
              name: redis
      ports:
        - protocol: TCP
          port: 6379
    # Allow external HTTPS (for external API calls)
    - to:
        - ipBlock:
            cidr: 0.0.0.0/0
            except:
              - 10.0.0.0/8
              - 172.16.0.0/12
              - 192.168.0.0/16
      ports:
        - protocol: TCP
          port: 443
```

### Kustomization Base

```yaml
# k8s/base/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

namespace: fastapi-app

resources:
  - namespace.yaml
  - serviceaccount.yaml
  - configmap.yaml
  - secret.yaml
  - deployment.yaml
  - service.yaml
  - hpa.yaml
  - pdb.yaml
  - ingress.yaml
  - networkpolicy.yaml

commonLabels:
  app.kubernetes.io/name: fastapi-app
  app.kubernetes.io/managed-by: kustomize
```

### Production Overlay

```yaml
# k8s/overlays/production/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

namespace: fastapi-app-prod

resources:
  - ../../base

namePrefix: prod-

commonLabels:
  environment: production

images:
  - name: myregistry/fastapi-app
    newTag: v1.0.0

replicas:
  - name: fastapi-app
    count: 5

patches:
  - path: patches/deployment-resources.yaml
  - path: patches/hpa-scaling.yaml

configMapGenerator:
  - name: fastapi-app-config
    behavior: merge
    literals:
      - LOG_LEVEL=WARNING
      - CORS_ORIGINS=https://app.example.com
```

### Helm Chart

```yaml
# k8s/helm/fastapi-app/Chart.yaml
apiVersion: v2
name: fastapi-app
description: FastAPI Application Helm Chart
type: application
version: 1.0.0
appVersion: "1.0.0"
keywords:
  - fastapi
  - python
  - api
maintainers:
  - name: DevOps Team
    email: devops@example.com
```

### Helm Values

```yaml
# k8s/helm/fastapi-app/values.yaml
replicaCount: 3

image:
  repository: myregistry/fastapi-app
  pullPolicy: IfNotPresent
  tag: ""

imagePullSecrets: []
nameOverride: ""
fullnameOverride: ""

serviceAccount:
  create: true
  annotations: {}
  name: ""

podAnnotations:
  prometheus.io/scrape: "true"
  prometheus.io/port: "8000"

podSecurityContext:
  runAsNonRoot: true
  runAsUser: 1000
  fsGroup: 1000

securityContext:
  allowPrivilegeEscalation: false
  readOnlyRootFilesystem: true
  capabilities:
    drop:
      - ALL

service:
  type: ClusterIP
  port: 80

ingress:
  enabled: true
  className: nginx
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
  hosts:
    - host: api.example.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: fastapi-app-tls
      hosts:
        - api.example.com

resources:
  limits:
    cpu: 500m
    memory: 512Mi
  requests:
    cpu: 100m
    memory: 256Mi

autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70
  targetMemoryUtilizationPercentage: 80

nodeSelector: {}

tolerations: []

affinity:
  podAntiAffinity:
    preferredDuringSchedulingIgnoredDuringExecution:
      - weight: 100
        podAffinityTerm:
          labelSelector:
            matchExpressions:
              - key: app.kubernetes.io/name
                operator: In
                values:
                  - fastapi-app
          topologyKey: kubernetes.io/hostname

config:
  logLevel: INFO
  corsOrigins: https://app.example.com

secrets:
  databaseUrl: ""
  redisUrl: ""
  secretKey: ""

postgresql:
  enabled: false
  # External database configuration

redis:
  enabled: false
  # External Redis configuration
```

### Deployment Commands

```bash
# Apply with Kustomize
kubectl apply -k k8s/overlays/production

# Preview changes
kubectl diff -k k8s/overlays/production

# Deploy with Helm
helm upgrade --install fastapi-app k8s/helm/fastapi-app \
  --namespace fastapi-app \
  --create-namespace \
  -f k8s/helm/fastapi-app/values-production.yaml

# Rollback
helm rollback fastapi-app 1

# Check status
kubectl rollout status deployment/fastapi-app -n fastapi-app
```

## Kubernetes Best Practices

| Practice | Description |
|----------|-------------|
| Resource limits | Prevent resource exhaustion |
| Health probes | Enable self-healing |
| PDB | Ensure availability during updates |
| Anti-affinity | Spread pods across nodes |
| Sealed secrets | Secure secret management |
| HPA | Auto-scale based on load |

## References

- `_references/DEPLOYMENT-PATTERN.md`
