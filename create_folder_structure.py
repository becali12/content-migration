import os
from google_sheet_operations import get_first_col, get_all_sheet_values
from store_md_files import get_all_articles
from process_articles import remove_punctuation


def create_directory(path, folder):
    try:
        os.mkdir(path + folder)
        print(f"Folder {folder} created at {path}")
    except FileExistsError:
        print(f"Folder {folder} already exists in {path}")


def create_index_file(original_name, slug, sidebar_position):
    file_content = f'---\ntitle: {original_name}\nslug: {slug}\nsidebar_position: {sidebar_position}\n---'
    file_path = f'./docs/{slug}/index.mdx'

    with open(file_path, 'w') as file:
        file.write(file_content)

    return sidebar_position + 1


def get_categories():
    categories = get_first_col()
    unique_categories = list(set(categories[1:]))
    return unique_categories

def get_article_category(article, sheet_data):
    title = article['title']
    for row in sheet_data:
        category = row[0]
        article_title = row[1]
        if article_title == title:
            category = category.replace(' ', '-')
            return category
    return None

def create_folder_structure():
    sidebar_position = 1
    create_directory('./', 'static')
    create_directory('./', 'docs')
    create_directory('./static/', 'img')
    create_directory('./static/img/', 'help-center-images')

    categories = get_categories()
    articles = get_all_articles()

    for category in categories:
        original_name = category
        category = category.replace(' ', '-')
        create_directory('./docs/', category)
        create_directory('./static/img/help-center-images/', category)
        sidebar_position = create_index_file(original_name, category, sidebar_position)

    sheet_data = get_all_sheet_values()
    for article in articles:
        article_category = get_article_category(article, sheet_data)
        if article_category:
            title = article['title']
            title = remove_punctuation(title)
            create_directory(f'./static/img/help-center-images/{article_category}/', title)
        else:
            print('Article - ' + article['title'] + ' - was not added to google sheet.')