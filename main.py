import argparse
import logging
import os
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


class ErrRedirection(Exception):
    pass


BOOKS_URL = "https://tululu.org/"
BOOKS_DOWNLOAD_URL = "https://tululu.org/txt.php"


def download_files(url, file_path, headers={}, params={}):
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    check_for_redirect(response)
    with open(file_path, 'wb') as file:
        file.write(response.content)


def check_for_redirect(response):
    if response.url == BOOKS_URL:
        raise ErrRedirection("Redirection")


def parse_book_page(html_page, book_url):
    book_info = {
        "title": "",
        "author": "",
        "pic_url": "",
        "comments": "",
        "genre": "",
    }
    soup = BeautifulSoup(html_page.text, 'lxml')

    page_title = soup.select_one("h1").text
    pic_tag_src = soup.select_one("div.bookimage img")["src"]
    book_info["comments"] = [comment.text for comment in soup.select("div.texts span.black")]
    book_info["genres"] = [genre.text for genre in soup.select("span.d_book a")]
    book_info["pic_url"] = urljoin(book_url, pic_tag_src)
    book_info["title"], book_info["author"] = page_title.split("::")

    return book_info


def download_txt(book_id, book_title, directory="./books"):
    book_file_name = sanitize_filename(f"{book_id}.{book_title}.txt")
    book_path = os.path.join(directory, book_file_name)

    payload = {
        "id": book_id
    }

    download_files(BOOKS_DOWNLOAD_URL, book_path, params=payload)


def download_image(image_url, book_id, book_title, directory="./images"):
    extension = os.path.splitext(urlparse(image_url).path)[1]
    image_file_name = sanitize_filename(f"{book_id}.{book_title}{extension}")
    image_path = os.path.join(directory, image_file_name)

    download_files(image_url, image_path)


def display_downloaded_books_info(book_info):
    print("Название книги:", book_info["title"])
    print("Автор:", book_info["author"])
    print("Жанр:", book_info["genres"])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("start_id", help="id первой книги", default=0, nargs='?')
    parser.add_argument("end_id", help="id последней книги", default=10, nargs='?')
    parser.add_argument("--books_dir", help="папка для сохранения текстовых файлов", default="./books")
    parser.add_argument("--images_dir", help="папка для сохранения обложек  книг", default="./images")
    args = parser.parse_args()
    start_id = int(args.start_id)
    end_id = int(args.end_id)
    books_dir = args.books_dir
    images_dir = args.images_dir

    os.makedirs(books_dir, exist_ok=True)
    os.makedirs(images_dir, exist_ok=True)

    for number in range(start_id, end_id+1):
        try:
            book_id = number

            book_url = f"{BOOKS_URL}b{book_id}"
            response = requests.get(book_url)
            response.raise_for_status()
            check_for_redirect(response)
            book_info = parse_book_page(response, book_url)

            display_downloaded_books_info(book_info)

            download_txt(book_id, book_info["title"], books_dir)
            download_image(book_info["pic_url"], book_id, book_info["title"], images_dir)

        except requests.exceptions.HTTPError as error:
            logging.warning(error)

        except ErrRedirection:
            logging.warning("Redirection")


if __name__ == '__main__':
    main()
