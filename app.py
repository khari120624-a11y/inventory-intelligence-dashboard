"""
Inventory Intelligence Dashboard
Streamlit Application for Enterprise Inventory Analytics, Demand Profiling, Stock-Out Risk, Overstock, and Forecasting.
"""

import os
import sys
import io
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.config import (
    CRITICAL_STOCKOUT_DAYS,
    LOW_STOCK_DAYS,
    OVERSTOCK_DAYS,
    SLOW_MOVING_DAYS,
    DEFAULT_LEAD_TIME_DAYS,
    STATUS_CRITICAL,
    STATUS_LOW_STOCK,
    STATUS_HEALTHY,
    STATUS_OVERSTOCK,
    STATUS_SLOW_MOVING,
    ALL_STATUSES,
    STATUS_COLORS,
    RISK_TIER_COLORS,
    RISK_TIER_LOW,
    RISK_TIER_MEDIUM,
    RISK_TIER_HIGH,
    RISK_TIER_CRITICAL
)
from src.data_loader import load_data_from_path, generate_data_profile, detect_column_mappings
from src.preprocessing import preprocess_inventory_data, save_processed_data
from src.analytics import compute_product_analytics, compute_category_analytics, compute_time_series_demand
from src.risk_engine import attach_risk_scores
from src.recommendations import attach_recommendations
from src.forecasting import forecast_product_demand
from src.export_engine import generate_powerbi_exports

