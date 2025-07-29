# Zzzgrams Lambda Deployment Script (PowerShell)
# This script packages and deploys the Lambda function to AWS

param(
    [string]$FunctionName = "zzzgrams-sleep-analyzer",
    [string]$Region = "us-east-1"
)

# Stop on any error
$ErrorActionPreference = "Stop"

Write-Host "🚀 Starting Zzzgrams Lambda deployment..." -ForegroundColor Green

# Check if AWS CLI is installed
try {
    $awsVersion = aws --version
    Write-Host "✅ AWS CLI found: $awsVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ AWS CLI is not installed. Please install it first." -ForegroundColor Red
    exit 1
}

# Check if required environment variables are set
$requiredVars = @("SNOO_USERNAME", "SNOO_PASSWORD", "BABY_ID")
$missingVars = @()

foreach ($var in $requiredVars) {
    if (-not (Get-Variable -Name $var -ErrorAction SilentlyContinue)) {
        $missingVars += $var
    }
}

if ($missingVars.Count -gt 0) {
    Write-Host "❌ Missing required environment variables: $($missingVars -join ', ')" -ForegroundColor Red
    Write-Host "Please set these variables before running the deployment script." -ForegroundColor Yellow
    exit 1
}

# Create deployment directory
$DeployDir = "lambda-deployment"
Write-Host "📁 Creating deployment directory: $DeployDir" -ForegroundColor Blue

if (Test-Path $DeployDir) {
    Remove-Item -Recurse -Force $DeployDir
}
New-Item -ItemType Directory -Path $DeployDir | Out-Null

# Copy source code
Write-Host "📦 Copying source code..." -ForegroundColor Blue
Copy-Item -Recurse "src" $DeployDir
Copy-Item "lambda/lambda_function.py" $DeployDir

# Install dependencies
Write-Host "📦 Installing dependencies..." -ForegroundColor Blue
pip install -r requirements.txt -t $DeployDir

# Create deployment package
Write-Host "📦 Creating deployment package..." -ForegroundColor Blue
Set-Location $DeployDir
Compress-Archive -Path * -DestinationPath "../zzzgrams-lambda.zip" -Force
Set-Location ..

# Deploy to AWS Lambda
Write-Host "🚀 Deploying to AWS Lambda..." -ForegroundColor Blue
try {
    aws lambda update-function-code `
        --function-name $FunctionName `
        --zip-file "fileb://zzzgrams-lambda.zip" `
        --region $Region

    Write-Host "✅ Deployment completed successfully!" -ForegroundColor Green
    Write-Host "📦 Deployment package: zzzgrams-lambda.zip" -ForegroundColor Blue
    Write-Host "🔗 Lambda function: $FunctionName" -ForegroundColor Blue
} catch {
    Write-Host "❌ Deployment failed: $_" -ForegroundColor Red
    exit 1
}

# Clean up
Write-Host "🧹 Cleaning up..." -ForegroundColor Blue
Remove-Item -Recurse -Force $DeployDir
Remove-Item "zzzgrams-lambda.zip" -ErrorAction SilentlyContinue

Write-Host "🎉 Deployment finished!" -ForegroundColor Green 