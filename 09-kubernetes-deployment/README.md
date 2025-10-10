# Example 9: Kubernetes Deployment

This example demonstrates how to deploy the FastAPI + MCP wrapper system to Kubernetes. It shows production-ready containerization and orchestration patterns for MCP applications.

## What This Example Demonstrates

- Containerizing MCP servers with Docker
- Kubernetes deployment patterns
- Service discovery in Kubernetes
- Health checks and readiness probes
- Resource management (CPU/memory limits)
- Multi-container applications
- Environment-based configuration
- Automated deployment scripts

## Architecture

```
┌─────────────────────────────────────────────┐
│         Kubernetes Cluster                   │
│                                               │
│  ┌──────────────────────────────────────┐  │
│  │  FastAPI Deployment (2 replicas)     │  │
│  │  ┌────────────┐  ┌────────────┐     │  │
│  │  │ FastAPI    │  │ FastAPI    │     │  │
│  │  │ Container  │  │ Container  │     │  │
│  │  └────────────┘  └────────────┘     │  │
│  └──────────────────────────────────────┘  │
│              ▲                               │
│              │ HTTP (port 8000)              │
│              │                               │
│  ┌──────────────────────────────────────┐  │
│  │  FastAPI Service (ClusterIP)         │  │
│  └──────────────────────────────────────┘  │
│              ▲                               │
│              │                               │
│  ┌──────────────────────────────────────┐  │
│  │  MCP Server Deployment (1 replica)   │  │
│  │  ┌────────────┐                      │  │
│  │  │ MCP Server │                      │  │
│  │  │ Container  │                      │  │
│  │  └────────────┘                      │  │
│  └──────────────────────────────────────┘  │
│                                               │
└─────────────────────────────────────────────┘
```

## Directory Structure

```
09-kubernetes-deployment/
├── fastapi-app/
│   ├── app.py              # FastAPI application
│   ├── Dockerfile          # FastAPI container image
│   └── requirements.txt    # Python dependencies
├── mcp-server/
│   ├── server.py          # MCP server wrapper
│   ├── Dockerfile         # MCP server container image
│   └── requirements.txt   # Python dependencies
├── kubernetes/
│   ├── fastapi-deployment.yaml    # FastAPI Deployment
│   ├── fastapi-service.yaml       # FastAPI Service
│   ├── mcp-deployment.yaml        # MCP Deployment
│   └── mcp-service.yaml           # MCP Service
├── deploy.sh              # Automated deployment script
├── cleanup.sh             # Cleanup script
└── README.md              # This file
```

## Prerequisites

### Required Tools
- **Docker**: For building container images
- **kubectl**: Kubernetes CLI tool
- **Kubernetes Cluster**: One of:
  - **Minikube** (local development)
  - **kind** (Kubernetes in Docker)
  - **Docker Desktop** (with Kubernetes enabled)
  - **Cloud provider** (GKE, EKS, AKS)

### Setup Local Kubernetes

**Option 1: Minikube**
```bash
# Install Minikube
brew install minikube  # macOS
# or follow: https://minikube.sigs.k8s.io/docs/start/

# Start Minikube
minikube start

# Verify
kubectl get nodes
```

**Option 2: kind**
```bash
# Install kind
brew install kind  # macOS
# or follow: https://kind.sigs.k8s.io/docs/user/quick-start/

# Create cluster
kind create cluster --name mcp-demo

# Verify
kubectl cluster-info
```

**Option 3: Docker Desktop**
```bash
# Enable Kubernetes in Docker Desktop settings
# Preferences → Kubernetes → Enable Kubernetes

# Verify
kubectl get nodes
```

## Quick Start

### 1. Deploy Everything

```bash
cd 09-kubernetes-deployment

# Make scripts executable
chmod +x deploy.sh cleanup.sh

# Deploy to Kubernetes
./deploy.sh
```

The script will:
1. Build Docker images
2. Load images into cluster (if using kind/minikube)
3. Deploy FastAPI and MCP server
4. Wait for pods to be ready
5. Display deployment status

### 2. Access the Services

**Port Forward FastAPI:**
```bash
kubectl port-forward service/fastapi-service 8000:8000
```

Then visit http://localhost:8000 or test with curl:
```bash
# Test FastAPI
curl http://localhost:8000/tasks

# Create a task
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Task", "description": "From Kubernetes"}'
```

### 3. View Logs

```bash
# FastAPI logs
kubectl logs -f deployment/fastapi-deployment

# MCP Server logs
kubectl logs -f deployment/mcp-server-deployment

# All logs
kubectl logs -f -l app=fastapi
kubectl logs -f -l app=mcp-server
```

### 4. Check Pod Status

```bash
# List all pods
kubectl get pods

# Detailed pod info
kubectl describe pod <pod-name>

# Get pod events
kubectl get events --sort-by='.lastTimestamp'
```

### 5. Cleanup

```bash
./cleanup.sh
```

## Manual Deployment

If you prefer to deploy manually:

### Build Images

```bash
# FastAPI
cd fastapi-app
docker build -t task-manager-fastapi:latest .

# MCP Server
cd ../mcp-server
docker build -t task-manager-mcp:latest .
```

