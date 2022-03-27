import argparse
import os
import json
import requests
from bs4 import BeautifulSoup
from pathlib import Path
from pathvalidate import sanitize_filename
from urllib.parse import urljoin, urlparse


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError


def get_book_name_and_author(soup):
    title_tag = soup.select_one('.ow_px_td h1')
    return title_tag.text.split(' \xa0 :: \xa0 ')


def download_book(book_url):
    download_url = 'https://tululu.org/txt.php'
    book_id = urlparse(book_url)
    book_id = book_id.path.strip('/')[1:]
    response = requests.get(
        download_url,
        params={'id': book_id}
    )
    response.raise_for_status()
    check_for_redirect(response)
    return response.text


def save_txt(book, filename, folder='books/'):
    filename = sanitize_filename(filename)
    directory = os.path.join(folder, filename)
    with open(f'{directory}.txt', 'w') as file:
        file.write(book)
    return f'{filename}.txt'


def get_book_image_url(soup):
    image_url = soup.select_one('.ow_px_td img')['src']
    image_url = urljoin('https://tululu.org/', image_url)
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
    base_download_url = 'https://tululu.org/txt.php'
    genre_tag = soup.select('.ow_px_td span.d_book a')
    genres = [genre.text for genre in genre_tag]
    return genres


def parse_book_page(main_book_url):
    response = requests.get(main_book_url)
    response.raise_for_status()
    check_for_redirect(response)

    soup = BeautifulSoup(response.text, 'lxml')
    book_name, book_author = get_book_name_and_author(soup)
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
    response.raise_for_status()
    check_for_redirect(response)

    soup = BeautifulSoup(response.text, 'lxml')
    books_tags = soup.select('.ow_px_td .bookimage a')
    books_ids = [
        urljoin('https://tululu.org', book_tag['href'])
        for book_tag in books_tags
    ]
    return books_ids


def download_books_on_page(
        books_urls,
        books_folder,
        images_folder,
        page_number,
        skip_imgs,
        skip_txt,
):
    books_on_page = []
    for book_id, book_url in enumerate(books_urls):
        response = requests.get(book_url)
        try:
            response.raise_for_status()
            check_for_redirect(response)
            book_parameters = parse_book_page(book_url)
        except requests.HTTPError:
            continue

        if not skip_imgs:
            download_image(
                book_parameters['book_image_url'],
                book_parameters['image_name'],
                images_folder
            )
        if not skip_txt:
            try:
                book_in_text = download_book(book_url)
                book_parameters['book_name'] = save_txt(
                    book_in_text,
                    f'{page_number}_{book_id}.{book_parameters["book_name"]}',
                    books_folder
                )
            except requests.HTTPError:
                continue
        books_on_page.append(book_parameters)
    return books_on_page


def save_json(books, json_folder):
    with open(f'{json_folder}books.json', 'w') as f:
        json.dump(books, f)


def download_all_books(
        start_page,
        end_page,
        books_folder,
        images_folder,
        json_folder,
        skip_imgs,
        skip_txt,
):
    base_page_url = 'https://tululu.org/l55/'
    books = []
    for page_number in range(start_page, end_page + 1):
        try:
            books_urls = get_all_books_on_page(f'{base_page_url}{page_number}/')
            books += download_books_on_page(
                books_urls,
                books_folder,
                images_folder,
                page_number,
                skip_imgs,
                skip_txt,
            )
        except requests.HTTPError:
            continue

    save_json(books, json_folder)


def get_page_amount():
    url = 'https://tululu.org/l55/'
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    comments_tag = soup.select('.ow_px_td .center .npage')[-1]
    return int(comments_tag.text)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--start_page',
        help='номер первой страницы с книгами',
        type=int,
        default=1
    )
    parser.add_argument(
        '--end_page',
        help='номер последней страницы с книгами',
        type=int,
        default=get_page_amount()
    )
    parser.add_argument(
        '--skip_imgs',
        help='Не скачивать картинки',
        action='store_true',
    )
    parser.add_argument(
        '--skip_txt',
        help='Не скачивать текст книг',
        action='store_true'
    )
    parser.add_argument(
        '--dest_folder',
        help='Указать путь к каталогу с результатами '
             'парсинга: картинкам, книгам, JSON.'
             'По умолчанию директория файла main.py',
        default=''
    )
    parser.add_argument(
        '--json_path',
        help='указать свой путь к *.json файлу с результатами',
        default='json/'
    )
    args = parser.parse_args()

    books_folder = 'books/'
    images_folder = 'images/'

    if not args.skip_txt:
        Path(os.path.join(args.dest_folder, books_folder)).\
            mkdir(parents=True, exist_ok=True)
    if not args.skip_imgs:
        Path(os.path.join(args.dest_folder, images_folder)).\
            mkdir(parents=True, exist_ok=True)
    Path(os.path.join(args.dest_folder, args.json_path)).\
        mkdir(parents=True, exist_ok=True)

    download_all_books(
        args.start_page,
        args.end_page,
        os.path.join(args.dest_folder, books_folder),
        os.path.join(args.dest_folder, images_folder),
        os.path.join(args.dest_folder, args.json_path),
        args.skip_imgs,
        args.skip_txt,
    )
