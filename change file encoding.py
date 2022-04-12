import json
import os


def get_books_from_file(file_path, file_name):
    path = os.path.join(file_path, file_name)
    with open(path, "r") as file:
        books = json.load(file)
    return books


def change_file_encoding(books, books_path):
    for book in books:
        book_path = os.path.join(books_path, book["book_name"])
        print(book_path)

        with open(book_path, 'r', encoding="ANSI") as f:
            data = f.read()
        with open(book_path, 'wb') as fh:
            fh.write(data.encode('utf-8'))


if __name__ == '__main__':
    json_file_path = 'json'
    json_file_name = 'books.json'
    books_path = 'books'

    books = get_books_from_file(json_file_path, json_file_name)

    change_file_encoding(books, books_path)
