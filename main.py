import argparse
import os
import requests
from bs4 import BeautifulSoup
from pathlib import Path
from pathvalidate import sanitize_filename
from pprint import pprint
from urllib.parse import urljoin, urlparse


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError


def get_book_author(soup):
    title_tag = soup.select_one('.ow_px_td h1')
    return title_tag.text.split(' \xa0 :: \xa0 ')


def save_txt(response, filename, folder='books/'):
    filename = sanitize_filename(filename)
    directory = os.path.join(folder, filename)
    with open(f'{directory}.txt', 'w') as file:
        file.write(response.text)


def get_book_image_url(soup):
    image_url = soup.select_one('.ow_px_td img')['src']
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
    comments_tag = soup.select('.ow_px_td .texts .black')
    comments = [comment.text for comment in comments_tag]
    return comments


def get_book_genre(soup):
    genre_tag = soup.select('.ow_px_td span.d_book a')
    genres = [genre.text for genre in genre_tag]
    return genres


def parse_book_page(main_book_url):
    response = requests.get(main_book_url)
    response.raise_for_status()
    check_for_redirect(response)
    print(main_book_url)

    soup = BeautifulSoup(response.text, 'lxml')
    book_name, book_author = get_book_author(soup)
    book_genres = get_book_genre(soup)
    book_comments = get_book_comments(soup)
    book_image_url = get_book_image_url(soup)
    image_name = get_image_name(book_image_url)
    all_book_parameter = {
        'book_name': book_name,
        'book_author': book_author,
        'book_genres': book_genres,
        'book_comments': book_comments,
        'book_image_url': book_image_url,
        'image_name': image_name,
    }
    return all_book_parameter


def get_all_books_on_page(page_url):
    response = requests.get(page_url)
    response.raise_for_status()
    try:
        response.raise_for_status()
        check_for_redirect(response)
    except requests.HTTPError:
        return

    soup = BeautifulSoup(response.text, 'lxml')
    books_tags = soup.select('.ow_px_td .bookimage a')
    books_ids = [
        urljoin('http://tululu.org', book_tag['href'])
        for book_tag in books_tags
    ]
    return books_ids


def download_books_on_page(books_urls, books_folder, images_folder):
    books_on_page = []
    for book_id, book_url in enumerate(books_urls):
        response = requests.get(book_url)
        try:
            response.raise_for_status()
            check_for_redirect(response)
        except requests.HTTPError:
            return
        try:
            all_book_parameter = parse_book_page(book_url)
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
                f'{book_id}.{all_book_parameter["book_name"]}',
                books_folder
            )
        books_on_page.append(all_book_parameter)
    return books_on_page


def download_all_books(start_page, end_page, books_folder, images_folder):
    base_page_url = 'http://tululu.org/l55/'
    books = []
    for page_number in range(start_page, end_page + 1):
        books_urls = get_all_books_on_page(f'{base_page_url}{page_number}/')
        books += download_books_on_page(books_urls, books_folder, images_folder)
    pprint(books)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('start_page', help='номер первой страницы с книгами', type=int)
    parser.add_argument('end_page', help='номер последней страницы с книгами', type=int)
    args = parser.parse_args()

    books_folder = 'books/'
    images_folder = 'images/'

    Path(books_folder).mkdir(parents=True, exist_ok=True)
    Path(images_folder).mkdir(parents=True, exist_ok=True)
    download_all_books(
        args.start_page,
        args.end_page,
        books_folder,
        images_folder
    )
