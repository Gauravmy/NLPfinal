# 🚀 Deploy Resume Screening Pro to Streamlit Cloud

## Quick Start (5 Minutes)

### Step 1: Setup GitHub SSH Key (One-time)

Since password authentication isn't supported, use SSH:

```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "your-email@gmail.com"

# When prompted:
# - File location: Press Enter (default)
# - Passphrase: Press Enter twice (empty)

# Copy the public key
# (On Windows PowerShell)
Get-Content $env:USERPROFILE\.ssh\id_ed25519.pub | Set-Clipboard
```

Add to GitHub:
1. Go to: https://github.com/settings/keys
2. Click "New SSH key"
3. Paste the key
4. Click "Add SSH key"

---

### Step 2: Update Git Remote (if using HTTPS)

```bash
cd c:\Users\hp\Desktop\NLPpro

# Change remote from HTTPS to SSH
git remote remove origin
git remote add origin git@github.com:gaurav2302221-cell/NLP-G1.git

# Verify
git remote -v
```

---

### Step 3: Commit & Push Code

```bash
cd c:\Users\hp\Desktop\NLPpro

# Make sure you're on main branch
git checkout main

# Add all changes
git add -A

# Commit
git commit -m "Resume Screening Pro v4.1 - Premium UI/UX with Dark Theme"

# Push to GitHub
git push origin main
```

**Expected output:**
```
✓ Working tree clean
✓ 3 files changed
✓ Pushed to origin/main
```

---

### Step 4: Deploy to Streamlit Cloud

1. **Sign In to Streamlit Cloud**
   - Go to: https://share.streamlit.io
   - Click "Sign in with GitHub"
   - Authorize Streamlit

2. **Create New App**
   - Click "New app" button
   - Select:
     - Repository: `gaurav2302221-cell/NLP-G1`
     - Branch: `main`
     - File path: `resume_screening_project/app.py`

3. **Configure (Optional)**
   - Advanced settings (if needed)
   - Python 3.11 recommended
   - Leave other settings as default

4. **Deploy**
   - Click "Deploy" button
   - Wait 2-3 minutes
   - ✅ Your app is live!

---

## 📍 Your Public URL

After deployment, your app will be available at:
```
https://resume-screening-[unique-id].streamlit.app
```

Share this link with anyone!

---

## 🎯 What Gets Deployed

✅ `app.py` - Main application  
✅ `src/` - All source modules  
✅ `requirements.txt` - Dependencies  
✅ `runtime.txt` - Python version  
✅ `packages.txt` - System packages  
✅ `data/resumes/` - Sample data  

---

## 🔧 Troubleshooting

### "Authentication failed"
```
Fix: Use SSH instead of HTTPS (follow Step 2)
```

### App doesn't start
```
Fix: Check Python version in runtime.txt
Fix: Ensure all imports in app.py are correct
Fix: Verify requirements.txt has all packages
```

### Resume upload fails
```
Fix: Ensure pdfplumber, python-docx are in requirements.txt
Fix: File size under 200MB
```

### App times out
```
Fix: Model loading takes time on first run
Fix: Subsequent runs are fast due to caching
```

---

## 📊 Deployment Checklist

Before deploying:

- [ ] All code committed to git
- [ ] GitHub remote is correct (git remote -v)
- [ ] No authentication errors
- [ ] App runs locally: `streamlit run app.py`
- [ ] No hardcoded file paths
- [ ] requirements.txt is complete
- [ ] Python version in runtime.txt is 3.11+

---

## ✨ Features Available After Deploy

Users will be able to:

✅ Upload resumes (TXT, PDF, DOCX)  
✅ Paste job descriptions  
✅ Select AI models (BERT, TF-IDF, Hybrid, Ensemble)  
✅ See skill matching percentages  
✅ View interactive charts  
✅ Export results (CSV/Excel)  
✅ All with beautiful UI!  

---

## 💰 Cost

**Free Tier:**
- ✅ 3 apps
- ✅ Unlimited usage
- ✅ Public apps
- ✅ Perfect for demo/portfolio

**Pro Tier ($20/month):**
- Private apps
- Custom domains
- Priority support
- Increased compute

---

## 🎉 Success!

Once deployed:
1. ✅ App is live on the internet
2. ✅ No local server needed
3. ✅ Share URL with anyone
4. ✅ 24/7 availability
5. ✅ Professional portfolio piece

---

## 📞 Support

- **Streamlit Docs**: https://docs.streamlit.io
- **Cloud Guide**: https://docs.streamlit.io/streamlit-cloud
- **Community**: https://discuss.streamlit.io

---

## 🔐 Security Notes

✅ All data processed locally (no server storage)  
✅ HTTPS encryption by default  
✅ No external API calls  
✅ User data stays with user  
✅ Open source = reviewable code  

---

**Good luck! 🚀**

Your Resume Screening Pro is about to go live! 🎉
