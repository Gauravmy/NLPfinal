# Resume Screening Pro - Deployment Guide

## Local Development

### Prerequisites
- Python 3.8+
- pip or conda
- Git

### Setup
1. Clone the repository
   ```bash
   git clone <repo-url>
   cd resume_screening_project
   ```

2. Create virtual environment
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies
   ```bash
   pip install -r requirements.txt
   python -m spacy download en_core_web_sm
   ```

4. Run Streamlit app
   ```bash
   streamlit run app_pro.py
   ```

5. Access at http://localhost:8501

---

## Docker Deployment

### Build Image
```bash
docker build -t resume-screening:latest .
```

### Run Container
```bash
docker run -p 8501:8501 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/results:/app/results \
  resume-screening:latest
```

### Docker Compose
```bash
docker-compose up -d
```

Access at http://localhost:8501

---

## Cloud Deployment

### Streamlit Cloud
1. Push to GitHub
2. Go to https://streamlit.io/cloud
3. New app → Select repo → Select app_pro.py
4. Deploy

### Heroku
1. Create `Procfile`:
   ```
   web: streamlit run app_pro.py --server.port=$PORT --server.address=0.0.0.0
   ```

2. Deploy:
   ```bash
   git push heroku main
   ```

### AWS EC2
1. Launch Ubuntu instance
2. Install dependencies
3. Clone repo and setup
4. Use systemd or supervisor to manage process
5. Use Nginx as reverse proxy

### Google Cloud Run
```bash
gcloud run deploy resume-screening \
  --source . \
  --platform managed \
  --region us-central1 \
  --port 8501
```

---

## Environment Configuration

1. Copy `.env.example` to `.env`
2. Fill in your values
3. Load in app with `python-dotenv`

---

## Performance Optimization

### Caching
- BERT model cached after first run
- Streamlit @st.cache_resource for heavy operations

### GPU Support
- Set `USE_GPU=True` if available
- Requires CUDA and torch GPU version

### Horizontal Scaling
- Use load balancer (Nginx/HAProxy)
- Run multiple Streamlit instances on different ports
- Share data via centralized storage

---

## Monitoring

### Logs
```bash
# Docker logs
docker logs resume-screening-app

# Streamlit debug
streamlit run app_pro.py --logger.level=debug
```

### Health Check
- Built-in Streamlit health endpoint: /_stcore/health
- Docker health check: curl http://localhost:8501/_stcore/health

---

## Troubleshooting

### Issue: BERT model not found
- Solution: Run `python -m sentence_transformers` to pre-cache
- Or set `SENTENCE_TRANSFORMERS_HOME` env var

### Issue: Out of memory
- Solution: Set batch size smaller
- Or use smaller BERT model

### Issue: Slow processing
- Solution: Enable GPU
- Or pre-process and cache resumes

---

## Security Best Practices

1. Use HTTPS in production
2. Set strong SECRET_KEY
3. Limit upload file size
4. Validate all inputs
5. Use environment variables for secrets
6. Regular dependency updates

---

## Maintenance

### Update Dependencies
```bash
pip install --upgrade -r requirements.txt
```

### Clean Cache
```bash
rm -rf ~/.cache/huggingface/
rm -rf .streamlit/
```

### Backup
```bash
git push origin main
docker tag resume-screening:latest resume-screening:backup-date
```

---

## Support

- GitHub Issues: Report bugs
- Discussions: Ask questions
- Wiki: Documentation
- Email: support@example.com
