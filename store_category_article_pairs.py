from google_sheet_operations import *
from store_md_files import *
import time

def extract_info(article):
    title = article['title']
    url = article['html_url']
    category_id = article['section_id']
    return [category_id, title, url]

# stores the following rows in the google sheet:
# category - article_title - article_url
def store_category_article_pairs():
    articles = get_all_articles()
    for article in articles:
        article_info = extract_info(article)
        store_to_sheet(article_info)
        time.sleep(1)
