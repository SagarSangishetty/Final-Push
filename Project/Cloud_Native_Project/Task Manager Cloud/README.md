# DevOps Task Manager — AWS Production Project

## What this app is
A Task Manager app used as a **real-world DevOps deployment project** covering all 5 phases:
- VPC + RDS in private subnet (Phase 1)
- EKS + ECR (Phase 2)
- Secrets Manager + IRSA (Phase 3)
- ALB Ingress + HTTPS (Phase 4)
- CloudWatch Container Insights (Phase 5)

**Stack:** React (nginx) · Python FastAPI · PostgreSQL on RDS

---

## Project Structure
```
devops-app/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app entry
│   │   ├── core/database.py     # SQLAlchemy + DB health check
│   │   ├── models/task.py       # Task table
│   │   └── api/
│   │       ├── health.py        # /live /ready /startup probes
│   │       └── tasks.py         # CRUD endpoints
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── App.jsx              # React UI (fetches /api/tasks)
│   │   └── App.css
│   ├── nginx.conf               # Proxies /api/ → backend-service
│   └── Dockerfile
└── k8s/base/
    ├── backend-deployment.yaml  # 3 probes wired to /api/health/*
    ├── frontend-deployment.yaml # liveness + readiness on /health
    ├── ingress.yaml             # ALB + ACM + HTTPS redirect
    └── irsa-and-secrets.yaml    # ServiceAccount + ExternalSecret
```

---

## Health Check Endpoints

| Endpoint | Probe | What it checks |
|---|---|---|
| `GET /api/health/live` | Liveness | App process is alive |
| `GET /api/health/ready` | Readiness | App + RDS DB reachable |
| `GET /api/health/startup` | Startup | App has finished initializing |
| `GET /health` (nginx) | Liveness + Readiness | nginx is serving |

---

## Deployment Steps

### Phase 1 — Network
1. Create VPC with 2 public + 2 private subnets (2 AZs)
2. Launch RDS PostgreSQL in private subnets
3. Security Group: RDS SG allows port 5432 from backend pod SG only

### Phase 2 — EKS + ECR
```bash
# Create cluster
eksctl create cluster --name task-cluster --region ap-south-1 --nodes 2 --node-type t3.small

# Create ECR repos
aws ecr create-repository --repository-name task-manager/backend
aws ecr create-repository --repository-name task-manager/frontend

# Authenticate + push
aws ecr get-login-password | docker login --username AWS --password-stdin <ACCOUNT>.dkr.ecr.<REGION>.amazonaws.com
docker build -t task-manager/backend ./backend
docker tag task-manager/backend:latest <ECR_URI>/task-manager/backend:latest
docker push <ECR_URI>/task-manager/backend:latest
# Repeat for frontend
```

### Phase 3 — Secrets Manager + IRSA
```bash
# Store RDS creds in Secrets Manager
aws secretsmanager create-secret \
  --name prod/taskmanager/rds \
  --secret-string '{"host":"<RDS_ENDPOINT>","port":"5432","dbname":"taskdb","username":"postgres","password":"<YOUR_PASSWORD>"}'

# Create IRSA role (eksctl handles OIDC)
eksctl create iamserviceaccount \
  --cluster task-cluster \
  --name backend-sa \
  --namespace default \
  --attach-policy-arn arn:aws:iam::aws:policy/SecretsManagerReadWrite \
  --approve

# Install External Secrets Operator
helm repo add external-secrets https://charts.external-secrets.io
helm install external-secrets external-secrets/external-secrets -n external-secrets --create-namespace
```

### Phase 4 — ALB + HTTPS
```bash
# Install AWS Load Balancer Controller
helm repo add eks https://aws.github.io/eks-charts
helm install aws-load-balancer-controller eks/aws-load-balancer-controller \
  -n kube-system \
  --set clusterName=task-cluster

# Apply manifests
kubectl apply -f k8s/base/
```

### Phase 5 — CloudWatch
```bash
# Enable Container Insights
aws eks update-addon \
  --cluster-name task-cluster \
  --addon-name amazon-cloudwatch-observability

# View logs
# CloudWatch → Log Groups → /aws/containerinsights/task-cluster/application
```

---

## API Endpoints
```
GET  /api/tasks        List all tasks
POST /api/tasks        Create task  { title, description, priority }
GET  /api/tasks/:id    Get one task
PATCH /api/tasks/:id   Update task
DELETE /api/tasks/:id  Delete task

GET  /api/health/live     Liveness probe
GET  /api/health/ready    Readiness probe (checks RDS)
GET  /api/health/startup  Startup probe
```
