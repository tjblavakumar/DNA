# Troubleshooting Guide

Common issues and their solutions for the Daily News AI Assistant.

## 🔍 Diagnostic Tools

### 1. Run Setup Test
```bash
python test_setup.py
```
This checks Python version, dependencies, environment config, AWS connection, database, and file structure.

### 2. Check Application Logs
Look at the terminal output when running `python app.py` for detailed error messages.

### 3. Check AWS CloudWatch
If using AWS, check CloudWatch logs for Bedrock API errors.

---

## ❌ Installation Issues

### Error: "No module named 'flask'"

**Cause**: Dependencies not installed or virtual environment not activated

**Solution**:
```bash
# Activate virtual environment
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### Error: "Python version too old"

**Cause**: Python < 3.10

**Solution**:
```bash
# Check version
python3 --version

# Install Python 3.10+ (Ubuntu/Debian)
sudo apt update
sudo apt install python3.10

# Or use pyenv
pyenv install 3.10.12
pyenv local 3.10.12
```

### Error: "Permission denied: setup.sh"

**Cause**: Script not executable

**Solution**:
```bash
chmod +x setup.sh
./setup.sh
```

---

## 🔐 AWS & Authentication Issues

### Error: "NoCredentialsError"

**Cause**: AWS credentials not configured

**Solution**:
```bash
# Check .env file exists
ls -la .env

# Verify contents
cat .env

# Should contain:
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_DEFAULT_REGION=us-east-1
```

### Error: "AccessDeniedException" from Bedrock

**Cause**: Model access not enabled or insufficient IAM permissions

**Solution**:

1. **Enable Model Access**:
   - Go to [AWS Bedrock Console](https://console.aws.amazon.com/bedrock/)
   - Click "Model access" in sidebar
   - Click "Manage model access"
   - Find "Amazon Nova Pro" and enable it
   - Wait for approval (usually instant)

2. **Check IAM Permissions**:
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Action": "bedrock:InvokeModel",
         "Resource": "arn:aws:bedrock:us-east-1::foundation-model/us.amazon.nova-pro-v1:0"
       }
     ]
   }
   ```

### Error: "ThrottlingException"

**Cause**: Too many requests to AWS Bedrock

**Solution**:
- The app automatically retries once
- Wait a few seconds and try again
- Reduce number of RSS feeds
- Process fewer articles at once
- Request limit increase from AWS Support

### Error: "ValidationException: Invalid model ID"

**Cause**: Model ID incorrect or not available in region

**Solution**:
```python
# In services.py, verify:
modelId='us.amazon.nova-pro-v1:0'
region_name='us-east-1'

# Amazon Nova Pro is only available in us-east-1
```

---

## 📰 Article Processing Issues

### Issue: No articles appearing after refresh

**Possible Causes & Solutions**:

1. **No active feeds**:
   ```bash
   # Check feeds in admin panel
   # Or query database:
   python3 -c "from database import *; s=get_session(); print(s.query(Feed).filter_by(active=True).count())"
   ```

2. **No active topics**:
   ```bash
   # Check topics in admin panel
   # Or query database:
   python3 -c "from database import *; s=get_session(); print(s.query(Topic).filter_by(active=True).count())"
   ```

3. **Score threshold too high**:
   - Edit `services.py` line ~120
   - Change `if max_score > 75:` to `if max_score > 50:`
   - Restart application

4. **RSS feeds invalid**:
   - Test feed URLs in browser
   - Check for valid RSS/XML format
   - Try different feeds

5. **Articles already exist**:
   - App skips duplicate URLs
   - Try different RSS feeds
   - Clear database: `rm news_assistant.db` and restart

### Issue: Processing takes forever

**Causes & Solutions**:

1. **Too many articles**:
   - Reduce feeds
   - Limit articles per feed (edit `services.py` line ~95)

2. **Slow scraping**:
   - Some websites are slow to respond
   - Check terminal logs for timeout errors
   - Consider removing problematic feeds

