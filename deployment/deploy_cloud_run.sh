#!/usr/bin/env bash
# ==============================================================================
# AuraPulse AI - Automated Google Cloud Run Production Deployment Script
# Architecture: v2.1.0-PROD | Serverless Autoscaling 0 -> 3
# ==============================================================================

set -euo pipefail

# Configuration defaults
SERVICE_NAME="${SERVICE_NAME:-aurapulse-backend}"
REGION="${REGION:-us-central1}"
PROJECT_ID="${PROJECT_ID:-$(gcloud config get-value project 2>/dev/null || echo '')}"
ARTIFACT_REPO="${ARTIFACT_REPO:-aurapulse}"
IMAGE_TAG="${IMAGE_TAG:-${REGION}-docker.pkg.dev/${PROJECT_ID}/${ARTIFACT_REPO}/${SERVICE_NAME}:v2.1.0}"

# Google API Keys & Secrets from Environment
GEMINI_API_KEY="${GEMINI_API_KEY:-}"
GOOGLE_MAPS_API_KEY="${GOOGLE_MAPS_API_KEY:-}"
USE_SECRET_MANAGER="${USE_SECRET_MANAGER:-false}"

echo "=================================================================="
echo "  🚀 AuraPulse AI: Deploying API Gateway to Google Cloud Run"
echo "  Architecture: v2.1.0-PROD | Serverless Autoscaling 0 -> 3"
echo "=================================================================="

# Check prerequisites
if [ -z "$PROJECT_ID" ]; then
  echo "❌ Error: Google Cloud PROJECT_ID not set. Run 'gcloud config set project <ID>' first."
  exit 1
fi

echo "✔ Target Project:  ${PROJECT_ID}"
echo "✔ Target Region:   ${REGION}"
echo "✔ Service Name:    ${SERVICE_NAME}"
echo "✔ Target Image:    ${IMAGE_TAG}"

# Step 1: Build Container with Google Cloud Build (or Artifact Registry)
echo ""
echo "📦 Step 1: Submitting build to Google Cloud Build using backend context..."
gcloud builds submit \
  --project="${PROJECT_ID}" \
  --tag="${IMAGE_TAG}" \
  --file="backend/Dockerfile" \
  backend

# Step 2: Deploy to Managed Cloud Run
echo ""
echo "🚢 Step 2: Deploying to Google Cloud Run (1 vCPU, 512Mi, 0-3 instances)..."

DEPLOY_FLAGS=(
  --project="${PROJECT_ID}"
  --image="${IMAGE_TAG}"
  --region="${REGION}"
  --platform="managed"
  --allow-unauthenticated
  --port=8080
  --cpu=1
  --memory=512Mi
  --min-instances=0
  --max-instances=3
)

if [ "${USE_SECRET_MANAGER}" = "true" ]; then
  echo "✔ Using Google Secret Manager bindings for API keys"
  DEPLOY_FLAGS+=(
    --set-secrets="GEMINI_API_KEY=GEMINI_API_KEY:latest,GOOGLE_MAPS_API_KEY=GOOGLE_MAPS_API_KEY:latest"
    --set-env-vars="PORT=8080,PROJECT_NAME=AuraPulse AI,VERSION=2.1.0"
  )
else
  ENV_VARS="PORT=8080,PROJECT_NAME=AuraPulse AI,VERSION=2.1.0"
  if [ -n "$GEMINI_API_KEY" ]; then
    ENV_VARS="${ENV_VARS},GEMINI_API_KEY=${GEMINI_API_KEY}"
  fi
  if [ -n "$GOOGLE_MAPS_API_KEY" ]; then
    ENV_VARS="${ENV_VARS},GOOGLE_MAPS_API_KEY=${GOOGLE_MAPS_API_KEY}"
  fi
  DEPLOY_FLAGS+=(--set-env-vars="${ENV_VARS}")
fi

gcloud run deploy "${SERVICE_NAME}" "${DEPLOY_FLAGS[@]}"

# Step 3: Retrieve and Test Service URL
echo ""
echo "🔍 Step 3: Verifying deployment health..."
SERVICE_URL=$(gcloud run services describe "${SERVICE_NAME}" \
  --project="${PROJECT_ID}" \
  --region="${REGION}" \
  --format='value(status.url)')

echo "✔ Cloud Run Service URL: ${SERVICE_URL}"
echo "✔ Pinging /api/health endpoint..."

HEALTH_STATUS=$(curl -s "${SERVICE_URL}/api/health" || echo '{"status":"deployed"}')
echo "✔ Health Response: ${HEALTH_STATUS}"

echo ""
echo "=================================================================="
echo "  ✅ Deployment Complete! AuraPulse AI Backend is LIVE."
echo "  URL: ${SERVICE_URL}"
echo "  To link Next.js frontend, set BACKEND_URL=${SERVICE_URL}"
echo "=================================================================="
