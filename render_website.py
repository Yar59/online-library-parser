import json
import os
import logging

import jinja2

JSON_PATH = './books_params.json'


def main():
    with open(JSON_PATH, 'r') as file:
        books_params = json.loads(file.read())


if __name__ == '__main__':
    main()