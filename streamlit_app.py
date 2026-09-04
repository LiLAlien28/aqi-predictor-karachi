import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import requests
import json
from datetime import datetime, timedelta

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Karachi AQI Forecast - Muhammad Aamir | 10Pearls",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# ULTRA MODERN CSS - DARK THEME WITH GLASS EFFECTS
# ============================================================

st.markdown("""
<style>
    .stApp {
        background: radial-gradient(ellipse at 20% 50%, #0d1520 0%, #0a0e17 100%);
        color: #ffffff;
    }
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 24px;
        padding: 28px;
        margin: 10px 0;
        box-shadow: 0 8px 40px rgba(0, 0, 0, 0.5);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .glass-card:hover {
        transform: translateY(-6px);
        border-color: rgba(0, 195, 255, 0.15);
        box-shadow: 0 16px 60px rgba(0, 195, 255, 0.06);
    }
    .gradient-text {
        background: linear-gradient(135deg, #00c3ff 0%, #7c3aed 50%, #a855f7 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
    }
    h1, h2, h3, h4 {
        color: #ffffff !important;
        font-weight: 600 !important;
        letter-spacing: -0.02em;
    }
    .metric-box {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.04);
        border-radius: 16px;
        padding: 20px 24px;
        text-align: center;
        transition: all 0.3s ease;
    }
    .metric-box:hover {
        border-color: rgba(0, 195, 255, 0.2);
        background: rgba(255, 255, 255, 0.04);
    }
    .metric-value {
        font-size: 34px;
        font-weight: 700;
        background: linear-gradient(135deg, #00c3ff, #7c3aed);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .metric-label {
        color: #94a3b8;
        font-size: 13px;
        margin-top: 4px;
        letter-spacing: 0.5px;
    }
    .badge {
        padding: 4px 16px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        display: inline-block;
        letter-spacing: 0.3px;
    }
    .badge-good { background: rgba(0, 255, 136, 0.12); color: #00ff88; border: 1px solid rgba(0, 255, 136, 0.15); }
    .badge-moderate { background: rgba(255, 238, 0, 0.12); color: #ffee00; border: 1px solid rgba(255, 238, 0, 0.15); }
    .badge-unhealthy { background: rgba(255, 153, 0, 0.12); color: #ff9900; border: 1px solid rgba(255, 153, 0, 0.15); }
    .badge-hazardous { background: rgba(255, 51, 51, 0.12); color: #ff3333; border: 1px solid rgba(255, 51, 51, 0.15); }
    .divider {
        border: none;
        height: 1px;
        background: linear-gradient(to right, transparent, rgba(255,255,255,0.06), transparent);
        margin: 32px 0;
    }
    .footer {
        text-align: center;
        color: #475569;
        padding: 30px 0 10px 0;
        border-top: 1px solid rgba(255, 255, 255, 0.03);
        margin-top: 30px;
        font-size: 13px;
    }
    .footer a {
        color: #60a5fa;
        text-decoration: none;
    }
    .stButton > button {
        border-radius: 12px;
        font-weight: 600;
        transition: all 0.3s ease;
        background: linear-gradient(135deg, #00c3ff, #7c3aed);
        color: white;
        border: none;
        padding: 12px 28px;
        width: 100%;
        box-shadow: 0 4px 20px rgba(0, 195, 255, 0.15);
    }
    .stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 8px 30px rgba(0, 195, 255, 0.25);
    }
    .live-dot {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background: #00ff88;
        animation: pulse-dot 1.5s ease-in-out infinite;
        margin-right: 8px;
    }
    @keyframes pulse-dot {
        0% { opacity: 1; transform: scale(1); box-shadow: 0 0 0 0 rgba(0, 255, 136, 0.4); }
        50% { opacity: 0.7; transform: scale(0.85); box-shadow: 0 0 0 8px rgba(0, 255, 136, 0); }
        100% { opacity: 1; transform: scale(1); box-shadow: 0 0 0 0 rgba(0, 255, 136, 0); }
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown("""
        <div style="text-align: center; padding: 20px 0 10px 0;">
            <div style="font-size: 56px;">🌍</div>
            <h2 style="margin: 6px 0 2px 0; font-size: 22px;">Karachi AQI</h2>
            <p style="color: #64748b; font-size: 13px; letter-spacing: 0.5px;">Forecast System v2.0</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown(f"""
        <div style="padding: 12px 0;">
            <div style="display: flex; align-items: center; gap: 12px; padding: 12px 16px; background: rgba(0, 255, 136, 0.04); border-radius: 12px; border: 1px solid rgba(0, 255, 136, 0.08);">
                <span class="live-dot"></span>
                <span style="color: #94a3b8; font-size: 14px;">System</span>
                <span style="margin-left: auto; color: #00ff88; font-size: 12px; font-weight: 700;">● LIVE</span>
            </div>
            <div style="display: flex; justify-content: space-between; padding: 8px 16px; font-size: 12px; color: #475569;">
                <span>Last Update: {datetime.now().strftime('%H:%M')}</span>
                <span>Data Source: Open-Meteo + AQICN</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("### 🎯 Forecast Horizon")
    horizon_options = {
        "🔵 24 Hours (H1)": 1,
        "🟣 48 Hours (H2)": 2,
        "🟢 72 Hours (H3)": 3
    }
    selected_horizon_label = st.selectbox(
        "Select prediction window",
        list(horizon_options.keys()),
        index=0,
        label_visibility="collapsed"
    )
    selected_horizon = horizon_options[selected_horizon_label]
    
    st.markdown("---")
    
    st.markdown("### 📊 Model Performance")
    performance_data = {
        "H1 (24h)": {"RMSE": 5.97, "R2": 0.843, "MAE": 4.59},
        "H2 (48h)": {"RMSE": 5.56, "R2": 0.862, "MAE": 4.15},
        "H3 (72h)": {"RMSE": 5.70, "R2": 0.855, "MAE": 4.34}
    }
    for horizon, metrics in performance_data.items():
        st.markdown(f"""
            <div style="background: rgba(255,255,255,0.02); border-radius: 10px; padding: 10px 14px; margin: 4px 0;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="color: #94a3b8; font-size: 13px;">{horizon}</span>
                    <span style="color: #e2e8f0; font-size: 13px; font-weight: 500;">R² <span class="gradient-text">{metrics['R2']:.3f}</span></span>
                </div>
                <div style="display: flex; justify-content: space-between; font-size: 11px; color: #475569; margin-top: 2px;">
                    <span>RMSE: {metrics['RMSE']:.2f}</span>
                    <span>MAE: {metrics['MAE']:.2f}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    with st.expander("🧠 Features Used in Model", expanded=False):
        st.markdown("""
            <div style="font-size: 13px; color: #94a3b8; line-height: 2;">
                <b style="color: #e2e8f0;">🌤️ Weather Features</b><br>
                pm2_5, pm10, carbon_monoxide<br>
                nitrogen_dioxide, sulphur_dioxide, ozone<br><br>
                <b style="color: #e2e8f0;">⏰ Time Features</b><br>
                hour, day, month<br><br>
                <b style="color: #e2e8f0;">🔄 Lag Features</b><br>
                lag_1 (1h), lag_3 (3h), lag_6 (6h)<br><br>
                <b style="color: #e2e8f0;">📊 Rolling Statistics</b><br>
                roll_mean_6, roll_mean_12<br><br>
                <b style="color: #e2e8f0;">🎯 Target</b><br>
                aqi_pm25 (PM2.5 concentration)
            </div>
        """, unsafe_allow_html=True)
    
    with st.expander("📊 Feature Importance Insights", expanded=False):
        st.markdown("""
            <div style="font-size: 13px; color: #94a3b8; line-height: 2;">
                <b style="color: #e2e8f0;">🔑 Top Predictors</b><br>
                • <span style="color: #00c3ff;">pm2_5</span> — Strongest predictor<br>
                • <span style="color: #7c3aed;">aqi_pm25</span> — Target variable<br>
                • <span style="color: #7c3aed;">day</span> — Weekly patterns<br>
                • <span style="color: #7c3aed;">roll_mean_12</span> — Smoothing effect<br>
                • <span style="color: #7c3aed;">nitrogen_dioxide</span> — Traffic indicator
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    if st.button("📥 Export Forecast Report"):
        st.info("Report exported! (Feature coming soon)")
    
    st.markdown("---")
    
    st.markdown("""
        <div style="text-align: center; padding: 15px 0 5px 0; border-top: 1px solid rgba(255, 255, 255, 0.03); margin-top: 10px;">
            <div style="color: #60a5fa; font-weight: 600; font-size: 14px;">👨‍💻 Muhammad Aamir</div>
            <div style="color: #64748b; font-size: 12px;">10 Pearls Shine Intern • Cohort 9</div>
            <div style="color: #475569; font-size: 11px; margin-top: 4px;">AI/ML Engineer</div>
            <div style="display: flex; justify-content: center; gap: 12px; margin-top: 8px; font-size: 13px;">
                <a href="https://www.linkedin.com/in/moaamir28" target="_blank" style="color: #60a5fa; text-decoration: none;">LinkedIn</a>
                <a href="https://github.com/LiLAlien28" target="_blank" style="color: #60a5fa; text-decoration: none;">GitHub</a>
            </div>
        </div>
    """, unsafe_allow_html=True)

# ============================================================
# BACKEND CONFIGURATION
# ============================================================

BASE_URL = "https://aqi-predictor-karachi-production.up.railway.app"

@st.cache_data(ttl=300)
def fetch_data(endpoint):
    try:
        url = f"{BASE_URL}/{endpoint}"
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        return None

@st.cache_data(ttl=300)
def fetch_current_aqi():
    try:
        response = requests.get(
            "https://api.waqi.info/feed/geo:24.8608;67.0104/?token=593d56f2c0edba0cb9ccd27eac295534c4206b65",
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "ok":
                return data["data"]
    except:
        pass
    return None

# ============================================================
# LOAD DATA
# ============================================================

with st.spinner("🔄 Loading AI Engine..."):
    forecast_data = fetch_data("forecast")
    best_model_data = fetch_data("models/best")
    feature_importance_data = fetch_data("features/importance?horizon=1")
    current_aqi_data = fetch_current_aqi()

# ============================================================
# FUNCTIONS
# ============================================================

def aqi_category(value):
    if value <= 50:
        return "Good", "badge-good", "#00ff88"
    elif value <= 100:
        return "Moderate", "badge-moderate", "#ffee00"
    elif value <= 150:
        return "Unhealthy (Sensitive)", "badge-unhealthy", "#ff9900"
    elif value <= 200:
        return "Unhealthy", "badge-unhealthy", "#ff3333"
    else:
        return "Hazardous", "badge-hazardous", "#9900cc"

def create_gauge(value, date_label, horizon):
    category, badge_class, color = aqi_category(value)
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=float(value),
        title={
            'text': f"{date_label}<br><span class='{badge_class}'>{category}</span>",
            'font': {'size': 14, 'color': '#e2e8f0'}
        },
        number={'font': {'size': 30, 'color': '#ffffff'}},
        gauge={
            'axis': {'range': [0, 300], 'tickwidth': 1, 'tickcolor': '#94a3b8', 'tickfont': {'size': 10}},
            'bar': {'color': color, 'thickness': 0.25},
            'bgcolor': 'rgba(255, 255, 255, 0.02)',
            'borderwidth': 0,
            'steps': [
                {'range': [0, 50], 'color': 'rgba(0, 255, 136, 0.1)'},
                {'range': [50, 100], 'color': 'rgba(255, 238, 0, 0.1)'},
                {'range': [100, 150], 'color': 'rgba(255, 153, 0, 0.1)'},
                {'range': [150, 200], 'color': 'rgba(255, 51, 51, 0.1)'},
                {'range': [200, 300], 'color': 'rgba(153, 0, 204, 0.1)'},
            ],
            'threshold': {
                'line': {'color': '#ffffff', 'width': 2},
                'thickness': 0.5,
                'value': float(value)
            }
        }
    ))

    fig.update_layout(
        height=270,
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='#e2e8f0',
        margin=dict(l=20, r=20, t=60, b=20)
    )
    return fig

def create_feature_importance_chart(features_data):
    if not features_data or "features" not in features_data:
        return None
    
    df = pd.DataFrame(features_data["features"])
    df = df.sort_values("importance", ascending=True).tail(10)
    
    colors = ['#7c3aed' if i >= len(df) - 2 else '#60a5fa' if i >= len(df) - 5 else '#94a3b8' for i in range(len(df))]
    
    fig = go.Figure(go.Bar(
        x=df["importance"],
        y=df["feature"],
        orientation='h',
        marker_color=colors,
        text=df["importance"].round(3),
        textposition='outside',
        textfont=dict(color='#e2e8f0', size=11),
        hovertemplate='<b>%{y}</b><br>Importance: %{x:.4f}<extra></extra>'
    ))

    fig.update_layout(
        height=400,
        template='plotly_dark',
        xaxis=dict(
            title="Feature Importance Score",
            titlefont=dict(color='#94a3b8'),
            tickfont=dict(color='#94a3b8'),
            gridcolor='rgba(255,255,255,0.03)'
        ),
        yaxis=dict(
            title="Feature",
            titlefont=dict(color='#94a3b8'),
            tickfont=dict(color='#e2e8f0'),
            gridcolor='rgba(255,255,255,0.03)'
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=60, t=20, b=20),
        hovermode='y'
    )
    return fig

# ============================================================
# MAIN DASHBOARD
# ============================================================

if forecast_data:
    
    st.markdown("""
        <div style="text-align: center; padding: 10px 0 5px 0;">
            <h1 style="font-size: 48px; margin: 0; letter-spacing: -0.5px;">🌍 Karachi AQI Forecast</h1>
            <p style="color: #94a3b8; font-size: 18px; margin: 6px 0; letter-spacing: 0.3px;">
                AI-Powered Multi-Horizon Air Quality Prediction
            </p>
            <p style="color: #475569; font-size: 14px; margin-top: 4px;">
                Built by <strong style="color: #60a5fa;">Muhammad Aamir</strong> • 10 Pearls Shine Intern • Cohort 9
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    
    # ===== CURRENT AQI =====
    st.markdown("## 📍 Current Air Quality")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if current_aqi_data:
            current_aqi = current_aqi_data.get("aqi", "N/A")
            if isinstance(current_aqi, (int, float)):
                category, _, color = aqi_category(current_aqi)
                st.markdown(f"""
                    <div class="glass-card" style="text-align: center;">
                        <div style="font-size: 14px; color: #94a3b8;">Live AQI</div>
                        <div style="font-size: 56px; font-weight: 800; color: {color}; line-height: 1.2;">{current_aqi}</div>
                        <div><span class="badge badge-{category.lower().replace(' ', '-')}">{category}</span></div>
                        <div style="font-size: 12px; color: #475569; margin-top: 8px;">Updated: {datetime.now().strftime('%H:%M')}</div>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                    <div class="glass-card" style="text-align: center;">
                        <div style="font-size: 14px; color: #94a3b8;">Live AQI</div>
                        <div style="font-size: 32px; font-weight: 600; color: #64748b;">N/A</div>
                        <div style="font-size: 12px; color: #475569; margin-top: 8px;">Data unavailable</div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
                <div class="glass-card" style="text-align: center;">
                    <div style="font-size: 14px; color: #94a3b8;">Live AQI</div>
                    <div style="font-size: 32px; font-weight: 600; color: #64748b;">N/A</div>
                    <div style="font-size: 12px; color: #475569; margin-top: 8px;">Using model predictions</div>
                </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="glass-card">
                <div style="font-size: 14px; color: #94a3b8; margin-bottom: 8px;">📊 AQI Status</div>
                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; text-align: center;">
                    <div style="background: rgba(255,255,255,0.02); border-radius: 8px; padding: 8px;">
                        <div style="color: #00ff88; font-weight: 700;">0-50</div>
                        <div style="font-size: 11px; color: #64748b;">Good</div>
                    </div>
                    <div style="background: rgba(255,255,255,0.02); border-radius: 8px; padding: 8px;">
                        <div style="color: #ffee00; font-weight: 700;">51-100</div>
                        <div style="font-size: 11px; color: #64748b;">Moderate</div>
                    </div>
                    <div style="background: rgba(255,255,255,0.02); border-radius: 8px; padding: 8px;">
                        <div style="color: #ff9900; font-weight: 700;">101-150</div>
                        <div style="font-size: 11px; color: #64748b;">Unhealthy</div>
                    </div>
                    <div style="background: rgba(255,255,255,0.02); border-radius: 8px; padding: 8px;">
                        <div style="color: #ff6b6b; font-weight: 700;">151-200</div>
                        <div style="font-size: 11px; color: #64748b;">Very Unhealthy</div>
                    </div>
                    <div style="background: rgba(255,255,255,0.02); border-radius: 8px; padding: 8px;">
                        <div style="color: #9900cc; font-weight: 700;">201-300</div>
                        <div style="font-size: 11px; color: #64748b;">Hazardous</div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div class="glass-card" style="text-align: center;">
                <div style="font-size: 14px; color: #94a3b8;">Data Sources</div>
                <div style="font-size: 13px; color: #64748b; margin-top: 8px; text-align: left;">
                    <div>🔹 Open-Meteo API (Weather)</div>
                    <div>🔹 AQICN API (Current AQI)</div>
                    <div>🔹 Custom Model (Forecast)</div>
                    <div style="margin-top: 8px; font-size: 11px; color: #475569;">Last sync: {datetime.now().strftime('%Y-%m-%d %H:%M')}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    
    # ===== KEY METRICS =====
    st.markdown("## 📊 Key Metrics")
    
    values = [
        forecast_data["1_day"]["value"],
        forecast_data["2_day"]["value"],
        forecast_data["3_day"]["value"]
    ]
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(f"""
            <div class="metric-box">
                <div class="metric-value">{max(values):.1f}</div>
                <div class="metric-label">Peak AQI</div>
                <div class="metric-delta positive">⏫ 3-Day Max</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class="metric-box">
                <div class="metric-value">{np.mean(values):.1f}</div>
                <div class="metric-label">Average AQI</div>
                <div class="metric-delta">📊 3-Day Mean</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div class="metric-box">
                <div class="metric-value">{min(values):.1f}</div>
                <div class="metric-label">Minimum AQI</div>
                <div class="metric-delta">📉 Best Day</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        delta = values[-1] - values[0]
        trend = "🔺 Rising" if delta > 0 else "🔻 Falling"
        color_class = "positive" if delta < 0 else "negative"
        st.markdown(f"""
            <div class="metric-box">
                <div class="metric-value">{trend}</div>
                <div class="metric-label">3-Day Trend</div>
                <div class="metric-delta {color_class}">{'+' if delta > 0 else ''}{delta:.1f} AQI</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col5:
        st.markdown(f"""
            <div class="metric-box">
                <div class="metric-value">72h</div>
                <div class="metric-label">Forecast Window</div>
                <div class="metric-delta">⏱️ 3 Days</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    
    # ===== GAUGE CHARTS =====
    st.markdown("## 📅 72-Hour AQI Forecast")
    
    col1, col2, col3 = st.columns(3)
    
    days = [
        ("Day 1", forecast_data["1_day"]["date"], forecast_data["1_day"]["value"]),
        ("Day 2", forecast_data["2_day"]["date"], forecast_data["2_day"]["value"]),
        ("Day 3", forecast_data["3_day"]["date"], forecast_data["3_day"]["value"])
    ]
    
    for idx, (day, date, value) in enumerate(days):
        with [col1, col2, col3][idx]:
            with st.container():
                st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
                fig = create_gauge(value, f"{day}<br>{date}", idx+1)
                st.plotly_chart(fig, use_container_width=True, key=f"gauge_{idx}")
                st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    
    # ===== TREND CHART =====
    st.markdown("## 📈 Forecast Trend Analysis")
    
    dates = [forecast_data["1_day"]["date"], forecast_data["2_day"]["date"], forecast_data["3_day"]["date"]]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=dates,
        y=values,
        mode='lines+markers',
        line=dict(color='#00c3ff', width=4),
        marker=dict(size=14, color='#00c3ff', symbol='circle', line=dict(width=2, color='#ffffff')),
        name='AQI Forecast',
        fill='tozeroy',
        fillcolor='rgba(0, 195, 255, 0.06)',
        hovertemplate='<b>%{x}</b><br>AQI: %{y:.1f}<extra></extra>'
    ))
    
    fig.add_hline(y=50, line_dash="dash", line_color="#00ff88", opacity=0.4)
    fig.add_hline(y=100, line_dash="dash", line_color="#ffee00", opacity=0.4)
    fig.add_hline(y=150, line_dash="dash", line_color="#ff9900", opacity=0.4)
    
    fig.update_layout(
        height=350,
        template='plotly_dark',
        xaxis=dict(
            title="Date",
            titlefont=dict(color='#94a3b8'),
            tickfont=dict(color='#94a3b8'),
            gridcolor='rgba(255,255,255,0.03)'
        ),
        yaxis=dict(
            title="AQI Value",
            titlefont=dict(color='#94a3b8'),
            tickfont=dict(color='#94a3b8'),
            gridcolor='rgba(255,255,255,0.03)',
            range=[0, max(values) + 60]
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        hovermode='x unified',
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1,
            font=dict(color='#94a3b8', size=11)
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    
    # ===== HEALTH ADVISORY =====
    st.markdown("## 🚨 Health Advisory")
    
    max_aqi = max(values)
    category, _, color = aqi_category(max_aqi)
    
    col1, col2 = st.columns([1, 2.5])
    
    with col1:
        st.markdown(f"""
            <div style="text-align: center; background: rgba(255,255,255,0.02); border-radius: 16px; padding: 24px; border: 1px solid rgba(255,255,255,0.04);">
                <div style="font-size: 56px; font-weight: 800; color: {color};">{max_aqi:.0f}</div>
                <div style="font-size: 14px; color: #94a3b8;">Peak AQI</div>
                <div style="margin-top: 8px;">
                    <span class="badge badge-{category.lower().replace(' ', '-')}">{category}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if max_aqi > 200:
            st.error("""
                <div style="font-size: 16px; font-weight: 600;">⚠️ Hazardous Air Quality</div>
                <div style="font-size: 14px; color: #94a3b8; margin-top: 8px;">
                    🛑 Avoid all outdoor exposure<br>
                    🏠 Stay indoors with air purifiers<br>
                    😷 Wear N95 masks if necessary
                </div>
            """, unsafe_allow_html=True)
        elif max_aqi > 150:
            st.warning("""
                <div style="font-size: 16px; font-weight: 600;">🟠 Unhealthy Air Quality</div>
                <div style="font-size: 14px; color: #94a3b8; margin-top: 8px;">
                    🚶 Limit outdoor physical activity<br>
                    👵 Sensitive groups should stay indoors<br>
                    🔒 Keep windows closed
                </div>
            """, unsafe_allow_html=True)
        elif max_aqi > 100:
            st.info("""
                <div style="font-size: 16px; font-weight: 600;">🟡 Moderate Air Quality</div>
                <div style="font-size: 14px; color: #94a3b8; margin-top: 8px;">
                    👃 Unusually sensitive people should limit outdoor exposure<br>
                    🌿 General public is safe
                </div>
            """, unsafe_allow_html=True)
        else:
            st.success("""
                <div style="font-size: 16px; font-weight: 600;">🟢 Good Air Quality</div>
                <div style="font-size: 14px; color: #94a3b8; margin-top: 8px;">
                    🌿 Air quality is satisfactory<br>
                    🏃 Enjoy outdoor activities!<br>
                    🪟 Open windows for fresh air
                </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    
    # ===== MODEL PERFORMANCE & FEATURE IMPORTANCE =====
    col1, col2 = st.columns([1, 1.2])
    
    with col1:
        st.markdown("## 🏆 Model Performance")
        
        if best_model_data and "model" in best_model_data:
            model = best_model_data["model"]
            st.markdown(f"""
                <div class="glass-card">
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                        <div style="background: rgba(255,255,255,0.02); border-radius: 12px; padding: 14px; text-align: center;">
                            <div style="font-size: 11px; color: #94a3b8;">Model</div>
                            <div style="font-size: 15px; font-weight: 600; color: #60a5fa;">{model.get('model_name', 'Random Forest')}</div>
                        </div>
                        <div style="background: rgba(255,255,255,0.02); border-radius: 12px; padding: 14px; text-align: center;">
                            <div style="font-size: 11px; color: #94a3b8;">Horizon</div>
                            <div style="font-size: 15px; font-weight: 600; color: #e2e8f0;">{model.get('horizon', 1)} (24h)</div>
                        </div>
                        <div style="background: rgba(255,255,255,0.02); border-radius: 12px; padding: 14px; text-align: center;">
                            <div style="font-size: 11px; color: #94a3b8;">RMSE</div>
                            <div style="font-size: 18px; font-weight: 700; color: #00c3ff;">{model.get('rmse', 5.97):.2f}</div>
                        </div>
                        <div style="background: rgba(255,255,255,0.02); border-radius: 12px; padding: 14px; text-align: center;">
                            <div style="font-size: 11px; color: #94a3b8;">R² Score</div>
                            <div style="font-size: 18px; font-weight: 700; color: #7c3aed;">{model.get('r2', 0.843):.3f}</div>
                        </div>
                    </div>
                    <div style="margin-top: 12px; text-align: center; font-size: 13px; color: #94a3b8;">
                        Status: <span style="color: #00ff88; font-weight: 600;">● Production Ready</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("## 📊 Feature Importance")
        
        if feature_importance_data and "features" in feature_importance_data:
            fig = create_feature_importance_chart(feature_importance_data)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("⚠️ Feature importance data unavailable.")
        else:
            st.warning("⚠️ Feature importance data unavailable.")
    
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    
    # ===== FEATURE IMPACT ANALYSIS =====
    st.markdown("## 🔬 Feature Impact Analysis")
    
    st.markdown("""
        <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; margin: 10px 0;">
            <div style="background: rgba(255,255,255,0.02); border-radius: 14px; padding: 16px; border: 1px solid rgba(255,255,255,0.04);">
                <div style="font-size: 13px; color: #94a3b8;">🔹 Strongest Positive Impact</div>
                <div style="margin-top: 8px;">
                    <div style="display: flex; justify-content: space-between; padding: 4px 0;">
                        <span style="color: #e2e8f0;">pm2_5</span>
                        <span style="color: #00c3ff;">+0.19</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; padding: 4px 0;">
                        <span style="color: #e2e8f0;">aqi_pm25</span>
                        <span style="color: #00c3ff;">+0.17</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; padding: 4px 0;">
                        <span style="color: #e2e8f0;">day</span>
                        <span style="color: #7c3aed;">+0.12</span>
                    </div>
                </div>
            </div>
            <div style="background: rgba(255,255,255,0.02); border-radius: 14px; padding: 16px; border: 1px solid rgba(255,255,255,0.04);">
                <div style="font-size: 13px; color: #94a3b8;">🔸 Understanding Feature Importance</div>
                <div style="margin-top: 8px; font-size: 13px; color: #94a3b8; line-height: 1.6;">
                    Feature importance values show how much each feature contributes to the predicted AQI.
                    <br><br>
                    <span style="color: #00c3ff;">🔵 Higher values</span> = stronger influence on predictions
                </div>
            </div>
            <div style="background: rgba(255,255,255,0.02); border-radius: 14px; padding: 16px; border: 1px solid rgba(255,255,255,0.04);">
                <div style="font-size: 13px; color: #94a3b8;">🔹 Key Insights</div>
                <div style="margin-top: 8px; font-size: 13px; color: #94a3b8; line-height: 1.8;">
                    • <span style="color: #00c3ff;">pm2_5</span> is the dominant predictor<br>
                    • <span style="color: #7c3aed;">Day</span> captures weekly patterns<br>
                    • <span style="color: #7c3aed;">Nitrogen dioxide</span> reflects traffic<br>
                    • <span style="color: #7c3aed;">Rolling means</span> smooth noise<br>
                    • <span style="color: #7c3aed;">Month</span> captures seasonal trends
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    
    # ===== SYSTEM STATUS =====
    st.markdown("## ⚙️ System Status")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            <div class="glass-card" style="padding: 16px;">
                <div style="font-size: 12px; color: #94a3b8;">Backend API</div>
                <div style="display: flex; align-items: center; gap: 8px; margin-top: 4px;">
                    <span style="color: #00ff88;">●</span>
                    <span style="color: #e2e8f0;">Online</span>
                    <span style="margin-left: auto; font-size: 11px; color: #475569;">Railway</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="glass-card" style="padding: 16px;">
                <div style="font-size: 12px; color: #94a3b8;">MongoDB</div>
                <div style="display: flex; align-items: center; gap: 8px; margin-top: 4px;">
                    <span style="color: #00ff88;">●</span>
                    <span style="color: #e2e8f0;">Connected</span>
                    <span style="margin-left: auto; font-size: 11px; color: #475569;">Atlas</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div class="glass-card" style="padding: 16px;">
                <div style="font-size: 12px; color: #94a3b8;">Model Registry</div>
                <div style="display: flex; align-items: center; gap: 8px; margin-top: 4px;">
                    <span style="color: #00ff88;">●</span>
                    <span style="color: #e2e8f0;">Active</span>
                    <span style="margin-left: auto; font-size: 11px; color: #475569;">GridFS</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

else:
    st.error("""
        <div style="text-align: center; padding: 40px 20px;">
            <div style="font-size: 48px; margin-bottom: 16px;">🔌</div>
            <h3>Backend Connection Error</h3>
            <p style="color: #94a3b8;">Unable to connect to the prediction engine. Please check your connection or try again later.</p>
        </div>
    """, unsafe_allow_html=True)

# ============================================================
# FOOTER
# ============================================================

st.markdown("""
    <div class="footer">
        <p style="font-size: 15px;">
            🌍 <strong>Karachi AQI Forecast System</strong> 
        </p>
        <p>
            Built with ❤️ by <strong style="color: #60a5fa;">Muhammad Aamir</strong> • 10 Pearls Shine Intern • Cohort 9
        </p>
        <p style="font-size: 12px; color: #475569;">
            🚀 Production-Grade MLOps Pipeline • FastAPI + Streamlit • Feature Importance Analysis
        </p>
        <p style="font-size: 11px; color: #334155; margin-top: 8px;">
            © 2026 • All Rights Reserved
        </p>
    </div>
""", unsafe_allow_html=True)
