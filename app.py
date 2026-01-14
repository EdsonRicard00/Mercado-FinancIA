import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from textblob import TextBlob
from GoogleNews import GoogleNews
import pandas as pd

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(layout="wide", page_title="Mercado-FinancIA | Luxury", page_icon="💎")

# --- 2. CSS "LUXURY METALS" ---
st.markdown("""
<style>
    /* FONTE E RESET */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: #1d1d1f;
    }
    .stApp { background-color: #fbfbfd; } /* Fundo claro para destacar os metais */

    /* --- NOVAS CLASSES: METAIS PRECIOSOS --- */

    /* ESTILO PRATA/PLATINA (Escovado) */
    .silver-card {
        /* Degradê diagonal suave para simular reflexo metálico */
        background: linear-gradient(135deg, #f0f2f5 0%, #ffffff 50%, #d9dfe6 100%);
        border: 1px solid rgba(255, 255, 255, 0.8);
        border-radius: 20px;
        padding: 25px;
        /* Sombra dupla: uma externa suave e uma interna branca para brilho nas bordas */
        box-shadow: 
            0 10px 30px rgba(0,0,0,0.08),
            inset 0 0 15px rgba(255,255,255,0.9);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .silver-card:hover {
        transform: translateY(-5px);
        box-shadow: 
            0 15px 40px rgba(0,0,0,0.12),
            inset 0 0 15px rgba(255,255,255,1);
    }

    /* ESTILO OURO (Dourado Rico) */
    .gold-card {
        /* Degradê quente de ouro */
        background: linear-gradient(135deg, #E6C35C 0%, #F7E49A 50%, #BD952D 100%);
        border: 1px solid rgba(255, 255, 255, 0.4);
        border-radius: 20px;
        padding: 25px;
        /* Sombra com tom dourado */
        box-shadow: 
            0 10px 30px rgba(189, 149, 45, 0.3),
            inset 0 0 20px rgba(255,255,255,0.4);
        color: #4a3b10 !important; /* Texto marrom escuro para contraste no ouro */
        transition: transform 0.3s ease;
        text-align: center;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .gold-card:hover {
        transform: translateY(-5px);
         box-shadow: 0 15px 40px rgba(189, 149, 45, 0.4);
    }


    /* --- APLICAÇÃO NOS ELEMENTOS NATIVOS --- */
    
    /* Hero Section */
    .hero-title {
        font-size: 56px; font-weight: 600; letter-spacing: -0.02em;
        background: linear-gradient(180deg, #1d1d1f 0%, #4a4a4a 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .hero-subtitle { font-size: 24px; color: #86868b; font-weight: 400; }

    /* Sidebar Minimalista */
    [data-testid="stSidebar"] { background-color: #f5f5f7; border-right: 1px solid rgba(0,0,0,0.05); }
    
    /* Métricas Nativas (Preço) -> Transformando em Prata */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #f0f2f5 0%, #ffffff 50%, #d9dfe6 100%);
        border-radius: 20px;
        padding: 25px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.08), inset 0 0 15px rgba(255,255,255,0.9);
        border: 1px solid rgba(255, 255, 255, 0.8);
    }
    div[data-testid="stMetricLabel"] { color: #6e6e73; }
    div[data-testid="stMetricValue"] { color: #1d1d1f; font-weight: 600; }

    /* Inputs */
    .stSelectbox > div > div { background-color: #ffffff !important; border-radius: 12px; }
    .stSlider > div > div > div > div { background-color: #BD952D !important; } /* Slider Dourado */

    /* CTA Final */
    .cta-section {
        /* Um toque sutil de prata no fundo final */
        background: linear-gradient(to bottom, #fbfbfd, #eaeaee);
        padding: 80px 20px; margin-top: 60px; border-radius: 30px; text-align: center;
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

# HERO
st.markdown("""
<div style="text-align: center; padding: 60px 20px;">
    <div class="hero-title">Inteligência Financeira.<br>Padrão Ouro.</div>
    <div class="hero-subtitle">Uma experiência desenhada para quem exige clareza absoluta e valor real.</div>
</div>
""", unsafe_allow_html=True)

# VALUE PROPOSITION (CAIXAS PRATEADAS)
col_v1, col_v2, col_v3 = st.columns(3)
with col_v1:
    st.markdown("""
    <div class="silver-card" style="text-align: center;">
        <span style="font-size: 30px;">⚡</span>
        <div style="font-weight: 600; margin: 10px 0; color: #1d1d1f;">Velocidade</div>
        <div style="color: #86868b; font-size: 14px;">Dados processados em tempo real.</div>
    </div>
    """, unsafe_allow_html=True)
with col_v2:
    st.markdown("""
    <div class="silver-card" style="text-align: center;">
        <span style="font-size: 30px;">🔒</span>
        <div style="font-weight: 600; margin: 10px 0; color: #1d1d1f;">Precisão</div>
        <div style="color: #86868b; font-size: 14px;">Algoritmos de IA refinados.</div>
    </div>
    """, unsafe_allow_html=True)
with col_v3:
    st.markdown("""
    <div class="silver-card" style="text-align: center;">
        <span style="font-size: 30px;">💎</span>
        <div style="font-weight: 600; margin: 10px 0; color: #1d1d1f;">Exclusividade</div>
        <div style="color: #86868b; font-size: 14px;">Design premium para decisões premium.</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# SIDEBAR
st.sidebar.markdown("### Seleção")
selected_asset_name = st.sidebar.selectbox("Ativo", options=list(ASSET_DB.keys()))
ticker_input = ASSET_DB[selected_asset_name]
st.sidebar.markdown("<br>", unsafe_allow_html=True)
st.sidebar.markdown("### Período")
time_option = st.sidebar.select_slider("", options=["1M", "6M", "1A", "5A", "Max"], value="1A")
time_map = {"1M": "1mo", "6M": "6mo", "1A": "1y", "5A": "5y", "Max": "max"}
st.sidebar.markdown("---")
st.sidebar.markdown("""<div style="color: #86868b; font-size: 12px; text-align: center;">Designed by Edson Junior<br><span style="opacity: 0.5;">Luxury FinTech Interface</span></div>""", unsafe_allow_html=True)

# APP LOGIC
if ticker_input:
    period_yf = time_map[time_option]
    clean_name = selected_asset_name
    history = get_stock_data(ticker_input, period_yf)
    news = get_real_news(clean_name)

    if history is not None and not history.empty:
        st.markdown(f"<h3 style='text-align:center; font-weight:600; margin-bottom:30px; color:#1d1d1f;'>Análise: {clean_name}</h3>", unsafe_allow_html=True)
        
        current_price = history['Close'].iloc[-1]
        delta = current_price - history['Close'].iloc[-2]
        currency = "R$" if ".SA" in ticker_input else "US$"
        
        c1, c2 = st.columns([1.5, 1])
        
        with c1:
            # O card de preço será PRATA (definido no CSS global do stMetric)
            st.metric("Cotação Atual", f"{currency} {current_price:.2f}", f"{delta:.2f}")
        
        with c2:
            score, sentiment_text = analyze_sentiment(news)
            # Cores de texto ajustadas para contrastar com o DOURADO
            color_sent = "#214e2b" if score > 0.05 else "#7a221e" if score < -0.05 else "#4a3b10"
            
            # O card de Sentimento será DOURADO
            st.markdown(f"""
            <div class="gold-card">
                <div style="font-size: 12px; text-transform: uppercase; letter-spacing: 1px; opacity: 0.8;">Sentimento IA</div>
                <div style="font-size: 24px; font-weight: 700; color: {color_sent}; margin-top: 5px;">{sentiment_text}</div>
            </div>
            """, unsafe_allow_html=True)

        # GRÁFICO
        st.markdown("<br>", unsafe_allow_html=True)
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1, row_heights=[0.75, 0.25])
        # Cores do gráfico ajustadas para tons mais ricos
        fig.add_trace(go.Candlestick(x=history.index, open=history['Open'], high=history['High'], low=history['Low'], close=history['Close'], name="Preço", increasing_line_color='#2ecc71', decreasing_line_color='#e74c3c', increasing_fillcolor='rgba(46, 204, 113, 0.1)', decreasing_fillcolor='rgba(231, 76, 60, 0.1)'), row=1, col=1)
        fig.add_trace(go.Bar(x=history.index, y=history['Volume'], name="Volume", marker_color='#bdc3c7', opacity=0.4), row=2, col=1)
        fig.update_layout(template='plotly_white', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=550, xaxis_rangeslider_visible=False, showlegend=False, margin=dict(l=20, r=20, t=20, b=20), hovermode="x unified")
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.05)')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.05)')
        st.plotly_chart(fig, use_container_width=True)

        # NOTÍCIAS (CAIXAS PRATEADAS EM LISTA)
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("<h4 style='font-weight: 600; color: #1d1d1f; margin-bottom: 20px;'>Contexto Global</h4>", unsafe_allow_html=True)
        
        if news:
            for n in news[:3]:
                # Cada notícia é um card prateado
                st.markdown(f"""
                <div class="silver-card" style="padding: 20px; margin-bottom: 15px; display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <a href="{n['link']}" target="_blank" style="text-decoration: none; color: #1d1d1f; font-weight: 600; font-size: 16px;">{n['title']}</a>
                        <div style="font-size: 13px; color: #86868b; margin-top: 5px;">{n.get('date', 'Recentemente')} • Fonte Confiável</div>
                    </div>
                    <span style="font-size: 20px; color: #d9dfe6;">↗</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("<div style='color:#86868b; font-style:italic;'>Sem ruído no momento.</div>", unsafe_allow_html=True)

    else:
        st.warning("Dados indisponíveis temporariamente.")

# CTA FINAL
st.markdown("""
<div class="cta-section">
    <div style="font-size: 32px; font-weight: 600; color: #1d1d1f; margin-bottom: 20px;">O padrão ouro da sua carteira.</div>
    <div style="color: #86868b; font-size: 18px;">Mercado-FinancIA Luxury.</div>
</div>
""", unsafe_allow_html=True)