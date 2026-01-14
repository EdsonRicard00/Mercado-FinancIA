import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from textblob import TextBlob
from GoogleNews import GoogleNews
import pandas as pd

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(layout="wide", page_title="Mercado-FinancIA | Premium", page_icon="💎")

# --- 2. CSS AVANÇADO (DESIGN SYSTEM PREMIUM) ---
st.markdown("""
<style>
    /* --- RESET & TIPOGRAFIA --- */
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Inter:wght@300;400;600&display=swap');

    /* Fundo Global Animado (Subtil) */
    .stApp {
        background: radial-gradient(circle at 50% 10%, #1a1a1a 0%, #050505 90%);
        color: #f0f0f0;
        font-family: 'Inter', sans-serif;
    }

    /* --- HERO SECTION (O Título Principal) --- */
    .hero-container {
        text-align: center;
        padding: 60px 20px;
        background: linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.01) 100%);
        backdrop-filter: blur(20px);
        border-radius: 30px;
        border: 1px solid rgba(255,255,255,0.08);
        box-shadow: 0 20px 50px rgba(0,0,0,0.5);
        margin-bottom: 50px;
        animation: fadeIn 1.5s ease-in-out;
    }

    .hero-title {
        font-family: 'Playfair Display', serif;
        font-size: 4em;
        background: linear-gradient(to right, #ffffff, #d4af37, #ffffff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 10px;
        letter-spacing: -1px;
    }

    .hero-subtitle {
        color: #a0a0a0;
        font-size: 1.2em;
        font-weight: 300;
        max-width: 600px;
        margin: 0 auto;
    }

    /* --- SIDEBAR (Menu Lateral) --- */
    [data-testid="stSidebar"] {
        background-color: rgba(10, 10, 10, 0.95);
        border-right: 1px solid #333;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2 {
        color: #d4af37 !important; /* Dourado */
        font-family: 'Playfair Display', serif;
    }

    /* --- CARDS DE PREÇO (Métricas) --- */
    div[data-testid="stMetric"] {
        background: linear-gradient(145deg, #1e1e1e, #161616);
        border: 1px solid #333;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 5px 5px 15px rgba(0,0,0,0.3);
        transition: transform 0.3s ease, border-color 0.3s;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-5px);
        border-color: #d4af37;
    }
    div[data-testid="stMetricLabel"] { color: #888 !important; font-size: 0.9em; text-transform: uppercase; letter-spacing: 1px; }
    div[data-testid="stMetricValue"] { color: #fff !important; font-size: 2.2em !important; font-family: 'Playfair Display', serif; }

    /* --- SENTIMENT CARD (IA) --- */
    .sentiment-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 25px;
        text-align: center;
        backdrop-filter: blur(10px);
    }
    .sentiment-label { color: #888; text-transform: uppercase; letter-spacing: 2px; font-size: 0.8em; }
    .sentiment-value { font-size: 1.8em; font-weight: 600; margin-top: 10px; }

    /* --- NOTÍCIAS (News Cards) --- */
    .news-card {
        background-color: #111;
        border-left: 3px solid #333;
        padding: 20px;
        margin-bottom: 15px;
        border-radius: 0 10px 10px 0;
        transition: all 0.3s ease;
    }
    .news-card:hover {
        background-color: #1a1a1a;
        border-left: 3px solid #d4af37; /* Destaque Dourado ao passar o mouse */
        padding-left: 30px; /* Animação de movimento */
        cursor: pointer;
    }
    .news-date { color: #555; font-size: 0.8em; margin-bottom: 5px; }
    .news-link { text-decoration: none; color: #e0e0e0; font-size: 1.1em; font-weight: 500; display: block;}
    .news-link:hover { color: #d4af37; }

    /* --- INPUTS & SLIDERS (Customização dos controles) --- */
    .stSelectbox > div > div { background-color: #1a1a1a !important; color: white !important; border-color: #333; }
    .stSlider > div > div > div > div { background-color: #d4af37 !important; }

    /* Animação de Entrada */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
</style>
""", unsafe_allow_html=True)