# Page Configuration
st.set_page_config(
    page_title="Inventory Intelligence Dashboard",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── 3-D Robot Intro Animation ─────────────────────────────────────────────────
# Uses st.components.v1.html so JS executes freely (no Streamlit CSP blocking)
import streamlit.components.v1 as components

if "intro_shown" not in st.session_state:
    st.session_state.intro_shown = False

if not st.session_state.intro_shown:
    st.session_state.intro_shown = True
    components.html("""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800;900&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html,body{width:100%;height:100%;overflow:hidden;background:#000}
/* ── overlay ── */
#ov{position:fixed;inset:0;z-index:9999;background:radial-gradient(ellipse 120% 100% at 50% 60%,#0D1B3E 0%,#060B18 55%,#000 100%);display:flex;flex-direction:column;align-items:center;justify-content:center;overflow:hidden;transition:opacity 1s ease,transform 1s ease}
#ov.hide{opacity:0;transform:scale(1.06);pointer-events:none}
/* stars */
.stars{position:absolute;inset:0;background-image:radial-gradient(1px 1px at 8% 12%,rgba(255,255,255,.8) 0%,transparent 100%),radial-gradient(1px 1px at 20% 70%,rgba(255,255,255,.6) 0%,transparent 100%),radial-gradient(1px 1px at 35% 5%,rgba(56,189,248,.9) 0%,transparent 100%),radial-gradient(1px 1px at 50% 45%,rgba(255,255,255,.5) 0%,transparent 100%),radial-gradient(1px 1px at 62% 25%,rgba(192,132,252,.9) 0%,transparent 100%),radial-gradient(1px 1px at 75% 80%,rgba(255,255,255,.7) 0%,transparent 100%),radial-gradient(1px 1px at 88% 15%,rgba(56,189,248,.8) 0%,transparent 100%),radial-gradient(1.5px 1.5px at 15% 90%,rgba(56,189,248,.7) 0%,transparent 100%),radial-gradient(1.5px 1.5px at 45% 55%,rgba(192,132,252,.7) 0%,transparent 100%),radial-gradient(1.5px 1.5px at 70% 35%,rgba(255,255,255,.8) 0%,transparent 100%);animation:twinkle 4s ease-in-out infinite alternate}
@keyframes twinkle{from{opacity:.5}to{opacity:1}}
/* cash particles */
.cp{position:absolute;animation:cf linear infinite;opacity:0;filter:drop-shadow(0 0 6px rgba(52,211,153,.8));pointer-events:none}
@keyframes cf{0%{transform:translateY(110vh) rotate(0deg);opacity:0}10%{opacity:.9}90%{opacity:.6}100%{transform:translateY(-10vh) rotate(380deg);opacity:0}}
/* orbit rings */
.or{position:absolute;border-radius:50%;border:1px solid rgba(56,189,248,.12);animation:orb linear infinite;pointer-events:none}
.or::after{content:'';position:absolute;width:8px;height:8px;border-radius:50%;background:#38BDF8;top:-4px;left:50%;transform:translateX(-50%);box-shadow:0 0 12px #38BDF8}
.r1{width:200px;height:200px;top:50%;left:50%;margin:-100px 0 0 -100px;animation-duration:5s}
.r2{width:310px;height:310px;top:50%;left:50%;margin:-155px 0 0 -155px;animation-duration:9s;animation-direction:reverse}
.r3{width:440px;height:440px;top:50%;left:50%;margin:-220px 0 0 -220px;animation-duration:15s}
@keyframes orb{from{transform:rotate(0deg)}to{transform:rotate(360deg)}}
/* scene */
.scene{display:flex;flex-direction:column;align-items:center;position:relative;z-index:2;animation:si .9s cubic-bezier(.34,1.56,.64,1) both}
@keyframes si{from{transform:translateY(60px) scale(.85);opacity:0}to{transform:translateY(0) scale(1);opacity:1}}
/* robot */
.robot{position:relative;width:140px;animation:bob 2.2s ease-in-out infinite,sp 8s ease-in-out infinite}
@keyframes bob{0%,100%{transform:translateY(0)}50%{transform:translateY(-12px)}}
@keyframes sp{0%{transform:perspective(600px) rotateY(0deg) translateY(0)}25%{transform:perspective(600px) rotateY(14deg) translateY(-6px)}50%{transform:perspective(600px) rotateY(0deg) translateY(-12px)}75%{transform:perspective(600px) rotateY(-14deg) translateY(-6px)}100%{transform:perspective(600px) rotateY(0deg) translateY(0)}}
.ant{position:absolute;top:-24px;left:50%;transform:translateX(-50%);width:4px;height:20px;background:linear-gradient(180deg,#38BDF8,#1E40AF);border-radius:2px;box-shadow:0 0 8px #38BDF8}
.ant::after{content:'';position:absolute;top:-8px;left:50%;transform:translateX(-50%);width:12px;height:12px;border-radius:50%;background:radial-gradient(circle,#7DD3FC,#0EA5E9);box-shadow:0 0 16px #38BDF8,0 0 32px rgba(56,189,248,.6);animation:ap 1.1s ease-in-out infinite}
@keyframes ap{0%,100%{transform:translateX(-50%) scale(1);box-shadow:0 0 10px #38BDF8,0 0 22px rgba(56,189,248,.4)}50%{transform:translateX(-50%) scale(1.4);box-shadow:0 0 22px #38BDF8,0 0 44px rgba(56,189,248,.8)}}
.head{width:80px;height:65px;margin:0 auto;background:linear-gradient(160deg,#1E3A5F,#0F2040,#071628);border:2px solid rgba(56,189,248,.5);border-radius:14px 14px 8px 8px;position:relative;box-shadow:0 0 22px rgba(56,189,248,.25),0 4px 16px rgba(0,0,0,.6),inset 0 1px 0 rgba(255,255,255,.1)}
.head::before{content:'';position:absolute;top:12px;left:10px;right:10px;height:24px;background:linear-gradient(135deg,rgba(56,189,248,.12),rgba(99,102,241,.12));border:1px solid rgba(56,189,248,.4);border-radius:6px;box-shadow:0 0 14px rgba(56,189,248,.25) inset}
.eye{position:absolute;top:17px;width:14px;height:14px;border-radius:50%;background:radial-gradient(circle at 35% 35%,#7DD3FC,#0369A1);animation:eg 1.8s ease-in-out infinite}
.el{left:16px}.er{right:16px}
@keyframes eg{0%,100%{box-shadow:0 0 8px #38BDF8,0 0 16px rgba(56,189,248,.4)}50%{box-shadow:0 0 20px #38BDF8,0 0 40px rgba(56,189,248,.8)}}
.mouth{position:absolute;bottom:10px;left:50%;transform:translateX(-50%);width:34px;height:8px;border-radius:0 0 8px 8px;border:2px solid rgba(56,189,248,.5);border-top:none;overflow:hidden}
.mb{position:absolute;top:2px;left:2px;right:2px;height:3px;background:linear-gradient(90deg,#38BDF8,#818CF8,#C084FC,#38BDF8);background-size:300% 100%;border-radius:2px;animation:ms .8s linear infinite}
@keyframes ms{0%{background-position:0% 50%}100%{background-position:300% 50%}}
.neck{width:22px;height:10px;background:linear-gradient(180deg,#1E3A5F,#0F2040);border:1px solid rgba(56,189,248,.3);border-radius:3px;margin:0 auto}
.body{width:110px;height:90px;background:linear-gradient(160deg,#1A3352,#0E2038,#07152A);border:2px solid rgba(56,189,248,.4);border-radius:12px;position:relative;margin:0 auto;box-shadow:0 0 24px rgba(56,189,248,.18),0 8px 24px rgba(0,0,0,.6),inset 0 1px 0 rgba(255,255,255,.07)}
.body::after{content:'';position:absolute;bottom:14px;left:8px;right:8px;height:2px;background:linear-gradient(90deg,transparent,rgba(56,189,248,.5),transparent)}
.chest{position:absolute;top:14px;left:50%;transform:translateX(-50%);width:54px;height:32px;border:1px solid rgba(56,189,248,.35);border-radius:6px;display:flex;align-items:center;justify-content:center;gap:6px}
.cd{width:9px;height:9px;border-radius:50%;animation:cb 1.2s ease-in-out infinite}
.cd:nth-child(1){background:#EF4444;animation-delay:0s;box-shadow:0 0 8px #EF4444}
.cd:nth-child(2){background:#F59E0B;animation-delay:.4s;box-shadow:0 0 8px #F59E0B}
.cd:nth-child(3){background:#10B981;animation-delay:.8s;box-shadow:0 0 8px #10B981}
@keyframes cb{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.25;transform:scale(.7)}}
.arms{position:absolute;top:0;left:-36px;right:-36px;display:flex;justify-content:space-between}
.arm{width:26px;height:80px;background:linear-gradient(180deg,#1A3352,#0E2038);border:1.5px solid rgba(56,189,248,.35);border-radius:8px;position:relative;box-shadow:0 4px 12px rgba(0,0,0,.4)}
.arm.L{transform-origin:top center;animation:hc 2.2s ease-in-out infinite}
@keyframes hc{0%,100%{transform:rotate(-35deg) translateY(-8px)}50%{transform:rotate(-44deg) translateY(-15px)}}
.arm.R{transform-origin:top center;animation:sw 2.2s ease-in-out infinite}
@keyframes sw{0%,100%{transform:rotate(8deg)}50%{transform:rotate(16deg)}}
.hand{position:absolute;bottom:-10px;left:50%;transform:translateX(-50%);width:22px;height:14px;background:linear-gradient(180deg,#1E3A5F,#0F2040);border:1.5px solid rgba(56,189,248,.4);border-radius:5px}
.cash{position:absolute;bottom:-38px;left:50%;transform:translateX(-50%);font-size:1.9rem;filter:drop-shadow(0 0 12px rgba(52,211,153,1)) drop-shadow(0 0 24px rgba(52,211,153,.5));animation:cw 2.2s ease-in-out infinite;z-index:10}
@keyframes cw{0%,100%{transform:translateX(-50%) rotate(6deg) scale(1)}50%{transform:translateX(-50%) rotate(-6deg) scale(1.15)}}
.legs{display:flex;justify-content:center;gap:12px;margin-top:4px}
.leg{width:26px;height:38px;background:linear-gradient(180deg,#1A3352,#0E2038);border:1.5px solid rgba(56,189,248,.3);border-radius:6px 6px 10px 10px;position:relative}
.foot{position:absolute;bottom:-8px;left:-4px;width:34px;height:10px;background:linear-gradient(180deg,#1E3A5F,#0D1B37);border:1.5px solid rgba(56,189,248,.35);border-radius:5px;box-shadow:0 4px 10px rgba(0,0,0,.5)}
.leg:nth-child(1){animation:wl 2.2s ease-in-out infinite}
.leg:nth-child(2){animation:wr 2.2s ease-in-out infinite}
@keyframes wl{0%,100%{transform:rotate(-5deg)}50%{transform:rotate(5deg)}}
@keyframes wr{0%,100%{transform:rotate(5deg)}50%{transform:rotate(-5deg)}}
.rshadow{width:120px;height:16px;background:radial-gradient(ellipse,rgba(56,189,248,.22) 0%,transparent 70%);margin:10px auto 0;border-radius:50%;animation:shp 2.2s ease-in-out infinite}
@keyframes shp{0%,100%{transform:scaleX(1);opacity:.7}50%{transform:scaleX(.8);opacity:.35}}
/* text */
.ititle{font-family:'Inter',sans-serif;font-size:clamp(1.6rem,5vw,2.6rem);font-weight:900;background:linear-gradient(135deg,#38BDF8,#818CF8,#C084FC);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;filter:drop-shadow(0 2px 12px rgba(56,189,248,.5));letter-spacing:-.02em;text-align:center;animation:fu 1s .4s both}
.isub{font-size:.9rem;color:#94A3B8;margin-top:8px;letter-spacing:.08em;text-transform:uppercase;text-align:center;animation:fu 1s .7s both;font-family:'Inter',sans-serif}
.itag{font-size:.78rem;color:#38BDF8;margin-top:6px;letter-spacing:.14em;text-transform:uppercase;text-align:center;animation:fu 1s 1s both;font-family:'Inter',sans-serif}
@keyframes fu{from{opacity:0;transform:translateY(18px)}to{opacity:1;transform:translateY(0)}}
/* progress */
.pw{margin-top:28px;width:260px;animation:fu .5s 1.2s both}
.pb{height:4px;background:rgba(56,189,248,.15);border-radius:2px;overflow:hidden}
.pf{height:100%;background:linear-gradient(90deg,#38BDF8,#818CF8,#C084FC);border-radius:2px;width:0%;box-shadow:0 0 14px rgba(56,189,248,.6);animation:pfi 3s .8s cubic-bezier(.4,0,.2,1) forwards}
@keyframes pfi{to{width:100%}}
.pl{font-size:.7rem;color:#475569;text-align:center;margin-top:8px;letter-spacing:.1em;text-transform:uppercase;font-family:'Inter',sans-serif}
/* skip btn */
#sk{margin-top:18px;background:transparent;border:1px solid rgba(56,189,248,.3);color:#475569;font-family:'Inter',sans-serif;font-size:.73rem;padding:6px 22px;border-radius:20px;cursor:pointer;letter-spacing:.08em;transition:all .2s;animation:fu .5s 2s both}
#sk:hover{border-color:rgba(56,189,248,.7);color:#94A3B8;box-shadow:0 0 18px rgba(56,189,248,.2)}
</style>
</head>
<body>
<div id="ov">
  <div class="stars"></div>
  <div class="or r1"></div><div class="or r2"></div><div class="or r3"></div>
  <span class="cp" style="left:6%;font-size:1.4rem;animation-duration:4.2s;animation-delay:0s">💵</span>
  <span class="cp" style="left:15%;font-size:1.8rem;animation-duration:5.5s;animation-delay:.7s">💰</span>
  <span class="cp" style="left:28%;font-size:1.1rem;animation-duration:3.8s;animation-delay:.2s">💵</span>
  <span class="cp" style="left:40%;font-size:2rem;animation-duration:6.2s;animation-delay:1.4s">💸</span>
  <span class="cp" style="left:54%;font-size:1.4rem;animation-duration:4.6s;animation-delay:.5s">💴</span>
  <span class="cp" style="left:65%;font-size:1.4rem;animation-duration:5.1s;animation-delay:1s">💵</span>
  <span class="cp" style="left:76%;font-size:1.4rem;animation-duration:3.6s;animation-delay:.3s">💰</span>
  <span class="cp" style="left:86%;font-size:1.4rem;animation-duration:5.9s;animation-delay:.8s">💸</span>
  <span class="cp" style="left:93%;font-size:1.1rem;animation-duration:4.3s;animation-delay:1.6s">💵</span>
  <div class="scene">
    <div class="robot">
      <div class="ant"></div>
      <div class="head">
        <div class="eye el"></div>
        <div class="eye er"></div>
        <div class="mouth"><div class="mb"></div></div>
      </div>
      <div class="neck"></div>
      <div class="body">
        <div class="arms">
          <div class="arm L"><div class="hand"></div><div class="cash">💵</div></div>
          <div class="arm R"><div class="hand"></div></div>
        </div>
        <div class="chest"><div class="cd"></div><div class="cd"></div><div class="cd"></div></div>
      </div>
      <div class="legs">
        <div class="leg"><div class="foot"></div></div>
        <div class="leg"><div class="foot"></div></div>
      </div>
    </div>
    <div class="rshadow"></div>
    <div style="margin-top:22px">
      <div class="ititle">Inventory Intelligence</div>
      <div class="isub">Enterprise Analytics Platform</div>
      <div class="itag">⚡ Demand · Risk · Forecasting ⚡</div>
    </div>
    <div class="pw">
      <div class="pb"><div class="pf"></div></div>
      <div class="pl" id="lbl">Initializing systems...</div>
    </div>
    <button id="sk" onclick="go()">SKIP INTRO ›</button>
  </div>
</div>
<script>
var ov=document.getElementById('ov');
var lbl=document.getElementById('lbl');
var steps=[
  {t:600, msg:'Loading data pipeline...'},
  {t:1200,msg:'Calibrating risk engine...'},
  {t:1900,msg:'Generating forecasts...'},
  {t:2600,msg:'Building dashboards...'},
  {t:3200,msg:'Ready! \uD83D\uDE80'}
];
steps.forEach(function(s){setTimeout(function(){if(lbl)lbl.textContent=s.msg;},s.t);});
function go(){
  ov.classList.add('hide');
  setTimeout(function(){ov.style.display='none';},1000);
}
setTimeout(go,4400);
window.go=go;
</script>
</body>
</html>""", height=700, scrolling=False)

# Dummy placeholder that gets hidden — intro fills screen via the iframe
st.markdown("""
<style>
/* Push iframe to cover full viewport */
iframe[title="st.iframe"] {
    position: fixed !important;
    inset: 0 !important;
    width: 100vw !important;
    height: 100vh !important;
    z-index: 99999 !important;
    border: none !important;
    background: #000 !important;
}
</style>
""", unsafe_allow_html=True)

# ── OLD INTRO BLOCK (disabled) ────────────────────────────────────────────────
if False:
    st.markdown("""
<style>
/* ═══════════════════════════════════ INTRO OVERLAY ══════════════════════════ */
#robot-intro-overlay {
    position: fixed;
    inset: 0;
    z-index: 99999;
    background: radial-gradient(ellipse 120% 100% at 50% 60%,
        #0D1B3E 0%, #060B18 55%, #000000 100%);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    overflow: hidden;
    transition: opacity 0.9s ease, transform 0.9s ease;
}
#robot-intro-overlay.hide {
    opacity: 0;
    transform: scale(1.05);
    pointer-events: none;
}

/* ── Stars background ── */
.intro-stars {
    position: absolute;
    inset: 0;
    background-image:
        radial-gradient(1px 1px at  8% 12%, rgba(255,255,255,0.8) 0%, transparent 100%),
        radial-gradient(1px 1px at 20% 70%, rgba(255,255,255,0.6) 0%, transparent 100%),
        radial-gradient(1px 1px at 35%  5%, rgba(56,189,248,0.9)  0%, transparent 100%),
        radial-gradient(1px 1px at 50% 45%, rgba(255,255,255,0.5) 0%, transparent 100%),
        radial-gradient(1px 1px at 62% 25%, rgba(192,132,252,0.9) 0%, transparent 100%),
        radial-gradient(1px 1px at 75% 80%, rgba(255,255,255,0.7) 0%, transparent 100%),
        radial-gradient(1px 1px at 88% 15%, rgba(56,189,248,0.8)  0%, transparent 100%),
        radial-gradient(1px 1px at 93% 60%, rgba(255,255,255,0.6) 0%, transparent 100%),
        radial-gradient(1.5px 1.5px at 15% 90%, rgba(56,189,248,0.7) 0%, transparent 100%),
        radial-gradient(1.5px 1.5px at 45% 55%, rgba(192,132,252,0.7) 0%, transparent 100%),
        radial-gradient(1.5px 1.5px at 70% 35%, rgba(255,255,255,0.8) 0%, transparent 100%),
        radial-gradient(1.5px 1.5px at 82% 92%, rgba(56,189,248,0.6) 0%, transparent 100%);
    animation: twinkle 4s ease-in-out infinite alternate;
}
@keyframes twinkle {
    from { opacity: 0.6; }
    to   { opacity: 1.0; }
}

/* ── Floating cash particles ── */
.cash-particle {
    position: absolute;
    font-size: 1.4rem;
    animation: cashFloat linear infinite;
    opacity: 0;
    pointer-events: none;
    filter: drop-shadow(0 0 6px rgba(52, 211, 153, 0.7));
}
@keyframes cashFloat {
    0%   { transform: translateY(110vh) rotate(0deg);   opacity: 0; }
    10%  { opacity: 0.85; }
    90%  { opacity: 0.6; }
    100% { transform: translateY(-10vh) rotate(360deg); opacity: 0; }
}

/* ── 3D scene container ── */
.intro-scene {
    perspective: 900px;
    display: flex;
    flex-direction: column;
    align-items: center;
    position: relative;
    z-index: 2;
    animation: sceneEntrance 0.9s cubic-bezier(0.34,1.56,0.64,1) both;
}
@keyframes sceneEntrance {
    from { transform: translateY(60px) scale(0.85); opacity: 0; }
    to   { transform: translateY(0px)  scale(1);    opacity: 1; }
}

/* ─────────────────────── ROBOT ─────────────────────── */
.robot {
    position: relative;
    width: 140px;
    transform-style: preserve-3d;
    animation: robotBob 2.2s ease-in-out infinite, robotSpin3D 8s ease-in-out infinite;
}
@keyframes robotBob {
    0%, 100% { transform: translateY(0px);  }
    50%       { transform: translateY(-12px); }
}
@keyframes robotSpin3D {
    0%   { transform: perspective(600px) rotateY(0deg)   translateY(0px);  }
    25%  { transform: perspective(600px) rotateY(12deg)  translateY(-6px);  }
    50%  { transform: perspective(600px) rotateY(0deg)   translateY(-12px); }
    75%  { transform: perspective(600px) rotateY(-12deg) translateY(-6px);  }
    100% { transform: perspective(600px) rotateY(0deg)   translateY(0px);  }
}

/* Antenna */
.robot-antenna {
    position: absolute;
    top: -22px; left: 50%;
    transform: translateX(-50%);
    width: 4px; height: 18px;
    background: linear-gradient(180deg, #38BDF8, #1E40AF);
    border-radius: 2px;
    box-shadow: 0 0 8px #38BDF8;
}
.robot-antenna::after {
    content: '';
    position: absolute;
    top: -7px; left: 50%;
    transform: translateX(-50%);
    width: 10px; height: 10px;
    border-radius: 50%;
    background: radial-gradient(circle, #38BDF8, #0EA5E9);
    box-shadow: 0 0 14px #38BDF8, 0 0 28px rgba(56,189,248,0.5);
    animation: antennaPulse 1.1s ease-in-out infinite;
}
@keyframes antennaPulse {
    0%, 100% { box-shadow: 0 0 10px #38BDF8, 0 0 22px rgba(56,189,248,0.4); transform: translateX(-50%) scale(1);   }
    50%       { box-shadow: 0 0 20px #38BDF8, 0 0 44px rgba(56,189,248,0.8); transform: translateX(-50%) scale(1.35); }
}

/* Head */
.robot-head {
    width: 80px; height: 65px;
    margin: 0 auto;
    background: linear-gradient(160deg, #1E3A5F 0%, #0F2040 60%, #071628 100%);
    border: 2px solid rgba(56,189,248,0.5);
    border-radius: 14px 14px 8px 8px;
    position: relative;
    box-shadow:
        0 0 20px rgba(56,189,248,0.25),
        0 4px 16px rgba(0,0,0,0.6),
        inset 0 1px 0 rgba(255,255,255,0.1);
    transform-style: preserve-3d;
}
/* Face visor */
.robot-head::before {
    content: '';
    position: absolute;
    top: 12px; left: 10px; right: 10px; height: 24px;
    background: linear-gradient(135deg, rgba(56,189,248,0.15), rgba(99,102,241,0.15));
    border: 1px solid rgba(56,189,248,0.4);
    border-radius: 6px;
    box-shadow: 0 0 12px rgba(56,189,248,0.3) inset;
}
/* Eyes */
.robot-eye {
    position: absolute;
    top: 17px;
    width: 14px; height: 14px;
    border-radius: 50%;
    background: radial-gradient(circle at 35% 35%, #7DD3FC, #0369A1);
    box-shadow: 0 0 10px #38BDF8, 0 0 20px rgba(56,189,248,0.5);
    animation: eyeGlow 1.8s ease-in-out infinite;
}
.robot-eye.left  { left: 16px; }
.robot-eye.right { right: 16px; }
@keyframes eyeGlow {
    0%, 100% { box-shadow: 0 0 8px #38BDF8,  0 0 16px rgba(56,189,248,0.4); }
    50%       { box-shadow: 0 0 18px #38BDF8, 0 0 36px rgba(56,189,248,0.8); }
}
/* Mouth */
.robot-mouth {
    position: absolute;
    bottom: 10px; left: 50%;
    transform: translateX(-50%);
    width: 34px; height: 8px;
    border-radius: 0 0 8px 8px;
    border: 2px solid rgba(56,189,248,0.5);
    border-top: none;
    overflow: hidden;
}
.robot-mouth-bar {
    position: absolute;
    top: 2px; left: 2px; right: 2px; height: 3px;
    background: linear-gradient(90deg, #38BDF8, #818CF8, #38BDF8);
    background-size: 200% 100%;
    border-radius: 2px;
    animation: mouthScan 0.9s linear infinite;
}
@keyframes mouthScan {
    0%   { background-position: 0%   50%; }
    100% { background-position: 200% 50%; }
}

/* Neck */
.robot-neck {
    width: 22px; height: 10px;
    background: linear-gradient(180deg, #1E3A5F, #0F2040);
    border: 1px solid rgba(56,189,248,0.3);
    border-radius: 3px;
    margin: 0 auto;
}

/* Body */
.robot-body {
    width: 110px; height: 90px;
    background: linear-gradient(160deg, #1A3352 0%, #0E2038 50%, #07152A 100%);
    border: 2px solid rgba(56,189,248,0.4);
    border-radius: 12px;
    position: relative;
    margin: 0 auto;
    box-shadow:
        0 0 24px rgba(56,189,248,0.18),
        0 8px 24px rgba(0,0,0,0.6),
        inset 0 1px 0 rgba(255,255,255,0.08);
}
/* Chest panel */
.robot-chest {
    position: absolute;
    top: 14px; left: 50%;
    transform: translateX(-50%);
    width: 52px; height: 32px;
    background: linear-gradient(135deg, rgba(56,189,248,0.08), rgba(99,102,241,0.08));
    border: 1px solid rgba(56,189,248,0.35);
    border-radius: 6px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 5px;
    padding: 4px;
}
.chest-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    animation: chestBlink 1.2s ease-in-out infinite;
}
.chest-dot:nth-child(1) { background: #EF4444; animation-delay: 0s;    box-shadow: 0 0 8px #EF4444; }
.chest-dot:nth-child(2) { background: #F59E0B; animation-delay: 0.4s;  box-shadow: 0 0 8px #F59E0B; }
.chest-dot:nth-child(3) { background: #10B981; animation-delay: 0.8s;  box-shadow: 0 0 8px #10B981; }
@keyframes chestBlink {
    0%, 100% { opacity: 1; transform: scale(1); }
    50%       { opacity: 0.3; transform: scale(0.75); }
}
/* Belt line */
.robot-body::after {
    content: '';
    position: absolute;
    bottom: 14px; left: 8px; right: 8px; height: 2px;
    background: linear-gradient(90deg, transparent, rgba(56,189,248,0.5), transparent);
    border-radius: 1px;
}

/* Arms */
.robot-arms {
    position: absolute;
    top: 0; left: -34px; right: -34px;
    display: flex;
    justify-content: space-between;
}
.robot-arm {
    width: 26px; height: 80px;
    background: linear-gradient(180deg, #1A3352 0%, #0E2038 100%);
    border: 1.5px solid rgba(56,189,248,0.35);
    border-radius: 8px;
    position: relative;
    box-shadow: 0 4px 12px rgba(0,0,0,0.4);
}
/* Left arm raised to hold cash */
.robot-arm.left {
    transform-origin: top center;
    animation: holdCash 2.2s ease-in-out infinite;
}
@keyframes holdCash {
    0%, 100% { transform: rotate(-35deg) translateY(-8px);  }
    50%       { transform: rotate(-42deg) translateY(-14px); }
}
/* Right arm hangs naturally */
.robot-arm.right {
    transform-origin: top center;
    animation: armSwing 2.2s ease-in-out infinite;
}
@keyframes armSwing {
    0%, 100% { transform: rotate(8deg);  }
    50%       { transform: rotate(14deg); }
}
/* Hand grips */
.robot-hand {
    position: absolute;
    bottom: -10px; left: 50%;
    transform: translateX(-50%);
    width: 22px; height: 14px;
    background: linear-gradient(180deg, #1E3A5F, #0F2040);
    border: 1.5px solid rgba(56,189,248,0.4);
    border-radius: 5px;
}

/* Cash bundle on left hand */
.cash-bundle {
    position: absolute;
    bottom: -36px; left: 50%;
    transform: translateX(-50%) rotate(5deg);
    font-size: 1.8rem;
    filter: drop-shadow(0 0 10px rgba(52, 211, 153, 0.9))
            drop-shadow(0 0 20px rgba(52, 211, 153, 0.4));
    animation: cashWave 2.2s ease-in-out infinite;
    z-index: 10;
}
@keyframes cashWave {
    0%, 100% { transform: translateX(-50%) rotate(5deg)   scale(1);    }
    50%       { transform: translateX(-50%) rotate(-5deg)  scale(1.12); }
}

/* Legs */
.robot-legs {
    display: flex;
    justify-content: center;
    gap: 12px;
    margin-top: 4px;
}
.robot-leg {
    width: 26px; height: 38px;
    background: linear-gradient(180deg, #1A3352, #0E2038);
    border: 1.5px solid rgba(56,189,248,0.3);
    border-radius: 6px 6px 10px 10px;
    position: relative;
}
.robot-foot {
    position: absolute;
    bottom: -8px; left: -4px;
    width: 34px; height: 10px;
    background: linear-gradient(180deg, #1E3A5F, #0D1B37);
    border: 1.5px solid rgba(56,189,248,0.35);
    border-radius: 5px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.5);
}
/* Walking legs animation */
.robot-leg:first-child { animation: walkL 2.2s ease-in-out infinite; }
.robot-leg:last-child  { animation: walkR 2.2s ease-in-out infinite; }
@keyframes walkL {
    0%, 100% { transform: rotate(-4deg);  }
    50%       { transform: rotate(4deg);   }
}
@keyframes walkR {
    0%, 100% { transform: rotate(4deg);   }
    50%       { transform: rotate(-4deg);  }
}

/* ── Ground glow shadow ── */
.robot-shadow {
    width: 120px; height: 18px;
    background: radial-gradient(ellipse, rgba(56,189,248,0.22) 0%, transparent 70%);
    margin: 8px auto 0 auto;
    animation: shadowPulse 2.2s ease-in-out infinite;
    border-radius: 50%;
}
@keyframes shadowPulse {
    0%, 100% { transform: scaleX(1);    opacity: 0.7; }
    50%       { transform: scaleX(0.85); opacity: 0.4; }
}

/* ── Intro text ── */
.intro-text-wrap {
    text-align: center;
    margin-top: 28px;
    position: relative;
    z-index: 2;
}
.intro-title {
    font-family: 'Inter', sans-serif;
    font-size: clamp(1.8rem, 4vw, 2.8rem);
    font-weight: 900;
    background: linear-gradient(135deg, #38BDF8 0%, #818CF8 50%, #C084FC 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    filter: drop-shadow(0 2px 10px rgba(56,189,248,0.5));
    letter-spacing: -0.02em;
    animation: titleReveal 1s 0.4s cubic-bezier(0.22,1,0.36,1) both;
}
@keyframes titleReveal {
    from { opacity: 0; transform: translateY(20px); filter: blur(8px) drop-shadow(0 2px 0 transparent); }
    to   { opacity: 1; transform: translateY(0px);  filter: blur(0px) drop-shadow(0 2px 10px rgba(56,189,248,0.5)); }
}
.intro-sub {
    font-family: 'Inter', sans-serif;
    font-size: 1rem;
    color: #94A3B8;
    margin-top: 8px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    animation: titleReveal 1s 0.7s cubic-bezier(0.22,1,0.36,1) both;
}
.intro-tagline {
    font-family: 'Inter', sans-serif;
    font-size: 0.85rem;
    color: #38BDF8;
    margin-top: 6px;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    animation: titleReveal 1s 1.0s cubic-bezier(0.22,1,0.36,1) both;
}

/* ── Progress bar ── */
.intro-progress-wrap {
    margin-top: 32px;
    width: 260px;
    position: relative;
    z-index: 2;
    animation: fadeIn 0.5s 1.2s both;
}
@keyframes fadeIn { from { opacity:0; } to { opacity:1; } }
.intro-progress-bg {
    width: 100%; height: 4px;
    background: rgba(56,189,248,0.15);
    border-radius: 2px;
    overflow: hidden;
}
.intro-progress-bar {
    height: 100%;
    background: linear-gradient(90deg, #38BDF8, #818CF8, #C084FC);
    border-radius: 2px;
    animation: progressFill 2.8s 0.8s cubic-bezier(0.4,0,0.2,1) forwards;
    width: 0%;
    box-shadow: 0 0 12px rgba(56,189,248,0.6);
}
@keyframes progressFill {
    0%   { width: 0%; }
    100% { width: 100%; }
}
.intro-progress-label {
    font-family: 'Inter', sans-serif;
    font-size: 0.72rem;
    color: #475569;
    text-align: center;
    margin-top: 8px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    animation: loadingDots 1.2s 0.8s steps(4) infinite;
}
@keyframes loadingDots {
    0%  { content: 'Initializing';    }
}

/* ── Skip button ── */
.intro-skip {
    margin-top: 20px;
    position: relative;
    z-index: 2;
    animation: fadeIn 0.5s 2.0s both;
}
.intro-skip button, #skipBtn {
    background: transparent;
    border: 1px solid rgba(56,189,248,0.3);
    color: #475569;
    font-family: 'Inter', sans-serif;
    font-size: 0.75rem;
    padding: 6px 20px;
    border-radius: 20px;
    cursor: pointer;
    transition: all 0.2s;
    letter-spacing: 0.08em;
}
#skipBtn:hover {
    border-color: rgba(56,189,248,0.7);
    color: #94A3B8;
    box-shadow: 0 0 16px rgba(56,189,248,0.2);
}

/* ── Orbit ring decoration ── */
.orbit-ring {
    position: absolute;
    border-radius: 50%;
    border: 1px solid rgba(56,189,248,0.12);
    animation: orbit linear infinite;
    pointer-events: none;
}
.orbit-ring::after {
    content: '';
    position: absolute;
    width: 8px; height: 8px;
    border-radius: 50%;
    background: #38BDF8;
    top: -4px; left: 50%;
    transform: translateX(-50%);
    box-shadow: 0 0 10px #38BDF8;
}
.orbit-ring.r1 { width: 200px; height: 200px; top: 50%; left: 50%; margin: -100px 0 0 -100px; animation-duration: 5s; }
.orbit-ring.r2 { width: 300px; height: 300px; top: 50%; left: 50%; margin: -150px 0 0 -150px; animation-duration: 9s;  animation-direction: reverse; }
.orbit-ring.r3 { width: 420px; height: 420px; top: 50%; left: 50%; margin: -210px 0 0 -210px; animation-duration: 14s; }
@keyframes orbit { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }

/* Hide Streamlit while intro plays */
body.intro-playing .stApp > div:not(#robot-intro-overlay) { display: none !important; }
</style>

<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">

<div id="robot-intro-overlay">
    <div class="intro-stars"></div>

    <!-- Orbit decorations -->
    <div class="orbit-ring r1"></div>
    <div class="orbit-ring r2"></div>
    <div class="orbit-ring r3"></div>

    <!-- Cash floating particles -->
    <span class="cash-particle" style="left:8%;  animation-duration:4.2s; animation-delay:0.0s; font-size:1.2rem;">💵</span>
    <span class="cash-particle" style="left:18%; animation-duration:5.5s; animation-delay:0.8s; font-size:1.6rem;">💰</span>
    <span class="cash-particle" style="left:30%; animation-duration:3.9s; animation-delay:0.3s; font-size:1.1rem;">💵</span>
    <span class="cash-particle" style="left:42%; animation-duration:6.1s; animation-delay:1.5s; font-size:1.8rem;">💸</span>
    <span class="cash-particle" style="left:55%; animation-duration:4.7s; animation-delay:0.6s; font-size:1.3rem;">💴</span>
    <span class="cash-particle" style="left:65%; animation-duration:5.3s; animation-delay:1.1s; font-size:1.5rem;">💵</span>
    <span class="cash-particle" style="left:75%; animation-duration:3.7s; animation-delay:0.2s; font-size:1.2rem;">💰</span>
    <span class="cash-particle" style="left:85%; animation-duration:5.8s; animation-delay:0.9s; font-size:1.4rem;">💸</span>
    <span class="cash-particle" style="left:92%; animation-duration:4.4s; animation-delay:1.7s; font-size:1.0rem;">💵</span>

    <!-- 3D Robot -->
    <div class="intro-scene">
        <div class="robot">
            <div class="robot-antenna"></div>
            <div class="robot-head">
                <div class="robot-eye left"></div>
                <div class="robot-eye right"></div>
                <div class="robot-mouth"><div class="robot-mouth-bar"></div></div>
            </div>
            <div class="robot-neck"></div>
            <div class="robot-body">
                <div class="robot-arms">
                    <div class="robot-arm left">
                        <div class="robot-hand"></div>
                        <div class="cash-bundle">💵</div>
                    </div>
                    <div class="robot-arm right">
                        <div class="robot-hand"></div>
                    </div>
                </div>
                <div class="robot-chest">
                    <div class="chest-dot"></div>
                    <div class="chest-dot"></div>
                    <div class="chest-dot"></div>
                </div>
            </div>
            <div class="robot-legs">
                <div class="robot-leg"><div class="robot-foot"></div></div>
                <div class="robot-leg"><div class="robot-foot"></div></div>
            </div>
        </div>
        <div class="robot-shadow"></div>

        <!-- Text -->
        <div class="intro-text-wrap">
            <div class="intro-title">Inventory Intelligence</div>
            <div class="intro-sub">Enterprise Analytics Platform</div>
            <div class="intro-tagline">⚡ Demand · Risk · Forecasting ⚡</div>
        </div>

        <!-- Progress bar -->
        <div class="intro-progress-wrap">
            <div class="intro-progress-bg">
                <div class="intro-progress-bar" id="introProgressBar"></div>
            </div>
            <div class="intro-progress-label" id="introProgressLabel">Initializing systems...</div>
        </div>

        <!-- Skip -->
        <div class="intro-skip">
            <button id="skipBtn" onclick="dismissIntro()">SKIP INTRO ›</button>
        </div>
    </div>
</div>

<script>
(function() {
    var overlay = document.getElementById('robot-intro-overlay');
    var label   = document.getElementById('introProgressLabel');
    if (!overlay) return;

    // Only show once per browser session
    if (sessionStorage.getItem('intro_done') === '1') {
        overlay.style.display = 'none';
        return;
    }

    document.body.classList.add('intro-playing');

    var steps = [
        { t: 600,  msg: 'Loading data pipeline...' },
        { t: 1200, msg: 'Calibrating risk engine...' },
        { t: 1900, msg: 'Generating forecasts...' },
        { t: 2500, msg: 'Building dashboards...' },
        { t: 3100, msg: 'Ready! 🚀' }
    ];

    steps.forEach(function(s) {
        setTimeout(function() {
            if (label) label.textContent = s.msg;
        }, s.t);
    });

    // Auto-dismiss after 4.2s
    setTimeout(dismissIntro, 4200);

    function dismissIntro() {
        if (!overlay) return;
        overlay.classList.add('hide');
        document.body.classList.remove('intro-playing');
        sessionStorage.setItem('intro_done', '1');
        setTimeout(function() {
            overlay.style.display = 'none';
        }, 950);
    }

    // Expose globally for skip button
    window.dismissIntro = dismissIntro;
})();
</script>
""", unsafe_allow_html=True)

# ── 3-D Design System ────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ═══════════════════════════════════════════════════════════════════
   FONTS & BASE
═══════════════════════════════════════════════════════════════════ */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

*, *::before, *::after { box-sizing: border-box; }

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* ═══════════════════════════════════════════════════════════════════
   DEEP-SPACE BACKGROUND  (starfield + depth fog)
═══════════════════════════════════════════════════════════════════ */
.stApp, .main, section[data-testid="stMain"] {
    background:
        radial-gradient(ellipse 80% 60% at 20% 10%,  rgba(56,189,248,0.07)  0%, transparent 60%),
        radial-gradient(ellipse 60% 50% at 80% 80%,  rgba(192,132,252,0.07) 0%, transparent 55%),
        radial-gradient(ellipse 100% 100% at 50% 50%, rgba(15,23,42,1)       0%, #060B18 100%);
    color: #F8FAFC;
}

/* subtle animated star-dots via repeating gradient */
.stApp::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image:
        radial-gradient(1px 1px at 10%  15%, rgba(255,255,255,0.55) 0%, transparent 100%),
        radial-gradient(1px 1px at 35%  70%, rgba(255,255,255,0.35) 0%, transparent 100%),
        radial-gradient(1px 1px at 60%  30%, rgba(255,255,255,0.45) 0%, transparent 100%),
        radial-gradient(1px 1px at 80%  55%, rgba(255,255,255,0.30) 0%, transparent 100%),
        radial-gradient(1px 1px at 92%  10%, rgba(255,255,255,0.50) 0%, transparent 100%),
        radial-gradient(1px 1px at 50%  90%, rgba(255,255,255,0.40) 0%, transparent 100%),
        radial-gradient(1.5px 1.5px at 25% 45%, rgba(56,189,248,0.6) 0%, transparent 100%),
        radial-gradient(1.5px 1.5px at 75% 20%, rgba(192,132,252,0.6) 0%, transparent 100%);
    pointer-events: none;
    z-index: 0;
}

/* ═══════════════════════════════════════════════════════════════════
   HERO HEADER  — 3-D extruded text
═══════════════════════════════════════════════════════════════════ */
.hero-wrap {
    perspective: 900px;
    padding: 10px 0 4px 0;
}
.hero-title {
    font-size: clamp(1.8rem, 3.5vw, 2.6rem);
    font-weight: 900;
    letter-spacing: -0.02em;
    background: linear-gradient(135deg, #38BDF8 0%, #818CF8 50%, #C084FC 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    /* 3-D text shadow stack — creates the extrusion illusion */
    filter: drop-shadow(0 2px 0 rgba(56,189,248,0.25))
            drop-shadow(0 4px 0 rgba(99,102,241,0.18))
            drop-shadow(0 8px 18px rgba(0,0,0,0.55));
    transform: perspective(600px) rotateX(4deg);
    display: inline-block;
    margin-bottom: 0.15rem;
}
.hero-sub {
    color: #94A3B8;
    font-size: 1rem;
    font-weight: 400;
    margin-bottom: 1.4rem;
    letter-spacing: 0.01em;
}

/* ═══════════════════════════════════════════════════════════════════
   KPI CARDS  — lifted 3-D slab with glowing edge & float animation
═══════════════════════════════════════════════════════════════════ */
@keyframes float-card {
    0%, 100% { transform: translateY(0px)   rotateX(1.5deg) rotateY(-0.5deg); }
    50%       { transform: translateY(-4px)  rotateX(2.5deg) rotateY( 0.5deg); }
}

.kpi-card {
    position: relative;
    background: linear-gradient(
        160deg,
        rgba(30, 41, 59, 0.85) 0%,
        rgba(15, 23, 42, 0.95) 100%
    );
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 14px;
    padding: 16px 18px 14px 18px;
    min-width: 0;
    overflow: hidden;
    /* multi-layer shadow = 3-D depth illusion */
    box-shadow:
        0 1px  0   rgba(255,255,255,0.06) inset,   /* top-edge shine   */
        0 -1px 0   rgba(0,0,0,0.5)        inset,   /* bottom-edge dark  */
        0 4px  8px  rgba(0,0,0,0.4),               /* contact shadow   */
        0 12px 30px rgba(0,0,0,0.35),              /* ambient lift     */
        0 2px  60px rgba(56,189,248,0.04);          /* distant glow     */
    transform: perspective(700px) rotateX(2deg) rotateY(-0.5deg);
    transform-style: preserve-3d;
    transition: transform 0.28s ease, box-shadow 0.28s ease, border-color 0.28s ease;
    animation: float-card 5s ease-in-out infinite;
    cursor: default;
}

/* glowing top edge pseudo-element */
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 10%; right: 10%;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(56,189,248,0.55), transparent);
    border-radius: 50%;
}

