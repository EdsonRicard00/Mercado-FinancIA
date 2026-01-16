import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from textblob import TextBlob
from GoogleNews import GoogleNews
import pandas as pd
import numpy as np

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(layout="wide", page_title="BolsaValorIAS", page_icon="🏛️")

# --- 2. CSS PREMIUM (HOVER DOURADO & FOOTER CEO) ---
st.markdown("""
<style>
    /* IMPORTANDO FONTES */
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&family=Inter:wght@300;400;600&family=Playfair+Display:wght@400;600;700&display=swap');

    /* RESET GERAL DARK */
    .stApp {
        background-color: #050505;
        background-image: radial-gradient(circle at 50% 0%, #1a1a1a 0%, #000000 80%);
        color: #e0e0e0;
        font-family: 'Inter', sans-serif;
    }

    /* --- O HEADER BOLSAVALORIAS --- */
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
    .logo-box::before {
        content: ''; position: absolute; top: 0; left: -50%; width: 100%; height: 100%;
        background: linear-gradient(to right, transparent, rgba(255,255,255,0.8), transparent);
        transform: skewX(-25deg); animation: shine 6s infinite;
    }
    .logo-text { font-family: 'Cinzel', serif; font-size: 65px; font-weight: 700; margin: 0; letter-spacing: 2px; color: #1a1a1a; text-shadow: 1px 1px 0px rgba(255,255,255,0.5); }
    .logo-highlight { color: #b8860b; text-shadow: 1px 1px 0px rgba(255,255,255,0.8); }
    .logo-subtitle { font-family: 'Inter', sans-serif; color: #555; font-size: 16px; font-weight: 500; margin-top: 15px; text-transform: uppercase; letter-spacing: 1px; }

    /* --- INTERATIVIDADE DOURADA (HOVER EFFECT) --- */
    /* Quando passar o mouse, a caixa brilha em dourado */
    .dash-card:hover, .top-ticker-box:hover, .highlight-card:hover, .news-item:hover {
        border-color: #d4af37 !important;
        box-shadow: 0 0 20px rgba(212, 175, 55, 0.3) !important;
        transform: translateY(-5px);
        background-color: rgba(20, 20, 20, 0.9);
        transition: all 0.3s ease;
    }

    /* --- TICKERS DO TOPO --- */
    .top-ticker-box {
        background-color: rgba(20, 20, 20, 0.6);
        border-radius: 12px;
        padding: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        text-align: left;
        backdrop-filter: blur(5px);
        transition: transform 0.3s ease;
    }
    .top-ticker-name { font-size: 11px; color: #888; font-weight: 600; text-transform: uppercase; }
    .top-ticker-price { font-size: 18px; color: #fff; font-weight: 700; font-family: 'Inter', sans-serif; margin: 5px 0; }
    .top-ticker-change { font-size: 12px; font-weight: 600; }
    .up { color: #00ff88; }
    .down { color: #ff3b30; }

    /* --- CARDS DASHBOARD --- */
    .dash-card {
        background-color: #0e0e0e; border: 1px solid #1f1f1f; border-radius: 16px; padding: 24px;
        height: 100%; transition: all 0.3s ease;
    }

    /* --- CONTROLES --- */
    .control-label { font-family: 'Playfair Display', serif; color: #d4af37; font-size: 18px; margin-bottom: 10px; }
    
    /* --- SENTIMENT CARD --- */
    .ai-badge {
        background-color: rgba(212, 175, 55, 0.1); color: #d4af37; padding: 5px 10px; border-radius: 20px;
        font-size: 11px; font-weight: 600; text-transform: uppercase; display: inline-block; margin-bottom: 10px;
    }
    .sentiment-score { font-size: 36px; font-weight: 700; color: #ffffff; font-family: 'Playfair Display', serif; }

    /* --- NOTÍCIAS --- */
    .news-item { padding: 15px 10px; border-bottom: 1px solid #1f1f1f; border-radius: 8px; transition: all 0.3s ease; }
    .news-title { color: #e0e0e0; font-size: 14px; font-weight: 500; text-decoration: none; display: block; margin-bottom: 5px; }
    .news-meta { font-size: 11px; color: #555; }
    
    /* --- AÇÕES EM DESTAQUE --- */
    .highlight-card { background: #0e0e0e; border: 1px solid #1f1f1f; padding: 15px; border-radius: 12px; text-align: center; transition: all 0.3s ease; }
    .stockai-header { font-family: 'Playfair Display', serif; font-size: 24px; color: #fff; margin-bottom: 15px; }
    
    /* --- FOOTER (RODAPÉ DO CEO) --- */
    .ceo-footer {
        margin-top: 80px;
        padding: 40px;
        text-align: center;
        border-top: 1px solid #222;
        background: linear-gradient(to bottom, #050505, #111);
    }
    .ceo-text {
        font-family: 'Cinzel', serif;
        color: #d4af37;
        font-size: 18px;
        letter-spacing: 2px;
        text-transform: uppercase;
    }
    .ceo-sub {
        font-family: 'Inter', sans-serif;
        color: #666;
        font-size: 12px;
        margin-top: 10px;
    }

    /* SIDEBAR & INPUTS */
    [data-testid="stSidebar"] { background-color: #0a0a0a; border-right: 1px solid #222; }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2 { color: #d4af37 !important; }
    .stSelectbox > div > div { background-color: #161616 !important; border: 1px solid #333; color: white !important; }
    .stSlider > div > div > div > div { background-color: #d4af37 !important; }
    
    @keyframes shine { 100% { left: 125%; } }
</style>
""", unsafe_allow_html=True)

