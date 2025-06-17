from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
import time
import csv
import os

def create_driver():
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--enable-unsafe-swiftshader")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.set_page_load_timeout(60)
    return driver

driver = create_driver()
wait = WebDriverWait(driver, 10)

etalase_url = "Masukan-link-Disini" #Masukan link disini
driver.get(etalase_url)
time.sleep(3)


last_count = 0
scroll_pause_time = 2
max_scroll_attempts = 10
scroll_attempts = 0

def scroll_slowly_to_bottom(driver, delay=0.5, step=300):
    last_height = driver.execute_script("return document.body.scrollHeight")
    current_position = 0

    while current_position < last_height:
        driver.execute_script(f"window.scrollTo(0, {current_position});")
        time.sleep(delay)
        current_position += step
        last_height = driver.execute_script("return document.body.scrollHeight") 

while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(scroll_pause_time)
    produk_cards = driver.find_elements(By.CSS_SELECTOR, 'div[class*="css-tjjb18"] a')
    current_count = len(produk_cards)
    print(f" Produk saat ini: {current_count}")
    
    if current_count == last_count:
        scroll_attempts += 1
    else:
        scroll_attempts = 0
        last_count = current_count

    if scroll_attempts >= max_scroll_attempts:
        print(" Sudah mencapai akhir halaman.")
        break

produk_links = set()
for card in produk_cards:
    href = card.get_attribute("href")
    if href:
        produk_links.add(href)

produk_links = list(produk_links)
print(f" Total link produk unik ditemukan: {len(produk_links)}")


csv_file = "tokopedia_datatesting.csv" #Masukan nama disini
if not os.path.exists(csv_file):
    with open(csv_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(["Nama", "Nama_Toko", "Harga", "banyak_terjual", "Rating", "Link", "Komentar"])


for index, link in enumerate(produk_links):
    if index > 0 and index % 10 == 0:
        driver.quit()
        print(" 🔄 Restart driver untuk menjaga stabilitas...")
        driver = create_driver()

    try:
        driver.get(link)
    except (TimeoutException, WebDriverException) as e:
        print(f"[{index+1}] Gagal buka link (Timeout/Crash): {link}")
        continue

    time.sleep(3)

    try:
        nama = driver.find_element(By.CSS_SELECTOR, '[data-testid="lblPDPDetailProductName"]').text
    except:
        nama = "-"

    try:
        Nama_toko = driver.find_element(By.CSS_SELECTOR, '[data-testid="llbPDPFooterShopName"]').text
    except:
        Nama_toko = "-"

    try:
        harga = driver.find_element(By.CSS_SELECTOR, '[data-testid="lblPDPDetailProductPrice"]').text
    except:
        harga = "-"

    try:
        sold_element = driver.find_element(By.CSS_SELECTOR, '[data-testid="lblPDPDetailProductSoldCounter"]')
        banyak_terjual = sold_element.text.replace("Terjual", "").strip()
    except:
        banyak_terjual = "-"

    try:
        rating = driver.find_element(By.CSS_SELECTOR, '[data-testid="lblPDPDetailProductRatingNumber"]').text
    except:
        rating = "-"

    scroll_slowly_to_bottom(driver, delay=0.3, step=300)

    komentar = ""
    try:
        komentar_elements = driver.find_elements(By.CSS_SELECTOR, 'section#review-feed span[data-testid="lblItemUlasan"]')
        komentar_list = [el.text.strip() for el in komentar_elements[:3]]
        komentar = " || ".join(komentar_list)
    except Exception as e:
        komentar = "-"
        print(f"[{index+1}] Gagal ambil komentar")

    with open(csv_file, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow([nama, Nama_toko, harga, banyak_terjual, rating, link, komentar])

    print(f"[{index+1}] ✅ Tersimpan: {nama}")

driver.quit()
print(" ✅ Selesai! Semua data disimpan di CSV")
