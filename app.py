import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from textblob import TextBlob
from GoogleNews import GoogleNews
import pandas as pd

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(layout="wide", page_title="BolsaValorIAS", page_icon="🏛️")

# --- 2. CSS "ROYAL DARK & METALS" ---
st.markdown("""
<style>
    /* IMPORTANDO FONTES DE LUXO */
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&family=Inter:wght@300;400;600&family=Playfair+Display:wght@700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* FUNDO PRETO PROFUNDO */
    .stApp {
        background-color: #000000;
        background-image: radial-gradient(circle at 50% 0%, #1a1a1a 0%, #000000 85%);
        color: #e0e0e0;
    }

    /* --- HEADER LUXUOSO --- */
    .logo-box {
        background: linear-gradient(120deg, #ffffff 0%, #f0f0f0 30%, #e6e6e6 50%, #fbf5b7 85%, #d4af37 100%);
        border: 2px solid #ffffff;
        border-radius: 20px;
        padding: 40px 20px;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 0 30px rgba(212, 175, 55, 0.3), inset 0 0 20px rgba(255, 255, 255, 0.8);
        position: relative;
        overflow: hidden;
    }
    
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

    /* --- NOVO: MARKET TICKER CARDS (Resumo de Mercado) --- */
    .market-card {
        background-color: rgba(30, 30, 30, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        backdrop-filter: blur(5px);
        transition: transform 0.2s;
    }
    .market-card:hover { transform: scale(1.05); border-color: #d4af37; }
    .market-symbol { font-size: 14px; color: #888; font-weight: 600; letter-spacing: 1px; }
    .market-price { font-size: 18px; color: #fff; font-weight: 700; margin: 5px 0; }
    .market-change-up { color: #00ff88; font-size: 13px; font-weight: 600; }
    .market-change-down { color: #ff4b4b; font-size: 13px; font-weight: 600; }

    /* --- CARDS METÁLICOS --- */
    .silver-card {
        background: linear-gradient(135deg, #e0e0e0 0%, #ffffff 50%, #a0a0a0 100%);
        border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 15px; padding: 25px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5), inset 0 0 10px rgba(255,255,255,0.8);
        color: #1a1a1a !important; transition: transform 0.3s ease;
    }
    .silver-card:hover { transform: translateY(-5px); box-shadow: 0 0 20px rgba(255, 255, 255, 0.4); }
    
    .gold-card {
        background: linear-gradient(135deg, #bf953f 0%, #fcf6ba 40%, #b38728 80%, #fbf5b7 100%);
        border: 1px solid rgba(255, 215, 0, 0.3); border-radius: 15px; padding: 25px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5), inset 0 0 10px rgba(255,215,0,0.5);
        color: #3b2a05 !important; text-align: center; height: 100%; display: flex; flex-direction: column; justify-content: center;
        transition: transform 0.3s ease;
    }
    .gold-card:hover { transform: translateY(-5px); box-shadow: 0 0 25px rgba(255, 215, 0, 0.6); }

    /* SIDEBAR & INPUTS */
    [data-testid="stSidebar"] { background-color: #0a0a0a; border-right: 1px solid #222; }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { color: #d4af37 !important; }
    .stSelectbox > div > div { background-color: #111 !important; color: white !important; border: 1px solid #333; }
    .stSlider > div > div > div > div { background-color: #d4af37 !important; }
    
    @keyframes shine { 100% { left: 125%; } }
    
    .cta-section {
        background: linear-gradient(to bottom, #111, #000);
        padding: 60px 20px; margin-top: 60px; border-radius: 30px; 
        text-align: center; border: 1px solid #222;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. DADOS ---
ASSET_DB = {
    "Apple Inc.": "AAPL", "Microsoft": "MSFT", "NVIDIA": "NVDA", "Alphabet": "GOOGL",
    "Amazon": "AMZN", "Tesla": "TSLA", "Meta": "META", "Bitcoin": "BTC-USD",
    "Gold": "GC=F", "Petrobras": "PETR4.SA", "Vale": "VALE3.SA", "Itaú": "ITUB4.SA",
    "Ambev": "ABEV3.SA", "Nubank": "NU", "Weg": "WEGE3.SA"
}

@st.cache_data(ttl=3600)
def get_stock_data(ticker, period_code):
    try:
        data = yf.Ticker(ticker)
        interval = "1wk" if period_code == "max" else "1d"
        history = data.history(period=period_code, interval=interval)
        return history
    except: return None

@st.cache_data(ttl=3600)
def get_real_news(term):
    try:
        googlenews = GoogleNews(period='7d', lang='en') 
        googlenews.search(f"{term} finance")
        return googlenews.result()
    except: return []

# --- NOVA FUNÇÃO: RESUMO DE MERCADO ---
def render_market_summary():
    # Lista de ativos para o radar (Ticker Yahoo : Nome Exibição)
    summary_tickers = {
        "^BVSP": "IBOVESPA",
        "BRL=X": "USD/BRL",
        "EURBRL=X": "EUR/BRL",
        "^GSPC": "S&P 500",
        "BTC-USD": "BITCOIN"
    }
    
    cols = st.columns(len(summary_tickers))
    
    for i, (ticker, name) in enumerate(summary_tickers.items()):
        try:
            data = yf.Ticker(ticker).history(period="5d")
            if not data.empty:
                current = data['Close'].iloc[-1]
                prev = data['Close'].iloc[-2]
                change = ((current - prev) / prev) * 100
                
                color_class = "market-change-up" if change >= 0 else "market-change-down"
                arrow = "▲" if change >= 0 else "▼"
                
                with cols[i]:
                    st.markdown(f"""
                    <div class="market-card">
                        <div class="market-symbol">{name}</div>
                        <div class="market-price">{current:,.2f}</div>
                        <div class="{color_class}">{arrow} {change:.2f}%</div>
                    </div>
                    """, unsafe_allow_html=True)
        except:
            pass
# --------------------------------------

def analyze_sentiment(news_list):
    if not news_list: return 0, "Analisando..."
    polarity_sum, count = 0, 0
    for n in news_list[:5]:
        text = n.get('title', '')
        if text:
            analysis = TextBlob(text)
            polarity_sum += analysis.sentiment.polarity
            count += 1
    avg = polarity_sum / count if count > 0 else 0
    if avg > 0.1: return avg, "Tendência de Alta"
    elif avg < -0.1: return avg, "Tendência de Baixa"
    return avg, "Estabilidade"

# --- 4. LAYOUT PRINCIPAL ---

# HEADER LUXUOSO
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

# === INSERINDO O RADAR DE MERCADO ===
st.markdown("<h5 style='color:#888; margin-bottom:10px;'>📡 Radar de Mercado (Tempo Real)</h5>", unsafe_allow_html=True)
render_market_summary()
st.markdown("<br><hr style='border-color: #333;'><br>", unsafe_allow_html=True)
# ====================================

# VALUE PROPOSITION
col_v1, col_v2, col_v3 = st.columns(3)
with col_v1:
    st.markdown("""
    <div class="silver-card" style="text-align: center;">
        <span style="font-size: 30px;">⚡</span>
        <div style="font-weight: 600; margin: 10px 0;">Velocidade</div>
        <div style="font-size: 14px; opacity: 0.8;">Processamento Instantâneo</div>
    </div>
    """, unsafe_allow_html=True)
with col_v2:
    st.markdown("""
    <div class="silver-card" style="text-align: center;">
        <span style="font-size: 30px;">🎯</span>
        <div style="font-weight: 600; margin: 10px 0;">Rigor</div>
        <div style="font-size: 14px; opacity: 0.8;">Zero Ruído</div>
    </div>
    """, unsafe_allow_html=True)
with col_v3:
    st.markdown("""
    <div class="silver-card" style="text-align: center;">
        <span style="font-size: 30px;">💎</span>
        <div style="font-weight: 600; margin: 10px 0;">Elite</div>
        <div style="font-size: 14px; opacity: 0.8;">Tecnologia Premium</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# SIDEBAR
st.sidebar.markdown("### Seleção de Ativos")
selected_asset_name = st.sidebar.selectbox("Ativo", options=list(ASSET_DB.keys()))
ticker_input = ASSET_DB[selected_asset_name]
st.sidebar.markdown("<br>", unsafe_allow_html=True)
st.sidebar.markdown("### Horizonte")
time_option = st.sidebar.select_slider("", options=["1M", "6M", "1A", "5A", "Max"], value="1A")
time_map = {"1M": "1mo", "6M": "6mo", "1A": "1y", "5A": "5y", "Max": "max"}
st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style="text-align: center; margin-top: 10px;">
    <p style="color: #d4af37; font-size: 1.1em; font-family: 'Cinzel', serif;">Edson Junior</p>
    <div style="display: flex; justify-content: center; gap: 15px;">
        <a href="https://www.linkedin.com/" target="_blank"><img src="https://img.icons8.com/color/48/000000/linkedin.png" width="28"></a>
        <a href="https://github.com/EdsonRicard00" target="_blank"><img src="https://img.icons8.com/fluency/48/000000/github.png" width="28"></a>
    </div>
    <p style="color: #666; font-size: 0.7em; margin-top: 10px;">CEO & Developer</p>
</div>
""", unsafe_allow_html=True)

# APP LOGIC
if ticker_input:
    period_yf = time_map[time_option]
    clean_name = selected_asset_name
    history = get_stock_data(ticker_input, period_yf)
    news = get_real_news(clean_name)

    if history is not None and not history.empty:
        st.markdown(f"<h3 style='text-align:center; font-weight:300; margin-bottom:30px; color:#fff;'>Análise: <span style='color:#d4af37; font-weight:600;'>{clean_name}</span></h3>", unsafe_allow_html=True)
        
        current_price = history['Close'].iloc[-1]
        delta = current_price - history['Close'].iloc[-2]
        currency = "R$" if ".SA" in ticker_input else "US$"
        
        c1, c2 = st.columns([1.5, 1])
        
        with c1:
            st.metric("Cotação Atual", f"{currency} {current_price:.2f}", f"{delta:.2f}")
        
        with c2:
            score, sentiment_text = analyze_sentiment(news)
            color_sent = "#214e2b" if score > 0.05 else "#7a221e" if score < -0.05 else "#4a3b10"
            
            st.markdown(f"""
            <div class="gold-card">
                <div style="font-size: 12px; text-transform: uppercase; letter-spacing: 2px; opacity: 0.8;">Veredito da IA</div>
                <div style="font-size: 24px; font-weight: 800; color: {color_sent}; margin-top: 5px;">{sentiment_text}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1, row_heights=[0.75, 0.25])
        
        fig.add_trace(go.Candlestick(x=history.index, open=history['Open'], high=history['High'], low=history['Low'], close=history['Close'], name="Preço", increasing_line_color='#00ff88', decreasing_line_color='#ff4b4b'), row=1, col=1)
        fig.add_trace(go.Bar(x=history.index, y=history['Volume'], name="Volume", marker_color='#ffffff', opacity=0.3), row=2, col=1)
        
        fig.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)', 
            height=550, 
            xaxis_rangeslider_visible=False, 
            showlegend=False, 
            margin=dict(l=20, r=20, t=20, b=20),
            font=dict(color="#e0e0e0")
        )
        fig.update_xaxes(gridcolor='rgba(255,255,255,0.1)')
        fig.update_yaxes(gridcolor='rgba(255,255,255,0.1)')
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("<h4 style='font-weight: 600; color: #fff; margin-bottom: 20px;'>Radar de Notícias</h4>", unsafe_allow_html=True)
        
        if news:
            for n in news[:3]:
                st.markdown(f"""
                <div class="silver-card" style="padding: 15px; margin-bottom: 15px; display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <a href="{n['link']}" target="_blank" style="text-decoration: none; color: #1a1a1a; font-weight: 700; font-size: 16px;">{n['title']}</a>
                        <div style="font-size: 12px; color: #444; margin-top: 5px;">{n.get('date', 'Agora')} • BolsaValorIAS Feed</div>
                    </div>
                    <span style="font-size: 18px; color: #888;">➤</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.write("Sem dados.")

# CTA FINAL
st.markdown("""
<div class="cta-section">
    <div style="font-size: 30px; font-weight: 600; color: #fff; margin-bottom: 15px;">BolsaValorIAS.</div>
    <div style="color: #888; font-size: 16px;">O futuro dos seus investimentos começa aqui.</div>
</div>
""", unsafe_allow_html=True)