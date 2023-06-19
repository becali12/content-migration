from process_articles import process_articles
from create_folder_structure import create_folder_structure




if __name__ == '__main__':
    # creates the actual folders
    create_folder_structure()

    # processes the articles (links / titles / etc.) to comply with Docusaurus format
    # and stores the articles + images in their relevant folders
    # process_articles()

