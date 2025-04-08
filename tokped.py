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
etalase_url = "https://www.tokopedia.com/goodgamingshop/etalase/gaming-mouse"
driver.get(etalase_url)
time.sleep(5)

# --- Ambil semua link produk dari etalase ---
produk_cards = driver.find_elements(By.CSS_SELECTOR, 'div[data-testid="master-product-card"] a')
produk_links = []

for card in produk_cards[:20]:  # Ubah angka ini kalau mau lebih banyak produk
    href = card.get_attribute("href")
    if href:
        produk_links.append(href)

print(f"🔗 Total link produk ditemukan: {len(produk_links)}")

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
        rating = driver.find_element(By.CSS_SELECTOR, '[data-testid="lblPDPDetailProductRatingNumber"]').text
    except:
        rating = "-"

    # --- Scroll agar komentar muncul ---
    driver.execute_script("window.scrollTo(0, 1500);")
    time.sleep(3)

    komentar = ""
    try:
        komentar_elements = driver.find_elements(By.CSS_SELECTOR, 'span[data-testid="lblItemUlasan"]')
        komentar_list = [el.text.strip() for el in komentar_elements[:3]]
        komentar = " || ".join(komentar_list)
    except Exception as e:
        print("⚠️ Gagal ambil komentar:", e)

    produk_list.append([nama, harga, rating, link, komentar])
    print(f"✅ Data produk: {nama}")

# --- Simpan ke CSV ---
with open("tokopedia_gamingmouse.csv", mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Nama", "Harga", "Rating", "Link", "Komentar"])
    writer.writerows(produk_list)

driver.quit()
print("🎉 Selesai! Data disimpan di 'tokopedia_gamingmouse.csv'")
