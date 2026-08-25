#!/usr/bin/env bash
set -euo pipefail

ENVIRONMENT="${1:-}"

if [[ "$ENVIRONMENT" != "dev" && "$ENVIRONMENT" != "prod" ]]; then
  echo "Usage: $0 <dev|prod>"
  echo
  echo "Examples:"
  echo "  $0 dev"
  echo "  $0 prod"
  exit 1
fi

REGION="${REGION:-us-central1}"
NOTIFICATION_EMAIL="${NOTIFICATION_EMAIL:-}"

if [[ "$ENVIRONMENT" == "dev" ]]; then
  PROJECT_ID="gcp-project-506020"
  TF_STATE="terraform.tfstate"
  TF_VARS="dev.tfvars"
else
  PROJECT_ID="gcp-project-prod-506521"
  TF_STATE="prod.tfstate"
  TF_VARS="prod.tfvars"
fi

IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/covid-data/covid-pipeline:phase-7"

terraform init

echo
echo "==> Terraform plan..."
terraform plan \
  -state="$TF_STATE" \
  -var-file="$TF_VARS" \
  -var="project_id=$PROJECT_ID" \
  -var="location=$REGION" \
  -var="container_image=$IMAGE" \
  -var="app_version=phase-7" \
  -var="notification_email=$NOTIFICATION_EMAIL"

echo
echo "==> Terraform apply..."
terraform apply \
  -state="$TF_STATE" \
  -var-file="$TF_VARS" \
  -var="project_id=$PROJECT_ID" \
  -var="location=$REGION" \
  -var="container_image=$IMAGE" \
  -var="app_version=phase-7" \
  -var="notification_email=$NOTIFICATION_EMAIL" \
  -auto-approve

echo
echo "=========================================="
echo " Deployment completed successfully"
echo " Environment : $ENVIRONMENT"
echo " Project     : $PROJECT_ID"
echo " State       : $TF_STATE"
echo "=========================================="