# --- 3. BANCO DE DADOS DE ATIVOS ---
ASSET_DB = {
    "🟡 Ouro (Gold Futures)": "GC=F", "⚪ Prata (Silver Futures)": "SI=F", "₿ Bitcoin (USD)": "BTC-USD",
    "🛢️ Petróleo Brent": "BZ=F", "🇺🇸 NVIDIA": "NVDA", "🇺🇸 Apple": "AAPL", "🇺🇸 Microsoft": "MSFT",
    "🇺🇸 Alphabet (Google)": "GOOGL", "🇺🇸 Amazon": "AMZN", "🇺🇸 Meta": "META", "🇺🇸 Tesla": "TSLA",
    "🇺🇸 Berkshire Hathaway": "BRK-B", "🇺🇸 JPMorgan": "JPM", "🇺🇸 Visa": "V", "🇺🇸 Johnson & Johnson": "JNJ",
    "🇺🇸 Walmart": "WMT", "🇺🇸 ExxonMobil": "XOM", "🇺🇸 Home Depot": "HD", "🇺🇸 Broadcom": "AVGO",
    "🇹🇼 TSMC": "TSM", "🇨🇳 Tencent": "TCEHY", "🇰🇷 Samsung": "SSNLF", "🇨🇭 Nestlé": "NSRGY",
    "🇯🇵 Toyota": "TM", "🇸🇦 Saudi Aramco": "2222.SR", "🇬🇧 Shell": "SHEL",
    "🇧🇷 Petrobras (PETR4)": "PETR4.SA", "🇧🇷 Vale (VALE3)": "VALE3.SA", "🇧🇷 Itaú (ITUB4)": "ITUB4.SA",
    "🇧🇷 Bradesco (BBDC4)": "BBDC4.SA", "🇧🇷 Banco do Brasil (BBAS3)": "BBAS3.SA", "🇧🇷 Nubank (NU)": "NU",
    "🇧🇷 Ambev (ABEV3)": "ABEV3.SA", "🇧🇷 B3 (B3SA3)": "B3SA3.SA", "🇧🇷 BTG Pactual (BPAC11)": "BPAC11.SA",
    "🇧🇷 Weg (WEGE3)": "WEGE3.SA", "🇧🇷 Suzano (SUZB3)": "SUZB3.SA", "🇧🇷 Gerdau (GGBR4)": "GGBR4.SA",
    "🇧🇷 Localiza (RENT3)": "RENT3.SA", "🇧🇷 JBS (JBSS3)": "JBSS3.SA", "🇧🇷 Magalu (MGLU3)": "MGLU3.SA",
    "🇧🇷 Sabesp (SBSP3)": "SBSP3.SA", "🇧🇷 Klabin (KLBN11)": "KLBN11.SA", "🇧🇷 Embraer (EMBR3)": "EMBR3.SA",
    "🇧🇷 Raízen (RAIZ4)": "RAIZ4.SA", "🇧🇷 Engie (ENGI11)": "ENGI11.SA", "🇧🇷 Hapvida (HAPV3)": "HAPV3.SA",
    "🇧🇷 Cogna (COGN3)": "COGN3.SA", "🇧🇷 MRV (MRVE3)": "MRVE3.SA", "🇧🇷 Natura (NTCO3)": "NTCO3.SA",
    "🇧🇷 XP Inc.": "XP"
}

# --- 4. FUNÇÕES DE BACKEND (Cacheado para Performance) ---
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
        googlenews.search(f"{term} market")
        return googlenews.result()
    except: return []

def analyze_sentiment(news_list):
    if not news_list: return 0, "Aguardando dados..."
    polarity_sum, count = 0, 0
    for n in news_list[:5]:
        text = n.get('title', '') + " " + n.get('desc', '')
        if text.strip():
            analysis = TextBlob(text)
            polarity_sum += analysis.sentiment.polarity
            count += 1
    avg = polarity_sum / count if count > 0 else 0
    if avg > 0.05: return avg, "OTIMISTA"
    elif avg < -0.05: return avg, "PESSIMISTA"
    return avg, "NEUTRO"

# --- 5. INTERFACE DO USUÁRIO (UX/UI) ---

# SIDEBAR (Configurações)
st.sidebar.markdown("## ⚙️ Painel de Controle")
selected_asset_name = st.sidebar.selectbox("Selecione o Ativo:", options=list(ASSET_DB.keys()))
ticker_input = ASSET_DB[selected_asset_name]

st.sidebar.markdown("<br>", unsafe_allow_html=True)
st.sidebar.markdown("### 📅 Horizonte Temporal")
time_option = st.sidebar.select_slider("", options=["1 Mês", "6 Meses", "1 Ano", "5 Anos", "25 Anos (Max)"], value="1 Ano")
time_map = {"1 Mês": "1mo", "6 Meses": "6mo", "1 Ano": "1y", "5 Anos": "5y", "25 Anos (Max)": "max"}

st.sidebar.markdown("---")
st.sidebar.markdown("<small style='color: #666'>Mercado-FinancIA v2.0 • Powered by Python</small>", unsafe_allow_html=True)

