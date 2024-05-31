# web_scraper.py

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
from bs4 import BeautifulSoup
import re
import time
from config import QGOLD_SITE_URL

def extract_urls_by_item_number(item_string):
    print("Now working with ", item_string)
    options = Options()
    #options.page_load_strategy = 'eager'
    options.add_argument('--allow-insecure-localhost')
    options.add_argument('--remote-debugging-port=9222')
    options.add_argument('--headless')  # Run Chrome in headless mode
    options.add_argument('--disable-gpu')  # Disable GPU acceleration
    options.add_argument('--no-sandbox')  # Disable the sandbox for increased security
    options.add_argument('--disable-dev-shm-usage')  # Overcome limited resource problems
    options.add_argument("--window-size=1920,1080")  # Set window size for headless mode
    options.add_argument('--disable-features=SameSiteByDefaultCookies,CookiesWithoutSameSiteMustBeSecure')
    service = ChromeService(executable_path=ChromeDriverManager().install())

    driver = webdriver.Chrome(service=service, options=options)
    driver.get(QGOLD_SITE_URL)
    time.sleep(2)

    wait = WebDriverWait(driver, 20)
    search_box = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'input-search')))
    search_box.send_keys(item_string)
    search_box.send_keys(Keys.ENTER)

    wait = WebDriverWait(driver, 300)
    print("Site is navigated to Product item page")
    time.sleep(10)
    search_result = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'p.search-result')))

    # Get the text of the search result
    search_result_text = search_result.text
    print("search_result_text", search_result)

    # Check if "No product(s) mat" is in the search result text
    if "No product(s) matches" in search_result_text:
        print("The text 'No product(s) matches' is present in the search result.")
        driver.quit()
        return ''
    else:
        print("The text 'No product(s) matches' is not present in the search result.")
        try:
            product_item = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.product-item')))
            driver.execute_script("arguments[0].scrollIntoView();", product_item)
            wait.until(EC.invisibility_of_element((By.CSS_SELECTOR, 'div.ng-progress-bar')))
            product_item.click()
        except ElementClickInterceptedException:
            print("Blocking element found, retrying...")
            wait.until(EC.invisibility_of_element((By.CSS_SELECTOR, 'div.ng-progress-bar')))
            product_item.click()

        wait = WebDriverWait(driver, 300)
        print("Site is navigated to detailed Product information page")
        try:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.ngx-gallery-thumbnails')))
        except TimeoutException:
            print("gallary element not found, retrying...")
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.ngx-gallery-thumbnails')))
            
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        thumbnail_div = soup.find_all('a', class_='ngx-gallery-thumbnail')

        image_urls = [re.search(r'url\("?(.*?)"?\)', a_tag.get('style')).group(1) for a_tag in thumbnail_div if a_tag.get('style')]

        driver.execute_script('arguments[0].style.display="none";', wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.ng-progress-bar'))))
        wait = WebDriverWait(driver, 300)
        try:
            blocking_elements = driver.find_elements(By.CSS_SELECTOR, 'span.label.ng-star-inserted')
            for element in blocking_elements:
                driver.execute_script('arguments[0].style.display="none";', element)
            
            wait = WebDriverWait(driver, 300)
            try:
                navbar_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.navbar-collapse.navbar-container-main')))
                driver.execute_script('arguments[0].style.display="none";', navbar_element)
            except TimeoutException:
                print("gallary element not found, retrying...")
                navbar_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.navbar-collapse.navbar-container-main')))
                driver.execute_script('arguments[0].style.display="none";', navbar_element)

            time.sleep(2)
            video_button = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CLASS_NAME, 'video_link_container')))
            driver.execute_script("arguments[0].scrollIntoView();", video_button)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            video_button.click()

            try:
                driver.execute_script('arguments[0].style.display="none";', wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.ng-progress-bar'))))
            except Exception as e:
                print(f"No blocking element found: {e}")

            wait.until(EC.presence_of_element_located((By.TAG_NAME, 'video')))
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            video_tag = soup.find('video')
            mp4_url = video_tag.find('source', {'type': 'video/mp4'})['src'] if video_tag else ''
        except TimeoutException:
            mp4_url=''
            print("There is no video file")
        driver.quit()

        print("Got urls of images and video of item_number:", item_string)

        return {"item_number": item_string, "image_urls": image_urls, "video_url": mp4_url}
