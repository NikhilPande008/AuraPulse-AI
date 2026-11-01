#!/usr/bin/env bash
# ==============================================================================
# AuraPulse AI - Automated Google Cloud Run Production Deployment Script
# Architecture: v2.2.0 | Serverless Full-Stack Deployment
# ==============================================================================

set -euo pipefail

# Configuration defaults
SERVICE_NAME="${SERVICE_NAME:-aurapulse-backend}"
WEB_SERVICE_NAME="${WEB_SERVICE_NAME:-aurapulse-web}"
REGION="${REGION:-us-central1}"
PROJECT_ID="${PROJECT_ID:-$(gcloud config get-value project 2>/dev/null || echo '')}"
ARTIFACT_REPO="${ARTIFACT_REPO:-aurapulse}"
IMAGE_TAG="${IMAGE_TAG:-${REGION}-docker.pkg.dev/${PROJECT_ID}/${ARTIFACT_REPO}/${SERVICE_NAME}:v2.2.0}"
WEB_IMAGE="${WEB_IMAGE:-${REGION}-docker.pkg.dev/${PROJECT_ID}/${ARTIFACT_REPO}/${WEB_SERVICE_NAME}:v2.2.0}"
# Note: min-instances=1 keeps instances warm to avoid cold starts (costs ~$10-15/month per service)
MIN_INSTANCES="${MIN_INSTANCES:-1}"

# Google API Keys & Secrets Configuration
USE_SECRET_MANAGER="${USE_SECRET_MANAGER:-true}"
ALLOW_PLAIN_ENV_KEYS="${ALLOW_PLAIN_ENV_KEYS:-false}"
GEMINI_API_KEY="${GEMINI_API_KEY:-}"
GOOGLE_MAPS_API_KEY="${GOOGLE_MAPS_API_KEY:-}"

echo "=================================================================="
echo "  🚀 AuraPulse AI: Deploying Full-Stack Services to Google Cloud Run"
echo "  Architecture: v2.2.0 | Backend + Next.js Frontend"
echo "=================================================================="

# Check prerequisites
if [ -z "$PROJECT_ID" ]; then
  echo "❌ Error: Google Cloud PROJECT_ID not set. Run 'gcloud config set project <ID>' first."
  exit 1
fi

PROJECT_NUMBER="$(gcloud projects describe "$PROJECT_ID" --format='value(projectNumber)' 2>/dev/null || echo '')"
RUNTIME_SA="${RUNTIME_SA:-${PROJECT_NUMBER}-compute@developer.gserviceaccount.com}"

echo "✔ Target Project:        ${PROJECT_ID} (${PROJECT_NUMBER:-unknown})"
echo "✔ Target Region:         ${REGION}"
echo "✔ Backend Service:       ${SERVICE_NAME}"
echo "✔ Frontend Service:      ${WEB_SERVICE_NAME}"
echo "✔ Backend Image:         ${IMAGE_TAG}"
echo "✔ Frontend Image:        ${WEB_IMAGE}"
echo "✔ Runtime Service Acct:  ${RUNTIME_SA}"

# Step 0: Enable required GCP services and configure Artifact Registry (idempotent)
echo ""
echo "⚙️ Step 0: Enabling required Google Cloud APIs and Artifact Registry..."
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  secretmanager.googleapis.com \
  --project="${PROJECT_ID}"

gcloud artifacts repositories describe "${ARTIFACT_REPO}" \
  --location="${REGION}" \
  --project="${PROJECT_ID}" >/dev/null 2>&1 \
  || gcloud artifacts repositories create "${ARTIFACT_REPO}" \
       --repository-format=docker \
       --location="${REGION}" \
       --project="${PROJECT_ID}" \
       --description="AuraPulse AI container registry"

# Step 1: Build Backend Container with Google Cloud Build
echo ""
echo "📦 Step 1: Submitting backend build to Google Cloud Build..."
gcloud builds submit backend \
  --project="${PROJECT_ID}" \
  --tag="${IMAGE_TAG}"

# Step 2: Deploy Backend to Managed Cloud Run
echo ""
echo "🚢 Step 2: Deploying Backend to Google Cloud Run (${MIN_INSTANCES}-3 instances)..."

DEPLOY_FLAGS=(
  --project="${PROJECT_ID}"
  --image="${IMAGE_TAG}"
  --region="${REGION}"
  --platform="managed"
  --allow-unauthenticated
  --port=8080
  --cpu=1
  --memory=512Mi
  --min-instances="${MIN_INSTANCES}"
  --max-instances=3
)

