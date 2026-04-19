"""
main.py — AquaGuard IoT Water Leakage Detection System  (v4.0 — Nature UI)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
UI v4.0 CHANGES (UI/UX only — all backend logic is UNTOUCHED):
  ✦  Deep-ocean bioluminescent design theme
  ✦  Animated ripple header with wave SVG decoration
  ✦  Glassmorphism sensor cards with gradient borders
  ✦  Fade-in + slide-up section entrance animations
  ✦  Pulsing red glow on leak — calm cyan glow on normal
  ✦  Redesigned sidebar with nature palette
  ✦  Organic section headers with flowing underline
  ✦  Upgraded Plotly charts (spline curves, gradient fills)
  ✦  Rich alert banner with animated icon
  ✦  Redesigned footer with water-drop motif
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BACKEND CODE IS IDENTICAL TO v3.0 — only layout/CSS/chart styling changed.
Run:  streamlit run main.py
"""

# ═══════════════════════════════════════════════════════════════════════════════
# IMPORTS  — unchanged from v3.0
# ═══════════════════════════════════════════════════════════════════════════════
import time
import random
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime

from database import (
    init_db, log_reading, log_leak_event,
    get_recent_readings, get_leak_history, get_logs, get_leak_logs, get_stats,
)
from alerts import send_email_alert, send_sms_alert


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG  — unchanged from v3.0
# ═══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="AquaGuard — Water Leakage Detection",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ═══════════════════════════════════════════════════════════════════════════════
# ▼▼▼  UI v4.0 — CUSTOM CSS  (nature / deep-ocean bioluminescent theme)  ▼▼▼
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
/* ── Google Fonts: Syne (display) + Nunito (body) ── */
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=Nunito:wght@300;400;500;600&display=swap');

/* ══════════════════════════════════════════════════════════
   DESIGN TOKENS — deep ocean bioluminescent palette
   ══════════════════════════════════════════════════════════ */
:root {
    /* backgrounds */
    --bg-deep:      #020b14;
    --bg-mid:       #041826;
    --bg-surface:   #062035;
    --bg-card:      rgba(6, 32, 53, 0.75);
    --bg-card-alt:  rgba(4, 24, 38, 0.85);

    /* accent colours */
    --cyan:         #00d4ff;
    --cyan-dim:     rgba(0, 212, 255, 0.12);
    --cyan-glow:    rgba(0, 212, 255, 0.35);
    --teal:         #00e5b0;
    --teal-dim:     rgba(0, 229, 176, 0.12);
    --teal-glow:    rgba(0, 229, 176, 0.30);
    --emerald:      #10b981;
    --sky:          #38bdf8;
    --red:          #ff4d6d;
    --red-dim:      rgba(255, 77, 109, 0.12);
    --red-glow:     rgba(255, 77, 109, 0.40);
    --amber:        #f59e0b;

    /* text */
    --text-primary:  #e0f4ff;
    --text-secondary:#7ab8cc;
    --text-muted:    #3d7a96;

    /* borders */
    --border:       rgba(0, 180, 220, 0.15);
    --border-bright:rgba(0, 212, 255, 0.40);

    /* typography */
    --font-display: 'Syne', sans-serif;
    --font-body:    'Nunito', sans-serif;
}

/* ── Global reset ── */
html, body, .stApp {
    background: var(--bg-deep) !important;
    color: var(--text-primary) !important;
    font-family: var(--font-body) !important;
}

/* animated background mesh */
.stApp::before {
    content: '';
    position: fixed; inset: 0; z-index: 0; pointer-events: none;
    background:
        radial-gradient(ellipse 80% 50% at 10% 20%, rgba(0,180,220,0.06) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 90% 80%, rgba(0,229,176,0.05) 0%, transparent 55%),
        radial-gradient(ellipse 50% 60% at 50% 50%, rgba(2,11,20,0) 0%, transparent 100%);
    animation: mesh-drift 18s ease-in-out infinite alternate;
}
@keyframes mesh-drift {
    0%   { opacity: 0.6; transform: scale(1)    translateY(0px); }
    100% { opacity: 1.0; transform: scale(1.04) translateY(-12px); }
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #031220 0%, #041a2e 100%) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color: var(--text-primary) !important; }
[data-testid="stSidebar"] .stMarkdown p { color: var(--text-secondary) !important; }

/* sidebar brand */
.sidebar-brand {
    text-align: center;
    padding: 1.2rem 0 0.8rem;
}
.sidebar-brand .brand-icon {
    font-size: 2.8rem;
    display: block;
    animation: float 3s ease-in-out infinite;
    filter: drop-shadow(0 0 12px var(--cyan));
}
.sidebar-brand .brand-name {
    font-family: var(--font-display);
    font-size: 1.3rem;
    font-weight: 800;
    background: linear-gradient(135deg, var(--cyan), var(--teal));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: 0.5px;
    display: block;
    margin-top: 0.3rem;
}
.sidebar-brand .brand-sub {
    font-size: 0.68rem;
    color: var(--text-muted) !important;
    letter-spacing: 2px;
    text-transform: uppercase;
}
@keyframes float {
    0%,100% { transform: translateY(0px);  }
    50%      { transform: translateY(-6px); }
}

/* sidebar section labels */
.sidebar-section {
    font-family: var(--font-display);
    font-size: 0.62rem;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: var(--text-muted) !important;
    padding: 0.15rem 0 0.4rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 0.7rem;
}

/* ── Metric cards  (Streamlit native) ── */
[data-testid="stMetric"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-top: 2px solid var(--cyan) !important;
    border-radius: 14px !important;
    padding: 0.9rem 1.1rem !important;
    backdrop-filter: blur(12px);
    transition: transform 0.25s, box-shadow 0.25s;
}
[data-testid="stMetric"]:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 32px rgba(0,212,255,0.12);
}
[data-testid="stMetricLabel"] {
    color: var(--text-secondary) !important;
    font-family: var(--font-display) !important;
    font-size: 0.7rem !important;
    text-transform: uppercase;
    letter-spacing: 1.5px;
}
[data-testid="stMetricValue"] {
    font-family: var(--font-display) !important;
    font-size: 1.75rem !important;
    font-weight: 700 !important;
    color: var(--cyan) !important;
}
[data-testid="stMetricDelta"] { font-size: 0.78rem !important; }

