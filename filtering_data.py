import re

def filter_text(text):
    # Filter email addresses
    emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)

    # Filter mentions (Twitter-style)
    mentions = re.findall(r'@\w+', text)

    # Filter hashtags
    hashtags = re.findall(r'#\w+', text)

    # Filter links (HTTP/HTTPS)
    links = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)

    # Filter HTML tags
    html_tags = re.findall(r'<[^>]+>', text)


    return {
        'emails': emails,
        'mentions': mentions,
        'hashtags': hashtags,
        'links': links,
        'html_tags': html_tags,
    }

if __name__ == "__main__":
    # Example text with HTML tags
    example_text = """
    For more information, contact <a href="support@example.com">support@example.com</a>.
    Follow us on Twitter: @example_user. Visit our website: https://www.example.com
    Join the conversation with #PythonProgramming.
    Connect with John Doe at john.doe@example.com.
    I love using Python for <b>natural language processing</b> and sentiment analysis!
    """

    # Filter information from the text
    filtered_info = filter_text(example_text)
    print(example_text)
    print()
    # Display the filtered information
    print("Emails:", filtered_info['emails'])
    print("Mentions:", filtered_info['mentions'])
    print("Hashtags:", filtered_info['hashtags'])
    print("Links:", filtered_info['links'])
    print("HTML Tags:", filtered_info['html_tags'])
