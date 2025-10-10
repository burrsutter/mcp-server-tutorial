#!/bin/bash
set -e

echo "🧹 Cleaning up MCP Task Manager from Kubernetes"
echo ""

# Delete Kubernetes resources
echo "Deleting MCP Server..."
kubectl delete -f kubernetes/mcp-service.yaml --ignore-not-found=true
kubectl delete -f kubernetes/mcp-deployment.yaml --ignore-not-found=true

echo "Deleting FastAPI..."
kubectl delete -f kubernetes/fastapi-service.yaml --ignore-not-found=true
kubectl delete -f kubernetes/fastapi-deployment.yaml --ignore-not-found=true

echo ""
echo "✅ Cleanup complete!"
echo ""
echo "📊 Remaining resources:"
kubectl get all | grep -E "(fastapi|mcp)" || echo "No resources found"
echo ""