/* bottom face — creates a 3-D "slab" depth effect */
.kpi-card::after {
    content: '';
    position: absolute;
    bottom: -5px; left: 4px; right: 4px;
    height: 10px;
    background: linear-gradient(180deg, rgba(0,0,0,0.45), transparent);
    border-radius: 0 0 14px 14px;
    filter: blur(4px);
    z-index: -1;
}

.kpi-card:hover {
    transform: perspective(700px) rotateX(0deg) rotateY(0deg) translateY(-6px) scale(1.02);
    box-shadow:
        0 1px  0   rgba(255,255,255,0.10) inset,
        0 -1px 0   rgba(0,0,0,0.5)        inset,
        0 8px  20px rgba(0,0,0,0.5),
        0 20px 50px rgba(0,0,0,0.4),
        0 0    40px rgba(56,189,248,0.14);
    border-color: rgba(56,189,248,0.45);
    animation-play-state: paused;   /* freeze float on hover */
}

.kpi-title {
    font-size: 0.68rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: #7DD3FC;           /* lighter sky-blue — better contrast vs dark */
    font-weight: 700;
    margin-bottom: 7px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.kpi-value {
    font-size: clamp(1.35rem, 2vw, 1.8rem);
    font-weight: 800;
    color: #F8FAFC;
    line-height: 1.2;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    /* 3-D number extrusion */
    text-shadow:
        0 1px 0 rgba(255,255,255,0.15),
        0 2px 4px rgba(0,0,0,0.6);
}

.kpi-sub {
    font-size: 0.70rem;
    color: #475569;
    margin-top: 6px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

/* KPI row spacer */
.kpi-row-gap { margin-bottom: 14px; }

/* ═══════════════════════════════════════════════════════════════════
   SECTION HEADINGS  — 3-D depth bar + glow
═══════════════════════════════════════════════════════════════════ */
.section-title {
    font-size: 1.1rem;
    font-weight: 700;
    color: #F8FAFC;
    margin-top: 1.2rem;
    margin-bottom: 0.65rem;
    display: flex;
    align-items: center;
    gap: 10px;
    /* 3-D left bar with glow */
    border-left: 4px solid #38BDF8;
    padding-left: 12px;
    position: relative;
    /* depth via shadow */
    text-shadow:
        0 1px 0  rgba(255,255,255,0.12),
        0 2px 6px rgba(0,0,0,0.55);
    filter: drop-shadow(0 0 8px rgba(56,189,248,0.18));
}
/* Glowing underline that extends from the accent bar */
.section-title::after {
    content: '';
    position: absolute;
    left: 0; bottom: -4px;
    width: 60px; height: 2px;
    background: linear-gradient(90deg, #38BDF8, transparent);
    border-radius: 2px;
    opacity: 0.7;
}

/* ═══════════════════════════════════════════════════════════════════
   CHART CONTAINERS  — floating panel with 3-D frame
═══════════════════════════════════════════════════════════════════ */
div[data-testid="stPlotlyChart"] {
    background: linear-gradient(160deg, rgba(15,23,42,0.8) 0%, rgba(8,13,28,0.95) 100%);
    border: 1px solid rgba(56,189,248,0.12);
    border-radius: 14px;
    padding: 6px;
    box-shadow:
        0 1px 0 rgba(255,255,255,0.05) inset,
        0 8px 24px rgba(0,0,0,0.45),
        0 0   40px rgba(56,189,248,0.05);
    transform: perspective(1200px) rotateX(1deg);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}
div[data-testid="stPlotlyChart"]:hover {
    transform: perspective(1200px) rotateX(0deg) translateY(-2px);
    box-shadow:
        0 1px 0 rgba(255,255,255,0.07) inset,
        0 14px 36px rgba(0,0,0,0.55),
        0 0    50px rgba(56,189,248,0.09);
}

/* ═══════════════════════════════════════════════════════════════════
   ALERT BANNER  — 3-D raised slab
═══════════════════════════════════════════════════════════════════ */
.alert-banner {
    background: linear-gradient(105deg,
        rgba(239,68,68,0.18) 0%,
        rgba(30,41,59,0.92)  60%,
        rgba(15,23,42,0.98)  100%);
    border-left: 4px solid #EF4444;
    border-radius: 10px;
    padding: 14px 20px;
    margin-bottom: 20px;
    box-shadow:
        0 1px 0 rgba(239,68,68,0.15) inset,
        0 6px 20px rgba(0,0,0,0.4),
        0 0   30px rgba(239,68,68,0.07);
    transform: perspective(800px) rotateX(1.5deg);
}

/* ═══════════════════════════════════════════════════════════════════
   STATUS BADGES  — glassy pill
═══════════════════════════════════════════════════════════════════ */
.badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 9999px;
    font-size: 0.74rem;
    font-weight: 700;
    letter-spacing: 0.03em;
    box-shadow: 0 2px 6px rgba(0,0,0,0.35), 0 1px 0 rgba(255,255,255,0.08) inset;
}
.badge-critical    { background: rgba(239,68,68,0.22);   color: #FCA5A5; border: 1px solid rgba(239,68,68,0.45);  }
.badge-low-stock   { background: rgba(245,158,11,0.22);  color: #FDE68A; border: 1px solid rgba(245,158,11,0.45); }
.badge-healthy     { background: rgba(16,185,129,0.22);  color: #6EE7B7; border: 1px solid rgba(16,185,129,0.45); }
.badge-overstock   { background: rgba(99,102,241,0.22);  color: #A5B4FC; border: 1px solid rgba(99,102,241,0.45); }
.badge-slow-moving { background: rgba(139,92,246,0.22);  color: #C4B5FD; border: 1px solid rgba(139,92,246,0.45); }

/* ═══════════════════════════════════════════════════════════════════
   DATA TABLE  — dark glass frame
═══════════════════════════════════════════════════════════════════ */
div[data-testid="stDataFrame"] {
    border: 1px solid rgba(56,189,248,0.12);
    border-radius: 10px;
    overflow: hidden;
    box-shadow: 0 4px 20px rgba(0,0,0,0.4), 0 0 30px rgba(56,189,248,0.04);
}

/* ═══════════════════════════════════════════════════════════════════
   SIDEBAR  — dark glass panel
═══════════════════════════════════════════════════════════════════ */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(8,14,28,0.97) 0%, rgba(12,20,40,0.95) 100%);
    border-right: 1px solid rgba(56,189,248,0.10);
    box-shadow: 4px 0 30px rgba(0,0,0,0.5);
}
</style>
""", unsafe_allow_html=True)

# Helper Functions with Caching
@st.cache_data
def get_processed_data(file_path_or_bytes, file_name: str, low_days, over_days, slow_days):
    """
    Cached data processing pipeline.
    """
    if isinstance(file_path_or_bytes, str):
        raw_df = load_data_from_path(file_path_or_bytes)
    else:
        # Uploaded file
        if file_name.endswith(".csv"):
            raw_df = pd.read_csv(file_path_or_bytes)
        elif file_name.endswith((".xls", ".xlsx")):
            raw_df = pd.read_excel(file_path_or_bytes)
        elif file_name.endswith(".parquet"):
            raw_df = pd.read_parquet(file_path_or_bytes)
        else:
            raw_df = pd.read_csv(file_path_or_bytes)

    profile = generate_data_profile(raw_df, file_name)
    mapping = profile["column_mapping"]
    clean_df, audit_log = preprocess_inventory_data(raw_df, mapping)
    
    prod_analytics = compute_product_analytics(
        clean_df,
        low_stock_days=low_days,
        overstock_days=over_days,
        slow_moving_days=slow_days
    )
    prod_analytics = attach_risk_scores(prod_analytics)
    prod_analytics = attach_recommendations(prod_analytics)
    
    cat_summary = compute_category_analytics(prod_analytics)
    
    return raw_df, clean_df, prod_analytics, cat_summary, profile, audit_log

# SIDEBAR CONTROLS
st.sidebar.markdown("### 📦 Inventory Intelligence")
st.sidebar.caption("v2.4 Hackathon Edition")

# Navigation
page = st.sidebar.radio(
    "Navigation",
    [
        "📊 Executive Overview",
        "📈 Demand Analytics",
        "⚠️ Stock Risk & Stock-Outs",
        "🧊 Overstock & Slow-Moving",
        "🔍 Product Explorer",
        "⚙️ Data Profiling & Audit"
    ],
    index=0
)

st.sidebar.markdown("---")
st.sidebar.markdown("#### 📂 Dataset Selection")

data_source = st.sidebar.radio(
    "Data Source",
    ["Standard Benchmark (5.4k rows)", "Upload Custom Dataset (CSV/XLSX)"],
    index=0
)

uploaded_file = None
if data_source == "Upload Custom Dataset (CSV/XLSX)":
    uploaded_file = st.sidebar.file_uploader(
        "Upload dataset",
        type=["csv", "xlsx", "xls", "parquet"],
        help="Upload any inventory or sales CSV with SKU, Demand, Stock, Date, etc."
    )

st.sidebar.markdown("---")
st.sidebar.markdown("#### 🎛️ Operational Thresholds")
cfg_low_days = st.sidebar.slider("Low Stock Threshold (Days)", min_value=1.0, max_value=21.0, value=float(LOW_STOCK_DAYS), step=1.0)
cfg_over_days = st.sidebar.slider("Overstock Threshold (Days)", min_value=30.0, max_value=120.0, value=float(OVERSTOCK_DAYS), step=5.0)
cfg_slow_days = st.sidebar.slider("Slow-Moving Threshold (Days)", min_value=14.0, max_value=90.0, value=float(SLOW_MOVING_DAYS), step=5.0)

# Load data based on selection
if uploaded_file is not None:
    raw_df, clean_df, prod_analytics, cat_summary, profile, audit_log = get_processed_data(
        uploaded_file, uploaded_file.name, cfg_low_days, cfg_over_days, cfg_slow_days
    )
else:
    benchmark_path = "data/raw/retail_inventory_transactions.csv"
    if not os.path.exists(benchmark_path):
        from scripts.generate_dataset import generate_inventory_data
        generate_inventory_data()
    raw_df, clean_df, prod_analytics, cat_summary, profile, audit_log = get_processed_data(
        benchmark_path, "retail_inventory_transactions.csv", cfg_low_days, cfg_over_days, cfg_slow_days
    )

# Sidebar Power BI Exports
st.sidebar.markdown("---")
st.sidebar.markdown("#### 📥 Power BI Exports")
if st.sidebar.button("Generate & Update CSV Exports"):
    exports = generate_powerbi_exports(prod_analytics, clean_df, cat_summary, "exports")
    st.sidebar.success(f"Generated {len(exports)} analytical CSVs in `exports/`!")

# Export Download Links
export_files = [
    ("inventory_summary.csv", "⬇️ Download inventory_summary.csv"),
    ("product_risk.csv", "⬇️ Download product_risk.csv"),
    ("demand_trends.csv", "⬇️ Download demand_trends.csv"),
    ("category_summary.csv", "⬇️ Download category_summary.csv")
]

for fname, label in export_files:
    fpath = os.path.join("exports", fname)
    if os.path.exists(fpath):
        with open(fpath, "rb") as f:
            st.sidebar.download_button(
                label,
                f,
                file_name=fname,
                mime="text/csv",
                key=f"dl_{fname}"
            )

# GLOBAL INTERACTIVE FILTERS
st.sidebar.markdown("---")
st.sidebar.markdown("#### 🔍 Filter Engine")

all_categories = sorted(prod_analytics["category"].unique().tolist())
selected_categories = st.sidebar.multiselect("Category Filter", all_categories, default=all_categories)

all_statuses = [STATUS_CRITICAL, STATUS_LOW_STOCK, STATUS_HEALTHY, STATUS_OVERSTOCK, STATUS_SLOW_MOVING]
available_statuses = [s for s in all_statuses if s in prod_analytics["inventory_status"].unique()]
selected_statuses = st.sidebar.multiselect("Inventory Status", available_statuses, default=available_statuses)

all_tiers = [RISK_TIER_CRITICAL, RISK_TIER_HIGH, RISK_TIER_MEDIUM, RISK_TIER_LOW]
available_tiers = [t for t in all_tiers if t in prod_analytics["risk_tier"].unique()]
selected_tiers = st.sidebar.multiselect("Risk Tier", available_tiers, default=available_tiers)

# Filter product analytics
filtered_prods = prod_analytics[
    (prod_analytics["category"].isin(selected_categories)) &
    (prod_analytics["inventory_status"].isin(selected_statuses)) &
    (prod_analytics["risk_tier"].isin(selected_tiers))
].copy()

# Filter clean transactions
filtered_clean = clean_df[
    (clean_df["category"].isin(selected_categories)) &
    (clean_df["sku"].isin(filtered_prods["sku"]))
].copy()

# HEADER
st.markdown('<div class="hero-title">Inventory Intelligence Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">Demand, Stock Risk & Inventory Optimization Platform</div>', unsafe_allow_html=True)

# -------------------------------------------------------------
# PAGE 1: EXECUTIVE OVERVIEW
# -------------------------------------------------------------
if page == "📊 Executive Overview":
    # ── KPI calculations (unchanged) ──────────────────────────
    tot_products = len(filtered_prods)
    tot_stock = int(filtered_prods["current_stock"].sum())
    tot_demand = int(filtered_prods["total_demand"].sum())
    stockout_count = int((filtered_prods["inventory_status"] == STATUS_CRITICAL).sum())
    overstock_count = int((filtered_prods["inventory_status"] == STATUS_OVERSTOCK).sum())
    slow_count = int((filtered_prods["inventory_status"] == STATUS_SLOW_MOVING).sum())
    tot_value = filtered_prods["inventory_value"].sum()
    tot_excess_val = filtered_prods["overstock_value"].sum()

    # ── Row 1: four cards — Products · Inventory · Demand · Stock-Out ──
    k1, k2, k3, k4 = st.columns(4)

    with k1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Total Products</div>
            <div class="kpi-value">{tot_products}</div>
            <div class="kpi-sub">SKUs Analyzed</div>
        </div>
        """, unsafe_allow_html=True)
    with k2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Total Inventory</div>
            <div class="kpi-value">{tot_stock:,.0f}</div>
            <div class="kpi-sub">Units On-Hand</div>
        </div>
        """, unsafe_allow_html=True)
    with k3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Total Demand</div>
            <div class="kpi-value">{tot_demand:,.0f}</div>
            <div class="kpi-sub">Units Consumed</div>
        </div>
        """, unsafe_allow_html=True)
    with k4:
        st.markdown(f"""
        <div class="kpi-card" style="border-left: 3px solid #EF4444;">
            <div class="kpi-title" style="color:#F87171;">Stockout Risk</div>
            <div class="kpi-value" style="color:#EF4444;">{stockout_count}</div>
            <div class="kpi-sub">Critical / Depleted</div>
        </div>
        """, unsafe_allow_html=True)

    # Small vertical gap between the two KPI rows
    st.markdown('<div class="kpi-row-gap"></div>', unsafe_allow_html=True)

    # ── Row 2: four cards — Overstock · Slow-Moving · Inv. Value · Excess ──
    k5, k6, k7, k8 = st.columns(4)

    with k5:
        st.markdown(f"""
        <div class="kpi-card" style="border-left: 3px solid #6366F1;">
            <div class="kpi-title" style="color:#818CF8;">Overstock SKUs</div>
            <div class="kpi-value" style="color:#6366F1;">{overstock_count}</div>
            <div class="kpi-sub">&gt; {int(cfg_over_days)} Days Coverage</div>
        </div>
        """, unsafe_allow_html=True)
    with k6:
        st.markdown(f"""
        <div class="kpi-card" style="border-left: 3px solid #8B5CF6;">
            <div class="kpi-title" style="color:#A78BFA;">Slow-Moving SKUs</div>
            <div class="kpi-value" style="color:#8B5CF6;">{slow_count}</div>
            <div class="kpi-sub">Low Turnover Velocity</div>
        </div>
        """, unsafe_allow_html=True)
    with k7:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Inv. Value</div>
            <div class="kpi-value">${tot_value/1000:,.1f}k</div>
            <div class="kpi-sub">Working Capital Tied</div>
        </div>
        """, unsafe_allow_html=True)
    with k8:
        st.markdown(f"""
        <div class="kpi-card" style="border-left: 3px solid #F59E0B;">
            <div class="kpi-title" style="color:#FBBF24;">Excess Value</div>
            <div class="kpi-value">${tot_excess_val/1000:,.1f}k</div>
            <div class="kpi-sub">Trapped Cash</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Urgent Stock-Out Alert Banner if any critical items
    critical_items = filtered_prods[filtered_prods["inventory_status"] == STATUS_CRITICAL]
    if not critical_items.empty:
        crit_names = ", ".join(critical_items["product_name"].head(3).tolist())
        more_str = f" and {len(critical_items)-3} more" if len(critical_items) > 3 else ""
        st.markdown(f"""
        <div class="alert-banner">
            <strong style="color:#EF4444; font-size:1.05rem;">🚨 Immediate Attention Required:</strong>
            <span style="color:#F8FAFC;"> {len(critical_items)} product(s) face imminent stock exhaustion or zero inventory ({crit_names}{more_str}). Immediate replenishment purchase orders recommended.</span>
        </div>
        """, unsafe_allow_html=True)

    # Visual Charts Row 1: Status Distribution Donut & Total Demand Trend
    col_ch1, col_ch2 = st.columns([4, 6])
    
    with col_ch1:
        st.markdown('<div class="section-title">📦 Inventory Status Distribution</div>', unsafe_allow_html=True)
        status_counts = filtered_prods["inventory_status"].value_counts().reset_index()
        status_counts.columns = ["Status", "Count"]
        
        fig_donut = px.pie(
            status_counts,
            names="Status",
            values="Count",
            hole=0.55,
            color="Status",
            color_discrete_map=STATUS_COLORS
        )
        fig_donut.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#CBD5E1"),
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
            margin=dict(t=10, b=30, l=10, r=10)
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    with col_ch2:
        st.markdown('<div class="section-title">📈 Overall Demand Trend (Units Sold Over Time)</div>', unsafe_allow_html=True)
        if "date" in filtered_clean.columns:
            daily_agg = filtered_clean.groupby("date")["units_sold"].sum().reset_index()
            # 7-day rolling average for smooth trend
            daily_agg["7d_ma"] = daily_agg["units_sold"].rolling(7, min_periods=1).mean()
            
            fig_trend = go.Figure()
            fig_trend.add_trace(go.Bar(
                x=daily_agg["date"],
                y=daily_agg["units_sold"],
                name="Daily Units Sold",
                marker_color="rgba(56, 189, 248, 0.4)",
                opacity=0.6
            ))
            fig_trend.add_trace(go.Scatter(
                x=daily_agg["date"],
                y=daily_agg["7d_ma"],
                name="7-Day Moving Avg",
                line=dict(color="#38BDF8", width=3)
            ))
            fig_trend.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#CBD5E1"),
                xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)"),
                yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)", title="Units Sold"),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                margin=dict(t=25, b=20, l=10, r=10)
            )
            st.plotly_chart(fig_trend, use_container_width=True)
        else:
            st.info("Date column not present in dataset; demand trend chart unavailable.")

    # Charts Row 2: Top High-Demand vs Critical Stock-Out vs Overstock
    c_sub1, c_sub2 = st.columns(2)
    with c_sub1:
        st.markdown('<div class="section-title">🔥 Top 7 High-Demand Products</div>', unsafe_allow_html=True)
        top_demand = filtered_prods.sort_values("total_demand", ascending=True).tail(7)
        fig_bar = px.bar(
            top_demand,
            x="total_demand",
            y="product_name",
            orientation="h",
            color="category",
            text="total_demand",
            labels={"total_demand": "Total Units Sold", "product_name": "Product"}
        )
        fig_bar.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#CBD5E1"),
            xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)"),
            yaxis=dict(autorange="reversed"),
            margin=dict(t=10, b=10, l=10, r=10)
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with c_sub2:
        st.markdown('<div class="section-title">🚨 Critical Stock-Out Watchlist</div>', unsafe_allow_html=True)
        if not critical_items.empty:
            crit_display = critical_items[[
                "sku", "product_name", "category", "current_stock", 
                "avg_daily_demand", "days_of_inventory", "inventory_risk_score"
            ]].copy()
            crit_display.columns = ["SKU", "Product", "Category", "Stock", "Daily Demand", "Days Remaining", "Risk Score"]
            st.dataframe(
                crit_display.sort_values("Risk Score", ascending=False),
                hide_index=True,
                use_container_width=True
            )
        else:
            st.success("No products currently at critical stock-out status.")

