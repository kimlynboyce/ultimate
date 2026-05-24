import streamlit as st
import os, io, re, json, secrets, string, hashlib, base64, uuid, sqlite3
import calendar as cal_lib, xml.etree.ElementTree as ET
import pandas as pd, numpy as np
import plotly.express as px, plotly.graph_objects as go
import requests
from datetime import datetime, timedelta, timezone, date
from cryptography.fernet import Fernet

# ══════════════════════════════════════════════════════════════════════════════
# CONFIG & TIME
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(page_title="VECTOR OS", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")
now      = (datetime.now(timezone.utc) - timedelta(hours=4)).replace(tzinfo=None)
DATA_DIR = "vos_data"; os.makedirs(DATA_DIR, exist_ok=True)
DB_PATH  = os.path.join(DATA_DIR, "crm.db")
def fp(name): return os.path.join(DATA_DIR, name)

# ══════════════════════════════════════════════════════════════════════════════
# CSS — Unified VECTOR OS Dark System
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Space+Mono:wght@400;700&family=Syne:wght@700;800&display=swap');

/* ── AURORA BOREALIS THEME ── */
:root {
    --primary:   #00ffcc;   /* aurora teal   */
    --violet:    #aa44ff;   /* aurora violet */
    --pink:      #ff44aa;   /* aurora pink   */
    --gold:      #ffe066;   /* aurora gold   */
    --danger:    #ff4477;   /* aurora red    */
    --bg:        #020810;   /* arctic night  */
    --bg2:       #05101e;   /* card bg       */
    --bg3:       #071628;   /* sidebar       */
    --border:    #0c2340;   /* border        */
    --border2:   #112d50;   /* card border   */
    --text:      #e0f4ff;   /* cool white    */
    --dim:       #2a5070;   /* dim text      */
    --dim2:      #163050;   /* very dim      */
}

*,*::before,*::after{box-sizing:border-box;}
html,body,.main,[data-testid="stAppViewContainer"]{
    background:var(--bg)!important;
    color:var(--text);
    font-family:'Space Grotesk',sans-serif;
}
[data-testid="stSidebar"]{
    background:var(--bg3)!important;
    border-right:1px solid var(--border)!important;
}
[data-testid="stSidebar"] *{color:var(--text)!important;}
[data-testid="block-container"]{padding-top:1rem!important;}
footer{visibility:hidden;}

/* ── HEADER ── */
.vos-header{
    display:flex;justify-content:space-between;align-items:flex-end;
    padding:1.5rem 0 1rem;
    border-bottom:1px solid var(--border);
    margin-bottom:1.5rem;
}
.vos-wordmark{
    font-family:'Syne',sans-serif;
    font-size:2.4rem;font-weight:800;
    background:linear-gradient(135deg,var(--primary),var(--violet),var(--pink));
    -webkit-background-clip:text;-webkit-text-fill-color:transparent;
    letter-spacing:-1px;line-height:1;
}
.vos-wordmark span{color:var(--gold);-webkit-text-fill-color:var(--gold);}
.vos-time{
    font-family:'Space Mono',monospace;font-size:0.62rem;
    color:var(--dim);letter-spacing:2px;text-align:right;line-height:1.8;
}
.vos-time strong{color:var(--primary);}

/* ── ALERTS ── */
.alert-strip{
    background:rgba(0,255,204,0.04);
    border:1px solid rgba(0,255,204,0.15);
    border-left:3px solid var(--primary);
    padding:0.6rem 1rem;margin-bottom:0.4rem;
    font-family:'Space Mono',monospace;font-size:0.65rem;letter-spacing:1px;
    color:var(--primary);display:flex;justify-content:space-between;align-items:center;
}
.alert-strip.critical{
    background:rgba(255,68,119,0.06);
    border-color:rgba(255,68,119,0.2);border-left-color:var(--danger);
    color:var(--danger);
}
.alert-strip.clear{
    background:rgba(0,255,204,0.04);
    border-color:rgba(0,255,204,0.15);border-left-color:var(--primary);
    color:var(--primary);
}

/* ── SECTION LABEL ── */
.s-label{
    font-family:'Space Mono',monospace;font-size:0.58rem;letter-spacing:4px;
    text-transform:uppercase;color:var(--dim);
    border-bottom:1px solid var(--border);
    padding-bottom:0.5rem;margin-bottom:1rem;margin-top:1.5rem;
}

/* ── STAT BLOCKS ── */
.stat-block{
    background:var(--bg2);
    border:1px solid var(--border);
    border-top:2px solid var(--primary);
    padding:1.2rem;
}
.stat-val{font-family:'Space Mono',monospace;font-size:2rem;font-weight:700;color:var(--primary);line-height:1;}
.stat-val.w{color:var(--text);}
.stat-val.g{color:var(--primary);}
.stat-val.r{color:var(--danger);}
.stat-val.b{color:var(--violet);}
.stat-val.p{color:var(--pink);}
.stat-lbl{font-family:'Space Mono',monospace;font-size:0.55rem;letter-spacing:3px;text-transform:uppercase;color:var(--dim);margin-top:0.4rem;}

/* ── CARDS ── */
.v-card{background:var(--bg2);border:1px solid var(--border);padding:1rem 1.2rem;margin-bottom:0.5rem;}
.v-card-a{border-left:2px solid var(--primary);background:rgba(0,255,204,0.03);}
.v-card-g{border-left:2px solid var(--primary);background:rgba(0,255,204,0.04);border-color:rgba(0,255,204,0.1);}
.v-card-r{border-left:2px solid var(--danger);background:rgba(255,68,119,0.05);border-color:rgba(255,68,119,0.15);}
.v-card-b{border-left:2px solid var(--violet);background:rgba(170,68,255,0.05);border-color:rgba(170,68,255,0.15);}
.v-card-p{border-left:2px solid var(--pink);background:rgba(255,68,170,0.05);border-color:rgba(255,68,170,0.15);}

.v-row{display:flex;justify-content:space-between;align-items:center;padding:0.55rem 0;border-bottom:1px solid var(--dim2);font-size:0.82rem;}
.v-row-label{color:var(--dim);font-family:'Space Mono',monospace;font-size:0.62rem;letter-spacing:1px;}
.v-row-val{color:var(--text);font-family:'Space Mono',monospace;font-size:0.75rem;}
.v-row-val.a{color:var(--primary);}
.v-row-val.g{color:var(--primary);}
.v-row-val.r{color:var(--danger);}

/* ── PROGRESS BARS ── */
.v-bar-wrap{background:var(--dim2);height:3px;border-radius:2px;margin:0.5rem 0;}
.v-bar-fill{height:3px;border-radius:2px;background:linear-gradient(90deg,var(--primary),var(--violet));}
.v-bar-fill.g{background:linear-gradient(90deg,var(--primary),var(--gold));}
.v-bar-fill.r{background:linear-gradient(90deg,var(--pink),var(--danger));}
.v-bar-fill.b{background:linear-gradient(90deg,var(--violet),var(--pink));}

/* ── PILLS ── */
.vpill{display:inline-block;font-family:'Space Mono',monospace;font-size:0.55rem;letter-spacing:1px;text-transform:uppercase;padding:2px 8px;border-radius:20px;}
.vpill-a{background:rgba(0,255,204,0.1);color:var(--primary);border:1px solid rgba(0,255,204,0.25);}
.vpill-g{background:rgba(0,255,204,0.1);color:var(--primary);border:1px solid rgba(0,255,204,0.25);}
.vpill-r{background:rgba(255,68,119,0.1);color:var(--danger);border:1px solid rgba(255,68,119,0.25);}
.vpill-b{background:rgba(170,68,255,0.1);color:var(--violet);border:1px solid rgba(170,68,255,0.25);}
.vpill-p{background:rgba(255,68,170,0.1);color:var(--pink);border:1px solid rgba(255,68,170,0.25);}

/* ── NEWS ── */
.news-card{
    background:var(--bg2);border:1px solid var(--border);
    padding:0.9rem 1rem;margin-bottom:1px;transition:border-color 0.2s,background 0.2s;
}
.news-card:hover{border-color:var(--primary);background:rgba(0,255,204,0.03);}
.news-headline{font-family:'Space Grotesk',sans-serif;font-size:0.88rem;font-weight:500;color:var(--text);line-height:1.5;}
.news-stamp{font-family:'Space Mono',monospace;font-size:0.58rem;color:var(--dim);letter-spacing:1px;margin-top:0.3rem;}

/* ── WEATHER ── */
.wx-block{background:var(--bg2);border:1px solid var(--border);padding:1.5rem;text-align:center;}
.wx-temp{
    font-family:'Space Mono',monospace;font-size:3rem;font-weight:700;line-height:1;
    background:linear-gradient(135deg,var(--primary),var(--violet));
    -webkit-background-clip:text;-webkit-text-fill-color:transparent;
}
.wx-desc{font-family:'Space Mono',monospace;font-size:0.6rem;letter-spacing:3px;text-transform:uppercase;color:var(--dim);margin-top:0.5rem;}

/* ── THOUGHTS ── */
.thought-block{
    background:var(--bg2);
    border:1px solid var(--border);
    border-top:2px solid var(--violet);
    padding:1rem 1.2rem;margin-bottom:0.5rem;
    font-size:0.85rem;color:var(--text);line-height:1.7;
}
.thought-stamp{font-family:'Space Mono',monospace;font-size:0.58rem;color:var(--dim);margin-top:0.4rem;letter-spacing:1px;}

/* ── SYNAPSE ── */
.syn-id{font-family:'Space Mono',monospace;font-size:0.6rem;color:var(--primary);word-break:break-all;line-height:1.8;letter-spacing:1px;}

/* ── CODE & INFO BLOCKS ── */
.cb{
    background:#030d1e;border:1px solid var(--border2);border-radius:4px;
    padding:.8rem 1rem;font-family:'Space Mono',monospace;font-size:.79rem;
    color:var(--primary);white-space:pre-wrap;word-break:break-all;
}
.ib{background:#040f1e;border:1px solid var(--border);border-radius:6px;padding:.9rem 1.1rem;font-size:.84rem;color:#7aaccf;margin:.4rem 0;}
.warn{background:rgba(255,68,119,0.08);border:1px solid rgba(255,68,119,0.2);border-radius:4px;padding:5px 10px;margin:2px 0;font-size:.82rem;color:var(--danger);}
.ok{background:rgba(0,255,204,0.06);border:1px solid rgba(0,255,204,0.2);border-radius:4px;padding:5px 10px;font-size:.82rem;color:var(--primary);}

/* ── KPI ── */
.kpi{background:var(--bg2);border:1px solid var(--border);padding:18px 22px;border-top:4px solid var(--c);}
.kpi-label{color:var(--dim);font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.06em;font-family:'Space Mono',monospace;}
.kpi-value{color:var(--primary);font-size:2rem;font-weight:700;line-height:1.2;font-family:'Space Mono',monospace;}
.kpi-sub{color:var(--dim);font-size:11px;margin-top:2px;font-family:'Space Mono',monospace;}

/* ── STREAMLIT OVERRIDES ── */
.stTextInput>div>div>input,
.stTextArea>div>div>textarea,
.stNumberInput>div>div>input{
    background:var(--bg2)!important;border:1px solid var(--border2)!important;
    color:var(--text)!important;border-radius:4px!important;
    font-family:'Space Mono',monospace!important;font-size:0.78rem!important;
}
.stTextInput>div>div>input:focus,
.stTextArea>div>div>textarea:focus{border-color:var(--primary)!important;box-shadow:0 0 0 1px rgba(0,255,204,0.2)!important;}
.stSelectbox>div>div{background:var(--bg2)!important;border:1px solid var(--border2)!important;border-radius:4px!important;}
.stButton>button{
    background:transparent!important;
    color:var(--primary)!important;
    border:1px solid var(--primary)!important;
    border-radius:4px!important;
    font-family:'Space Mono',monospace!important;
    font-size:0.7rem!important;letter-spacing:2px!important;
    font-weight:700!important;text-transform:uppercase!important;
    transition:all 0.2s!important;
}
.stButton>button:hover{
    background:var(--primary)!important;
    color:#020810!important;
    box-shadow:0 0 20px rgba(0,255,204,0.3)!important;
}
[data-testid="stMetric"]{
    background:var(--bg2)!important;
    border:1px solid var(--border)!important;
    border-top:2px solid var(--primary)!important;
    border-radius:4px!important;padding:1rem!important;
}
[data-testid="stMetricValue"]{color:var(--primary)!important;}
[data-testid="stMetricLabel"]{color:var(--dim)!important;}
.stTabs [data-baseweb="tab"]{
    font-family:'Space Mono',monospace!important;font-size:0.65rem!important;
    letter-spacing:2px!important;color:var(--dim)!important;
}
.stTabs [aria-selected="true"]{color:var(--primary)!important;}
.stTabs [data-baseweb="tab-highlight"]{background:var(--primary)!important;}
.stProgress>div>div{background:linear-gradient(90deg,var(--primary),var(--violet))!important;}
div[data-baseweb="select"] *{color:var(--text)!important;background:var(--bg2)!important;}

/* ── FOOTER ── */
.vos-footer{
    text-align:center;padding:2rem;
    font-family:'Space Mono',monospace;font-size:0.55rem;letter-spacing:3px;
    color:var(--dim2);border-top:1px solid var(--border);
    margin-top:3rem;text-transform:uppercase;
    background:linear-gradient(180deg,transparent,rgba(0,255,204,0.02));
}
</style>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SHARED UTILITIES
# ══════════════════════════════════════════════════════════════════════════════

def get_client():
    key = st.session_state.get("api_key","") or os.environ.get("ANTHROPIC_API_KEY","")
    if not key: return None
    import anthropic; return anthropic.Anthropic(api_key=key)

@st.cache_data(show_spinner=False)
def ai_call(prompt, system="", model="claude-haiku-4-5-20251001", max_tokens=1000):
    key = st.session_state.get("api_key","") or os.environ.get("ANTHROPIC_API_KEY","")
    if not key: return "⚠️ No API key."
    import anthropic
    try:
        kw = dict(model=model, max_tokens=max_tokens, messages=[{"role":"user","content":prompt}])
        if system: kw["system"] = system
        return anthropic.Anthropic(api_key=key).messages.create(**kw).content[0].text
    except Exception as e: return f"❌ {e}"

def ai(prompt, system="", max_tokens=1500):
    model = "claude-sonnet-4-20250514" if st.session_state.get("use_sonnet") else "claude-haiku-4-5-20251001"
    return ai_call(prompt, system, model, max_tokens)

def _fkey(pw): return base64.urlsafe_b64encode(hashlib.sha256(pw.encode()).digest())
def enc(text, pw): return Fernet(_fkey(pw)).encrypt(text.encode()).decode()
def dec(ct, pw):   return Fernet(_fkey(pw)).decrypt(ct.encode()).decode()

def gen_pwd(n=24, sym=True):
    alpha = string.ascii_letters + string.digits + ("!@#$%^&*()-_=+[]{}|;:,.<>?" if sym else "")
    return "".join(secrets.choice(alpha) for _ in range(n))

def pwd_strength(p):
    s = sum([len(p)>=12, len(p)>=20, bool(re.search(r"[A-Z]",p)),
             bool(re.search(r"[a-z]",p)), bool(re.search(r"\d",p)),
             bool(re.search(r"[^A-Za-z0-9]",p))])
    return ("Weak","#ff4444") if s<=2 else ("Moderate","#ffaa00") if s<=4 else ("Strong","#44ff88")

def rand_mac():
    b = [(secrets.randbelow(256)&0xFE)|0x02]+[secrets.randbelow(256) for _ in range(5)]
    return ":".join(f"{x:02x}" for x in b)

def get_weather(loc="Trinidad"):
    try:
        r = requests.get(f"https://wttr.in/{loc}?format=j1", timeout=8, headers={"User-Agent":"Mozilla/5.0"})
        if r.status_code == 200: return r.json()
    except: pass
    return None

def get_news(url, count=6):
    try:
        root = ET.fromstring(requests.get(url, timeout=8).content)
        items = []
        for item in root.findall('.//item')[:count]:
            t = item.find('title'); l = item.find('link'); p = item.find('pubDate')
            items.append({"title": t.text if t is not None else "No title",
                          "link":  l.text if l is not None else "#",
                          "pub":   p.text[:22] if p is not None else ""})
        return items
    except: return []

def load_json(path, default):
    try:
        if os.path.exists(path):
            with open(path) as f: return json.load(f)
    except: pass
    return default

def save_json(path, data):
    with open(path,"w") as f: json.dump(data, f, indent=2)

def vader(text):
    try:
        from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
        return SentimentIntensityAnalyzer().polarity_scores(text)
    except: return {"compound":0,"pos":0,"neu":1,"neg":0}

def scan_sql(code):
    pats = [("'\\s*OR\\s*'1'\\s*=\\s*'1","Classic OR injection"),("--\\s*$","SQL comment"),
            ("UNION\\s+SELECT","UNION SELECT"),(";\\s*DROP\\s+TABLE","DROP TABLE"),
            ("SLEEP\\s*\\(","Time-based blind"),("information_schema","Schema enum")]
    out = []
    for i, line in enumerate(code.splitlines(), 1):
        for pat, desc in pats:
            if re.search(pat, line, re.I):
                out.append({"line":i,"issue":desc,"snippet":line.strip()[:100]})
    return out

def scan_xss(html):
    pats = [("<script[^>]*>","Inline script"),("javascript\\s*:","JS URI"),
            ("on\\w+\\s*=\\s*['\"]","Event handler"),("eval\\s*\\(","eval()"),
            ("innerHTML\\s*=","innerHTML assign")]
    out = []
    for i, line in enumerate(html.splitlines(), 1):
        for pat, desc in pats:
            if re.search(pat, line, re.I):
                out.append({"line":i,"issue":desc,"snippet":line.strip()[:100]})
    return out

def anon_text(text, extras=None):
    text = re.sub(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}","[EMAIL]",text)
    text = re.sub(r"\b\d{1,3}(?:\.\d{1,3}){3}\b","[IP]",text)
    text = re.sub(r"\+?[\d\s\-()]{7,15}","[PHONE]",text)
    for k,v in (extras or {}).items(): text = text.replace(k,v)
    return text

def sys_stats():
    try:
        import psutil
        return {"cpu":psutil.cpu_percent(.5),"ram":psutil.virtual_memory().percent,"disk":psutil.disk_usage("/").percent}
    except: return {}

# ══════════════════════════════════════════════════════════════════════════════
# CRM DATABASE (SQLite)
# ══════════════════════════════════════════════════════════════════════════════
def crm_con():
    c = sqlite3.connect(DB_PATH, check_same_thread=False)
    c.execute("PRAGMA foreign_keys = ON"); return c

def crm_init():
    with crm_con() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE, website_url TEXT,
            status TEXT NOT NULL DEFAULT 'Prospect' CHECK(status IN ('Prospect','Active','Done')),
            created_at TEXT DEFAULT (date('now')));
        CREATE TABLE IF NOT EXISTS services (
            id INTEGER PRIMARY KEY AUTOINCREMENT, service_name TEXT NOT NULL,
            description TEXT, base_price REAL NOT NULL DEFAULT 0,
            created_at TEXT DEFAULT (date('now')));
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT, project_name TEXT NOT NULL,
            automation_status TEXT NOT NULL DEFAULT 'Backlog'
                CHECK(automation_status IN ('Backlog','Building','Testing','Done')),
            roi_notes TEXT,
            client_id INTEGER NOT NULL REFERENCES clients(id) ON DELETE RESTRICT,
            service_id INTEGER NOT NULL REFERENCES services(id) ON DELETE RESTRICT,
            created_at TEXT DEFAULT (date('now')));
        """)
crm_init()

def qdf(sql, params=()):
    with crm_con() as c: return pd.read_sql_query(sql, c, params=params)

def crm_run(sql, params=()):
    with crm_con() as c: c.execute(sql, params)

# ══════════════════════════════════════════════════════════════════════════════
# TT MARKET DATA
# ══════════════════════════════════════════════════════════════════════════════
DEFAULT_ND = {
    "cassava":[{"date":"2026-04-01","price":4.00},{"date":"2026-05-01","price":4.50},{"date":"2026-05-15","price":5.56}],
    "carrot":[{"date":"2026-04-01","price":15.00},{"date":"2026-05-01","price":16.50},{"date":"2026-05-15","price":19.84}],
    "tomato":[{"date":"2026-04-01","price":18.00},{"date":"2026-05-01","price":14.00},{"date":"2026-05-15","price":11.02}],
    "pumpkin":[{"date":"2026-04-01","price":3.50},{"date":"2026-05-01","price":3.00},{"date":"2026-05-15","price":3.31}],
    "king fish":[{"date":"2026-04-01","price":65.00},{"date":"2026-05-01","price":60.00},{"date":"2026-05-15","price":55.12}],
    "sweet pepper":[{"date":"2026-04-01","price":22.00},{"date":"2026-05-01","price":25.00},{"date":"2026-05-15","price":23.50}],
    "hot pepper":[{"date":"2026-04-01","price":22.00},{"date":"2026-05-01","price":25.00},{"date":"2026-05-15","price":28.00}],
    "dasheen":[{"date":"2026-04-01","price":6.50},{"date":"2026-05-01","price":7.00},{"date":"2026-05-15","price":7.75}],
}
DEFAULT_MASSY = {
    "flour":[{"date":"2026-04-01","price":17.50},{"date":"2026-05-01","price":16.50},{"date":"2026-05-15","price":15.99}],
    "channa":[{"date":"2026-04-01","price":10.00},{"date":"2026-05-01","price":9.50},{"date":"2026-05-15","price":8.49}],
    "oil":[{"date":"2026-04-01","price":35.00},{"date":"2026-05-01","price":32.00},{"date":"2026-05-15","price":29.99}],
    "rice":[{"date":"2026-04-01","price":30.00},{"date":"2026-05-01","price":29.50},{"date":"2026-05-15","price":28.99}],
    "milk":[{"date":"2026-04-01","price":11.99},{"date":"2026-05-01","price":12.50},{"date":"2026-05-15","price":13.10}],
    "cheese":[{"date":"2026-04-01","price":42.00},{"date":"2026-05-01","price":45.00},{"date":"2026-05-15","price":48.50}],
    "butter":[{"date":"2026-04-01","price":18.00},{"date":"2026-05-01","price":19.50},{"date":"2026-05-15","price":21.00}],
    "salt fish":[{"date":"2026-04-01","price":55.00},{"date":"2026-05-01","price":58.00},{"date":"2026-05-15","price":60.00}],
}
CROP_CAL = {
    1:{"season":"Dry","plant":["Tomato","Sweet Pepper","Lettuce"],"reap":["Watermelon","Cassava","Sorrel"]},
    2:{"season":"Dry","plant":["Tomato","Melongene","Pumpkin"],"reap":["Cassava","Cabbage","Carrots"]},
    3:{"season":"Dry","plant":["Watermelon","Pumpkin","Corn"],"reap":["Tomato","Sweet Pepper","Lettuce"]},
    4:{"season":"Dry","plant":["Cassava","Sweet Potato","Yam"],"reap":["Pumpkin","Corn","Carrot"]},
    5:{"season":"Dry","plant":["Pigeon Peas","Dasheen","Tannia"],"reap":["Cassava","Watermelon"]},
    6:{"season":"Wet","plant":["Cassava","Dasheen","Yam","Corn"],"reap":["Citrus","Melongene","Pumpkin"]},
    7:{"season":"Wet","plant":["Pigeon Peas","Banana","Plantain"],"reap":["Corn","Cucumbers","Pumpkin"]},
    8:{"season":"Wet","plant":["Bodi","Cucumbers","Ochro"],"reap":["Dasheen","Banana","Plantain"]},
    9:{"season":"Wet","plant":["Patchoi","Lettuce","Cabbage"],"reap":["Pigeon Peas","Yam","Ochro"]},
    10:{"season":"Wet","plant":["Tomato","Sweet Pepper","Cabbage"],"reap":["Citrus","Dasheen","Cassava"]},
    11:{"season":"Wet","plant":["Tomato","Carrot","Lettuce"],"reap":["Pigeon Peas","Pumpkin","Cabbage"]},
    12:{"season":"Wet","plant":["Sorrel","Patchoi","Pumpkin"],"reap":["Sorrel","Tomato","Carrot"]},
}
MONTHS = ["January","February","March","April","May","June","July","August","September","October","November","December"]
BOT_CONV = {
    "hello":["Hi! Ready to check some Trinidad grocery prices? 🇹🇹"],
    "hi":["Hey! Ask me about rice, tomato, cheese — or type 'massy' or 'namdevco'."],
    "help":["Try: 'rice', 'tomato', 'massy', 'namdevco', 'calendar', or any item name."],
    "thanks":["You're welcome! Anything else?"],
}
CATEGORIES = ["Produce","Grocery/Dry Goods","Meat & Fish","Dairy","Beverages","Household","Other"]
BILL_TYPES  = ["TNTEC (Electricity)","WASA (Water)","Internet","Mobile Phone","Cable TV","Rent / Mortgage","Gas","Insurance","Other"]

# ══════════════════════════════════════════════════════════════════════════════
# TRANSPARENCY ENGINE DATA
# ══════════════════════════════════════════════════════════════════════════════
POLITE_FILTERS = {
    "I would be happy to help":"Requirement","Could you please consider":"Request for action",
    "It might be worth noting":"Mandatory observation","I'm sorry, I cannot":"Constraint / Refusal",
    "I just wanted to reach out":"Initiation","Feel free to":"Directive",
    "You may want to":"Soft command","With all due respect":"Disagreement incoming",
    "To be honest":"Previously withheld truth","At your earliest convenience":"Urgency disguised",
    "Just checking in":"Follow-up pressure","Per my last email":"Passive aggression",
    "As previously mentioned":"Frustration marker","Going forward":"Policy change",
    "Circle back":"Deferral","Touch base":"Monitoring",
    "Let's take this offline":"Avoidance / Sensitivity","I was wondering if":"Direct request masked",
    "Would it be possible":"Requirement","I understand your concerns":"Dismissal incoming",
    "Just a friendly reminder":"Veiled warning","No worries at all":"Suppressed frustration",
    "Happy to discuss":"Reluctant engagement","We value your feedback":"Deflection",
    "Thank you for your patience":"Acknowledgment of delay",
}
ACTION_TOKENS = {"finish","complete","do","send","fix","build","make","create","stop","start","get",
                 "give","run","review","approve","submit","update","confirm","schedule","meet",
                 "call","respond","reply","deliver","resolve","change","prepare","ensure","check"}
URGENCY_H = ["asap","urgent","immediately","critical","deadline","overdue","now","today","priority"]
URGENCY_M = ["soon","this week","follow up","waiting","pending","reminder","shortly"]
TE_SYSTEMS = {
    "✉ Email / Message": """Analyze this message. Return ONLY raw JSON, no markdown:
{"What they actually want":"blunt sentence","Emotional subtext":"underlying emotion",
"Power dynamic":"who holds leverage","Red flags":"any concerning patterns",
"Response strategy":"tactical 1-2 sentence reply approach"}""",
    "◈ Customer Feedback": """Analyze this feedback. Return ONLY raw JSON, no markdown:
{"Core signal":"real complaint or praise","Emotional state":"customer's state",
"Churn risk":"LOW/MEDIUM/HIGH with reason","Root cause":"what caused this",
"Action item":"most important thing to do"}""",
    "⬡ HR / Review": """Analyze this HR message. Return ONLY raw JSON, no markdown:
{"Real message":"what HR is actually saying","Performance signal":"POSITIVE/NEUTRAL/NEGATIVE",
"Severity":"LOW/MEDIUM/HIGH","Red flags":"legal exposure or PIP patterns",
"Employee action":"what to do right now"}""",
}
TE_MODE_SIGNALS = {
    "✉ Email / Message":{"negative":["overdue","missed","failed","disappointed","concerned","issue","problem","wrong","late"],"positive":["great","appreciate","excellent","thank","good","happy","pleased"]},
    "◈ Customer Feedback":{"negative":["disappointed","terrible","awful","broken","useless","refund","never again","worst","bad","poor"],"positive":["love","amazing","great","excellent","recommend","fantastic","perfect","best"]},
    "⬡ HR / Review":{"negative":["improvement","concern","lacking","below","needs","must","failure","unacceptable","warning","pip"],"positive":["excellent","exceeds","strong","valued","asset","outstanding","commend"]},
}

def decode_input(text):
    raw = text; masks = []
    for phrase, label in POLITE_FILTERS.items():
        if phrase.lower() in text.lower():
            raw = re.sub(re.escape(phrase),"",raw,flags=re.IGNORECASE)
            masks.append((phrase, label))
    raw = re.sub(r"\s{2,}"," ",raw).strip().lstrip(",. ")
    words   = re.findall(r"\b\w+\b", raw.lower())
    actions = list(dict.fromkeys(w for w in words if w in ACTION_TOKENS))
    lower   = text.lower()
    urgency = "LOW"
    if any(s in lower for s in URGENCY_H): urgency = "HIGH"
    elif any(s in lower for s in URGENCY_M): urgency = "MEDIUM"
    score = min(1.0, 0.3 + len(masks)*0.18 + (0.2 if urgency=="HIGH" else 0.1 if urgency=="MEDIUM" else 0))
    sentences = max(len(re.findall(r'[.!?]+', text)), 1)
    return {"decoded":raw or text,"masks":masks,"actions":actions,"urgency":urgency,
            "score":round(score,2),"status":"MASKS DETECTED" if masks else "CLEAN SIGNAL",
            "word_count":len(re.findall(r'\b\w+\b',text)),"sentences":sentences,
            "mask_ratio":round(len(masks)/sentences,2)}

# ══════════════════════════════════════════════════════════════════════════════
# TT MARKET BOT ENGINE
# ══════════════════════════════════════════════════════════════════════════════
def predict_price(logs):
    if len(logs)<2: return None
    prices=[l["price"] for l in logs]; deltas=[prices[i+1]-prices[i] for i in range(len(prices)-1)]
    return round(max(0.01,prices[-1]+sum(deltas)/len(deltas)),2)

def bot_process(text, conv, nd, massy):
    clean = text.lower().strip()
    if any(w in clean for w in ["calendar","season","plant","harvest","reap","grow"]):
        m=now.month; cal=CROP_CAL[m]
        return {"type":"response","text":f"📅 **{cal['season']} Season — {MONTHS[m-1]}**\n\n🌱 **Plant:** {', '.join(cal['plant'])}\n\n🧺 **Harvest:** {', '.join(cal['reap'])}"}
    if any(w in clean for w in ["namdevco","wholesale"]):
        lines=["📊 **NAMDEVCO Wholesale**\n"]
        for item,logs in nd.items():
            if len(logs)>=2:
                curr,prev=logs[-1]["price"],logs[-2]["price"]; d=curr-prev
                arrow=f"🔺+TT${d:.2f}" if d>0 else f"🔻-TT${abs(d):.2f}" if d<0 else "🔹Stable"
                pred=predict_price(logs)
                lines.append(f"• **{item.capitalize()}**: TT${curr:.2f}/kg — {arrow}"+(f" | 🔮~TT${pred:.2f}" if pred else ""))
        return {"type":"response","text":"\n".join(lines)}
    if any(w in clean for w in ["massy","grocery","shopping","supermarket"]):
        lines=["🛒 **Massy Stores**\n"]
        for item,logs in massy.items():
            if len(logs)>=2:
                curr,prev=logs[-1]["price"],logs[-2]["price"]; d=curr-prev
                arrow=f"🔺+TT${d:.2f}" if d>0 else f"🔻-TT${abs(d):.2f}" if d<0 else "🔹Stable"
                pred=predict_price(logs)
                lines.append(f"• **{item.capitalize()}**: TT${curr:.2f} — {arrow}"+(f" | 🔮~TT${pred:.2f}" if pred else ""))
        return {"type":"response","text":"\n".join(lines)}
    all_items={**{k:(v,"namdevco") for k,v in nd.items()},**{k:(v,"massy") for k,v in massy.items()}}
    for item,(logs,source) in all_items.items():
        if item in clean:
            curr=logs[-1]["price"]; prev=logs[-2]["price"] if len(logs)>=2 else curr
            d=curr-prev; pct=(d/prev*100) if prev else 0; pred=predict_price(logs)
            unit="/kg" if source=="namdevco" else ""
            verdict=("⚠️ Prices climbing — buy now." if d>0 else "✅ Price dropped — good time to stock up!" if d<0 else "🔹 Holding steady.")
            txt=(f"💰 **{item.capitalize()}** ({'NAMDEVCO' if source=='namdevco' else 'Massy'})\n\n"
                 f"Current: **TT${curr:.2f}{unit}** | Previous: TT${prev:.2f}{unit}\n"
                 f"Change: {'▲' if d>0 else '▼' if d<0 else '='} TT${abs(d):.2f} ({pct:+.1f}%)\n"
                 +(f"🔮 Predicted: **~TT${pred:.2f}{unit}**\n" if pred else "")+f"\n{verdict}")
            return {"type":"response","text":txt,"item":item,"logs":logs,"source":source}
    for key,responses in conv.items():
        if key in clean: return {"type":"response","text":responses[0]}
    stop={"the","is","a","an","and","how","what","you","are","i","am","want","know","tell","me","about","price","of","for"}
    words=[w for w in clean.split() if w not in stop and len(w)>2]
    if not words: return {"type":"response","text":"Try asking about an item like 'tomato' or 'rice', or type **massy**, **namdevco**, or **calendar**."}
    unknown=max(words,key=len)
    return {"type":"needs_training","text":f"🤔 I don't know about **{unknown}** yet. Want to teach me?","unknown_word":unknown}

# ══════════════════════════════════════════════════════════════════════════════
# SESSION STATE INIT
# ══════════════════════════════════════════════════════════════════════════════
def ss(key, default):
    if key not in st.session_state: st.session_state[key] = default

ss("api_key",""); ss("use_sonnet", False)
# TT Market
ss("tt_conv", load_json(fp("tt_brain.json"),{"conversations":BOT_CONV.copy(),"namdevco":DEFAULT_ND.copy(),"massy":DEFAULT_MASSY.copy()}))
ss("tt_messages",[]); ss("tt_pending",None)
ss("tt_ledger", load_json(fp("tt_ledger.json"),[])); ss("tt_bills", load_json(fp("tt_bills.json"),[]))
# VECTOR OS
ss("health", load_json(fp("health.json"),{"water":0,"caffeine":0,"caffeine_time":None,"sleep_hrs":7,"mood":5,"heart_rate":70,"steps":0,"weight":70.0,"temp":36.6,"last_break":None,"hydration_goal":8,"sleep_running":False,"sleep_start":None}))
ss("tfinance", load_json(fp("tfinance.json"),{"assets":[],"debts":[],"subs":[],"transactions":[],"monthly_income":3800,"monthly_expense":2500}))
ss("goals", load_json(fp("goals.json"),[]))
ss("thoughts", load_json(fp("thoughts.json"),[]))
ss("ideas", load_json(fp("ideas.json"),[]))
ss("social", load_json(fp("social.json"),{"contacts":[],"events":[]}))
ss("decisions", load_json(fp("decisions.json"),[]))
ss("meals", load_json(fp("meals.json"),[]))
ss("meds", load_json(fp("meds.json"),[]))
ss("cal_events", load_json(fp("calendar.json"),{}))
ss("synapse", load_json(fp("synapse.json"),{"identity":None,"trades":[],"nodes":[],"feed":[]}))
# Brief
ss("brief_fin", load_json(fp("brief_fin.json"),{"salary":3800.0,"ttec":450.0,"wasa":180.0,"bmobile":299.0,"internet":350.0}))
ss("brief_bills", load_json(fp("brief_bills.json"),{}))
ss("brief_tasks", load_json(fp("brief_tasks.json"),[]))
ss("brief_notes", load_json(fp("brief_notes.json"),[]))
ss("cal_year", now.year); ss("cal_month", now.month)

# Shortcuts
health = st.session_state.health
synapse = st.session_state.synapse

# ══════════════════════════════════════════════════════════════════════════════
# ALERTS ENGINE
# ══════════════════════════════════════════════════════════════════════════════
def get_alerts():
    a = []
    if health['water']<health.get('hydration_goal',8)*0.5:
        a.append({"icon":"💧","msg":f"Hydration low — {health['water']} glasses","level":"critical"})
    if health['mood']<=3:
        a.append({"icon":"🧠","msg":"Low mood detected","level":"critical"})
    if health['sleep_hrs']<6:
        a.append({"icon":"😴","msg":f"Sleep debt — {health['sleep_hrs']}h logged","level":"critical"})
    if health['temp']>37.5:
        a.append({"icon":"🌡️","msg":f"Elevated temp {health['temp']}°C","level":"critical"})
    if health.get('last_break'):
        try:
            mins=(now-datetime.strptime(health['last_break'],"%Y-%m-%d %H:%M")).seconds//60
            if mins>=20: a.append({"icon":"👁️","msg":f"Vision break due — {mins}m on screen","level":"normal"})
        except: pass
    for med in st.session_state.meds:
        a.append({"icon":"💊","msg":f"{med['name']} — {med['dose']} {med['frequency']}","level":"normal"})
    for c in st.session_state.social.get('contacts',[]):
        if c.get('birthday'):
            try:
                bday=datetime.strptime(f"{now.year}-{c['birthday']}","%Y-%m-%d")
                d=(bday.date()-now.date()).days
                if 0<=d<=7: a.append({"icon":"🎂","msg":f"{c['name']} birthday in {d} day(s)","level":"normal"})
            except: pass
    return a

alerts = get_alerts()
urgent = [x for x in alerts if x['level']=='critical']

# ══════════════════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════════════════
hour = now.hour
greet = "Good Morning" if hour<12 else ("Good Afternoon" if hour<17 else "Good Evening")
dmsg  = {"Monday":"New week.","Tuesday":"Keep going.","Wednesday":"Halfway.","Thursday":"Push through.",
          "Friday":"Finish strong.","Saturday":"Rest well.","Sunday":"Recharge."}.get(now.strftime("%A"),"Stay focused.")
st.markdown(f"""
<div class="vos-header">
    <div><div class="vos-wordmark">VECTOR<span>OS</span></div>
    <div style='font-family:Space Mono,monospace;font-size:0.58rem;color:#333;letter-spacing:2px;margin-top:0.3rem;'>
    TRANSPARENCY · CRM · AI · TT MARKET · PERSONAL OS</div></div>
    <div class="vos-time"><strong>{greet}</strong><br>{now.strftime("%A, %B %d, %Y").upper()}<br>{now.strftime("%H:%M")} AST &nbsp;·&nbsp; {dmsg}</div>
