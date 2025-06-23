#!/usr/bin/env python3
"""
Pashto Data Gathering Script

This script gathers high-quality Pashto text data from various internet sources,
cleans and normalizes it, and stores it in a structured format ready for model fine-tuning.
"""

import requests
import pandas as pd
import numpy as np
import re
import os
import time
import random
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urlparse
from tqdm import tqdm
import argparse
import logging
import concurrent.futures
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data_gathering.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load stopwords for text cleaning
def load_stopwords():
    try:
        stopwords = pd.read_csv('/workspaces/pashto-text-dataset/ZamAI_Pashto_Datasets/stopwords.csv', header=None)[0].tolist()
        return set(stopwords)
    except FileNotFoundError:
        logger.warning("Stopwords file not found. Running create_stopwords.py...")
        # If the stopwords file doesn't exist, run the script to create it
        import subprocess
        subprocess.run(['python', '/workspaces/pashto-text-dataset/ZamAI_Pashto_Datasets/scripts/create_stopwords.py'])
        # Try loading again
        try:
            stopwords = pd.read_csv('/workspaces/pashto-text-dataset/ZamAI_Pashto_Datasets/stopwords.csv', header=None)[0].tolist()
            return set(stopwords)
        except Exception as e:
            logger.error(f"Failed to load stopwords: {e}")
            # Return a minimal set if everything fails
            return set(['د', 'په', 'او', 'چې', 'له', 'نه'])

# Define a list of reliable Pashto news and content sources
DEFAULT_SOURCES = [
    # News websites
    {
        "name": "BBC Pashto",
        "url": "https://www.bbc.com/pashto",
        "article_pattern": "a.gs-c-promo-heading",
        "title_selector": "h1",
        "content_selector": ".bbc-19j92fr"
    },
    {
        "name": "VOA Pashto",
        "url": "https://www.pashtovoa.com/",
        "article_pattern": "div.media-block a",
        "title_selector": "h1.title",
        "content_selector": ".wsw"
    },
    {
        "name": "Azadi Radio",
        "url": "https://pa.azadiradio.com/",
        "article_pattern": "a.img-wrap",
        "title_selector": "h1",
        "content_selector": ".wsw"
    },
    {
        "name": "Tolonews",
        "url": "https://tolonews.com/ps",
        "article_pattern": "h4.title a",
        "title_selector": ".article-details h1",
        "content_selector": ".article-body"
    },
    {
        "name": "Pajhwok",
        "url": "https://www.pajhwok.com/ps",
        "article_pattern": ".title a",
        "title_selector": "h1",
        "content_selector": ".field-body"
    }
]

# Text cleaning and normalization functions
def normalize_text(text):
    if text is None:
        return ""
    
    # Remove extra whitespaces and newlines
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters except Pashto alphabet
    text = re.sub(r'[^\s\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]', '', text)
    
    # Remove quotes often found in text
    text = text.replace('"', '').replace('"', '')
    
    return text.strip()

def preprocess_text(text, stopwords_set, remove_stopwords=True):
    # First normalize
    text = normalize_text(text)
    
    # If we don't want to remove stopwords
    if not remove_stopwords:
        return text
    
    # Split words and remove stopwords
    words = text.split()
    meaningful_words = [w for w in words if w not in stopwords_set]
    
    # Join back into text
    return " ".join(meaningful_words)

def extract_text_from_html(soup, selector):
    """Extract text from HTML using selector"""
    try:
        elements = soup.select(selector)
        if elements:
            return " ".join([elem.get_text(strip=True) for elem in elements])
        else:
            return ""
    except Exception as e:
        logger.error(f"Error extracting text with selector {selector}: {e}")
        return ""

