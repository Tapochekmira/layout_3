import requests
from pathlib import Path


def download_books(directory):
    base_download_url = 'https://tululu.org/txt.php'
    books_ids = [i for i in range(1, 11)]

    for book_id in books_ids:
        response = requests.get(
            base_download_url,
            params={'id': book_id}
        )
        response.raise_for_status()
        with open(f'{directory}{book_id}.txt', 'wb') as file:
            file.write(response.content)


if __name__ == '__main__':
    directory = 'books/'

    Path(directory).mkdir(parents=True, exist_ok=True)
    download_books(directory)
