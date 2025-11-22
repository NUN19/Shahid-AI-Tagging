# Migrate from Render to Railway - Step by Step

## 🚀 Why Railway?

- ✅ **Much faster** than Render
- ✅ **No sleep mode** - always responsive
- ✅ **Free tier:** $5 credit/month (usually enough)
- ✅ **Same security** as Render
- ✅ **Easy setup** (5 minutes)

---

## Step 1: Sign Up for Railway

1. **Go to Railway:**
   - Visit: https://railway.app
   - Click "Start a New Project"

2. **Sign Up:**
   - Click "Login with GitHub"
   - Authorize Railway

---

## Step 2: Create New Project

1. **In Railway Dashboard:**
   - Click "New Project"
   - Select "Deploy from GitHub repo"

2. **Connect Repository:**
   - Find: `Shahid-AI-Tagging`
   - Click "Deploy Now"

---

## Step 3: Configure Service

Railway auto-detects Python, but verify:

1. **Settings Tab:**
   - **Start Command:** `gunicorn app:app`
   - **Build Command:** (auto-detected, should be fine)

2. **Variables Tab:**
   - Click "New Variable"
   - Add:
     - `GEMINI_API_KEY` = your API key
     - `SESSION_COOKIE_SECURE` = `true`
     - `FLASK_ENV` = `production`

---

## Step 4: Deploy!

1. **Railway auto-deploys** when you connect the repo
2. **Wait 2-3 minutes** (much faster than Render!)
3. **Get your URL:**
   - Railway generates a URL automatically
   - Format: `your-app-name.up.railway.app`
   - You can add custom domain later

---

## Step 5: Test

1. **Click your Railway URL**
2. **App should load quickly** (no 30-second wait!)
3. **Test uploading mind map**
4. **Test analyzing scenarios**

---

## ✅ Benefits You'll Notice

- ⚡ **Much faster** - no sleep mode delays
- ⚡ **Always responsive** - no waiting for wake-up
- ⚡ **Faster deployments** - 2-3 minutes vs 5-10
- ⚡ **Better user experience**

---

## 🔄 Keep Render or Switch?

**You can:**
- Keep both (test which you prefer)
- Switch completely to Railway
- Use Railway for production, Render as backup

---

## 💰 Cost

**Railway Free Tier:**
- $5 credit/month
- Usually free for low-traffic apps
- Pay-as-you-go after credit
- Much cheaper than Render's $7/month for always-on

---

## 🎯 Ready to Switch?

1. Go to: https://railway.app
2. Sign up with GitHub
3. Deploy your repo
4. Add environment variables
5. Get your faster link!

**Want help?** I can guide you through each step!

