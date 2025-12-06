# Daily News AI Assistant - Project Overview

## 📋 Project Summary

A production-ready Flask application that intelligently aggregates, analyzes, and curates news articles using AWS Bedrock's Amazon Nova Pro AI model. The system automatically scores articles against user-defined topics and presents only the most relevant content through a professional dashboard interface.

## 🎯 Key Features

### Core Functionality
- **RSS Feed Aggregation**: Collect articles from unlimited RSS sources
- **AI-Powered Analysis**: AWS Bedrock Amazon Nova Pro analyzes each article
- **Smart Content Extraction**: Automatically scrapes full article text when RSS feeds provide insufficient content
- **Topic-Based Scoring**: Articles scored 0-100 against custom topics
- **Intelligent Filtering**: Only saves articles scoring > 75 on any topic
- **Auto-Cleanup**: Removes articles older than 24 hours
- **PDF Export**: Generate professional PDFs with AI summaries

### User Interface
- **Professional Dashboard**: Federal Reserve-inspired design
- **Real-time Processing**: Live status updates during AI analysis
- **Admin Panels**: Easy management of feeds and topics
- **Responsive Design**: Works on desktop and mobile
- **Visual Feedback**: Color-coded badges and progress indicators

## 🏗️ Architecture

### Technology Stack

**Backend**:
- Python 3.10+
- Flask (Web Framework)
- SQLAlchemy (ORM)
- SQLite (Development DB)

**AI/ML**:
- AWS Bedrock Runtime
- Amazon Nova Pro v1:0 Model
- Boto3 (AWS SDK)

**Data Processing**:
- Feedparser (RSS parsing)
- BeautifulSoup4 (Web scraping)
- Requests (HTTP client)

**Document Generation**:
- ReportLab (PDF creation)

**Frontend**:
- HTML5 + CSS3
- Bootstrap 5
- Vanilla JavaScript
- Bootstrap Icons

### System Flow

```
1. User clicks "Refresh News"
   ↓
2. System fetches RSS feeds
   ↓
3. For each article:
   - Check if already exists (by URL)
   - Extract content (RSS or scrape)
   - Truncate to 3000 chars
   - Send to AWS Bedrock
   - Receive AI analysis (summary + scores)
   - If max score > 75: Save to DB
   - Else: Discard
   ↓
4. Cleanup articles > 24 hours old
   ↓
5. Display results on dashboard
```

### Database Schema

**Feeds Table**:
- id (PK)
- name
- url
- active (boolean)

**Topics Table**:
- id (PK)
- name
- keywords (comma-separated)
- active (boolean)

**Articles Table**:
- id (PK)
- title
- url (unique)
- author
- content (full text)
- summary (AI-generated)
- topic_scores (JSON)
- primary_topic
- published_date
- created_at

## 📁 File Structure

```
daily-news-ai-assistant/
├── Core Application
│   ├── app.py                  # Flask routes and application
│   ├── database.py             # SQLAlchemy models
│   ├── services.py             # Business logic & AI integration
│   └── pdf_generator.py        # PDF generation
│
├── Configuration
│   ├── requirements.txt        # Python dependencies
│   ├── .env.example           # Environment template
│   ├── .gitignore             # Git ignore rules
│   └── setup.sh               # Automated setup script
│
├── Templates (Jinja2)
│   ├── base.html              # Base layout
│   ├── dashboard.html         # Main article view
│   ├── admin_feeds.html       # Feed management
│   └── admin_topics.html      # Topic management
│
├── Static Assets
│   ├── README.txt             # Static files guide
│   └── frb_sf_logo.jpg        # Logo (optional)
│
├── Utilities
│   ├── init_sample_data.py    # Sample data loader
│   └── test_setup.py          # Setup validation
│
└── Documentation
    ├── README.md              # Main documentation
    ├── QUICKSTART.md          # Quick start guide
    ├── DEPLOYMENT.md          # Production deployment
    └── PROJECT_OVERVIEW.md    # This file
```

## 🔧 Configuration

### Environment Variables

Required in `.env`:
```
AWS_ACCESS_KEY_ID=xxx
AWS_SECRET_ACCESS_KEY=xxx
AWS_DEFAULT_REGION=us-east-1
FLASK_SECRET_KEY=xxx
FLASK_ENV=development
```

### AWS Requirements

1. **IAM Permissions**:
   - `bedrock:InvokeModel` on Amazon Nova Pro

2. **Model Access**:
   - Enable Amazon Nova Pro in Bedrock console
   - Region: us-east-1

3. **Cost Estimate**:
   - ~$0.001 per article analyzed
   - ~$30/month for 1000 articles/day

## 🚀 Quick Start

```bash
# 1. Setup
./setup.sh

# 2. Configure
cp .env.example .env
# Edit .env with AWS credentials

# 3. Initialize sample data
python init_sample_data.py

# 4. Test setup
python test_setup.py

# 5. Run
python app.py

# 6. Access
# Open http://localhost:5000
```

## 🎨 UI Design

