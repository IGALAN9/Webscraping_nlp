from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import csv

# --- Setup WebDriver ---
options = Options()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
wait = WebDriverWait(driver, 10)

# --- Link etalase toko ---
etalase_url = "https://www.tokopedia.com/enterkomputer/etalase/gaming-mouse?sort=11"
driver.get(etalase_url)
time.sleep(3)

# --- Scroll otomatis untuk load semua produk ---
last_count = 0
scroll_pause_time = 2
max_scroll_attempts = 10
scroll_attempts = 0

while True:
    # Scroll ke bawah
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(scroll_pause_time)

    # Hitung jumlah produk saat ini
    produk_cards = driver.find_elements(By.CSS_SELECTOR, 'div[data-testid="master-product-card"] a')
    current_count = len(produk_cards)

    print(f"📦 Produk saat ini: {current_count}")

    if current_count == last_count:
        scroll_attempts += 1
    else:
        scroll_attempts = 0
        last_count = current_count

    if scroll_attempts >= max_scroll_attempts:
        print("✅ Sudah mencapai akhir halaman.")
        break

# --- Ambil semua link produk dari etalase ---
produk_links = set()
for card in produk_cards:
    href = card.get_attribute("href")
    if href:
        produk_links.add(href)

produk_links = list(produk_links)
print(f"🔗 Total link produk unik ditemukan: {len(produk_links)}")

produk_list = []

# --- Kunjungi tiap produk ---
for link in produk_links:
    driver.get(link)
    time.sleep(3)

    try:
        nama = driver.find_element(By.CSS_SELECTOR, '[data-testid="lblPDPDetailProductName"]').text
    except:
        nama = "-"

    try:
        harga = driver.find_element(By.CSS_SELECTOR, '[data-testid="lblPDPDetailProductPrice"]').text
    except:
        harga = "-"

    try:
        banyak_terjual = driver.find_element(By.CSS_SELECTOR, '[data-testid="lblPDPDetailProductSoldCounter"]').text
    except:
        banyak_terjual = "-"
    
    try:
        rating = driver.find_element(By.CSS_SELECTOR, '[data-testid="lblPDPDetailProductRatingNumber"]').text
    except:
        rating = "-"

    # --- Scroll agar komentar muncul ---
    driver.execute_script("window.scrollTo(0, 1500);")
    time.sleep(2)

    komentar = ""
    try:
        komentar_elements = driver.find_elements(By.CSS_SELECTOR, 'span[data-testid="lblItemUlasan"]')
        komentar_list = [el.text.strip() for el in komentar_elements[:3]]
        komentar = " || ".join(komentar_list)
    except Exception as e:
        print("⚠️ Gagal ambil komentar:", e)

    produk_list.append([nama, harga, banyak_terjual, rating, link, komentar])
    print(f"✅ Data produk: {nama}")

# --- Simpan ke CSV ---
with open("tokopedia_enterkomputer.csv", mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Nama", "Harga", "banyak_terjual", "Rating", "Link", "Komentar"])
    writer.writerows(produk_list)

driver.quit()
print("🎉 Selesai! Data disimpan di 'hasil_scrapping.csv'")
