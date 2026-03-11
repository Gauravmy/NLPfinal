# Resume Screening Pro v3.0 - Deployment Guide

**Production-Ready Resume Screening System with Modern UI/UX**

---

## Quick Start

### Local Deployment (5 minutes)

```bash
# 1. Clone and setup
cd resume_screening_project

# 2. Install dependencies
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# 3. Run application
streamlit run app.py
```

The app will open at `http://localhost:8501`

---

## Requirements

- **Python**: 3.8 or higher
- **RAM**: 4GB minimum (8GB recommended)
- **Disk**: 2GB for dependencies
- **Modern Browser**: Chrome, Firefox, Safari, or Edge

---

## Features

### 4 Ranking Models
- **TF-IDF**: Fast, frequency-based matching
- **BERT**: Semantic understanding with transformers
- **Hybrid**: Combines TF-IDF + skill matching
- **Deep Ensemble**: Best accuracy, combines all models

### Analysis & Metrics
- Candidate ranking by relevance
- Skill extraction and matching
- Category distribution analysis
- Model comparison and visualization
- Performance metrics (precision, recall, MAP)

### Export Options
- CSV (for spreadsheets)
- Excel (formatted tables)
- JSON (for integrations)

---

## Directory Structure

```
resume_screening_project/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── .streamlit/           # Streamlit configuration
│   └── config.toml       # UI/Theme settings
├── data/                 # Resume sample data
│   └── resumes/         # Resumes organized by category
├── src/                 # Core modules
│   ├── resume_parser.py
│   ├── skill_extractor.py
│   ├── job_parser.py
│   ├── ranking_engine.py
│   ├── model_comparison.py
│   ├── evaluation.py
│   └── ...
├── Dockerfile           # For containerization
├── docker-compose.yml   # Multi-container setup
└── README.md            # This guide
```

---

## Deployment Options

### Option 1: Local Machine
```bash
streamlit run app.py
```
Perfect for: Testing, development, small teams

### Option 2: Streamlit Cloud (Recommended for Public Use)

1. **Create Streamlit Cloud Account**
   - Go to https://share.streamlit.io
   - Sign up with GitHub account

2. **Push Code to GitHub**
   ```bash
   git add .
   git commit -m "Deploy resume screening app"
   git push origin main
   ```

3. **Deploy on Streamlit Cloud**
   - Connect your GitHub repository
   - Select branch and app.py file
   - Click Deploy
   - Get a public URL instantly

**Live Demo**: Share the URL - no installation needed!

### Option 3: Docker Container

```bash
# Build image
docker build -t resume-screener .

# Run container
docker run -p 8501:8501 resume-screener

# Or with docker-compose
docker-compose up
```

Perfect for: Server deployments, cloud platforms

### Option 4: Cloud Platforms

#### AWS (EC2)
```bash
# Create Ubuntu instance
# Install Python 3.8+, clone repo, run streamlit
# Use security groups to open port 8501
```

#### Google Cloud (VM or App Engine)
```bash
# Deploy Docker container to Cloud Run
gcloud run deploy resume-screener --source .
```

#### Microsoft Azure
```bash
# Deploy using Azure App Service or Container Instances
```

---

## Configuration

### Theme & UI (.streamlit/config.toml)

```toml
[theme]
primaryColor = "#667eea"        # Purple
backgroundColor = "#f8f9fa"      # Light gray
secondaryBackgroundColor = "#e8e8f0"
textColor = "#262730"

[server]
headless = true
port = 8501
maxUploadSize = 200             # MB
enableXsrfProtection = true

[client]
showErrorDetails = false
toolbarMode = "minimal"
```

### Performance Tuning

```toml
[browser]
gatherUsageStats = false

[client]
maxMessageSize = 400            # KB
```

---

## Usage Guide

### 1. Load Resumes
- **Via Directory**: Resumes must be organized by category:
  ```
  data/resumes/
  ├── ENGINEERING/
  ├── IT/
  ├── SALES/
  └── ...
  ```
- **Browse Path**: Enter path in sidebar

### 2. Enter Job Description
- Copy-paste from job posting
- Include required and preferred skills
- Better descriptions = better results

### 3. Select Ranking Models
- Choose one or multiple models
- Compare results across models
- Deep Ensemble recommended for best accuracy

### 4. Analyze
- Click "Analyze" button
- Wait for processing (30-60 seconds first run)
- Results update in real-time with progress bar