/* ══════════════════════════════════════════════════════════
   GLASS SENSOR CARDS
   ══════════════════════════════════════════════════════════ */
.sensor-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1.2rem;
    margin: 1rem 0 1.4rem;
}
.glass-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 1.4rem 1.6rem;
    backdrop-filter: blur(16px);
    position: relative;
    overflow: hidden;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    animation: fade-slide-up 0.6s ease both;
}
.glass-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    border-radius: 20px 20px 0 0;
}
.glass-card.card-flow::before   { background: linear-gradient(90deg, var(--cyan), transparent); }
.glass-card.card-moist::before  { background: linear-gradient(90deg, var(--teal), transparent); }
.glass-card.card-status::before { background: linear-gradient(90deg, var(--emerald), transparent); }
.glass-card.card-count::before  { background: linear-gradient(90deg, var(--amber), transparent); }
.glass-card.card-leak::before   { background: linear-gradient(90deg, var(--red), transparent); }

.glass-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 40px rgba(0,0,0,0.3), 0 0 0 1px var(--border-bright);
}
.glass-card .card-icon {
    font-size: 1.9rem;
    line-height: 1;
    margin-bottom: 0.7rem;
    display: block;
}
.glass-card .card-label {
    font-family: var(--font-display);
    font-size: 0.65rem;
    letter-spacing: 2.5px;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-bottom: 0.3rem;
}
.glass-card .card-value {
    font-family: var(--font-display);
    font-size: 2rem;
    font-weight: 800;
    line-height: 1.1;
    color: var(--cyan);
}
.glass-card .card-value.red   { color: var(--red); }
.glass-card .card-value.teal  { color: var(--teal); }
.glass-card .card-value.green { color: var(--emerald); }
.glass-card .card-value.amber { color: var(--amber); }
.glass-card .card-sub {
    font-size: 0.75rem;
    color: var(--text-secondary);
    margin-top: 0.25rem;
}
/* Corner glow orb */
.glass-card .card-orb {
    position: absolute;
    bottom: -25px; right: -25px;
    width: 90px; height: 90px;
    border-radius: 50%;
    opacity: 0.08;
}
.glass-card.card-flow  .card-orb { background: var(--cyan);    box-shadow: 0 0 40px var(--cyan); }
.glass-card.card-moist .card-orb { background: var(--teal);    box-shadow: 0 0 40px var(--teal); }
.glass-card.card-status .card-orb{ background: var(--emerald); box-shadow: 0 0 40px var(--emerald); }

/* ══════════════════════════════════════════════════════════
   STATUS BADGE
   ══════════════════════════════════════════════════════════ */
.status-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    border-radius: 999px;
    padding: 0.45rem 1.3rem;
    font-family: var(--font-display);
    font-size: 0.82rem;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
}
.status-badge.normal {
    background: var(--teal-dim);
    color: var(--teal);
    border: 1px solid rgba(0,229,176,0.35);
    box-shadow: 0 0 20px rgba(0,229,176,0.12);
    animation: glow-teal 2.5s ease-in-out infinite;
}
.status-badge.leak {
    background: var(--red-dim);
    color: var(--red);
    border: 1px solid rgba(255,77,109,0.40);
    box-shadow: 0 0 24px rgba(255,77,109,0.25);
    animation: glow-red 0.9s ease-in-out infinite;
}
.status-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    display: inline-block;
}
.status-badge.normal .status-dot {
    background: var(--teal);
    animation: blink-teal 2s infinite;
}
.status-badge.leak .status-dot {
    background: var(--red);
    animation: blink-red 0.7s infinite;
}
@keyframes glow-teal { 0%,100%{box-shadow:0 0 16px rgba(0,229,176,0.12)} 50%{box-shadow:0 0 28px rgba(0,229,176,0.25)} }
@keyframes glow-red  { 0%,100%{box-shadow:0 0 20px rgba(255,77,109,0.25)} 50%{box-shadow:0 0 40px rgba(255,77,109,0.55)} }
@keyframes blink-teal{ 0%,100%{opacity:1} 50%{opacity:0.3} }
@keyframes blink-red { 0%,100%{opacity:1} 50%{opacity:0.2} }

/* ══════════════════════════════════════════════════════════
   SECTION HEADERS
   ══════════════════════════════════════════════════════════ */
.section-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin: 2rem 0 1.2rem;
    animation: fade-slide-up 0.5s ease both;
}
.section-header .sec-icon {
    font-size: 1.2rem;
    width: 38px; height: 38px;
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    background: var(--bg-surface);
    border: 1px solid var(--border);
    flex-shrink: 0;
}
.section-header .sec-title {
    font-family: var(--font-display);
    font-size: 0.72rem;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: var(--text-secondary);
}
.section-header .sec-line {
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, var(--border), transparent);
}

/* ══════════════════════════════════════════════════════════
   ALERT BANNERS
   ══════════════════════════════════════════════════════════ */
.alert-leak {
    background: linear-gradient(135deg, rgba(255,77,109,0.10) 0%, rgba(255,77,109,0.04) 100%);
    border: 1px solid rgba(255,77,109,0.35);
    border-left: 4px solid var(--red);
    border-radius: 16px;
    padding: 1.2rem 1.6rem;
    margin: 0.5rem 0 1rem;
    animation: alert-shake 0.4s ease, fade-slide-up 0.4s ease;
    position: relative;
    overflow: hidden;
}
.alert-leak::after {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background: linear-gradient(135deg, rgba(255,77,109,0.04), transparent);
    animation: alert-pulse 1.5s ease-in-out infinite;
    pointer-events: none;
}
.alert-leak .al-title {
    font-family: var(--font-display);
    font-size: 1rem;
    font-weight: 700;
    color: var(--red);
    display: flex; align-items: center; gap: 0.5rem;
    margin-bottom: 0.5rem;
}
.alert-leak .al-icon { animation: spin-pulse 1s ease-in-out infinite; display: inline-block; }
.alert-leak .al-body  { font-size: 0.83rem; color: rgba(255,100,130,0.85); line-height: 1.6; }
.alert-leak .al-meta  { font-size: 0.75rem; color: rgba(255,100,130,0.60); margin-top: 0.4rem; }

