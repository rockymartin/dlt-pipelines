#!/bin/bash

# Cloud Run deployment script for Pokemon Pipeline
# This script deploys the Pokemon data pipeline to Google Cloud Run

set -e

# Configuration
PROJECT_ID=${PROJECT_ID:-"your-project-id"}
SERVICE_NAME="pokemon-pipeline"
REGION=${REGION:-"us-central1"}
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo "Deploying Pokemon Pipeline to Cloud Run..."
echo "Project ID: ${PROJECT_ID}"
echo "Service Name: ${SERVICE_NAME}"
echo "Region: ${REGION}"

# Build and push the Docker image
echo "Building Docker image..."
docker build -t ${IMAGE_NAME} .

echo "Pushing image to Google Container Registry..."
docker push ${IMAGE_NAME}

# Deploy to Cloud Run
echo "Deploying to Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
    --image ${IMAGE_NAME} \
    --platform managed \
    --region ${REGION} \
    --project ${PROJECT_ID} \
    --memory 2Gi \
    --cpu 2 \
    --timeout 3600 \
    --max-instances 10 \
    --set-env-vars "POKEMON_RESOURCES=pokemon_details,berries" \
    --set-env-vars "POKEMON_LIMIT=50" \
    --no-allow-unauthenticated

echo "Deployment completed!"
echo "Service URL: https://${REGION}-${PROJECT_ID}.cloudfunctions.net/${SERVICE_NAME}"

# Optional: Run the job immediately
echo "Running the pipeline job..."
gcloud run jobs create pokemon-pipeline-job \
    --image ${IMAGE_NAME} \
    --region ${REGION} \
    --project ${PROJECT_ID} \
    --memory 2Gi \
    --cpu 2 \
    --timeout 3600 \
    --set-env-vars "POKEMON_RESOURCES=pokemon_details,berries" \
    --set-env-vars "POKEMON_LIMIT=50" \
    --max-retries 3

echo "Job created! You can execute it with:"
echo "gcloud run jobs execute pokemon-pipeline-job --region ${REGION} --project ${PROJECT_ID}"
