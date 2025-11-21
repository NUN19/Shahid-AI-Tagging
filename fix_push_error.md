# Fix "failed to push some refs" Error

This error usually means the GitHub repository has files (like README) that your local repo doesn't have.

## Solution: Pull first, then push

Run these commands in Git Bash:

```bash
cd "/d/AI Shahid project"

# Pull the remote repository first (this merges remote files with local)
git pull origin main --allow-unrelated-histories

# If there are conflicts, resolve them, then:
git add .
git commit -m "Merge remote repository"

# Now push
git push -u origin main
```

## Alternative: Force push (if you don't need remote files)

**⚠️ Warning:** This will overwrite anything on GitHub with your local files.

```bash
cd "/d/AI Shahid project"
git push -u origin main --force
```

## Step-by-step fix:

1. Open Git Bash
2. Navigate: `cd "/d/AI Shahid project"`
3. Run: `git pull origin main --allow-unrelated-histories`
4. If asked for commit message, press Enter (use default)
5. Run: `git push -u origin main`

This should work!

