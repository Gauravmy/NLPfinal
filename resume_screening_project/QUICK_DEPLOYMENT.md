# Quick Deployment Reference

**Resume Screening Pro v3.0 - One-Page Deployment Guide**

---

## Option 1: Local (5 min) - FASTEST

```bash
cd resume_screening_project
pip install -r requirements.txt
python -m spacy download en_core_web_sm
streamlit run app.py
```
🌐 Opens at http://localhost:8501

---

## Option 2: Streamlit Cloud (2 min) - EASIEST PUBLIC

1. Push to GitHub
2. Go https://share.streamlit.io
3. Connect repo → Select app.py → Deploy
4. Share public URL!

✨ Free tier | No server management | Instant deployment

---

## Option 3: Docker (5 min)

```bash
docker build -t resume-screener .
docker run -p 8501:8501 resume-screener
```
🌐 Opens at http://localhost:8501

---

## Option 4: Cloud Platforms

| Platform | Command |
|----------|---------|
| **AWS** | EC2 + Streamlit (see guide) |
| **Google Cloud** | Cloud Run (Docker) |
| **Azure** | Container Instances |
| **DigitalOcean** | Droplet + Docker |

---

## Quick Troubleshooting

| Issue | Solution |
|-------|----------|
| "Module not found" | `pip install -r requirements.txt --upgrade` |
| First run slow | Normal! BERT loads (~60s). Cache used after. |
| Port 8501 in use | `streamlit run app.py --server.port 8502` |
| Out of memory | Use TF-IDF model or smaller batch |
| Can't find resumes | Check `data/resumes/` path exists |

---

## Required Structure

```
data/resumes/
├── ENGINEERING/
├── IT/
├── SALES/
└── ...
```
Organize by job category, use .txt files

---

## Features Checklist

- ✅ 4 ranking models (TF-IDF, BERT, Hybrid, Ensemble)
- ✅ Skill extraction & matching
- ✅ Multi-format export (CSV, Excel, JSON)
- ✅ Real-time visualization
- ✅ Model comparison
- ✅ Modern, accessible UI
- ✅ Production-ready

---

## File Quick Reference

| File | Purpose |
|------|---------|
| `app.py` | Main application (RUN THIS) |
| `requirements.txt` | Dependencies to install |
| `README.md` | User guide & overview |
| `DEPLOYMENT_GUIDE.md` | Full deployment instructions |
| `.streamlit/config.toml` | UI theme settings |
| `data/resumes/` | Resume data directory |

---

## Performance Tips

⚡ **Faster**: Use TF-IDF model, smaller batch size, close other apps

🎯 **Better**: Use Deep Ensemble, detailed job descriptions, quality resumes

💾 **Memory**: Limit to 500 resumes per run, clear cache if needed

---

## First Run Checklist

- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Download spacy model: `python -m spacy download en_core_web_sm`
- [ ] Run app: `streamlit run app.py`
- [ ] Load sample resumes from data/
- [ ] Enter job description
- [ ] Select Deep Ensemble model
- [ ] Click Analyze
- [ ] Review results in tabs
- [ ] Export to CSV/Excel

---

## Need Help?

📖 **Full Guide**: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)  
📚 **User Manual**: [README.md](README.md)  
✅ **Checklist**: [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)  
📊 **Summary**: [DEPLOYMENT_SUMMARY.md](DEPLOYMENT_SUMMARY.md)  

---

## System Requirements

- Python 3.8+
- 4GB RAM (8GB recommended)
- 2GB disk space
- Modern browser (Chrome, Firefox, Safari, Edge)

---

## Success = 3 Steps

```
1. Install dependencies
2. Run streamlit run app.py  
3. Load data and analyze
```

That's it! 🎉

---

## Which Deployment Option?

**Choose Local if**: Testing, single user, development  
**Choose Streamlit Cloud if**: Public access, no server management, free tier  
**Choose Docker if**: Server deployment, consistent environment  
**Choose Cloud if**: Enterprise, scaling, team access  

---

**Ready? Pick Option 1 or 2 above and start!**

Questions → See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md#troubleshooting)
