# book.py
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import time, os, requests, re, json

def send_telegram(msg):
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if token and chat_id:
        requests.post(f"https://api.telegram.org/bot{token}/sendMessage",
                      data={"chat_id": chat_id, "text": msg})

def buy_5sim_number():
    url = "https://5sim.net/v1/user/buy/activation/spain/movistar/icp"
    headers = {"Authorization": f"Bearer {os.getenv('FIVESM_API_KEY')}"}
    try:
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            data = res.json()
            send_telegram(f"📱 Bought 5SIM number: {data['phone']}")
            return data['id']
        else:
            send_telegram(f"❌ 5SIM: {res.text}")
    except Exception as e:
        send_telegram(f"❌ 5SIM: {e}")
    return None

def get_5sim_otp(order_id):
    if not order_id:
        return None
    url = f"https://5sim.net/v1/user/check/{order_id}"
    headers = {"Authorization": f"Bearer {os.getenv('FIVESM_API_KEY')}"}
    for _ in range(60):
        try:
            res = requests.get(url, headers=headers)
            if res.status_code == 200:
                data = res.json()
                if data.get("sms"):
                    for sms in data["sms"]:
                        body = sms["text"]
                        match = re.search(r"\b\d{6}\b", body)
                        if match:
                            return match.group(0)
                else:
                    print("⏳ Waiting for SMS...")
            else:
                print("❌ 5SIM API:", res.text)
        except Exception as e:
            print("❌ 5SIM:", e)
        time.sleep(5)
    return None

def solve_captcha(audio_url):
    # Dummy for now. Use 2Captcha in production.
    return "123456"

if __name__ == "__main__":
    date, time_str = os.sys.argv[1], os.sys.argv[2]
    with open("session.json") as f:
        session = json.load(f)

    options = uc.ChromeOptions()
    options.add_argument("--headless=new")
    driver = uc.Chrome(options=options)

    try:
        driver.get("https://icp.administracionelectronica.gob.es/icpplustiem/icpplustiem")
        driver.add_cookie({"name": "ICPPLUS", "value": session["ICPPLUS"]})
        driver.add_cookie({"name": "JSESSIONID", "value": session["JSESSIONID"]})
        driver.refresh()

        audio = driver.find_element(By.XPATH, "//img[@alt='CAPTCHA']").get_attribute("src")
        captcha = solve_captcha(audio)
        driver.find_element(By.NAME, "txtCaptcha").send_keys(captcha)

        driver.find_element(By.XPATH, f"//input[@value='{date}']").click()
        driver.find_element(By.XPATH, f"//input[@value='{time_str}']").click()
        driver.find_element(By.XPATH, "//button[text()='Sí']").click()
        time.sleep(5)

        driver.find_element(By.XPATH, "//button[text()='Enviar SMS']").click()
        time.sleep(10)

        order_id = buy_5sim_number()
        otp = get_5sim_otp(order_id)
        if otp:
            driver.find_element(By.NAME, "txtCodigoVerificacion").send_keys(otp)
            driver.find_element(By.XPATH, "//input[@value='Aceptar']").click()
            time.sleep(3)

            pdf_url = driver.find_element(By.XPATH, "//a[contains(@href, 'imprimir')]").get_attribute("href")
            pdf_data = requests.get(pdf_url, cookies=driver.get_cookies()).content
            filename = f"CITA_{date}_{time_str.replace(':', '')}.pdf"
            with open(filename, "wb") as f:
                f.write(pdf_data)
            send_telegram(f"✅ BOOKED! PDF: {filename}")
            send_telegram(f"📍 Office: {session['OFFICE']} | NIE: {session['NIE']}")
        else:
            send_telegram("❌ OTP not received")
    finally:
        driver.quit()
