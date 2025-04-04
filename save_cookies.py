from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import json

# 📁 Lancer Chrome avec profil vierge
options = Options()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options)

# 🔎 Aller sur le site
url = "https://www.analyst-desk.com"
driver.get(url)
print("🔄 Page d'accueil ouverte")

# 🚪 Pause : ici tu te connectes manuellement
print("⏳ Connecte-toi manuellement puis appuie sur ENTRÉE ici pour sauvegarder les cookies...")
input()

# 🔢 Récupérer et sauvegarder les cookies
cookies = driver.get_cookies()
with open("cookies.json", "w") as f:
    json.dump(cookies, f, indent=4)

print("✅ Cookies sauvegardés dans cookies.json")
driver.quit()
