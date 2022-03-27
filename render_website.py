import json
import os
from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import grouper, chunked
from pathlib import Path


def get_books_from_file(file_path, file_name):
    path = os.path.join(file_path, file_name)
    with open(path, "r") as file:
        books_json = file.read()
    books = json.loads(books_json)
    return books


def fill_template():
    json_file_path = 'json'
    json_file_name = 'books.json'
    images_path = 'images'
    books_path = 'books'
    pages_path = 'pages'
    Path(pages_path).mkdir(parents=True, exist_ok=True)

    books = get_books_from_file(json_file_path, json_file_name)

    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    for page_id, books_per_page in enumerate(list(chunked(books, 10))):
        render_books = []
        for book in books_per_page:
            new_render_book = {
                'image': os.path.join(f'../{images_path}', book['image_name']),
                'book_path': os.path.join(f'../{books_path}', book['book_name']),
                'name': book['book_name'].split('.')[1],
                'author': book['book_author'],
            }
            render_books.append(new_render_book)

        template = env.get_template('template.html')
        rendered_page = template.render(
            books=list(grouper(render_books, 2, None))
        )

        with open(os.path.join(pages_path, f'index{page_id}.html'), 'w', encoding="utf8") as file:
            file.write(rendered_page)


if __name__ == '__main__':
    fill_template()

    server = Server()
    server.watch('template.html', fill_template)
    server.serve(root='.')
