# Quick Start Guide - Secure Shareable Web App

## 🎉 What's New

Your app is now **secure and shareable**! Excel files are processed **entirely in the browser** - they never leave the user's device.

## 🚀 Quick Start

### 1. Test Locally

```bash
python app.py
```

Visit: `http://localhost:5000`

**First time:** You'll be redirected to `/setup` to upload your mind map.

### 2. Upload Mind Map

1. Click or drag your Excel file (.xlsx or .xls)
2. File is processed **in your browser** (secure!)
3. Click "Process & Continue"
4. You're redirected to the main app

### 3. Use the App

- Enter customer scenarios
- Upload images/videos
- Get AI tag recommendations
- Everything works as before!

## 🔒 Security Features

✅ **Excel processed in browser** - Never leaves your device  
✅ **Only tag structure sent to server** - No sensitive data  
✅ **Session-based storage** - No files on server  
✅ **Automatic cleanup** - Session expires after 24 hours

## 📤 Sharing Options

### Option 1: Cloud Deployment (Permanent Link)

**Recommended for production use**

1. **Push to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <your-repo-url>
   git push -u origin main
   ```

2. **Deploy to Render:**
   - Go to https://render.com
   - New → Web Service
   - Connect GitHub repo
   - Set environment variables:
     - `GEMINI_API_KEY` = your API key
     - `SECRET_KEY` = (optional, auto-generated)
   - Deploy
   - Share permanent link!

3. **Deploy to Heroku:**
   - Install Heroku CLI
   - `heroku create your-app-name`
   - `heroku config:set GEMINI_API_KEY=your_key`
   - `git push heroku main`
   - Share Heroku URL!

### Option 2: Ngrok (Temporary Link)

**For quick testing/sharing**

1. **Start your app:**
   ```bash
   python app.py
   ```

2. **In another terminal, start ngrok:**
   ```bash
   ngrok http 5000
   ```

3. **Share the ngrok URL** (e.g., `https://abc123.ngrok.io`)

4. **Note:** URL changes on restart (unless you use authtoken)

## 🔧 Configuration

### Environment Variables

Create `.env` file:
```env
GEMINI_API_KEY=your_gemini_api_key_here
SECRET_KEY=optional_secret_key_for_sessions
FLASK_HOST=0.0.0.0  # For cloud deployment
FLASK_PORT=5000
```

### Get Gemini API Key (Free!)

1. Visit: https://makersuite.google.com/app/apikey
2. Sign in with Google
3. Click "Create API Key"
4. Copy and add to `.env`

## 📋 Features

✅ **All original features preserved:**
- AI-powered tag recommendations
- Image/video analysis
- Bilingual interface (English/Arabic)
- Confidence levels
- Detailed reasoning
- Beautiful UI

✅ **New features:**
- Secure client-side Excel processing
- Session-based mind map storage
- Easy mind map upload
- Change mind map anytime

## 🐛 Troubleshooting

### "No mind map loaded"
- Upload a mind map at `/setup`
- Make sure Excel file is valid (.xlsx or .xls)

### "Error processing file"
- Check browser console for errors
- Ensure Excel file is not corrupted
- Try a different Excel file

### "GEMINI_API_KEY not found"
- Create `.env` file
- Add `GEMINI_API_KEY=your_key`
- Restart app

### Session expired
- Upload mind map again
- Sessions last 24 hours

## 📝 User Flow

1. **First Visit:**
   - User visits link
   - Redirected to `/setup`
   - Uploads Excel mind map
   - Redirected to main app

2. **Using App:**
   - Enter scenarios
   - Upload images/videos
   - Get recommendations
   - All features work!

3. **Change Mind Map:**
   - Click "Change Mind Map"
   - Upload new Excel file
   - Continue using app

## 🎯 Next Steps

1. ✅ Test locally
2. ✅ Deploy to cloud (Render/Heroku)
3. ✅ Share link with users
4. ✅ Users upload their own mind maps
5. ✅ Enjoy secure, shareable app!

---

**Questions?** Check `IMPLEMENTATION_SUMMARY.md` for detailed technical info!