### 5. Review Results
- **Rankings Tab**: Sortable candidate list
- **Analysis Tab**: Skills and category distribution
- **Comparison Tab**: Model performance comparison
- **Export Tab**: Download all results

---

## Performance Tips

### Faster Processing
1. Use TF-IDF only for quick screening
2. Process smaller resume batches
3. Cache models (automatic on first load)
4. Uses multi-processing where available

### Better Accuracy
1. Use Deep Ensemble model
2. Include detailed job descriptions
3. Ensure resume quality
4. Review category distribution

### Memory Management
1. Limit to 500 resumes per batch
2. Clear cache: `streamlit cache clear`
3. Monitor system RAM usage
4. Use smaller models for constrained systems

---

## Troubleshooting

### "Module not found" Error
```bash
pip install -r requirements.txt --upgrade
python -m spacy download en_core_web_sm
```

### Slow Processing
- First run loads BERT model (~500MB)
- Subsequent runs use cached model
- Can take 30-60 seconds for large batches

### Memory Issues
- Reduce batch size or resume count
- Close other applications
- Increase system RAM
- Use cloud deployment for scalability

### Data Not Found
- Verify path: `./data/resumes`
- Check category subdirectories exist
- Resumes must be `.txt` files
- Encoding must be UTF-8

---

## API Reference

### Main Functions

```python
from src.ranking_engine import rank_candidates
from src.model_comparison import rank_by_bert, rank_by_tfidf
from src.skill_extractor import extract_skills

# Rank candidates
results = rank_candidates(
    candidate_dict,      # {name: (text, skills)}
    job_description,     # str
    job_skills,         # set
    similarity_weight=0.7,
    skill_weight=0.3
)

# Extract skills
skills = extract_skills(resume_text)

# Get BERT rankings
bert_results = rank_by_bert(dataframe, job_description)
```

---

## Security

### Best Practices
1. ✓ No data stored on servers (Streamlit Cloud)
2. ✓ HTTPS encrypted transmission
3. ✓ CSRF protection enabled
4. ✓ Input validation on all fields
5. ✓ Error details hidden in production

### For Sensitive Data
- Use local deployment only
- Enable firewall restrictions
- Use VPN for remote access
- Audit resume data regularly

---

## Advanced Configuration

### Custom Models
```python
# In app.py or via API
from transformers import AutoModel
model = AutoModel.from_pretrained("your-model-name")
```

### Add Custom Skills
```python
# skill_extractor.py
CUSTOM_SKILLS = {
    'your_skill': ['synonym1', 'synonym2'],
    ...
}
```

### Environment Variables
```bash
# Create .env file
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_HEADLESS=true
STREAMLIT_LOGGER_LEVEL=error
```

---

## Monitoring & Analytics

### Local Metrics
- View metrics in app Analysis tab
- Export results for further analysis
- Check logs: `.streamlit/logs/`

### Cloud Monitoring
- Streamlit Cloud dashboard
- GitHub Actions for CI/CD
- Set up alerts for failures

---

## FAQs

**Q: Can I process PDFs directly?**
A: Currently requires .txt files. Use online PDF-to-text converters first.

**Q: How many resume can I process?**
A: Tested with 2,484 resumes. Larger sizes need server deployment.

**Q: Is this production-ready?**
A: Yes! Features 4 models, error handling, and modern UI. Ready for deployment.

**Q: Can I customize the models?**
A: Yes. Modify `src/model_comparison.py` or train custom models.

**Q: How to deploy to production?**
A: Use Streamlit Cloud, Docker, or cloud platforms (AWS, GCP, Azure).

---

## Support & Updates

- **GitHub**: [Your Repo URL]
- **Issues**: Report bugs on GitHub
- **Discussions**: Ask questions in Discussions
- **Updates**: Regular updates to models and features

---

## Version History

### v3.0.0 (Current)
- ✓ Modern, accessible UI/UX
- ✓ Production-ready with error handling
- ✓ 4 ranking models
- ✓ Improved performance and caching
- ✓ Better documentation

### v2.0.0
- BERT model integration
- Hybrid ranking
- Excel export

### v1.0.0
- Initial release
- TF-IDF ranking
- Basic UI

---

## License

This project is licensed under the MIT License.

---

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create feature branch
3. Submit pull request
4. Include tests and documentation

---

**Ready to deploy? Start with Option 2 (Streamlit Cloud) for instant public access!**
