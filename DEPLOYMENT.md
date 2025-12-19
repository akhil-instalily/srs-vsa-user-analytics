# Deployment Guide

## Database Configuration for Cloud Run

### Issue: IP Whitelisting
Your local dev environment works because your IP is whitelisted in the PostgreSQL firewall rules. Cloud Run IPs are dynamic, so you have two options:

### Option 1: Cloud SQL Proxy (Recommended for Google Cloud SQL)
If using Google Cloud SQL, use the Cloud SQL Proxy connector:
```bash
gcloud sql instances describe INSTANCE_NAME
# Add --add-cloudsql-instances flag to Cloud Run deployment
```

### Option 2: Firewall Rule for Azure PostgreSQL (Recommended)
If using Azure PostgreSQL, add a firewall rule to allow Azure services:

1. Go to Azure Portal → Your PostgreSQL Server
2. Navigate to "Connection security"
3. Turn ON "Allow access to Azure services"
4. This allows all Azure/Cloud services to connect

Alternatively, you can whitelist specific IP ranges for Cloud Run:
- Get Cloud Run's egress IPs after deployment
- Add them to PostgreSQL firewall rules

### Option 3: Private Networking (Most Secure)
Set up VPC peering between Cloud Run and your database for private connectivity.

## Backend Deployment (Cloud Run)

### Prerequisites
- Google Cloud SDK installed
- Docker installed
- Project ID: `your-gcp-project-id`

### Steps

1. **Authenticate with Google Cloud**
```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

2. **Enable Required APIs**
```bash
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

3. **Build and Push Docker Image**
```bash
cd backend
docker build -t gcr.io/YOUR_PROJECT_ID/vsa-analytics-api .
docker push gcr.io/YOUR_PROJECT_ID/vsa-analytics-api
```

4. **Deploy to Cloud Run**
```bash
gcloud run deploy vsa-analytics-api \
  --image gcr.io/YOUR_PROJECT_ID/vsa-analytics-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars DB_HOST=your-db-host,DB_PORT=5432,DB_NAME=your-db,DB_USER=your-user \
  --set-secrets DB_PASSWORD=db-password:latest,GROQ_API_KEY=groq-api-key:latest \
  --memory 1Gi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 10
```

**Note:** Store secrets in Google Secret Manager:
```bash
echo -n "your-db-password" | gcloud secrets create db-password --data-file=-
echo -n "your-groq-key" | gcloud secrets create groq-api-key --data-file=-
```

5. **Get Service URL**
```bash
gcloud run services describe vsa-analytics-api --region us-central1 --format 'value(status.url)'
```

6. **Test the Deployment**
```bash
curl https://YOUR-SERVICE-URL/health
curl "https://YOUR-SERVICE-URL/analytics/session-metrics?start_date=2025-12-01T00:00:00&end_date=2025-12-31T23:59:59&product_context=pool&user_type=all"
```

## Frontend Deployment (Vercel)

### Steps

1. **Install Vercel CLI**
```bash
npm i -g vercel
```

2. **Login to Vercel**
```bash
vercel login
```

3. **Deploy from Frontend Directory**
```bash
cd frontend
vercel --prod
```

4. **Set Environment Variable**
In Vercel dashboard:
- Go to Project Settings → Environment Variables
- Add: `NEXT_PUBLIC_API_URL` = `https://your-cloud-run-url`
- Redeploy

Alternatively via CLI:
```bash
vercel env add NEXT_PUBLIC_API_URL production
# Enter your Cloud Run URL when prompted
vercel --prod
```

## Post-Deployment Checklist

- [ ] Database firewall allows Cloud Run connections
- [ ] Backend health check returns 200: `/health`
- [ ] Backend API returns data: `/analytics/session-metrics`
- [ ] Frontend loads and can fetch from backend
- [ ] Environment variables are set correctly
- [ ] CORS is properly configured for frontend domain

## Monitoring

### Cloud Run Logs
```bash
gcloud run services logs read vsa-analytics-api --region us-central1 --limit 50
```

### Vercel Logs
Check the Vercel dashboard or use:
```bash
vercel logs
```

## Troubleshooting

### Database Connection Failed
- Check if Azure "Allow access to Azure services" is enabled
- Verify DB credentials in Cloud Run environment variables
- Check Secret Manager permissions
- Test connection from Cloud Run:
  ```bash
  gcloud run services update vsa-analytics-api --set-env-vars DEBUG=true
  ```

### CORS Errors
- Update `app/main.py` to include your Vercel domain in `allow_origins`
- Redeploy backend

### High Latency
- Check if min-instances is 0 (cold starts)
- Consider setting min-instances to 1 for production
- Check database connection pooling settings
