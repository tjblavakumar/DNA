# Daily News AI Assistant

A Flask-based news aggregation and analysis application that uses AWS Bedrock (Amazon Nova Pro) to intelligently score and summarize articles based on user-defined topics.

## Features

- **RSS Feed Aggregation**: Collect articles from multiple RSS feeds
- **AI-Powered Analysis**: Uses AWS Bedrock Amazon Nova Pro to analyze and score articles
- **Smart Content Extraction**: Automatically scrapes full article content when RSS feeds provide insufficient text
- **Topic-Based Filtering**: Only saves articles with relevance scores > 75
- **Professional Dashboard**: Clean, Federal Reserve-inspired UI
- **PDF Export**: Generate professional PDFs of articles with AI summaries
- **Auto-Cleanup**: Automatically removes articles older than 24 hours

## Tech Stack

- **Backend**: Python 3.10+, Flask, SQLAlchemy (SQLite)
- **AI/ML**: AWS Bedrock Runtime (Amazon Nova Pro v1:0)
- **Data Processing**: Feedparser, BeautifulSoup4
- **PDF Generation**: ReportLab
- **Frontend**: HTML5, CSS3, Bootstrap 5, JavaScript

## Prerequisites

- Python 3.10 or higher
- AWS Account with Bedrock access
- AWS credentials configured with permissions for `bedrock-runtime:InvokeModel`
- Amazon Nova Pro model access enabled in AWS Bedrock (us-east-1 region)

## Installation

1. **Clone or download this repository**

2. **Create a virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your AWS credentials:
   ```
   AWS_ACCESS_KEY_ID=your_access_key_here
   AWS_SECRET_ACCESS_KEY=your_secret_key_here
   AWS_DEFAULT_REGION=us-east-1
   FLASK_SECRET_KEY=your_random_secret_key
   FLASK_ENV=development
   ```

5. **Initialize the database**:
   The database will be automatically created when you first run the application.

## Usage

1. **Start the application**:
   ```bash
   python app.py
   ```

2. **Access the dashboard**:
   Open your browser and navigate to `http://localhost:5000`

3. **Configure RSS Feeds**:
   - Click "RSS Feeds" in the sidebar
   - Add your desired RSS feed URLs
   - Toggle feeds on/off as needed

4. **Configure Topics**:
   - Click "Topics" in the sidebar
   - Add topics with relevant keywords (comma-separated)
   - Example: Topic "Technology" with keywords "AI, machine learning, software, tech"

5. **Fetch News**:
   - Return to the Dashboard
   - Click "Refresh News" button
   - Wait for the AI to process articles (orange banner will appear)
   - Page will auto-reload when processing is complete

6. **View and Export**:
   - Browse analyzed articles on the dashboard
   - Click the PDF button to download a formatted report
   - Click the X button to delete articles

## How It Works

1. **Fetching**: The app fetches articles from active RSS feeds
2. **Content Extraction**: If RSS description is < 500 chars, it scrapes the full article
3. **AI Analysis**: Each article is sent to AWS Bedrock Amazon Nova Pro for analysis
4. **Scoring**: The AI returns topic relevance scores (0-100) and a summary
5. **Filtering**: Only articles with ANY topic score > 75 are saved
6. **Cleanup**: Articles older than 24 hours are automatically deleted

## Project Structure

```
daily-news-ai-assistant/
├── app.py                  # Flask application and routes
├── database.py             # SQLAlchemy models and database setup
├── services.py             # Core business logic and AI integration
├── pdf_generator.py        # PDF generation functionality
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── templates/             # HTML templates
│   ├── base.html
│   ├── dashboard.html
│   ├── admin_feeds.html
│   └── admin_topics.html
├── static/                # Static files (CSS, JS, images)
│   └── frb_sf_logo.jpg   # Optional logo
└── news_assistant.db      # SQLite database (auto-created)
```

## AWS Bedrock Configuration

This application uses the **Amazon Nova Pro** model (`us.amazon.nova-pro-v1:0`) in the `us-east-1` region.

### Required AWS Permissions

Your AWS IAM user/role needs:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel"
      ],
      "Resource": "arn:aws:bedrock:us-east-1::foundation-model/us.amazon.nova-pro-v1:0"
    }
  ]
}
```

### Enable Model Access

1. Go to AWS Bedrock console
2. Navigate to "Model access"
3. Request access to "Amazon Nova Pro"
4. Wait for approval (usually instant)

## Troubleshooting

### AWS Credentials Error
- Ensure your `.env` file has valid AWS credentials
- Verify your IAM user has Bedrock permissions
- Check that Amazon Nova Pro is enabled in your AWS account

### No Articles Appearing
- Verify RSS feeds are active and valid
- Check that topics are configured with relevant keywords
- Ensure at least one topic score is > 75 (lower the threshold in `services.py` if needed)
- Check application logs for errors

### Scraping Failures
- Some websites block automated scraping
- The app will fall back to RSS description if scraping fails
- Consider adding more RSS feeds with full content

## Customization

### Change Score Threshold
Edit `services.py`, line ~120:
```python
if max_score > 75:  # Change this value
```

### Change Article Retention Period
Edit `services.py`, line ~140:
```python
cutoff_date = datetime.utcnow() - timedelta(hours=24)  # Change hours
```

### Modify UI Colors
Edit `templates/base.html` CSS variables:
```css
:root {
    --navy-blue: #003366;
    --accent-orange: #ff6b35;
}
```

## License

MIT License - Feel free to use and modify as needed.

## Support

For issues related to:
- **AWS Bedrock**: Check AWS documentation and service status
- **Application bugs**: Review logs and error messages
- **Feature requests**: Modify the code to suit your needs

## Notes

- The application uses SQLite for simplicity. For production, consider PostgreSQL or MySQL.
- Background processing runs in a thread. For production, use Celery or similar task queue.
- The AI analysis can be slow for many articles. Be patient during the first refresh.
- AWS Bedrock charges apply based on token usage. Monitor your AWS costs.