if [ "${USE_SECRET_MANAGER}" = "true" ]; then
  echo "✔ Checking Secret Manager secrets exist..."
  for secret_name in GEMINI_API_KEY GOOGLE_MAPS_API_KEY; do
    if ! gcloud secrets describe "${secret_name}" --project="${PROJECT_ID}" >/dev/null 2>&1; then
      echo "❌ Error: Secret '${secret_name}' does not exist in Secret Manager."
      echo "Create it using:"
      echo "  printf %s \"\$YOUR_KEY\" | gcloud secrets create ${secret_name} --data-file=- --project=\"${PROJECT_ID}\""
      exit 1
    fi
  done

  # Grant secretAccessor role to runtime service account
  echo "✔ Ensuring ${RUNTIME_SA} has roles/secretmanager.secretAccessor..."
  for secret_name in GEMINI_API_KEY GOOGLE_MAPS_API_KEY; do
    gcloud secrets add-iam-policy-binding "${secret_name}" \
      --project="${PROJECT_ID}" \
      --member="serviceAccount:${RUNTIME_SA}" \
      --role="roles/secretmanager.secretAccessor" >/dev/null 2>&1 || true
  done

  DEPLOY_FLAGS+=(
    --set-secrets="GEMINI_API_KEY=GEMINI_API_KEY:latest,GOOGLE_MAPS_API_KEY=GOOGLE_MAPS_API_KEY:latest"
    --set-env-vars="PROJECT_NAME=AuraPulse AI,VERSION=2.2.0"
  )
elif [ "${ALLOW_PLAIN_ENV_KEYS}" = "true" ]; then
  echo "⚠️ WARNING: Deploying with plain environment variables for API keys."
  ENV_VARS="PROJECT_NAME=AuraPulse AI,VERSION=2.2.0"
  if [ -n "$GEMINI_API_KEY" ]; then
    ENV_VARS="${ENV_VARS},GEMINI_API_KEY=${GEMINI_API_KEY}"
  fi
  if [ -n "$GOOGLE_MAPS_API_KEY" ]; then
    ENV_VARS="${ENV_VARS},GOOGLE_MAPS_API_KEY=${GOOGLE_MAPS_API_KEY}"
  fi
  DEPLOY_FLAGS+=(--set-env-vars="${ENV_VARS}")
else
  echo "❌ Error: USE_SECRET_MANAGER is false and ALLOW_PLAIN_ENV_KEYS is not true."
  echo "Set USE_SECRET_MANAGER=true (recommended) or ALLOW_PLAIN_ENV_KEYS=true."
  exit 1
fi

gcloud run deploy "${SERVICE_NAME}" "${DEPLOY_FLAGS[@]}"

# Step 3: Retrieve Backend URL
echo ""
echo "🔍 Step 3: Retrieving Backend API URL..."
API_URL="$(gcloud run services describe "${SERVICE_NAME}" \
  --project="${PROJECT_ID}" \
  --region="${REGION}" \
  --format='value(status.url)')"
echo "✔ Backend API URL: ${API_URL}"

# Step 4: Build and Deploy Frontend
echo ""
echo "📦 Step 4: Submitting frontend build with BACKEND_URL=${API_URL}..."
gcloud builds submit frontend \
  --project="${PROJECT_ID}" \
  --config frontend/cloudbuild.yaml \
  --substitutions=_BACKEND_URL="${API_URL}",_IMAGE="${WEB_IMAGE}"

echo ""
echo "🚢 Step 5: Deploying Frontend to Google Cloud Run (port 3000)..."
gcloud run deploy "${WEB_SERVICE_NAME}" \
  --project="${PROJECT_ID}" \
  --image="${WEB_IMAGE}" \
  --port=3000 \
  --allow-unauthenticated \
  --region="${REGION}" \
  --min-instances=1 \
  --max-instances=3 \
  --memory=512Mi

WEB_URL="$(gcloud run services describe "${WEB_SERVICE_NAME}" \
  --project="${PROJECT_ID}" \
  --region="${REGION}" \
  --format='value(status.url)')"
echo "✔ Frontend Web URL: ${WEB_URL}"

# Step 6: Update Backend CORS to trust Frontend URL
echo ""
echo "🔒 Step 6: Updating Backend ALLOWED_ORIGIN to trust ${WEB_URL}..."
gcloud run services update "${SERVICE_NAME}" \
  --project="${PROJECT_ID}" \
  --region="${REGION}" \
  --update-env-vars="ALLOWED_ORIGIN=${WEB_URL}"

# Step 7: Verify Health of both services
echo ""
echo "🔍 Step 7: Verifying deployment health endpoints..."
echo "--- Backend Direct Health (${API_URL}/api/health) ---"
API_HEALTH="$(curl -s "${API_URL}/api/health" || echo '{"status":"unreachable"}')"
echo "${API_HEALTH}"

echo "--- Frontend Proxied Health (${WEB_URL}/api/health) ---"
WEB_HEALTH="$(curl -s "${WEB_URL}/api/health" || echo '{"status":"unreachable"}')"
echo "${WEB_HEALTH}"

echo ""
echo "=================================================================="
echo "  ✅ Full-Stack Deployment Complete! AuraPulse AI is LIVE."
echo "  Frontend URL: ${WEB_URL}"
echo "  Backend API:  ${API_URL}"
echo "=================================================================="