# -------------------------------------------------------------
# PAGE 2: DEMAND ANALYTICS
# -------------------------------------------------------------
elif page == "📈 Demand Analytics":
    st.markdown('<div class="section-title">📈 Multi-Dimensional Demand Analytics</div>', unsafe_allow_html=True)

    # Time Granularity Selector
    t_col1, t_col2 = st.columns([3, 7])
    with t_col1:
        freq_option = st.selectbox(
            "Aggregation Cadence",
            ["Daily ('D')", "Weekly ('W')", "Monthly ('M')"],
            index=0
        )
        freq_code = "D" if "Daily" in freq_option else ("W" if "Weekly" in freq_option else "M")

    # Time Series Demand Chart
    if "date" in filtered_clean.columns:
        ts_demand = compute_time_series_demand(filtered_clean, freq=freq_code)
        fig_ts = px.line(
            ts_demand,
            x="date",
            y="units_sold",
            color="category",
            title=f"Category Demand Velocity Trend ({freq_option})",
            labels={"units_sold": "Units Sold", "date": "Date", "category": "Category"}
        )
        fig_ts.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#CBD5E1"),
            xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)"),
            yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_ts, use_container_width=True)

    # Top 10 vs Bottom 10 Demand Comparison
    d_col1, d_col2 = st.columns(2)
    with d_col1:
        st.markdown('<div class="section-title">🏆 Top 10 Products by Demand</div>', unsafe_allow_html=True)
        top_10 = filtered_prods.sort_values("total_demand", ascending=False).head(10)
        fig_top10 = px.bar(
            top_10,
            x="total_demand",
            y="product_name",
            orientation="h",
            color="avg_daily_demand",
            color_continuous_scale="Viridis",
            labels={"total_demand": "Units Sold", "product_name": "Product", "avg_daily_demand": "Daily Demand"}
        )
        fig_top10.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#CBD5E1"),
            yaxis=dict(autorange="reversed")
        )
        st.plotly_chart(fig_top10, use_container_width=True)

    with d_col2:
        st.markdown('<div class="section-title">📉 Bottom 10 Products by Demand (Low Velocity)</div>', unsafe_allow_html=True)
        bottom_10 = filtered_prods.sort_values("total_demand", ascending=True).head(10)
        fig_bot10 = px.bar(
            bottom_10,
            x="total_demand",
            y="product_name",
            orientation="h",
            color="current_stock",
            color_continuous_scale="Magma",
            labels={"total_demand": "Units Sold", "product_name": "Product", "current_stock": "Current Stock"}
        )
        fig_bot10.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#CBD5E1"),
            yaxis=dict(autorange="reversed")
        )
        st.plotly_chart(fig_bot10, use_container_width=True)

    # Category Level Demand & Velocity Breakdown
    st.markdown('<div class="section-title">🏷️ Category Demand & Inventory Value Summary</div>', unsafe_allow_html=True)
    cat_disp = cat_summary[[
        "category", "total_products", "total_demand", "total_inventory",
        "total_inventory_value", "total_overstock_value", "critical_count", "overstock_count"
    ]].copy()
    cat_disp.columns = [
        "Category", "SKUs", "Total Demand", "Total Stock", "Inventory Value ($)",
        "Overstock Value ($)", "Critical Stockouts", "Overstocked SKUs"
    ]
    st.dataframe(cat_disp.style.format({
        "Total Demand": "{:,.0f}",
        "Total Stock": "{:,.0f}",
        "Inventory Value ($)": "${:,.2f}",
        "Overstock Value ($)": "${:,.2f}"
    }), use_container_width=True, hide_index=True)

    # Detailed Demand Table
    st.markdown('<div class="section-title">📋 Comprehensive Product Demand & Velocity Ledger</div>', unsafe_allow_html=True)
    full_demand_table = filtered_prods[[
        "sku", "product_name", "category", "total_demand", "avg_daily_demand",
        "movement_class", "demand_trend", "trend_pct", "current_stock", "days_of_inventory"
    ]].copy()
    st.dataframe(full_demand_table, use_container_width=True, hide_index=True)