3. **AWS Bedrock latency**:
   - Normal: 2-5 seconds per article
   - Check AWS service status
   - Verify region is us-east-1

### Issue: Scraping fails for certain sites

**Cause**: Website blocks automated access or has complex structure

**Solution**:
- App falls back to RSS description
- This is expected behavior
- Use RSS feeds with full content
- Or manually add article content

### Issue: AI summaries are poor quality

**Causes & Solutions**:

1. **Insufficient content**:
   - Ensure articles have > 500 chars
   - Check scraping is working

2. **Adjust AI parameters**:
   ```python
   # In services.py, modify inferenceConfig:
   "inferenceConfig": {
       "max_new_tokens": 1500,  # Increase for longer summaries
       "temperature": 0.5,      # Increase for more creative
       "top_p": 0.9
   }
   ```

3. **Improve system prompt**:
   - Edit prompt in `services.py` line ~165
   - Be more specific about desired output

---

## 💾 Database Issues

### Error: "database is locked"

**Cause**: SQLite doesn't handle concurrent writes well

**Solution**:
```python
# Short term: Restart application
# Long term: Migrate to PostgreSQL (see DEPLOYMENT.md)
```

### Issue: Database corruption

**Solution**:
```bash
# Backup current database
cp news_assistant.db news_assistant.db.backup

# Delete and recreate
rm news_assistant.db
python app.py  # Will recreate automatically

# Reinitialize sample data
python init_sample_data.py
```

### Issue: Old articles not being deleted

**Check**:
```python
# Verify cleanup is running
# Check services.py line ~140
cutoff_date = datetime.utcnow() - timedelta(hours=24)
```

**Solution**:
- Cleanup runs during each refresh
- Manually delete: Click X button on articles
- Or clear database: `rm news_assistant.db`

---

## 🌐 Web Interface Issues

### Error: "Address already in use"

**Cause**: Port 5000 is occupied

**Solution**:
```bash
# Find process using port 5000
lsof -i :5000  # Mac/Linux
netstat -ano | findstr :5000  # Windows

# Kill the process
kill -9 <PID>  # Mac/Linux
taskkill /PID <PID> /F  # Windows

# Or use different port
# In app.py, change:
app.run(debug=True, host='0.0.0.0', port=5001)
```

### Issue: Page not loading / 404 errors

**Solution**:
```bash
# Verify app is running
# Check terminal for errors
# Ensure you're accessing http://localhost:5000 (not https)
# Clear browser cache
# Try different browser
```

### Issue: "Refresh News" button does nothing

**Check**:
1. Open browser console (F12)
2. Look for JavaScript errors
3. Check network tab for failed requests

**Solution**:
```bash
# Verify /refresh_news endpoint works:
curl -X POST http://localhost:5000/refresh_news

# Should return: {"status": "started", ...}
```

### Issue: Processing banner never disappears

**Cause**: Status polling not working

**Solution**:
1. Check browser console for errors
2. Verify `/status` endpoint works:
   ```bash
   curl http://localhost:5000/status
   ```
3. Manually reload page after a few minutes

---

## 📄 PDF Generation Issues

### Error: "ReportLab not found"

**Solution**:
```bash
pip install reportlab
```

### Issue: PDF download fails

**Check**:
```bash
# Verify article exists
# Check terminal logs for errors
# Ensure write permissions in directory
```

### Issue: PDF formatting issues

**Solution**:
- Edit `pdf_generator.py`
- Adjust styles, fonts, or layout
- Test with different articles

---

## 🔧 Performance Issues

### Issue: High memory usage

**Causes & Solutions**:

1. **Too many articles in database**:
   ```bash
   # Check count
   python3 -c "from database import *; s=get_session(); print(s.query(Article).count())"
   
   # Delete old articles
   # Reduce retention period in services.py
   ```