class PashtoDataGatherer:
    def __init__(self, sources=None, output_dir='/workspaces/pashto-text-dataset/ZamAI_Pashto_Datasets/gathered_data', 
                 max_articles_per_source=50, delay_between_requests=1.0):
        self.sources = sources if sources is not None else DEFAULT_SOURCES
        self.output_dir = output_dir
        self.max_articles_per_source = max_articles_per_source
        self.delay = delay_between_requests
        self.stopwords = load_stopwords()
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Create a session for all requests
        self.session = requests.Session()
        # Use a realistic user agent
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def get_article_urls(self, source_info):
        """Get article URLs from a source"""
        article_urls = []
        source_name = source_info["name"]
        source_url = source_info["url"]
        article_pattern = source_info["article_pattern"]
        
        try:
            logger.info(f"Getting article URLs from {source_name}...")
            response = self.session.get(source_url, timeout=10)
            if response.status_code != 200:
                logger.error(f"Failed to get content from {source_url}: Status {response.status_code}")
                return article_urls
            
            soup = BeautifulSoup(response.text, 'html.parser')
            article_links = soup.select(article_pattern)
            
            # Extract URLs
            for link in article_links:
                if link.has_attr('href'):
                    href = link['href']
                    # Handle relative URLs
                    if not href.startswith(('http://', 'https://')):
                        parsed_url = urlparse(source_url)
                        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
                        if href.startswith('/'):
                            href = base_url + href
                        else:
                            href = base_url + '/' + href
                    
                    article_urls.append(href)
            
            # Limit number of articles
            article_urls = article_urls[:self.max_articles_per_source]
            logger.info(f"Found {len(article_urls)} article URLs from {source_name}")
            
        except Exception as e:
            logger.error(f"Error getting article URLs from {source_name}: {e}")
        
        # Add random delay
        time.sleep(self.delay + random.uniform(0, 1))
        
        return article_urls
    
    def scrape_article_content(self, url, source_info):
        """Scrape content from an article URL"""
        try:
            logger.debug(f"Scraping content from {url}")
            response = self.session.get(url, timeout=15)
            if response.status_code != 200:
                logger.error(f"Failed to get content from {url}: Status {response.status_code}")
                return None, None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract title and content
            title = extract_text_from_html(soup, source_info["title_selector"])
            content = extract_text_from_html(soup, source_info["content_selector"])
            
            # Add random delay to be polite
            time.sleep(self.delay + random.uniform(0, 0.5))
            
            return title, content
        
        except Exception as e:
            logger.error(f"Error scraping content from {url}: {e}")
            return None, None
    
    def process_article(self, url, source_info):
        """Process a single article"""
        title, content = self.scrape_article_content(url, source_info)
        
        if not title or not content:
            return None
        
        # Normalize text
        normalized_title = normalize_text(title)
        normalized_content = normalize_text(content)
        
        # Only keep articles with sufficient content
        if len(normalized_content) < 50:  # Minimum content length
            return None
        
        # Process text (with and without stopword removal)
        processed_title = preprocess_text(title, self.stopwords, remove_stopwords=True)
        processed_content = preprocess_text(content, self.stopwords, remove_stopwords=True)
        
        return {
            "url": url,
            "source": source_info["name"],
            "title": normalized_title,
            "content": normalized_content,
            "processed_title": processed_title,
            "processed_content": processed_content,
            "collected_at": datetime.now().isoformat()
        }
    
    def gather_data(self):
        """Main function to gather data from all sources"""
        all_articles = []
        
        logger.info(f"Starting data gathering from {len(self.sources)} sources...")
        
        for source_info in self.sources:
            source_name = source_info["name"]
            logger.info(f"Processing source: {source_name}")
            
            # Get article URLs from this source
            article_urls = self.get_article_urls(source_info)
            
            # Process articles - use ThreadPoolExecutor for parallel processing
            source_articles = []
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                # Submit all scraping tasks
                future_to_url = {
                    executor.submit(self.process_article, url, source_info): url 
                    for url in article_urls
                }
                
                # Process as they complete
                for future in tqdm(concurrent.futures.as_completed(future_to_url), 
                                  total=len(future_to_url), 
                                  desc=f"Scraping {source_name}"):
                    url = future_to_url[future]
                    try:
                        article_data = future.result()
                        if article_data:
                            source_articles.append(article_data)
                    except Exception as e:
                        logger.error(f"Error processing {url}: {e}")
            
            logger.info(f"Successfully gathered {len(source_articles)} articles from {source_name}")
            all_articles.extend(source_articles)
            
            # Save articles from each source separately
            if source_articles:
                self.save_articles(source_articles, f"{source_name.lower().replace(' ', '_')}.csv")
        
        # Save all articles to a single file
        if all_articles:
            self.save_articles(all_articles, "all_gathered_articles.csv")
        
        return all_articles
    
    def save_articles(self, articles, filename):
        """Save articles to CSV and JSON formats"""
        if not articles:
            logger.warning("No articles to save.")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"{self.output_dir}/{timestamp}_{filename.split('.')[0]}"
        
        # Save to CSV
        df = pd.DataFrame(articles)
        csv_filename = f"{base_filename}.csv"
        df.to_csv(csv_filename, index=False, encoding='utf-8')
        logger.info(f"Saved {len(articles)} articles to {csv_filename}")
        
        # Save to JSON
        json_filename = f"{base_filename}.json"
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(articles, f, ensure_ascii=False, indent=2)
        logger.info(f"Saved {len(articles)} articles to {json_filename}")

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Gather Pashto text data from the internet")
    parser.add_argument('--max-articles', type=int, default=50, 
                        help='Maximum number of articles to gather per source')
    parser.add_argument('--delay', type=float, default=1.0, 
                        help='Delay between requests in seconds')
    parser.add_argument('--output-dir', type=str, 
                        default='/workspaces/pashto-text-dataset/ZamAI_Pashto_Datasets/gathered_data',
                        help='Directory to save gathered data')
    parser.add_argument('--sources-file', type=str, default=None,
                        help='JSON file with custom sources configuration')
    
    args = parser.parse_args()
    
    # Load custom sources if specified
    sources = DEFAULT_SOURCES
    if args.sources_file:
        try:
            with open(args.sources_file, 'r', encoding='utf-8') as f:
                sources = json.load(f)
            logger.info(f"Loaded {len(sources)} custom sources from {args.sources_file}")
        except Exception as e:
            logger.error(f"Error loading custom sources: {e}")
            logger.info("Falling back to default sources")
    
    # Create data gatherer and run
    gatherer = PashtoDataGatherer(
        sources=sources,
        output_dir=args.output_dir,
        max_articles_per_source=args.max_articles,
        delay_between_requests=args.delay
    )
    
    logger.info("Starting data gathering process...")
    articles = gatherer.gather_data()
    logger.info(f"Data gathering complete! Collected {len(articles)} articles in total")
    
    # Provide summary statistics
    if articles:
        df = pd.DataFrame(articles)
        content_lengths = df['content'].str.len()
        logger.info(f"Content length statistics:")
        logger.info(f"  Mean: {content_lengths.mean():.2f} characters")
        logger.info(f"  Min: {content_lengths.min()} characters")
        logger.info(f"  Max: {content_lengths.max()} characters")
        logger.info(f"  Median: {content_lengths.median()} characters")
    
    logger.info(f"All data saved to {args.output_dir}")

if __name__ == "__main__":
    main()
