#!/bin/bash
set -e

echo "🚀 Deploying MCP Task Manager to Kubernetes"
echo ""

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl is not installed. Please install kubectl first."
    exit 1
fi

# Check if we're using minikube or kind
if command -v minikube &> /dev/null; then
    echo "📦 Detected Minikube - setting Docker environment"
    eval $(minikube docker-env)
elif command -v kind &> /dev/null; then
    echo "📦 Detected kind cluster"
    USING_KIND=true
else
    echo "⚠️  No local Kubernetes detected. Assuming remote cluster."
fi

# Build Docker images
echo ""
echo "🔨 Building Docker images..."
echo ""

echo "Building FastAPI image..."
docker build -t task-manager-fastapi:latest ./fastapi-app/

echo "Building MCP Server image..."
docker build -t task-manager-mcp:latest ./mcp-server/

# Load images into kind if using kind
if [ "$USING_KIND" = true ]; then
    echo ""
    echo "📦 Loading images into kind cluster..."
    kind load docker-image task-manager-fastapi:latest
    kind load docker-image task-manager-mcp:latest
fi

# Apply Kubernetes manifests
echo ""
echo "☸️  Applying Kubernetes manifests..."
echo ""

echo "Deploying FastAPI..."
kubectl apply -f kubernetes/fastapi-deployment.yaml
kubectl apply -f kubernetes/fastapi-service.yaml

echo "Deploying MCP Server..."
kubectl apply -f kubernetes/mcp-deployment.yaml
kubectl apply -f kubernetes/mcp-service.yaml

# Wait for deployments
echo ""
echo "⏳ Waiting for deployments to be ready..."
kubectl wait --for=condition=available --timeout=120s deployment/fastapi-deployment
kubectl wait --for=condition=available --timeout=120s deployment/mcp-server-deployment

# Display status
echo ""
echo "✅ Deployment complete!"
echo ""
echo "📊 Deployment Status:"
kubectl get deployments
echo ""
echo "🔌 Services:"
kubectl get services
echo ""
echo "📦 Pods:"
kubectl get pods
echo ""

# Get FastAPI URL
echo "🌐 To access the FastAPI service:"
echo "   Run: kubectl port-forward service/fastapi-service 8000:8000"
echo "   Then visit: http://localhost:8000"
echo ""
echo "📋 To view logs:"
echo "   FastAPI: kubectl logs -f deployment/fastapi-deployment"
echo "   MCP Server: kubectl logs -f deployment/mcp-server-deployment"
echo ""
echo "🧹 To cleanup:"
echo "   Run: ./cleanup.sh"
echo ""
