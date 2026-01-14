import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from textblob import TextBlob
from GoogleNews import GoogleNews
import pandas as pd

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(layout="wide", page_title="Mercado-FinancIA", page_icon="🍏")

# --- 2. CSS "APPLE DESIGN SYSTEM" ---
st.markdown("""
<style>
    /* RESET E FONTE DO SISTEMA (San Francisco / Helvetica) */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        color: #1d1d1f; /* Cinza Apple Quase Preto */
    }

    /* FUNDO GERAL (Off-White Apple) */
    .stApp {
        background-color: #fbfbfd;
    }

    /* --- HERO SECTION --- */
    .hero-section {
        text-align: center;
        padding: 80px 20px 60px 20px;
        animation: fadeUp 1.2s cubic-bezier(0.16, 1, 0.3, 1);
    }
    
    .hero-title {
        font-size: 56px;
        font-weight: 600;
        letter-spacing: -0.02em;
        line-height: 1.1;
        background: linear-gradient(180deg, #1d1d1f 0%, #4a4a4a 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 20px;
    }

    .hero-subtitle {
        font-size: 24px;
        color: #86868b;
        font-weight: 400;
        max-width: 700px;
        margin: 0 auto 40px auto;
        line-height: 1.4;
    }

    /* --- FEATURE CARDS (Seção de Valor) --- */
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 30px;
        padding: 40px 0;
        max-width: 1000px;
        margin: 0 auto;
    }
    .feature-item {
        text-align: center;
    }
    .feature-icon { font-size: 30px; margin-bottom: 15px; display: block; }
    .feature-head { font-size: 19px; font-weight: 600; margin-bottom: 10px; color: #1d1d1f; }
    .feature-text { font-size: 15px; color: #86868b; line-height: 1.5; }

    /* --- SIDEBAR (Minimalista) --- */
    [data-testid="stSidebar"] {
        background-color: #f5f5f7; /* Cinza claro Apple */
        border-right: 1px solid rgba(0,0,0,0.05);
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2 {
        color: #1d1d1f !important;
        font-weight: 500;
        letter-spacing: -0.01em;
    }

    /* --- METRIC CARDS (Estilo Widget iOS) --- */
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        border-radius: 20px;
        padding: 25px;
        box-shadow: 0 4px 24px rgba(0,0,0,0.04); /* Sombra ultra suave */
        border: 1px solid rgba(0,0,0,0.02);
        transition: transform 0.4s cubic-bezier(0.16, 1, 0.3, 1);
    }
    div[data-testid="stMetric"]:hover {
        transform: scale(1.02);
        box-shadow: 0 10px 40px rgba(0,0,0,0.08);
    }
    div[data-testid="stMetricLabel"] { font-size: 14px; color: #86868b; font-weight: 500; }
    div[data-testid="stMetricValue"] { font-size: 32px; color: #1d1d1f; font-weight: 600; letter-spacing: -1px; }

    /* --- SENTIMENT CARD (Glass) --- */
    .sentiment-box {
        background: #ffffff;
        border-radius: 20px;
        padding: 25px;
        box-shadow: 0 4px 24px rgba(0,0,0,0.04);
        text-align: center;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }

    /* --- NOTÍCIAS (Clean List) --- */
    .news-item {
        padding: 20px 0;
        border-bottom: 1px solid #e5e5e5;
        transition: opacity 0.3s;
    }
    .news-item:hover { opacity: 0.7; }
    .news-link {
        text-decoration: none;
        color: #1d1d1f;
        font-weight: 500;
        font-size: 18px;
        letter-spacing: -0.01em;
    }
    .news-meta {
        font-size: 13px;
        color: #86868b;
        margin-top: 5px;
    }
    
    /* --- INPUTS --- */
    .stSelectbox > div > div {
        background-color: #ffffff !important;
        color: #1d1d1f !important;
        border: 1px solid #d2d2d7;
        border-radius: 12px;
    }
    
    /* --- ANIMAÇÕES --- */
    @keyframes fadeUp {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* CTA FINAL */
    .cta-section {
        text-align: center;
        padding: 80px 20px;
        background: #ffffff;
        margin-top: 60px;
        border-radius: 30px;
    }
    .cta-text { font-size: 32px; font-weight: 600; color: #1d1d1f; margin-bottom: 20px; }
    .cta-sub { color: #86868b; font-size: 18px; }

</style>
""", unsafe_allow_html=True)

# --- 3. DADOS (Mantendo a lógica robusta) ---
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
    # Lógica refinada
    if avg > 0.1: return avg, "Tendência de Alta"
    elif avg < -0.1: return avg, "Tendência de Baixa"
    return avg, "Estabilidade"

# --- 4. LAYOUT PRINCIPAL (ESTRUTURA) ---

# HERO SECTION (O Impacto Visual)
st.markdown("""
<div class="hero-section">
    <div class="hero-title">Inteligência Financeira.<br>Elevada à Perfeição.</div>
    <div class="hero-subtitle">Uma experiência desenhada para quem exige clareza absoluta em um mundo de ruído.</div>
</div>
""", unsafe_allow_html=True)

# VALUE PROPOSITION (Grid Minimalista)
col_v1, col_v2, col_v3 = st.columns(3)
with col_v1:
    st.markdown("""
    <div class="feature-item">
        <span class="feature-icon">⚡</span>
        <div class="feature-head">Velocidade</div>
        <div class="feature-text">Dados em tempo real processados instantaneamente.</div>
    </div>
    """, unsafe_allow_html=True)
