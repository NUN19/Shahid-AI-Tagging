# Deploy to Render - Step by Step

## Quick Deployment Guide

### Step 1: Prepare Your Code

✅ Already done! Your code is ready.

### Step 2: Push to GitHub

1. **Initialize Git (if not already):**
   ```bash
   git init
   git add .
   git commit -m "Initial commit - Secure AI Tagging App"
   ```

2. **Create GitHub Repository:**
   - Go to https://github.com/new
   - Create a new repository (e.g., `ai-tagging-app`)
   - **Don't** initialize with README (you already have files)

3. **Push to GitHub:**
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/ai-tagging-app.git
   git branch -M main
   git push -u origin main
   ```

### Step 3: Deploy to Render

1. **Sign up at Render:**
   - Go to https://render.com
   - Sign up with GitHub (free)

2. **Create New Web Service:**
   - Click "New" → "Web Service"
   - Connect your GitHub repository
   - Select the repository you just pushed

3. **Configure Settings:**
   - **Name:** `ai-tagging-app` (or your choice)
   - **Environment:** `Python 3`
   - **Region:** Choose closest to you
   - **Branch:** `main`
   - **Root Directory:** (leave empty)
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`

4. **Add Environment Variables:**
   Click "Advanced" → "Add Environment Variable"
   - **Key:** `GEMINI_API_KEY`
   - **Value:** Your Gemini API key
   
   (Optional) Add:
   - **Key:** `SECRET_KEY`
   - **Value:** (Leave empty, will auto-generate)

5. **Deploy:**
   - Click "Create Web Service"
   - Wait 5-10 minutes for deployment
   - You'll see build logs in real-time

6. **Get Your URL:**
   - Once deployed, you'll get a URL like:
   - `https://ai-tagging-app.onrender.com`
   - **Share this URL!** 🎉

### Step 4: Update for Production (Optional)

After deployment, update `app.py` line 23:
```python
app.config['SESSION_COOKIE_SECURE'] = True  # For HTTPS
```

Then push again:
```bash
git add app.py
git commit -m "Enable secure cookies for production"
git push
```

Render will auto-deploy the update!

---

## That's It! 🎉

Your app is now live and shareable with a permanent URL!

**Benefits:**
- ✅ Permanent URL (doesn't change)
- ✅ 24/7 availability
- ✅ HTTPS included
- ✅ Free tier available
- ✅ Auto-deploys on git push

**Free Tier Limits:**
- App sleeps after 15 minutes of inactivity
- Wakes up on first request (may take 30 seconds)
- 750 hours/month free

**Need help?** Check Render docs: https://render.com/docs