### Load Images (kind/minikube)

**For kind:**
```bash
kind load docker-image task-manager-fastapi:latest
kind load docker-image task-manager-mcp:latest
```

**For Minikube:**
```bash
eval $(minikube docker-env)
# Then rebuild images
```

### Deploy to Kubernetes

```bash
# FastAPI
kubectl apply -f kubernetes/fastapi-deployment.yaml
kubectl apply -f kubernetes/fastapi-service.yaml

# MCP Server
kubectl apply -f kubernetes/mcp-deployment.yaml
kubectl apply -f kubernetes/mcp-service.yaml

# Wait for ready
kubectl wait --for=condition=available --timeout=120s deployment/fastapi-deployment
kubectl wait --for=condition=available --timeout=120s deployment/mcp-server-deployment
```

## Configuration

### Environment Variables

**FastAPI Container:**
- `ENVIRONMENT`: Deployment environment (default: "kubernetes")
- `PORT`: HTTP port (default: 8000)

**MCP Server Container:**
- `FASTAPI_URL`: URL to FastAPI service (default: "http://fastapi-service:8000")

### Resource Limits

Current settings in deployment manifests:

```yaml
resources:
  requests:
    memory: "128Mi"
    cpu: "100m"
  limits:
    memory: "256Mi"
    cpu: "500m"
```

Adjust based on your needs in the deployment YAML files.

### Replicas

- **FastAPI**: 2 replicas (for high availability)
- **MCP Server**: 1 replica (adjust as needed)

## Kubernetes Concepts Used

### Deployments
Manage pod replicas and updates:
- Rolling updates
- Health checks
- Resource management

### Services
Provide stable network endpoints:
- **ClusterIP**: Internal cluster communication
- Service discovery via DNS

### Health Checks
- **Liveness Probe**: Restart unhealthy pods
- **Readiness Probe**: Route traffic only to ready pods

### Resource Quotas
- CPU and memory requests/limits
- Prevent resource exhaustion

## Production Considerations

### 1. Image Registry

For production, push images to a registry:

```bash
# Tag images
docker tag task-manager-fastapi:latest your-registry/task-manager-fastapi:v1.0.0
docker tag task-manager-mcp:latest your-registry/task-manager-mcp:v1.0.0

# Push to registry
docker push your-registry/task-manager-fastapi:v1.0.0
docker push your-registry/task-manager-mcp:v1.0.0

# Update deployments to use registry images
# Change imagePullPolicy from "Never" to "IfNotPresent" or "Always"
```

### 2. Persistent Storage

Add persistent volumes for data:

```yaml
volumes:
- name: data
  persistentVolumeClaim:
    claimName: task-data-pvc
```

### 3. Ingress

Expose services externally:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: fastapi-ingress
spec:
  rules:
  - host: tasks.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: fastapi-service
            port:
              number: 8000
```

### 4. Secrets Management

Store sensitive data securely:

```bash
kubectl create secret generic api-keys \
  --from-literal=api-key=your-secret-key
```

### 5. Monitoring

Add monitoring with Prometheus/Grafana:
- Metrics endpoints
- Custom dashboards
- Alerting rules

### 6. Autoscaling

Enable horizontal pod autoscaling:

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: fastapi-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: fastapi-deployment
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

## Troubleshooting

### Pods Not Starting

```bash
# Check pod status
kubectl get pods

# Describe pod for events
kubectl describe pod <pod-name>

# Check logs
kubectl logs <pod-name>
```

Common issues:
- Image pull errors (check imagePullPolicy)
- Resource limits too low
- Missing environment variables

### Service Connection Issues

```bash
# Test service from another pod
kubectl run -it --rm debug --image=busybox --restart=Never -- sh
wget -O- http://fastapi-service:8000/health
```

### Health Check Failures

```bash
# Check health endpoint manually
kubectl port-forward <pod-name> 8000:8000
curl http://localhost:8000/health
```

Adjust probe timing if needed:
- `initialDelaySeconds`: Wait before first check
- `periodSeconds`: Check interval
- `timeoutSeconds`: Check timeout
- `failureThreshold`: Failures before restart

## Scaling

### Manual Scaling

```bash
# Scale FastAPI
kubectl scale deployment/fastapi-deployment --replicas=5

# Scale MCP Server
kubectl scale deployment/mcp-server-deployment --replicas=3
```

### Auto Scaling

Apply HPA configuration (see Production Considerations above).

## Updating

### Rolling Update

```bash
# Update image
kubectl set image deployment/fastapi-deployment \
  fastapi=task-manager-fastapi:v2.0.0

# Check rollout status
kubectl rollout status deployment/fastapi-deployment

# Rollback if needed
kubectl rollout undo deployment/fastapi-deployment
```

## Next Steps

- Add database persistence (PostgreSQL, MongoDB)
- Implement CI/CD pipelines
- Add monitoring and logging
- Configure autoscaling
- Set up ingress controllers
- Implement service mesh (Istio, Linkerd)
- Add security policies (NetworkPolicies, PodSecurityPolicies)
- Configure backup and disaster recovery

## Additional Resources

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Docker Documentation](https://docs.docker.com/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [MCP Protocol](https://modelcontextprotocol.io/)
