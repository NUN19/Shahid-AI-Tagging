# Push Code to GitHub - Step by Step

## Your Repository URL:
```
https://github.com/NUN19/Shahid-AI-Tagging.git
```

## Method 1: Using Git Bash (Recommended)

1. **Open Git Bash** (search in Start Menu)

2. **Navigate to your project:**
   ```bash
   cd "/d/AI Shahid project"
   ```
   (Note: In Git Bash, use `/d/` for D: drive and forward slashes)

3. **Run these commands one by one:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit - AI Tagging App"
   git branch -M main
   git remote add origin https://github.com/NUN19/Shahid-AI-Tagging.git
   git push -u origin main
   ```

4. **When prompted:**
   - Enter your GitHub username: `NUN19`
   - Enter your GitHub password: (use a Personal Access Token, not your password)
   
   **To create a Personal Access Token:**
   - Go to: https://github.com/settings/tokens
   - Click "Generate new token" → "Generate new token (classic)"
   - Name: "Deployment Token"
   - Select scopes: `repo` (check the box)
   - Click "Generate token"
   - **Copy the token** (you'll only see it once!)
   - Use this token as your password when pushing

---

## Method 2: Using Batch File (Easier)

1. **Double-click `push_to_github.bat`** in your project folder
2. Follow the prompts
3. When asked for password, use Personal Access Token (see above)

---

## Method 3: Using GitHub Desktop (Easiest - No Commands!)

1. **Download GitHub Desktop:**
   - https://desktop.github.com/
   - Install it

2. **Open GitHub Desktop:**
   - File → Add Local Repository
   - Browse to: `D:\AI Shahid project`
   - Click "Add repository"

3. **Publish to GitHub:**
   - Click "Publish repository" button
   - Repository name: `Shahid-AI-Tagging`
   - Make sure "Keep this code private" is unchecked (or checked, your choice)
   - Click "Publish Repository"

---

## After Pushing

Once your code is on GitHub:

1. ✅ Go to: https://github.com/NUN19/Shahid-AI-Tagging
2. ✅ Verify all your files are there
3. ✅ Then proceed to deploy on Render!

---

## Troubleshooting

### "Authentication failed"
- Use Personal Access Token instead of password
- See instructions above to create token

### "Repository not found"
- Check the repository URL is correct
- Make sure repository exists on GitHub

### "Permission denied"
- Make sure you're using the correct GitHub username
- Use Personal Access Token with `repo` scope

---

**Which method do you prefer?** I recommend Method 1 (Git Bash) or Method 3 (GitHub Desktop) for easiest experience!

