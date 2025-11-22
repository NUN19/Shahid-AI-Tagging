# Render Deployment - Quick Start

## 🎯 5-Minute Quick Guide

### 1. Go to Render
👉 https://render.com → Sign up with GitHub

### 2. Create Web Service
- Click "New" → "Web Service"
- Connect: `Shahid-AI-Tagging` repository

### 3. Settings
- **Name:** `shahid-ai-tagging`
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `gunicorn app:app`

### 4. Environment Variables
Add:
- `GEMINI_API_KEY` = your API key
- `SESSION_COOKIE_SECURE` = `true`

### 5. Deploy!
- Click "Create Web Service"
- Wait 5-10 minutes
- Get your link: `https://shahid-ai-tagging.onrender.com`

---

## 📋 Checklist

Before deploying, make sure:
- ✅ Code is on GitHub (https://github.com/NUN19/Shahid-AI-Tagging)
- ✅ You have your `GEMINI_API_KEY`
- ✅ You're signed up on Render

---

## 🎉 That's It!

Once deployed, share your link and users can:
1. Visit the link
2. Upload their mind map
3. Use the app!

---

**Detailed guide:** See `RENDER_DEPLOYMENT_STEPS.md`

