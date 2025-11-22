# Deploy to Render - Complete Step-by-Step Guide

## 🚀 Get Your Shareable Link in 10 Minutes!

---

## Step 1: Sign Up for Render

1. **Go to Render:**
   - Visit: https://render.com
   - Click "Get Started for Free"

2. **Sign Up:**
   - Click "Sign up with GitHub" (easiest option)
   - Authorize Render to access your GitHub account
   - Complete signup

---

## Step 2: Create New Web Service

1. **In Render Dashboard:**
   - Click "New" button (top right)
   - Select "Web Service"

2. **Connect Repository:**
   - Click "Connect account" if not connected
   - Select your GitHub account
   - Find and select: **`Shahid-AI-Tagging`**
   - Click "Connect"

---

## Step 3: Configure Your Service

Fill in these settings:

### Basic Settings:
- **Name:** `shahid-ai-tagging` (or your choice - will be in URL)
- **Region:** Choose closest to you (e.g., "Oregon (US West)")
- **Branch:** `main`
- **Root Directory:** (leave empty)

### Build & Deploy:
- **Environment:** `Python 3`
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `gunicorn app:app`

---

## Step 4: Add Environment Variables (IMPORTANT!)

Click "Advanced" → Scroll to "Environment Variables"

### Add These Variables:

1. **GEMINI_API_KEY** (Required)
   - **Key:** `GEMINI_API_KEY`
   - **Value:** Your Gemini API key (from your .env file)
   - Click "Add"

2. **SESSION_COOKIE_SECURE** (Recommended)
   - **Key:** `SESSION_COOKIE_SECURE`
   - **Value:** `true`
   - Click "Add"

3. **FLASK_ENV** (Optional)
   - **Key:** `FLASK_ENV`
   - **Value:** `production`
   - Click "Add"

---

## Step 5: Deploy!

1. **Review Settings:**
   - Make sure everything looks correct
   - Check environment variables are added

2. **Click "Create Web Service"**

3. **Wait for Deployment:**
   - You'll see build logs in real-time
   - First deployment takes 5-10 minutes
   - Watch the progress!

---

## Step 6: Get Your Shareable Link! 🎉

Once deployment completes:

1. **Status will show:** "Live" (green)
2. **Your URL will be:** `https://shahid-ai-tagging.onrender.com`
   (or whatever name you chose)

3. **Click the URL** to test your app!

4. **Share this URL** with anyone - they can use your app!

---

## ✅ Verification Checklist

After deployment, verify:

- [ ] App loads at the URL
- [ ] Setup page appears (upload mind map)
- [ ] Can upload Excel file
- [ ] Can analyze scenarios
- [ ] HTTPS is working (lock icon in browser)

---

## 🔧 Troubleshooting

### Build Fails:
- **Check logs** in Render dashboard
- Verify `requirements.txt` is correct
- Check Python version compatibility

### App Crashes:
- **Check logs** in Render dashboard
- Verify `GEMINI_API_KEY` is set correctly
- Check start command: `gunicorn app:app`

### Can't Access:
- Wait a few minutes (first deployment takes time)
- Check if service is "Live" (not "Sleeping")
- Free tier apps sleep after 15 min inactivity (wakes up on first request)

### Environment Variables Not Working:
- Verify variables are set in Render dashboard
- Check spelling (case-sensitive)
- Restart service after adding variables

---

## 📝 Quick Reference

**Your App URL:**
```
https://your-app-name.onrender.com
```

**Update Code:**
```bash
git add .
git commit -m "Update message"
git push
```
Render auto-deploys on push!

**View Logs:**
- Render dashboard → Your service → Logs

**Restart Service:**
- Render dashboard → Your service → Manual Deploy

---

## 💡 Free Tier Info

**What You Get:**
- ✅ Free hosting
- ✅ HTTPS included
- ✅ Auto-deploy on git push
- ✅ 750 hours/month

**Limitations:**
- ⚠️ App sleeps after 15 min inactivity
- ⚠️ Wakes up on first request (takes ~30 seconds)
- ⚠️ 750 hours/month limit

**Upgrade (Optional):**
- $7/month for always-on service
- No sleep, instant response

---

## 🎯 After Deployment

1. ✅ Test your app with the shareable link
2. ✅ Share with your team/users
3. ✅ Monitor usage in Render dashboard
4. ✅ Update code anytime (just push to GitHub)

---

## 🚀 Ready to Deploy?

1. Go to: https://render.com
2. Sign up with GitHub
3. Follow steps above
4. Get your shareable link!

**Need help?** Let me know if you encounter any issues!

