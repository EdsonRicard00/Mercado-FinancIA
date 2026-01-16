import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from textblob import TextBlob
from GoogleNews import GoogleNews
import pandas as pd
from datetime import datetime

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(layout="wide", page_title="BolsaValorIAS", page_icon="🏛️")

# --- 2. CSS HÍBRIDO (Header Luxo + Dashboard Dark Tech) ---
st.markdown("""
<style>
    /* IMPORTANDO FONTES: Cinzel (Logo), Playfair (Títulos), Inter (Dados) */
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&family=Inter:wght@300;400;600&family=Playfair+Display:wght@400;600;700&display=swap');

    /* RESET GERAL DARK */
    .stApp {
        background-color: #050505; /* Preto Profundo */
        background-image: radial-gradient(circle at 50% 0%, #1a1a1a 0%, #000000 80%);
        color: #e0e0e0;
        font-family: 'Inter', sans-serif;
    }

    /* --- O HEADER BOLSAVALORIAS (A Joia) --- */
    .logo-box {
        background: linear-gradient(120deg, #ffffff 0%, #f0f0f0 30%, #e6e6e6 50%, #fbf5b7 85%, #d4af37 100%);
        border: 2px solid #ffffff;
        border-radius: 20px;
        padding: 40px 20px;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 0 40px rgba(212, 175, 55, 0.2), inset 0 0 20px rgba(255, 255, 255, 0.8);
        position: relative;
        overflow: hidden;
    }
    
    /* Efeito de brilho */
    .logo-box::before {
        content: ''; position: absolute; top: 0; left: -50%; width: 100%; height: 100%;
        background: linear-gradient(to right, transparent, rgba(255,255,255,0.8), transparent);
        transform: skewX(-25deg); animation: shine 6s infinite;
    }

    .logo-text {
        font-family: 'Cinzel', serif; font-size: 65px; font-weight: 700; margin: 0; letter-spacing: 2px;
        color: #1a1a1a; text-shadow: 1px 1px 0px rgba(255,255,255,0.5);
    }
    .logo-highlight { color: #b8860b; text-shadow: 1px 1px 0px rgba(255,255,255,0.8); }
    .logo-subtitle {
        font-family: 'Inter', sans-serif; color: #555; font-size: 16px; font-weight: 500;
        margin-top: 15px; text-transform: uppercase; letter-spacing: 1px;
    }
    .logo-sub-detail { font-size: 14px; color: #777; margin-top: 5px; font-style: italic; }

    /* --- TICKERS DO TOPO (Mini Cards) --- */
    .top-ticker-box {
        background-color: rgba(20, 20, 20, 0.6);
        border-radius: 12px;
        padding: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        text-align: left;
        backdrop-filter: blur(5px);
    }
    .top-ticker-name { font-size: 11px; color: #888; font-weight: 600; text-transform: uppercase; }
    .top-ticker-price { font-size: 18px; color: #fff; font-weight: 700; font-family: 'Inter', sans-serif; margin: 5px 0; }
    .top-ticker-change { font-size: 12px; font-weight: 600; }
    .up { color: #00ff88; }
    .down { color: #ff3b30; }

    /* --- CARDS DASHBOARD (O Corpo Tecnológico) --- */
    .dash-card {
        background-color: #0e0e0e; /* Cinza Quase Preto */
        border: 1px solid #1f1f1f;
        border-radius: 16px;
        padding: 24px;
        height: 100%;
        transition: transform 0.2s;
    }
    .dash-card:hover { border-color: #d4af37; transform: translateY(-2px); }

    /* --- CONTROLES --- */
    .control-label {
        font-family: 'Playfair Display', serif; color: #d4af37; font-size: 18px; margin-bottom: 10px;
    }
    
    /* --- SENTIMENT CARD --- */
    .ai-badge {
        background-color: rgba(212, 175, 55, 0.1); color: #d4af37; padding: 5px 10px; border-radius: 20px;
        font-size: 11px; font-weight: 600; text-transform: uppercase; display: inline-block; margin-bottom: 10px;
    }
    .sentiment-score { font-size: 36px; font-weight: 700; color: #ffffff; font-family: 'Playfair Display', serif; }

    /* --- NOTÍCIAS --- */
    .news-item { padding: 15px 0; border-bottom: 1px solid #1f1f1f; }
    .news-title { color: #e0e0e0; font-size: 14px; font-weight: 500; text-decoration: none; display: block; margin-bottom: 5px; }
    .news-title:hover { color: #d4af37; }
    .news-meta { font-size: 11px; color: #555; }
    .tag-high { background: rgba(212, 175, 55, 0.2); color: #d4af37; padding: 2px 6px; border-radius: 4px; font-size: 10px; }

    /* --- AÇÕES EM DESTAQUE (Rodapé) --- */
    .highlight-card {
        background: #0e0e0e; border: 1px solid #1f1f1f; padding: 15px; border-radius: 12px; text-align: center;
    }
    .stockai-header { font-family: 'Playfair Display', serif; font-size: 24px; color: #fff; margin-bottom: 15px; }
    
    /* SIDEBAR & INPUTS */
    [data-testid="stSidebar"] { background-color: #0a0a0a; border-right: 1px solid #222; }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2 { color: #d4af37 !important; }
    .stSelectbox > div > div { background-color: #161616 !important; border: 1px solid #333; color: white !important; }
    .stSlider > div > div > div > div { background-color: #d4af37 !important; }
    
    @keyframes shine { 100% { left: 125%; } }

</style>
""", unsafe_allow_html=True)

