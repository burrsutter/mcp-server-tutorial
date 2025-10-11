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
# docker build -t task-manager-fastapi:latest ./fastapi-app/
podman build --arch amd64 --os linux -t quay.io/burrsutter/task-manager-fastapi:latest ./fastapi-app/
podman push quay.io/burrsutter/task-manager-fastapi:latest

echo "Building MCP Server image..."
# docker build -t task-manager-mcp:latest ./mcp-server/
podman build --arch amd64 --os linux -t quay.io/burrsutter/task-manager-mcp:latest ./mcp-server/
podman push quay.io/burrsutter/task-manager-mcp:latest


echo "Deploying FastAPI..."
oc apply -f openshift/fastapi-deployment.yaml
oc apply -f openshift/fastapi-service.yaml
oc apply -f openshift/fastapi-route.yaml

echo "Deploying MCP Server..."
oc apply -f openshift/mcp-server-deployment.yaml
oc apply -f openshift/mcp-server-service.yaml
oc apply -f openshift/mcp-server-route.yaml

# Wait for deployments
echo ""
echo "⏳ Waiting for deployments to be ready..."
oc wait --for=condition=available --timeout=120s deployment/fastapi-deployment
oc wait --for=condition=available --timeout=120s deployment/mcp-server-deployment

# Display status
echo ""
echo "✅ Deployment complete!"
echo ""
echo "📊 Deployment Status:"
oc get deployments
echo ""
echo "🔌 Services:"
oc get services
echo ""
echo "📦 Pods:"
oc get pods
echo ""

# Get FastAPI URL
echo "🌐 To access the MCP service:"
export MCP_URL=https://$(oc get routes -l app=mcp-server -o jsonpath="{range .items[*]}{.status.ingress[0].host}{end}")
echo "   " $MCP_URL
echo ""
