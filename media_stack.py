import http.client
import os
import urllib.parse
import smtplib
import json
import webbrowser  # Import webbrowser module
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import tempfile  # For creating a temporary HTML file

# Step 1: Fetch News Data from MediaStack API
def fetch_news():
    conn = http.client.HTTPConnection('api.mediastack.com')

    params = urllib.parse.urlencode({
        'access_key': 'e0be64430e8f77ff85d08f9c1229c001',
        'categories': 'technology,science',
        'sort': 'published_desc',
        'limit': 5,  # Fetch latest 5 articles
        'sources':'cnn,bbc'
    })

    conn.request('GET', '/v1/news?{}'.format(params))
    res = conn.getresponse()
    data = res.read()

    return json.loads(data.decode('utf-8'))  # Convert JSON response to dictionary

# Step 2: Format News in a Beautiful HTML Template
def format_news():
    news_data = fetch_news()
    news_list = news_data.get("data", [])

    if not news_list:
        return "<h2 style='color: red;'>No latest news found.</h2>"

    email_body = """
    <html>
    <head>
        <style>
            body { font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px; }
            .container { background-color: #ffffff; padding: 20px; border-radius: 8px; }
            h2 { color: #2E86C1; text-align: center; }
            .news-item { border-bottom: 1px solid #ddd; padding: 10px 0; }
            .news-title { font-size: 18px; color: #2E86C1; font-weight: bold; }
            .news-desc { font-size: 14px; color: #333; margin: 5px 0; }
            .news-link { text-decoration: none; color: #E74C3C; font-weight: bold; }
            .footer { margin-top: 20px; font-size: 12px; text-align: center; color: #777; }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>📰 Your Daily Tech & Cyber News Digest</h2>
    """

    for idx, article in enumerate(news_list, start=1):
        title = article.get("title", "No Title")
        description = article.get("description", "No Description")
        url = article.get("url", "#")  # Link to full article

        email_body += f"""
        <div class="news-item">
            <p class="news-title">🔹 {idx}. {title}</p>
            <p class="news-desc">{description}</p>
            <a class="news-link" href="{url}" target="_blank">🔗 Read More</a>
        </div>
        """

    email_body += """
            <div class="footer">
                ✉️ <i>This email was automatically generated using the <b>Mediastack API.<b></i><br>
                📅 Stay informed, stay ahead!
            </div>
        </div>
    </body>
    </html>
    """

    return email_body

# Step 3: Save HTML to a Temporary File and Open in Browser
import tempfile
import os
import webbrowser

def open_in_browser(html_content):
    """Saves the HTML content to a temporary file and opens it in the default web browser."""
    try:
        # Create a temporary file with UTF-8 encoding
        with tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode='w', encoding='utf-8') as temp_file:
            file_path = temp_file.name
            temp_file.write(html_content)  # No need to encode here

        # Open the file in the default web browser
        webbrowser.open('file://' + os.path.abspath(file_path))
    except Exception as e:
        print(f"Error opening in browser: {e}")


if __name__ == "__main__":
    html_body = format_news()
    open_in_browser(html_body)
