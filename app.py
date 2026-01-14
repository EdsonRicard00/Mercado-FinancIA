import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from textblob import TextBlob
from GoogleNews import GoogleNews
import pandas as pd

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(layout="wide", page_title="Global Market Hybrid", page_icon="💎")

# --- CSS: HYBRID LUXURY (Fundo Dark + Caixas Light Glass) ---
st.markdown("""
<style>
    /* 1. Fundo da Página: PRETO PROFUNDO */
    .stApp {
        background-color: #050505;
        background-image: radial-gradient(circle at 50% 0%, #1a1a1a 0%, #050505 80%);
    }

    /* 2. Títulos e Textos soltos na página: BRANCO (para contraste com fundo preto) */
    h1, h2, h3, .stMarkdown p {
        color: #ffffff !important;
        font-family: 'Helvetica Neue', sans-serif;
    }

    /* 3. SIDEBAR: Branco Vidro (Light Glass) */
    [data-testid="stSidebar"] {
        background-color: rgba(255, 255, 255, 0.9); /* Quase sólido para leitura */
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(255, 255, 255, 0.5);
    }
    /* Texto da Sidebar: ESCURO (pois o fundo é branco) */
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] label, [data-testid="stSidebar"] span, [data-testid="stSidebar"] p {
        color: #2c3e50 !important;
    }

    /* 4. CARDS DE MÉTRICAS: Branco Vidro */
    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.85); /* Vidro branco leitoso */
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.9);
        border-radius: 15px;
        padding: 15px;
        box-shadow: 0 10px 20px rgba(0,0,0,0.3);
        border-left: 5px solid #d4af37; /* Detalhe dourado */
    }
    /* Texto dentro das métricas: ESCURO */
    div[data-testid="stMetricLabel"] { color: #5a6e83 !important; }
    div[data-testid="stMetricValue"] { color: #2c3e50 !important; }
    div[data-testid="stMetricDelta"] { color: #2c3e50 !important; }

    /* 5. Inputs e Selectbox na Sidebar (Ajuste para fundo claro) */
    .stSelectbox > div > div {
        background-color: white !important;
        color: black !important;
        border: 1px solid #ccc;
    }
    .stSelectbox div[data-baseweb="select"] span {
        color: black !important;
    }

    /* Centralizar gráficos */
    .js-plotly-plot { margin: auto; }
</style>
""", unsafe_allow_html=True)

# --- DADOS E FUNÇÕES ---
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
    if not news_list: return 0, "Sem dados"
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

# --- SIDEBAR ---
st.sidebar.header("💎 Seleção")
selected_asset_name = st.sidebar.selectbox("Escolha o Ativo:", options=list(ASSET_DB.keys()))
ticker_input = ASSET_DB[selected_asset_name]
st.sidebar.markdown("---")
st.sidebar.markdown("### 📅 Período")
time_option = st.sidebar.select_slider("", options=["1 Mês", "6 Meses", "1 Ano", "5 Anos", "25 Anos (Max)"], value="1 Ano")
time_map = {"1 Mês": "1mo", "6 Meses": "6mo", "1 Ano": "1y", "5 Anos": "5y", "25 Anos (Max)": "max"}

# --- PRINCIPAL ---
st.title(f"🏛️ {selected_asset_name}")

if ticker_input:
    period_yf = time_map[time_option]
    with st.spinner('Processando...'):
        history = get_stock_data(ticker_input, period_yf)
        clean_name = selected_asset_name.split(" ", 1)[1] if " " in selected_asset_name else selected_asset_name
        news = get_real_news(clean_name)

    if history is not None and not history.empty:
        # MÉTRICAS COM FUNDO BRANCO E TEXTO ESCURO
        current_price = history['Close'].iloc[-1]
        delta = current_price - history['Close'].iloc[-2]
        currency = "R$" if ".SA" in ticker_input else "US$"
        
        col1, col2 = st.columns([1, 2])
        col1.metric("Preço Atual", f"{currency} {current_price:.2f}", f"{delta:.2f}")
        
        score, sentiment_text = analyze_sentiment(news)
        color = "#00b894" if score > 0 else "#d63031" if score < 0 else "#636e72"
        icon = "🔼" if score > 0 else "🔽" if score < 0 else "⏺"
        
        # CARD DE SENTIMENTO (Branco Vidro Personalizado)
        col2.markdown(f"""
            <div style='padding: 20px; background: rgba(255,255,255,0.85); border-radius: 15px; border: 1px solid white; box-shadow: 0 4px 15px rgba(0,0,0,0.2);'>
                <span style='color: #5a6e83; font-size: 14px;'>Sentimento de IA:</span><br>
                <span style='color:{color}; font-size: 26px; font-weight: bold;'>{icon} {sentiment_text}</span>
            </div>
            """, unsafe_allow_html=True)

        # GRÁFICOS (Fundo Transparente para destacar no Preto)
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_heights=[0.7, 0.3])
        
        # Velas NEON (Verde/Vermelho) para contraste no fundo PRETO
        fig.add_trace(go.Candlestick(x=history.index, open=history['Open'], high=history['High'], low=history['Low'], close=history['Close'], name="Preço", increasing_line_color='#00ff88', decreasing_line_color='#ff4b4b'), row=1, col=1)
        
        colors = ['#00ff88' if r['Open']-r['Close']>=0 else '#ff4b4b' for i, r in history.iterrows()]
        fig.add_trace(go.Bar(x=history.index, y=history['Volume'], name="Volume", marker_color=colors, opacity=0.5), row=2, col=1)

        fig.update_layout(
            template='plotly_dark', # Mantém o tema escuro APENAS para o gráfico (eixos brancos)
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            height=600, xaxis_rangeslider_visible=False, showlegend=False,
            title=dict(text=f"Gráfico: {clean_name}", font=dict(color="white"))
        )
        st.plotly_chart(fig, use_container_width=True)

        # NOTÍCIAS (CARDS BRANCOS "VIDRO")
        st.markdown("---")
        st.subheader(f"📰 Notícias: {clean_name}")
        if not news: st.warning("Sem notícias recentes.")
        else:
            for n in news[:4]:
                st.markdown(f"""
                 <div style="
                    background: rgba(255, 255, 255, 0.9);
                    backdrop-filter: blur(10px);
                    border: 1px solid white;
                    padding: 15px; margin-bottom: 12px; border-radius: 12px;
                    box-shadow: 0 5px 15px rgba(0,0,0,0.2);
                    transition: transform 0.2s;
                 " onmouseover="this.style.transform='scale(1.02)'" onmouseout="this.style.transform='scale(1.0)'">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                        <small style="color: #666;">📅 {n.get('date', 'Recente')}</small>
                        <small style="color: #666;">Fonte: Google</small>
                    </div>
                    <a href="{n['link']}" target="_blank" style="text-decoration: none; color: #2c3e50; font-weight: bold; font-size: 1.1em;">
                        {n['title']}
                    </a>
                 </div>
                """, unsafe_allow_html=True)
    else: st.error("Dados indisponíveis.")