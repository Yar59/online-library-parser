import argparse
import logging
import os
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

CATEGORY_ID = "l55"
PAGES = 10


def parse_category_page(html_page):
    soup = BeautifulSoup(html_page.text, 'lxml')

    books_ids = [id['href'] for id in soup.select('div.bookimage a')]
    print(books_ids)


def main():
    try:
        for page in range(1, PAGES+1):
            category_url = urljoin('https://tululu.org/', CATEGORY_ID)
            category_page_url = f'{category_url}/{str(page)}/'
            page_content = requests.get(category_page_url)
            page_content.raise_for_status()
            parse_category_page(page_content)
    except requests.exceptions.HTTPError as error:
        logging.warning(error)


if __name__ == '__main__':
    main()