# --- 3. BANCO DE DADOS GIGANTE (100+ ATIVOS) ---
ASSET_DB = ASSET_DB = {
    # --- 🇺🇸 BIG TECH & US GIANTS ---
    "🇺🇸 Apple (AAPL)": "AAPL",
    "🇺🇸 Microsoft (MSFT)": "MSFT",
    "🇺🇸 NVIDIA (NVDA)": "NVDA",
    "🇺🇸 Amazon (AMZN)": "AMZN",
    "🇺🇸 Alphabet/Google (GOOGL)": "GOOGL",
    "🇺🇸 Meta/Facebook (META)": "META",
    "🇺🇸 Tesla (TSLA)": "TSLA",
    "🇺🇸 Netflix (NFLX)": "NFLX",
    "🇺🇸 AMD (AMD)": "AMD",
    "🇺🇸 Intel (INTC)": "INTC",
    "🇺🇸 Broadcom (AVGO)": "AVGO",
    "🇺🇸 Qualcomm (QCOM)": "QCOM",
    "🇺🇸 Adobe (ADBE)": "ADBE",
    "🇺🇸 Salesforce (CRM)": "CRM",
    "🇺🇸 Oracle (ORCL)": "ORCL",
    "🇺🇸 Uber (UBER)": "UBER",
    "🇺🇸 Airbnb (ABNB)": "ABNB",
    "🇺🇸 Disney (DIS)": "DIS",
    "🇺🇸 Coca-Cola (KO)": "KO",
    "🇺🇸 PepsiCo (PEP)": "PEP",
    "🇺🇸 McDonald's (MCD)": "MCD",
    "🇺🇸 Starbucks (SBUX)": "SBUX",
    "🇺🇸 Nike (NKE)": "NKE",
    "🇺🇸 Walmart (WMT)": "WMT",
    "🇺🇸 Costco (COST)": "COST",
    "🇺🇸 Visa (V)": "V",
    "🇺🇸 Mastercard (MA)": "MA",
    "🇺🇸 JPMorgan (JPM)": "JPM",
    "🇺🇸 Bank of America (BAC)": "BAC",
    "🇺🇸 Goldman Sachs (GS)": "GS",
    "🇺🇸 Exxon Mobil (XOM)": "XOM",
    "🇺🇸 Chevron (CVX)": "CVX",
    "🇺🇸 Pfizer (PFE)": "PFE",
    "🇺🇸 Johnson & Johnson (JNJ)": "JNJ",
    "🇺🇸 Eli Lilly (LLY)": "LLY",
    "🇺🇸 Berkshire Hathaway (BRK-B)": "BRK-B",

    # --- 🇧🇷 BRASIL (B3 IBOVESPA) ---
    "🇧🇷 Petrobras PN (PETR4)": "PETR4.SA",
    "🇧🇷 Petrobras ON (PETR3)": "PETR3.SA",
    "🇧🇷 Vale (VALE3)": "VALE3.SA",
    "🇧🇷 Itaú Unibanco (ITUB4)": "ITUB4.SA",
    "🇧🇷 Bradesco PN (BBDC4)": "BBDC4.SA",
    "🇧🇷 Bradesco ON (BBDC3)": "BBDC3.SA",
    "🇧🇷 Banco do Brasil (BBAS3)": "BBAS3.SA",
    "🇧🇷 Santander (SANB11)": "SANB11.SA",
    "🇧🇷 BTG Pactual (BPAC11)": "BPAC11.SA",
    "🇧🇷 B3 (B3SA3)": "B3SA3.SA",
    "🇧🇷 Ambev (ABEV3)": "ABEV3.SA",
    "🇧🇷 Weg (WEGE3)": "WEGE3.SA",
    "🇧🇷 Suzano (SUZB3)": "SUZB3.SA",
    "🇧🇷 Gerdau (GGBR4)": "GGBR4.SA",
    "🇧🇷 CSN (CSNA3)": "CSNA3.SA",
    "🇧🇷 Usiminas (USIM5)": "USIM5.SA",
    "🇧🇷 JBS (JBSS3)": "JBSS3.SA",
    "🇧🇷 Marfrig (MRFG3)": "MRFG3.SA",
    "🇧🇷 BRF (BRFS3)": "BRFS3.SA",
    "🇧🇷 Eletrobras (ELET3)": "ELET3.SA",
    "🇧🇷 Eletrobras PN (ELET6)": "ELET6.SA",
    "🇧🇷 Copel (CPLE6)": "CPLE6.SA",
    "🇧🇷 Cemig (CMIG4)": "CMIG4.SA",
    "🇧🇷 Engie (ENGI11)": "ENGI11.SA",
    "🇧🇷 Equatorial (EQTL3)": "EQTL3.SA",
    "🇧🇷 Sabesp (SBSP3)": "SBSP3.SA",
    "🇧🇷 Prio (PRIO3)": "PRIO3.SA",
    "🇧🇷 Brava Energia (BRAV3)": "BRAV3.SA",
    "🇧🇷 Localiza (RENT3)": "RENT3.SA",
    "🇧🇷 Rumo (RAIL3)": "RAIL3.SA",
    "🇧🇷 Azul (AZUL4)": "AZUL4.SA",
    "🇧🇷 Embraer (EMBR3)": "EMBR3.SA",
    "🇧🇷 Magazine Luiza (MGLU3)": "MGLU3.SA",
    "🇧🇷 Lojas Renner (LREN3)": "LREN3.SA",
    "🇧🇷 Raia Drogasil (RADL3)": "RADL3.SA",
    "🇧🇷 Vibra (VBBR3)": "VBBR3.SA",
    "🇧🇷 Ultrapar (UGPA3)": "UGPA3.SA",
    "🇧🇷 Hapvida (HAPV3)": "HAPV3.SA",
    "🇧🇷 Rede D'Or (RDOR3)": "RDOR3.SA",
    "🇧🇷 Telefônica/Vivo (VIVT3)": "VIVT3.SA",
    "🇧🇷 TIM (TIMS3)": "TIMS3.SA",
    "🇧🇷 Totvs (TOTS3)": "TOTS3.SA",
    "🇧🇷 Nubank (ROXO34/NU)": "NU",
    "🇧🇷 XP Inc (XP)": "XP",

    # --- ₿ CRIPTO & MOEDAS ---
    "₿ Bitcoin (USD)": "BTC-USD",
    "₿ Ethereum (USD)": "ETH-USD",
    "₿ Solana (USD)": "SOL-USD",
    "💵 Dólar (USD/BRL)": "BRL=X",
    "💶 Euro (EUR/BRL)": "EURBRL=X",

    # --- 🌍 GLOBAL & COMMODITIES ---
    "🟡 Ouro (Gold Futures)": "GC=F",
    "⚪ Prata (Silver Futures)": "SI=F",
    "🛢️ Petróleo WTI": "CL=F",
    "🛢️ Petróleo Brent": "BZ=F",
    "🌏 TSMC (Taiwan)": "TSM",
    "🌏 Alibaba (China)": "BABA",
    "🌏 Tencent (China)": "TCEHY",
    "🌏 Samsung (Coreia)": "SSNLF",
    "🌏 Toyota (Japão)": "TM",
    "🌏 Sony (Japão)": "SONY",
    "🌏 Shell (UK)": "SHEL",
    "🌏 AstraZeneca (UK)": "AZN",
    "🌏 SAP (Alemanha)": "SAP",
    "🌏 ASML (Holanda)": "ASML",
    "🌏 LVMH (Louis Vuitton)": "LVMUY",
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
        # Lógica para 30 Anos e Max
        interval = "1d"
        if period in ["5y", "10y", "30y", "max"]: interval = "1wk" 
        
        hist = data.history(period=period, interval=interval)
        return hist
    except: return None

@st.cache_data(ttl=3600)
def get_news(term):
    try:
        googlenews = GoogleNews(period='3d', lang='en') 
        clean_term = term.split("(")[0].replace("🇺🇸", "").replace("🇧🇷", "").replace("₿", "").strip()
        googlenews.search(f"{clean_term} market news")
        return googlenews.result()
    except: return []

# --- 4. LAYOUT DA PÁGINA ---

# HEADER BOLSAVALORIAS
st.markdown("""
<div class="logo-box">
    <div class="logo-text">
        BolsaValor<span class="logo-highlight">IAS</span>
    </div>
    <div class="logo-subtitle">
        — Inteligência Financeira de Alta Precisão —
    </div>
</div>
""", unsafe_allow_html=True)

# TOP SUMMARY
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

# --- CORPO PRINCIPAL ---
col_left, col_mid, col_right = st.columns([1, 2.5, 1.2])

with col_left:
    st.markdown("""<div class="dash-card">""", unsafe_allow_html=True)
    st.markdown('<div class="control-label">Ativo</div>', unsafe_allow_html=True)
    selected_name = st.selectbox("", options=list(ASSET_DB.keys()), label_visibility="collapsed")
    ticker = ASSET_DB[selected_name]
    
    # --- NOVO HORIZONTE DE 30 ANOS ---
    st.markdown('<br><div class="control-label">Horizonte</div>', unsafe_allow_html=True)
    time_map = {
        "1 Dia": "1d", "5 Dias": "5d", "1 Mês": "1mo", "1 Ano": "1y", 
        "5 Anos": "5y", "10 Anos": "10y", "30 Anos": "30y"
    }
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
        currency = "R$" if ".SA" in ticker else "US$"
        
        st.markdown(f"""
            <div style="font-family: 'Playfair Display'; font-size: 28px; color: #fff; line-height: 1.2;">{selected_name.split('(')[0]}</div>
            <div style="font-size: 24px; color: {color}; font-weight: bold; margin-top: 10px;">{currency} {curr:,.2f}</div>
            <div style="font-size: 14px; color: {color};">{delta:+.2f} ({pct:+.2f}%)</div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col_mid:
    # --- SISTEMA DE ABAS (TABS) ---
    tab1, tab2, tab3 = st.tabs(["📊 Visão Geral", "📈 Tendência (Técnica)", "📋 Dados Históricos"])
    
    history = get_asset_history(ticker, period)
    
    with tab1: # ABA 1: GRÁFICO PADRÃO
        st.markdown("""<div class="dash-card">""", unsafe_allow_html=True)
        if history is not None:
            fig = go.Figure()
            line_color = '#00ff88' if history['Close'].iloc[-1] >= history['Close'].iloc[0] else '#ff3b30'
            fig.add_trace(go.Scatter(x=history.index, y=history['Close'], mode='lines', fill='tozeroy', line=dict(color=line_color, width=2), name=ticker))
            fig.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=0, t=20, b=0), height=450, xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)'))
            st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with tab2: # ABA 2: TENDÊNCIA (Média Móvel)
        st.markdown("""<div class="dash-card">""", unsafe_allow_html=True)
        if history is not None:
            # Calculando Média Móvel
            history['SMA'] = history['Close'].rolling(window=20).mean()
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(x=history.index, y=history['Close'], mode='lines', name='Preço', line=dict(color='#ffffff', width=1)))
            fig2.add_trace(go.Scatter(x=history.index, y=history['SMA'], mode='lines', name='Tendência (Média 20)', line=dict(color='#d4af37', width=2)))
            fig2.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=0, t=20, b=0), height=450, title="Análise de Tendência (Ouro = Média)", xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)'))
            st.plotly_chart(fig2, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with tab3: # ABA 3: DADOS
        st.markdown("""<div class="dash-card">""", unsafe_allow_html=True)
        if history is not None:
            st.dataframe(history[['Open', 'High', 'Low', 'Close', 'Volume']].sort_index(ascending=False), height=450, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)


with col_right:
    st.markdown("""<div class="dash-card">""", unsafe_allow_html=True)
    news = get_news(selected_name)
    sentiment_score = 0
    if news:
        blob = [TextBlob(n['title']) for n in news[:5]]
        sentiment_score = sum([b.sentiment.polarity for b in blob]) / len(blob)
    sent_label = "OTIMISTA" if sentiment_score > 0.05 else "PESSIMISTA" if sentiment_score < -0.05 else "NEUTRO"
    sent_color = "#00ff88" if sentiment_score > 0.05 else "#ff3b30" if sentiment_score < -0.05 else "#aaaaaa"
    
    st.markdown(f"""
        <div class="ai-badge">⚡ Análise IA</div>
        <div style="font-size: 12px; color: #888;">Sentimento Global</div>
        <div class="sentiment-score" style="color: {sent_color}; font-size: 28px;">{sent_label}</div>
        <div style="height: 4px; width: 100%; background: #333; margin-top: 10px; border-radius: 2px;">
            <div style="height: 100%; width: {min(abs(sentiment_score)*100 + 50, 100)}%; background: {sent_color}; border-radius: 2px;"></div>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("<br><hr style='border-color:#333'><br>", unsafe_allow_html=True)
    st.markdown('<div style="font-family:Playfair Display; font-weight:700; color:#fff; margin-bottom:15px;">Notícias</div>', unsafe_allow_html=True)
    if news:
        for n in news[:3]:
            st.markdown(f"""<div class="news-item"><a href="{n['link']}" target="_blank" class="news-title">{n['title']}</a><span class="news-meta">{n.get('date', 'News')}</span></div>""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- AÇÕES EM DESTAQUE ---
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="stockai-header">Ações em Destaque</div>', unsafe_allow_html=True)
destaque_tickers = ["AAPL", "PETR4.SA", "VALE3.SA", "MSFT", "NVDA", "BTC-USD"]
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
                name_clean = t.replace(".SA", "")
                st.markdown(f"""<div class="highlight-card"><div style="font-weight:700; color:#fff;">{name_clean}</div><div style="margin-top:10px; font-size:16px; color:#fff; font-weight:600;">{curr:.2f}</div><div style="font-size:12px; color:{color};">{pct:+.2f}%</div></div>""", unsafe_allow_html=True)
            except: pass

# --- FOOTER DO CEO (RODAPÉ) ---
st.markdown("""
<div class="ceo-footer">
    <div class="ceo-text">Desenvolvido por Edson</div>
    <div style="color: #666; font-size: 14px; margin: 5px 0;">&</div>
    <div class="ceo-text">CEO da BolsaValorIAS</div>
    <div class="ceo-sub">© 2026 Todos os direitos reservados. Inteligência Artificial Financeira.</div>
</div>
""", unsafe_allow_html=True)