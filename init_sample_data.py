"""
Initialize the database with sample feeds and topics
Run this after first setup to get started quickly
"""
from database import get_session, Feed, Topic

def init_sample_data():
    session = get_session()
    
    # Check if data already exists
    if session.query(Feed).count() > 0 or session.query(Topic).count() > 0:
        print("Database already has data. Skipping initialization.")
        return
    
    print("Initializing sample data...")
    
    # Sample RSS Feeds
    feeds = [
        Feed(name="TechCrunch", url="https://techcrunch.com/feed/", active=True),
        Feed(name="BBC News", url="http://feeds.bbci.co.uk/news/rss.xml", active=True),
        Feed(name="Hacker News", url="https://hnrss.org/frontpage", active=True),
        Feed(name="Reuters Technology", url="https://www.reutersagency.com/feed/?taxonomy=best-topics&post_type=best", active=True),
        Feed(name="Wired", url="https://www.wired.com/feed/rss", active=True),
    ]
    
    # Sample Topics
    topics = [
        Topic(
            name="Technology",
            keywords="AI, artificial intelligence, machine learning, software, hardware, tech, innovation, startup, coding, programming, computer, digital",
            active=True
        ),
        Topic(
            name="Finance",
            keywords="stocks, market, economy, banking, investment, finance, trading, cryptocurrency, bitcoin, money, financial, business",
            active=True
        ),
        Topic(
            name="Politics",
            keywords="government, election, policy, legislation, congress, senate, president, political, vote, democracy, law",
            active=True
        ),
        Topic(
            name="Health",
            keywords="medical, healthcare, disease, treatment, hospital, doctor, medicine, health, wellness, pandemic, vaccine, drug",
            active=True
        ),
        Topic(
            name="Science",
            keywords="research, study, science, scientific, discovery, experiment, laboratory, physics, chemistry, biology, space, astronomy",
            active=True
        ),
        Topic(
            name="Climate",
            keywords="climate, environment, global warming, carbon, emissions, renewable, energy, sustainability, green, pollution, weather",
            active=True
        ),
    ]
    
    # Add to database
    for feed in feeds:
        session.add(feed)
    
    for topic in topics:
        session.add(topic)
    
    session.commit()
    
    print(f"✓ Added {len(feeds)} sample RSS feeds")
    print(f"✓ Added {len(topics)} sample topics")
    print("\nSample data initialized successfully!")
    print("You can now run the application and click 'Refresh News' to start fetching articles.")

if __name__ == "__main__":
    init_sample_data()
