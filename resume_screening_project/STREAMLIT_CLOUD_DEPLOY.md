# Streamlit Cloud Deployment Instructions

## Quick Deployment to Streamlit Cloud (2 minutes)

### Prerequisites
- GitHub account (free)
- Streamlit Cloud account (free at share.streamlit.io)

### Step 1: Prepare Repository
```bash
# This code is already git-ready. Just ensure these files exist:
# - app.py (main application)
# - requirements.txt (dependencies)
# - .gitignore (for clean repo)

git add .
git commit -m "Resume Screening Pro v3.0 - Ready for Streamlit Cloud"
git push origin main
```

### Step 2: Connect to Streamlit Cloud
1. Go to https://share.streamlit.io
2. Click "New App"
3. Fill in:
   - GitHub repo: `your-username/resume-screening` (or your repo name)
   - Branch: `main`
   - Main file path: `resume_screening_project/app.py`
4. Click "Deploy"

### Step 3: Configuration (Optional)
Advanced users can create `.streamlit/secrets.toml` for sensitive data:
```toml
# Don't commit this file - Streamlit Cloud has built-in secrets management
# Access via: st.secrets["key_name"]
```

### Step 4: Access Your App
- Streamlit Cloud will assign a public URL
- Share it with your team immediately!
- App updates automatically when you push to GitHub

---

## Alternative: Deploy from Local Machine

### Option A: Using Streamlit CLI
```bash
streamlit login  # Connect to Streamlit account
streamlit run app.py
```

### Option B: Using Git
```bash
git push origin main  # Streamlit Cloud auto-deploys
```

---

## Optimization Tips for Streamlit Cloud

### Performance
1. App uses lazy loading to reduce startup time
2. Models cached automatically
3. Data cached with @st.cache_data

### Storage Limits
- Streamlit Cloud: 1GB per app
- Not a problem for resume screening

### Resource Usage
- CPU: Sufficient for 500+ resume batches
- RAM: 1GB available (enough for BERT + data)
- No GPU (but not needed for this workload)

---

## Troubleshooting

### App Won't Deploy
- Check requirements.txt syntax
- Verify all imports available
- Check GitHub repo access

### Slow First Run
- BERT model loads on first use (~60s)
- Subsequent runs cached (5-15s)
- This is normal and expected

### Out of Memory
- Use TF-IDF model instead of BERT
- Process smaller resume batches
- Clear cache in app settings

---

## Monitoring Your Deployment

1. **View Logs**: Click ☰ → Settings → Logs
2. **Check Status**: Dashboard shows app status
3. **Performance**: Monitor from Streamlit Cloud console

---

## Enable GitHub Integration

Make your deployment automatic:

1. In Streamlit Cloud app settings
2. Enable "Auto-deploy on push"
3. All GitHub commits trigger app update

---

## Custom Domain (Advanced)

Streamlit Cloud provides:
- Default: `app-name.streamlit.app`
- Custom domain available with Streamlit+ subscription

---

## Share Your App

After deployment:
1. Copy the app URL
2. Share via email, social media, or website
3. Anyone can access without installation

---

## Security Considerations

- No resume data stored on Streamlit Cloud
- All processing happens in the app
- Use GitHub secrets for any API keys
- Enabled CSRF protection by default

---

## Cost

- **Free Tier**: Unlimited apps, 1 GB storage, 15 restarts/day
- **Streamlit+**: $5/month for more resources and custom domains

Most users stay on free tier!

---

## Success!

Your app is now live and accessible to everyone!

Share the URL and start screening resumes.
