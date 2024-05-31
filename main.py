import os
import logging
import time
from config import EXTERNAL_DRIVE_PATH, IMAGE_S3_BUCKET_NAME, VIDEO_S3_BUCKET_NAME
from downloader import download_and_resize_image, download_file
from s3_uploader import upload_to_s3
from web_scraper import extract_urls_by_item_number
from excel_handler import extract_item_numbers, update_excel_with_urls
from checkpoints import save_checkpoint, load_checkpoint
from parse_url import get_original_name

MAX_RETRIES = 100
RETRY_DELAY_SECONDS = 10

logging.basicConfig(filename='process.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def process_item(item_urls, external_drive_path, checkpoints):
    item_number = item_urls["item_number"]
    image_urls = item_urls["image_urls"]
    video_url = item_urls["video_url"]
    s3_urls = []
    local_paths = []

    for idx, image_url in enumerate(image_urls):
        image_original_name = get_original_name(image_url)
        checkpoint_key = image_original_name
        if checkpoint_key in checkpoints:
            logging.info(f"Skipping {checkpoint_key}, already processed.")
            s3_urls.append(checkpoints[checkpoint_key])
            continue

        image = download_and_resize_image(image_url)
        local_image_path = os.path.join(external_drive_path, f"{image_original_name}")
        image.save(local_image_path)
        local_paths.append(local_image_path)
        
        s3_key = f"{image_original_name}"
        s3_url = upload_to_s3(local_image_path, IMAGE_S3_BUCKET_NAME, s3_key)
        s3_urls.append(s3_url)

        checkpoints[checkpoint_key] = s3_url
        save_checkpoint(checkpoints)
        logging.info(f"Processed {checkpoint_key}")

    if video_url:
        video_original_name = get_original_name(video_url)
        checkpoint_key = video_original_name
        if checkpoint_key in checkpoints:
            logging.info(f"Skipping {checkpoint_key}, already processed.")
            s3_urls.append(checkpoints[checkpoint_key])
        else:
            local_video_path = os.path.join(external_drive_path, f"{video_original_name}")
            download_file(video_url, local_video_path)
            local_paths.append(local_video_path)
            
            s3_key = f"{video_original_name}"
            s3_url = upload_to_s3(local_video_path, VIDEO_S3_BUCKET_NAME, s3_key)
            s3_urls.append(s3_url)

            checkpoints[checkpoint_key] = s3_url
            save_checkpoint(checkpoints)
            logging.info(f"Processed {checkpoint_key}")
    
    return s3_urls

def get_last_processed_item(checkpoints):
    last_processed_item = None
    for key in checkpoints.keys():
        item_number = key.split('_')[0]
        if not last_processed_item or item_number > last_processed_item:
            last_processed_item = item_number
    return last_processed_item

def main():
    retries = 0
    while retries < MAX_RETRIES:
        try:
            checkpoints = load_checkpoint()
            item_numbers = extract_item_numbers()
            last_processed_item = get_last_processed_item(checkpoints)
            if last_processed_item:
                start_index = item_numbers[item_numbers == last_processed_item].index[0] + 1
            else:
                start_index = 0

            for item_number in item_numbers[start_index:]:
                logging.info(item_number)
                item_urls = extract_urls_by_item_number(item_number)
                if item_urls:
                    s3_urls = process_item(item_urls, EXTERNAL_DRIVE_PATH, checkpoints)
                    update_excel_with_urls(item_urls["item_number"], s3_urls)
                else:
                    checkpoints[item_number] = ''
                    save_checkpoint(checkpoints)
            logging.info("Program completed successfully")
            break
        except Exception as e:
            logging.error(f"Error occurred: {e}")
            retries += 1
            if retries < MAX_RETRIES:
                logging.info(f"Retrying in {RETRY_DELAY_SECONDS} seconds...")
                time.sleep(RETRY_DELAY_SECONDS)
            else:
                logging.error("Maximum retries exceeded. Exiting...")

if __name__ == "__main__":
    main()
