# Push with Personal Access Token

GitHub no longer accepts passwords. You need a **Personal Access Token**.

## Step 1: Create Personal Access Token

1. **Go to GitHub Settings:**
   - Visit: https://github.com/settings/tokens
   - Or: GitHub → Your Profile → Settings → Developer settings → Personal access tokens → Tokens (classic)

2. **Generate New Token:**
   - Click "Generate new token" → "Generate new token (classic)"
   - Name: `Deployment Token` (or any name)
   - Expiration: Choose duration (90 days recommended)
   - **Select scopes:** Check `repo` (this gives full repository access)
   - Scroll down and click "Generate token"

3. **Copy the Token:**
   - ⚠️ **IMPORTANT:** Copy the token NOW - you'll only see it once!
   - It looks like: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
   - Save it somewhere safe (password manager, notes, etc.)

## Step 2: Push Again with Token

### Option A: Use Git Bash

1. **Open Git Bash**

2. **Run these commands:**
   ```bash
   cd "/d/AI Shahid project"
   git push -u origin main
   ```

3. **When prompted:**
   - Username: `NUN19`
   - Password: **Paste your Personal Access Token** (not your GitHub password!)

### Option B: Use Batch Script

1. **Double-click `push_with_token.bat`** (I'll create this)
2. When asked for password, paste your token

## Step 3: Verify Success

1. Go to: https://github.com/NUN19/Shahid-AI-Tagging
2. You should see all your files:
   - `app.py`
   - `ai_analyzer.py`
   - `templates/`
   - `requirements.txt`
   - etc.

## After Success ✅

Once your code is on GitHub, we'll deploy to Render to get your shareable link!

---

**Need help?** Let me know if you see any errors!

