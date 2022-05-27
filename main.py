import requests
import os
import logging
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename

BOOKS_URL = "https://tululu.org/"
BOOKS_DOWNLOAD_URL = "https://tululu.org/txt.php"
COUNT_OF_BOOKS = 10
DIR_PATH = "./books"


def download_files(url, file_path, headers={}, params={}):
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    check_for_redirect(response)
    with open(file_path, 'wb') as file:
        file.write(response.content)


def check_for_redirect(response):
    if len(response.history) > 0:
        raise requests.exceptions.HTTPError


def parse_book_page(book_url):
    response = requests.get(book_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    book_title = soup.find("h1").text
    book_author = "отсутствует"
    if "::" in book_title:
        book_title, book_author = book_title.split("::")
    return book_title.strip(), book_author.strip()


def download_txt(book_id, book_title, directory="./books"):
    book_file_name = sanitize_filename(f"{book_id}.{book_title}.txt")
    book_path = os.path.join(directory, book_file_name)

    payload = {
        "id": book_id
    }
    try:
        download_files(BOOKS_DOWNLOAD_URL, book_path, params=payload)
    except requests.exceptions.HTTPError:
        logging.warning(f"Redirection for book with id {book_id}")


if __name__ == '__main__':
    try:
        os.makedirs(DIR_PATH, exist_ok=True)
        for number in range(COUNT_OF_BOOKS):
            book_id = number + 1
            book_url = f"{BOOKS_URL}b{book_id}"
            book_title, book_author = parse_book_page(book_url)
            download_txt(book_id, book_title, DIR_PATH)
    except requests.exceptions.HTTPError as error:
        logging.warning(error)
