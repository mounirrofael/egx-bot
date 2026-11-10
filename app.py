from flask import Flask, request
import requests

TOKEN = "9226284466:AAF4kiKNFHsab7cTc4T6dMPkXI1VMwb5aLo"
BASE = f"https://api.telegram.org/bot{TOKEN}"
app = Flask(__name__)

def send(chat_id, text):
    requests.post(f"{BASE}/sendMessage", json={"chat_id": chat_id, "text": text}, timeout=10)

def get_price(symbol):
    symbol = symbol.strip().upper()
    if "." not in symbol:
        symbol = symbol + ".CA"
    try:
        r = requests.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}", headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        if r.status_code == 200:
            res = r.json()['chart']['result']
            if res and res[0]['meta'].get('regularMarketPrice'):
                return res[0]['meta']['regularMarketPrice']
    except: pass
    try:
        r = requests.get(f"https://stooq.com/q/l/?s={symbol.lower()}&f=sd2t2ohlcv&h&e=csv", headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        lines = r.text.strip().splitlines()
        if len(lines) > 1:
            close = float(lines[1].split(",")[6])
            if close > 0:
                return close
    except: pass
    return None

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    msg = data.get("message", {})
    chat_id = msg.get("chat", {}).get("id")
    text = msg.get("text", "").strip()
    if chat_id and text:
        t = text.lower()
        if t.startswith("/start"):
            send(chat_id, "أهلاً بيك في بوت البورصة المصرية\nاكتب: /price COMI")
        elif t.startswith("/price"):
            parts = text.split()
            if len(parts) < 2:
                send(chat_id, "اكتب: /price COMI")
            else:
                p = get_price(parts[1])
                if p:
                    send(chat_id, f"سعر {parts[1].upper()} = {p:.2f} جنيه")
                else:
                    send(chat_id, "مش لاقي السهم ده، جرب COMI او HRHO")
    return "ok"

@app.route("/")
def index():
    return "Bot is running!"
