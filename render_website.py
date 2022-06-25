import json

from jinja2 import Environment, FileSystemLoader, select_autoescape
from more_itertools import chunked

JSON_PATH = './books_params.json'


def main():
    with open(JSON_PATH, 'r', encoding='UTF-8') as file:
        books_params = json.loads(file.read())
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html'])
    )
    template = env.get_template('template.html')
    paired_books = chunked(books_params, 2)
    rendered_page = template.render(
        paired_books=paired_books
    )

    with open('index.html', 'w', encoding="utf8") as file:
        file.write(rendered_page)


if __name__ == '__main__':
    main()
