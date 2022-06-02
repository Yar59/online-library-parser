import argparse
import logging
import os
from time import sleep
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
    book_params = {
        "title": "",
        "author": "",
        "pic_url": "",
        "comments": "",
        "genre": "",
    }
    soup = BeautifulSoup(html_page.text, 'lxml')

    page_title = soup.select_one("h1").text
    pic_tag_src = soup.select_one("div.bookimage img")["src"]
    book_params["comments"] = [comment.text for comment in soup.select("div.texts span.black")]
    book_params["genres"] = [genre.text for genre in soup.select("span.d_book a")]
    book_params["pic_url"] = urljoin(book_url, pic_tag_src)
    book_params["title"], book_params["author"] = page_title.split("::")

    return book_params


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


def display_books_params(book_params):
    print("Название книги:", book_params["title"])
    print("Автор:", book_params["author"])
    print("Жанр:", book_params["genres"])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("start_id", help="id первой книги", default=0, nargs="?", type=int)
    parser.add_argument("end_id", help="id последней книги", default=10, nargs="?", type=int)
    parser.add_argument("--books_dir", help="папка для сохранения текстовых файлов", default="./books")
    parser.add_argument("--images_dir", help="папка для сохранения обложек  книг", default="./images")
    args = parser.parse_args()
    start_id = args.start_id
    end_id = args.end_id
    books_dir = args.books_dir
    images_dir = args.images_dir

    os.makedirs(books_dir, exist_ok=True)
    os.makedirs(images_dir, exist_ok=True)

    for number in range(start_id, end_id+1):
        book_id = number
        book_url = f"{BOOKS_URL}b{book_id}"
        while True:
            try:
                response = requests.get(book_url)
                response.raise_for_status()
                check_for_redirect(response)
                book_params = parse_book_page(response, book_url)

                download_txt(book_id, book_params["title"], books_dir)
                download_image(book_params["pic_url"], book_id, book_params["title"], images_dir)
                break
            except requests.exceptions.HTTPError as error:
                logging.warning(error)

            except ErrRedirection:
                logging.warning("Redirection")

            except requests.exceptions.ConnectionError:
                logging.warning("Connection Error\nPlease check your internet connection")
                sleep(5)
                logging.warning("Trying to reconnect")

        display_books_params(book_params)


if __name__ == '__main__':
    main()
