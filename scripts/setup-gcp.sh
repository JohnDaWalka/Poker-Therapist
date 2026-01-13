#!/bin/bash
# setup-gcp.sh - Automate Google Cloud Platform setup for Poker Therapist

set -e

GREEN='\033[0;32m'
NC='\033[0m'

echo -e "${GREEN}Poker Therapist GCP Setup${NC}"

PROJECT_ID="${GCP_PROJECT_ID:-poker-therapist-prod}"
REGION="${GCP_REGION:-us-central1}"
BUCKET_NAME="${GCP_BUCKET_NAME:-poker-therapist-data}"
SERVICE_ACCOUNT_NAME="poker-therapist-sa"

echo "Creating project $PROJECT_ID..."
gcloud projects create $PROJECT_ID --name="Poker Therapist" || echo "Project exists"
gcloud config set project $PROJECT_ID

echo "Enabling APIs..."
gcloud services enable storage.googleapis.com iam.googleapis.com

echo "Creating bucket..."
gsutil mb -p $PROJECT_ID -c STANDARD -l $REGION gs://$BUCKET_NAME/ || echo "Bucket exists"

echo "Creating service account..."
gcloud iam service-accounts create $SERVICE_ACCOUNT_NAME --display-name="Poker Therapist SA" || echo "SA exists"

echo "Setup complete!"
