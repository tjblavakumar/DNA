from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file
from database import get_session, Feed, Topic, Article
from services import NewsService
from pdf_generator import generate_pdf
import json
import os
from dotenv import load_dotenv
from threading import Thread
import logging

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global news service instance
news_service = NewsService()

# Background processing
def background_fetch():
    """Run fetch_and_process_news in background"""
    try:
        logger.info("Starting background news fetch")
        results = news_service.fetch_and_process_news()
        logger.info(f"Background fetch completed: {results}")
    except Exception as e:
        logger.error(f"Error in background fetch: {e}")

@app.route('/')
def dashboard():
    """Main dashboard showing articles"""
    session = get_session()
    articles = session.query(Article).order_by(Article.created_at.desc()).all()
    
    # Parse topic scores for display
    articles_data = []
    for article in articles:
        article_dict = article.to_dict()
        try:
            article_dict['topic_scores_parsed'] = json.loads(article.topic_scores)
        except:
            article_dict['topic_scores_parsed'] = {}
        articles_data.append(article_dict)
    
    return render_template('dashboard.html', articles=articles_data)

@app.route('/refresh_news', methods=['POST'])
def refresh_news():
    """Trigger background news processing"""
    if news_service.is_processing():
        return jsonify({"status": "already_running", "message": "Processing already in progress"})
    
    # Start background thread
    thread = Thread(target=background_fetch)
    thread.daemon = True
    thread.start()
    
    return jsonify({"status": "started", "message": "News refresh started"})

@app.route('/status')
def status():
    """Check processing status"""
    is_processing = news_service.is_processing()
    session = get_session()
    article_count = session.query(Article).count()
    
    return jsonify({
        "processing": is_processing,
        "article_count": article_count
    })

@app.route('/download_pdf/<int:article_id>')
def download_pdf(article_id):
    """Generate and download PDF for an article"""
    session = get_session()
    article = session.query(Article).get(article_id)
    
    if not article:
        return "Article not found", 404
    
    try:
        pdf_buffer = generate_pdf(article)
        filename = f"article_{article_id}.pdf"
        
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        logger.error(f"Error generating PDF: {e}")
        return f"Error generating PDF: {str(e)}", 500

@app.route('/delete_article/<int:article_id>', methods=['POST'])
def delete_article(article_id):
    """Delete an article"""
    session = get_session()
    article = session.query(Article).get(article_id)
    
    if article:
        session.delete(article)
        session.commit()
    
    return redirect(url_for('dashboard'))

# Admin Routes - Feeds
@app.route('/admin/feeds')
def admin_feeds():
    """Manage RSS feeds"""
    session = get_session()
    feeds = session.query(Feed).all()
    return render_template('admin_feeds.html', feeds=feeds)

@app.route('/admin/feeds/add', methods=['POST'])
def add_feed():
    """Add a new feed"""
    name = request.form.get('name')
    url = request.form.get('url')
    
    if name and url:
        session = get_session()
        feed = Feed(name=name, url=url, active=True)
        session.add(feed)
        session.commit()
    
    return redirect(url_for('admin_feeds'))

@app.route('/admin/feeds/toggle/<int:feed_id>', methods=['POST'])
def toggle_feed(feed_id):
    """Toggle feed active status"""
    session = get_session()
    feed = session.query(Feed).get(feed_id)
    
    if feed:
        feed.active = not feed.active
        session.commit()
    
    return redirect(url_for('admin_feeds'))

@app.route('/admin/feeds/delete/<int:feed_id>', methods=['POST'])
def delete_feed(feed_id):
    """Delete a feed"""
    session = get_session()
    feed = session.query(Feed).get(feed_id)
    
    if feed:
        session.delete(feed)
        session.commit()
    
    return redirect(url_for('admin_feeds'))

# Admin Routes - Topics
@app.route('/admin/topics')
def admin_topics():
    """Manage topics"""
    session = get_session()
    topics = session.query(Topic).all()
    return render_template('admin_topics.html', topics=topics)

@app.route('/admin/topics/add', methods=['POST'])
def add_topic():
    """Add a new topic"""
    name = request.form.get('name')
    keywords = request.form.get('keywords')
    
    if name and keywords:
        session = get_session()
        topic = Topic(name=name, keywords=keywords, active=True)
        session.add(topic)
        session.commit()
    
    return redirect(url_for('admin_topics'))

@app.route('/admin/topics/toggle/<int:topic_id>', methods=['POST'])
def toggle_topic(topic_id):
    """Toggle topic active status"""
    session = get_session()
    topic = session.query(Topic).get(topic_id)
    
    if topic:
        topic.active = not topic.active
        session.commit()
    
    return redirect(url_for('admin_topics'))

@app.route('/admin/topics/delete/<int:topic_id>', methods=['POST'])
def delete_topic(topic_id):
    """Delete a topic"""
    session = get_session()
    topic = session.query(Topic).get(topic_id)
    
    if topic:
        session.delete(topic)
        session.commit()
    
    return redirect(url_for('admin_topics'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
