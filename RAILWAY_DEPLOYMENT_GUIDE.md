# Deploy to Railway - Complete Guide

## 🚀 Quick Deployment Steps

### Step 1: Sign Up for Railway

1. **Go to Railway:**
   - Visit: https://railway.app
   - Click "Start a New Project"

2. **Sign Up:**
   - Click "Login with GitHub"
   - Authorize Railway to access your GitHub

---

### Step 2: Create New Project

1. **In Railway Dashboard:**
   - Click "New Project"
   - Select "Deploy from GitHub repo"

2. **Select Repository:**
   - Find: `Shahid-AI-Tagging`
   - Click on it
   - Railway will start deploying automatically!

---

### Step 3: Configure Settings

Railway auto-detects Python, but verify:

1. **Settings Tab:**
   - **Start Command:** `gunicorn app:app`
   - **Build Command:** (auto-detected, should be fine)

2. **If not auto-detected:**
   - Go to Settings → Deploy
   - Set Start Command: `gunicorn app:app`

---

### Step 4: Add Environment Variables

1. **Go to Variables Tab:**
   - Click "New Variable"

2. **Add These Variables:**

   **Required:**
   - **Name:** `GEMINI_API_KEY`
   - **Value:** Your Gemini API key
   - Click "Add"

   **Recommended:**
   - **Name:** `SESSION_COOKIE_SECURE`
   - **Value:** `true`
   - Click "Add"

   - **Name:** `FLASK_ENV`
   - **Value:** `production`
   - Click "Add"

---

### Step 5: Get Your Shareable Link!

1. **Go to Settings Tab:**
   - Scroll to "Domains"
   - Railway generates a domain automatically
   - Format: `your-app-name.up.railway.app`

2. **Or Generate Custom Domain:**
   - Click "Generate Domain"
   - Get your custom URL

3. **Your app is live!** 🎉

---

## ✅ Verification

After deployment:

1. **Check Status:**
   - Should show "Deployed" (green)
   - No errors in logs

2. **Test Your App:**
   - Visit your Railway URL
   - Should see upload page
   - Test uploading Excel file
   - Test analyzing scenarios

---

## 🔧 Troubleshooting

### Build Fails:
- Check "Deploy Logs" tab
- Verify `requirements.txt` is correct
- Check Python version

### App Crashes:
- Check "Deploy Logs" for errors
- Verify `GEMINI_API_KEY` is set
- Check Start Command: `gunicorn app:app`

### Can't Access:
- Wait a few minutes (first deployment)
- Check deployment status
- Verify domain is active

---

## 📝 Quick Reference

**Your Railway URL:**
```
https://your-app-name.up.railway.app
```

**Update Code:**
```bash
git push origin main
```
Railway auto-deploys on push!

**View Logs:**
- Railway dashboard → Your project → Deployments → View logs

**Restart:**
- Railway dashboard → Deployments → Redeploy

---

## 💰 Cost

**Free Tier:**
- $5 credit/month
- Usually free for small apps
- Pay-as-you-go after credit
- No credit card required!

---

## 🎯 Next Steps

1. ✅ Sign up at Railway
2. ✅ Deploy from GitHub
3. ✅ Add environment variables
4. ✅ Get your shareable link
5. ✅ Test your app!

---

**Ready to deploy?** Follow the steps above - it takes about 5 minutes!

