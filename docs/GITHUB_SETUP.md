# GitHub Setup Instructions

## ✅ Git Repository Initialized!

Your local git repository is ready. Follow these steps to upload to GitHub:

## Step 1: Create GitHub Repository

1. Go to https://github.com/new
2. **Repository name:** `trump-truth-social-monitor` (or your preferred name)
3. **Description:** "AI-powered trading monitor for Trump's Truth Social posts"
4. **Visibility:** 
   - ✅ **Public** - If you want to share it
   - ✅ **Private** - If you want to keep it private (recommended for trading tools)
5. **DO NOT** initialize with README, .gitignore, or license (we already have these)
6. Click **"Create repository"**

## Step 2: Connect Your Local Repository to GitHub

After creating the repository, GitHub will show you commands. Use these:

```bash
# Add GitHub as remote origin
git remote add origin https://github.com/YOUR_USERNAME/trump-truth-social-monitor.git

# Push your code
git branch -M main
git push -u origin main
```

**Replace `YOUR_USERNAME` with your actual GitHub username!**

## Step 3: Verify Upload

1. Refresh your GitHub repository page
2. You should see all your files uploaded
3. Verify README.md displays correctly

## What's Been Included

✅ All core application files
✅ Complete test suite
✅ Full documentation
✅ Configuration examples
✅ Installation scripts
✅ .gitignore (protects sensitive files)

## What's NOT Included (Protected by .gitignore)

❌ `.env` file (your API keys - KEEP PRIVATE!)
❌ `data/*.json` files (your generated data)
❌ `__pycache__/` (Python cache)
❌ Log files

## Quick Commands Reference

```bash
# Check status
git status

# View commit history
git log --oneline

# Add new changes
git add .
git commit -m "Your commit message"
git push

# Pull latest changes (if working from multiple machines)
git pull
```

## Security Reminders

🔒 **NEVER commit these files:**
- `.env` (contains API keys)
- Any files with passwords or secrets
- Personal data files

✅ **Always use `.env.example` for sharing configuration format**

## Setting Up on Another Machine

When you clone the repo elsewhere:

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/trump-truth-social-monitor.git
cd trump-truth-social-monitor

# Install dependencies
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# Create your .env file
copy .env.example .env
# Then edit .env with your keys

# Test
python run_tests.py

# Run
python main.py
```

## Branch Strategy (Optional)

For more organized development:

```bash
# Create development branch
git checkout -b development

# Make changes...
git add .
git commit -m "Add new feature"

# Push development branch
git push -u origin development

# Merge to main when ready
git checkout main
git merge development
git push
```

## Troubleshooting

### "Permission denied"
Make sure you're logged into GitHub and have the correct repository URL.

### "Failed to push"
```bash
# Pull first, then push
git pull --rebase origin main
git push
```

### "Large files rejected"
GitHub has a 100MB file limit. Check what's being added:
```bash
git ls-files -s | sort -k4 -n -r | head -10
```

## Next Steps

1. Create GitHub repository
2. Run the commands from Step 2
3. Verify everything uploaded correctly
4. Share the repository link (if public)
5. Continue development!

---

**Your project is ready for GitHub! 🚀**

