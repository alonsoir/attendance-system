import requests
from bs4 import BeautifulSoup
import os
import shutil  # For terminal size detection
from collections import defaultdict  # Organize data
import math  # For scaling

# Constants for terminal characters
BLOCK = '██'  # Full block
MEDIUM_SHADE = '▓▓'  # Medium shade
LIGHT_SHADE = '▒▒'  # Light shade
BLANK = '  '  # Two spaces (empty bar)

def get_terminal_width():
    """Detect the terminal width, default to 80 if detection fails."""
    try:
        terminal_width = shutil.get_terminal_size().columns
        return terminal_width
    except (AttributeError, OSError):  # Handle cases where terminal size can't be determined
        return 80  # Sensible default

def scrape_website(url, access_key):
    """Scrape a website and return paragraph texts."""
    params = {'access_key': access_key, 'url': url}
    try:
        api_result = requests.get('http://api.scrapestack.com/scrape', params)
        api_result.raise_for_status()
        soup = BeautifulSoup(api_result.content, "html.parser")
        paragraphs = [p.get_text() for p in soup.find_all('p')]
        return paragraphs
    except requests.exceptions.RequestException as e:
        print(f"Request Error: {e}")
        return None

def analyze_text(paragraphs):
    """Simple text analysis: paragraph lengths."""
    if not paragraphs:
        return {}

    paragraph_lengths = [len(p) for p in paragraphs]
    return {
        "min": min(paragraph_lengths),
        "max": max(paragraph_lengths),
        "avg": sum(paragraph_lengths) / len(paragraph_lengths) if paragraphs else 0
    }

def scale_value(value, min_val, max_val, max_width):
    """Scale a value to fit within a terminal width."""
    if max_val == min_val:  # Prevent division by zero
        return 0
    return int(max_width * (value - min_val) / (max_val - min_val))

def create_histogram(paragraphs, terminal_width):
    """
    Creates a simplified histogram of paragraph lengths using terminal characters.
    Scales bars based on paragraph lengths relative to the longest paragraph.
    """
    if not paragraphs:
        return "No paragraphs to create histogram."

    paragraph_lengths = [len(p) for p in paragraphs]
    max_length = max(paragraph_lengths)  # Determine maximum length
    num_buckets = 10  # 10 bars
    bucket_size = max_length / num_buckets  # Range of each bucket

    # Group paragraphs into buckets based on their length
    buckets = defaultdict(int)  # Count paragraphs in each bucket
    for length in paragraph_lengths:
        bucket_index = min(int(length / bucket_size), num_buckets - 1)  # Ensure within range
        buckets[bucket_index] += 1

    # Determine the maximum count in any bucket for scaling the bars
    max_count = max(buckets.values()) if buckets else 1  # Avoid division by zero

    # Generate the histogram string
    histogram_lines = []
    for i in range(num_buckets):
        count = buckets[i]
        # Scale the bar length based on the count relative to the maximum count
        scaled_length = scale_value(count, 0, max_count, terminal_width // 2)

        # Create the bar using terminal characters and add labels
        bar = BLOCK * scaled_length  # Use full block character
        histogram_lines.append(f"{i*int(bucket_size):5d}-{((i+1)*int(bucket_size))-1:5d}: {bar}")

    return "\n".join(histogram_lines)

def print_to_terminal(paragraphs, analysis_results, terminal_width):
    """
    Print paragraph summaries and a simplified histogram to the terminal.
    """
    if not paragraphs:
        print("No paragraphs to display.")
        return

    # Print analysis results
    print("\n--- Text Analysis ---")
    if analysis_results:
        print(f"Min length: {analysis_results['min']}")
        print(f"Max length: {analysis_results['max']}")
        print(f"Avg length: {analysis_results['avg']:.2f}")

    # Create and print the histogram
    print("\n--- Paragraph Length Distribution ---")
    histogram = create_histogram(paragraphs, terminal_width)
    print(histogram)

if __name__ == "__main__":
    # Get URL and API key from environment variables
    target_url = os.environ.get("TARGET_URL", "https://scrapestack.com/documentation")
    api_key = os.environ.get("SCRAPESTACK_API_KEY", "YOUR_API_KEY")
    terminal_width = get_terminal_width()

    # Scrape the website
    paragraphs = scrape_website(target_url, api_key)

    if paragraphs:
        analysis_results = analyze_text(paragraphs)  # Analyze the extracted text
        print_to_terminal(paragraphs, analysis_results, terminal_width)  # Print to terminal
    else:
        print("Failed to scrape the website or no paragraphs found.")