# -------------------------------------------------------------
# PAGE 3: STOCK RISK & STOCK-OUTS
# -------------------------------------------------------------
elif page == "⚠️ Stock Risk & Stock-Outs":
    st.markdown('<div class="section-title">⚠️ Stock-Out Risk Engine & Replenishment Matrix</div>', unsafe_allow_html=True)

    # Prominent Immediate Action Required Section
    crit_high = filtered_prods[filtered_prods["risk_tier"].isin([RISK_TIER_CRITICAL, RISK_TIER_HIGH])]
    
    st.markdown("""
    <div class="alert-banner">
        <h4 style="margin:0 0 8px 0; color:#EF4444;">🚨 Immediate Action Required: Expedited Reorders</h4>
        <div>The products below have high stock-out risk due to imminent stock depletion relative to supplier lead times.
        Procurement action must be initiated to prevent stock-outs.</div>
    </div>
    """, unsafe_allow_html=True)

    if not crit_high.empty:
        action_table = crit_high[[
            "sku", "product_name", "category", "current_stock", "avg_daily_demand",
            "days_of_inventory", "reorder_point", "lead_time_days", "inventory_risk_score",
            "risk_tier", "recommended_action", "recommendation_rationale"
        ]].sort_values("inventory_risk_score", ascending=False)
        st.dataframe(action_table, use_container_width=True, hide_index=True)
    else:
        st.success("No products are currently in Critical or High Risk stockout tiers.")

    # Visualizations: Risk Distribution & Stock vs Demand Scatter
    r_col1, r_col2 = st.columns(2)

    with r_col1:
        st.markdown('<div class="section-title">📊 Inventory Risk Score Distribution (0 - 100)</div>', unsafe_allow_html=True)
        fig_risk = px.histogram(
            filtered_prods,
            x="inventory_risk_score",
            color="risk_tier",
            color_discrete_map=RISK_TIER_COLORS,
            nbins=20,
            labels={"inventory_risk_score": "Inventory Risk Score", "count": "Product Count"}
        )
        fig_risk.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#CBD5E1"),
            xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)"),
            yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)")
        )
        st.plotly_chart(fig_risk, use_container_width=True)

    with r_col2:
        st.markdown('<div class="section-title">🎯 Current Stock vs. Daily Demand (Risk Quadrant)</div>', unsafe_allow_html=True)
        fig_scatter = px.scatter(
            filtered_prods,
            x="avg_daily_demand",
            y="current_stock",
            color="risk_tier",
            color_discrete_map=RISK_TIER_COLORS,
            size="total_demand",
            hover_name="product_name",
            hover_data=["sku", "days_of_inventory", "lead_time_days", "inventory_risk_score"],
            labels={"avg_daily_demand": "Average Daily Demand (Units)", "current_stock": "Current Stock On-Hand"}
        )
        # Add safety threshold lines
        fig_scatter.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#CBD5E1"),
            xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)"),
            yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)")
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    # Days of Inventory Distribution
    st.markdown('<div class="section-title">⏱️ Days of Inventory Remaining by Product</div>', unsafe_allow_html=True)
    days_plot_df = filtered_prods.copy()
    days_plot_df["capped_days"] = days_plot_df["days_of_inventory"].clip(upper=120)
    fig_days = px.bar(
        days_plot_df.sort_values("days_of_inventory"),
        x="product_name",
        y="capped_days",
        color="inventory_status",
        color_discrete_map=STATUS_COLORS,
        labels={"capped_days": "Days of Inventory (Capped at 120D)", "product_name": "Product"}
    )
    fig_days.add_hline(y=cfg_low_days, line_dash="dash", line_color="#EF4444", annotation_text=f"Low Stock Threshold ({cfg_low_days}d)")
    fig_days.add_hline(y=cfg_over_days, line_dash="dash", line_color="#6366F1", annotation_text=f"Overstock Threshold ({cfg_over_days}d)")
    fig_days.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#CBD5E1"),
        xaxis=dict(tickangle=-45, showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)")
    )
    st.plotly_chart(fig_days, use_container_width=True)

    # Transparent Scoring Explanation Accordion
    with st.expander("ℹ️ How the Inventory Risk Score (0 - 100) is Calculated"):
        st.markdown("""
        **The Inventory Risk Score measures product stock-out vulnerability based on four objective operational factors:**
        
        1. **Coverage Urgency (0–40 Points):** Evaluates days of inventory relative to supplier lead time. If days remaining < lead time, replenishment cannot arrive before stock exhaustion, earning maximum penalty.
        2. **Stock Depletion & Reorder Threshold (0–25 Points):** Measures proximity of on-hand inventory to 0 or below the reorder point.
        3. **Demand Velocity & Acceleration (0–20 Points):** Penalizes products with rising demand or high consumption rates that deplete existing stock faster than anticipated.
        4. **Lead Time Exposure (0–15 Points):** Long supplier replenishment cycles increase vulnerability if reordering is delayed.
        
        *Note: This is an explainable operational vulnerability index, not a speculative statistical probability.*
        """)