# --- 3. DADOS & FUNÇÕES ---
ASSET_DB = {
    "Apple Inc.": "AAPL", "Microsoft": "MSFT", "NVIDIA": "NVDA", "Tesla": "TSLA",
    "Amazon": "AMZN", "Google": "GOOGL", "Meta": "META", "Bitcoin": "BTC-USD",
    "Ibovespa": "^BVSP", "Petrobras": "PETR4.SA", "Vale": "VALE3.SA", "Itaú": "ITUB4.SA",
    "Ambev": "ABEV3.SA", "Nubank": "NU", "Weg": "WEGE3.SA"
}

@st.cache_data(ttl=300)
def get_live_data(tickers):
    try:
        data = yf.download(tickers, period="5d", interval="1d", progress=False)['Close']
        return data
    except: return None

@st.cache_data(ttl=3600)
def get_asset_history(ticker, period):
    try:
        data = yf.Ticker(ticker)
        interval = "1m" if period == "1d" else "15m" if period == "5d" else "1d"
        if period == "max": interval = "1wk"
        hist = data.history(period=period, interval=interval)
        return hist
    except: return None

@st.cache_data(ttl=3600)
def get_news(term):
    try:
        googlenews = GoogleNews(period='3d', lang='en') 
        googlenews.search(f"{term} finance")
        return googlenews.result()
    except: return []

# --- 4. LAYOUT DA PÁGINA ---

# === HEADER BOLSAVALORIAS (RESTAURADO) ===
st.markdown("""
<div class="logo-box">
    <div class="logo-text">
        BolsaValor<span class="logo-highlight">IAS</span>
    </div>
    <div class="logo-subtitle">
        — Inteligência Financeira de Alta Precisão —
    </div>
    <div class="logo-sub-detail">
        "Uma análise rigorosa. Sempre trabalhando incansavelmente para entregar o melhor para você."
    </div>
</div>
""", unsafe_allow_html=True)
# ==========================================

# TOP SUMMARY (MERCADOS GLOBAIS)
top_tickers = ["^GSPC", "^IXIC", "^DJI", "BTC-USD", "BRL=X"]
top_names = {"^GSPC": "S&P 500", "^IXIC": "NASDAQ", "^DJI": "DOW JONES", "BTC-USD": "BITCOIN", "BRL=X": "DÓLAR"}
top_data = get_live_data(top_tickers)

if top_data is not None and not top_data.empty:
    cols = st.columns(5)
    for i, ticker in enumerate(top_tickers):
        with cols[i]:
            try:
                curr = top_data[ticker].iloc[-1]
                prev = top_data[ticker].iloc[-2]
                chg = ((curr - prev)/prev)*100
                color_class = "up" if chg >= 0 else "down"
                sign = "+" if chg >= 0 else ""
                
                st.markdown(f"""
                <div class="top-ticker-box">
                    <div class="top-ticker-name">{top_names[ticker]}</div>
                    <div class="top-ticker-price">{curr:,.2f}</div>
                    <div class="top-ticker-change {color_class}">{sign}{chg:.2f}%</div>
                </div>
                """, unsafe_allow_html=True)
            except: pass

st.markdown("<br>", unsafe_allow_html=True)

# --- GRID PRINCIPAL (Controles, Gráfico, IA) ---
col_left, col_mid, col_right = st.columns([1, 2.5, 1.2])