with col_v2:
    st.markdown("""
    <div class="feature-item">
        <span class="feature-icon">🔒</span>
        <div class="feature-head">Precisão</div>
        <div class="feature-text">Algoritmos de IA que filtram o essencial.</div>
    </div>
    """, unsafe_allow_html=True)
with col_v3:
    st.markdown("""
    <div class="feature-item">
        <span class="feature-icon">💎</span>
        <div class="feature-head">Design</div>
        <div class="feature-text">Visualização limpa para decisões complexas.</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# --- SIDEBAR (Controles Discretos) ---
st.sidebar.markdown("### Seleção")
selected_asset_name = st.sidebar.selectbox("Ativo", options=list(ASSET_DB.keys()))
ticker_input = ASSET_DB[selected_asset_name]

st.sidebar.markdown("<br>", unsafe_allow_html=True)
st.sidebar.markdown("### Período")
time_option = st.sidebar.select_slider("", options=["1M", "6M", "1A", "5A", "Max"], value="1A")
time_map = {"1M": "1mo", "6M": "6mo", "1A": "1y", "5A": "5y", "Max": "max"}

# ASSINATURA SIDEBAR (Minimalista)
st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style="color: #86868b; font-size: 12px; text-align: center;">
    Designed by Edson Junior<br>
    <span style="opacity: 0.5;">Engineering meets Art</span>
</div>
""", unsafe_allow_html=True)

# --- APP LOGIC ---

if ticker_input:
    period_yf = time_map[time_option]
    clean_name = selected_asset_name
    
    # Processamento silencioso
    history = get_stock_data(ticker_input, period_yf)
    news = get_real_news(clean_name)

    if history is not None and not history.empty:
        
        # SEÇÃO DE DESTAQUE (Metrics)
        st.markdown(f"<h3 style='text-align:center; font-weight:600; margin-bottom:30px; color:#1d1d1f;'>Análise: {clean_name}</h3>", unsafe_allow_html=True)
        
        current_price = history['Close'].iloc[-1]
        delta = current_price - history['Close'].iloc[-2]
        currency = "R$" if ".SA" in ticker_input else "US$"
        
        c1, c2 = st.columns([1.5, 1])
        
        with c1:
            st.metric("Cotação Atual", f"{currency} {current_price:.2f}", f"{delta:.2f}")
        
        with c2:
            score, sentiment_text = analyze_sentiment(news)
            # Cores Apple (Verde = #34c759, Vermelho = #ff3b30)
            color_sent = "#34c759" if score > 0.05 else "#ff3b30" if score < -0.05 else "#86868b"
            
            st.markdown(f"""
            <div class="sentiment-box">
                <div style="font-size: 12px; color: #86868b; text-transform: uppercase; letter-spacing: 1px;">Sentimento IA</div>
                <div style="font-size: 24px; font-weight: 600; color: {color_sent}; margin-top: 5px;">{sentiment_text}</div>
            </div>
            """, unsafe_allow_html=True)

        # GRÁFICO (Minimalista / Apple Style)
        st.markdown("<br>", unsafe_allow_html=True)
        
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1, row_heights=[0.75, 0.25])
        
        # Candle Clean
        fig.add_trace(go.Candlestick(
            x=history.index, open=history['Open'], high=history['High'], low=history['Low'], close=history['Close'],
            name="Preço", 
            increasing_line_color='#34c759', # Apple Green
            decreasing_line_color='#ff3b30', # Apple Red
            increasing_fillcolor='rgba(52, 199, 89, 0.1)', # Preenchimento suave
            decreasing_fillcolor='rgba(255, 59, 48, 0.1)'
        ), row=1, col=1)
        
        # Volume Suave
        fig.add_trace(go.Bar(
            x=history.index, y=history['Volume'], name="Volume", 
            marker_color='#86868b', opacity=0.3
        ), row=2, col=1)

        # Layout Limpo (Visual Silence)
        fig.update_layout(
            template='plotly_white', # Fundo branco nativo
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)',
            height=550, 
            xaxis_rangeslider_visible=False, 
            showlegend=False,
            margin=dict(l=20, r=20, t=20, b=20),
            hovermode="x unified"
        )
        # Refinando as grades para serem quase invisíveis
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.05)')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.05)')

        st.plotly_chart(fig, use_container_width=True)

        # SEÇÃO EMOCIONAL (Notícias)
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("<h4 style='font-weight: 600; color: #1d1d1f; margin-bottom: 20px;'>Contexto Global</h4>", unsafe_allow_html=True)
        
        if news:
            for n in news[:3]:
                st.markdown(f"""
                <div class="news-item">
                    <a href="{n['link']}" target="_blank" class="news-link">{n['title']}</a>
                    <div class="news-meta">{n.get('date', 'Recentemente')} • Google News</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("<div style='color:#86868b; font-style:italic;'>Sem ruído no momento.</div>", unsafe_allow_html=True)

    else:
        st.warning("Dados indisponíveis temporariamente.")

# FOOTER / CTA FINAL
st.markdown("""
<div class="cta-section">
    <div class="cta-text">O futuro do seu patrimônio é agora.</div>
    <div class="cta-sub">Mercado-FinancIA Pro.</div>
</div>
""", unsafe_allow_html=True)