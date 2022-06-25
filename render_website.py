import json
import os

from jinja2 import Environment, FileSystemLoader, select_autoescape
from more_itertools import chunked

JSON_PATH = './books_params.json'
PAGES_DIR = './pages'


def main():
    with open(JSON_PATH, 'r', encoding='UTF-8') as file:
        books_params = json.loads(file.read())
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html'])
    )
    template = env.get_template('./templates/template.html')

    books_pages = list(chunked(books_params, 10))
    total_pages = len(books_pages)
    os.makedirs(PAGES_DIR, exist_ok=True)

    for number, books_page in enumerate(books_pages):
        rendered_page = template.render(
            paired_books=chunked(books_page, 2),
            page_number=number+1,
            total_pages=total_pages,
        )
        page_path = f'{PAGES_DIR}/index{number + 1}.html'
        with open(page_path, 'w', encoding="utf8") as file:
            file.write(rendered_page)


if __name__ == '__main__':
    main()
