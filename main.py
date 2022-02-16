import requests
import os
from pathlib import Path
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError


def get_book_author(book_id):
    url = f'http://tululu.org/b{book_id}'
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'lxml')
    title_tag = soup.find('td', class_='ow_px_td').find('h1')
    return title_tag.text.split(' \xa0 :: \xa0 ')


def download_txt(response, filename, folder='books/'):
    filename = sanitize_filename(filename)
    directory = os.path.join(folder, filename)
    with open(f'{directory}.txt', 'wb') as file:
        file.write(response.content)


def download_books(folder):
    base_download_url = 'https://tululu.org/txt.php'
    books_ids = [i for i in range(1, 11)]

    for book_id in books_ids:
        response = requests.get(
            base_download_url,
            params={'id': book_id}
        )
        response.raise_for_status()
        try:
            check_for_redirect(response)
        except requests.HTTPError:
            continue

        book_name, book_author = get_book_author(book_id)
        download_txt(response, f'{book_id}. {book_name}', folder)


if __name__ == '__main__':
    folder = 'books/'

    Path(folder).mkdir(parents=True, exist_ok=True)
    download_books(folder)


