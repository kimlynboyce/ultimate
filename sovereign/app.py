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
now = (datetime.now(timezone.utc) - timedelta(hours=4)).replace(tzinfo=None)
DATA_DIR = "vos_data"; os.makedirs(DATA_DIR, exist_ok=True)
DB_PATH = os.path.join(DATA_DIR, "crm.db")
def fp(name): return os.path.join(DATA_DIR, name)

# ══════════════════════════════════════════════════════════════════════════════
# CSS — Unified VECTOR OS Dark System
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Space+Mono:wght@400;700&family=Syne:wght@700;800&display=swap');

/* ── AURORA BOREALIS THEME ── */
:root {
    --primary: #00ffcc; /* aurora teal */
    --violet: #aa44ff; /* aurora violet */
    --pink: #ff44aa; /* aurora pink */
    --gold: #ffe066; /* aurora gold */
    --danger: #ff4477; /* aurora red */
    --bg: #020810; /* arctic night */
    --bg2: #05101e; /* card bg */
    --bg3: #071628; /* sidebar */
    --border: #0c2340; /* border */
    --border2: #112d50; /* card border */
    --text: #e0f4ff; /* cool white */
    --dim: #2a5070; /* dim text */
    --dim2: #163050; /* very dim */
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
def dec(ct, pw): return Fernet(_fkey(pw)).decrypt(ct.encode()).decode()

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
                          "link": l.text if l is not None else "#",
                          "pub": p.text[:22] if p is not None else ""})
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
BILL_TYPES = ["TNTEC (Electricity)","WASA (Water)","Internet","Mobile Phone","Cable TV","Rent / Mortgage","Gas","Insurance","Other"]

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
    words = re.findall(r"\b\w+\b", raw.lower())
    actions = list(dict.fromkeys(w for w in words if w in ACTION_TOKENS))
    lower = text.lower()
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
ss("mode_vos", "Morning Brief")

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
dmsg = {"Monday":"New week.","Tuesday":"Keep going.","Wednesday":"Halfway.","Thursday":"Push through.",
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
        mode_vos = st.radio("MODE",["Morning Brief","Command","Network"],label_visibility="visible",key="mode_vos")
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
            w=get_weather()
            if w: st.session_state["cc_wx"]=w; st.session_state["cc_wx_sel"]="Trinidad"
        w=st.session_state.get("cc_wx")
        if w:
            cur=w['current_condition'][0]
            c1,c2,c3,c4=st.columns(4)
            c1.markdown(f'<div class="stat-block"><div class="stat-val">{cur["temp_C"]}°</div><div class="stat-lbl">Temp C</div></div>',unsafe_allow_html=True)
            c2.markdown(f'<div class="stat-block"><div class="stat-val w">{cur["FeelsLikeC"]}°</div><div class="stat-lbl">Feels Like</div></div>',unsafe_allow_html=True)
            c3.markdown(f'<div class="stat-block"><div class="stat-val b">{cur["humidity"]}%</div><div class="stat-lbl">Humidity</div></div>',unsafe_allow_html=True)
            c4.markdown(f'<div class="stat-block"><div class="stat-val p">{cur["windspeedKmph"]}km/h</div><div class="stat-lbl">Wind</div></div>',unsafe_allow_html=True)
            st.markdown(f'<div class="v-card" style="text-align:center;padding:1.5rem;margin-top:1rem;"><div style="font-family:Space Mono,monospace;font-size:0.9rem;color:var(--primary);letter-spacing:3px;">{cur["weatherDesc"][0]["value"].upper()}</div></div>',unsafe_allow_html=True)
            st.markdown('<div class="s-label">3-Day Forecast</div>',unsafe_allow_html=True)
            dcols=st.columns(3)
            for i,day in enumerate(w["weather"][:3]):
                label=["Today","Tomorrow",datetime.strptime(day["date"],"%Y-%m-%d").strftime("%A")][i]
                dcols[i].markdown(f'<div class="stat-block"><div style="font-family:Space Mono,monospace;font-size:0.6rem;color:var(--dim);letter-spacing:2px;margin-bottom:0.5rem;">{label.upper()}</div><div class="stat-val" style="font-size:1.4rem;">{day["maxtempC"]}°</div><div class="stat-lbl">{day["mintempC"]}° low</div></div>',unsafe_allow_html=True)
        else:
            st.markdown('<div class="wx-block"><div class="wx-temp">--°</div><div class="wx-desc">Weather unavailable — check connection</div></div>',unsafe_allow_html=True)

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
            else: st.info("No services yet.")
        with t2:
            with st.form("add_svc"):
                c1,c2=st.columns(2)
                sn=c1.text_input("Service Name *"); sd=c1.text_area("Description",height=80)
                sp=c2.number_input("Base Price ($)",min_value=0.0,step=50.0)
                if st.form_submit_button("Add Service",type="primary"):
                    if sn:
                        crm_run("INSERT INTO services (service_name,description,base_price) VALUES (?,?,?)",(sn,sd or None,sp))
                        st.success(f"✅ '{sn}' added!"); st.rerun()
        with t3:
            df2=qdf("SELECT id,service_name FROM services ORDER BY service_name")
            if not df2.empty:
                smap=dict(zip(df2["service_name"],df2["id"])); sel=st.selectbox("Select",list(smap.keys()),key="svc_edit_sel")
                row=qdf("SELECT * FROM services WHERE id=?",(smap[sel],)).iloc[0]
                with st.form("edit_svc"):
                    c1,c2=st.columns(2)
                    nn=c1.text_input("Name",value=row["service_name"]); nd=c1.text_area("Description",value=row["description"] or "")
                    np_=c2.number_input("Base Price",value=float(row["base_price"]),min_value=0.0,step=50.0)
                    if st.form_submit_button("Save",type="primary"):
                        crm_run("UPDATE services SET service_name=?,description=?,base_price=? WHERE id=?",(nn,nd or None,np_,smap[sel]))
                        st.success("✅ Updated!"); st.rerun()
        with t4:
            df3=qdf("SELECT id,service_name FROM services ORDER BY service_name")
            if not df3.empty:
                smap3=dict(zip(df3["service_name"],df3["id"])); sel3=st.selectbox("Select to delete",list(smap3.keys()),key="svc_del_sel")
                pc=qdf("SELECT COUNT(*) AS n FROM projects WHERE service_id=?",(smap3[sel3],)).iloc[0]["n"]
                if pc>0: st.warning(f"⚠️ Used in {pc} project(s). Remove those first.")
                else:
                    if st.button("🗑 Delete",key="svc_del_btn"):
                        crm_run("DELETE FROM services WHERE id=?",(smap3[sel3],)); st.success("Deleted."); st.rerun()

    elif page == "Projects":
        STATUSES=["Backlog","Building","Testing","Done"]
        def load_projects():
            return qdf("SELECT p.id,p.project_name,p.automation_status,p.roi_notes,c.name AS client,s.service_name AS service,p.client_id,p.service_id,p.created_at FROM projects p JOIN clients c ON p.client_id=c.id JOIN services s ON p.service_id=s.id ORDER BY p.created_at DESC")
        st.markdown('<div class="s-label">Project Management</div>',unsafe_allow_html=True)
        t1,t2,t3,t4=st.tabs(["View All","➕ Add","✏️ Edit","🗑 Delete"])
        with t1:
            df=load_projects()
            if not df.empty:
                c1,c2=st.columns(2)
                fs=c1.multiselect("Filter Stage",STATUSES,default=STATUSES,key="proj_fs")
                fc_df=qdf("SELECT DISTINCT name FROM clients ORDER BY name")
                fc_opts=["All"]+fc_df["name"].tolist() if not fc_df.empty else ["All"]
                fc=c2.selectbox("Filter Client",fc_opts,key="proj_fc")
                filt=df[df["automation_status"].isin(fs)]
                if fc!="All": filt=filt[filt["client"]==fc]
                for _,row in filt.iterrows():
                    sc=STATUS_COLORS.get(row["automation_status"],"#444")
                    st.markdown(f'<div class="v-card v-card-a"><div style="display:flex;justify-content:space-between;"><span style="font-weight:600;">{row["project_name"]}</span><span class="vpill" style="background:{sc}22;color:{sc};border:1px solid {sc}44;">{row["automation_status"]}</span></div><div style="font-family:Space Mono,monospace;font-size:0.6rem;color:#444;margin-top:0.3rem;">👤 {row["client"]} · 🛠 {row["service"]}{(" · "+row["roi_notes"]) if row["roi_notes"] else ""}</div></div>',unsafe_allow_html=True)
            else: st.info("No projects yet.")
        with t2:
            cdf=qdf("SELECT id,name FROM clients ORDER BY name"); sdf=qdf("SELECT id,service_name FROM services ORDER BY service_name")
            if cdf.empty or sdf.empty: st.warning("Need at least one client and one service first.")
            else:
                cmap=dict(zip(cdf["name"],cdf["id"])); smap=dict(zip(sdf["service_name"],sdf["id"]))
                with st.form("add_proj"):
                    c1,c2=st.columns(2)
                    pn=c1.text_input("Project Name *"); pc2=c1.selectbox("Client",list(cmap.keys()))
                    ps=c2.selectbox("Stage",STATUSES); psv=c2.selectbox("Service",list(smap.keys()))
                    proi=st.text_area("ROI Notes",height=60)
                    if st.form_submit_button("Create Project",type="primary"):
                        if pn:
                            crm_run("INSERT INTO projects (project_name,automation_status,roi_notes,client_id,service_id) VALUES (?,?,?,?,?)",(pn,ps,proi or None,cmap[pc2],smap[psv]))
                            st.success(f"✅ '{pn}' created!"); st.rerun()
        with t3:
            df2=load_projects()
            if not df2.empty:
                pmap=dict(zip(df2["project_name"]+" ("+df2["client"]+")",df2["id"])); sel=st.selectbox("Select",list(pmap.keys()),key="proj_edit_sel")
                row=df2[df2["id"]==pmap[sel]].iloc[0]
                cdf2=qdf("SELECT id,name FROM clients ORDER BY name"); sdf2=qdf("SELECT id,service_name FROM services ORDER BY service_name")
                cmap2=dict(zip(cdf2["name"],cdf2["id"])); smap2=dict(zip(sdf2["service_name"],sdf2["id"]))
                with st.form("edit_proj"):
                    c1,c2=st.columns(2)
                    nn=c1.text_input("Name",value=row["project_name"])
                    cur_c=next((k for k,v in cmap2.items() if v==row["client_id"]),list(cmap2.keys())[0])
                    nc=c1.selectbox("Client",list(cmap2.keys()),index=list(cmap2.keys()).index(cur_c))
                    ns=c2.selectbox("Stage",STATUSES,index=STATUSES.index(row["automation_status"]))
                    cur_s=next((k for k,v in smap2.items() if v==row["service_id"]),list(smap2.keys())[0])
                    nsv=c2.selectbox("Service",list(smap2.keys()),index=list(smap2.keys()).index(cur_s))
                    nroi=st.text_area("ROI Notes",value=row["roi_notes"] or "")
                    if st.form_submit_button("Save",type="primary"):
                        crm_run("UPDATE projects SET project_name=?,automation_status=?,roi_notes=?,client_id=?,service_id=? WHERE id=?",(nn,ns,nroi or None,cmap2[nc],smap2[nsv],pmap[sel]))
                        st.success("✅ Updated!"); st.rerun()
        with t4:
            df3=load_projects()
            if not df3.empty:
                pmap3=dict(zip(df3["project_name"]+" ("+df3["client"]+")",df3["id"])); sel3=st.selectbox("Select to delete",list(pmap3.keys()),key="proj_del_sel")
                if st.button("🗑 Delete Project",key="proj_del_btn"):
                    crm_run("DELETE FROM projects WHERE id=?",(pmap3[sel3],)); st.success("Deleted."); st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# ⚡ AGENTIC AI PLATFORM
# ══════════════════════════════════════════════════════════════════════════════
elif section == "⚡ Agentic AI Platform":
    if page == "Overview":
        st.markdown('<div class="s-label">50-Module Agentic AI Platform</div>',unsafe_allow_html=True)
        stats=sys_stats()
        c1,c2,c3,c4,c5=st.columns(5)
        c1.metric("Modules","50"); c2.metric("CPU",f"{stats.get('cpu','—')}%"); c3.metric("RAM",f"{stats.get('ram','—')}%")
        c4.metric("Disk",f"{stats.get('disk','—')}%"); c5.metric("Status","🟢 Online")
        modules={"🔒 Privacy":[(1,"Hardware Decoupling"),(2,"Protocol Masking"),(4,"Zero-Knowledge Storage"),(5,"Shadow VPN"),(6,"MAC Randomization"),(7,"OS Hardening"),(8,"Air-Gapped Syncing"),(9,"Power Independence"),(10,"Signal Awareness"),(12,"Metadata Scrubbing"),(14,"Email Aliasing"),(18,"Browser Fingerprint"),(19,"Right-to-be-Forgotten"),(20,"Credential Rotation"),(25,"Traffic Defense"),(29,"ID Decoupling")],
                 "🛡️ Security":[(11,"Synthetic Personas"),(16,"Social Eng Defense"),(17,"Deepfake Verify"),(21,"API Security"),(22,"TLS Audit"),(24,"SQL Injection Audit"),(27,"Smart Contract Audit"),(30,"XSS Prevention"),(44,"Data Honeypots"),(45,"Kill Switch")],
                 "🧠 Intelligence":[(26,"Dark Data"),(31,"Real-Time Monitor"),(32,"Adversarial Testing"),(33,"TT Market Predictions"),(34,"Sentiment Analysis"),(35,"Bias Detection"),(36,"Strategic Redacting"),(37,"Competitor Benchmark"),(38,"Safety Mapping"),(39,"Scarcity Alerts"),(40,"AI Evolution")],
                 "⚙️ Operations":[(3,"Local LLM Bridge"),(15,"Financial Tracker"),(28,"ISP Bypass"),(41,"Task Scheduling"),(42,"Ghost-Writing"),(43,"Self-Healing Servers"),(46,"Cross-Platform Sync"),(47,"Translation"),(48,"Neural Masking"),(49,"Mesh Networking"),(50,"Continuous Evolution")]}
        for suite,mods in modules.items():
            with st.expander(f"{suite} ({len(mods)} modules)"):
                cols=st.columns(3)
                for i,(n,name) in enumerate(mods):
                    cols[i%3].markdown(f'`#{n}` {name}')

    elif page == "Privacy Suite":
        st.markdown('<div class="s-label">Privacy & Anonymity Suite</div>',unsafe_allow_html=True)
        t=st.tabs(["#6 MAC Randomization","#4 Encryption","#12 Metadata Scrub","#14 Aliases","#20 Credentials","#19 RTBF"])
        with t[0]:
            iface=st.text_input("Interface",value="eth0",key="priv_mac_if")
            if st.button("Generate MAC",key="priv_mac_btn"):
                st.session_state["nmac"]=rand_mac()
            if "nmac" in st.session_state:
                st.success(f"MAC: `{st.session_state['nmac']}`")
                for osn,cmd in {"Linux":f"sudo ip link set {iface} down && sudo ip link set {iface} address {st.session_state['nmac']} && sudo ip link set {iface} up","macOS":f"sudo ifconfig {iface} ether {st.session_state['nmac']}","Windows":f'Set-NetAdapter -Name "{iface}" -MacAddress "{st.session_state["nmac"]}"'}.items():
                    st.markdown(f"**{osn}**"); st.markdown(f'<div class="cb">{cmd}</div>',unsafe_allow_html=True)
        with t[1]:
            e1,e2=st.columns(2)
            with e1:
                ep=st.text_input("Passphrase",type="password",key="enc_p"); ei=st.text_area("Plaintext",height=120,key="enc_i")
                if st.button("Encrypt",key="enc_btn") and ep and ei:
                    try: ct=enc(ei,ep); st.text_area("Ciphertext:",value=ct,height=120,key="enc_o"); st.download_button("Download",ct,file_name="encrypted.txt",key="dl_enc")
                    except Exception as ex: st.error(str(ex))
            with e2:
                dp=st.text_input("Passphrase",type="password",key="dec_p"); di=st.text_area("Ciphertext",height=120,key="dec_i")
                if st.button("Decrypt",key="dec_btn") and dp and di:
                    try: st.text_area("Plaintext:",value=dec(di.strip(),dp),height=120,key="dec_o")
                    except: st.error("❌ Wrong passphrase or corrupted data.")
        with t[2]:
            ups=st.file_uploader("Upload images",type=["jpg","jpeg","png"],accept_multiple_files=True,key="meta_up")
            if ups:
                for uf in ups:
                    raw=uf.read()
                    try:
                        from PIL import Image; from PIL.ExifTags import TAGS
                        img=Image.open(io.BytesIO(raw)); exif=img._getexif()
                        meta={TAGS.get(k,k):str(v) for k,v in (exif or {}).items()}
                        c1,c2=st.columns(2)
                        with c1:
                            st.markdown(f"**{uf.name} metadata:**")
                            for k,v in list(meta.items())[:8]: st.markdown(f"• {k}: {str(v)[:60]}")
                            if not meta: st.info("No EXIF found")
                        with c2:
                            fmt="PNG" if uf.name.lower().endswith(".png") else "JPEG"
                            clean_img=Image.new(img.mode,img.size); clean_img.putdata(list(img.getdata()))
                            buf=io.BytesIO(); clean_img.save(buf,format=fmt); buf.seek(0)
                            st.success(f"Stripped: {len(raw):,} → {len(buf.getvalue()):,} bytes")
                            st.download_button(f"Download clean {uf.name}",buf.getvalue(),file_name=f"clean_{uf.name}",key=f"dl_clean_{uf.name}")
                    except Exception as e: st.error(str(e))
        with t[3]:
            base=st.text_input("Base name",key="alias_base"); svc=st.text_input("Service",key="alias_svc")
            dom=st.selectbox("Domain",["simplelogin.io","addy.io","duck.com"],key="alias_dom")
            if st.button("Generate Alias",key="alias_btn") and base and svc:
                alias=f"{base}+{secrets.token_hex(4)}@{dom}"
                if "aliases" not in st.session_state: st.session_state["aliases"]=[]
                st.session_state["aliases"].append({"alias":alias,"service":svc,"date":str(date.today())})
                st.success(f"`{alias}`")
            for a in st.session_state.get("aliases",[]): st.markdown(f"✅ `{a['alias']}` → {a['service']}")
        with t[4]:
            pl=st.slider("Length",16,64,24,key="cred_pl"); sym=st.checkbox("Symbols",True,key="cred_sym"); n=st.number_input("Count",1,10,3,key="cred_n")
            if st.button("Generate",key="cred_btn"):
                st.session_state["creds"]=[gen_pwd(pl,sym) for _ in range(int(n))]
            for p in st.session_state.get("creds",[]):
                lbl,col=pwd_strength(p)
                st.markdown(f'`{p}` <span style="color:{col};font-size:0.8rem;">● {lbl}</span>',unsafe_allow_html=True)
        with t[5]:
            c1,c2=st.columns(2)
            rname=c1.text_input("Your name",key="rtbf_name"); rco=c1.text_input("Company",key="rtbf_co")
            remail=c2.text_input("Your email",key="rtbf_email"); rlaw=c2.radio("Law",["GDPR","CCPA","General"],horizontal=True,key="rtbf_law")
            if st.button("Generate RTBF Letter",key="rtbf_btn") and rname and rco:
                ref={"GDPR":"Articles 17 & 21 GDPR","CCPA":"Cal. Civ. Code §1798.105","General":"applicable data protection law"}[rlaw]
                dl={"GDPR":"one calendar month","CCPA":"45 days","General":"30 days"}[rlaw]
                letter=f"{rname}\n{remail}\n{now.strftime('%B %d, %Y')}\n\nData Protection Officer\n{rco}\n\nRe: Data Deletion Request Under {rlaw}\n\nI formally exercise my rights under {ref}.\nPlease erase all my personal data from all systems, backups, and processors.\nRespond within {dl}.\n\nSincerely,\n{rname}"
                st.text_area("Letter:",value=letter,height=250,key="rtbf_out")
                st.download_button("Download",letter,file_name=f"RTBF_{rco}.txt",key="dl_rtbf")

    elif page == "Security Suite":
        st.markdown('<div class="s-label">Security & Audit Suite</div>',unsafe_allow_html=True)
        t=st.tabs(["#24/#30 Code Audit","#11 Personas","#16 Social Eng","#44 Honeypots","#45 Kill Switch"])
        with t[0]:
            aud=st.radio("Type",["SQL Injection","XSS / Script"],horizontal=True,key="sec_aud")
            code_in=st.text_area("Paste code:",height=200,key="sec_code")
            c1,c2=st.columns(2)
            if c1.button("Pattern Scan",key="sec_pat") and code_in:
                findings=(scan_sql if aud=="SQL Injection" else scan_xss)(code_in)
                if findings:
                    for f in findings: st.markdown(f'<div class="warn">Line {f["line"]} — <b>{f["issue"]}</b><br><code>{f["snippet"]}</code></div>',unsafe_allow_html=True)
                else: st.markdown('<div class="ok">✅ No patterns detected</div>',unsafe_allow_html=True)
            if c2.button("AI Deep Audit",key="sec_ai") and code_in:
                with st.spinner("Auditing..."):
                    r=ai(f"Audit for {aud} vulnerabilities with line numbers, impact, and fixes:\n\n```\n{code_in}\n```",max_tokens=1500)
                st.markdown(r)
        with t[1]:
            ctx=st.text_area("Product/concept to test:",height=80,key="sec_pctx")
            cnt=st.slider("Personas",1,5,3,key="sec_pcnt"); reg=st.selectbox("Region",["Trinidad & Tobago","Caribbean","Global"],key="sec_preg")
            if st.button("Generate Personas",key="sec_pgo") and ctx:
                with st.spinner("Generating..."):
                    r=ai(f"Generate {cnt} distinct synthetic research personas for: {ctx}\nRegion: {reg}\nFor each: fictional name, age, occupation, top 3 pain points, decision style, one direct quote.",system="You are a senior UX researcher.",max_tokens=2000)
                st.markdown(r)
        with t[2]:
            msg=st.text_area("Suspicious message:",height=120,key="sec_semsg")
            if st.button("Analyze for Social Engineering",key="sec_se") and msg:
                with st.spinner("..."):
                    r=ai(f"Analyze for social engineering tactics. Rate threat Low/Med/High/Critical:\n\n{msg}",max_tokens=800)
                st.markdown(r)
        with t[3]:
            hp_svc=st.text_input("Generate fake credentials for:",placeholder="AWS / Database / VPN",key="sec_hp")
            if st.button("Generate Honeypot File",key="sec_hp_btn") and hp_svc:
                content=f"# {hp_svc} Credentials — DO NOT SHARE\n{hp_svc.upper()}_KEY={secrets.token_hex(16)}\n{hp_svc.upper()}_SECRET={secrets.token_urlsafe(32)}\n{hp_svc.upper()}_ENDPOINT=https://{hp_svc.lower()}.internal.corp.com"
                st.markdown(f'<div class="cb">{content}</div>',unsafe_allow_html=True)
                st.download_button("Download Honeypot",content,file_name=f"{hp_svc}_credentials.env",key="dl_hp")
        with t[4]:
            ks_os=st.selectbox("OS",["Linux","macOS","Windows"],key="sec_ks_os")
            ks_acts=st.multiselect("Actions",["Cut network","Lock screen","Log connections"],default=["Cut network","Lock screen"],key="sec_ks_acts")
            if st.button("Generate Kill Switch",key="sec_ks_btn"):
                lines=["#!/bin/bash","# EMERGENCY KILL SWITCH",""]
                if "Log connections" in " ".join(ks_acts): lines+=["ss -tunap > /tmp/ks_log.txt",""]
                if "Cut network" in " ".join(ks_acts):
                    if ks_os=="Linux": lines+=["for i in $(ip l|awk -F: '$0!~/lo/{print $2}'|tr -d ' '); do sudo ip link set $i down; done"]
                    elif ks_os=="macOS": lines+=["networksetup -setairportpower en0 off"]
                    else: lines=["Get-NetAdapter | Disable-NetAdapter -Confirm:$false"]
                if "Lock screen" in " ".join(ks_acts):
                    if ks_os=="Linux": lines+=["loginctl lock-session"]
                    elif ks_os=="macOS": lines+=["/System/Library/CoreServices/Menu\\ Extras/User.menu/Contents/Resources/CGSession -suspend"]
                    else: lines+=["rundll32.exe user32.dll,LockWorkStation"]
                script="\n".join(lines)
                st.markdown(f'<div class="cb">{script}</div>',unsafe_allow_html=True)
                st.download_button("Download Script",script,file_name="kill_switch.sh",key="dl_ks")

    elif page == "Intelligence Suite":
        st.markdown('<div class="s-label">Intelligence & Analytics Suite</div>',unsafe_allow_html=True)
        t=st.tabs(["#34 Sentiment","#33 TT Market","#26 Dark Data","#37 Competitor","#32 Adversarial"])
        with t[0]:
            sa_t=st.text_area("Text to analyze:",height=120,key="intel_sa")
            c1,c2=st.columns(2)
            if c1.button("VADER Analysis",key="intel_vader") and sa_t:
                s=vader(sa_t); compound=s["compound"]
                label="Positive 😊" if compound>.05 else "Negative 😞" if compound<-.05 else "Neutral 😐"
                fig=go.Figure(go.Indicator(mode="gauge+number",value=compound,title={"text":f"Sentiment: {label}"},
                    gauge={"axis":{"range":[-1,1]},"bar":{"color":"#ffaa00"}}))
                fig.update_layout(height=250,paper_bgcolor="#0e0e0e",font_color="#f0f0f0")
                st.plotly_chart(fig,use_container_width=True)
            if c2.button("AI Deep Sentiment",key="intel_ai_sent") and sa_t:
                with st.spinner("..."): r=ai(f"Deep sentiment and emotion analysis:\n\n{sa_t}",max_tokens=600)
                st.markdown(r)
        with t[1]:
            sector=st.selectbox("Sector",["Energy (Oil & Gas)","Real Estate","Retail","Tourism","Agriculture","Technology","Construction","Financial Services"],key="intel_sector")
            horizon=st.selectbox("Horizon",["3 months","6 months","12 months","3 years"],key="intel_hor")
            ctx=st.text_area("Context:",height=60,key="intel_ctx")
            if st.button("Generate TT Analysis",key="intel_mkt"):
                with st.spinner("Analyzing..."):
                    r=ai(f"Senior TT economist analysis. Sector: {sector}. Horizon: {horizon}. Context: {ctx}\n\nCurrent state, {horizon} outlook with confidence levels, TT-specific risks (energy dependence, USD scarcity), opportunities, recommended actions.",system="You are a leading Trinidad & Tobago economist.",max_tokens=2000)
                st.markdown(r)
                st.download_button("Export",r,file_name="tt_analysis.md",key="dl_mkt")
        with t[2]:
            dd_mode=st.radio("Input",["Paste text","Upload files"],horizontal=True,key="intel_ddm")
            all_text=[]
            if dd_mode=="Upload files":
                ups=st.file_uploader("Upload",accept_multiple_files=True,key="intel_ups")
                if ups:
                    for uf in ups:
                        try: all_text.append(f"=== {uf.name} ===\n"+uf.read().decode("utf-8","ignore")); st.success(f"✅ {uf.name}")
                        except Exception as e: st.error(str(e))
            else:
                p=st.text_area("Paste:",height=200,key="intel_paste")
                if p: all_text=[p]
            if all_text:
                extracts=st.multiselect("Extract:",["Business ideas","Action items","Key themes","Knowledge gaps"],default=["Business ideas","Action items"],key="intel_ex")
                if st.button("Illuminate Dark Data",key="intel_dd"):
                    combined="\n\n".join(all_text)
                    with st.spinner("Analyzing..."):
                        r=ai(f"Analyze this archive. Extract:\n"+"\n".join(f"- {x}" for x in extracts)+f"\n\nContent:\n---\n{combined[:10000]}\n---",system="You are an expert analyst excavating insights.",max_tokens=2500)
                    st.markdown(r)
        with t[3]:
            your_biz=st.text_area("Your business:",height=60,key="intel_ybiz")
            comps=st.text_area("Competitors (one/line):",height=80,key="intel_comps")
            if st.button("Benchmark",key="intel_cb") and your_biz and comps:
                cl=[c.strip() for c in comps.split("\n") if c.strip()]
                with st.spinner("..."):
                    r=ai(f"Competitive intelligence for Caribbean/TT market.\nYour business: {your_biz}\nCompetitors: {', '.join(cl)}\n\nComparison matrix, gaps, opportunities, strategy.",system="Competitive intelligence analyst with Caribbean expertise.",max_tokens=2000)
                st.markdown(r)
        with t[4]:
            adv_type=st.radio("Test:",["Business plan","Argument","Product idea"],horizontal=True,key="intel_adv")
            adv_in=st.text_area(f"Paste {adv_type}:",height=150,key="intel_adv_in")
            intensity=st.select_slider("Intensity",["Gentle","Moderate","Aggressive","Brutal"],value="Aggressive",key="intel_int")
            if st.button("Run Adversarial Test",key="intel_adv_btn") and adv_in:
                role={"Gentle":"constructive critic","Moderate":"skeptical investor","Aggressive":"hostile adversary","Brutal":"someone tasked with destroying this"}[intensity]
                with st.spinner("..."):
                    r=ai(f"Act as {role}. Find all flaws, weaknesses, blind spots:\n---\n{adv_in}\n---",max_tokens=1500)
                st.markdown(r)

    elif page == "Operations Suite":
        st.markdown('<div class="s-label">Operations Suite</div>',unsafe_allow_html=True)
        t=st.tabs(["#42 Ghost-Writing","#47 Translation","#48 Anonymize","#3 Local LLM","#41 Scheduler"])
        with t[0]:
            c1,c2=st.columns(2)
            gw_type=c1.selectbox("Type",["LinkedIn post","Business proposal","Email","Blog","Speech","Press release","Caption","Custom"],key="ops_gwt")
            gw_topic=c1.text_area("Topic/brief:",height=80,key="ops_gwto")
            gw_len=c1.select_slider("Length",["100w","250w","500w","800w"],value="500w",key="ops_gwl")
            gw_tone=c1.select_slider("Tone",["Formal","Professional","Conversational","Casual","Bold"],value="Professional",key="ops_gwtn")
            gw_style=c2.text_area("Your writing sample (voice match):",height=120,key="ops_gws")
            gw_audience=c2.text_input("Audience:",key="ops_gwa")
            if c2.button("Generate",key="ops_gw_btn") and gw_topic:
                style=f"\n\nMatch my voice:\n---\n{gw_style}\n---" if gw_style.strip() else ""
                with st.spinner("Writing..."):
                    r=ai(f"Write a {gw_type} (~{gw_len}). Topic: {gw_topic}. Tone: {gw_tone}. Audience: {gw_audience or 'general'}. Output only the final content.{style}",system="World-class ghostwriter.",max_tokens=2000)
                st.text_area("Output:",value=r,height=300,key="ops_gw_out")
                st.download_button("Download",r,file_name="ghost_write.txt",key="dl_gw")
        with t[1]:
            c1,c2=st.columns(2)
            src_l=c1.selectbox("From",["English","Spanish","French","Creole (TT)","Portuguese"],key="ops_srcl")
            tgt_l=c1.selectbox("To",["Spanish","English","French","Creole (TT)","Portuguese"],key="ops_tgtl")
            tr_ctx=c1.selectbox("Context",["Business","Casual","Legal","Medical"],key="ops_trctx")
            tr_local=c1.checkbox("Adapt for TT/Caribbean",True,key="ops_trl")
            src_txt=c2.text_area("Source:",height=180,key="ops_src")
            if c2.button("Translate",key="ops_tr") and src_txt:
                local="Adapt for Trinidad & Tobago / Caribbean audience." if tr_local else ""
                with st.spinner("..."): r=ai(f"Translate {src_l}→{tgt_l} for {tr_ctx}. {local}\n\nSource:\n---\n{src_txt}\n---",system="Expert translator with Caribbean knowledge.",max_tokens=1200)
                st.text_area("Translation:",value=r,height=180,key="ops_tr_out")
        with t[2]:
            npm_txt=st.text_area("Text to anonymize:",height=150,key="ops_anon")
            ops=st.multiselect("Operations",["Auto-detect PII","Style obfuscation"],default=["Auto-detect PII"],key="ops_anon_ops")
            custom_r=st.text_area("Custom replacements (original→replacement):",height=60,key="ops_anon_cr")
            if st.button("Apply Masking",key="ops_anon_btn") and npm_txt:
                creps={}
                for line in custom_r.split("\n"):
                    if "→" in line: k,v=line.split("→",1); creps[k.strip()]=v.strip()
                masked=anon_text(npm_txt,creps)
                if "Style obfuscation" in " ".join(ops):
                    with st.spinner("..."): r=ai(f"Apply anonymization. Output only the anonymized text:\n---\n{masked}\n---",max_tokens=1500)
                else: r=masked
                st.text_area("Anonymized:",value=r,height=150,key="ops_anon_out")
                st.download_button("Download",r,file_name="anonymized.txt",key="dl_anon")
        with t[3]:
            llm_tool=st.selectbox("Platform",["Ollama (recommended)","LM Studio","llama.cpp"],key="ops_llm")
            cfgs={"Ollama (recommended)":"curl -fsSL https://ollama.com/install.sh | sh\nollama pull llama3.1\nollama run llama3.1\n\n# API:\ncurl http://localhost:11434/v1/chat/completions -H 'Content-Type: application/json' -d '{\"model\":\"llama3.1\",\"messages\":[{\"role\":\"user\",\"content\":\"Hello\"}]}'","LM Studio":"# Download: lmstudio.ai → Install → Server tab → Start\n# API: http://localhost:1234/v1\n\nfrom openai import OpenAI\nclient=OpenAI(base_url='http://localhost:1234/v1',api_key='local')\nresponse=client.chat.completions.create(model='local-model',messages=[{'role':'user','content':'Hello'}])","llama.cpp":"git clone https://github.com/ggerganov/llama.cpp && cd llama.cpp && make\n# Download GGUF model from HuggingFace\n./server -m model.Q4_K_M.gguf --host 0.0.0.0 --port 8080"}
            st.markdown(f'<div class="cb">{cfgs[llm_tool]}</div>',unsafe_allow_html=True)
            st.download_button("Download Guide",cfgs[llm_tool],file_name="local_llm.sh",key="dl_llm")
        with t[4]:
            t_name=st.text_input("Task",key="ops_tname"); t_cmd=st.text_area("Command",height=60,key="ops_tcmd")
            t_freq=st.selectbox("Frequency",["Every 5 min","Every hour","Daily 9am","Weekly Mon"],key="ops_tfreq")
            t_os=st.radio("OS",["Linux (cron)","Windows","Python"],horizontal=True,key="ops_tos")
            if st.button("Generate Schedule",key="ops_sched") and t_name:
                cron_map={"Every 5 min":"*/5 * * * *","Every hour":"0 * * * *","Daily 9am":"0 9 * * *","Weekly Mon":"0 9 * * 1"}
                cron=cron_map.get(t_freq,"0 9 * * *")
                if "Linux" in t_os: sc=f"# crontab -e\n{cron} {t_cmd} >> /var/log/{t_name}.log 2>&1"
                elif "Windows" in t_os: sc=f'$A=New-ScheduledTaskAction -Execute "powershell" -Argument "{t_cmd}"\n$T=New-ScheduledTaskTrigger -Daily -At 9am\nRegister-ScheduledTask -TaskName "{t_name}" -Action $A -Trigger $T -Force'
                else: sc=f"import schedule, subprocess, time\ndef task():\n subprocess.run('{t_cmd}',shell=True)\nschedule.every().day.at('09:00').do(task)\nwhile True:\n schedule.run_pending()\n time.sleep(60)"
                st.markdown(f'<div class="cb">{sc}</div>',unsafe_allow_html=True)
                st.download_button("Download",sc,file_name=f"{t_name}_schedule.txt",key="dl_sched")

# ══════════════════════════════════════════════════════════════════════════════
# 🇹🇹 TT MARKET
# ══════════════════════════════════════════════════════════════════════════════
elif section == "🇹🇹 TT Market":
    brain=st.session_state.tt_conv
    tt_nd=brain["namdevco"]; tt_massy=brain["massy"]; tt_conv=brain["conversations"]
    def save_brain(): save_json(fp("tt_brain.json"),brain)

    if page == "Dashboard":
        st.markdown('<div class="s-label">TT Market Intelligence Dashboard</div>',unsafe_allow_html=True)
        month=now.month; season="Dry Season 🌞" if 1<=month<=5 else "Wet Season 🌧️"
        mu=sum(1 for l in tt_massy.values() if len(l)>=2 and l[-1]["price"]>l[-2]["price"])
        c1,c2,c3,c4=st.columns(4)
        c1.metric("🛒 Massy Items",len(tt_massy)); c2.metric("📊 NAMDEVCO Items",len(tt_nd))
        c3.metric("📈 Massy Up",f"{mu}/{len(tt_massy)}"); c4.metric("🌱 Season",season)
        st.markdown('<div class="s-label">Latest Prices</div>',unsafe_allow_html=True)
        tab1,tab2=st.tabs(["🛒 Massy","📊 NAMDEVCO Wholesale"])
        with tab1:
            cols=st.columns(4)
            for i,(item,logs) in enumerate(tt_massy.items()):
                if len(logs)>=2:
                    curr=logs[-1]["price"]; d=curr-logs[-2]["price"]
                    cols[i%4].metric(item.capitalize(),f"TT${curr:.2f}",f"{d:+.2f}",delta_color="inverse")
        with tab2:
            cols=st.columns(4)
            for i,(item,logs) in enumerate(tt_nd.items()):
                if len(logs)>=2:
                    curr=logs[-1]["price"]; d=curr-logs[-2]["price"]
                    cols[i%4].metric(item.capitalize(),f"TT${curr:.2f}/kg",f"{d:+.2f}",delta_color="inverse")
        cal=CROP_CAL[month]
        st.markdown('<div class="s-label">This Month — Farmers Almanac</div>',unsafe_allow_html=True)
        a,b=st.columns(2)
        a.success("**🌱 Plant now:**\n\n"+"\n".join(f"- {c}" for c in cal["plant"]))
        b.info("**🧺 Harvest:**\n\n"+"\n".join(f"- {c}" for c in cal["reap"]))

    elif page == "Chatbot":
        st.markdown('<div class="s-label">TT Market Chatbot</div>',unsafe_allow_html=True)
        for msg in st.session_state.tt_messages:
            with st.chat_message(msg["role"]): st.markdown(msg["content"])
        if st.session_state.tt_pending:
            word=st.session_state.tt_pending
            st.info(f"🎓 Teaching mode — I don't know **'{word}'** yet.")
            with st.form("train_form",clear_on_submit=True):
                teacher=st.text_input(f"What should I say about '{word}'?")
                cs,ck=st.columns(2); saved=cs.form_submit_button("Save & Teach",type="primary"); skip=ck.form_submit_button("Skip")
            if saved and teacher:
                key=word.lower().strip()
                if key not in tt_conv: tt_conv[key]=[]
                tt_conv[key].append(teacher); save_brain()
                st.session_state.tt_messages.append({"role":"assistant","content":f"✨ Learned about '{word}'!"})
                st.session_state.tt_pending=None; st.rerun()
            elif skip:
                st.session_state.tt_messages.append({"role":"assistant","content":"No worries! Ask me something else 😊"})
                st.session_state.tt_pending=None; st.rerun()
        user_input_tt=st.chat_input("Ask about a price, season, or food item...")
        if user_input_tt and not st.session_state.tt_pending:
            st.session_state.tt_messages.append({"role":"user","content":user_input_tt})
            with st.chat_message("user"): st.markdown(user_input_tt)
            result=bot_process(user_input_tt,tt_conv,tt_nd,tt_massy)
            with st.chat_message("assistant"):
                st.markdown(result["text"])
                if result.get("logs") and len(result["logs"])>=2:
                    logs=result["logs"]; unit="/kg" if result.get("source")=="namdevco" else ""
                    fig=go.Figure(); fig.add_trace(go.Scatter(x=[l["date"] for l in logs],y=[l["price"] for l in logs],mode="lines+markers",line=dict(color="#ffaa00",width=2)))
                    fig.update_layout(height=200,margin=dict(l=10,r=10,t=10,b=10),paper_bgcolor="#0e0e0e",plot_bgcolor="#0e0e0e",font_color="#f0f0f0",showlegend=False)
                    st.plotly_chart(fig,use_container_width=True)
            st.session_state.tt_messages.append({"role":"assistant","content":result["text"]})
            if result["type"]=="needs_training": st.session_state.tt_pending=result["unknown_word"]
            st.rerun()

    elif page == "Price Tracker":
        st.markdown('<div class="s-label">Price Tracker</div>',unsafe_allow_html=True)
        st.subheader("🛒 Massy Stores")
        rows=[]
        for item,logs in tt_massy.items():
            if len(logs)>=2:
                curr,prev=logs[-1]["price"],logs[-2]["price"]; d=curr-prev; pct=round(d/prev*100,1) if prev else 0
                rows.append({"Item":item.capitalize(),"Prev TT$":prev,"Latest TT$":curr,"Δ TT$":round(d,2),"Δ %":pct,"Trend":"Rising 🔺" if d>0 else "Falling 🔻" if d<0 else "Stable 🔹","🔮 Predicted":predict_price(logs)})
        if rows:
            st.dataframe(pd.DataFrame(rows),use_container_width=True)
            with st.expander("➕ Add / Update Massy Price"):
                a1,a2,a3=st.columns(3)
                ni=a1.text_input("Item",key="massy_ni"); np_=a2.number_input("Price (TT$)",min_value=0.01,step=0.50,key="massy_np")
                if a3.button("Save",key="massy_save") and ni:
                    key=ni.lower().strip()
                    if key not in tt_massy: tt_massy[key]=[]
                    tt_massy[key].append({"date":date.today().isoformat(),"price":round(np_,2)}); save_brain()
                    st.success(f"✅ Saved TT${np_:.2f} for {ni}"); st.rerun()
        st.subheader("📊 NAMDEVCO Wholesale")
        nd_rows=[]
        for item,logs in tt_nd.items():
            if len(logs)>=2:
                curr,prev=logs[-1]["price"],logs[-2]["price"]; d=curr-prev; pct=round(d/prev*100,1) if prev else 0
                nd_rows.append({"Item":item.capitalize(),"Prev TT$":prev,"Latest TT$":curr,"Δ TT$":round(d,2),"Δ %":pct,"Trend":"Rising 🔺" if d>0 else "Falling 🔻" if d<0 else "Stable 🔹","🔮 Predicted":predict_price(logs)})
        if nd_rows: st.dataframe(pd.DataFrame(nd_rows),use_container_width=True)

    elif page == "Farmers Calendar":
        st.markdown('<div class="s-label">Farmers Calendar — Trinidad & Tobago</div>',unsafe_allow_html=True)
        month=now.month; cal=CROP_CAL[month]
        st.subheader(f"📅 {MONTHS[month-1]} — {cal['season']} Season")
        c1,c2=st.columns(2)
        c1.success("### 🌱 Plant Now\n\n"+"\n".join(f"- {c}" for c in cal["plant"]))
        c2.info("### 🧺 Harvest Now\n\n"+"\n".join(f"- {c}" for c in cal["reap"]))
        st.markdown('<div class="s-label">Full Year</div>',unsafe_allow_html=True)
        cl,cr=st.columns(2)
        for m in range(1,13):
            col=cl if m<=6 else cr; data=CROP_CAL[m]
            with col.expander(f"{'👉 ' if m==month else ''}{MONTHS[m-1]} — {data['season']}",expanded=(m==month)):
                a,b=st.columns(2)
                a.markdown("**🌱 Plant**"); [a.markdown(f"- {c}") for c in data["plant"]]
                b.markdown("**🧺 Harvest**"); [b.markdown(f"- {c}") for c in data["reap"]]
        st.markdown('<div class="s-label">Search a Crop</div>',unsafe_allow_html=True)
        cq=st.text_input("Crop name",key="tt_crop_srch")
        if cq:
            pm=[MONTHS[m-1] for m,d in CROP_CAL.items() if any(cq.lower() in c.lower() for c in d["plant"])]
            hm=[MONTHS[m-1] for m,d in CROP_CAL.items() if any(cq.lower() in c.lower() for c in d["reap"])]
            pc,hc=st.columns(2)
            if pm: pc.success(f"**🌱 Plant {cq} in:**\n\n"+"\n".join(f"- {m}" for m in pm))
            else: pc.warning("No planting data found.")
            if hm: hc.info(f"**🧺 Harvest {cq} in:**\n\n"+"\n".join(f"- {m}" for m in hm))
            else: hc.warning("No harvest data found.")

    elif page == "Weather":
        st.markdown('<div class="s-label">Weather — Trinidad & Tobago</div>',unsafe_allow_html=True)
        locs={"Trinidad":"Trinidad","Tobago":"Tobago","Port of Spain":"Port+of+Spain,Trinidad","San Fernando":"San+Fernando,Trinidad","Chaguanas":"Chaguanas,Trinidad"}
        cl,cb2=st.columns([3,1]); loc=cl.selectbox("Location",list(locs.keys()),key="tt_wx_loc")
        cb2.write(""); cb2.write("")
        if cb2.button("Get Forecast",key="tt_wx_btn"):
            w=get_weather(locs[loc])
            if w: st.session_state["tt_wx"]=w
        if "tt_wx" not in st.session_state:
            w=get_weather()
            if w: st.session_state["tt_wx"]=w
        w=st.session_state.get("tt_wx")
        if w:
            cur=w['current_condition'][0]
            m1,m2,m3,m4=st.columns(4)
            m1.metric("🌡️ Temp",f"{cur['temp_C']}°C"); m2.metric("🤔 Feels Like",f"{cur['FeelsLikeC']}°C")
            m3.metric("💧 Humidity",f"{cur['humidity']}%"); m4.metric("💨 Wind",f"{cur['windspeedKmph']} km/h")
            desc=cur['weatherDesc'][0]['value']; st.info(f"**{desc}**")
            if int(cur['windspeedKmph'])>60: st.error("⚠️ HIGH WINDS — Secure crops!")
            elif "Rain" in desc: st.warning("🌧️ RAIN — Delay spraying or fertilising.")
            elif int(cur['temp_C'])>32: st.warning("☀️ HOT — Irrigate early morning.")
            else: st.success("✅ Good conditions for fieldwork.")
            st.markdown('<div class="s-label">3-Day Forecast</div>',unsafe_allow_html=True)
            dcols=st.columns(3)
            for i,day in enumerate(w["weather"][:3]):
                label=["Today","Tomorrow",datetime.strptime(day["date"],"%Y-%m-%d").strftime("%A")][i]
                rain=sum(float(h.get("precipMM",0)) for h in day["hourly"])
                dcols[i].markdown(f'<div class="stat-block"><div style="font-family:Space Mono,monospace;font-size:0.6rem;color:var(--dim);letter-spacing:2px;margin-bottom:0.5rem;">{label.upper()}</div><div class="stat-val" style="font-size:1.4rem;">{day["maxtempC"]}°</div><div class="stat-lbl">{day["mintempC"]}° low · {rain:.1f}mm rain</div></div>',unsafe_allow_html=True)
        else:
            st.markdown('<div class="wx-block"><div class="wx-temp">--°</div><div class="wx-desc">Weather unavailable — check connection</div></div>',unsafe_allow_html=True)

    elif page == "Ledger":
        ledger=st.session_state.tt_ledger; today=date.today()
        total=sum(e["price"]*e["qty"] for e in ledger)
        this_mo=sum(e["price"]*e["qty"] for e in ledger if e.get("date_bought","")[:7]==today.strftime("%Y-%m"))
        exp_soon=[e for e in ledger if e.get("expiry_date") and 0<=(date.fromisoformat(e["expiry_date"])-today).days<=5]
        expired=[e for e in ledger if e.get("expiry_date") and (date.fromisoformat(e["expiry_date"])-today).days<0]
        m1,m2,m3,m4=st.columns(4)
        m1.metric("Items",len(ledger)); m2.metric("Total Spent",f"TT${total:,.2f}")
        m3.metric("This Month",f"TT${this_mo:,.2f}"); m4.metric("⚠️ Expiring",len(exp_soon),delta=f"{len(expired)} expired",delta_color="inverse")
        if expired:
            with st.expander(f"🔴 {len(expired)} EXPIRED",expanded=True):
                for e in expired: st.error(f"❌ {e['item']} — expired {e['expiry_date']}")
        if exp_soon:
            with st.expander(f"🟡 {len(exp_soon)} expiring soon",expanded=True):
                for e in exp_soon:
                    d=(date.fromisoformat(e["expiry_date"])-today).days
                    st.warning(f"⚠️ {e['item']} — {d} day(s) left")
        st.markdown('<div class="s-label">Add Purchase</div>',unsafe_allow_html=True)
        with st.form("ledger_form",clear_on_submit=True):
            r1,r2,r3=st.columns(3)
            item_name=r1.text_input("Item *"); category=r1.selectbox("Category",CATEGORIES); store=r1.text_input("Store")
            price=r2.number_input("Price (TT$) *",min_value=0.01,step=0.50,format="%.2f"); qty=r2.number_input("Qty",min_value=1,value=1); unit=r2.selectbox("Unit",["each","kg","lb","pack","litre","bottle","bag"])
            d_bought=r3.date_input("Date bought",value=today,key="led_dbought"); expiry=r3.date_input("Expiry (optional)",value=today,key="led_exp"); notes=r3.text_input("Notes",key="led_notes")
            if st.form_submit_button("💾 Save",type="primary"):
                if item_name:
                    ledger.append({"id":len(ledger)+1,"item":item_name,"category":category,"store":store,"price":round(price,2),"qty":qty,"unit":unit,"total":round(price*qty,2),"date_bought":d_bought.isoformat(),"expiry_date":expiry.isoformat() if expiry else None,"notes":notes})
                    save_json(fp("tt_ledger.json"),ledger); st.session_state.tt_ledger=ledger; st.success(f"✅ Added {item_name}"); st.rerun()
        if ledger:
            df=pd.DataFrame(ledger)
            st.dataframe(df[["item","category","store","price","qty","total","date_bought","expiry_date"]],use_container_width=True,height=280)
            cat_totals={};
            for e in ledger: cat_totals[e.get("category","Other")]=cat_totals.get(e.get("category","Other"),0)+e["total"]
            fig=px.pie(values=list(cat_totals.values()),names=list(cat_totals.keys()),title="Spending by Category")
            fig.update_layout(paper_bgcolor="#0e0e0e",font_color="#f0f0f0"); st.plotly_chart(fig,use_container_width=True)

    elif page == "Bills":
        bills=st.session_state.tt_bills; today=date.today()
        unpaid=[b for b in bills if "Paid" not in b.get("status","")]
        due_soon=[b for b in bills if b.get("due_date") and "Paid" not in b.get("status","") and 0<=(date.fromisoformat(b["due_date"])-today).days<=7]
        m1,m2,m3,m4=st.columns(4)
        m1.metric("Total",len(bills)); m2.metric("Unpaid",len(unpaid),delta=f"TT${sum(b['amount'] for b in unpaid):,.2f}",delta_color="inverse")
        m3.metric("Due This Week",len(due_soon)); m4.metric("Total Owed",f"TT${sum(b['amount'] for b in unpaid):,.2f}")
        if due_soon:
            with st.expander(f"🟡 {len(due_soon)} due this week",expanded=True):
                for b in due_soon:
                    d=(date.fromisoformat(b["due_date"])-today).days
                    st.warning(f"⏰ {b['bill_type']} — TT${b['amount']:.2f} due in {d} day(s)")
        with st.form("bill_form",clear_on_submit=True):
            bc1,bc2,bc3=st.columns(3)
            btype=bc1.selectbox("Bill Type",BILL_TYPES); amount=bc1.number_input("Amount (TT$)",min_value=0.01,step=5.0,format="%.2f")
            due_date=bc2.date_input("Due Date",value=today,key="bill_due"); status=bc2.selectbox("Status",["Unpaid 🔴","Paid ✅","Overdue ⚠️"],key="bill_status")
            dpaid=bc3.date_input("Date Paid",value=today,key="bill_paid"); ref=bc3.text_input("Reference No.",key="bill_ref")
            if st.form_submit_button("💾 Save Bill",type="primary"):
                bills.append({"id":len(bills)+1,"bill_type":btype,"amount":round(amount,2),"due_date":due_date.isoformat() if due_date else None,"status":status,"date_paid":dpaid.isoformat() if dpaid else None,"ref_no":ref,"logged_on":today.isoformat()})
                save_json(fp("tt_bills.json"),bills); st.session_state.tt_bills=bills; st.success(f"✅ Logged {btype}"); st.rerun()
        if bills:
            st.dataframe(pd.DataFrame(bills)[["bill_type","amount","due_date","status","date_paid","ref_no"]],use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# 🖥 VECTOR OS
# ══════════════════════════════════════════════════════════════════════════════
elif section == "🖥 VECTOR OS":
    health=st.session_state.health
    mode_vos=st.session_state.get("mode_vos","Morning Brief")
    def save_health(): save_json(fp("health.json"),health)

    if mode_vos == "Morning Brief":
        if page == "Overview":
            col_l,col_r=st.columns([2,1],gap="large")
            with col_l:
                st.markdown('<div class="s-label">Top Headlines</div>',unsafe_allow_html=True)
                for item in get_news("https://www.theguardian.com/world/rss"):
                    st.markdown(f'<a href="{item["link"]}" target="_blank" style="text-decoration:none;"><div class="news-card"><div class="news-headline">{item["title"]}</div><div class="news-stamp">{item["pub"]}</div></div></a>',unsafe_allow_html=True)
            with col_r:
                st.markdown('<div class="s-label">Weather</div>',unsafe_allow_html=True)
                w=get_weather()
                if w:
                    tc=w['current_condition'][0]['temp_C']; dc=w['current_condition'][0]['weatherDesc'][0]['value']
                    fl=w['current_condition'][0]['FeelsLikeC']; hm=w['current_condition'][0]['humidity']
                    st.markdown(f'<div class="wx-block"><div class="wx-temp">{tc}°</div><div class="wx-desc">{dc}</div><div style="font-family:Space Mono,monospace;font-size:0.58rem;color:var(--dim);margin-top:0.4rem;">Feels {fl}° · Humidity {hm}%</div></div>',unsafe_allow_html=True)
                else:
                    st.markdown('<div class="wx-block"><div class="wx-temp">--°</div><div class="wx-desc">Unavailable</div></div>',unsafe_allow_html=True)
                st.markdown('<div class="s-label">Bills</div>',unsafe_allow_html=True)
                fin=st.session_state.brief_fin; bl=st.session_state.brief_bills
                planned=fin['ttec']+fin['wasa']+fin['bmobile']+fin['internet']; surplus=fin['salary']-planned
                sc="g" if surplus>=0 else "r"
                st.markdown(f'<div class="v-card"><div class="v-row"><span class="v-row-label">Salary</span><span class="v-row-val">${fin["salary"]:,.0f}</span></div><div class="v-row"><span class="v-row-label">Bills</span><span class="v-row-val r">${planned:,.0f}</span></div><div class="v-row"><span class="v-row-label">Surplus</span><span class="v-row-val {sc}">${surplus:,.0f}</span></div></div>',unsafe_allow_html=True)
                for b in ["ttec","wasa","bmobile","internet"]:
                    paid=bl.get(b,0); cls="g" if paid>0 else "r"
                    st.markdown(f'<div class="v-row"><span class="v-row-label">{b.upper()}</span><span class="v-row-val {cls}">{"$"+str(paid) if paid>0 else "PENDING"}</span></div>',unsafe_allow_html=True)
                st.markdown('<div class="s-label">Tasks</div>',unsafe_allow_html=True)
                active_t=[t for t in st.session_state.brief_tasks if t['status']=='Active']
                for t in active_t[:4]:
                    cls="v-card-r" if t['importance']=='Urgent' else "v-card-a"
                    st.markdown(f'<div class="{cls} v-card" style="padding:0.6rem 1rem;margin-bottom:2px;"><span style="font-size:0.8rem;">{"🔴" if t["importance"]=="Urgent" else "○"} {t["name"]}</span></div>',unsafe_allow_html=True)

        elif page == "Finances":
            fin=st.session_state.brief_fin; bl=st.session_state.brief_bills
            planned=fin['ttec']+fin['wasa']+fin['bmobile']+fin['internet']; surplus=fin['salary']-planned
            c1,c2,c3=st.columns(3)
            c1.markdown(f'<div class="stat-block"><div class="stat-val">${fin["salary"]:,.0f}</div><div class="stat-lbl">Salary</div></div>',unsafe_allow_html=True)
            c2.markdown(f'<div class="stat-block"><div class="stat-val r">${planned:,.0f}</div><div class="stat-lbl">Planned Bills</div></div>',unsafe_allow_html=True)
            c3.markdown(f'<div class="stat-block"><div class="stat-val {"g" if surplus>=0 else "r"}">${surplus:,.0f}</div><div class="stat-lbl">Surplus</div></div>',unsafe_allow_html=True)
            st.markdown('<div class="s-label">Settle Bills</div>',unsafe_allow_html=True)
            col1,col2,col3=st.columns([2,2,1])
            b_sel=col1.selectbox("Bill",["ttec","wasa","bmobile","internet"],key="vos_bsel")
            b_amt=col2.number_input("Amount Paid",min_value=0.0,key="vos_bamt")
            if col3.button("Settle",key="vos_bsave"):
                bl[b_sel]=b_amt; save_json(fp("brief_bills.json"),bl); st.rerun()
            with st.expander("Update Figures"):
                fin['salary']=st.number_input("Salary",value=fin['salary'],key="vos_sal"); fin['ttec']=st.number_input("T&TEC",value=fin['ttec'],key="vos_ttec")
                fin['wasa']=st.number_input("WASA",value=fin['wasa'],key="vos_wasa"); fin['bmobile']=st.number_input("BMobile",value=fin['bmobile'],key="vos_bm"); fin['internet']=st.number_input("Internet",value=fin['internet'],key="vos_inet")
                if st.button("Save",key="vos_fin_save"): save_json(fp("brief_fin.json"),fin); st.rerun()

        elif page == "Tasks & Notes":
            col1,col2=st.columns(2,gap="large")
            tasks=st.session_state.brief_tasks; notes=st.session_state.brief_notes
            with col1:
                st.markdown('<div class="s-label">Tasks</div>',unsafe_allow_html=True)
                with st.form("new_task",clear_on_submit=True):
                    c1,c2=st.columns([3,1]); tt=c1.text_input("New Task",key="vos_tt"); tl=c2.selectbox("Priority",["Normal","Urgent"],key="vos_tl")
                    if st.form_submit_button("Add"):
                        if tt: tasks.append({"name":tt,"importance":tl,"status":"Active","time":now.strftime("%Y-%m-%d %H:%M")}); save_json(fp("brief_tasks.json"),tasks); st.rerun()
                for i,t in enumerate(tasks):
                    if t['status']=='Active':
                        ca,cb=st.columns([5,1]); cls="v-card-r" if t['importance']=='Urgent' else "v-card-a"
                        ca.markdown(f'<div class="{cls} v-card" style="padding:0.6rem 1rem;margin-bottom:2px;"><span style="font-size:0.8rem;">{"🔴" if t["importance"]=="Urgent" else "○"} {t["name"]}</span></div>',unsafe_allow_html=True)
                        if cb.button("✓",key=f"vos_td_{i}"):
                            tasks[i]['status']='Finished'; save_json(fp("brief_tasks.json"),tasks); st.rerun()
            with col2:
                st.markdown('<div class="s-label">Notes</div>',unsafe_allow_html=True)
                with st.form("new_note",clear_on_submit=True):
                    nt=st.text_area("New Note",height=80,key="vos_nt")
                    if st.form_submit_button("Save"):
                        if nt: notes.append({"text":nt,"date":now.strftime("%Y-%m-%d %H:%M")}); save_json(fp("brief_notes.json"),notes); st.rerun()
                for n in reversed(notes[-6:]):
                    st.markdown(f'<div class="v-card v-card-a" style="margin-bottom:2px;"><div style="font-size:0.82rem;color:#ccc;">{n["text"]}</div><div style="font-family:Space Mono,monospace;font-size:0.58rem;color:#333;margin-top:0.3rem;">{n["date"]}</div></div>',unsafe_allow_html=True)

        elif page == "Calendar":
            st.markdown('<div class="s-label">Calendar</div>',unsafe_allow_html=True)
            col_prev,col_title,col_next=st.columns([1,4,1])
            if col_prev.button("◀",key="cal_prev"):
                if st.session_state.cal_month==1: st.session_state.cal_month=12; st.session_state.cal_year-=1
                else: st.session_state.cal_month-=1
                st.rerun()
            if col_next.button("▶",key="cal_next"):
                if st.session_state.cal_month==12: st.session_state.cal_month=1; st.session_state.cal_year+=1
                else: st.session_state.cal_month+=1
                st.rerun()
            yr=st.session_state.cal_year; mo=st.session_state.cal_month
            col_title.markdown(f'<div style="font-family:Space Mono,monospace;font-size:1rem;color:#ffaa00;letter-spacing:3px;text-align:center;padding:0.4rem 0;">{datetime(yr,mo,1).strftime("%B %Y").upper()}</div>',unsafe_allow_html=True)
            cal_matrix=cal_lib.monthcalendar(yr,mo)
            cols=st.columns(7)
            for i,d in enumerate(["MON","TUE","WED","THU","FRI","SAT","SUN"]):
                cols[i].markdown(f'<div style="font-family:Space Mono,monospace;font-size:0.58rem;color:#444;text-align:center;letter-spacing:2px;padding:0.3rem 0;">{d}</div>',unsafe_allow_html=True)
            cal_evts=st.session_state.cal_events
            for week in cal_matrix:
                cols=st.columns(7)
                for i,day in enumerate(week):
                    if day==0: cols[i].markdown('<div style="padding:0.5rem;"></div>',unsafe_allow_html=True)
                    else:
                        dk=f"{yr}-{mo:02d}-{day:02d}"; has_ev=dk in cal_evts and len(cal_evts[dk])>0
                        is_today=(day==now.day and mo==now.month and yr==now.year)
                        border="2px solid #ffaa00" if is_today else ("1px solid #44ff88" if has_ev else "1px solid #141414")
                        bg="#1a0f00" if is_today else ("#081508" if has_ev else "#0e0e0e")
                        color="#ffaa00" if is_today else ("#44ff88" if has_ev else "#555")
                        dot='<div style="width:4px;height:4px;background:#44ff88;border-radius:50%;margin:2px auto 0;"></div>' if has_ev else ""
                        cols[i].markdown(f'<div style="background:{bg};border:{border};padding:0.4rem 0.2rem;text-align:center;min-height:48px;"><div style="font-family:Space Mono,monospace;font-size:0.75rem;color:{color};">{day}</div>{dot}</div>',unsafe_allow_html=True)
            st.markdown("<br>",unsafe_allow_html=True)
            c1,c2=st.columns(2)
            with c1:
                sel_date=st.date_input("Select Date",value=now.date(),key="cal_sel_date")
                ev_text=st.text_input("Event",key="cal_ev_text"); ev_time=st.text_input("Time (optional)",key="cal_ev_time")
                if st.button("Save Event",key="cal_save"):
                    if ev_text:
                        dk=sel_date.strftime("%Y-%m-%d")
                        if dk not in cal_evts: cal_evts[dk]=[]
                        cal_evts[dk].append({"text":ev_text,"time":ev_time,"created":now.strftime("%Y-%m-%d %H:%M")})
                        save_json(fp("calendar.json"),cal_evts); st.success(f"Saved for {dk}"); st.rerun()
            with c2:
                st.markdown('<div style="font-family:Space Mono,monospace;font-size:0.6rem;color:#444;letter-spacing:2px;margin-bottom:0.5rem;">UPCOMING</div>',unsafe_allow_html=True)
                today_str=now.strftime("%Y-%m-%d"); upcoming={k:v for k,v in cal_evts.items() if k>=today_str}
                for dk in sorted(upcoming.keys())[:6]:
                    for ev in upcoming[dk]:
                        t_str=f" · {ev['time']}" if ev.get('time') else ""
                        st.markdown(f'<div class="v-card v-card-g" style="padding:0.5rem 0.8rem;margin-bottom:2px;"><div style="font-size:0.78rem;color:#44ff88;">{ev["text"]}</div><div style="font-family:Space Mono,monospace;font-size:0.58rem;color:#333;">{dk}{t_str}</div></div>',unsafe_allow_html=True)

        elif page == "Search":
            q=st.text_input("Search...",key="vos_srch")
            if q:
                enc_q=q.replace(' ','+')
                st.markdown(f'<a href="https://www.google.com/search?q={enc_q}" target="_blank" style="text-decoration:none;"><div class="v-card v-card-a" style="text-align:center;font-family:Space Mono,monospace;font-size:0.7rem;letter-spacing:2px;color:#ffaa00;">SEARCH GOOGLE → {q.upper()}</div></a>',unsafe_allow_html=True)
            links=[("Google","https://www.google.com"),("The Guardian","https://www.theguardian.com"),("TT Stock Exchange","https://www.stockex.co.tt"),("TT Weather","https://www.meteorology.gov.tt"),("BMobile","https://www.bmobile.co.tt"),("WASA","https://www.wasa.gov.tt"),("T&TEC","https://www.ttec.co.tt"),("Republic Bank","https://www.republictt.com")]
            c1,c2=st.columns(2)
            for i,(label,url) in enumerate(links):
                col=c1 if i%2==0 else c2
                col.markdown(f'<a href="{url}" target="_blank" style="text-decoration:none;"><div class="news-card" style="margin-bottom:2px;"><div class="news-headline" style="font-size:0.8rem;">{label}</div><div class="news-stamp">{url}</div></div></a>',unsafe_allow_html=True)

    elif mode_vos == "Command":
        if page == "Dashboard":
            c1,c2,c3,c4,c5=st.columns(5)
            mc="g" if health['mood']>=7 else ("a" if health['mood']>=4 else "r")
            c1.markdown(f'<div class="stat-block"><div class="stat-val">{health["water"]}/{health.get("hydration_goal",8)}</div><div class="stat-lbl">Hydration</div></div>',unsafe_allow_html=True)
            c2.markdown(f'<div class="stat-block"><div class="stat-val {mc}">{health["mood"]}/10</div><div class="stat-lbl">Mood</div></div>',unsafe_allow_html=True)
            c3.markdown(f'<div class="stat-block"><div class="stat-val w">{health["heart_rate"]}</div><div class="stat-lbl">BPM</div></div>',unsafe_allow_html=True)
            c4.markdown(f'<div class="stat-block"><div class="stat-val b">{health["steps"]}</div><div class="stat-lbl">Steps</div></div>',unsafe_allow_html=True)
            c5.markdown(f'<div class="stat-block"><div class="stat-val">{health["sleep_hrs"]}h</div><div class="stat-lbl">Sleep</div></div>',unsafe_allow_html=True)
            col_l,col_r=st.columns([2,1],gap="large")
            with col_l:
                st.markdown('<div class="s-label">Active Goals</div>',unsafe_allow_html=True)
                ag=[g for g in st.session_state.goals if g['status']=='Active']
                for g in ag[:5]:
                    pct=g.get('progress',0); bc="g" if pct>=70 else ("a" if pct>=30 else "r")
                    st.markdown(f'<div class="v-card v-card-a"><div style="display:flex;justify-content:space-between;"><span style="font-size:0.85rem;font-weight:500;">{g["name"]}</span><span class="vpill vpill-a">{pct}%</span></div><div class="v-bar-wrap"><div class="v-bar-fill {bc}" style="width:{pct}%;"></div></div><div style="font-family:Space Mono,monospace;font-size:0.58rem;color:#333;">{g.get("category","—")} · Due: {g.get("due","—")}</div></div>',unsafe_allow_html=True)
                st.markdown('<div class="s-label">Recent Thoughts</div>',unsafe_allow_html=True)
                for t in reversed(st.session_state.thoughts[-3:]):
                    st.markdown(f'<div class="thought-block">{t["text"]}<div class="thought-stamp">{t.get("mood_tag","—")} · {t["date"]}</div></div>',unsafe_allow_html=True)
            with col_r:
                st.markdown('<div class="s-label">Alerts</div>',unsafe_allow_html=True)
                for al in alerts[:6]:
                    cls="v-card-r" if al['level']=='critical' else "v-card-a"
                    st.markdown(f'<div class="{cls} v-card" style="padding:0.6rem 1rem;margin-bottom:2px;font-size:0.78rem;">{al["icon"]} {al["msg"]}</div>',unsafe_allow_html=True)
                if not alerts: st.markdown('<div class="v-card v-card-g" style="padding:0.6rem 1rem;color:#44ff88;font-size:0.78rem;">✓ All clear</div>',unsafe_allow_html=True)
                st.markdown('<div class="s-label">Net Worth</div>',unsafe_allow_html=True)
                tf=st.session_state.tfinance; ta=sum(a.get('value',0) for a in tf.get('assets',[])); td=sum(d.get('amount',0) for d in tf.get('debts',[])); nw=ta-td
                nc="g" if nw>=0 else "r"
                st.markdown(f'<div class="v-card"><div class="v-row"><span class="v-row-label">Assets</span><span class="v-row-val g">${ta:,.0f}</span></div><div class="v-row"><span class="v-row-label">Debts</span><span class="v-row-val r">${td:,.0f}</span></div><div class="v-row"><span class="v-row-label">Net Worth</span><span class="v-row-val {nc}">${nw:,.0f}</span></div></div>',unsafe_allow_html=True)

        elif page == "Health":
            t1,t2,t3=st.tabs(["Vitals","Hydration & Sleep","Medications"])
            with t1:
                c1,c2,c3=st.columns(3)
                health['heart_rate']=c1.number_input("Heart Rate BPM",40,200,health['heart_rate'],key="h_hr")
                health['steps']=c1.number_input("Steps",0,value=health['steps'],key="h_st")
                health['weight']=c2.number_input("Weight kg",0.0,value=float(health['weight']),format="%.1f",key="h_wt")
                health['temp']=c2.number_input("Body Temp °C",35.0,42.0,float(health['temp']),format="%.1f",key="h_tp")
                health['mood']=c3.slider("Mood 1-10",1,10,health['mood'],key="h_md")
                health['sleep_hrs']=c3.number_input("Sleep hrs",0.0,24.0,float(health['sleep_hrs']),format="%.1f",key="h_sl")
                if st.button("Save Vitals",key="h_save"): save_health(); st.success("✅ Saved"); st.rerun()
                flags=[]
                if health['temp']>37.5: flags.append(f"🌡️ Temp {health['temp']}°C")
                if health['heart_rate']>100: flags.append(f"💓 HR {health['heart_rate']}")
                if health['mood']<=3: flags.append("🧠 Low mood")
                if health['sleep_hrs']<5: flags.append(f"😴 {health['sleep_hrs']}h sleep")
                for f in flags: st.markdown(f'<div class="v-card v-card-r" style="padding:0.6rem 1rem;font-size:0.8rem;">{f}</div>',unsafe_allow_html=True)
                if not flags: st.markdown('<div class="v-card v-card-g" style="padding:0.6rem 1rem;font-size:0.8rem;color:#44ff88;">✓ Vitals normal</div>',unsafe_allow_html=True)
            with t2:
                health['hydration_goal']=st.number_input("Daily Goal (glasses)",1,20,health.get('hydration_goal',8),key="h_hg")
                health['water']=st.number_input("Glasses Today",0,30,health['water'],key="h_wt2")
                pct=min(health['water']/health['hydration_goal'],1.0); color="g" if pct>=0.8 else ("a" if pct>=0.5 else "r")
                st.markdown(f'<div class="v-card"><div class="v-bar-wrap"><div class="v-bar-fill {color}" style="width:{int(pct*100)}%;"></div></div><div style="font-family:Space Mono,monospace;font-size:0.65rem;color:#444;text-align:right;">{int(pct*100)}%</div></div>',unsafe_allow_html=True)
                c1,c2=st.columns(2)
                if c1.button("Add Glass 💧",key="h_glass"): health['water']+=1; save_health(); st.rerun()
                if c2.button("Save Hydration",key="h_hyd_save"): save_health(); st.rerun()
                st.markdown('<div class="s-label">Sleep Timer</div>',unsafe_allow_html=True)
                if not health.get('sleep_running'):
                    if st.button("▶ Start Sleep",key="h_sleep_start"):
                        health['sleep_start']=now.strftime("%Y-%m-%d %H:%M"); health['sleep_running']=True; save_health(); st.rerun()
                else:
                    st.markdown(f'<div class="v-card v-card-g" style="font-family:Space Mono,monospace;font-size:0.65rem;color:#44ff88;">😴 Started: {health["sleep_start"]}</div>',unsafe_allow_html=True)
                    if st.button("⏹ Stop & Log",key="h_sleep_stop"):
                        try:
                            hrs=round((now-datetime.strptime(health['sleep_start'],"%Y-%m-%d %H:%M")).seconds/3600,1)
                            health['sleep_hrs']=hrs; health['sleep_running']=False; health['sleep_start']=None; save_health(); st.success(f"Logged {hrs}h"); st.rerun()
                        except: pass
            with t3:
                meds=st.session_state.meds
                with st.form("add_med",clear_on_submit=True):
                    c1,c2,c3=st.columns(3)
                    mn=c1.text_input("Medication"); md=c2.text_input("Dose"); mf=c3.text_input("Frequency")
                    if st.form_submit_button("Add"):
                        if mn: meds.append({"name":mn,"dose":md,"frequency":mf}); save_json(fp("meds.json"),meds); st.rerun()
                for med in meds:
                    st.markdown(f'<div class="v-card v-card-a" style="padding:0.6rem 1rem;font-size:0.82rem;">💊 {med["name"]} — {med["dose"]} {med["frequency"]}</div>',unsafe_allow_html=True)

        elif page == "Nutrition":
            meals=st.session_state.meals
            with st.form("log_meal",clear_on_submit=True):
                c1,c2,c3=st.columns(3)
                mn=c1.text_input("Meal/Food",key="vos_mn"); mc2=c2.number_input("Calories",min_value=0,key="vos_mc"); mt=c3.selectbox("Type",["Breakfast","Lunch","Dinner","Snack"],key="vos_mt")
                if st.form_submit_button("Log Meal"):
                    if mn: meals.append({"name":mn,"calories":mc2,"type":mt,"date":now.strftime("%Y-%m-%d %H:%M")}); save_json(fp("meals.json"),meals); st.rerun()
            today_m=[m for m in meals if m['date'].startswith(now.strftime("%Y-%m-%d"))]; total_c=sum(m['calories'] for m in today_m)
            c1,c2,c3=st.columns(3)
            c1.markdown(f'<div class="stat-block"><div class="stat-val">{total_c}</div><div class="stat-lbl">Calories Today</div></div>',unsafe_allow_html=True)
            c2.markdown(f'<div class="stat-block"><div class="stat-val w">{len(today_m)}</div><div class="stat-lbl">Meals Logged</div></div>',unsafe_allow_html=True)
            rem=max(0,2000-total_c)
            c3.markdown(f'<div class="stat-block"><div class="stat-val {"g" if rem>0 else "r"}">{rem}</div><div class="stat-lbl">Remaining</div></div>',unsafe_allow_html=True)
            for m in today_m:
                st.markdown(f'<div class="v-card v-card-a"><div style="display:flex;justify-content:space-between;"><span>{m["name"]}</span><span class="vpill vpill-a">{m["calories"]} kcal</span></div><div style="font-family:Space Mono,monospace;font-size:0.58rem;color:#333;">{m["type"]} · {m["date"]}</div></div>',unsafe_allow_html=True)

        elif page == "Goals":
            goals=st.session_state.goals
            with st.form("add_goal",clear_on_submit=True):
                c1,c2=st.columns(2)
                gn=c1.text_input("Goal Name",key="vos_gn"); gc=c2.selectbox("Category",["Health","Finance","Career","Learning","Personal","Other"],key="vos_gc")
                c3,c4=st.columns(2); gt=c3.text_input("Target",key="vos_gt"); gd=c4.text_input("Due YYYY-MM-DD",key="vos_gd")
                if st.form_submit_button("Add Goal"):
                    if gn: goals.append({"name":gn,"category":gc,"target":gt,"due":gd,"progress":0,"status":"Active","wins":[]}); save_json(fp("goals.json"),goals); st.rerun()
            ag=[g for g in goals if g['status']=='Active']; cg=[g for g in goals if g['status']=='Complete']
            if ag:
                st.markdown('<div class="s-label">Active</div>',unsafe_allow_html=True)
                for i,g in enumerate(goals):
                    if g['status']!='Active': continue
                    pct=g.get('progress',0); bc="g" if pct>=70 else ("a" if pct>=30 else "r")
                    c1,c2,c3=st.columns([4,2,1])
                    c1.markdown(f'<div class="v-card v-card-a"><div style="font-weight:600;">{g["name"]}</div><div class="v-bar-wrap"><div class="v-bar-fill {bc}" style="width:{pct}%;"></div></div><div style="font-family:Space Mono,monospace;font-size:0.58rem;color:#333;">{g["category"]} · {pct}% · Due: {g.get("due","—")}</div></div>',unsafe_allow_html=True)
                    np2=c2.slider("",0,100,pct,key=f"vos_gp_{i}")
                    if np2!=pct: goals[i]['progress']=np2; save_json(fp("goals.json"),goals); st.rerun()
                    if c3.button("✓",key=f"vos_gd_{i}"): goals[i]['status']='Complete'; save_json(fp("goals.json"),goals); st.rerun()
            if cg:
                st.markdown('<div class="s-label">Complete</div>',unsafe_allow_html=True)
                for g in cg: st.markdown(f'<div class="v-card v-card-g" style="padding:0.6rem 1rem;color:#44ff88;">✓ {g["name"]}</div>',unsafe_allow_html=True)

        elif page == "Mind":
            thoughts=st.session_state.thoughts
            t1,t2=st.tabs(["Thought Log","Mood Trend"])
            with t1:
                moods=["😊 Positive","😐 Neutral","😔 Low","😤 Frustrated","🤩 Energized","😰 Anxious","😌 Calm"]
                with st.form("add_thought",clear_on_submit=True):
                    tt=st.text_area("What's on your mind?",height=100,key="vos_tht"); tm=st.selectbox("Mood",moods,key="vos_thm")
                    if st.form_submit_button("Lock Thought"):
                        if tt: thoughts.append({"text":tt,"mood_tag":tm,"date":now.strftime("%Y-%m-%d %H:%M")}); save_json(fp("thoughts.json"),thoughts); st.rerun()
                for t in reversed(thoughts[-10:]):
                    st.markdown(f'<div class="thought-block">{t["text"]}<div class="thought-stamp">{t.get("mood_tag","—")} · {t["date"]}</div></div>',unsafe_allow_html=True)
            with t2:
                if thoughts:
                    mm={"😊 Positive":8,"😐 Neutral":5,"😔 Low":2,"😤 Frustrated":3,"🤩 Energized":9,"😰 Anxious":3,"😌 Calm":7}
                    df=pd.DataFrame([{"date":t['date'][:10],"score":mm.get(t['mood_tag'],5)} for t in thoughts])
                    df=df.groupby('date')['score'].mean().reset_index()
                    if not df.empty: st.line_chart(df.set_index('date')['score'])

        elif page == "Ideas":
            ideas=st.session_state.ideas
            with st.form("add_idea",clear_on_submit=True):
                it=st.text_input("Idea Title",key="vos_it"); ib=st.text_area("Describe",height=80,key="vos_ib"); ig=st.text_input("Tags (comma separated)",key="vos_ig")
                if st.form_submit_button("Capture"):
                    if it:
                        ni={"title":it,"body":ib,"tags":ig,"date":now.strftime("%Y-%m-%d %H:%M"),"links":[]}
                        ntags=[t.strip().lower() for t in ig.split(",") if t.strip()]
                        for ex in ideas:
                            xt=[t.strip().lower() for t in ex.get('tags','').split(",") if t.strip()]
                            ov=set(ntags)&set(xt)
                            if ov: ni['links'].append(f"Linked to '{ex['title']}' via {', '.join(ov)}")
                        ideas.insert(0,ni); save_json(fp("ideas.json"),ideas); st.rerun()
            srch=st.text_input("Search ideas...",key="vos_idea_srch")
            filt=[i for i in ideas if not srch or srch.lower() in i['title'].lower() or srch.lower() in i['body'].lower()]
            for idea in filt:
                links_html='<div style="font-family:Space Mono,monospace;font-size:0.6rem;color:#4488ff;margin-top:0.3rem;">🔗 '+'·'.join(idea["links"])+'</div>' if idea.get("links") else ""
                st.markdown(f'<div class="v-card v-card-b"><div style="font-weight:600;color:#4488ff;">{idea["title"].upper()}</div><div style="font-size:0.82rem;color:#888;margin-top:0.3rem;">{idea["body"]}</div>{links_html}<div style="font-family:Space Mono,monospace;font-size:0.58rem;color:#333;margin-top:0.4rem;">Tags: {idea.get("tags","—")} · {idea["date"]}</div></div>',unsafe_allow_html=True)

        elif page == "Social":
            social=st.session_state.social
            t1,t2=st.tabs(["Contacts","Events"])
            with t1:
                with st.form("add_contact",clear_on_submit=True):
                    c1,c2,c3=st.columns(3); cn=c1.text_input("Name",key="vos_cn"); cr=c2.selectbox("Relation",["Friend","Family","Colleague","Client","Mentor","Other"],key="vos_cr"); cb2=c3.text_input("Birthday MM-DD",key="vos_cb")
                    cl_=st.text_input("Last Contact YYYY-MM-DD",key="vos_cl"); cn2=st.text_area("Notes",height=50,key="vos_cn2")
                    if st.form_submit_button("Add Contact"):
                        if cn: social['contacts'].append({"name":cn,"relation":cr,"birthday":cb2,"last_contact":cl_,"notes":cn2}); save_json(fp("social.json"),social); st.rerun()
                for c in social['contacts']:
                    bs=False
                    if c.get('birthday'):
                        try:
                            bd=datetime.strptime(f"{now.year}-{c['birthday']}","%Y-%m-%d")
                            if 0<=(bd.date()-now.date()).days<=14: bs=True
                        except: pass
                    cls="v-card-a" if bs else "v-card"
                    st.markdown(f'<div class="{cls} v-card"><div style="display:flex;justify-content:space-between;"><span style="font-weight:500;">{c["name"]}</span><span class="vpill vpill-b">{c["relation"]}</span></div><div style="font-family:Space Mono,monospace;font-size:0.58rem;color:#444;margin-top:0.3rem;">Last: {c.get("last_contact","—")} · Birthday: {c.get("birthday","—")} {"🎂" if bs else ""}</div></div>',unsafe_allow_html=True)
            with t2:
                with st.form("add_soc_event",clear_on_submit=True):
                    c1,c2,c3=st.columns(3); en=c1.text_input("Event",key="vos_en"); ed=c2.text_input("Date",key="vos_ed"); et=c3.selectbox("Type",["Birthday","Meeting","Deadline","Social","Other"],key="vos_et")
                    if st.form_submit_button("Add"):
                        if en: social['events'].append({"name":en,"date":ed,"type":et}); save_json(fp("social.json"),social); st.rerun()
                for e in sorted(social['events'],key=lambda x:x.get('date','9999'))[:10]:
                    st.markdown(f'<div class="v-card v-card-b"><div class="v-row"><span>{e["name"]}</span><span class="vpill vpill-b">{e["type"]}</span></div><div style="font-family:Space Mono,monospace;font-size:0.58rem;color:#444;">{e["date"]}</div></div>',unsafe_allow_html=True)

        elif page == "Decisions":
            decisions=st.session_state.decisions
            with st.form("decision",clear_on_submit=True):
                dt=st.text_input("Decision?",key="vos_dt")
                c1,c2=st.columns(2)
                dp=c1.text_area("✅ Pros (one per line)",height=80,key="vos_dp"); pw=c1.select_slider("Pro Weight",[1,2,3,4,5],value=3,key="vos_pw")
                dc=c2.text_area("❌ Cons (one per line)",height=80,key="vos_dc"); cw=c2.select_slider("Con Weight",[1,2,3,4,5],value=3,key="vos_cw")
                dg=st.slider("Gut 1-10",1,10,5,key="vos_dg"); du=st.selectbox("Urgency",["Low","Medium","High — now"],key="vos_du")
                if st.form_submit_button("Run Analysis"):
                    if dt:
                        pl=[p.strip() for p in dp.split('\n') if p.strip()]; cl_=[c.strip() for c in dc.split('\n') if c.strip()]
                        fs=((len(pl)*pw+dg)/(len(cl_)*cw+1))
                        rec="DO IT" if fs>=5 else ("PROCEED WITH CAUTION" if fs>=3 else ("THINK MORE" if fs>=1.5 else "AVOID"))
                        decisions.append({"title":dt,"pros":dp,"cons":dc,"gut":dg,"recommendation":rec,"urgency":du,"date":now.strftime("%Y-%m-%d %H:%M")}); save_json(fp("decisions.json"),decisions); st.rerun()
            for d in reversed(decisions[:5]):
                rc={"DO IT":"vpill-g","PROCEED WITH CAUTION":"vpill-a","THINK MORE":"vpill-p","AVOID":"vpill-r"}.get(d['recommendation'],"vpill-a")
                vc={"DO IT":"v-card-g","PROCEED WITH CAUTION":"v-card-a","THINK MORE":"v-card-p","AVOID":"v-card-r"}.get(d['recommendation'],"v-card-a")
                st.markdown(f'<div class="{vc} v-card"><div style="display:flex;justify-content:space-between;align-items:center;"><span style="font-weight:600;">{d["title"]}</span><span class="vpill {rc}">{d["recommendation"]}</span></div><div style="font-size:0.78rem;color:#888;margin-top:0.4rem;"><b>Pros:</b> {d["pros"][:80]}</div><div style="font-size:0.78rem;color:#888;"><b>Cons:</b> {d["cons"][:80]}</div><div style="font-family:Space Mono,monospace;font-size:0.58rem;color:#444;margin-top:0.4rem;">Gut: {d["gut"]}/10 · {d["date"]}</div></div>',unsafe_allow_html=True)

        elif page == "Life Log":
            c1,c2,c3,c4=st.columns(4)
            c1.markdown(f'<div class="stat-block"><div class="stat-val w">{len(st.session_state.thoughts)}</div><div class="stat-lbl">Thoughts</div></div>',unsafe_allow_html=True)
            c2.markdown(f'<div class="stat-block"><div class="stat-val w">{len(st.session_state.ideas)}</div><div class="stat-lbl">Ideas</div></div>',unsafe_allow_html=True)
            c3.markdown(f'<div class="stat-block"><div class="stat-val w">{len(st.session_state.goals)}</div><div class="stat-lbl">Goals</div></div>',unsafe_allow_html=True)
            c4.markdown(f'<div class="stat-block"><div class="stat-val w">{len(st.session_state.decisions)}</div><div class="stat-lbl">Decisions</div></div>',unsafe_allow_html=True)
            all_data={"exported":now.strftime("%Y-%m-%d %H:%M"),"health":health,"goals":st.session_state.goals,"thoughts":st.session_state.thoughts,"ideas":st.session_state.ideas,"social":st.session_state.social,"decisions":st.session_state.decisions}
            st.download_button("Export All Data",json.dumps(all_data,indent=2),f"vectoros_{now.strftime('%Y%m%d')}.json","application/json",key="vos_export")
            st.markdown('<div class="s-label">Reset</div>',unsafe_allow_html=True)
            c1,c2,c3=st.columns(3)
            if c1.button("Clear Thoughts",key="vos_clr_th"): save_json(fp("thoughts.json"),[]); st.rerun()
            if c2.button("Clear Ideas",key="vos_clr_id"): save_json(fp("ideas.json"),[]); st.rerun()
            if c3.button("Clear Decisions",key="vos_clr_dc"): save_json(fp("decisions.json"),[]); st.rerun()

    elif mode_vos == "Network":
        def gen_identity():
            uid=str(uuid.uuid4()); seed=hashlib.sha256(uid.encode()).hexdigest()
            pub=hashlib.sha256(seed.encode()).hexdigest(); zkp=hashlib.sha256((pub+"ZKP").encode()).hexdigest()[:16]
            return {"node_id":uid,"public_key":pub,"zkp_proof":zkp,"created":now.strftime("%Y-%m-%d %H:%M:%S"),"status":"SOVEREIGN"}
        def trade_hash(t): return hashlib.sha256(json.dumps(t,sort_keys=True).encode()).hexdigest()[:12]

        if page == "Synapse ID":
            if not synapse.get("identity"):
                st.markdown('<div class="v-card"><div style="font-family:Space Mono,monospace;font-size:0.7rem;color:#444;">No sovereign identity initialized.</div></div>',unsafe_allow_html=True)
                if st.button("⚡ Initialize Sovereign Identity",key="syn_init"):
                    synapse["identity"]=gen_identity(); save_json(fp("synapse.json"),synapse); st.rerun()
            else:
                ident=synapse["identity"]
                for label,val,color in [("NODE ID",ident["node_id"],"#44ff88"),("PUBLIC KEY",ident["public_key"],"#44ff88"),("ZERO KNOWLEDGE PROOF",ident["zkp_proof"],"#ffaa00")]:
                    st.markdown(f'<div class="v-card v-card-g"><div style="font-family:Space Mono,monospace;font-size:0.6rem;color:#444;letter-spacing:2px;margin-bottom:0.5rem;">{label}</div><div class="syn-id" style="color:{color};">{val}</div></div>',unsafe_allow_html=True)
                c1,c2=st.columns(2)
                c1.download_button("Export ID",json.dumps({"public_key":ident["public_key"],"zkp_proof":ident["zkp_proof"]},indent=2),"synapse_id.json",key="dl_syn")
                if c2.button("Reset Identity",key="syn_reset"): synapse["identity"]=None; save_json(fp("synapse.json"),synapse); st.rerun()

        elif page == "Value Trades":
            with st.form("new_trade",clear_on_submit=True):
                c1,c2=st.columns(2)
                tf=c1.text_input("From",key="vos_tf"); to2=c1.text_input("Offering",key="vos_to"); tq=c1.number_input("Qty",min_value=0.1,step=0.5,key="vos_tq"); tu=c1.selectbox("Unit",["Hours","kWh","kg","Units"],key="vos_tu")
                tt2=c2.text_input("To",key="vos_tt2"); tr=c2.text_input("Requesting",key="vos_tr"); trq=c2.number_input("Qty Requested",min_value=0.1,step=0.5,key="vos_trq"); tru=c2.selectbox("Unit ",["Hours","kWh","kg","Units"],key="vos_tru")
                if st.form_submit_button("Execute Trade"):
                    if tf and to2 and tt2 and tr:
                        t={"from":tf,"offer":f"{tq} {tu} of {to2}","to":tt2,"request":f"{trq} {tru} of {tr}","timestamp":now.strftime("%Y-%m-%d %H:%M"),"hash":None}
                        t["hash"]=trade_hash(t); synapse["trades"].insert(0,t); save_json(fp("synapse.json"),synapse); st.rerun()
            for tr in synapse["trades"]:
                st.markdown(f'<div class="v-card v-card-b"><div style="font-family:Space Mono,monospace;font-size:0.58rem;color:#4488ff;margin-bottom:0.4rem;">HASH: {tr["hash"]}</div><div style="font-size:0.82rem;">{tr["from"]} → {tr["to"]}</div><div style="font-size:0.78rem;color:#888;margin-top:0.3rem;"><span style="color:#44ff88;">{tr["offer"]}</span> ↔ <span style="color:#ffaa00;">{tr["request"]}</span></div><div style="font-family:Space Mono,monospace;font-size:0.58rem;color:#333;">{tr["timestamp"]}</div></div>',unsafe_allow_html=True)

        elif page == "Nodes":
            with st.form("add_node",clear_on_submit=True):
                c1,c2,c3=st.columns(3); nn=c1.text_input("Node Name",key="vos_nn"); nl=c2.text_input("Location",key="vos_nl"); ns=c3.selectbox("Status",["Online","Offline"],key="vos_ns")
                if st.form_submit_button("Add Node"):
                    if nn: synapse["nodes"].append({"name":nn,"location":nl,"status":ns,"id":hashlib.sha256(nn.encode()).hexdigest()[:8],"added":now.strftime("%Y-%m-%d %H:%M")}); save_json(fp("synapse.json"),synapse); st.rerun()
            online=[n for n in synapse["nodes"] if n['status']=='Online']
            c1,c2,c3=st.columns(3)
            c1.markdown(f'<div class="stat-block"><div class="stat-val w">{len(synapse["nodes"])}</div><div class="stat-lbl">Total Nodes</div></div>',unsafe_allow_html=True)
            c2.markdown(f'<div class="stat-block"><div class="stat-val g">{len(online)}</div><div class="stat-lbl">Online</div></div>',unsafe_allow_html=True)
            c3.markdown(f'<div class="stat-block"><div class="stat-val a">{min(int(len(online)/max(len(synapse["nodes"]),1)*100),100)}%</div><div class="stat-lbl">Network Health</div></div>',unsafe_allow_html=True)
            for node in synapse["nodes"]:
                cls="v-card-g" if node['status']=='Online' else "v-card-r"; dot="●" if node['status']=='Online' else "○"
                st.markdown(f'<div class="{cls} v-card" style="padding:0.6rem 1rem;"><span style="font-family:Space Mono,monospace;font-size:0.65rem;">{dot} {node["name"]} · {node.get("location","—")} · ID:{node["id"]}</span></div>',unsafe_allow_html=True)

        elif page == "Truth Feed":
            with st.form("add_event_tf",clear_on_submit=True):
                et2=st.text_input("Event/Claim",key="vos_et2"); es=st.text_input("Your Source/Location",key="vos_es"); ed2=st.text_area("Details",height=60,key="vos_ed2")
                if st.form_submit_button("Submit for Corroboration"):
                    if et2 and es:
                        ex=next((e for e in synapse["feed"] if e['title'].lower()==et2.lower()),None)
                        if ex: ex["sources"].append({"source":es,"detail":ed2,"time":now.strftime("%Y-%m-%d %H:%M")}); ex["corroborations"]=len(ex["sources"])
                        else: synapse["feed"].insert(0,{"title":et2,"sources":[{"source":es,"detail":ed2,"time":now.strftime("%Y-%m-%d %H:%M")}],"corroborations":1,"created":now.strftime("%Y-%m-%d %H:%M")})
                        save_json(fp("synapse.json"),synapse); st.rerun()
            verified=[e for e in synapse["feed"] if e['corroborations']>=3]; pending=[e for e in synapse["feed"] if e['corroborations']<3]
            if verified:
                st.markdown('<div class="s-label">✓ Verified (3+ sources)</div>',unsafe_allow_html=True)
                for e in verified: st.markdown(f'<div class="v-card v-card-g"><div style="font-weight:500;color:#44ff88;">{e["title"]}</div><div style="font-family:Space Mono,monospace;font-size:0.58rem;color:#2a5a2a;">{e["corroborations"]} corroborations · {e["created"]}</div></div>',unsafe_allow_html=True)
            if pending:
                st.markdown('<div class="s-label">⏳ Pending Corroboration</div>',unsafe_allow_html=True)
                for e in pending: st.markdown(f'<div class="v-card v-card-a"><div>{e["title"]}</div><div style="font-family:Space Mono,monospace;font-size:0.58rem;color:#555;">{e["corroborations"]}/3 · needs {3-e["corroborations"]} more</div></div>',unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="vos-footer">
    VECTOR OS · TRANSPARENCY ENGINE · CRM · AGENTIC AI (50 MODULES) · TT MARKET · PERSONAL OS
    · TRINIDAD & TOBAGO · {now.strftime("%B %Y").upper()} · ALL SYSTEMS UNIFIED
</div>
""", unsafe_allow_html=True)
