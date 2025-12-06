# Quick Start Guide

Get the Daily News AI Assistant running in 5 minutes!

## Prerequisites

- Python 3.10+
- AWS Account with Bedrock access
- AWS credentials (Access Key ID and Secret Access Key)

## Step-by-Step Setup

### 1. Install Dependencies

**Linux/Mac:**
```bash
chmod +x setup.sh
./setup.sh
```

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

### 2. Configure AWS Credentials

Edit the `.env` file:
```bash
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_DEFAULT_REGION=us-east-1
FLASK_SECRET_KEY=your-random-secret-key-here
```

### 3. Enable AWS Bedrock Access

1. Go to [AWS Bedrock Console](https://console.aws.amazon.com/bedrock/)
2. Click "Model access" in the left sidebar
3. Click "Manage model access"
4. Find "Amazon Nova Pro" and enable it
5. Wait for approval (usually instant)

### 4. Initialize Sample Data (Optional)

```bash
python init_sample_data.py
```

This adds sample RSS feeds and topics to get you started.

### 5. Run the Application

```bash
python app.py
```

### 6. Access the Dashboard

Open your browser to: **http://localhost:5000**

### 7. Fetch Your First Articles

1. Click "Refresh News" button on the dashboard
2. Wait for the orange banner ("AI is working for you...")
3. Page will auto-reload when complete
4. View analyzed articles with AI summaries!

## What's Next?

### Add Your Own Feeds
1. Click "RSS Feeds" in sidebar
2. Add any RSS feed URL
3. Toggle feeds on/off as needed

### Customize Topics
1. Click "Topics" in sidebar
2. Add topics with relevant keywords
3. Articles are scored against these topics

### Export Articles
- Click the green PDF button on any article
- Get a formatted PDF with AI summary and full content

### Delete Old Articles
- Click the red X button to remove articles
- Articles older than 24 hours are auto-deleted

## Troubleshooting

### "No module named 'flask'"
```bash
source venv/bin/activate  # Activate virtual environment first
pip install -r requirements.txt
```

### "AWS credentials not found"
- Check your `.env` file exists and has valid credentials
- Verify AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY are set

### "No articles appearing"
- Verify RSS feeds are active (check admin panel)
- Ensure topics are configured
- Check that AWS Bedrock is enabled
- Look at terminal logs for errors

### "Bedrock throttling"
- AWS has rate limits on API calls
- The app automatically retries once
- Wait a few seconds and try again

## Tips for Best Results

1. **Start Small**: Begin with 2-3 RSS feeds and 3-4 topics
2. **Good Keywords**: Use specific, relevant keywords for topics
3. **Monitor Scores**: Check which articles score high to refine topics
4. **Adjust Threshold**: Edit `services.py` to change the 75-point threshold
5. **Check Logs**: Terminal output shows detailed processing information

## Common RSS Feeds

**Technology:**
- TechCrunch: https://techcrunch.com/feed/
- Wired: https://www.wired.com/feed/rss
- Ars Technica: https://feeds.arstechnica.com/arstechnica/index

**News:**
- BBC: http://feeds.bbci.co.uk/news/rss.xml
- Reuters: https://www.reutersagency.com/feed/
- NPR: https://feeds.npr.org/1001/rss.xml

**Tech News:**
- Hacker News: https://hnrss.org/frontpage
- The Verge: https://www.theverge.com/rss/index.xml

## Need Help?

Check the full README.md for detailed documentation and customization options.

Enjoy your AI-powered news assistant! 🚀
