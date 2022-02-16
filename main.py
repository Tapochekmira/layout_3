import requests
import os
from pathlib import Path
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin, urlparse


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


def get_book_image_url(book_id):
    url = f'http://tululu.org/b{book_id}'
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'lxml')
    image_tag = soup.find('td', class_='ow_px_td').find('img')
    image_url = image_tag['src']
    image_url = urljoin('http://tululu.org/', image_url)
    return image_url


def get_image_name(book_image_url):
    image_path = urlparse(book_image_url).path
    image_name = image_path.split('/')[-1]
    return image_name


def download_image(url, image_name, folder='image/'):
    response = requests.get(url)
    response.raise_for_status()

    directory = os.path.join(folder, image_name)
    with open(directory, 'wb') as file:
        file.write(response.content)


def get_book_comments(book_id):
    url = f'http://tululu.org/b{book_id}'
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'lxml')
    comments_tag = soup.find('td', class_='ow_px_td').find_all('div', class_='texts')
    comments = []
    if comments_tag:
        for comment in comments_tag:
            comment = comment.find('span', class_='black')
            comments.append(comment.text)
    return comments


def get_book_genre(book_id):
    url = f'http://tululu.org/b{book_id}'
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'lxml')
    genre_tag = soup.find('td', class_='ow_px_td').find('span', class_='d_book').find_all('a')
    genres = []
    for genre in genre_tag:
        genre = genre.text
        genres.append(genre)
    return genres


def download_books(books_folder, images_folder):
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
        print(book_name)
        print(get_book_genre(book_id))
        # print( *get_book_comments(book_id), sep='\n--- ')
        # print()
        # book_image_url = get_book_image_url(book_id)
        # image_name = get_image_name(book_image_url)
        # download_image(book_image_url, image_name, images_folder)
        # download_txt(response, f'{book_id}. {book_name}', books_folder)


if __name__ == '__main__':
    books_folder = 'books/'
    images_folder = 'images/'

    Path(books_folder).mkdir(parents=True, exist_ok=True)
    Path(images_folder).mkdir(parents=True, exist_ok=True)
    download_books(books_folder,images_folder)


