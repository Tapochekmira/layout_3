import json
import os
from pprint import pprint
from jinja2 import Environment, FileSystemLoader, select_autoescape


def get_books_from_file(file_path, file_name):
    path = os.path.join(file_path, file_name)
    with open(path, "r") as file:
        books_json = file.read()
    books = json.loads(books_json)
    return books


def fill_template(books, images_path):
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    render_books = []
    for book in books:
        new_render_book = {
            'image': os.path.join(images_path, book['image_name']),
            'name': book['book_name'],
            'author': book['book_author'],
        }
        render_books.append(new_render_book)

    template = env.get_template('template.html')
    rendered_page = template.render(books=render_books)

    with open('index.html', 'w', encoding="utf8") as file:
        file.write(rendered_page)


if __name__ == '__main__':
    json_file_path = 'json/'
    json_file_name = 'books.json'
    images_path = 'images'
    books = get_books_from_file(json_file_path, json_file_name)
    fill_template(books, images_path)