.alert-normal {
    background: linear-gradient(135deg, rgba(0,229,176,0.08) 0%, rgba(0,229,176,0.03) 100%);
    border: 1px solid rgba(0,229,176,0.25);
    border-left: 4px solid var(--teal);
    border-radius: 16px;
    padding: 1rem 1.4rem;
    display: flex; align-items: center; gap: 0.8rem;
    animation: fade-slide-up 0.4s ease;
}
.alert-normal .an-icon { font-size: 1.4rem; }
.alert-normal .an-text { font-size: 0.85rem; color: var(--teal); font-family: var(--font-display); }
.alert-normal .an-sub  { font-size: 0.75rem; color: rgba(0,229,176,0.60); margin-top: 0.2rem; }

.alert-pill {
    display: inline-flex; align-items: center; gap: 0.5rem;
    background: rgba(245,158,11,0.10);
    color: var(--amber);
    border: 1px solid rgba(245,158,11,0.30);
    border-radius: 8px;
    padding: 0.3rem 0.85rem;
    font-family: var(--font-display);
    font-size: 0.72rem;
    letter-spacing: 0.5px;
    margin-top: 0.6rem;
}

@keyframes alert-shake {
    0%,100%{ transform: translateX(0);   }
    20%    { transform: translateX(-4px); }
    40%    { transform: translateX(4px);  }
    60%    { transform: translateX(-2px); }
    80%    { transform: translateX(2px);  }
}
@keyframes alert-pulse { 0%,100%{opacity:0} 50%{opacity:1} }
@keyframes spin-pulse  { 0%,100%{transform:scale(1)} 50%{transform:scale(1.25)} }

/* ══════════════════════════════════════════════════════════
   FADE-IN ANIMATIONS
   ══════════════════════════════════════════════════════════ */
@keyframes fade-slide-up {
    from { opacity: 0; transform: translateY(16px); }
    to   { opacity: 1; transform: translateY(0);    }
}
.fade-in-1 { animation: fade-slide-up 0.5s ease 0.05s both; }
.fade-in-2 { animation: fade-slide-up 0.5s ease 0.15s both; }
.fade-in-3 { animation: fade-slide-up 0.5s ease 0.25s both; }
.fade-in-4 { animation: fade-slide-up 0.5s ease 0.35s both; }

/* ══════════════════════════════════════════════════════════
   HEADER
   ══════════════════════════════════════════════════════════ */
