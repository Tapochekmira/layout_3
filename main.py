import requests
import os
import argparse
from pathlib import Path
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin, urlparse


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError


def get_book_author(soup):
    title_tag = soup.find('td', class_='ow_px_td').find('h1')
    return title_tag.text.split(' \xa0 :: \xa0 ')


def save_txt(response, filename, folder='books/'):
    filename = sanitize_filename(filename)
    directory = os.path.join(folder, filename)
    with open(f'{directory}.txt', 'w') as file:
         file.write(response.text)


def get_book_image_url(soup):
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


def get_book_comments(soup):
    comments_tag = soup.find('td', class_='ow_px_td').find_all('div', class_='texts')
    comments = [comment.find('span', class_='black') for comment in comments_tag]
    return comments


def get_book_genre(soup):
    genre_tag = soup.find('td', class_='ow_px_td').find('span', class_='d_book').find_all('a')
    genres = [genre.text for genre in genre_tag]
    return genres


def parse_book_page(main_book_url):
    response = requests.get(main_book_url)
    response.raise_for_status()
    check_for_redirect(response)

    soup = BeautifulSoup(response.text, 'lxml')
    book_name, book_author = get_book_author(soup)
    book_genres = get_book_genre(soup)
    book_comments = get_book_comments(soup)
    book_image_url = get_book_image_url(soup)
    image_name = get_image_name(book_image_url)
    all_book_parameter ={
        'book_name': book_name,
        'book_author': book_author,
        'book_genres': book_genres,
        'book_comments': book_comments,
        'book_image_url': book_image_url,
        'image_name': image_name,
    }
    return all_book_parameter


def download_books(start_id, end_id, books_folder, images_folder):
    base_download_url = 'https://tululu.org/txt.php'

    for book_id in range(start_id, end_id + 1):
        response = requests.get(
            base_download_url,
            params={'id': book_id}
        )
        try:
            response.raise_for_status()
            check_for_redirect(response)
        except requests.HTTPError:
            continue

        main_book_url = f'http://tululu.org/b{book_id}/'
        try:
            all_book_parameter = parse_book_page(main_book_url)
        except requests.HTTPError:
            continue
        if all_book_parameter:
            download_image(
                all_book_parameter['book_image_url'],
                all_book_parameter['image_name'],
                images_folder
            )
            save_txt(
                response,
                f'{book_id}. {all_book_parameter["book_name"]}',
                books_folder
            )


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('start_id', help='id первой книги', type=int)
    parser.add_argument('end_id', help='id последней книги', type=int)
    args = parser.parse_args()

    books_folder = 'books/'
    images_folder = 'images/'

    Path(books_folder).mkdir(parents=True, exist_ok=True)
    Path(images_folder).mkdir(parents=True, exist_ok=True)
    download_books(
        args.start_id,
        args.end_id,
        books_folder,
        images_folder
    )


