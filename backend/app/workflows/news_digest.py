"""
News Digest Workflow - Fetch tech news and send via email
"""
import requests
from datetime import datetime, timedelta
from .base import WorkflowBase
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

class NewsDigestWorkflow(WorkflowBase):
    """
    Fetches top tech news and sends email digest
    """
    
    def __init__(self):
        super().__init__()
        # Using NewsAPI (free tier: 100 requests/day)
        # Get your API key from: https://newsapi.org/
        self.news_api_key = os.environ.get("NEWS_API_KEY")
        print("Loaded NEWS_API_KEY:", self.news_api_key)
        if not self.news_api_key:
            raise ValueError("NEWS_API_KEY not configured")
        self.news_api_url = "https://newsapi.org/v2/top-headlines"
    

    def fetch_news(self, category="technology", country="in", limit=10):

        base_url = "https://newsapi.org/v2/top-headlines"

        params = {
            "category": category,
            "country": country,
            "pageSize": limit,
            "apiKey": self.news_api_key
        }

        response = requests.get(base_url, params=params)
        data = response.json()

        articles = data.get("articles", [])

        # ---------- FALLBACK 1 ----------
        if not articles:
            self.log_info("No articles for IN, trying US")

            params["country"] = "us"
            response = requests.get(base_url, params=params)
            data = response.json()
            articles = data.get("articles", [])

        # ---------- FALLBACK 2 ----------
        if not articles:
            self.log_info("No headlines found, trying global search")

            search_url = "https://newsapi.org/v2/everything"

            params = {
                "q": "technology",
                "sortBy": "publishedAt",
                "pageSize": limit,
                "apiKey": self.news_api_key
            }

            response = requests.get(search_url, params=params)
            data = response.json()
            articles = data.get("articles", [])

        return articles
            
    def format_email_html(self, articles, category='Technology'):
        """
        Format articles into HTML email
        """
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                           color: white; padding: 20px; text-align: center; }}
                .article {{ border-bottom: 1px solid #ddd; padding: 20px; }}
                .article:hover {{ background-color: #f9f9f9; }}
                .title {{ font-size: 18px; font-weight: bold; color: #2563eb; margin-bottom: 10px; }}
                .description {{ color: #666; margin-bottom: 10px; }}
                .meta {{ font-size: 12px; color: #999; }}
                .footer {{ text-align: center; padding: 20px; color: #999; font-size: 12px; }}
                a {{ color: #2563eb; text-decoration: none; }}
                a:hover {{ text-decoration: underline; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📰 {category} News Digest</h1>
                <p>{datetime.now().strftime('%B %d, %Y')}</p>
            </div>
            <div style="padding: 20px; max-width: 800px; margin: 0 auto;">
        """
        
        for idx, article in enumerate(articles, 1):
            title = article.get('title', 'No title')
            description = article.get('description', 'No description available')
            url = article.get('url', '#')
            source = article.get('source', {}).get('name', 'Unknown')
            published = article.get('publishedAt', '')
            
            # Format published date
            if published:
                try:
                    pub_date = datetime.fromisoformat(published.replace('Z', '+00:00'))
                    published = pub_date.strftime('%B %d, %Y at %I:%M %p')
                except:
                    pass
            
            html += f"""
                <div class="article">
                    <div class="title">{idx}. {title}</div>
                    <div class="description">{description}</div>
                    <div class="meta">
                        <strong>Source:</strong> {source} | 
                        <strong>Published:</strong> {published}
                    </div>
                    <a href="{url}" target="_blank">Read More →</a>
                </div>
            """
        
        html += """
            </div>
            <div class="footer">
                <p>Powered by UAOS - Unified AI Automation OS</p>
                <p>This is an automated email. Do not reply.</p>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def send_email(self, to_email, subject, html_content):
        """
        Send email using SMTP
        For development: Using Gmail SMTP (you need App Password)
        """
        try:
            # Email configuration from environment variables
            smtp_host = os.environ.get('SMTP_HOST', 'smtp.gmail.com')
            smtp_port = int(os.environ.get('SMTP_PORT', '587'))
            smtp_user = os.environ.get('SMTP_USER', 'your-email@gmail.com')
            smtp_password = os.environ.get('SMTP_PASSWORD', 'your-app-password')
            from_email = os.environ.get('FROM_EMAIL', smtp_user)
            
            self.log_info(f"Sending email to {to_email}")
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = from_email
            msg['To'] = to_email
            
            # Attach HTML content
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.send_message(msg)
            
            self.log_info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            self.log_error(f"Error sending email: {str(e)}")
            raise
    
    def execute(self, config):
        """
        Execute news digest workflow
        
        Expected config:
        {
            'email': 'user@example.com',
            'category': 'technology',  # optional
            'country': 'us',          # optional
            'limit': 10               # optional
        }
        """
        try:
            import os

            # Ensure email exists
            if 'email' not in config or not config.get('email'):
                config['email'] = os.environ.get("FROM_EMAIL")

            self.validate_config(config, ['email'])

            email = config.get('email') or "your_email@gmail.com"

            # Fix placeholder issue
            if "user_email" in email or "<" in email:
                email = os.environ.get("FROM_EMAIL")
            category = config.get('category', 'technology')
            country = config.get('country', 'us')
            limit = config.get('limit', 10)
            
            # Fetch news
            articles = self.fetch_news(category, country, limit)
            
            if not articles:
                return False, "No news articles found", {}
            
            # Format email
            subject = f"📰 {category.title()} News Digest - {datetime.now().strftime('%B %d, %Y')}"
            html_content = self.format_email_html(articles, category.title())
            
            # Send email
            self.send_email(email, subject, html_content)
            
            return True, f"Successfully sent {len(articles)} news articles to {email}", {
                'articles_count': len(articles),
                'category': category,
                'recipient': email
            }
            
        except Exception as e:
            self.log_error(f"Workflow execution failed: {str(e)}")
            return False, f"Failed: {str(e)}", {}