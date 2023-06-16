from store_md_files import get_all_articles, store_mdx_file
from markdownify import markdownify as md
from google_sheet_operations import get_all_sheet_values
import requests
import re
from tqdm import tqdm

# replace all punctuation and whitespaces in the title with dashes, so that Docusaurus can read the file
def remove_punctuation(title):
    punctuation = ' \'.,"‘:;?/()_+!%&*`~'
    for char in punctuation:
        if char == '?' and title[-1] == '?':
            title = title.replace(char, '')
        else:
            title = title.replace(char, '-')
    # remove excess dashes
    while title[-1] == '-':
        title = title[:-1]
    return title


def remove_colon(title):
    if title[0] == '"':
        title = title.replace('"', ' ')
    return title.replace(':', ' ')


# replace whitespaces with dashes in filenames
# check if filename ends in .png or .gif etc. and if not, add last 3 chars of content-type
def download_and_store_images(links, category, article_title):
    # list containing updated (filename, path) tuples, will be used when replacing the links in the article
    new_links = []
    # sometimes multiple images have the same name in the same article, need to check and modify duplicates
    checked_filenames = []
    for link in links:
        url = link[1]
        filename = link[0]
        filename = filename.replace(' ', '-')
        response = requests.get(url)
        if response.status_code == 200:
            content_type = response.headers.get("content-type")
            if len(filename) > 4:
                # delete extension from file name, we're gonna add it from content-type
                if filename[-4] == '.':
                    filename = filename[:-4]
                elif filename[-5] == '.':
                    filename = filename[:-5]
            else:
                filename = 'image'

            # check if filename was already used, if yes modify it so it's unique
            if filename in checked_filenames:
                filename = filename + '-duplicate'
            checked_filenames.append(filename)

            if content_type[-3:] == 'gif' or content_type[-3:] == 'png' or content_type[-3:] == 'jpg':
                filename = filename + '.' + content_type[-3:]
            elif content_type[-4:] == 'jpeg':
                filename = filename + '.' + content_type[-4:]
            else:
                filename = filename + '.' + 'png'

            path = './static/img/help-center-images/' + category + '/' + article_title + '/'
            with open(path + filename, "wb") as file:
                file.write(response.content)
            # print(f"Image downloaded successfully and stored to help-center-images/{category}/{article_title}")
            docusaurus_path = '@site' + path[1:] + filename
            new_links.append((filename, docusaurus_path))
        else:
            print("Failed to download the image.")
    return new_links


def get_article_category(title, sheet_data):
    for row in sheet_data:
        category = row[0]
        article_title = row[1]
        if article_title == title:
            category = category.replace(' ', '-')
            return category
    return None


def replace_links(md_file, old_links, new_links):
    if len(old_links) == len(new_links):
        for i in range(len(new_links)):
            md_file = md_file.replace(old_links[i][1], new_links[i][1])
    else:
        print('Something went wrong in replace_links')
    return md_file


def find_image_links(md_file):
    pattern = r"!\[.*?\]\(https://support.metamask.io/hc/article_attachments/\d+\)"
    links = re.findall(pattern, md_file)
    links_list = []
    if links:
        for link in links:
            pattern = r"!\[(.*?)\]\((.*?)\)"
            matches = re.search(pattern, link)
            if matches:
                image_title = matches.group(1)
                image_link = matches.group(2)
                links_list.append((image_title, image_link))
            else:
                print("Couldn't get link or image title using regex - in find_image_links")
    # else:
    #     print('No image links were found in the article - in find_image_links')

    return links_list


# returns a list of all article-reference links within an article
def find_article_links(md_file):
    pattern = r"https://support.metamask.io/hc/en-us/articles/\d+"
    links = re.findall(pattern, md_file)
    return links


def get_article_title_by_id(articles, article_id):
    for article in articles:
        if str(article_id) == str(article['id']):
            title = article['title']
            return title
    return None


def replace_article_links(md_file, old_links, articles, sheet_data):
    for link in old_links:
        # all links follow this format: https://support.metamask.io/hc/en-us/articles/360057536611
        referenced_article_id = link[46:]
        referenced_article_title = get_article_title_by_id(articles, referenced_article_id)
        if referenced_article_title:
            ref_category = get_article_category(referenced_article_title, sheet_data)
            referenced_article_title = remove_punctuation(referenced_article_title)
            if ref_category:
                md_file = md_file.replace(link, f'../{ref_category}/{referenced_article_title}.mdx')
            else:
                print(f'Could not extract category for: {referenced_article_title}')
        else:
            print(f'Could not extract referenced article title from id - the article at {link} might have been deleted.')
    return md_file


# adds the original article title to the md file, so that it appears without dashes in docusaurus
def preserve_title(md_file, title, new_title):
    if ':' in title or '"' in title:
        title = remove_colon(title)
    custom_title = f"---\ntitle: {title}\nslug: {new_title}\n---\n\n"
    new_md = custom_title + md_file
    return new_md



# for every article:
#   search for links that follow this format: https://support.metamask.io/hc/article_attachments/13921484870939
#   download the attachments from ZD api and store them into ../category_name/article/image
#   replace those links with ../category_name/article/image
# feed the modified articles to process_article_links (from main.py)
def process_articles():
    articles = get_all_articles()
    sheet_data = get_all_sheet_values()

    # for article in articles:
    for article in tqdm(articles, desc='Processing articles', unit='article'):
        original_title = title = article['title']
        category = get_article_category(title, sheet_data)
        title = remove_punctuation(title)

        if category:
            # print(f"Processing article {title}")
            md_file = md(article["body"])
            md_file = preserve_title(md_file, original_title, title)

            # modify article reference links
            article_links = find_article_links(md_file)
            if article_links:
                md_file = replace_article_links(md_file, article_links, articles, sheet_data)

            # modify image links
            links = find_image_links(md_file)
            if len(links) != 0:
                updated_links = download_and_store_images(links, category, title)
                md_file = replace_links(md_file, links, updated_links)

            # store mdx file to /docs/category/file.mdx
            store_mdx_file(md_file, category, title)

        else:
            print('Article - ' + title + ' - was not added to the sheet')