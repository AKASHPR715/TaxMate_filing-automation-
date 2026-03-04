#!/bin/bash

# TaxMate GCP Cloud Run Deployment Script
# Usage: ./deploy_gcp.sh

# Exit on error
set -e

# Project configuration
PROJECT_ID=$(gcloud config get-value project)
SERVICE_NAME="taxmate-api"
REGION="us-central1" # Change as needed

echo "🚀 Starting TaxMate deployment to GCP Cloud Run..."
echo "📍 Project: $PROJECT_ID"
echo "📍 Service: $SERVICE_NAME"
echo "📍 Region: $REGION"

# 1. Enable necessary services
echo "⚙️ Enabling Cloud Run and Artifact Registry..."
gcloud services enable run.googleapis.com artifactregistry.googleapis.com cloudbuild.googleapis.com

# 2. Build and push image using Cloud Build (no local Docker needed)
echo "📦 Building and pushing Docker image to GCP..."
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME

# 3. Deploy to Cloud Run
echo "🚢 Deploying to Cloud Run..."
# We explicitly map key variables to avoid parsing issues with complex URIs
gcloud run deploy $SERVICE_NAME \
  --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 2 \
  --timeout 120 \
  --set-env-vars "MONGO_URI=$(grep MONGO_URI .env | cut -d '=' -f2-)" \
  --set-env-vars "DB_NAME=$(grep DB_NAME .env | cut -d '=' -f2-)" \
  --set-env-vars "QDRANT_URL=$(grep QDRANT_URL .env | cut -d '=' -f2-)" \
  --set-env-vars "QDRANT_API_KEY=$(grep QDRANT_API_KEY .env | cut -d '=' -f2-)" \
  --set-env-vars "OPENROUTER_API_KEY=$(grep OPENROUTER_API_KEY .env | cut -d '=' -f2-)" \
  --set-env-vars "NVIDIA_API_KEY=$(grep NVIDIA_API_KEY .env | cut -d '=' -f2-)" \
  --set-env-vars "GOOGLE_API_KEY=$(grep GOOGLE_API_KEY .env | cut -d '=' -f2-)" \
  --set-env-vars "TAVILY_API_KEY=$(grep TAVILY_API_KEY .env | cut -d '=' -f2-)" \
  --set-env-vars "LLAMA_CLOUD_API_KEY=$(grep LLAMA_CLOUD_API_KEY .env | cut -d '=' -f2-)" \
  --set-env-vars "SECRET_KEY=$(grep SECRET_KEY .env | cut -d '=' -f2-)" \
  --set-env-vars "ALLOWED_ORIGINS=$(grep ALLOWED_ORIGINS .env | cut -d '=' -f2-)" \
  --set-env-vars "ENVIRONMENT=production"

echo "✅ Deployment complete!"
gcloud run services describe $SERVICE_NAME --platform managed --region $REGION --format 'value(status.url)'
