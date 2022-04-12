import json
import os
from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import grouper, chunked
from pathlib import Path
from math import ceil


def get_books_from_file(file_path, file_name):
    path = os.path.join(file_path, file_name)
    with open(path, "r") as file:
        books = json.load(file)
    return books


def fill_template(books_pre_page):
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
    pages = list(chunked(books, books_pre_page))
    for page_id, books_per_page in enumerate(pages):
        books_for_render = []
        pages_amount = len(pages)
        for book in books_per_page:
            book_for_render = {
                'image': f'../{images_path}/{book["image_name"]}',
                'book_path': f'../{books_path}/{book["book_name"]}',
                'name': book['book_name'].split('.')[1],
                'author': book['book_author'],
                'genres': book['book_genres'],
            }
            books_for_render.append(book_for_render)

        template = env.get_template('template.html')
        rendered_page = template.render(
            books=list(grouper(books_for_render, 2, None)),
            pages_amount=pages_amount,
            current_page=page_id
        )
        with open(os.path.join(pages_path, f'index{page_id}.html'), 'w', encoding="utf8") as file:
            file.write(rendered_page)


if __name__ == '__main__':
    books_pre_page = 10
    fill_template(books_pre_page)

    server = Server()
    server.watch('template.html', fill_template)
    server.serve(root='.')