with col_left:
    st.markdown("""<div class="dash-card">""", unsafe_allow_html=True)
    st.markdown('<div class="control-label">Ativo</div>', unsafe_allow_html=True)
    selected_name = st.selectbox("", options=list(ASSET_DB.keys()), label_visibility="collapsed")
    ticker = ASSET_DB[selected_name]
    
    st.markdown('<br><div class="control-label">Horizonte</div>', unsafe_allow_html=True)
    time_map = {"1 Dia": "1d", "5 Dias": "5d", "1 Mês": "1mo", "6 Meses": "6mo", "1 Ano": "1y", "5 Anos": "5y"}
    time_sel = st.select_slider("", options=list(time_map.keys()), value="1 Ano")
    period = time_map[time_sel]
    
    st.markdown("<br><hr style='border-color:#333'><br>", unsafe_allow_html=True)
    
    info_hist = get_asset_history(ticker, "5d")
    if info_hist is not None:
        curr = info_hist['Close'].iloc[-1]
        prev = info_hist['Close'].iloc[-2]
        delta = curr - prev
        pct = (delta/prev)*100
        color = "#00ff88" if delta >= 0 else "#ff3b30"
        st.markdown(f"""
            <div style="font-family: 'Playfair Display'; font-size: 32px; color: #fff;">{ticker}</div>
            <div style="font-size: 24px; color: {color}; font-weight: bold;">{curr:,.2f}</div>
            <div style="font-size: 14px; color: {color};">{delta:+.2f} ({pct:+.2f}%)</div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

with col_mid:
    st.markdown("""<div class="dash-card">""", unsafe_allow_html=True)
    
    history = get_asset_history(ticker, period)
    if history is not None:
        fig = go.Figure()
        line_color = '#00ff88' if history['Close'].iloc[-1] >= history['Close'].iloc[0] else '#ff3b30'
        fig.add_trace(go.Scatter(
            x=history.index, y=history['Close'], mode='lines', fill='tozeroy',
            line=dict(color=line_color, width=2), name=ticker
        ))
        fig.update_layout(
            template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=0, r=0, t=20, b=0), height=450,
            xaxis=dict(showgrid=False, zeroline=False), yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', zeroline=False)
        )
        st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col_right:
    st.markdown("""<div class="dash-card">""", unsafe_allow_html=True)
    
    news = get_news(selected_name)
    sentiment_score = 0
    if news:
        blob = [TextBlob(n['title']) for n in news[:5]]
        sentiment_score = sum([b.sentiment.polarity for b in blob]) / len(blob)
    
    sent_label = "ALTA" if sentiment_score > 0 else "BAIXA"
    sent_color = "#00ff88" if sentiment_score > 0 else "#ff3b30"
    
    st.markdown(f"""
        <div class="ai-badge">⚡ Análise IA</div>
        <div style="font-size: 12px; color: #888;">Sentimento: {ticker}</div>
        <div class="sentiment-score" style="color: {sent_color}">{sent_label}</div>
        <div style="height: 4px; width: 100%; background: #333; margin-top: 10px; border-radius: 2px;">
            <div style="height: 100%; width: {min(abs(sentiment_score)*100 + 50, 100)}%; background: {sent_color}; border-radius: 2px;"></div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br><hr style='border-color:#333'><br>", unsafe_allow_html=True)
    st.markdown('<div style="font-family:Playfair Display; font-weight:700; color:#fff; margin-bottom:15px;">Notícias</div>', unsafe_allow_html=True)
    
    if news:
        for i, n in enumerate(news[:3]):
            st.markdown(f"""
            <div class="news-item">
                <a href="{n['link']}" target="_blank" class="news-title">{n['title']}</a>
                <span class="news-meta">{n.get('date', 'Hoje')} • Google News</span>
            </div>
            """, unsafe_allow_html=True)
    else: st.write("Sem notícias.")
    st.markdown("</div>", unsafe_allow_html=True)

# --- AÇÕES EM DESTAQUE ---
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="stockai-header">Ações em Destaque</div>', unsafe_allow_html=True)

destaque_tickers = ["AAPL", "GOOGL", "MSFT", "NVDA", "AMZN", "TSLA"]
destaque_data = get_live_data(destaque_tickers)

if destaque_data is not None:
    cols_d = st.columns(6)
    for i, t in enumerate(destaque_tickers):
        with cols_d[i]:
            try:
                curr = destaque_data[t].iloc[-1]
                prev = destaque_data[t].iloc[-2]
                pct = ((curr-prev)/prev)*100
                color = "#00ff88" if pct >= 0 else "#ff3b30"
                
                st.markdown(f"""
                <div class="highlight-card">
                    <div style="font-weight:700; color:#fff;">{t}</div>
                    <div style="margin-top:10px; font-size:16px; color:#fff; font-weight:600;">{curr:.2f}</div>
                    <div style="font-size:12px; color:{color};">{pct:+.2f}%</div>
                </div>
                """, unsafe_allow_html=True)
            except: pass

# --- FOOTER ---
st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style="text-align: center; margin-top: 10px;">
    <p style="color: #d4af37; font-size: 1.1em; font-family: 'Cinzel', serif;">Edson Junior</p>
    <div style="display: flex; justify-content: center; gap: 15px;">
        <a href="https://www.linkedin.com/" target="_blank"><img src="https://img.icons8.com/color/48/000000/linkedin.png" width="28"></a>
        <a href="https://github.com/EdsonRicard00" target="_blank"><img src="https://img.icons8.com/fluency/48/000000/github.png" width="28"></a>
    </div>
</div>
""", unsafe_allow_html=True)