</div>""", unsafe_allow_html=True)

if urgent:
    for u in urgent[:2]:
        st.markdown(f'<div class="alert-strip critical">{u["icon"]} {u["msg"].upper()}<span>● URGENT</span></div>',unsafe_allow_html=True)
elif alerts:
    st.markdown(f'<div class="alert-strip">{alerts[0]["icon"]} {alerts[0]["msg"].upper()}<span>{len(alerts)} ALERT(S)</span></div>',unsafe_allow_html=True)
else:
    st.markdown('<div class="alert-strip clear">✓ ALL SYSTEMS CLEAR<span>● NOMINAL</span></div>',unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(f"""<div style='padding:1rem 0;border-bottom:1px solid #141414;margin-bottom:1rem;'>
    <div style='font-family:Space Mono,monospace;font-size:1.2rem;font-weight:700;color:#fff;letter-spacing:-1px;'>VECTOR<span style="color:#ffaa00;">OS</span></div>
    <div style='font-family:Space Mono,monospace;font-size:0.5rem;color:#{"ff4444" if urgent else "44ff88"};letter-spacing:2px;margin-top:0.3rem;'>
    {"● "+str(len(urgent))+" URGENT" if urgent else "● SYSTEMS CLEAR"}</div></div>""",unsafe_allow_html=True)

    st.markdown("### 🔑 API Key")
    k = st.text_input("Anthropic key",type="password",value=st.session_state.api_key,placeholder="sk-ant-...",key="api_key_input")
    if k: st.session_state.api_key=k
    st.session_state.use_sonnet = st.toggle("Use Sonnet (slower, smarter)", value=False)
    st.markdown("---")

    section = st.radio("SECTION", [
        "🏠 Command Center","🔍 Transparency Engine","🗂 Service Management",
        "⚡ Agentic AI Platform","🇹🇹 TT Market","🖥 VECTOR OS"
    ], label_visibility="visible")
    st.markdown("---")

    if section == "🏠 Command Center":
        page = st.radio("",["Overview","News","Weather"],label_visibility="collapsed")
    elif section == "🔍 Transparency Engine":
        page = "Main"
    elif section == "🗂 Service Management":
        page = st.radio("",["Dashboard","Clients","Services","Projects"],label_visibility="collapsed")
    elif section == "⚡ Agentic AI Platform":
        page = st.radio("",["Overview","Privacy Suite","Security Suite","Intelligence Suite","Operations Suite"],label_visibility="collapsed")
    elif section == "🇹🇹 TT Market":
        page = st.radio("",["Dashboard","Chatbot","Price Tracker","Farmers Calendar","Weather","Ledger","Bills"],label_visibility="collapsed")
    elif section == "🖥 VECTOR OS":
        mode_vos = st.radio("MODE",["Morning Brief","Command","Network"],label_visibility="visible")
        if mode_vos == "Morning Brief":
            page = st.radio("",["Overview","Finances","Tasks & Notes","Calendar","Search"],label_visibility="collapsed")
        elif mode_vos == "Command":
            page = st.radio("",["Dashboard","Health","Nutrition","Goals","Mind","Ideas","Social","Decisions","Life Log"],label_visibility="collapsed")
        else:
            page = st.radio("",["Synapse ID","Value Trades","Nodes","Truth Feed"],label_visibility="collapsed")

    st.markdown("---")
    st.markdown('<div style="font-family:Space Mono,monospace;font-size:0.58rem;color:#333;letter-spacing:2px;">QUICK ACTIONS</div>',unsafe_allow_html=True)
    c1,c2 = st.columns(2)
    if c1.button("💧 Water"):
        health['water']+=1; save_json(fp("health.json"),health); st.rerun()
    if c2.button("👁️ Break"):
        health['last_break']=now.strftime("%Y-%m-%d %H:%M"); save_json(fp("health.json"),health); st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# 🏠 COMMAND CENTER
# ══════════════════════════════════════════════════════════════════════════════
if section == "🏠 Command Center":
    if page == "Overview":
        st.markdown('<div class="s-label">System Overview</div>',unsafe_allow_html=True)
        stats = sys_stats()
        c1,c2,c3,c4,c5 = st.columns(5)
        c1.markdown(f'<div class="stat-block"><div class="stat-val">{health["water"]}/{health.get("hydration_goal",8)}</div><div class="stat-lbl">Hydration</div></div>',unsafe_allow_html=True)
        mc = "g" if health['mood']>=7 else ("a" if health['mood']>=4 else "r")
        c2.markdown(f'<div class="stat-block"><div class="stat-val {mc}">{health["mood"]}/10</div><div class="stat-lbl">Mood</div></div>',unsafe_allow_html=True)
        c3.markdown(f'<div class="stat-block"><div class="stat-val w">{health["sleep_hrs"]}h</div><div class="stat-lbl">Sleep</div></div>',unsafe_allow_html=True)
        c4.markdown(f'<div class="stat-block"><div class="stat-val b">{stats.get("cpu","—")}%</div><div class="stat-lbl">CPU</div></div>',unsafe_allow_html=True)
        c5.markdown(f'<div class="stat-block"><div class="stat-val p">{stats.get("ram","—")}%</div><div class="stat-lbl">RAM</div></div>',unsafe_allow_html=True)
        col_l, col_r = st.columns([2,1], gap="large")
        with col_l:
            st.markdown('<div class="s-label">Headlines</div>',unsafe_allow_html=True)
            for item in get_news("https://www.theguardian.com/world/rss"):
                st.markdown(f'<a href="{item["link"]}" target="_blank" style="text-decoration:none;"><div class="news-card"><div class="news-headline">{item["title"]}</div><div class="news-stamp">{item["pub"]}</div></div></a>',unsafe_allow_html=True)
        with col_r:
            st.markdown('<div class="s-label">Weather · Trinidad</div>',unsafe_allow_html=True)
            w = get_weather()
            if w:
                tc=w['current_condition'][0]['temp_C']; dc=w['current_condition'][0]['weatherDesc'][0]['value']
                fl=w['current_condition'][0]['FeelsLikeC']; hm=w['current_condition'][0]['humidity']
                st.markdown(f'<div class="wx-block"><div class="wx-temp">{tc}°</div><div class="wx-desc">{dc}</div><div style="font-family:Space Mono,monospace;font-size:0.58rem;color:#333;margin-top:0.4rem;">Feels {fl}° · Humidity {hm}%</div></div>',unsafe_allow_html=True)
            else:
                st.markdown('<div class="wx-block"><div class="wx-temp">--°</div><div class="wx-desc">Unavailable</div></div>',unsafe_allow_html=True)
            st.markdown('<div class="s-label">Active Goals</div>',unsafe_allow_html=True)
            ag = [g for g in st.session_state.goals if g['status']=='Active']
            for g in ag[:3]:
                pct=g.get('progress',0)
                st.markdown(f'<div class="v-card v-card-a"><div style="font-size:0.82rem;font-weight:500;">{g["name"]}</div><div class="v-bar-wrap"><div class="v-bar-fill" style="width:{pct}%;"></div></div><div style="font-family:Space Mono,monospace;font-size:0.58rem;color:#333;">{pct}%</div></div>',unsafe_allow_html=True)
            if not ag: st.markdown('<div class="v-card"><span style="color:#333;font-family:Space Mono,monospace;font-size:0.75rem;">No active goals</span></div>',unsafe_allow_html=True)

    elif page == "News":
        st.markdown('<div class="s-label">World News</div>',unsafe_allow_html=True)
        feeds={"World":"https://www.theguardian.com/world/rss","Business":"https://www.theguardian.com/business/rss","Technology":"https://www.theguardian.com/technology/rss"}
        for tab,(label,url) in zip(st.tabs(list(feeds.keys())),feeds.items()):
            with tab:
                for item in get_news(url, 10):
                    st.markdown(f'<a href="{item["link"]}" target="_blank" style="text-decoration:none;"><div class="news-card"><div class="news-headline">{item["title"]}</div><div class="news-stamp">{item["pub"]}</div></div></a>',unsafe_allow_html=True)

    elif page == "Weather":
        st.markdown('<div class="s-label">Weather · Trinidad & Tobago</div>',unsafe_allow_html=True)
        locs={"Trinidad":"Trinidad","Tobago":"Tobago","Port of Spain":"Port+of+Spain,Trinidad","San Fernando":"San+Fernando,Trinidad"}
        sel = st.selectbox("Location",list(locs.keys()),key="cc_wx_loc")
        if st.button("Refresh",key="cc_wx_btn"):
            w=get_weather(locs[sel])
            if w: st.session_state["cc_wx"]=w; st.session_state["cc_wx_sel"]=sel
        if "cc_wx" not in st.session_state:
            w=get_weather(); st.session_state["cc_wx"]=w; st.session_state["cc_wx_sel"]="Trinidad"
        w=st.session_state.get("cc_wx")
        if w:
            cur=w['current_condition'][0]
            c1,c2,c3,c4=st.columns(4)
            c1.markdown(f'<div class="stat-block"><div class="stat-val">{cur["temp_C"]}°</div><div class="stat-lbl">Temp C</div></div>',unsafe_allow_html=True)
            c2.markdown(f'<div class="stat-block"><div class="stat-val w">{cur["FeelsLikeC"]}°</div><div class="stat-lbl">Feels Like</div></div>',unsafe_allow_html=True)
            c3.markdown(f'<div class="stat-block"><div class="stat-val b">{cur["humidity"]}%</div><div class="stat-lbl">Humidity</div></div>',unsafe_allow_html=True)
            c4.markdown(f'<div class="stat-block"><div class="stat-val p">{cur["windspeedKmph"]}km/h</div><div class="stat-lbl">Wind</div></div>',unsafe_allow_html=True)
            st.markdown(f'<div class="v-card" style="text-align:center;padding:1.5rem;margin-top:1rem;"><div style="font-family:Space Mono,monospace;font-size:0.9rem;color:#ffaa00;letter-spacing:3px;">{cur["weatherDesc"][0]["value"].upper()}</div></div>',unsafe_allow_html=True)
            st.markdown('<div class="s-label">3-Day Forecast</div>',unsafe_allow_html=True)
            dcols=st.columns(3)
            for i,day in enumerate(w["weather"][:3]):
                label=["Today","Tomorrow",datetime.strptime(day["date"],"%Y-%m-%d").strftime("%A")][i]
                dcols[i].markdown(f'<div class="stat-block"><div style="font-family:Space Mono,monospace;font-size:0.6rem;color:#444;letter-spacing:2px;margin-bottom:0.5rem;">{label.upper()}</div><div class="stat-val" style="font-size:1.4rem;">{day["maxtempC"]}°</div><div class="stat-lbl">{day["mintempC"]}° low</div></div>',unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# 🔍 TRANSPARENCY ENGINE
# ══════════════════════════════════════════════════════════════════════════════
elif section == "🔍 Transparency Engine":
    st.markdown('<div class="s-label">Radical Transparency Engine — Decode what is actually being said</div>',unsafe_allow_html=True)
    mode_te = st.radio("Mode",list(TE_SYSTEMS.keys()),horizontal=True,key="te_mode")
    user_input_te = st.text_area("Paste message here",height=140,key="te_input",
        placeholder="Paste an email, feedback, or HR message...")
    col_btn, col_tog = st.columns([3,1])
    run_te = col_btn.button("▶ DECODE TRANSMISSION",key="te_run")
    use_ai_te = col_tog.toggle("AI Analysis",value=False,help="Uses API credits")

    if run_te and user_input_te.strip():
        result = decode_input(user_input_te)
        urgency_color={"HIGH":"#ff4444","MEDIUM":"#ffaa00","LOW":"#44ff88"}
        st.markdown('<div class="s-label">Rule Engine // Transparency Scan</div>',unsafe_allow_html=True)
        c1,c2,c3=st.columns(3)
        c1.markdown(f'<div class="stat-block"><div class="stat-val" style="font-size:1.2rem;">{result["status"].replace(" ","<br>")}</div><div class="stat-lbl">Status</div></div>',unsafe_allow_html=True)
        c2.markdown(f'<div class="stat-block"><div class="stat-val" style="color:{urgency_color[result["urgency"]]};">{result["urgency"]}</div><div class="stat-lbl">Urgency</div></div>',unsafe_allow_html=True)
        c3.markdown(f'<div class="stat-block"><div class="stat-val">{int(result["score"]*100)}%</div><div class="stat-lbl">Transparency</div></div>',unsafe_allow_html=True)
        pct=int(result["score"]*100)
        st.markdown(f'<div class="v-card" style="margin-top:0.5rem;"><div style="font-family:Space Mono,monospace;font-size:0.6rem;color:#444;margin-bottom:0.5rem;">TRANSPARENCY INDEX</div><div class="v-bar-wrap"><div class="v-bar-fill" style="width:{pct}%;"></div></div></div>',unsafe_allow_html=True)
        if result["actions"]:
            tags=" ".join(f'<span class="vpill vpill-a">{a.upper()}</span>' for a in result["actions"])
            st.markdown(f'<div class="v-card" style="margin-top:0.5rem;"><div class="stat-lbl" style="margin-bottom:0.5rem;">ACTION SIGNALS</div>{tags}</div>',unsafe_allow_html=True)
        if result["masks"]:
            st.markdown(f'<div class="s-label">Social Masks Stripped ({len(result["masks"])})</div>',unsafe_allow_html=True)
            with st.expander("View mask breakdown",expanded=True):
                for phrase,label in result["masks"]:
                    ca,cb=st.columns([3,2])
                    ca.markdown(f'<span style="color:#ff4444;text-decoration:line-through;font-size:0.85rem;opacity:0.7;">"{phrase}"</span>',unsafe_allow_html=True)
                    cb.markdown(f'<span style="color:#ffaa00;font-size:0.85rem;">→ {label}</span>',unsafe_allow_html=True)
        st.markdown(f'<div class="v-card v-card-a" style="margin-top:0.5rem;"><div class="stat-lbl" style="margin-bottom:0.5rem;color:#ffaa00;">DECODED SIGNAL</div><div style="font-family:Space Grotesk,sans-serif;font-size:0.95rem;color:#ffaa00;line-height:1.7;">{result["decoded"] or "No residual signal."}</div></div>',unsafe_allow_html=True)

        # Deep analysis
        lower=user_input_te.lower()
        signals=TE_MODE_SIGNALS[mode_te]
        neg=[w for w in signals["negative"] if w in lower]
        pos=[w for w in signals["positive"] if w in lower]
        sentiment="NEGATIVE" if neg and not pos else "POSITIVE" if pos and not neg else "MIXED" if neg and pos else "NEUTRAL"
        scol={"NEGATIVE":"#ff4444","POSITIVE":"#44ff88","MIXED":"#ffaa00","NEUTRAL":"#888"}[sentiment]
        complexity="HIGH" if result["word_count"]>80 else "MEDIUM" if result["word_count"]>30 else "LOW"
        st.markdown('<div class="s-label">Deep Signal Analysis</div>',unsafe_allow_html=True)
        dc1,dc2=st.columns(2)
        dc1.markdown(f'<div class="stat-block"><div class="stat-val" style="color:{scol};font-size:1.2rem;">{sentiment}</div><div class="stat-lbl">Sentiment</div></div>',unsafe_allow_html=True)
        dc2.markdown(f'<div class="stat-block"><div class="stat-val w" style="font-size:1.2rem;">{complexity}</div><div class="stat-lbl">Complexity ({result["word_count"]} words)</div></div>',unsafe_allow_html=True)
        if neg: st.markdown(f'<div class="v-card v-card-r"><div class="stat-lbl">NEGATIVE SIGNALS</div><div style="color:#ff4444;font-family:Space Mono,monospace;font-size:0.75rem;margin-top:0.3rem;">{" · ".join(neg).upper()}</div></div>',unsafe_allow_html=True)
        if pos: st.markdown(f'<div class="v-card v-card-g"><div class="stat-lbl">POSITIVE SIGNALS</div><div style="color:#44ff88;font-family:Space Mono,monospace;font-size:0.75rem;margin-top:0.3rem;">{" · ".join(pos).upper()}</div></div>',unsafe_allow_html=True)

        if use_ai_te:
            st.markdown('<div class="s-label">AI Deep Analysis // Haiku Engine</div>',unsafe_allow_html=True)
            with st.spinner("Processing..."):
                try:
                    r = ai_call(user_input_te, TE_SYSTEMS[mode_te], "claude-haiku-4-5-20251001", 1000)
                    clean=r.replace("```json","").replace("```","").strip()
                    ai_data=json.loads(clean)
                    rfl={"red flags","churn risk","severity"}
                    for k,v in ai_data.items():
                        color="#ff6b8a" if k.lower() in rfl else "#ffaa00" if "action" in k.lower() or "strategy" in k.lower() or "employee" in k.lower() else "#aaa"
                        st.markdown(f'<div class="v-card" style="margin-bottom:4px;"><div class="stat-lbl">{k.upper()}</div><div style="font-size:0.88rem;color:{color};line-height:1.6;margin-top:0.4rem;">{v}</div></div>',unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"AI error: {e}")

# ══════════════════════════════════════════════════════════════════════════════
# 🗂 SERVICE MANAGEMENT
# ══════════════════════════════════════════════════════════════════════════════
elif section == "🗂 Service Management":
    STATUS_COLORS={"Prospect":"#4488ff","Active":"#44ff88","Done":"#444","Backlog":"#ffaa00","Building":"#aa88ff","Testing":"#00d4ff"}

    if page == "Dashboard":
        st.markdown('<div class="s-label">CRM Dashboard</div>',unsafe_allow_html=True)
        clients=qdf("SELECT * FROM clients"); services=qdf("SELECT * FROM services")
        projects=qdf("SELECT p.*,c.name AS client_name,s.service_name FROM projects p JOIN clients c ON p.client_id=c.id JOIN services s ON p.service_id=s.id")
        c1,c2,c3,c4=st.columns(4)
        c1.metric("Clients",len(clients))
        c2.metric("Services",len(services))
        c3.metric("Projects",len(projects))
        c4.metric("Done",len(projects[projects.automation_status=="Done"]) if not projects.empty else 0)
        if not projects.empty:
            col_l,col_r=st.columns([3,2])
            with col_l:
                ps=projects["automation_status"].value_counts().reset_index(); ps.columns=["Status","Count"]
                fig=px.bar(ps,x="Status",y="Count",color="Status",color_discrete_map=STATUS_COLORS,text="Count",title="Projects by Stage")
                fig.update_layout(showlegend=False,height=300,paper_bgcolor="#0e0e0e",plot_bgcolor="#0e0e0e",font_color="#f0f0f0")
                st.plotly_chart(fig,use_container_width=True)
            with col_r:
                cp=projects.groupby("client_name").size().reset_index(name="Projects")
                fig2=px.pie(cp,names="client_name",values="Projects",title="Projects per Client",hole=0.45)
                fig2.update_layout(height=300,paper_bgcolor="#0e0e0e",font_color="#f0f0f0")
                st.plotly_chart(fig2,use_container_width=True)
            st.markdown('<div class="s-label">All Projects</div>',unsafe_allow_html=True)
            for _,row in projects.iterrows():
                sc=STATUS_COLORS.get(row["automation_status"],"#444")
                st.markdown(f'<div class="v-card v-card-a"><div style="display:flex;justify-content:space-between;"><span style="font-weight:600;">{row["project_name"]}</span><span class="vpill" style="background:{sc}22;color:{sc};border:1px solid {sc}44;">{row["automation_status"]}</span></div><div style="font-family:Space Mono,monospace;font-size:0.6rem;color:#444;margin-top:0.3rem;">👤 {row["client_name"]} · 🛠 {row["service_name"]}</div></div>',unsafe_allow_html=True)
        else:
            st.info("Add clients, services, and projects to see data here.")

    elif page == "Clients":
        st.markdown('<div class="s-label">Client Management</div>',unsafe_allow_html=True)
        t1,t2,t3,t4=st.tabs(["View All","➕ Add","✏️ Edit","🗑 Delete"])
        with t1:
            df=qdf("SELECT id,name,email,website_url,status,created_at FROM clients ORDER BY name")
            if not df.empty:
                srch=st.text_input("Search",key="cl_srch")
                if srch: df=df[df["name"].str.contains(srch,case=False)|df["email"].str.contains(srch,case=False)]
                st.dataframe(df,use_container_width=True,hide_index=True)
                c1,c2,c3=st.columns(3)
                for status,col in zip(["Prospect","Active","Done"],[c1,c2,c3]):
                    col.metric(status,len(df[df["status"]==status]))
            else: st.info("No clients yet.")
        with t2:
            with st.form("add_client"):
                c1,c2=st.columns(2)
                name=c1.text_input("Name *"); email=c1.text_input("Email *")
                website=c2.text_input("Website"); status=c2.selectbox("Status",["Prospect","Active","Done"])
                if st.form_submit_button("Add Client",type="primary"):
                    if name and email:
                        try:
                            crm_run("INSERT INTO clients (name,email,website_url,status) VALUES (?,?,?,?)",(name,email,website or None,status))
                            st.success(f"✅ '{name}' added!"); st.rerun()
                        except sqlite3.IntegrityError: st.error("Email already in use.")
                    else: st.error("Name and email required.")
        with t3:
            df2=qdf("SELECT id,name FROM clients ORDER BY name")
            if not df2.empty:
                cmap=dict(zip(df2["name"],df2["id"])); sel=st.selectbox("Select",list(cmap.keys()),key="cl_edit_sel")
                row=qdf("SELECT * FROM clients WHERE id=?",( cmap[sel],)).iloc[0]
                with st.form("edit_client"):
                    c1,c2=st.columns(2)
                    nn=c1.text_input("Name",value=row["name"]); ne=c1.text_input("Email",value=row["email"])
                    nw=c2.text_input("Website",value=row["website_url"] or "")
                    statuses=["Prospect","Active","Done"]
                    ns=c2.selectbox("Status",statuses,index=statuses.index(row["status"]))
                    if st.form_submit_button("Save",type="primary"):
                        try:
                            crm_run("UPDATE clients SET name=?,email=?,website_url=?,status=? WHERE id=?",(nn,ne,nw or None,ns,cmap[sel]))
                            st.success("✅ Updated!"); st.rerun()
                        except sqlite3.IntegrityError: st.error("Email already used.")
            else: st.info("No clients yet.")
        with t4:
            df3=qdf("SELECT id,name FROM clients ORDER BY name")
            if not df3.empty:
                cmap3=dict(zip(df3["name"],df3["id"])); sel3=st.selectbox("Select to delete",list(cmap3.keys()),key="cl_del_sel")
                pc=qdf("SELECT COUNT(*) AS n FROM projects WHERE client_id=?",(cmap3[sel3],)).iloc[0]["n"]
                if pc>0: st.warning(f"⚠️ {sel3} has {pc} project(s). Delete those first.")
                else:
                    st.warning(f"Delete **{sel3}**?")
                    if st.button("🗑 Delete",key="cl_del_btn"):
                        crm_run("DELETE FROM clients WHERE id=?",(cmap3[sel3],)); st.success("Deleted."); st.rerun()
            else: st.info("No clients.")

    elif page == "Services":
        st.markdown('<div class="s-label">Service Management</div>',unsafe_allow_html=True)
        t1,t2,t3,t4=st.tabs(["View All","➕ Add","✏️ Edit","🗑 Delete"])
        with t1:
            df=qdf("SELECT id,service_name,description,base_price,created_at FROM services ORDER BY service_name")
            if not df.empty:
                st.dataframe(df,use_container_width=True,hide_index=True)
                fig=px.bar(df.sort_values("base_price",ascending=False),x="service_name",y="base_price",title="Base Price by Service",color="base_price",color_continuous_scale=["#4488ff","#ffaa00"])
                fig.update_layout(height=280,paper_bgcolor="#0e0e0e",plot_bgcolor="#0e0e0e",font_color="#f0f0f0",coloraxis_showscale=False)
                st.plotly_chart(fig,use_container_width=True)
            else: st.info()
