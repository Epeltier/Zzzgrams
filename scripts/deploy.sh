#!/bin/bash

# Zzzgrams Lambda Deployment Script
# This script packages and deploys the Lambda function to AWS

set -e  # Exit on any error

echo "🚀 Starting Zzzgrams Lambda deployment..."

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI is not installed. Please install it first."
    exit 1
fi

# Check if required environment variables are set
if [ -z "$AWS_PROFILE" ] && [ -z "$AWS_ACCESS_KEY_ID" ]; then
    echo "❌ AWS credentials not configured. Please set AWS_PROFILE or AWS_ACCESS_KEY_ID/AWS_SECRET_ACCESS_KEY"
    exit 1
fi

# Create deployment directory
DEPLOY_DIR="lambda-deployment"
echo "📁 Creating deployment directory: $DEPLOY_DIR"
rm -rf $DEPLOY_DIR
mkdir -p $DEPLOY_DIR

# Copy source code
echo "📦 Copying source code..."
cp -r src/ $DEPLOY_DIR/
cp lambda/lambda_function.py $DEPLOY_DIR/

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt -t $DEPLOY_DIR/

# Create deployment package
echo "📦 Creating deployment package..."
cd $DEPLOY_DIR
zip -r ../zzzgrams-lambda.zip .
cd ..

# Deploy to AWS Lambda
echo "🚀 Deploying to AWS Lambda..."
aws lambda update-function-code \
    --function-name zzzgrams-sleep-analyzer \
    --zip-file fileb://zzzgrams-lambda.zip \
    --region us-east-1

echo "✅ Deployment completed successfully!"
echo "📦 Deployment package: zzzgrams-lambda.zip"
echo "🔗 Lambda function: zzzgrams-sleep-analyzer"

# Clean up
echo "🧹 Cleaning up..."
rm -rf $DEPLOY_DIR
rm zzzgrams-lambda.zip

echo "🎉 Deployment finished!" 