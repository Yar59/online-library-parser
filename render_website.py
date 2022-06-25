import json
import os
import logging

from jinja2 import Environment, FileSystemLoader, select_autoescape

JSON_PATH = './books_params.json'


def main():
    with open(JSON_PATH, 'r', encoding='UTF-8') as file:
        books_params = json.loads(file.read())
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html'])
    )
    template = env.get_template('template.html')

    rendered_page = template.render(
        books=books_params
    )

    with open('index.html', 'w', encoding="utf8") as file:
        file.write(rendered_page)


if __name__ == '__main__':
    main()
