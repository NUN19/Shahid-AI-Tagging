# Deploy to Fly.io - Free, Fast & Secure

## 🎯 Why Fly.io?

- ✅ **100% FREE** - 3 shared VMs (forever)
- ✅ **MUCH FASTER** than Render (no sleep mode!)
- ✅ **Always-on** - instant response
- ✅ **Same security** as Render
- ✅ **Global edge network**

---

## Step 1: Install Fly CLI

### Windows (PowerShell - Run as Administrator):

```powershell
iwr https://fly.io/install.ps1 -useb | iex
```

**Or download manually:**
- Visit: https://fly.io/docs/getting-started/installing-flyctl/
- Download Windows installer
- Run installer

**Verify installation:**
```bash
fly version
```

---

## Step 2: Sign Up

```bash
fly auth signup
```

This will:
- Open browser
- Let you sign up with GitHub (easiest)
- Authorize Fly.io

---

## Step 3: Deploy Your App

### Option A: Using fly.toml (Easiest)

I've created `fly.toml` for you! Just run:

```bash
cd "d:\AI Shahid project"
fly launch
```

Follow prompts:
- **App name:** `shahid-ai-tagging` (or your choice)
- **Region:** Choose closest (e.g., `iad` for US East)
- **PostgreSQL:** No
- **Redis:** No
- **Deploy now:** Yes

### Option B: Manual Setup

```bash
cd "d:\AI Shahid project"
fly launch --no-config
```

Then configure manually.

---

## Step 4: Add Environment Variables

```bash
fly secrets set GEMINI_API_KEY=your_actual_api_key_here
fly secrets set SESSION_COOKIE_SECURE=true
fly secrets set FLASK_ENV=production
```

**Replace `your_actual_api_key_here`** with your real Gemini API key!

---

## Step 5: Deploy!

```bash
fly deploy
```

Wait 2-3 minutes... Done! 🎉

---

## Step 6: Get Your URL

After deployment:

```bash
fly status
```

Or check Fly.io dashboard - your URL will be:
`https://shahid-ai-tagging.fly.dev`

---

## ✅ Verify It Works

1. Visit your Fly.io URL
2. Should load **instantly** (no 30-second wait!)
3. Test uploading mind map
4. Test analyzing scenarios

---

## 🔧 Troubleshooting

### "fly: command not found"
- Restart terminal after installation
- Or add Fly to PATH manually

### Deployment fails
- Check logs: `fly logs`
- Verify environment variables: `fly secrets list`
- Check `fly.toml` configuration

### App doesn't start
- Check port is 8080 (Fly.io requirement)
- Verify `PORT` environment variable
- Check logs: `fly logs`

---

## 📝 Useful Commands

```bash
# View logs
fly logs

# Check status
fly status

# List secrets
fly secrets list

# Update secrets
fly secrets set KEY=value

# Open app in browser
fly open

# SSH into app
fly ssh console
```

---

## 🎉 Benefits You'll Get

- ⚡ **Instant response** - no sleep delays
- ⚡ **Always-on** - no wake-up time
- ⚡ **Faster** - edge network
- ⚡ **Free** - 3 VMs forever
- ⚡ **Secure** - HTTPS, isolated

---

## 💰 Cost

**Free Tier:**
- 3 shared VMs (free forever)
- 160GB outbound data/month
- Usually enough for small apps
- No credit card required!

**If you exceed:**
- Pay-as-you-go
- Very cheap ($0.0000001 per second)
- Small apps usually stay free

---

## 🔄 Keep Render or Switch?

**You can:**
- Keep both (test which is better)
- Switch to Fly.io completely
- Use Fly.io for production

---

## 🚀 Ready to Deploy?

1. Install Fly CLI
2. Sign up: `fly auth signup`
3. Deploy: `fly launch`
4. Add secrets: `fly secrets set ...`
5. Deploy: `fly deploy`
6. Get your fast, free link!

**Need help?** Let me know if you encounter any issues!

