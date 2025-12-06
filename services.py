import json
import time
import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from database import get_session, Feed, Topic, Article
import boto3
from botocore.exceptions import ClientError
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewsService:
    def __init__(self):
        self.session = get_session()
        self.processing = False
        try:
            self.bedrock_client = boto3.client('bedrock-runtime', region_name='us-east-1')
        except Exception as e:
            logger.error(f"Failed to initialize Bedrock client: {e}")
            self.bedrock_client = None
    
    def fetch_and_process_news(self):
        """Main orchestration function for fetching and processing news"""
        if self.processing:
            logger.warning("Processing already in progress")
            return {"status": "already_running"}
        
        self.processing = True
        results = {
            "feeds_processed": 0,
            "articles_found": 0,
            "articles_saved": 0,
            "articles_discarded": 0,
            "errors": []
        }
        
        try:
            # Get active feeds and topics
            feeds = self.session.query(Feed).filter_by(active=True).all()
            topics = self.session.query(Topic).filter_by(active=True).all()
            
            if not topics:
                logger.warning("No active topics found")
                results["errors"].append("No active topics configured")
                return results
            
            topics_list = [topic.name for topic in topics]
            
            # Process each feed
            for feed in feeds:
                try:
                    logger.info(f"Processing feed: {feed.name}")
                    parsed_feed = feedparser.parse(feed.url)
                    results["feeds_processed"] += 1
                    
                    for entry in parsed_feed.entries[:10]:  # Limit to 10 articles per feed
                        try:
                            results["articles_found"] += 1
                            
                            # Check if article already exists
                            article_url = entry.get('link', '')
                            if not article_url:
                                continue
                            
                            existing = self.session.query(Article).filter_by(url=article_url).first()
                            if existing:
                                logger.info(f"Article already exists: {article_url}")
                                continue
                            
                            # Extract article data
                            title = entry.get('title', 'No Title')
                            author = entry.get('author', 'Unknown')
                            published = entry.get('published_parsed', None)
                            published_date = datetime(*published[:6]) if published else datetime.utcnow()
                            
                            # Get content - smart extraction
                            content = self._extract_content(entry, article_url)
                            
                            if not content or len(content) < 100:
                                logger.warning(f"Insufficient content for: {title}")
                                results["articles_discarded"] += 1
                                continue
                            
                            # Truncate to 3000 chars
                            content = content[:3000]
                            
                            # AI Analysis
                            analysis = self.analyze_article(content, topics_list)
                            
                            if not analysis:
                                logger.warning(f"AI analysis failed for: {title}")
                                results["articles_discarded"] += 1
                                continue
                            
                            # Check if any topic score > 75
                            topic_scores = analysis.get('topic_scores', {})
                            max_score = max(topic_scores.values()) if topic_scores else 0
                            
                            if max_score > 75:
                                # Find primary topic
                                primary_topic = max(topic_scores, key=topic_scores.get)
                                
                                # Save article
                                article = Article(
                                    title=title,
                                    url=article_url,
                                    author=author,
                                    content=content,
                                    summary=analysis.get('summary', ''),
                                    topic_scores=json.dumps(topic_scores),
                                    primary_topic=primary_topic,
                                    published_date=published_date
                                )
                                
                                self.session.add(article)
                                self.session.commit()
                                results["articles_saved"] += 1
                                logger.info(f"Saved article: {title} (Score: {max_score})")
                            else:
                                results["articles_discarded"] += 1
                                logger.info(f"Article discarded (max score {max_score}): {title}")
                        
                        except Exception as e:
                            logger.error(f"Error processing article: {e}")
                            results["errors"].append(str(e))
                            continue
                
                except Exception as e:
                    logger.error(f"Error processing feed {feed.name}: {e}")
                    results["errors"].append(f"Feed {feed.name}: {str(e)}")
                    continue
            
            # Cleanup old articles (> 24 hours)
            cutoff_date = datetime.utcnow() - timedelta(hours=24)
            deleted = self.session.query(Article).filter(Article.created_at < cutoff_date).delete()
            self.session.commit()
            logger.info(f"Deleted {deleted} old articles")
            results["articles_deleted"] = deleted
        
        except Exception as e:
            logger.error(f"Fatal error in fetch_and_process_news: {e}")
            results["errors"].append(f"Fatal: {str(e)}")
        
        finally:
            self.processing = False
        
        return results
    
    def _extract_content(self, entry, url):
        """Smart content extraction from RSS or web scraping"""
        # Try RSS description first
        description = entry.get('description', '') or entry.get('summary', '')
        
        # Clean HTML tags from description
        if description:
            soup = BeautifulSoup(description, 'html.parser')
            description = soup.get_text(strip=True)
        
        # If description is too short, scrape the full article
        if len(description) < 500:
            try:
                logger.info(f"Scraping full article from: {url}")
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Remove script and style elements
                for script in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
                    script.decompose()
                
                # Try to find main content
                article_content = None
                for selector in ['article', 'main', '.article-content', '.post-content', '#content']:
                    article_content = soup.select_one(selector)
                    if article_content:
                        break
                
                if not article_content:
                    article_content = soup.find('body')
                
                if article_content:
                    # Get text and clean it
                    text = article_content.get_text(separator=' ', strip=True)
                    # Remove extra whitespace
                    text = re.sub(r'\s+', ' ', text)
                    return text
                
            except Exception as e:
                logger.error(f"Error scraping {url}: {e}")
        
        return description
    
    def analyze_article(self, text, topics_list):
        """Analyze article using AWS Bedrock Amazon Nova Pro"""
        if not self.bedrock_client:
            logger.error("Bedrock client not initialized")
            return None
        
        try:
            # Construct the system prompt
            system_prompt = (
                f"You are a specialized news analyst. Analyze the following article text "
                f"against these topics: {', '.join(topics_list)}. "
                f"Return a strictly formatted JSON object with two keys: "
                f"'summary' (a concise bulleted summary) and 'topic_scores' "
                f"(a key-value pair of Topic Name and a relevance integer 0-100). "
                f"Do not output markdown, just the JSON."
            )
            
            # Amazon Nova Pro payload structure
            payload = {
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "text": f"{system_prompt}\n\nArticle text:\n{text}"
                            }
                        ]
                    }
                ],
                "inferenceConfig": {
                    "max_new_tokens": 1000,
                    "temperature": 0.3,
                    "top_p": 0.9
                }
            }
            
            # Call Bedrock
            response = self.bedrock_client.invoke_model(
                modelId='us.amazon.nova-pro-v1:0',
                body=json.dumps(payload),
                contentType='application/json',
                accept='application/json'
            )
            
            # Parse response
            response_body = json.loads(response['body'].read())
            
            # Extract the generated text
            generated_text = response_body.get('output', {}).get('message', {}).get('content', [{}])[0].get('text', '')
            
            if not generated_text:
                logger.error("No text in Bedrock response")
                return None
            
            # Parse JSON from response
            # Remove markdown code blocks if present
            generated_text = generated_text.strip()
            if generated_text.startswith('```'):
                generated_text = re.sub(r'^```json?\s*', '', generated_text)
                generated_text = re.sub(r'\s*```$', '', generated_text)
            
            analysis = json.loads(generated_text)
            
            # Validate structure
            if 'summary' not in analysis or 'topic_scores' not in analysis:
                logger.error("Invalid analysis structure")
                return None
            
            # Ensure all topics have scores
            for topic in topics_list:
                if topic not in analysis['topic_scores']:
                    analysis['topic_scores'][topic] = 0
            
            return analysis
        
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ThrottlingException':
                logger.warning("Bedrock throttling, waiting 2 seconds...")
                time.sleep(2)
                return self.analyze_article(text, topics_list)  # Retry once
            else:
                logger.error(f"Bedrock ClientError: {e}")
                return None
        
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {e}")
            logger.error(f"Response was: {generated_text[:500]}")
            return None
        
        except Exception as e:
            logger.error(f"Error in analyze_article: {e}")
            return None
    
    def is_processing(self):
        """Check if processing is currently running"""
        return self.processing
