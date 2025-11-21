# Step-by-Step Deployment Guide

## 🚀 Deploy to Render (Easiest - Free)

Follow these steps to get your permanent shareable link:

---

## Step 1: Install Git (If Not Installed)

1. **Download Git:**
   - Visit: https://git-scm.com/download/win
   - Download and install (use default options)
   - Restart terminal after installation

2. **Verify Installation:**
   ```bash
   git --version
   ```

---

## Step 2: Prepare Your Code

✅ **Already Done!** Your code is ready with:
- ✅ `Procfile` - For cloud deployment
- ✅ `requirements.txt` - With gunicorn
- ✅ `.gitignore` - Excludes sensitive files
- ✅ Secure session configuration

---

## Step 3: Initialize Git Repository

Open terminal in your project folder and run:

```bash
cd "d:\AI Shahid project"
git init
git add .
git commit -m "Initial commit - AI Tagging App"
```

**Note:** This creates a local git repository. Your `.env` file is already in `.gitignore`, so it won't be committed (secure!).

---

## Step 4: Create GitHub Repository

1. **Go to GitHub:**
   - Visit: https://github.com
   - Sign in (or create account - free)

2. **Create New Repository:**
   - Click "+" → "New repository"
   - Name: `ai-tagging-app` (or your choice)
   - Description: "AI-powered tag recommendation system"
   - **Make it Public** (or Private - your choice)
   - **DO NOT** initialize with README, .gitignore, or license
   - Click "Create repository"

3. **Copy the repository URL** (you'll see it on the next page)

---

## Step 5: Push to GitHub

In your terminal, run:

```bash
git remote add origin https://github.com/YOUR_USERNAME/ai-tagging-app.git
git branch -M main
git push -u origin main
```

**Replace `YOUR_USERNAME`** with your GitHub username!

You'll be prompted for GitHub credentials.

---

## Step 6: Deploy to Render

1. **Sign up at Render:**
   - Visit: https://render.com
   - Click "Get Started for Free"
   - Sign up with GitHub (easiest)

2. **Create New Web Service:**
   - Click "New" → "Web Service"
   - Click "Connect account" (if not connected)
   - Select your GitHub repository: `ai-tagging-app`
   - Click "Connect"

3. **Configure Settings:**
   
   **Basic Settings:**
   - **Name:** `ai-tagging-app` (or your choice)
   - **Region:** Choose closest to you
   - **Branch:** `main`
   - **Root Directory:** (leave empty)
   
   **Build & Deploy:**
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`

4. **Add Environment Variables:**
   
   Click "Advanced" → "Add Environment Variable"
   
   Add these variables:
   
   **Required:**
   - **Key:** `GEMINI_API_KEY`
   - **Value:** Your Gemini API key (from .env file)
   
   **Optional (but recommended):**
   - **Key:** `SESSION_COOKIE_SECURE`
   - **Value:** `true`
   
   - **Key:** `FLASK_ENV`
   - **Value:** `production`

5. **Deploy:**
   - Click "Create Web Service"
   - Wait 5-10 minutes for first deployment
   - Watch the build logs (you'll see progress)

---

## Step 7: Get Your Shareable Link! 🎉

Once deployment completes:

1. **You'll see:** "Your service is live"
2. **Your URL will be:** `https://ai-tagging-app.onrender.com`
   (or whatever name you chose)

3. **Share this URL!** Anyone can now:
   - Visit the link
   - Upload their mind map
   - Use the app

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
- Check build logs in Render dashboard
- Verify `requirements.txt` is correct
- Check Python version compatibility

### App Crashes:
- Check logs in Render dashboard
- Verify `GEMINI_API_KEY` is set correctly
- Check start command: `gunicorn app:app`

### Can't Access:
- Wait a few minutes (first deployment takes time)
- Check if service is "Live" (not "Sleeping")
- Free tier apps sleep after 15 min inactivity

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

## 🎯 Next Steps After Deployment

1. ✅ Test the app with the shareable link
2. ✅ Share with your team/users
3. ✅ Monitor usage in Render dashboard
4. ✅ Update code anytime (just push to GitHub)

---

## 💡 Pro Tips

1. **Free Tier:**
   - App sleeps after 15 min inactivity
   - Wakes up on first request (takes ~30 seconds)
   - 750 hours/month free

2. **Upgrade (Optional):**
   - $7/month for always-on service
   - No sleep, instant response

3. **Custom Domain:**
   - Can add your own domain
   - Free SSL certificate included

---

**Ready to deploy?** Follow the steps above and you'll have your shareable link in ~15 minutes! 🚀

