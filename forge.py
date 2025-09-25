# forge.py
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import time, random, json

def human_type(element, text):
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.05, 0.2))

def human_click(element):
    ActionChains(driver).move_to_element(element).pause(0.5).click().perform()
    time.sleep(random.uniform(1, 3))

options = uc.ChromeOptions()
options.add_argument("--start-maximized")
driver = uc.Chrome(options=options)

try:
    driver.get("https://icp.administracionelectronica.gob.es/icpplustiem/index.html?mDes=N")
    
    # Step 1: Select Badajoz
    human_click(driver.find_element(By.XPATH, "//select[@name='form']//option[contains(text(), 'Badajoz')]"))
    human_click(driver.find_element(By.XPATH, "//button[text()='Aceptar']"))
    time.sleep(2)

    # Step 2: Select procedure
    human_click(driver.find_element(By.XPATH, "//select[@name='tramiteGrupo[0]']//option[contains(text(), 'RECOGIDA DE TARJETA DE IDENTIDAD DE EXTRANJERO (TIE)')]"))
    human_click(driver.find_element(By.XPATH, "//button[text()='Aceptar']"))
    time.sleep(2)

    # Step 3: Select office
    human_click(driver.find_element(By.XPATH, "//option[contains(text(), 'CNP MÉRIDA TARJETAS')]"))
    human_click(driver.find_element(By.XPATH, "//button[text()='Aceptar']"))
    time.sleep(2)

    # Step 4: Enter NIE
    nie_field = driver.find_element(By.NAME, "txtIdCitado")
    human_type(nie_field, "Z3690330P")
    human_click(driver.find_element(By.XPATH, "//button[text()='Aceptar']"))
    time.sleep(2)

    # Step 5: Personal info
    driver.find_element(By.NAME, "txtDesCitado").send_keys("KASHIF")
    driver.find_element(By.NAME, "txtTelfCitado").send_keys("663939048")
    driver.find_element(By.NAME, "emailCitado").send_keys("decitaprevia@gmail.com")
    human_click(driver.find_element(By.XPATH, "//button[text()='Aceptar']"))
    time.sleep(5)

    # Extract session
    cookies = {c['name']: c['value'] for c in driver.get_cookies()}
    viewstate = driver.find_element(By.NAME, "__VIEWSTATE").get_attribute("value")

    with open("session.json", "w") as f:
        json.dump({
            "ICPPLUS": cookies.get("ICPPLUS"),
            "JSESSIONID": cookies.get("JSESSIONID"),
            "VIEWSTATE": viewstate,
            "CENTRO_ID": "18",
            "PROCEDURE_ID": "4094",
            "NIE": "Z3690330P",
            "NAME": "KASHIF",
            "PHONE": "663939048",
            "EMAIL": "decitaprevia@gmail.com",
            "PROVINCE": "Badajoz",
            "OFFICE": "CNP MÉRIDA TARJETAS",
            "PROCEDURE": "RECOGIDA DE TARJETA DE IDENTIDAD DE EXTRANJERO (TIE)"
        }, f)
    print("✅ SESSION FORGED! SAVE session.json")
finally:
    driver.quit()
