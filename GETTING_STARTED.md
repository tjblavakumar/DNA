# Getting Started with Daily News AI Assistant

Welcome! This guide will walk you through setting up and running your AI-powered news assistant in under 10 minutes.

## 📋 Prerequisites Checklist

Before you begin, ensure you have:

- [ ] **Python 3.10 or higher** installed
  - Check: `python3 --version`
  - If not installed: [Download Python](https://www.python.org/downloads/)

- [ ] **AWS Account** with Bedrock access
  - Sign up: [AWS Console](https://aws.amazon.com/)
  - Free tier available

- [ ] **AWS Access Keys** (Access Key ID + Secret Access Key)
  - Create in: AWS Console → IAM → Users → Security Credentials

- [ ] **Internet connection** for downloading dependencies and fetching news

## 🚀 Installation Steps

### Step 1: Download the Project

```bash
# If you have git
git clone <repository-url>
cd daily-news-ai-assistant

# Or download and extract the ZIP file
```

### Step 2: Run Automated Setup

**On Linux/Mac:**
```bash
chmod +x setup.sh
./setup.sh
```

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

This will:
- Create a virtual environment
- Install all dependencies
- Create a `.env` configuration file

### Step 3: Configure AWS Credentials

Edit the `.env` file with your AWS credentials:

```bash
# Linux/Mac
nano .env

# Windows
notepad .env
```

Replace the placeholder values:
```env
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE          # Your actual key
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG... # Your actual secret
AWS_DEFAULT_REGION=us-east-1                    # Keep as is
FLASK_SECRET_KEY=change-this-to-random-string   # Any random string
FLASK_ENV=development                           # Keep as is
```

**Important**: Never share or commit your `.env` file!

### Step 4: Enable AWS Bedrock Access

1. Go to [AWS Bedrock Console](https://console.aws.amazon.com/bedrock/)
2. Click **"Model access"** in the left sidebar
3. Click **"Manage model access"** button
4. Find **"Amazon Nova Pro"** in the list
5. Check the box next to it
6. Click **"Request model access"**
7. Wait for approval (usually instant)

### Step 5: Verify Setup

Run the test script to ensure everything is configured correctly:

```bash
python test_setup.py
```

You should see all checks pass with ✓ marks. If any fail, see the error messages and fix them.

### Step 6: Initialize Sample Data (Optional but Recommended)

Load sample RSS feeds and topics to get started quickly:

```bash
python init_sample_data.py
```

This adds:
- 5 popular RSS feeds (TechCrunch, BBC, Hacker News, etc.)
- 6 topic categories (Technology, Finance, Politics, Health, Science, Climate)

### Step 7: Start the Application

```bash
python app.py
```

You should see:
```
 * Running on http://0.0.0.0:5000
 * Debug mode: on
```

### Step 8: Access the Dashboard

Open your web browser and go to:
```
http://localhost:5000
```

You should see the Daily News AI Assistant dashboard!

## 🎯 First Use

### 1. Review Your Feeds

Click **"RSS Feeds"** in the sidebar to see your configured feeds.

**To add a new feed:**
1. Enter a name (e.g., "TechCrunch")
2. Enter the RSS URL (e.g., "https://techcrunch.com/feed/")
3. Click "Add Feed"

**Popular RSS Feeds:**
- TechCrunch: `https://techcrunch.com/feed/`
- BBC News: `http://feeds.bbci.co.uk/news/rss.xml`
- Hacker News: `https://hnrss.org/frontpage`
- Wired: `https://www.wired.com/feed/rss`
- Reuters: `https://www.reutersagency.com/feed/`

### 2. Configure Your Topics

Click **"Topics"** in the sidebar to see your topics.

**To add a new topic:**
1. Enter a topic name (e.g., "Artificial Intelligence")
2. Enter keywords separated by commas (e.g., "AI, machine learning, neural networks, deep learning")
3. Click "Add Topic"

**Tips for good keywords:**
- Be specific and relevant
- Include variations and synonyms
- Use 5-10 keywords per topic
- Include both technical and common terms

**Example Topics:**
- **Technology**: AI, software, hardware, tech, innovation, startup, coding
- **Finance**: stocks, market, economy, banking, investment, cryptocurrency
- **Health**: medical, healthcare, disease, treatment, wellness, vaccine
- **Climate**: environment, global warming, carbon, renewable energy

### 3. Fetch Your First Articles

1. Go back to **"Dashboard"**
2. Click the **"Refresh News"** button
3. Wait for the orange banner: "Please wait. AI is working for you..."
4. The page will automatically reload when processing is complete

**What happens:**
- Fetches articles from all active RSS feeds
- Extracts full article content (scrapes if needed)
- Sends each article to AWS Bedrock for AI analysis
- Scores articles against your topics (0-100)
- Saves only articles scoring > 75 on any topic
- Generates AI summaries

**First run may take 2-5 minutes** depending on number of feeds and articles.

### 4. Explore Your Articles

Once processing completes, you'll see article cards with:
- **Title** (clickable to read full article)
- **Primary Topic Badge** (highest scoring topic)
- **Author** and **Date**
- **AI-Generated Summary**
- **Topic Scores** (for all topics > 50)
- **Action Buttons**:
  - 🟢 **PDF**: Download formatted PDF report
  - 🔴 **X**: Delete article

### 5. Export to PDF

Click the green **PDF** button on any article to download a professional report including:
- Article title and metadata
- Topic relevance scores (table)
- AI-generated summary
- Full article content

Perfect for archiving or sharing!

## 🔄 Regular Usage

### Daily Workflow

1. **Morning**: Click "Refresh News" to get latest articles
2. **Review**: Browse AI-curated articles on dashboard
3. **Export**: Download PDFs of important articles
4. **Cleanup**: Delete articles you're not interested in

### Automatic Cleanup

Articles older than 24 hours are automatically deleted during each refresh. You can change this in `services.py`:

```python
# Line ~140
cutoff_date = datetime.utcnow() - timedelta(hours=24)  # Change hours
```

### Customization

**Adjust Score Threshold:**
If you're getting too few articles, lower the threshold:
```python
# In services.py, line ~120
if max_score > 75:  # Change to 60 or 50
```

**Change Refresh Frequency:**
The dashboard can auto-refresh every 10 seconds. Uncomment in `templates/dashboard.html`:
```javascript
// Line ~100
setInterval(() => location.reload(), 10000);
```

## 📊 Understanding the System

### How Articles Are Scored

1. **Content Extraction**: Full article text is extracted (up to 3000 chars)
2. **AI Analysis**: AWS Bedrock analyzes the content
3. **Topic Matching**: AI scores relevance to each topic (0-100)
4. **Filtering**: Only articles with ANY score > 75 are saved
5. **Primary Topic**: The highest-scoring topic becomes the primary topic

### What Makes a Good Score?

- **90-100**: Highly relevant, main focus of article
- **75-89**: Relevant, significant coverage
- **50-74**: Mentioned, but not main focus (not saved by default)
- **0-49**: Barely mentioned or not relevant

### Cost Considerations

**AWS Bedrock Pricing:**
- Amazon Nova Pro: ~$0.001 per article analyzed
- 100 articles/day = ~$3/month
- 1000 articles/day = ~$30/month

**Monitor your costs:**
- AWS Console → Billing Dashboard
- Set up billing alerts
- Review monthly usage

## 🛠️ Troubleshooting

### No Articles Appearing?

**Check:**
1. Are feeds active? (RSS Feeds page)
2. Are topics configured? (Topics page)
3. Are RSS feeds valid? (test URLs in browser)
4. Check terminal logs for errors

**Try:**
- Lower score threshold (edit `services.py`)
- Add more RSS feeds
- Refine topic keywords
- Run `python test_setup.py`

### Processing Takes Forever?

**Normal:**
- 2-5 seconds per article
- 10-20 articles = 1-2 minutes

**Too slow?**
- Reduce number of feeds
- Limit articles per feed
- Check internet connection
- Verify AWS region is us-east-1

### AWS Errors?

**Common issues:**
1. **NoCredentialsError**: Check `.env` file
2. **AccessDeniedException**: Enable model in Bedrock console
3. **ThrottlingException**: Wait and retry, or reduce feeds

**Solution:**
Run `python test_setup.py` to diagnose AWS issues.

### More Help?

See detailed troubleshooting in:
- `TROUBLESHOOTING.md` - Comprehensive error solutions
- `README.md` - Full documentation
- `QUICKSTART.md` - Quick reference guide

## 📚 Next Steps

### Learn More

- **README.md**: Complete documentation
- **PROJECT_OVERVIEW.md**: Architecture and design
- **DEPLOYMENT.md**: Production deployment guide
- **TROUBLESHOOTING.md**: Common issues and solutions

### Customize

- Add your favorite RSS feeds
- Create custom topics for your interests
- Adjust AI parameters in `services.py`
- Modify UI colors in `templates/base.html`
- Change retention period for articles

### Extend

- Add user authentication
- Implement email notifications
- Create API endpoints
- Add search functionality
- Build mobile app
- Integrate with Slack/Teams

## ✅ Success Checklist

You're all set when you can:

- [ ] Access dashboard at http://localhost:5000
- [ ] See RSS feeds in admin panel
- [ ] See topics in admin panel
- [ ] Click "Refresh News" without errors
- [ ] See articles appear on dashboard
- [ ] View AI summaries and topic scores
- [ ] Download PDF reports
- [ ] Delete articles

## 🎉 Congratulations!

You now have a fully functional AI-powered news assistant!

**What you've built:**
- Automated news aggregation from multiple sources
- AI-powered content analysis and scoring
- Intelligent filtering based on your interests
- Professional dashboard for browsing articles
- PDF export for archiving

**Enjoy your personalized news experience!** 🚀

---

**Need help?** Check `TROUBLESHOOTING.md` or run `python test_setup.py`

**Want to learn more?** Read `README.md` and `PROJECT_OVERVIEW.md`

**Ready for production?** See `DEPLOYMENT.md`