# ÁREA PRINCIPAL
# Hero Section (HTML Puro injetado)
st.markdown("""
    <div class="hero-container">
        <div class="hero-title">Mercado-FinancIA</div>
        <div class="hero-subtitle">Inteligência Artificial aplicada à análise de tendências globais. <br> Tome decisões baseadas em dados, não em palpites.</div>
    </div>
""", unsafe_allow_html=True)

if ticker_input:
    period_yf = time_map[time_option]
    clean_name = selected_asset_name.split(" ", 1)[1] if " " in selected_asset_name else selected_asset_name
    
    with st.spinner(f'Consultando satélites financeiros para {clean_name}...'):
        history = get_stock_data(ticker_input, period_yf)
        news = get_real_news(clean_name)

    if history is not None and not history.empty:
        # SEÇÃO 1: MÉTRICAS & SENTIMENTO
        st.markdown(f"<h3 style='margin-bottom: 20px; color: #d4af37;'>📊 Análise de {clean_name}</h3>", unsafe_allow_html=True)
        
        current_price = history['Close'].iloc[-1]
        delta = current_price - history['Close'].iloc[-2]
        currency = "R$" if ".SA" in ticker_input else "US$"
        
        col_metrics, col_sentiment = st.columns([1, 2])
        
        with col_metrics:
            st.metric("Cotação Atual", f"{currency} {current_price:.2f}", f"{delta:.2f}")

        with col_sentiment:
            score, sentiment_text = analyze_sentiment(news)
            color_sent = "#00ff88" if score > 0.05 else "#ff4b4b" if score < -0.05 else "#a0a0a0"
            icon_sent = "🚀" if score > 0.05 else "⚠️" if score < -0.05 else "⚖️"
            
            # Card HTML Personalizado para o Sentimento
            st.markdown(f"""
                <div class="sentiment-card">
                    <div class="sentiment-label">Sentimento de Mercado (IA Analysis)</div>
                    <div class="sentiment-value" style="color: {color_sent};">
                        {icon_sent} {sentiment_text}
                    </div>
                </div>
            """, unsafe_allow_html=True)

        # SEÇÃO 2: GRÁFICOS INTERATIVOS
        st.markdown("<br>", unsafe_allow_html=True)
        
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_heights=[0.7, 0.3])
        
        # Candlestick (Preço)
        fig.add_trace(go.Candlestick(
            x=history.index, open=history['Open'], high=history['High'], low=history['Low'], close=history['Close'],
            name="Preço", increasing_line_color='#00ff88', decreasing_line_color='#ff4b4b'
        ), row=1, col=1)
        
        # Volume (Barras)
        colors_vol = ['#00ff88' if r['Open']-r['Close']>=0 else '#ff4b4b' for i, r in history.iterrows()]
        fig.add_trace(go.Bar(
            x=history.index, y=history['Volume'], name="Volume", marker_color=colors_vol, opacity=0.3
        ), row=2, col=1)

        fig.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', # Fundo transparente para mesclar com o CSS
            height=600, xaxis_rangeslider_visible=False, showlegend=False,
            margin=dict(l=0, r=0, t=30, b=0),
            font=dict(family="Inter, sans-serif", size=12, color="#a0a0a0")
        )
        # Remove grades feias
        fig.update_xaxes(showgrid=False, zeroline=False)
        fig.update_yaxes(showgrid=True, gridcolor='rgba(255,255,255,0.05)', zeroline=False)

        st.plotly_chart(fig, use_container_width=True)

        # SEÇÃO 3: NOTÍCIAS (DESIGN PREMIUM)
        st.markdown("---")
        st.markdown("<h3 style='color: #d4af37;'>📰 Inteligência de Mercado</h3>", unsafe_allow_html=True)
        
        if not news:
            st.info("Nenhuma notícia recente encontrada nos feeds globais.")
        else:
            col_news1, col_news2 = st.columns(2)
            for i, n in enumerate(news[:4]):
                with (col_news1 if i % 2 == 0 else col_news2):
                    st.markdown(f"""
                    <div class="news-card">
                        <div class="news-date">📅 {n.get('date', 'Recentemente')} • Fonte: Google News</div>
                        <a href="{n['link']}" target="_blank" class="news-link">
                            {n['title']}
                        </a>
                    </div>
                    """, unsafe_allow_html=True)

    else:
        st.warning("Dados indisponíveis no momento. Tente outro ativo ou verifique sua conexão.")

else:
    st.info("👈 Selecione um ativo no menu lateral para iniciar a análise.")