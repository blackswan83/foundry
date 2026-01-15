# Deploying to Railway

This guide covers deploying the Nuraxi Foundry Demo to Railway.

## Option 1: Two Services (Recommended)

Deploy backend and frontend as separate Railway services for independent scaling.

### Step 1: Create Railway Project

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login
```

### Step 2: Create Project and Services

1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Click "New Project" → "Empty Project"
3. Name it "nuraxi-foundry"

### Step 3: Deploy Backend

```bash
cd backend

# Link to Railway project
railway link

# Create a new service called "api"
railway service create api

# Deploy
railway up
```

Note the backend URL (e.g., `https://api-production-xxxx.up.railway.app`)

### Step 4: Deploy Frontend

```bash
cd frontend

# Link to same Railway project
railway link

# Create a new service called "web"
railway service create web

# Set environment variable for API URL
railway variables set VITE_API_URL=https://api-production-xxxx.up.railway.app/api

# Deploy
railway up
```

### Step 5: Configure Custom Domains (Optional)

In Railway Dashboard:
1. Select your service
2. Go to Settings → Domains
3. Add custom domain or use Railway subdomain

---

## Option 2: Single Service

Deploy everything as one Railway service (simpler but less scalable).

### Deploy from Root

```bash
# From project root
cd foundry

# Login and link
railway login
railway link

# Deploy
railway up
```

The backend serves the API at `/api/*`. Configure your frontend to use relative paths.

---

## Environment Variables

### Backend
| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Server port | 8000 |
| `ALLOWED_ORIGINS` | Comma-separated list of allowed CORS origins | Auto-detected (same-origin) |
| `ALLOW_RAILWAY_DOMAINS` | Allow all Railway domains (dev only) | `false` |
| `RAILWAY_PUBLIC_DOMAIN` | Railway-provided public domain | Auto-set by Railway |

### Frontend
| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_URL` | Backend API URL | `/api` |
| `PORT` | Server port | 3000 |

### CORS Configuration

**Single Service (Frontend served by Backend):**
- No configuration needed - works automatically ✅

**Two Services (Separate URLs):**
```bash
# In backend service
railway variables set ALLOWED_ORIGINS=https://your-frontend-url.railway.app

# In frontend service  
railway variables set VITE_API_URL=https://your-backend-url.railway.app/api
```

---

## Quick Deploy via GitHub

1. Push code to GitHub
2. In Railway Dashboard, click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your repository
5. Railway auto-detects the configuration

For monorepo setup:
- Set **Root Directory** to `backend` for API service
- Set **Root Directory** to `frontend` for web service

---

## Verify Deployment

### Backend Health Check
```bash
curl https://your-backend-url.railway.app/health
```

### API Documentation
Visit: `https://your-backend-url.railway.app/api/docs`

### Frontend
Visit: `https://your-frontend-url.railway.app`

---

## Troubleshooting

### Build Fails
- Check Railway logs: `railway logs`
- Ensure Python 3.12+ and Node 22+ are available

### API Connection Issues
- Verify `VITE_API_URL` is set correctly in frontend service
- Check CORS settings in backend (currently allows all origins for demo)

### Port Issues
- Railway sets `PORT` automatically, ensure your app reads it

---

## Cost Estimate

Railway Hobby Plan ($5/month):
- Includes 512 MB RAM per service
- 100 GB bandwidth
- Sufficient for demo purposes

For production: Consider Pro plan for more resources.
