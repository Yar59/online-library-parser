import argparse
import json
import logging
import os
from time import sleep
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from main import download_txt, download_image, check_for_redirect, parse_book_page, ErrRedirection, BOOKS_URL


def parse_category_page(html_page):
    soup = BeautifulSoup(html_page.text, 'lxml')

    books_id = [id['href'] for id in soup.select('div.bookimage a')]
    return books_id


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--start_page", help="номер первой страницы категории", default=1, nargs="?", type=int)
    parser.add_argument("--end_page", help="номер последней страницы категории", default=1000, nargs="?", type=int)
    parser.add_argument("--category_id", help="id категории, например l55", default="l55")
    parser.add_argument("--books_dir", help="папка для сохранения текстовых файлов", default="./books")
    parser.add_argument("--images_dir", help="папка для сохранения обложек  книг", default="./images")
    parser.add_argument("--json_dir", help="папка для сохранения файла с описанием книг", default="./")
    parser.add_argument('--skip_imgs', help="не скачивать картинки", action='store_true')
    parser.add_argument('--skip_txt', help="не скачивать тексты книг", action='store_true')

    args = parser.parse_args()
    start_page = args.start_page
    end_page = args.end_page
    books_dir = args.books_dir
    images_dir = args.images_dir
    json_dir = args.json_dir
    category_id = args.category_id
    skip_imgs = args.skip_imgs
    skip_txt = args.skip_txt

    os.makedirs(books_dir, exist_ok=True)
    os.makedirs(images_dir, exist_ok=True)
    os.makedirs(json_dir, exist_ok=True)

    books_params = []

    page = start_page
    while page < end_page:

        category_url = urljoin('https://tululu.org/', category_id)
        category_page_url = f'{category_url}/{page}/'
        try:
            page_content = requests.get(category_page_url)
            page_content.raise_for_status()
            check_for_redirect(page_content)
            books_id = parse_category_page(page_content)
        except requests.exceptions.HTTPError as error:
            logging.warning(error)
        except ErrRedirection:
            logging.warning("pages ran out")
            break

        for book_id in books_id:
            numeric_book_id = book_id.replace('b', '').replace('/', '')
            book_url = f"{BOOKS_URL}b{numeric_book_id}/"
            while True:
                try:
                    response = requests.get(book_url)
                    response.raise_for_status()
                    check_for_redirect(response)
                    book_params = parse_book_page(response, book_url)

                    if not skip_txt:
                        book_params['book_path'] = download_txt(numeric_book_id, book_params["title"], books_dir)
                    if not skip_imgs:
                        book_params['image_path'] = download_image(
                            book_params["pic_url"],
                            numeric_book_id,
                            book_params["title"],
                            images_dir
                        )
                    books_params.append(book_params)
                    break
                except requests.exceptions.HTTPError as error:
                    logging.warning(error)
                    break

                except ErrRedirection:
                    logging.warning("Redirection")
                    break

                except requests.exceptions.ConnectionError:
                    logging.warning("Connection Error\nPlease check your internet connection")
                    sleep(5)
                    logging.warning("Trying to reconnect")
        page += 1

    params_file_path = os.path.join(json_dir, "books_params.json")
    with open(params_file_path, "w", encoding='utf8') as json_file:
        json.dump(books_params, json_file, ensure_ascii=False)


if __name__ == '__main__':
    main()