2. **Memory leak**:
   - Restart application
   - Monitor with `top` or `htop`

### Issue: Slow dashboard loading

**Solutions**:
1. Limit articles displayed
2. Add pagination
3. Implement caching
4. Optimize database queries

---

## 🐛 Development Issues

### Issue: Changes not reflecting

**Solution**:
```bash
# Ensure debug mode is on (app.py):
app.run(debug=True)

# Or manually restart:
# Ctrl+C to stop
python app.py  # Start again

# Clear browser cache
# Hard refresh: Ctrl+Shift+R (or Cmd+Shift+R on Mac)
```

### Issue: Template not found

**Check**:
```bash
# Verify templates directory structure
ls -la templates/

# Should contain:
# base.html
# dashboard.html
# admin_feeds.html
# admin_topics.html
```

### Issue: Static files not loading

**Check**:
```bash
# Verify static directory exists
ls -la static/

# Check Flask is serving static files
# Access: http://localhost:5000/static/README.txt
```

---

## 🔍 Debugging Tips

### Enable Verbose Logging

```python
# In services.py, change:
logging.basicConfig(level=logging.DEBUG)

# In database.py, change:
engine = create_engine('sqlite:///news_assistant.db', echo=True)
```

### Test Individual Components

```python
# Test database
python3 -c "from database import *; print(get_session().query(Feed).all())"

# Test AWS connection
python3 -c "import boto3; print(boto3.client('bedrock-runtime', region_name='us-east-1'))"

# Test RSS parsing
python3 -c "import feedparser; print(feedparser.parse('https://techcrunch.com/feed/'))"
```

### Check System Resources

```bash
# Memory usage
free -h

# Disk space
df -h

# CPU usage
top

# Network connectivity
ping aws.amazon.com
```

---

## 📞 Getting Help

### Before Asking for Help

1. Run `python test_setup.py`
2. Check application logs
3. Search this troubleshooting guide
4. Review README.md and QUICKSTART.md
5. Check AWS service status

### Information to Provide

When reporting issues, include:
- Python version: `python3 --version`
- OS: `uname -a` (Linux/Mac) or `ver` (Windows)
- Error messages (full stack trace)
- Steps to reproduce
- Output of `python test_setup.py`
- Relevant logs from terminal

### Resources

- **AWS Bedrock Status**: https://status.aws.amazon.com/
- **Flask Documentation**: https://flask.palletsprojects.com/
- **Python Documentation**: https://docs.python.org/3/

---

## ✅ Prevention Tips

### Regular Maintenance

```bash
# Weekly: Update dependencies
pip install --upgrade -r requirements.txt

# Monthly: Clean database
# Delete old articles manually or reduce retention period

# Monitor AWS costs
# Check AWS Billing Dashboard regularly
```

### Best Practices

1. **Always use virtual environment**
2. **Keep .env file secure** (never commit to git)
3. **Monitor AWS costs** (set billing alerts)
4. **Regular backups** of database
5. **Test changes** before deploying
6. **Keep dependencies updated**
7. **Monitor logs** for errors
8. **Use version control** (git)

---

## 🎯 Quick Fixes Checklist

When something goes wrong, try these in order:

- [ ] Restart the application
- [ ] Check .env file has correct AWS credentials
- [ ] Verify internet connection
- [ ] Run `python test_setup.py`
- [ ] Check AWS Bedrock console for model access
- [ ] Clear browser cache
- [ ] Check terminal logs for errors
- [ ] Verify RSS feeds are valid
- [ ] Ensure topics are configured
- [ ] Try with sample data: `python init_sample_data.py`
- [ ] Delete and recreate database: `rm news_assistant.db`
- [ ] Reinstall dependencies: `pip install -r requirements.txt`
- [ ] Check AWS service status
- [ ] Review this troubleshooting guide

---

Still having issues? Review the full documentation in README.md or check the PROJECT_OVERVIEW.md for architectural details.
