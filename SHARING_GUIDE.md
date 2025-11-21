# How to Share Your App

You have **2 options** to share your app:

## 🚀 Option 1: Ngrok (Quick & Easy - Temporary Link)

**Best for:** Quick testing, temporary sharing, immediate access

### Setup Steps:

1. **Download Ngrok:**
   - Visit: https://ngrok.com/download
   - Download for Windows
   - Extract `ngrok.exe` to a folder (e.g., `C:\ngrok\`)
   - Or add to PATH for easy access

2. **Start Your App** (if not already running):
   ```bash
   python app.py
   ```

3. **In a NEW terminal, start Ngrok:**
   ```bash
   ngrok http 5000
   ```
   
   Or if ngrok is not in PATH:
   ```bash
   C:\path\to\ngrok.exe http 5000
   ```

4. **Copy the Ngrok URL:**
   - You'll see something like: `https://abc123.ngrok.io`
   - Copy this URL
   - **Share this URL** with anyone!

### Ngrok Features:
- ✅ **Instant sharing** - No setup needed
- ✅ **HTTPS included** - Secure connection
- ✅ **Free tier available**
- ⚠️ **URL changes** on restart (unless you use authtoken)
- ⚠️ **Requires your PC to be running**

### Get Stable URL (Optional):
1. Sign up at https://dashboard.ngrok.com (free)
2. Get your authtoken
3. Run: `ngrok config add-authtoken YOUR_TOKEN`
4. Now your URL stays the same!

---

## ☁️ Option 2: Cloud Deployment (Permanent Link)

**Best for:** Production use, permanent access, 24/7 availability

### Option A: Render (Recommended - Easiest)

1. **Create GitHub Repository:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   ```
   
   Then push to GitHub:
   - Create repo on GitHub
   - `git remote add origin https://github.com/yourusername/your-repo.git`
   - `git push -u origin main`

2. **Deploy to Render:**
   - Go to https://render.com
   - Sign up (free)
   - Click "New" → "Web Service"
   - Connect your GitHub repository
   - Configure:
     - **Name:** your-app-name
     - **Environment:** Python 3
     - **Build Command:** `pip install -r requirements.txt`
     - **Start Command:** `gunicorn app:app`
   - Add Environment Variables:
     - `GEMINI_API_KEY` = your API key
     - `SECRET_KEY` = (optional, auto-generated)
   - Click "Create Web Service"
   - Wait for deployment (~5 minutes)
   - **Share your permanent URL!** (e.g., `https://your-app.onrender.com`)

### Option B: Heroku

1. **Install Heroku CLI:**
   - Download from: https://devcenter.heroku.com/articles/heroku-cli

2. **Create Procfile:**
   ```
   web: gunicorn app:app
   ```

3. **Deploy:**
   ```bash
   heroku login
   heroku create your-app-name
   heroku config:set GEMINI_API_KEY=your_key_here
   git push heroku main
   ```

4. **Share URL:** `https://your-app-name.herokuapp.com`

### Option C: Railway

1. Go to https://railway.app
2. Sign up with GitHub
3. New Project → Deploy from GitHub
4. Select your repo
5. Add environment variables
6. Deploy!

---

## 📊 Comparison

| Feature | Ngrok | Cloud (Render/Heroku) |
|---------|-------|----------------------|
| **Setup Time** | 2 minutes | 10-15 minutes |
| **URL Type** | Temporary | Permanent |
| **Cost** | Free | Free tier available |
| **Requires PC Running** | ✅ Yes | ❌ No |
| **24/7 Availability** | ❌ No | ✅ Yes |
| **Best For** | Testing, quick share | Production, permanent |

---

## 🎯 Quick Start (Ngrok - Fastest)

Since your app is already running, here's the fastest way:

1. **Download Ngrok:**
   - https://ngrok.com/download
   - Extract `ngrok.exe`

2. **Open new terminal and run:**
   ```bash
   ngrok http 5000
   ```

3. **Copy the HTTPS URL** (e.g., `https://abc123.ngrok.io`)

4. **Share it!** Anyone can access your app with this link.

---

## 🔒 Security Note

- **Ngrok:** Provides HTTPS automatically ✅
- **Cloud:** Make sure to set `SESSION_COOKIE_SECURE = True` in production
- Both options are secure for sharing!

---

## 💡 Recommendation

- **For quick testing:** Use Ngrok (2 minutes)
- **For permanent sharing:** Use Render/Heroku (15 minutes)

**Want me to help you set up one of these?** Just let me know which option you prefer!