### Color Scheme (Federal Reserve Style)
- **Primary**: Navy Blue (#003366)
- **Background**: Light Grey (#f5f5f5)
- **Accent**: Orange (#ff6b35)
- **Text**: Dark Grey (#666666)

### Key UI Elements
- **Sidebar Navigation**: Fixed left sidebar with logo
- **Dashboard Cards**: Hover effects, shadow elevation
- **Topic Badges**: Color-coded relevance indicators
- **Processing Banner**: Orange alert during AI work
- **Action Buttons**: Green (PDF), Red (Delete), Yellow (Toggle)

## 🔐 Security Considerations

### Current Implementation
- Environment-based configuration
- SQL injection protection (SQLAlchemy ORM)
- HTTPS-ready (requires reverse proxy)

### Production Recommendations
- Add user authentication (Flask-Login)
- Implement CSRF protection (Flask-WTF)
- Enable rate limiting (Flask-Limiter)
- Use HTTPS/SSL certificates
- Implement input validation
- Add API key authentication
- Use AWS IAM roles (not access keys)

## 📊 Performance

### Bottlenecks
1. **AI Analysis**: ~2-5 seconds per article
2. **Web Scraping**: ~1-3 seconds per article
3. **Database**: Minimal (SQLite sufficient for < 10k articles)

### Optimization Strategies
- Parallel processing (threading/multiprocessing)
- Caching AI results for duplicate content
- Database indexing on URL and created_at
- CDN for static assets
- Connection pooling for production DB

### Scalability
- **Current**: ~100 articles/hour
- **With Celery**: ~1000 articles/hour
- **With Lambda**: Unlimited (parallel execution)

## 🧪 Testing

### Manual Testing
```bash
python test_setup.py
```

### Unit Tests (Future Enhancement)
```python
# tests/test_services.py
def test_analyze_article():
    service = NewsService()
    result = service.analyze_article("test content", ["Tech"])
    assert 'summary' in result
    assert 'topic_scores' in result
```

## 🐛 Common Issues & Solutions

### Issue: No articles appearing
**Solution**: 
- Check RSS feeds are valid
- Verify topics are configured
- Lower score threshold (< 75)
- Check AWS credentials

### Issue: AWS throttling
**Solution**:
- Reduce concurrent requests
- Add exponential backoff
- Request limit increase

### Issue: Scraping failures
**Solution**:
- Some sites block scrapers
- Falls back to RSS description
- Add more RSS feeds

### Issue: Slow processing
**Solution**:
- Reduce articles per feed
- Implement caching
- Use background workers

## 🔄 Maintenance

### Daily
- Monitor error logs
- Check processing status
- Verify AWS costs

### Weekly
- Review article quality
- Update RSS feeds
- Refine topic keywords

### Monthly
- Update dependencies
- Security patches
- Database optimization
- Cost analysis

## 📈 Future Enhancements

### Planned Features
- [ ] User authentication system
- [ ] Email notifications for high-scoring articles
- [ ] Article bookmarking/favorites
- [ ] Advanced search and filtering
- [ ] Topic trend analysis
- [ ] Multi-language support
- [ ] Mobile app (React Native)
- [ ] Browser extension
- [ ] Slack/Teams integration
- [ ] Custom AI prompts per topic

### Technical Improvements
- [ ] Migrate to PostgreSQL
- [ ] Implement Celery for background tasks
- [ ] Add Redis caching
- [ ] Comprehensive test suite
- [ ] API endpoints (REST/GraphQL)
- [ ] WebSocket for real-time updates
- [ ] Docker containerization
- [ ] CI/CD pipeline
- [ ] Monitoring dashboard
- [ ] A/B testing framework

## 📚 Learning Resources

### AWS Bedrock
- [Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [Amazon Nova Models](https://aws.amazon.com/bedrock/nova/)
- [Boto3 Bedrock Guide](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-runtime.html)

### Flask
- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Tutorial](https://docs.sqlalchemy.org/en/20/tutorial/)
- [Jinja2 Templates](https://jinja.palletsprojects.com/)

### Web Scraping
- [BeautifulSoup Docs](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [Feedparser Guide](https://feedparser.readthedocs.io/)

## 🤝 Contributing

### Code Style
- PEP 8 for Python
- 4 spaces indentation
- Descriptive variable names
- Comprehensive docstrings

### Git Workflow
```bash
# Create feature branch
git checkout -b feature/new-feature

# Make changes and commit
git add .
git commit -m "Add: new feature description"

# Push and create PR
git push origin feature/new-feature
```

## 📄 License

MIT License - Free to use and modify

## 🆘 Support

### Getting Help
1. Check README.md for basic setup
2. Review QUICKSTART.md for common issues
3. Run test_setup.py for diagnostics
4. Check application logs for errors
5. Review AWS CloudWatch for Bedrock issues

### Contact
- GitHub Issues: [Create an issue]
- Documentation: See README.md
- AWS Support: For Bedrock-specific issues

## 🎓 Credits

Built with:
- Flask by Pallets
- AWS Bedrock by Amazon
- Bootstrap by Twitter
- ReportLab by ReportLab Inc.
- And many other open-source libraries

---

**Version**: 1.0.0  
**Last Updated**: December 2025  
**Status**: Production Ready  
**Maintained**: Yes
