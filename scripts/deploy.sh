#!/usr/bin/env bash
set -euo pipefail
: "${PROJECT_ID:?Set PROJECT_ID}"
: "${REGION:=us-central1}"
IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/covid-data/covid-pipeline:phase-3"

gcloud artifacts repositories describe covid-data --location="$REGION" >/dev/null 2>&1 || \
  gcloud artifacts repositories create covid-data --repository-format=docker --location="$REGION"

gcloud builds submit --tag "$IMAGE" .

cd terraform
terraform init
terraform apply -auto-approve \
  -var="project_id=$PROJECT_ID" \
  -var="region=$REGION" \
  -var="container_image=$IMAGE"
