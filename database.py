from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class Feed(Base):
    __tablename__ = 'feeds'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    url = Column(String(500), nullable=False)
    active = Column(Boolean, default=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'url': self.url,
            'active': self.active
        }

class Topic(Base):
    __tablename__ = 'topics'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    keywords = Column(Text, nullable=False)  # Comma-separated
    active = Column(Boolean, default=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'keywords': self.keywords,
            'active': self.active
        }

class Article(Base):
    __tablename__ = 'articles'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(500), nullable=False)
    url = Column(String(1000), unique=True, nullable=False)
    author = Column(String(200))
    content = Column(Text)
    summary = Column(Text)
    topic_scores = Column(Text)  # JSON string
    primary_topic = Column(String(100))
    published_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'url': self.url,
            'author': self.author,
            'content': self.content,
            'summary': self.summary,
            'topic_scores': self.topic_scores,
            'primary_topic': self.primary_topic,
            'published_date': self.published_date,
            'created_at': self.created_at
        }

# Database initialization
engine = create_engine('sqlite:///news_assistant.db', echo=False)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

def get_session():
    return Session()
