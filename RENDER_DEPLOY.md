# Render Deployment Guide

## 🚀 Deploy to Render.com

### Step 1: Prepare Your Repository
✅ Already done! Your code is ready for deployment.

### Step 2: Deploy Backend (Django)

1. **Go to [Render.com](https://render.com)** and sign up/login with GitHub

2. **Click "New +" → "Web Service"**

3. **Connect your GitHub repository:**
   - Select `SMVINAYKUMAR2341/FOSSEE`
   - Click "Connect"

4. **Configure the service:**
   ```
   Name: fossee-backend
   Region: Choose closest to you
   Branch: main
   Root Directory: backend
   Runtime: Python 3
   Build Command: ./build.sh
   Start Command: gunicorn core.wsgi:application
   ```

5. **Select Free Plan** (or paid if you prefer)

6. **Add Environment Variables:**
   Click "Advanced" → Add Environment Variables:
   ```
   SECRET_KEY = your-super-secret-key-here-generate-random
   DEBUG = False
   ALLOWED_HOSTS = .onrender.com
   CORS_ALLOWED_ORIGINS = https://your-frontend-url.onrender.com
   PYTHON_VERSION = 3.11.0
   ```

7. **Click "Create Web Service"** 🎉

   Your backend will be deployed at: `https://fossee-backend.onrender.com`

### Step 3: Deploy Frontend (React)

1. **Click "New +" → "Static Site"**

2. **Connect your GitHub repository:**
   - Select `SMVINAYKUMAR2341/FOSSEE`
   - Click "Connect"

3. **Configure the static site:**
   ```
   Name: fossee-frontend
   Branch: main
   Root Directory: frontend-react
   Build Command: npm install && npm run build
   Publish Directory: frontend-react/build
   ```

4. **Add Environment Variable:**
   ```
   REACT_APP_API_URL = https://fossee-backend.onrender.com/api
   ```

5. **Click "Create Static Site"** 🎉

   Your frontend will be deployed at: `https://fossee-frontend.onrender.com`

### Step 4: Update Backend CORS

After frontend is deployed, update backend environment variable:
- Go to backend service → Environment
- Update `CORS_ALLOWED_ORIGINS` to your actual frontend URL
- Click "Save Changes"

---

## 🔗 Your Live URLs

- **Frontend:** https://fossee-frontend.onrender.com
- **Backend API:** https://fossee-backend.onrender.com/api
- **Admin Panel:** https://fossee-backend.onrender.com/admin

---

## ⚡ Quick Deploy Commands (Alternative - Render CLI)

```bash
# Install Render CLI
npm install -g render-cli

# Login
render login

# Deploy from render.yaml
render deploy
```

---

## 🧪 Testing Your Deployed App

1. Visit your frontend URL
2. Register a new account
3. Upload the sample CSV
4. Check visualizations
5. Download PDF report

---

## 🚨 Important Notes

### Free Tier Limitations:
- Apps spin down after 15 minutes of inactivity
- First request after idle may take 30-60 seconds (cold start)
- 750 hours/month free (enough for one app running 24/7)

### Database Consideration:
- SQLite works but data may be lost on restarts
- For production, upgrade to PostgreSQL (free tier available)

---

## 🔧 Troubleshooting

**If build fails:**
1. Check build logs in Render dashboard
2. Ensure `build.sh` has execute permissions
3. Verify all dependencies in requirements.txt

**If app crashes:**
1. Check logs in Render dashboard
2. Verify environment variables are set
3. Check ALLOWED_HOSTS includes your Render domain

**Static files not loading:**
1. Run `python manage.py collectstatic` locally first
2. Ensure whitenoise is in MIDDLEWARE
3. Check STATIC_ROOT is set correctly

---

## 📊 Monitoring

- **Metrics:** Render dashboard shows CPU, memory, bandwidth
- **Logs:** Real-time logs available in dashboard
- **Alerts:** Set up email alerts for crashes

---

## 🎉 You're All Set!

Your application is now live and accessible worldwide! Share your links:
- Frontend: `https://your-app.onrender.com`
- API Docs: `https://your-backend.onrender.com/api`
