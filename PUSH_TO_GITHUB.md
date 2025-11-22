# Push to GitHub - Simple Guide

## 🚀 Quick Steps

### Step 1: Open Git Bash

Search "Git Bash" in Start Menu and open it.

### Step 2: Navigate to Project

```bash
cd "/d/AI Shahid project"
```

### Step 3: Check What Changed

```bash
git status
```

You should see:
- Modified files (app.py, templates, etc.)
- Deleted files (all the cleanup)
- New files (railway.json, fly.toml)

### Step 4: Add All Changes

```bash
git add .
```

This adds:
- All modified files
- All deleted files
- All new files

### Step 5: Commit Changes

```bash
git commit -m "Clean up project and fix errors"
```

### Step 6: Push to GitHub

```bash
git push origin main
```

If asked for password, use your **Personal Access Token** (not GitHub password).

---

## ✅ That's It!

After pushing:
- ✅ Changes will be on GitHub
- ✅ Railway will auto-deploy (1-2 minutes)
- ✅ Your deployed app will update

---

## 🔑 Personal Access Token

If Git asks for password:

1. Go to: https://github.com/settings/tokens
2. Generate new token (classic)
3. Check `repo` scope
4. Copy token
5. Use token as password when pushing

---

## 📝 Quick Command Summary

```bash
cd "/d/AI Shahid project"
git add .
git commit -m "Clean up project and fix errors"
git push origin main
```

---

**Ready?** Open Git Bash and run these commands!