.app-header {
    position: relative;
    padding: 1.8rem 0 1.4rem;
    margin-bottom: 0.5rem;
    overflow: hidden;
}
.app-header .header-bg {
    position: absolute; inset: 0;
    background: linear-gradient(135deg,
        rgba(0,212,255,0.06) 0%,
        rgba(0,229,176,0.04) 50%,
        transparent 100%);
    border-radius: 20px;
    border: 1px solid var(--border);
}
.app-header .header-content {
    position: relative;
    display: flex; align-items: center;
    gap: 1.4rem;
    padding: 0 1.6rem;
}
.app-header .header-logo {
    font-size: 3.5rem;
    filter: drop-shadow(0 0 16px var(--cyan));
    animation: float 4s ease-in-out infinite;
    line-height: 1;
    flex-shrink: 0;
}
.app-header .header-title {
    font-family: var(--font-display);
    font-size: 1.75rem;
    font-weight: 800;
    background: linear-gradient(135deg, var(--cyan) 0%, var(--teal) 60%, var(--emerald) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0; line-height: 1.15;
}
.app-header .header-sub {
    font-size: 0.78rem;
    color: var(--text-muted);
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-top: 0.3rem;
    font-family: var(--font-display);
}
.app-header .header-badge {
    margin-left: auto;
    font-family: var(--font-display);
    font-size: 0.65rem;
    letter-spacing: 1.5px;
    color: var(--text-muted);
    background: var(--bg-surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 0.35rem 0.75rem;
    white-space: nowrap;
}

/* wave decoration under header */
.wave-divider {
    width: 100%;
    overflow: hidden;
    line-height: 0;
    margin-top: 0.5rem;
    opacity: 0.35;
}
.wave-divider svg { display: block; width: 100%; height: 28px; }

/* ══════════════════════════════════════════════════════════
   HISTORY / DATA TABLE AREA
   ══════════════════════════════════════════════════════════ */
.history-box {
    background: var(--bg-card-alt);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.8rem;
}
.history-count {
    font-family: var(--font-display);
    font-size: 0.75rem;
    color: var(--text-secondary);
    letter-spacing: 1px;
    margin-bottom: 0.6rem;
}
.history-count span {
    color: var(--cyan);
    font-weight: 700;
}

[data-testid="stDataFrame"] {
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    overflow: hidden;
    background: var(--bg-card-alt) !important;
}

/* ══════════════════════════════════════════════════════════
   TABS
   ══════════════════════════════════════════════════════════ */
[data-testid="stTabs"] [role="tablist"] {
    border-bottom: 1px solid var(--border) !important;
    gap: 0.5rem;
}
[data-testid="stTabs"] button[role="tab"] {
    font-family: var(--font-display) !important;
    font-size: 0.78rem !important;
    letter-spacing: 0.5px !important;
    color: var(--text-secondary) !important;
    border-radius: 8px 8px 0 0 !important;
    transition: all 0.2s !important;
}
[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
    color: var(--cyan) !important;
    border-bottom: 2px solid var(--cyan) !important;
    background: var(--cyan-dim) !important;
}

/* ══════════════════════════════════════════════════════════
   BUTTONS
   ══════════════════════════════════════════════════════════ */
.stButton > button {
    background: var(--bg-surface) !important;
    border: 1px solid var(--border) !important;
    color: var(--text-secondary) !important;
    font-family: var(--font-display) !important;
    font-size: 0.78rem !important;
    border-radius: 10px !important;
    letter-spacing: 0.8px;
    transition: all 0.22s ease !important;
}
.stButton > button:hover {
    border-color: var(--cyan) !important;
    color: var(--cyan) !important;
    box-shadow: 0 0 16px rgba(0,212,255,0.15) !important;
    transform: translateY(-1px) !important;
}

/* ══════════════════════════════════════════════════════════
   MISC CONTROLS
   ══════════════════════════════════════════════════════════ */
[data-testid="stCheckbox"] label { color: var(--text-secondary) !important; font-family: var(--font-body) !important; }
[data-testid="stSlider"] label   { color: var(--text-muted) !important; font-size: 0.78rem; font-family: var(--font-body) !important; }
[data-testid="stToggle"]  label  { color: var(--text-primary) !important; }

/* info box */
[data-testid="stInfo"]    { background: rgba(0,212,255,0.06) !important; border-left-color: var(--cyan) !important; border-radius: 10px !important; }
[data-testid="stSuccess"] { background: rgba(0,229,176,0.07) !important; border-left-color: var(--teal) !important; border-radius: 10px !important; }
[data-testid="stError"]   { background: rgba(255,77,109,0.08) !important; border-left-color: var(--red)  !important; border-radius: 10px !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar       { width: 5px; }
::-webkit-scrollbar-track { background: var(--bg-deep); }
::-webkit-scrollbar-thumb { background: rgba(0,180,220,0.25); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: rgba(0,212,255,0.45); }

/* ══════════════════════════════════════════════════════════
   FOOTER
   ══════════════════════════════════════════════════════════ */
.app-footer {
    text-align: center;
    padding: 1.6rem 0 0.8rem;
    border-top: 1px solid var(--border);
    margin-top: 2rem;
}
.app-footer .footer-drops { font-size: 1.2rem; letter-spacing: 6px; opacity: 0.4; margin-bottom: 0.4rem; }
.app-footer .footer-text  {
    font-family: var(--font-display);
    font-size: 0.65rem;
    letter-spacing: 2.5px;
    text-transform: uppercase;
    color: var(--text-muted);
}
.app-footer .footer-stack {
    font-size: 0.7rem;
    color: rgba(61,122,150,0.55);
    margin-top: 0.2rem;
}
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# INITIALISE DATABASES  — unchanged from v3.0
# ═══════════════════════════════════════════════════════════════════════════════
init_db()


# ═══════════════════════════════════════════════════════════════════════════════
# SESSION STATE  — unchanged from v3.0
# ═══════════════════════════════════════════════════════════════════════════════
def _init_state():
    defaults = {
        "running":           False,
        "force_leak":        False,
        "flow_history":      [],
        "moisture_history":  [],
        "time_history":      [],
        "leak_flag":         False,
        "last_leak_trigger": "",
        "prev_flow":         None,
        "tick":              0,
        "alert_sent":        False,
        "session_leaks":     0,
        "alert_log":         [],
        "email_status":      "",
        "sms_status":        "",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init_state()


# ═══════════════════════════════════════════════════════════════════════════════
# BACKEND CONSTANTS & FUNCTIONS  — UNCHANGED from v3.0
# ═══════════════════════════════════════════════════════════════════════════════

NORMAL_FLOW_MEAN   = 12.0
NORMAL_FLOW_STD    = 1.2
NORMAL_MOISTURE    = 30.0
MOISTURE_STD       = 4.0
MOISTURE_THRESHOLD = 70.0
FLOW_DROP_PCT      = 0.45
MAX_HISTORY        = 60


def simulate_sensors(force_leak: bool) -> tuple:
    if force_leak:
        flow     = round(random.uniform(0.5, 3.5), 2)
        moisture = round(random.uniform(72, 95), 2)
    else:
        flow     = round(max(0.0, random.gauss(NORMAL_FLOW_MEAN, NORMAL_FLOW_STD)), 2)
        moisture = round(min(100.0, max(0.0, random.gauss(NORMAL_MOISTURE, MOISTURE_STD))), 2)
    return flow, moisture


def detect_leak(flow: float, moisture: float, prev_flow) -> tuple:
    reasons = []
    if moisture >= MOISTURE_THRESHOLD:
        reasons.append("moisture_high")
    if prev_flow is not None and prev_flow > 0:
        if (prev_flow - flow) / prev_flow >= FLOW_DROP_PCT:
            reasons.append("flow_drop")
    if reasons:
        return True, " + ".join(reasons)
    return False, ""


# ═══════════════════════════════════════════════════════════════════════════════
# ▼▼▼  UI v4.0 — PLOTLY CHART HELPERS  (upgraded styling)  ▼▼▼
# ═══════════════════════════════════════════════════════════════════════════════

# Shared layout applied to every chart
CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(4,24,38,0.55)",
    font=dict(family="Syne, sans-serif", color="#3d7a96", size=11),
    margin=dict(l=8, r=8, t=36, b=8),
    xaxis=dict(
        showgrid=False, zeroline=False,
        color="#3d7a96", linecolor="rgba(0,180,220,0.15)",
        tickfont=dict(size=9),
    ),
    yaxis=dict(
        gridcolor="rgba(0,180,220,0.08)", zeroline=False,
        linecolor="rgba(0,180,220,0.15)",
        tickfont=dict(size=9),
    ),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#7ab8cc", size=10)),
    hovermode="x unified",
    hoverlabel=dict(
        bgcolor="#031220",
        font_size=11,
        font_family="Syne, sans-serif",
        bordercolor="rgba(0,212,255,0.3)",
    ),
)


def make_flow_chart(times, values, leak_flag):
    """Flow rate — spline line + gradient fill, cyan normal / red leak."""
    colour = "#ff4d6d" if leak_flag else "#00d4ff"
    fill   = "rgba(255,77,109,0.12)" if leak_flag else "rgba(0,212,255,0.10)"
    fig = go.Figure()
    # Subtle baseline band
    fig.add_hrect(
        y0=NORMAL_FLOW_MEAN - NORMAL_FLOW_STD,
        y1=NORMAL_FLOW_MEAN + NORMAL_FLOW_STD,
        fillcolor="rgba(0,212,255,0.04)",
        line_width=0,
    )
    fig.add_trace(go.Scatter(
        x=times, y=values,
        mode="lines",
        line=dict(color=colour, width=2.5, shape="spline", smoothing=1.2),
        fill="tozeroy", fillcolor=fill,
        name="Flow Rate (L/min)",
        hovertemplate="<b>%{y:.2f} L/min</b><extra></extra>",
    ))
    fig.add_hline(
        y=NORMAL_FLOW_MEAN, line_dash="dot",
        line_color="rgba(0,212,255,0.35)", line_width=1,
        annotation_text="Baseline 12 L/min",
        annotation_font_color="rgba(0,212,255,0.55)",
        annotation_font_size=10,
    )
    fig.update_layout(
        **CHART_LAYOUT,
        title=dict(text="💧 Water Flow Rate", font=dict(size=13, color="#7ab8cc")),
        yaxis_range=[0, 22],
    )
    return fig


def make_moisture_chart(times, values, leak_flag):
    """Moisture — spline + gradient fill, teal normal / red leak."""
    colour = "#ff4d6d" if leak_flag else "#00e5b0"
    fill   = "rgba(255,77,109,0.12)" if leak_flag else "rgba(0,229,176,0.10)"
    fig = go.Figure()
    # Danger zone shading above threshold
    fig.add_hrect(
        y0=MOISTURE_THRESHOLD, y1=105,
        fillcolor="rgba(255,77,109,0.05)",
        line_width=0,
    )
    fig.add_trace(go.Scatter(
        x=times, y=values,
        mode="lines",
        line=dict(color=colour, width=2.5, shape="spline", smoothing=1.2),
        fill="tozeroy", fillcolor=fill,
        name="Moisture (%)",
        hovertemplate="<b>%{y:.1f}%</b><extra></extra>",
    ))
    fig.add_hline(
        y=MOISTURE_THRESHOLD, line_dash="dash",
        line_color="rgba(255,77,109,0.45)", line_width=1.2,
        annotation_text=f"⚠ Alert threshold {MOISTURE_THRESHOLD}%",
        annotation_font_color="rgba(255,77,109,0.65)",
        annotation_font_size=10,
    )
    fig.update_layout(
        **CHART_LAYOUT,
        title=dict(text="🌿 Moisture Level", font=dict(size=13, color="#7ab8cc")),
        yaxis_range=[0, 108],
    )
    return fig


def make_combined_chart(times, flows, moistures):
    """Combined dual-trace area chart."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=times, y=flows,
        mode="lines", name="Flow Rate",
        line=dict(color="#00d4ff", width=2, shape="spline", smoothing=1.1),
        fill="tozeroy", fillcolor="rgba(0,212,255,0.07)",
        hovertemplate="Flow: <b>%{y:.2f} L/min</b><extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=times, y=moistures,
        mode="lines", name="Moisture %",
        line=dict(color="#00e5b0", width=2, shape="spline", smoothing=1.1),
        fill="tozeroy", fillcolor="rgba(0,229,176,0.07)",
        hovertemplate="Moisture: <b>%{y:.1f}%</b><extra></extra>",
    ))
    fig.update_layout(
        **CHART_LAYOUT,
        title=dict(text="📊 Combined Sensor Trend", font=dict(size=13, color="#7ab8cc")),
        height=230,
    )
    return fig


def make_gauge(value, max_val, title, color, unit=""):
    """Upgraded Plotly gauge — cleaner, more minimal."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title=dict(text=title, font=dict(family="Syne, sans-serif", color="#3d7a96", size=11)),
        number=dict(
            font=dict(family="Syne, sans-serif", color=color, size=26),
            suffix=f" {unit}" if unit else "",
        ),
        gauge=dict(
            axis=dict(
                range=[0, max_val],
                tickcolor="rgba(0,180,220,0.2)",
                tickfont=dict(family="Syne", color="#3d7a96", size=8),
                nticks=6,
            ),
            bar=dict(color=color, thickness=0.22),
            bgcolor="rgba(0,0,0,0)",
            borderwidth=0,
            steps=[
                dict(range=[0, max_val * 0.33], color="rgba(0,180,220,0.05)"),
                dict(range=[max_val * 0.33, max_val * 0.66], color="rgba(0,180,220,0.08)"),
                dict(range=[max_val * 0.66, max_val * 0.85], color="rgba(0,180,220,0.11)"),
                dict(range=[max_val * 0.85, max_val], color="rgba(255,77,109,0.10)"),
            ],
            threshold=dict(
                line=dict(color="rgba(255,77,109,0.55)", width=2),
                thickness=0.7,
                value=max_val * 0.85,
            ),
        ),
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        height=190,
        margin=dict(l=16, r=16, t=28, b=0),
    )
    return fig


# ═══════════════════════════════════════════════════════════════════════════════
# ▼▼▼  UI v4.0 — SIDEBAR  ▼▼▼
# ═══════════════════════════════════════════════════════════════════════════════
with st.sidebar:

    # Brand block
    st.markdown("""
    <div class='sidebar-brand'>
      <span class='brand-icon'>💧</span>
      <span class='brand-name'>AquaGuard</span>
      <span class='brand-sub'>IoT Monitoring System</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)
    st.markdown("<div class='sidebar-section'>System Control</div>", unsafe_allow_html=True)

    # Start / Pause + Reset
    col_a, col_b = st.columns(2)
    with col_a:
        btn_label = "⏸  Pause" if st.session_state.running else "▶  Start"
        if st.button(btn_label, use_container_width=True):
            st.session_state.running = not st.session_state.running
    with col_b:
        if st.button("🔄  Reset", use_container_width=True):
            reset_keys = [
                "flow_history", "moisture_history", "time_history",
                "leak_flag", "last_leak_trigger", "prev_flow", "tick",
                "alert_sent", "session_leaks", "alert_log",
                "email_status", "sms_status",
            ]
            for k in reset_keys:
                if "history" in k or "log" in k:
                    st.session_state[k] = []
                elif k in ("alert_sent", "leak_flag"):
                    st.session_state[k] = False
                elif k == "prev_flow":
                    st.session_state[k] = None
                elif k in ("tick", "session_leaks"):
                    st.session_state[k] = 0
                else:
                    st.session_state[k] = ""
            st.rerun()

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
    st.markdown("<div class='sidebar-section'>Simulation</div>", unsafe_allow_html=True)

    # Manual leak toggle — BACKEND UNCHANGED
    st.session_state.force_leak = st.toggle(
        "🚨 Simulate Leak Manually",
        value=st.session_state.force_leak,
        help="Overrides sensor values to trigger a burst-pipe scenario",
    )

    refresh_rate = st.slider("Refresh interval (s)", 0.5, 3.0, 1.0, 0.5)
    show_raw     = st.checkbox("Show raw readings table")

    st.markdown("<div style='height:0.4rem'></div>", unsafe_allow_html=True)
    st.markdown("<div class='sidebar-section'>Detection Thresholds</div>", unsafe_allow_html=True)
    st.markdown(f"🌊 **Moisture alarm:** `{MOISTURE_THRESHOLD}%`")
    st.markdown(f"📉 **Flow drop alarm:** `>{int(FLOW_DROP_PCT*100)}%` sudden fall")
    st.markdown(f"〰 **Baseline flow:** `{NORMAL_FLOW_MEAN} L/min`")

    st.markdown("<div style='height:0.4rem'></div>", unsafe_allow_html=True)
    st.markdown("<div class='sidebar-section'>Session & DB Stats</div>", unsafe_allow_html=True)

    # Stats — BACKEND UNCHANGED
    stats = get_stats()
    st.metric("Total Readings",     stats["total_readings"])
    st.metric("Leak Events (DB)",   stats["total_leaks"])
    st.metric("Leaks This Session", st.session_state.session_leaks)
    st.metric("Avg Flow (L/min)",   stats["avg_flow"])
    st.metric("Avg Moisture (%)",   stats["avg_moisture"])

    # Last alert status — BACKEND UNCHANGED
    if st.session_state.email_status:
        st.markdown("<div style='height:0.3rem'></div>", unsafe_allow_html=True)
        st.markdown("<div class='sidebar-section'>Last Alert Status</div>", unsafe_allow_html=True)
        st.markdown(f"📧 Email: `{st.session_state.email_status}`")
        st.markdown(f"📱 SMS: `{st.session_state.sms_status}`")


# ═══════════════════════════════════════════════════════════════════════════════
# ▼▼▼  UI v4.0 — HEADER  ▼▼▼
# ═══════════════════════════════════════════════════════════════════════════════
run_state = "🟢 LIVE" if st.session_state.running else "⏸ PAUSED"

st.markdown(f"""
<div class='app-header fade-in-1'>
  <div class='header-bg'></div>
  <div class='header-content'>
    <div class='header-logo'>💧</div>
    <div>
      <div class='header-title'>Smart Water Leakage Detection System</div>
      <div class='header-sub'>IoT Simulation · Nature Conservation · Real-Time Monitoring</div>
    </div>
    <div class='header-badge'>{run_state} &nbsp;·&nbsp; v4.0</div>
  </div>
</div>

<div class='wave-divider'>
  <svg viewBox="0 0 1440 28" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M0,14 C240,28 480,0 720,14 C960,28 1200,0 1440,14 L1440,28 L0,28 Z"
          fill="rgba(0,212,255,0.08)"/>
    <path d="M0,20 C180,8 360,26 540,18 C720,10 900,24 1080,16 C1260,8 1380,22 1440,18 L1440,28 L0,28 Z"
          fill="rgba(0,229,176,0.05)"/>
  </svg>
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# SENSOR TICK  — BACKEND LOGIC UNCHANGED from v3.0
# ═══════════════════════════════════════════════════════════════════════════════
if st.session_state.running:
    flow, moisture = simulate_sensors(st.session_state.force_leak)
    leak, trigger  = detect_leak(flow, moisture, st.session_state.prev_flow)

    now_str = datetime.now().strftime("%H:%M:%S")
    st.session_state.flow_history.append(flow)
    st.session_state.moisture_history.append(moisture)
    st.session_state.time_history.append(now_str)
    st.session_state.prev_flow = flow
    st.session_state.tick += 1

    for key in ["flow_history", "moisture_history", "time_history"]:
        if len(st.session_state[key]) > MAX_HISTORY:
            st.session_state[key] = st.session_state[key][-MAX_HISTORY:]

    if leak:
        st.session_state.leak_flag = True
        st.session_state.last_leak_trigger = trigger
    else:
        st.session_state.leak_flag = False
        if st.session_state.alert_sent:
            st.session_state.alert_sent = False

    log_reading(flow, moisture, leak)
    if leak:
        log_leak_event(trigger or "manual", flow, moisture)

    if leak and not st.session_state.alert_sent:
        st.session_state.session_leaks += 1
        email_result = send_email_alert(flow, moisture, trigger or "manual")
        st.session_state.email_status = email_result
        sms_result   = send_sms_alert(flow, moisture, trigger or "manual")
        st.session_state.sms_status   = sms_result
        st.session_state.alert_log.append({
            "time": datetime.now().strftime("%H:%M:%S"),
            "trigger": trigger or "manual",
            "flow": flow, "moisture": moisture,
            "email": email_result, "sms": sms_result,
        })
        st.session_state.alert_sent = True

# Convenience aliases — UNCHANGED
cur_flow     = st.session_state.flow_history[-1]     if st.session_state.flow_history     else 0.0
cur_moisture = st.session_state.moisture_history[-1] if st.session_state.moisture_history else 0.0
is_leak      = st.session_state.leak_flag


# ═══════════════════════════════════════════════════════════════════════════════
# ▼▼▼  UI v4.0 — SECTION 1: LIVE MONITORING  ▼▼▼
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown("""
<div class='section-header fade-in-2'>
  <div class='sec-icon'>📡</div>
  <span class='sec-title'>Live Monitoring Panel</span>
  <div class='sec-line'></div>
</div>
""", unsafe_allow_html=True)

# ── Status badge ──────────────────────────────────────────────────────────────
if is_leak:
    st.markdown("""
    <div style='margin-bottom:1.2rem'>
      <span class='status-badge leak'>
        <span class='status-dot'></span>
        ⚠ &nbsp; Leak Detected
      </span>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div style='margin-bottom:1.2rem'>
      <span class='status-badge normal'>
        <span class='status-dot'></span>
        ✔ &nbsp; System Normal
      </span>
    </div>
    """, unsafe_allow_html=True)

# ── Glass sensor cards ────────────────────────────────────────────────────────
flow_delta = round(cur_flow - NORMAL_FLOW_MEAN, 2)
mois_delta = round(cur_moisture - NORMAL_MOISTURE, 2)
flow_col   = "red" if is_leak else "cyan"
mois_col   = "red" if cur_moisture >= MOISTURE_THRESHOLD else "teal"
stat_col   = "red" if is_leak else "green"
delta_sign = lambda v: f"+{v:.2f}" if v >= 0 else f"{v:.2f}"

st.markdown(f"""
<div class='sensor-grid fade-in-2'>

  <div class='glass-card card-flow'>
    <div class='card-orb'></div>
    <span class='card-icon'>💧</span>
    <div class='card-label'>Water Flow Rate</div>
    <div class='card-value {flow_col}'>{cur_flow} <span style='font-size:1rem;font-weight:400'>L/min</span></div>
    <div class='card-sub'>{delta_sign(flow_delta)} from baseline &nbsp;·&nbsp; Baseline: {NORMAL_FLOW_MEAN} L/min</div>
  </div>

  <div class='glass-card card-moist'>
    <div class='card-orb'></div>
    <span class='card-icon'>🌿</span>
    <div class='card-label'>Moisture Level</div>
    <div class='card-value {mois_col}'>{cur_moisture} <span style='font-size:1rem;font-weight:400'>%</span></div>
    <div class='card-sub'>{delta_sign(mois_delta)} from baseline &nbsp;·&nbsp; Threshold: {MOISTURE_THRESHOLD}%</div>
  </div>

  <div class='glass-card card-status'>
    <div class='card-orb'></div>
    <span class='card-icon'>{'🚨' if is_leak else '✅'}</span>
    <div class='card-label'>System Status</div>
    <div class='card-value {stat_col}'>{'LEAK' if is_leak else 'NORMAL'}</div>
    <div class='card-sub'>{'Active' if st.session_state.running else 'Paused'} &nbsp;·&nbsp; {st.session_state.tick} ticks logged</div>
  </div>

</div>
""", unsafe_allow_html=True)

# ── Streamlit metric row (DB totals) ─────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("💧 Flow Rate",         f"{cur_flow} L/min",  delta=f"{flow_delta:+.2f} from baseline", delta_color="inverse")
with c2:
    st.metric("🌡 Moisture Level",    f"{cur_moisture} %",  delta=f"{mois_delta:+.2f} from baseline", delta_color="inverse")
with c3:
    st.metric("🔴 Leak Status",       "LEAK" if is_leak else "NORMAL",
              delta="Active" if st.session_state.running else "Paused")
with c4:
    st.metric("🚨 Leaks This Session", st.session_state.session_leaks,
              delta=f"{st.session_state.tick} ticks logged")

# ── Gauges ────────────────────────────────────────────────────────────────────
g1, g2 = st.columns(2)
with g1:
    g_col = "#ff4d6d" if is_leak else "#00d4ff"
    st.plotly_chart(make_gauge(cur_flow, 20, "Flow Rate", g_col, "L/min"),
                    use_container_width=True, config=dict(displayModeBar=False))
with g2:
    g_col2 = "#ff4d6d" if cur_moisture >= MOISTURE_THRESHOLD else "#00e5b0"
    st.plotly_chart(make_gauge(cur_moisture, 100, "Moisture Level", g_col2, "%"),
                    use_container_width=True, config=dict(displayModeBar=False))


# ═══════════════════════════════════════════════════════════════════════════════
# ▼▼▼  UI v4.0 — SECTION 2: ALERTS  ▼▼▼
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown("""
<div class='section-header fade-in-3'>
  <div class='sec-icon'>🚨</div>
  <span class='sec-title'>Alerts Section</span>
  <div class='sec-line'></div>
</div>
""", unsafe_allow_html=True)

if is_leak:
    trigger_label = {
        "moisture_high":            "High moisture reading exceeded threshold",
        "flow_drop":                "Sudden drop in water flow detected",
        "flow_drop + moisture_high":"Both flow drop AND high moisture detected",
        "manual":                   "Manually triggered via dashboard",
    }.get(st.session_state.last_leak_trigger, "Leak condition triggered")

    # st.error() — required alert (v3.0)
    st.error(
        f"🚨 **WATER LEAKAGE DETECTED** — {trigger_label} | "
        f"Flow: **{cur_flow} L/min** | Moisture: **{cur_moisture}%** | "
        f"Time: **{datetime.now().strftime('%H:%M:%S')}**",
        icon="🚨",
    )

    # Custom styled alert banner
    st.markdown(f"""
    <div class='alert-leak fade-in-3'>
      <div class='al-title'>
        <span class='al-icon'>⚠</span>
        WATER LEAKAGE ALERT
      </div>
      <div class='al-body'>
        <strong>Trigger:</strong> {trigger_label}
      </div>
      <div class='al-meta'>
        Flow Rate: <strong>{cur_flow} L/min</strong> &nbsp;|&nbsp;
        Moisture: <strong>{cur_moisture}%</strong> &nbsp;|&nbsp;
        Detected at: <strong>{datetime.now().strftime('%H:%M:%S')}</strong>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Alert dispatch pill
    if st.session_state.alert_sent:
        st.markdown(
            f"<span class='alert-pill'>📧 Email: {st.session_state.email_status}"
            f" &nbsp;|&nbsp; 📱 SMS: {st.session_state.sms_status}</span>",
            unsafe_allow_html=True,
        )

else:
    # st.success() — required (v3.0)
    st.success(
        f"✔ **System Normal** — All sensors within safe range. "
        f"Flow: **{cur_flow} L/min** | Moisture: **{cur_moisture}%**",
        icon="✅",
    )

    st.markdown(f"""
    <div class='alert-normal fade-in-3'>
      <span class='an-icon'>🌊</span>
      <div>
        <div class='an-text'>All Systems Operating Normally</div>
        <div class='an-sub'>
          Flow: <strong>{cur_flow} L/min</strong> &nbsp;·&nbsp;
          Moisture: <strong>{cur_moisture}%</strong> &nbsp;·&nbsp;
          {datetime.now().strftime('%H:%M:%S')}
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# ▼▼▼  UI v4.0 — SECTION 3: GRAPHS  ▼▼▼
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown("""
<div class='section-header fade-in-3'>
  <div class='sec-icon'>📈</div>
  <span class='sec-title'>Graphs Section</span>
  <div class='sec-line'></div>
</div>
""", unsafe_allow_html=True)

if st.session_state.time_history:
    times     = st.session_state.time_history
    flows     = st.session_state.flow_history
    moistures = st.session_state.moisture_history

    ch1, ch2 = st.columns(2)
    with ch1:
        st.plotly_chart(make_flow_chart(times, flows, is_leak),
                        use_container_width=True, config=dict(displayModeBar=False))
    with ch2:
        st.plotly_chart(make_moisture_chart(times, moistures, is_leak),
                        use_container_width=True, config=dict(displayModeBar=False))

    st.plotly_chart(make_combined_chart(times, flows, moistures),
                    use_container_width=True, config=dict(displayModeBar=False))
else:
    st.info("▶ Press **Start** in the sidebar to begin live monitoring.")


# ═══════════════════════════════════════════════════════════════════════════════
# ▼▼▼  UI v4.0 — SECTION 4: HISTORY  ▼▼▼
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown("""
<div class='section-header fade-in-4'>
  <div class='sec-icon'>📋</div>
  <span class='sec-title'>Leak History  (water_data.db → logs)</span>
  <div class='sec-line'></div>
</div>
""", unsafe_allow_html=True)

tab_leaks, tab_full = st.tabs(["⚠ Leak Events Only", "📄 Full Sensor Log"])

with tab_leaks:
    leak_log_rows = get_leak_logs(50)
    if leak_log_rows:
        df_leaks = pd.DataFrame(leak_log_rows)
        df_leaks = df_leaks.rename(columns={
            "id": "ID", "time": "Timestamp",
            "flow": "Flow (L/min)", "moisture": "Moisture (%)", "status": "Status",
        })
        df_leaks["Status"] = "⚠ " + df_leaks["Status"]
        st.markdown(
            f"<div class='history-count'><span>{len(df_leaks)}</span> leak event(s) recorded in water_data.db</div>",
            unsafe_allow_html=True,
        )
        st.dataframe(df_leaks[["ID","Timestamp","Flow (L/min)","Moisture (%)","Status"]],
                     use_container_width=True, hide_index=True)
    else:
        st.markdown("<span style='color:#3d7a96;font-size:0.85rem'>"
                    "No leak events recorded yet — system running clean 🌊</span>",
                    unsafe_allow_html=True)

with tab_full:
    full_log_rows = get_logs(60)
    if full_log_rows:
        df_full = pd.DataFrame(full_log_rows)
        df_full["status"] = df_full["status"].map({
            "Normal":       "✔ Normal",
            "Leak Detected":"⚠ Leak Detected",
        }).fillna(df_full["status"])
        df_full = df_full.rename(columns={
            "id": "ID", "time": "Timestamp",
            "flow": "Flow (L/min)", "moisture": "Moisture (%)", "status": "Status",
        })
        st.markdown(
            f"<div class='history-count'><span>{len(df_full)}</span> total readings in water_data.db</div>",
            unsafe_allow_html=True,
        )
        st.dataframe(df_full[["ID","Timestamp","Flow (L/min)","Moisture (%)","Status"]],
                     use_container_width=True, hide_index=True)
    else:
        st.markdown("<span style='color:#3d7a96;font-size:0.85rem'>"
                    "No readings recorded yet.</span>", unsafe_allow_html=True)

# Alert dispatch log — BACKEND UNCHANGED
if st.session_state.alert_log:
    st.markdown("""
    <div class='section-header' style='margin-top:1.4rem'>
      <div class='sec-icon'>📬</div>
      <span class='sec-title'>Alert Dispatch Log (this session)</span>
      <div class='sec-line'></div>
    </div>
    """, unsafe_allow_html=True)
    df_alerts = pd.DataFrame(st.session_state.alert_log)
    df_alerts = df_alerts.rename(columns={
        "time": "Time", "trigger": "Trigger",
        "flow": "Flow (L/min)", "moisture": "Moisture (%)",
        "email": "Email Result", "sms": "SMS Result",
    })
    st.dataframe(df_alerts, use_container_width=True, hide_index=True)

# Raw readings table — BACKEND UNCHANGED
if show_raw:
    st.markdown("""
    <div class='section-header' style='margin-top:1.4rem'>
      <div class='sec-icon'>🗄</div>
      <span class='sec-title'>Raw Sensor Readings — sensor_readings (last 60)</span>
      <div class='sec-line'></div>
    </div>
    """, unsafe_allow_html=True)
    readings = get_recent_readings(60)
    if readings:
        df_raw = pd.DataFrame(readings)
        df_raw["leak_status"] = df_raw["leak_status"].map({0: "✔ Normal", 1: "⚠ Leak"})
        df_raw = df_raw.rename(columns={
            "id":"ID","timestamp":"Timestamp","flow_rate":"Flow (L/min)",
            "moisture":"Moisture (%)","leak_status":"Status",
        })
        st.dataframe(df_raw[["ID","Timestamp","Flow (L/min)","Moisture (%)","Status"]],
                     use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════════════════════════════════════════
# ▼▼▼  UI v4.0 — FOOTER  ▼▼▼
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class='app-footer'>
  <div class='footer-drops'>💧 💧 💧</div>
  <div class='footer-text'>AquaGuard &nbsp;·&nbsp; Smart Water Conservation System</div>
  <div class='footer-stack'>Streamlit &nbsp;·&nbsp; Plotly &nbsp;·&nbsp; SQLite &nbsp;·&nbsp; SMTP &nbsp;·&nbsp; Twilio &nbsp;·&nbsp; v4.0</div>
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# AUTO-REFRESH  — unchanged from v3.0
# ═══════════════════════════════════════════════════════════════════════════════
if st.session_state.running:
    time.sleep(refresh_rate)
    st.rerun()