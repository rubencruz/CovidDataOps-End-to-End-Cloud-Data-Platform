#!/usr/bin/env bash
set -euo pipefail
: "${PROJECT_ID:?Set PROJECT_ID}"
: "${REGION:=us-central1}"
cd terraform
terraform destroy \
  -var="project_id=$PROJECT_ID" \
  -var="region=$REGION" \
  -var="container_image=placeholder"
