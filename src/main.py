import requests
import logging
from tqdm import tqdm

VK_API_VERSION = '5.131'
VK_ACCESS_TOKEN = 'vk1.a.wEQi5PvcaC3C8NfJeXfsL3uFoAt2ztAfqCvhXpijK2W6fPbA9Q2UB4CVJkjqrROOY_ijZNbEvRn8Gxmd2yt6PO8IP_K50WG6kpLnuXaaaAfO5CCPsECmQVcXCvSffngu7aR7fQShB3MmnZ_-8fsqI4o6-gDt1l-Gv7iG1GPG31_BAdDlfOA_o5r_OKN-ALp0'
YANDEX_DISK_TOKEN = 'y0_AgAAAAAj7IvvAADLWwAAAAEOQmCaAABp32f8WXNGG7XKraidAcxkePfj0w'


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )


def get_vk_photos(user_id, access_token, count=5):
    url = 'https://api.vk.com/method/photos.get'
    params = {
        'access_token': access_token,
        'v': VK_API_VERSION,
        'owner_id': user_id,
        'album_id': 'profile',
        'extended': 1,
        'photo_sizes': 1,
        'count': count
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()['response']['items']
    else:
        logging.error(f"Error fetching VK photos: {response.status_code} - {response.text}")
        return []


def save_photos_to_yandex_disk(photos, yandex_token):
    headers = {
        'Authorization': f'OAuth {yandex_token}'
    }
    folder_name = 'VK_Photos'
    create_folder_url = 'https://cloud-api.yandex.net/v1/disk/resources'
    params = {'path': folder_name}
    requests.put(create_folder_url, headers=headers, params=params)

    for photo in tqdm(photos, desc="Uploading photos"):
        likes = photo['likes']['count']
        date = photo['date']
        filename = f"{likes}_{date}.jpg"

        sizes = photo['sizes']
        largest_photo = max(sizes, key=lambda size: size['width'] * size['height'])
        download_url = largest_photo['url']

        upload_url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        params = {'path': f'{folder_name}/{filename}', 'url': download_url}
        response = requests.post(upload_url, headers=headers, params=params)

        if response.status_code != 202:
            logging.error(f"Error uploading photo: {response.status_code} - {response.text}")


def rename_photos(photos):
    filename_counter = {}
    renamed_photos = []

    for photo in photos:
        likes = photo['likes']['count']
        date = photo['date']
        filename = f"{likes}.jpg"

        if filename in filename_counter:
            filename = f"{likes}_{date}.jpg"

        filename_counter[filename] = filename_counter.get(filename, 0) + 1
        photo['filename'] = filename
        renamed_photos.append(photo)

    return renamed_photos


def main():
    setup_logging()
    user_id = '569128624'
    vk_photos = get_vk_photos(user_id, VK_ACCESS_TOKEN)

    if vk_photos:
        vk_photos = rename_photos(vk_photos)
        save_photos_to_yandex_disk(vk_photos, YANDEX_DISK_TOKEN)


if __name__ == '__main__':
    main()