#!/bin/bash

# Render Deployment Helper Script
# This script helps you deploy your ELI5 microservices to Render

set -e

echo "🚀 ELI5 Microservices Render Deployment Helper"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ] || [ ! -f "render.yaml" ]; then
    print_error "Please run this script from the ELI5 project root directory"
    exit 1
fi

print_step "Checking prerequisites..."

# Check if git is initialized
if [ ! -d ".git" ]; then
    print_warning "Git repository not initialized. Initializing..."
    git init
    git add .
    git commit -m "Initial commit for Render deployment"
fi

# Check if there are uncommitted changes
if ! git diff --quiet --exit-code; then
    print_warning "You have uncommitted changes. Committing them..."
    git add .
    git commit -m "Prepare for Render deployment"
fi

print_step "Validating service configurations..."

# Check if Dockerfiles exist
services=("ELI5" "auth_service" "history_service")
for service in "${services[@]}"; do
    if [ ! -f "$service/Dockerfile" ]; then
        print_error "Dockerfile not found for $service"
        exit 1
    fi
    if [ ! -f "$service/requirements.txt" ]; then
        print_error "requirements.txt not found for $service"
        exit 1
    fi
    print_success "✓ $service configuration valid"
done

print_step "Environment variables check..."

# Check if .env exists (for reference)
if [ ! -f ".env" ]; then
    print_warning ".env file not found. Make sure you have your environment variables ready for Render."
fi

echo ""
echo "📋 Pre-deployment Checklist:"
echo "=============================="
echo "Before proceeding with Render deployment, make sure you have:"
echo ""
echo "✅ GitHub repository with your code pushed"
echo "✅ Render account (free tier is fine)"
echo "✅ Google Gemini API key"
echo "✅ Generated a secure SECRET_KEY for production"
echo ""

# Generate a sample SECRET_KEY
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
echo "💡 Sample SECRET_KEY for production: $SECRET_KEY"
echo ""

echo "🔗 Deployment URLs (after deployment):"
echo "======================================"
echo "• Main API: https://eli5-service.onrender.com"
echo "• Auth API: https://eli5-auth-service.onrender.com"
echo "• History API: https://eli5-history-service.onrender.com"
echo ""

echo "📖 Next Steps:"
echo "==============="
echo "1. Push your code to GitHub if you haven't already:"
echo "   git remote add origin <your-github-repo-url>"
echo "   git push -u origin main"
echo ""
echo "2. Follow the deployment guide in RENDER_DEPLOYMENT.md"
echo "3. Deploy services in this order:"
echo "   a) PostgreSQL Database"
echo "   b) Auth Service"
echo "   c) History Service"
echo "   d) ELI5 Main Service"
echo ""
echo "4. Update your frontend to use the new backend URL"
echo ""

read -p "Do you want to push changes to git now? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_step "Checking git remote..."
    
    if ! git remote get-url origin > /dev/null 2>&1; then
        print_warning "No git remote 'origin' found."
        echo "Please add your GitHub repository URL:"
        read -p "Enter GitHub repository URL: " repo_url
        git remote add origin "$repo_url"
    fi
    
    print_step "Pushing to GitHub..."
    git push -u origin main
    print_success "Code pushed to GitHub successfully!"
else
    print_warning "Remember to push your code to GitHub before deploying to Render"
fi

echo ""
print_success "Deployment preparation complete!"
echo "Please follow the detailed steps in RENDER_DEPLOYMENT.md to deploy your services."
