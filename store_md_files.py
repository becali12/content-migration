import requests
import os
from markdownify import markdownify as md

directory = "./markdown"

def create_directory():
    try:
        os.mkdir(directory)
        print("Folder created")
    except FileExistsError:
        print(f"Folder already exists")


def get_articles(page):
    response = requests.get(f"https://metamask.zendesk.com/api/v2/help_center/articles?page={page}&per_page=100")
    data = response.json()
    return data['articles']


def get_all_articles():
    response = requests.get(f"https://metamask.zendesk.com/api/v2/help_center/articles?per_page=100")
    data = response.json()
    pages = data['page_count']
    articles = []
    for page in range(1, pages+1):
        new_articles = get_articles(page)
        for article in new_articles:
            articles.append(article)
    return articles

def process_articles(articles):
    for article in articles:
        title = article['title']
        title = title.replace('/', '')
        with open(f"{directory}/{title}.md", "w") as file:
            md_file = md(article["body"])
            file.write(md_file)
            print(f'Successfully stored {title}.')

def fetch_and_store_md_files():
    create_directory()
    articles = get_all_articles()
    process_articles(articles)


def store_mdx_file(md_file, category, title):
    destination_file = f'docs/{category}/{title}.mdx'
    try:
        with open(destination_file, 'w') as file:
            file.write(md_file)
        # print(f"Successfully created {destination_file}")
    except FileExistsError:
        print(f"{destination_file} already exists.")
    except:
        print(f'An error occured when creating {destination_file}')