# -------------------------------------------------------------
# PAGE 4: OVERSTOCK & SLOW-MOVING
# -------------------------------------------------------------
elif page == "🧊 Overstock & Slow-Moving":
    st.markdown('<div class="section-title">🧊 Overstock, Sluggish Inventory & Trapped Capital Analysis</div>', unsafe_allow_html=True)

    overstocked_df = filtered_prods[filtered_prods["inventory_status"] == STATUS_OVERSTOCK]
    slow_moving_df = filtered_prods[filtered_prods["inventory_status"] == STATUS_SLOW_MOVING]

    # Metrics
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Overstocked Products", f"{len(overstocked_df)} SKUs")
    with m2:
        st.metric("Total Excess Units", f"{overstocked_df['excess_inventory'].sum():,.0f} units")
    with m3:
        st.metric("Trapped Capital in Excess Stock", f"${overstocked_df['overstock_value'].sum():,.2f}")
    with m4:
        st.metric("Slow-Moving Products", f"{len(slow_moving_df)} SKUs")

    # Overstock Table & Excess Valuation
    st.markdown('<div class="section-title">📦 Overstocked SKUs & Working Capital Reclaim Opportunity</div>', unsafe_allow_html=True)
    if not overstocked_df.empty:
        over_disp = overstocked_df[[
            "sku", "product_name", "category", "current_stock", "avg_daily_demand",
            "days_of_inventory", "excess_inventory", "excess_inventory_pct",
            "unit_cost", "overstock_value", "recommended_action", "recommendation_rationale"
        ]].sort_values("overstock_value", ascending=False)
        st.dataframe(over_disp.style.format({
            "current_stock": "{:,.0f}",
            "avg_daily_demand": "{:.2f}",
            "days_of_inventory": "{:.1f}",
            "excess_inventory": "{:,.0f}",
            "excess_inventory_pct": "{:.1f}%",
            "unit_cost": "${:,.2f}",
            "overstock_value": "${:,.2f}"
        }), use_container_width=True, hide_index=True)
    else:
        st.success("No products currently exceed the configured overstock threshold.")

    # Slow Moving Products Section
    st.markdown('<div class="section-title">🐢 Slow-Moving Inventory & Turnover Velocity Diagnostics</div>', unsafe_allow_html=True)
    if not slow_moving_df.empty:
        slow_disp = slow_moving_df[[
            "sku", "product_name", "category", "current_stock", "total_demand",
            "avg_daily_demand", "turnover_daily_pct", "days_of_inventory",
            "last_sale_date", "demand_trend", "trend_pct", "recommended_action"
        ]].sort_values("avg_daily_demand", ascending=True)
        st.dataframe(slow_disp.style.format({
            "current_stock": "{:,.0f}",
            "total_demand": "{:,.0f}",
            "avg_daily_demand": "{:.3f}",
            "turnover_daily_pct": "{:.2f}%",
            "days_of_inventory": "{:.0f}",
            "trend_pct": "{:+.1f}%"
        }), use_container_width=True, hide_index=True)
    else:
        st.success("No products currently classified as slow-moving.")

    # Mitigation Strategy Matrix
    st.markdown('<div class="section-title">💡 Actionable Optimization Strategies</div>', unsafe_allow_html=True)
    strat_col1, strat_col2, strat_col3 = st.columns(3)
    with strat_col1:
        st.info("""
        **1. Reduce Future Purchasing:**
        - Suspend automatic replenishment orders for SKUs with > 60 days coverage.
        - Negotiate supplier volume postponements.
        """)
    with strat_col2:
        st.warning("""
        **2. Targeted Promotional Stimulation:**
        - Bundle overstocked items with high-demand complementary products.
        - Feature slow-moving merchandise on seasonal banners.
        """)
    with strat_col3:
        st.success("""
        **3. Dynamic Lead Time & Reorder Alignment:**
        - Recalibrate safety stock buffers downward for stagnant items.
        - Reallocate freed warehouse space to top-velocity revenue drivers.
        """)

