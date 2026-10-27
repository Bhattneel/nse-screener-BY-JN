import streamlit as st
import streamlit.components.v1 as components
import requests
from bs4 import BeautifulSoup
import time
import re
import csv
import io
from datetime import datetime, timezone, timedelta
import html as _html
from concurrent.futures import ThreadPoolExecutor, as_completed

st.set_page_config(page_title="Breakout Desk · NSE", layout="wide", page_icon="📈")

TOP_N = 5
IST = timezone(timedelta(hours=5, minutes=30))

# Shared Memory Across All 2-3 Users on the Website (No Auto-Scan)
@st.cache_resource
def get_shared_store():
    return {"timestamp": None, "total_scanned": 0, "total_matched": 0, "results": []}

shared_store = get_shared_store()

# ------------------------------------------------------------------ PREMIUM THEME
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,800&family=Hanken+Grotesk:wght@400;500;600;700&display=swap');
:root { --bg:#062A21; --ink:#F2EDDA; --mut:#9DB8AC; --gold:#D8B35A; --gold2:#F4DB93; --up:#7BE3AB; --dn:#FF8F7E; --line:rgba(216,179,90,.28); }

.stApp { background:radial-gradient(1100px 560px at 85% -8%,#0F5A45 0%,transparent 60%),radial-gradient(900px 500px at 0% 100%,#0A4636 0%,transparent 55%),#062A21 !important;
  color:var(--ink) !important; font-family:'Hanken Grotesk',sans-serif; }
.block-container { max-width:1150px; padding-top:1.2rem; padding-bottom:3rem; }
#MainMenu, footer { visibility:hidden; }

.lbl { font:600 1.05rem 'Fraunces',serif; color:var(--gold2) !important; margin:16px 0 8px; display:flex; align-items:center; gap:12px; }
.lbl::after { content:""; flex:1; height:1px; background:linear-gradient(90deg,var(--line),transparent); }
[data-testid="stNumberInput"] label p, [data-testid="stTextArea"] label p, [data-testid="stCheckbox"] p, [data-testid="stRadio"] label p, [data-testid="stExpander"] summary p {
  color:var(--ink) !important; font-weight:600 !important; }
[data-baseweb="input"], [data-baseweb="base-input"], [data-baseweb="textarea"] { background:#041E17 !important; border-radius:10px !important; border:1px solid var(--line) !important; }
input, textarea { color:#F2EDDA !important; -webkit-text-fill-color:#F2EDDA !important; font-weight:600 !important; }
[data-testid="stNumberInput"] button { background:#093A2D !important; color:var(--gold2) !important; }
[data-testid="stExpander"] { border:1px solid var(--line) !important; border-radius:12px !important; background:rgba(4,30,23,.75) !important; }

.stButton>button { width:100%; border:0 !important; border-radius:6px 20px 6px 20px; padding:0.9rem;
  background:linear-gradient(110deg,#B88A2E,#F4DB93 35%,#D8B35A 55%,#B88A2E) !important; background-size:200% 100% !important;
  animation:foil 6s linear infinite; box-shadow:0 10px 30px rgba(216,179,90,.28); }
.stButton>button p, .stButton>button span { color:#1B1405 !important; font:800 1.08rem 'Fraunces',serif !important; }

.rs-head { margin:24px 0 14px; }
.rs-head h2 { font:800 clamp(1.4rem,3.2vw,2.1rem) 'Fraunces',serif; color:var(--gold2) !important; margin:0; }
.rs-head p { color:var(--mut) !important; margin:4px 0 0; font-size:.9rem; }
.rc { display:grid; grid-template-columns:60px 1.25fr 2fr 80px; gap:16px; align-items:center; padding:18px 20px; margin-bottom:14px;
  border:1px solid var(--line); border-radius:6px 20px 6px 20px; background:linear-gradient(135deg,rgba(9,58,45,.92),rgba(4,30,23,.95)); }
.rc.first { border:1.5px solid var(--gold); box-shadow:0 12px 34px rgba(216,179,90,.18); }
.rk { font:800 2.8rem/1 'Fraunces',serif; color:var(--gold); text-align:center; }
.mn h3 { font:700 1.45rem 'Fraunces',serif; margin:0; color:var(--ink) !important; }
.px { font:700 1.02rem 'Hanken Grotesk',sans-serif; color:var(--gold2) !important; margin:2px 0 10px; }
.gb { position:relative; height:6px; border-radius:9px; background:rgba(255,255,255,.12); }
.gb i { position:absolute; left:0; top:0; bottom:0; width:var(--w); border-radius:9px; background:linear-gradient(90deg,#7A5A1C,var(--gold2)); }
.gl { display:flex; justify-content:space-between; gap:8px; margin-top:6px; font-size:.75rem; color:var(--mut) !important; }
.lk { margin-top:10px; display:flex; gap:8px; flex-wrap:wrap; }
.lk a { color:#1B1405 !important; background:var(--gold2); text-decoration:none !important; font-weight:700; font-size:.78rem; padding:5px 12px; border-radius:4px 10px 4px 10px; }
.sts { display:grid; grid-template-columns:repeat(3,1fr); gap:10px 12px; }
.st span { display:block; font-size:.74rem; color:var(--mut) !important; }
.st b { font:700 1.1rem 'Fraunces',serif; color:var(--ink) !important; }
.st b.up { color:var(--up) !important; } .st b.dn { color:var(--dn) !important; }
.st em { display:block; font-style:normal; font-size:.7rem; color:var(--mut) !important; }
.sr { text-align:center; background:rgba(216,179,90,.1); border:1px solid var(--line); border-radius:12px; padding:10px 6px; }
.sr b { font:800 1.3rem 'Fraunces',serif; color:var(--gold2) !important; display:block; }
.sr span { font-size:.7rem; color:var(--mut) !important; }

@media (max-width:768px) {
  .rc { grid-template-columns:1fr; gap:12px; padding:16px; }
  .rk { font-size:1.8rem; text-align:left; }
  .sts { grid-template-columns:repeat(2,1fr); }
}
@keyframes foil { to { background-position:200% 0; } }
</style>
""", unsafe_allow_html=True)

HERO_HTML = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,800&family=Hanken+Grotesk:wght@400;600&display=swap');
*{box-sizing:border-box;margin:0;padding:0} body{background:transparent;font-family:'Hanken Grotesk',sans-serif;color:#F2EDDA;overflow:hidden}
.hero{position:relative;height:210px;padding:22px 24px;overflow:hidden;border:1px solid rgba(216,179,90,.38);border-radius:6px 24px 6px 24px;
 background:linear-gradient(135deg,rgba(8,52,41,.92),rgba(4,26,20,.96))}
.txt{position:relative;z-index:2;max-width:65%}
h1{font:800 clamp(22px,3.8vw,36px)/1.08 'Fraunces',serif}
h1 em{font-style:italic;font-weight:600;color:#F4DB93}
p{margin-top:8px;font-size:13.5px;line-height:1.45;color:#B9CEC4}
.facts{display:flex;flex-wrap:wrap;gap:6px 14px;margin-top:12px;font-size:12px;font-weight:600;color:#F4DB93}
.art{position:absolute;right:14px;top:10px;width:36%;height:185px;z-index:1;opacity:.85}
.art path,.art line{fill:none;stroke-linecap:round;stroke-linejoin:round}
.tl{stroke:#D8B35A;stroke-width:1.6;stroke-dasharray:6 7}
.coil{stroke:#F2EDDA;stroke-width:2.2;stroke-dasharray:1;stroke-dashoffset:1;animation:coil 6s ease-in-out infinite}
.brk{stroke:#7BE3AB;stroke-width:3.2;stroke-dasharray:1;stroke-dashoffset:1;filter:drop-shadow(0 0 6px #7BE3AB);animation:brk 6s ease-in-out infinite}
@keyframes coil{0%{stroke-dashoffset:1}50%,100%{stroke-dashoffset:0}}
@keyframes brk{0%,50%{stroke-dashoffset:1}80%,100%{stroke-dashoffset:0}}
@media(max-width:640px){.txt{max-width:100%}.art{opacity:.18;width:75%}}
</style>
<div class="hero">
 <div class="txt">
  <h1>The quiet before the <em>breakout.</em></h1>
  <p>100% Real NSE Data · Shared Team Terminal (1 Scan Updates All Devices)</p>
  <div class="facts"><span>◆ ₹10Cr+ Turnover</span><span>◆ 15D Consolidation</span><span>◆ 20%+ Profit YoY</span><span>◆ FII/DII Buying</span></div>
 </div>
 <svg class="art" viewBox="0 0 420 260" preserveAspectRatio="xMidYMid meet">
  <line class="tl" x1="20" y1="50" x2="300" y2="110"/><line class="tl" x1="20" y1="210" x2="300" y2="150"/>
  <path class="coil" pathLength="1" d="M20 130 L55 75 L90 185 L130 90 L170 165 L210 108 L250 148 L295 128"/>
  <path class="brk" pathLength="1" d="M295 128 L335 58 L355 84 L402 22"/>
 </svg>
</div>
"""
components.html(HERO_HTML, height=225)

DEFAULT_STOCKS = (
    "RELIANCE, TCS, HDFCBANK, ICICIBANK, INFY, BHARTIARTL, SBIN, LT, ITC, HINDUNILVR, "
    "TATAMOTORS, TRENT, BEL, HAL, ZOMATO, BAJFINANCE, MARUTI, SUNPHARMA, NTPC, TITAN, "
    "ADANIENT, POWERGRID, ULTRACEMCO, ASIANPAINT, COALINDIA, BAJAJ-AUTO, M&M, ONGC, "
    "ADANIPORTS, JSWSTEEL, TATASTEEL, GRASIM, HINDALCO, TECHM, WIPRO, DRREDDY, CIPLA, "
    "DIXON, POLYCAB, PERSISTENT, COFORGE, KPITTECH, VBL, CHOLAFIN, SIEMENS, ABB, PFC, RECLTD, "
    "CUMMINSIND, THERMAX, KAYNES, JYOTICNC, ANANTRAJ, NETWEB, ELECTCAST, GENUSPOWER, MCX, CDSL, "
    "BSE, ANGELONE, MOTILALOFS, MUTHOOTFIN, SUZLON, INOXWIND, APARINDS, KEI, SHREECEM, JINDALSTEL, "
    "TATAPOWER, TVSMOTOR, EICHERMOT, DIVISLAB, SBILIFE, HDFCLIFE, GODREJCP, DABUR, MARICO"
)

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

@st.cache_data(ttl=6 * 3600, show_spinner=False)
def load_nse_universe():
    for url in (
        "https://nsearchives.nseindia.com/content/equities/EQUITY_L.csv",
        "https://archives.nseindia.com/content/equities/EQUITY_L.csv",
    ):
        try:
            r = requests.get(url, headers=HEADERS, timeout=15)
            if r.status_code != 200:
                continue
            out = []
            for row in csv.DictReader(io.StringIO(r.text)):
                row = {(k or "").strip(): (v or "").strip() for k, v in row.items()}
                if row.get("SERIES") == "EQ" and row.get("SYMBOL"):
                    out.append(row["SYMBOL"].upper())
            if len(out) > 500:
                return out
        except Exception:
            continue
    raise ValueError("NSE list unavailable")

with st.expander("⚙️ Universe Settings", expanded=False):
    uni_mode = st.radio("Scan Mode:", ["High-Liquidity Institutional Universe (Fast - 20s)", "All NSE Stocks (Full Market - 3m)"], horizontal=True)
    symbols_input = st.text_area("Custom Symbols:", DEFAULT_STOCKS, height=70)

st.markdown("<div class='lbl'>Filters</div>", unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)
max_range = col1.number_input("Max 15D Range (%)", value=20.0, step=1.0)
min_profit_growth = col2.number_input("Min YoY Profit (%)", value=20.0, step=5.0)
min_turnover_cr = col3.number_input("Min Turnover (₹ Cr)", value=10.0, step=5.0)
secret_inst_mode = col4.checkbox("🔥 Smart Money Filter", value=True)

def get_yahoo_institutional_data(symbol):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}.NS?range=3mo&interval=1d"
    try:
        r = requests.get(url, headers=HEADERS, timeout=8)
        if r.status_code != 200:
            return None
        quote = r.json()["chart"]["result"][0]["indicators"]["quote"][0]
        opens, highs, lows, closes, vols = quote.get("open", []), quote.get("high", []), quote.get("low", []), quote.get("close", []), quote.get("volume", [])
        valid_days = [(o, h, l, c, v) for o, h, l, c, v in zip(opens, highs, lows, closes, vols) if None not in (o, h, l, c, v)]
        if len(valid_days) >= 50:
            sma_50 = sum(x[3] for x in valid_days[-50:]) / 50.0
        elif len(valid_days) >= 20:
            sma_50 = sum(x[3] for x in valid_days) / len(valid_days)
        else:
            return None

        last15 = valid_days[-15:]
        high_15, low_15, curr_price = max(x[1] for x in last15), min(x[2] for x in last15), last15[-1][3]
        avg_turnover_cr = sum((x[3] * x[4]) / 10000000 for x in last15) / 15.0
        cons_pct = ((high_15 - low_15) / low_15) * 100
        dist_from_breakout = ((high_15 - curr_price) / high_15) * 100

        up_vols = [x[4] for x in last15 if x[3] >= x[0]]
        down_vols = [x[4] for x in last15 if x[3] < x[0]]
        vol_ratio = round((sum(up_vols) / len(up_vols) if up_vols else 1) / max((sum(down_vols) / len(down_vols) if down_vols else 1), 1), 2)

        return {
            "LTP": round(curr_price, 2), "High15": round(high_15, 2), "Low15": round(low_15, 2),
            "Range": round(cons_pct, 2), "SMA50": round(sma_50, 2), "DistBreakout": round(dist_from_breakout, 2),
            "TurnoverCr": round(avg_turnover_cr, 2), "VolRatio": vol_ratio
        }
    except Exception:
        return None

def get_screener_data(symbol):
    for url in (f"https://www.screener.in/company/{symbol}/consolidated/", f"https://www.screener.in/company/{symbol}/"):
        try:
            r = requests.get(url, headers=HEADERS, timeout=10)
            if r.status_code != 200:
                continue
            soup = BeautifulSoup(r.text, "html.parser")
            q_sec = soup.find("section", {"id": "quarters"})
            profit_growth = None
            if q_sec:
                for row in q_sec.find_all("tr"):
                    if "Net Profit" in row.text:
                        cols = [c.text.strip().replace(",", "") for c in row.find_all("td")]
                        nums = [float(re.search(r"[-+]?\d*\.\d+|\d+", c).group(0)) if re.search(r"[-+]?\d*\.\d+|\d+", c) else None for c in cols[1:]]
                        if len(nums) >= 5 and nums[-1] is not None and nums[-5] is not None and nums[-5] > 0:
                            profit_growth = round(((nums[-1] - nums[-5]) / abs(nums[-5])) * 100, 2)
                        break

            sh_sec = soup.find("section", {"id": "shareholding"})
            fii_holding, fii_change, dii_change = 0.0, 0.0, 0.0
            if sh_sec:
                for row in sh_sec.find_all("tr"):
                    if "FIIs" in row.text:
                        cols = [c.text.strip().replace("%", "").replace(",", "") for c in row.find_all("td")]
                        nums = [float(re.search(r"[-+]?\d*\.\d+|\d+", c).group(0)) if re.search(r"[-+]?\d*\.\d+|\d+", c) else 0.0 for c in cols[1:]]
                        if len(nums) >= 1: fii_holding = nums[-1]
                        if len(nums) >= 2: fii_change = round(nums[-1] - nums[-2], 2)
                    elif "DIIs" in row.text:
                        cols = [c.text.strip().replace("%", "").replace(",", "") for c in row.find_all("td")]
                        nums = [float(re.search(r"[-+]?\d*\.\d+|\d+", c).group(0)) if re.search(r"[-+]?\d*\.\d+|\d+", c) else 0.0 for c in cols[1:]]
                        if len(nums) >= 2: dii_change = round(nums[-1] - nums[-2], 2)
            if profit_growth is not None or fii_holding > 0:
                return profit_growth, fii_holding, fii_change, dii_change
        except Exception:
            continue
    return None, 0.0, 0.0, 0.0

def card_html(idx, r):
    sym = r["Symbol"]
    span = r["High15"] - r["Low15"]
    pos = 100.0 if span <= 0 else min(100.0, max(0.0, (r["LTP"] - r["Low15"]) / span * 100))
    sm = r["SmartMoneyChg"]
    sm_txt = f"+{sm}%" if sm > 0 else f"{sm}%"
    sm_cls = "up" if sm > 0 else ("dn" if sm < 0 else "")
    fii_txt = f"+{r['FIIChg']}%" if r["FIIChg"] > 0 else f"{r['FIIChg']}%"
    vol_cls = "up" if r["VolRatio"] >= 1.0 else ""
    tv = _html.escape(f"https://in.tradingview.com/chart/?symbol=NSE%3A{sym}")
    sc = _html.escape(f"https://www.screener.in/company/{sym}/consolidated/")
    stats = [
        ("YoY profit", f"+{r['ProfitGrowth']}%", "up", ""),
        ("Daily turnover", f"₹{r['TurnoverCr']:,} Cr", "", ""),
        ("15-day range", f"{r['Range']}%", "", ""),
        ("Up/down vol", f"{r['VolRatio']}x", vol_cls, ""),
        ("FII holding", f"{r['FII']}%", "", f"{fii_txt} QoQ"),
        ("FII + DII chg", sm_txt, sm_cls, ""),
    ]
    cells = "".join(f"<div class='st'><span>{a}</span><b class='{c}'>{b}</b>{f'<em>{d}</em>' if d else ''}</div>" for a, b, c, d in stats)
    first = " first" if idx == 1 else ""
    return (
        f"<article class='rc{first}'>"
        f"<div class='rk'>#{idx}</div>"
        f"<div class='mn'><h3>{_html.escape(sym)}</h3><div class='px'>₹{r['LTP']:,.2f}</div>"
        f"<div class='gb' style='--w:{pos:.0f}%'><i></i></div>"
        f"<div class='gl'><span>Low: ₹{r['Low15']:,}</span><span>Breakout: ₹{r['High15']:,} ({r['DistBreakout']}% away)</span></div>"
        f"<div class='lk'><a href='{tv}' target='_blank'>📊 Open Chart</a>"
        f"<a href='{sc}' target='_blank'>🔍 Screener Proof</a></div></div>"
        f"<div class='sts'>{cells}</div>"
        f"<div class='sr'><b>{r['Score']}</b><span>SCORE</span></div>"
        f"</article>"
    )

st.markdown("<br>", unsafe_allow_html=True)
if st.button("🚀 RUN LIVE SCAN (Updates for All Users)", type="primary"):
    if uni_mode.startswith("All"):
        try:
            symbols = load_nse_universe()
        except Exception:
            symbols = [s.strip().upper() for s in DEFAULT_STOCKS.split(",") if s.strip()]
    else:
        symbols = [s.strip().upper() for s in symbols_input.split(",") if s.strip()]
    symbols = list(dict.fromkeys(symbols))

    with st.status("Scanning live market data...", expanded=True) as status:
        prog = st.progress(0)
        st.write(f"Step 1: Filtering price & turnover for {len(symbols):,} stocks...")
        tech_passed = []
        total, done = len(symbols), 0
        with ThreadPoolExecutor(max_workers=12) as pool:
            futures = {pool.submit(get_yahoo_institutional_data, s): s for s in symbols}
            for fut in as_completed(futures):
                sym = futures[fut]
                done += 1
                res = fut.result()
                if res and res["TurnoverCr"] >= min_turnover_cr and res["Range"] <= max_range:
                    if not (secret_inst_mode and (res["LTP"] < res["SMA50"] or res["DistBreakout"] > 8.0)):
                        res["Symbol"] = sym
                        tech_passed.append(res)
                if done % 10 == 0 or done == total:
                    prog.progress(done / total)
        
        st.write(f"Step 2: Scraping real Earnings & FII/DII data for {len(tech_passed)} stocks...")
        final_results = []
        for n, item in enumerate(tech_passed, 1):
            prog.progress(n / max(len(tech_passed), 1))
            p_growth, fii_hold, fii_chg, dii_chg = get_screener_data(item["Symbol"])
            time.sleep(0.35)
            if p_growth is not None and p_growth >= min_profit_growth:
                smart_money_net = round(fii_chg + dii_chg, 2)
                if secret_inst_mode and (fii_chg < 0 and smart_money_net <= 0):
                    continue
                item["ProfitGrowth"] = p_growth
                item["FII"] = fii_hold
                item["FIIChg"] = fii_chg
                item["SmartMoneyChg"] = smart_money_net
                score = (p_growth * 0.3) + (item["TurnoverCr"] * 0.05) + (smart_money_net * 5.0) + (item["VolRatio"] * 10.0) - item["DistBreakout"]
                item["Score"] = round(score, 1)
                final_results.append(item)

        final_results.sort(key=lambda x: x["Score"], reverse=True)
        shared_store["timestamp"] = datetime.now(IST).strftime("%d %b %Y, %I:%M %p IST")
        shared_store["total_scanned"] = total
        shared_store["total_matched"] = len(final_results)
        shared_store["results"] = final_results[:TOP_N]
        status.update(label="✅ Scan Complete & Shared Across All Users!", state="complete", expanded=False)

if shared_store["timestamp"] and shared_store["results"]:
    top = shared_store["results"]
    st.markdown(
        f"<div class='rs-head'><h2>Top {len(top)} Institutional Breakout Setups</h2>"
        f"<p>🕒 Last Scanned: <b>{shared_store['timestamp']}</b> &nbsp;|&nbsp; {shared_store['total_matched']} matched out of {shared_store['total_scanned']:,} stocks</p></div>"
        + "".join(card_html(i, r) for i, r in enumerate(top, 1)),
        unsafe_allow_html=True,
    )
elif shared_store["timestamp"]:
    st.warning(f"Last scan ({shared_store['timestamp']}) me strict filters par koi stock match nahi hua.")
else:
    st.info("👆 Click 'RUN LIVE SCAN' to scan live NSE data. Results will automatically display here for all team members.")