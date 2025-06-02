# Render Deployment Guide

## Overview

This guide will help you deploy the ELI5 microservices to Render.

## Services to Deploy

1. **ELI5 Main Service** - Core API with AI explanations
2. **Auth Service** - User authentication and management
3. **History Service** - User explanation history
4. **PostgreSQL Database** - Persistent data storage

## Deployment Steps

### Step 1: Push Code to GitHub

Ensure your code is in a GitHub repository that Render can access.

### Step 2: Create PostgreSQL Database

1. Go to Render Dashboard → New → PostgreSQL
2. Name: `eli5-database`
3. Database Name: `eli5_db`
4. User: `eli5_user`
5. Region: Oregon (or your preferred region)
6. Plan: Free
7. Save the connection details for later

### Step 3: Deploy Auth Service

1. Go to Render Dashboard → New → Web Service
2. Connect your GitHub repository
3. Configuration:

   - Name: `eli5-auth-service`
   - Region: Oregon
   - Branch: main (or your default branch)
   - Root Directory: `auth_service`
   - Runtime: Docker
   - Dockerfile Path: `./Dockerfile`
   - Plan: Free

4. Environment Variables:

   - `DATABASE_URL`: [Use the PostgreSQL connection string from Step 2]
   - `SECRET_KEY`: [Generate a secure random string]
   - `ALGORITHM`: `HS256`
   - `ACCESS_TOKEN_EXPIRE_MINUTES`: `30`
   - `HISTORY_SERVICE_URL`: `https://eli5-history-service.onrender.com`
   - `ELI5_SERVICE_URL`: `https://eli5-service.onrender.com`

5. Deploy and wait for completion

### Step 4: Deploy History Service

1. Go to Render Dashboard → New → Web Service
2. Connect your GitHub repository
3. Configuration:

   - Name: `eli5-history-service`
   - Region: Oregon
   - Branch: main
   - Root Directory: `history_service`
   - Runtime: Docker
   - Dockerfile Path: `./Dockerfile`
   - Plan: Free

4. Environment Variables:

   - `DATABASE_URL`: [Same PostgreSQL connection string from Step 2]
   - `SECRET_KEY`: [Same as auth service]
   - `ALGORITHM`: `HS256`
   - `AUTH_SERVICE_URL`: `https://eli5-auth-service.onrender.com`
   - `ELI5_SERVICE_URL`: `https://eli5-service.onrender.com`

5. Deploy and wait for completion

### Step 5: Deploy ELI5 Main Service

1. Go to Render Dashboard → New → Web Service
2. Connect your GitHub repository
3. Configuration:

   - Name: `eli5-service`
   - Region: Oregon
   - Branch: main
   - Root Directory: `ELI5`
   - Runtime: Docker
   - Dockerfile Path: `./Dockerfile`
   - Plan: Free

4. Environment Variables:

   - `GEMINI_API_KEY`: [Your Google Gemini API key]
   - `GEMINI_MODEL`: `gemini-2.0-flash-thinking-exp-01-21`
   - `AUTH_SERVICE_URL`: `https://eli5-auth-service.onrender.com`
   - `HISTORY_SERVICE_URL`: `https://eli5-history-service.onrender.com`
   - `HTTP_TIMEOUT`: `30.0`
   - `HTTP_MAX_RETRIES`: `3`

5. Deploy and wait for completion

### Step 6: Update Frontend Configuration

Update your frontend deployment to use the new backend URL:

- Backend URL: `https://eli5-service.onrender.com`

### Step 7: Test the Deployment

1. Check that all services are healthy
2. Test user registration and login
3. Test explanation generation
4. Test history retrieval

## Important Notes

### Database Migration

Since you're moving from SQLite to PostgreSQL, you'll need to:

1. Update your database models to be PostgreSQL compatible
2. Run database migrations on the new PostgreSQL instance

### Free Tier Limitations

- Services may spin down after 15 minutes of inactivity
- First request after spin-down may take 30-60 seconds
- Limited to 750 hours per month per service

### Service URLs

After deployment, your services will be available at:

- Main API: `https://eli5-service.onrender.com`
- Auth API: `https://eli5-auth-service.onrender.com`
- History API: `https://eli5-history-service.onrender.com`

### Environment Variables Security

- Never commit actual API keys or secrets to your repository
- Use Render's environment variable management for sensitive data
- Consider using different SECRET_KEY values for different environments

## Troubleshooting

### Common Issues

1. **Build Failures**: Check Dockerfile syntax and dependencies
2. **Environment Variables**: Ensure all required variables are set
3. **Service Communication**: Verify service URLs are correct
4. **Database Connection**: Check PostgreSQL connection string format

### Monitoring

- Use Render's built-in logs to monitor service health
- Set up health check endpoints in your services
- Monitor service startup times and resource usage

## Scaling Considerations

- Start with free tier and monitor usage
- Upgrade to paid plans as needed for better performance
- Consider adding health checks and monitoring
- Implement proper error handling and retries for service communication