# -------------------------------------------------------------
# PAGE 5: PRODUCT EXPLORER & FORECASTING
# -------------------------------------------------------------
elif page == "🔍 Product Explorer":
    st.markdown('<div class="section-title">🔍 Single Product Deep Dive & Demand Forecasting</div>', unsafe_allow_html=True)

    # Product Selector
    prod_options = [f"{row['sku']} — {row['product_name']}" for _, row in filtered_prods.iterrows()]
    if not prod_options:
        st.warning("No products match the selected sidebar filters.")
    else:
        selected_option = st.selectbox("Select Product to Inspect", prod_options, index=0)
        selected_sku = selected_option.split(" — ")[0]
        
        prod_row = filtered_prods[filtered_prods["sku"] == selected_sku].iloc[0]
        prod_history = clean_df[clean_df["sku"] == selected_sku].copy()

        # Product Header & Status Badge
        badge_cls = {
            STATUS_CRITICAL: "badge-critical",
            STATUS_LOW_STOCK: "badge-low-stock",
            STATUS_HEALTHY: "badge-healthy",
            STATUS_OVERSTOCK: "badge-overstock",
            STATUS_SLOW_MOVING: "badge-slow-moving"
        }.get(prod_row["inventory_status"], "badge-healthy")

        st.markdown(f"""
        <div style="background: rgba(30, 41, 59, 0.5); padding: 16px 20px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.08); margin-bottom: 20px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h2 style="margin: 0; color: #F8FAFC;">{prod_row['product_name']}</h2>
                    <span style="color: #94A3B8; font-size: 0.9rem;">SKU: {prod_row['sku']} | Category: {prod_row['category']}</span>
                </div>
                <div style="text-align: right;">
                    <span class="badge {badge_cls}" style="font-size: 0.9rem; padding: 6px 14px;">{prod_row['inventory_status']}</span>
                    <div style="margin-top: 6px; font-size: 0.85rem; color: #94A3B8;">Risk Score: <strong style="color:#F8FAFC;">{prod_row['inventory_risk_score']}/100 ({prod_row['risk_tier']})</strong></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 6 KPI cards for this product
        p_c1, p_c2, p_c3, p_c4, p_c5, p_c6 = st.columns(6)
        with p_c1:
            st.metric("Current Stock", f"{int(prod_row['current_stock']):,} units")
        with p_c2:
            st.metric("Total Demand", f"{int(prod_row['total_demand']):,} units")
        with p_c3:
            st.metric("Daily Demand", f"{prod_row['avg_daily_demand']:.2f} units/day")
        with p_c4:
            st.metric("Days of Inventory", f"{prod_row['days_of_inventory']:.1f} days")
        with p_c5:
            st.metric("Reorder Point", f"{int(prod_row['reorder_point']):,} units")
        with p_c6:
            st.metric("Inventory Value", f"${prod_row['inventory_value']:,.2f}")

        # Explainable Recommendation Card
        st.markdown(f"""
        <div style="background: rgba(15, 23, 42, 0.9); border-left: 4px solid {prod_row['action_color']}; border-radius: 8px; padding: 16px; margin: 18px 0;">
            <div style="font-size: 0.85rem; text-transform: uppercase; color: #94A3B8; font-weight: 600;">System Recommendation</div>
            <div style="font-size: 1.15rem; font-weight: 700; color: #F8FAFC; margin: 4px 0 8px 0;">{prod_row['recommended_action']}</div>
            <div style="color: #CBD5E1; font-size: 0.95rem; line-height: 1.5;"><strong>Rationale:</strong> {prod_row['recommendation_rationale']}</div>
            <div style="color: #94A3B8; font-size: 0.85rem; margin-top: 6px;"><strong>Operational Impact:</strong> {prod_row['expected_impact']}</div>
        </div>
        """, unsafe_allow_html=True)

        # Demand Forecasting Section
        st.markdown('<div class="section-title">🔮 Machine Learning Demand Forecast (Horizon Analysis)</div>', unsafe_allow_html=True)
        fc_horizon = st.slider("Forecast Horizon (Days Ahead)", min_value=7, max_value=30, value=14, step=1)
        
        forecast_result = forecast_product_demand(prod_history, horizon_days=fc_horizon)
        
        if forecast_result["success"]:
            hist_df = forecast_result["historical_df"]
            fc_df = forecast_result["forecast_df"]
            metrics = forecast_result["metrics"]

            # Display forecast validation metrics
            f_m1, f_m2, f_m3, f_m4 = st.columns(4)
            with f_m1:
                st.metric("Forecast Algorithm", "Linear Trend + 7D MA")
            with f_m2:
                st.metric("Backtest MAE (Mean Abs Error)", f"{metrics['MAE']:.2f} units")
            with f_m3:
                st.metric("Backtest RMSE", f"{metrics['RMSE']:.2f} units")
            with f_m4:
                st.metric("Forecast Horizon", f"{metrics['Horizon_Days']} Days Ahead")

            # Plotly Chart: Historical Actuals + Future Forecast
            fig_fc = go.Figure()
            # Historical actuals
            fig_fc.add_trace(go.Scatter(
                x=hist_df["date"],
                y=hist_df["units_sold"],
                name="Historical Actual Demand",
                line=dict(color="#38BDF8", width=2)
            ))
            # Forecast upper confidence bound
            fig_fc.add_trace(go.Scatter(
                x=fc_df["date"],
                y=fc_df["forecast_upper"],
                name="Upper Bound (80% CI)",
                line=dict(color="rgba(192, 132, 252, 0.2)", width=0),
                showlegend=False
            ))
            # Forecast lower confidence bound with fill
            fig_fc.add_trace(go.Scatter(
                x=fc_df["date"],
                y=fc_df["forecast_lower"],
                name="Forecast Confidence Interval",
                fill="tonexty",
                fillcolor="rgba(192, 132, 252, 0.15)",
                line=dict(color="rgba(192, 132, 252, 0.2)", width=0)
            ))
            # Forecast mean
            fig_fc.add_trace(go.Scatter(
                x=fc_df["date"],
                y=fc_df["forecast_demand"],
                name=f"Predicted Demand ({fc_horizon}d)",
                line=dict(color="#C084FC", width=3, dash="dash")
            ))
            fig_fc.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#CBD5E1"),
                xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)", title="Date"),
                yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)", title="Units Demanded"),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig_fc, use_container_width=True)
        else:
            st.info(forecast_result["message"])

        # Raw Transaction History Accordion
        with st.expander("📄 View Historical Transaction Log"):
            st.dataframe(prod_history.sort_values("date", ascending=False).head(50), use_container_width=True, hide_index=True)

# -------------------------------------------------------------
# PAGE 6: DATA PROFILING & AUDIT
# -------------------------------------------------------------
elif page == "⚙️ Data Profiling & Audit":
    st.markdown('<div class="section-title">⚙️ Data Ingestion Profile & Cleaning Audit Log</div>', unsafe_allow_html=True)

    # Profiling Metrics
    p1, p2, p3, p4 = st.columns(4)
    with p1:
        st.metric("Total Records Ingested", f"{profile['rows']:,}")
    with p2:
        st.metric("Total Raw Columns", f"{profile['columns']}")
    with p3:
        st.metric("Duplicate Rows Detected", f"{profile['duplicate_count']}")
    with p4:
        st.metric("Clean Records Retained", f"{audit_log['rows_after_cleaning']:,}")

    # Column Mapping Table
    st.markdown('<div class="section-title">🗺️ Automatic Column Mapping Results</div>', unsafe_allow_html=True)
    map_data = []
    for canonical, mapped in profile["column_mapping"].items():
        map_data.append({
            "Canonical Field": canonical,
            "Mapped Raw Column": mapped if mapped else "Not Present (Handled with defaults)",
            "Status": "✅ Mapped" if mapped else "⚠️ Default Applied"
        })
    st.dataframe(pd.DataFrame(map_data), use_container_width=True, hide_index=True)

    # Cleaning Audit Log
    st.markdown('<div class="section-title">🧹 Transparent Preprocessing Decisions</div>', unsafe_allow_html=True)
    for dec in audit_log["cleaning_decisions"]:
        st.markdown(f"- {dec}")

    # Raw Dataset Sample
    with st.expander("🔎 Inspect Ingested Raw Dataset (First 20 Rows)"):
        st.dataframe(raw_df.head(20), use_container_width=True)
