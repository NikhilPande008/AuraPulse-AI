# AuraPulse AI Deployment Guide

This guide describes how to deploy AuraPulse AI (Backend: FastAPI on Google Cloud Run; Frontend: Next.js 15 on Google Cloud Run) using Google Cloud Build and Cloud Run.

## Prerequisites

1. **Google Cloud SDK (`gcloud`)** installed and authenticated:
   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```
2. **Active Google Cloud Project** with billing enabled.
3. **API Keys**:
   - `GEMINI_API_KEY`: Google AI Studio or Vertex AI Gemini API key.
   - `GOOGLE_MAPS_API_KEY`: Google Cloud Places API (New) key.

## Secret Manager Setup

Store your sensitive keys in Google Secret Manager:

```bash
# Enable Secret Manager API
gcloud services enable secretmanager.googleapis.com

# Create secrets
echo -n "your-gemini-api-key" | gcloud secrets create GEMINI_API_KEY --data-file=-
echo -n "your-google-maps-api-key" | gcloud secrets create GOOGLE_MAPS_API_KEY --data-file=-
```

The deployment script will automatically check for these secrets and grant the Cloud Run runtime service account (`<project-number>-compute@developer.gserviceaccount.com`) `roles/secretmanager.secretAccessor`.

## Deployment

Run the automated deployment script from the project root:

```bash
chmod +x deployment/deploy_cloud_run.sh
./deployment/deploy_cloud_run.sh
```

### Configuration Options (Environment Variables)

- `PROJECT_ID`: Target GCP project ID (defaults to current `gcloud config get-value project`).
- `REGION`: Target region (defaults to `us-central1`).
- `SERVICE_NAME`: Backend service name (defaults to `aurapulse-backend`).
- `WEB_SERVICE_NAME`: Frontend service name (defaults to `aurapulse-web`).
- `IMAGE_TAG`: Custom backend container image tag override.
- `WEB_IMAGE`: Custom frontend container image tag override.
- `MIN_INSTANCES`: Minimum instances for backend and frontend (defaults to `1` to eliminate cold starts; set to `0` for development cost savings).
- `ALLOW_PLAIN_ENV_KEYS`: Set to `true` if deploying without Secret Manager (passes local env values directly as environment variables).

### Expected Outputs

1. **Backend Cloud Run Service**: `aurapulse-backend` listening on port 8080.
   - Verifies health check: `GET /api/health` -> returns status 200 with integration flags.
2. **Frontend Cloud Run Service**: `aurapulse-web` listening on port 3000.
   - Built with `--build-arg BACKEND_URL=https://<aurapulse-backend-url>`.
   - Verifies health check: `GET /` -> returns status 200.
3. Backend CORS `ALLOWED_ORIGIN` is updated to include the frontend URL.

## Rollback Procedure

If a deployment introduces issues, roll back traffic to a prior known-healthy revision using Cloud Run traffic splitting:

```bash
# List revisions
gcloud run revisions list --service aurapulse-backend --region us-central1
gcloud run revisions list --service aurapulse-web --region us-central1

# Roll back backend to previous revision
gcloud run services update-traffic aurapulse-backend \
  --to-revisions PREVIOUS_REVISION_NAME=100 \
  --region us-central1

# Roll back frontend to previous revision
gcloud run services update-traffic aurapulse-web \
  --to-revisions PREVIOUS_REVISION_NAME=100 \
  --region us-central1
```

## Custom Domain Mapping (Optional)

To map a custom domain (e.g., `aurapulse.ai` or `app.example.com`):

1. Map the custom domain to the frontend Cloud Run service:
   ```bash
   gcloud beta run domain-mappings create \
     --service=aurapulse-web \
     --domain=app.example.com \
     --region=us-central1
   ```
2. Update DNS records with the DNS Resource Records (CNAME / A) returned by the command.
3. Update `ALLOWED_ORIGIN` on the backend service to include `https://app.example.com`.
