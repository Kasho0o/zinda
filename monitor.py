# monitor.py
import requests, json, time, threading, os, subprocess

def load_session():
    with open("session.json") as f:
        return json.load(f)

def session_keeper():
    session = load_session()
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": f"ICPPLUS={session['ICPPLUS']}; JSESSIONID={session['JSESSIONID']}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    while True:
        try:
            requests.post("https://icp.administracionelectronica.gob.es/icpplustiem/loadAgenda",
                          data="fecha=20250901&hora=0000&idCentro=18&tipoCita=4094",
                          headers=headers, timeout=10)
            print("🔄 Session renewed")
            time.sleep(14400)
        except:
            time.sleep(60)

def check_slots():
    session = load_session()
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": f"ICPPLUS={session['ICPPLUS']}; JSESSIONID={session['JSESSIONID']}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    for day in range(1, 31):
        date = f"202509{day:02d}"
        data = f"fecha={date}&hora=0000&idCentro={session['CENTRO_ID']}&tipoCita={session['PROCEDURE_ID']}"
        try:
            res = requests.post("https://icp.administracionelectronica.gob.es/icpplustiem/loadAgenda",
                                data=data, headers=headers, timeout=10)
            if res.status_code == 200:
                slots = res.json()
                for slot in slots:
                    if slot["estado"] == "LIBRE":
                        return {"date": date, "time": slot["hora"]}
        except Exception as e:
            print("Error:", e)
    return None

def send_telegram(msg):
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if token and chat_id:
        requests.post(f"https://api.telegram.org/bot{token}/sendMessage",
                      data={"chat_id": chat_id, "text": msg})

if __name__ == "__main__":
    threading.Thread(target=session_keeper, daemon=True).start()
    print("✅ Monitor started for Mérida (Badajoz)")
    while True:
        slot = check_slots()
        if slot:
            msg = f"🎯 SLOT FOUND: {slot['date']} at {slot['time']} — RECOGIDA TIE (Mérida)"
            print(msg)
            send_telegram(msg)
            subprocess.Popen(["python", "book.py", slot["date"], slot["time"]])
            break
        time.sleep(30)
