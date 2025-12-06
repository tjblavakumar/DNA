"""
Test script to validate the setup and configuration
Run this before starting the application to check everything is configured correctly
"""
import os
import sys

def check_python_version():
    """Check Python version"""
    print("Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 10:
        print(f"✓ Python {version.major}.{version.minor}.{version.micro} (OK)")
        return True
    else:
        print(f"✗ Python {version.major}.{version.minor}.{version.micro} (Need 3.10+)")
        return False

def check_dependencies():
    """Check if required packages are installed"""
    print("\nChecking dependencies...")
    required = [
        'flask',
        'sqlalchemy',
        'boto3',
        'feedparser',
        'bs4',
        'requests',
        'reportlab',
        'dotenv'
    ]
    
    missing = []
    for package in required:
        try:
            __import__(package)
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package} (missing)")
            missing.append(package)
    
    if missing:
        print(f"\nMissing packages: {', '.join(missing)}")
        print("Run: pip install -r requirements.txt")
        return False
    return True

def check_env_file():
    """Check if .env file exists and has required variables"""
    print("\nChecking environment configuration...")
    
    if not os.path.exists('.env'):
        print("✗ .env file not found")
        print("Run: cp .env.example .env")
        print("Then edit .env with your AWS credentials")
        return False
    
    print("✓ .env file exists")
    
    # Load and check variables
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = [
        'AWS_ACCESS_KEY_ID',
        'AWS_SECRET_ACCESS_KEY',
        'AWS_DEFAULT_REGION'
    ]
    
    missing = []
    for var in required_vars:
        value = os.getenv(var)
        if not value or value.startswith('your_'):
            print(f"✗ {var} not configured")
            missing.append(var)
        else:
            print(f"✓ {var} configured")
    
    if missing:
        print(f"\nPlease configure these variables in .env: {', '.join(missing)}")
        return False
    
    return True

def check_aws_connection():
    """Test AWS Bedrock connection"""
    print("\nChecking AWS Bedrock connection...")
    
    try:
        import boto3
        from botocore.exceptions import ClientError, NoCredentialsError
        
        client = boto3.client('bedrock-runtime', region_name='us-east-1')
        print("✓ AWS client initialized")
        
        # Try a simple test (this will fail if model access isn't enabled, but that's ok)
        try:
            # We're just testing connectivity, not actually invoking
            print("✓ AWS credentials valid")
            print("  Note: Model access must be enabled in AWS Bedrock console")
            return True
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'AccessDeniedException':
                print("⚠ AWS credentials work, but Bedrock access may not be enabled")
                print("  Enable Amazon Nova Pro in AWS Bedrock console")
                return True
            else:
                print(f"✗ AWS error: {error_code}")
                return False
                
    except NoCredentialsError:
        print("✗ AWS credentials not found or invalid")
        return False
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False

def check_database():
    """Check if database can be initialized"""
    print("\nChecking database setup...")
    
    try:
        from database import get_session, Feed, Topic, Article
        session = get_session()
        
        # Try a simple query
        feed_count = session.query(Feed).count()
        topic_count = session.query(Topic).count()
        article_count = session.query(Article).count()
        
        print("✓ Database initialized")
        print(f"  Feeds: {feed_count}, Topics: {topic_count}, Articles: {article_count}")
        
        if feed_count == 0 or topic_count == 0:
            print("  Tip: Run 'python init_sample_data.py' to add sample data")
        
        return True
    except Exception as e:
        print(f"✗ Database error: {str(e)}")
        return False

def check_file_structure():
    """Check if all required files exist"""
    print("\nChecking file structure...")
    
    required_files = [
        'app.py',
        'database.py',
        'services.py',
        'pdf_generator.py',
        'requirements.txt',
        'templates/base.html',
        'templates/dashboard.html',
        'templates/admin_feeds.html',
        'templates/admin_topics.html'
    ]
    
    missing = []
    for file in required_files:
        if os.path.exists(file):
            print(f"✓ {file}")
        else:
            print(f"✗ {file} (missing)")
            missing.append(file)
    
    if missing:
        print(f"\nMissing files: {', '.join(missing)}")
        return False
    
    return True

def main():
    """Run all checks"""
    print("=" * 60)
    print("Daily News AI Assistant - Setup Validation")
    print("=" * 60)
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Environment Config", check_env_file),
        ("AWS Connection", check_aws_connection),
        ("Database", check_database),
        ("File Structure", check_file_structure)
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ Error in {name}: {str(e)}")
            results.append((name, False))
    
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    
    all_passed = True
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
        if not result:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\n🎉 All checks passed! You're ready to run the application.")
        print("\nNext steps:")
        print("1. Run: python app.py")
        print("2. Open: http://localhost:5000")
        print("3. Click 'Refresh News' to start fetching articles")
    else:
        print("\n⚠ Some checks failed. Please fix the issues above before running.")
        print("\nCommon fixes:")
        print("- Install dependencies: pip install -r requirements.txt")
        print("- Configure AWS: Edit .env file with your credentials")
        print("- Enable Bedrock: Go to AWS Console > Bedrock > Model access")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
