import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import requests
from datetime import datetime, timedelta
import json

# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="Karachi AQI Forecast - Muhammad Aamir",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================================
# CUSTOM CSS - MODERN DARK UI
# ==========================================================

st.markdown("""
    <style>
        /* Main background */
        .stApp {
            background: linear-gradient(135deg, #0e1117 0%, #1a1f2e 100%);
            color: #ffffff;
        }
        
        /* Cards */
        .card {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 16px;
            padding: 24px;
            margin: 10px 0;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        .card:hover {
            transform: translateY(-4px);
            box-shadow: 0 12px 48px rgba(0, 0, 0, 0.5);
        }
        
        /* Headers */
        h1, h2, h3, h4 {
            color: #ffffff !important;
            font-weight: 600 !important;
        }
        
        /* Metric boxes */
        .metric-box {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 12px;
            padding: 16px;
            text-align: center;
        }
        .metric-value {
            font-size: 32px;
            font-weight: 700;
            background: linear-gradient(135deg, #00c3ff, #7c3aed);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .metric-label {
            color: #94a3b8;
            font-size: 14px;
            margin-top: 4px;
        }
        
        /* Status badges */
        .badge {
            padding: 6px 16px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: 600;
            display: inline-block;
        }
        .badge-good { background: rgba(0, 255, 136, 0.2); color: #00ff88; }
        .badge-moderate { background: rgba(255, 238, 0, 0.2); color: #ffee00; }
        .badge-unhealthy { background: rgba(255, 153, 0, 0.2); color: #ff9900; }
        .badge-hazardous { background: rgba(255, 51, 51, 0.2); color: #ff3333; }
        
        /* Divider */
        .custom-divider {
            border: none;
            height: 1px;
            background: linear-gradient(to right, transparent, rgba(255,255,255,0.1), transparent);
            margin: 30px 0;
        }
        
        /* Footer */
        .footer {
            text-align: center;
            color: #64748b;
            padding: 30px 0 10px 0;
            border-top: 1px solid rgba(255, 255, 255, 0.05);
            margin-top: 30px;
        }
        .footer a {
            color: #60a5fa;
            text-decoration: none;
        }
        .footer a:hover {
            color: #93bbfc;
            text-decoration: underline;
        }
        
        /* Sidebar */
        .css-1d391kg {
            background: rgba(14, 17, 23, 0.9);
            backdrop-filter: blur(10px);
        }
        
        /* Success/Warning/Error boxes */
        .stAlert {
            border-radius: 12px;
            border-left: 4px solid;
        }
        
        /* Buttons */
        .stButton > button {
            border-radius: 8px;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        .stButton > button:hover {
            transform: scale(1.02);
        }
        
        /* Author credit in sidebar */
        .sidebar-author {
            text-align: center;
            padding: 15px 0 5px 0;
            border-top: 1px solid rgba(255, 255, 255, 0.05);
            margin-top: 20px;
        }
        .sidebar-author .name {
            color: #60a5fa;
            font-weight: 600;
            font-size: 15px;
        }
        .sidebar-author .cohort {
            color: #94a3b8;
            font-size: 12px;
        }
    </style>
""", unsafe_allow_html=True)

# ==========================================================
# SIDEBAR
# ==========================================================

with st.sidebar:
    # Logo/Header
    st.markdown("""
        <div style="text-align: center; padding: 20px 0;">
            <div style="font-size: 48px;">🌍</div>
            <h2 style="margin: 10px 0 5px 0;">Karachi AQI</h2>
            <p style="color: #94a3b8; font-size: 14px;">Forecast System</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # System Status
    st.markdown("### 📊 System Status")
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 10px;">
            <span style="display: inline-block; width: 10px; height: 10px; border-radius: 50%; background: #00ff88; animation: pulse 2s infinite;"></span>
            <span style="color: #94a3b8; font-size: 14px;">Operational</span>
        </div>
        <style>
            @keyframes pulse {
                0% { opacity: 1; }
                50% { opacity: 0.5; }
                100% { opacity: 1; }
            }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Features List
    st.markdown("### ⚙️ Features")
    features = [
        "📈 3-Day Forecast",
        "📊 Gauge Visualization",
        "📉 Trend Analysis",
        "🏆 Model Performance",
        "🔬 Feature Importance"
    ]
    for feature in features:
        st.markdown(f"- {feature}")
    
    st.markdown("---")
    
    # Author Credit
    st.markdown("""
        <div class="sidebar-author">
            <div class="name">👨‍💻 Muhammad Aamir</div>
            <div class="cohort">Cohort 9</div>
            <div style="color: #64748b; font-size: 11px; margin-top: 4px;">10 Pearls Shine Intern</div>
        </div>
    """, unsafe_allow_html=True)

# ==========================================================
# HEADER
# ==========================================================

st.markdown("""
    <div style="text-align: center; padding: 20px 0 10px 0;">
        <h1 style="font-size: 48px; margin: 0;">🌍 Karachi AQI Forecast</h1>
        <p style="color: #94a3b8; font-size: 18px; margin: 5px 0;">
            AI-Powered Multi-Horizon Air Quality Prediction
        </p>
        <p style="color: #64748b; font-size: 14px;">
            By <strong style="color: #60a5fa;">Muhammad Aamir</strong> • Cohort 9
        </p>
    </div>
""", unsafe_allow_html=True)

st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)

# ==========================================================
# BACKEND URLS
# ==========================================================

BASE_URL = "https://web-production-382ce.up.railway.app"

FORECAST_URL = f"{BASE_URL}/forecast"
BEST_MODEL_URL = f"{BASE_URL}/models/best"
FEATURE_URL = f"{BASE_URL}/features/importance?horizon=1"

# ==========================================================
# FETCH FORECAST
# ==========================================================

def fetch_data(url, timeout=30):
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except:
        return None

with st.spinner("🔄 Connecting to backend..."):
    results = fetch_data(FORECAST_URL)

if results is None:
    st.error("🚨 Backend unavailable. Please try again.")
    if st.button("🔄 Retry Connection"):
        st.rerun()
    st.stop()

# ==========================================================
# AQI CATEGORY
# ==========================================================

def aqi_category(value):
    if value <= 50:
        return "Good", "badge-good"
    elif value <= 100:
        return "Moderate", "badge-moderate"
    elif value <= 150:
        return "Unhealthy (Sensitive)", "badge-unhealthy"
    elif value <= 200:
        return "Unhealthy", "badge-unhealthy"
    else:
        return "Hazardous", "badge-hazardous"

# ==========================================================
# GAUGE FUNCTION
# ==========================================================

def create_gauge(value, date_label):
    category, badge_class = aqi_category(value)
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={
            'text': f"{date_label}<br><span class='{badge_class}'>{category}</span>",
            'font': {'size': 16}
        },
        gauge={
            'axis': {'range': [0, 300], 'tickwidth': 1, 'tickcolor': "white"},
            'bar': {'color': "#00c3ff"},
            'steps': [
                {'range': [0, 50], 'color': "rgba(0, 255, 136, 0.2)"},
                {'range': [50, 100], 'color': "rgba(255, 238, 0, 0.2)"},
                {'range': [100, 150], 'color': "rgba(255, 153, 0, 0.2)"},
                {'range': [150, 200], 'color': "rgba(255, 51, 51, 0.2)"},
                {'range': [200, 300], 'color': "rgba(153, 0, 204, 0.2)"},
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': value
            }
        }
    ))

    fig.update_layout(
        height=320,
        paper_bgcolor="#0e1117",
        font_color="white",
        margin=dict(l=20, r=20, t=50, b=20)
    )

    st.plotly_chart(fig, use_container_width=True)

# ==========================================================
# FORECAST SECTION
# ==========================================================

st.markdown("## 📅 Multi-Day AQI Forecast")

col1, col2, col3 = st.columns(3)

with col1:
    with st.container():
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        create_gauge(results["1_day"]["value"],
                     f"Day 1<br>{results['1_day']['date']}")
        st.markdown("</div>", unsafe_allow_html=True)

with col2:
    with st.container():
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        create_gauge(results["2_day"]["value"],
                     f"Day 2<br>{results['2_day']['date']}")
        st.markdown("</div>", unsafe_allow_html=True)

with col3:
    with st.container():
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        create_gauge(results["3_day"]["value"],
                     f"Day 3<br>{results['3_day']['date']}")
        st.markdown("</div>", unsafe_allow_html=True)

# ==========================================================
# TREND CHART
# ==========================================================

st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)
st.markdown("## 📈 Forecast Trend")

forecast_dates = [
    results["1_day"]["date"],
    results["2_day"]["date"],
    results["3_day"]["date"]
]

forecast_values = [
    results["1_day"]["value"],
    results["2_day"]["value"],
    results["3_day"]["value"]
]

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=forecast_dates,
    y=forecast_values,
    mode='lines+markers',
    line=dict(color="#00c3ff", width=4),
    marker=dict(size=12, color="#00c3ff", symbol="circle"),
    name="AQI Forecast",
    fill='tozeroy',
    fillcolor='rgba(0, 195, 255, 0.1)'
))

# Add horizontal lines for AQI categories
fig.add_hline(y=50, line_dash="dash", line_color="#00ff88", opacity=0.5, annotation_text="Good")
fig.add_hline(y=100, line_dash="dash", line_color="#ffee00", opacity=0.5, annotation_text="Moderate")
fig.add_hline(y=150, line_dash="dash", line_color="#ff9900", opacity=0.5, annotation_text="Unhealthy")
fig.add_hline(y=200, line_dash="dash", line_color="#ff3333", opacity=0.5, annotation_text="Hazardous")

fig.update_layout(
    height=450,
    template="plotly_dark",
    xaxis_title="Date",
    yaxis_title="AQI Value",
    paper_bgcolor="#0e1117",
    plot_bgcolor="rgba(255, 255, 255, 0.02)",
    hovermode="x unified",
    legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01
    )
)

st.plotly_chart(fig, use_container_width=True)

# ==========================================================
# HEALTH ADVISORY
# ==========================================================

st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)
st.markdown("## 🚨 Health Advisory")

max_aqi = max(forecast_values)
category, _ = aqi_category(max_aqi)

col1, col2 = st.columns([1, 2])

with col1:
    st.metric("Peak AQI Forecast", f"{max_aqi}", delta=f"{category}")

with col2:
    if max_aqi > 200:
        st.error("🔴 **Hazardous** - Avoid all outdoor exposure. Stay indoors with air purifiers.")
    elif max_aqi > 150:
        st.warning("🟠 **Unhealthy** - Limit outdoor activity. Sensitive groups should stay indoors.")
    elif max_aqi > 100:
        st.info("🟡 **Moderate** - Sensitive groups should limit prolonged outdoor exposure.")
    else:
        st.success("🟢 **Good** - Air quality is satisfactory. Enjoy outdoor activities!")

# ==========================================================
# BEST PRODUCTION MODEL
# ==========================================================

st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)
st.markdown("## 🏆 Best Production Model")

best_model_data = fetch_data(BEST_MODEL_URL)

if best_model_data and "model" in best_model_data:
    best_model = best_model_data["model"]
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
            <div class="metric-box">
                <div class="metric-label">Model Name</div>
                <div style="font-size: 20px; font-weight: 600; color: #60a5fa;">{}</div>
            </div>
        """.format(best_model.get("model_name", "N/A")), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="metric-box">
                <div class="metric-label">RMSE</div>
                <div class="metric-value">{}</div>
            </div>
        """.format(round(best_model.get("rmse", 0), 2)), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div class="metric-box">
                <div class="metric-label">R² Score</div>
                <div class="metric-value">{}</div>
            </div>
        """.format(round(best_model.get("r2", 0), 3)), unsafe_allow_html=True)
    
    with col4:
        r2 = best_model.get("r2", 0)
        if r2 > 0.8:
            status = "✅ Strong"
            color = "#00ff88"
        elif r2 > 0.6:
            status = "⚠️ Moderate"
            color = "#ff9900"
        else:
            status = "❌ Needs Improvement"
            color = "#ff3333"
        
        st.markdown("""
            <div class="metric-box">
                <div class="metric-label">Performance</div>
                <div style="font-size: 20px; font-weight: 600; color: {};">{}</div>
            </div>
        """.format(color, status), unsafe_allow_html=True)

else:
    st.warning("⚠️ Best model details unavailable.")

# ==========================================================
# FEATURE IMPORTANCE
# ==========================================================

st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)
st.markdown("## 📊 Top Feature Importance")

feature_data = fetch_data(FEATURE_URL)

if feature_data and "features" in feature_data:
    df = pd.DataFrame(feature_data["features"])
    df = df.sort_values("importance", ascending=False).head(10)

    fig = go.Figure()

    # Use gradient colors
    colors = ['#00c3ff' if i < 3 else '#60a5fa' if i < 6 else '#94a3b8' for i in range(len(df))]
    
    fig.add_trace(go.Bar(
        x=df["importance"],
        y=df["feature"],
        orientation="h",
        marker_color=colors,
        text=df["importance"].round(3),
        textposition="outside",
        textfont=dict(color="white")
    ))

    fig.update_layout(
        title="Top 10 Features Affecting AQI",
        template="plotly_dark",
        height=500,
        yaxis=dict(autorange="reversed", title="Feature"),
        xaxis=dict(title="Importance Score"),
        paper_bgcolor="#0e1117",
        plot_bgcolor="rgba(255, 255, 255, 0.02)",
        margin=dict(l=20, r=20, t=50, b=20)
    )

    st.plotly_chart(fig, use_container_width=True)
    
    # Add explanation
    st.info("📌 **Insight:** Features with higher importance scores have greater influence on AQI predictions. Lag features and weather variables are typically the strongest predictors.")

else:
    st.warning("⚠️ Feature importance unavailable.")

# ==========================================================
# FOOTER
# ==========================================================

st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)

st.markdown("""
    <div class="footer">
        <p style="font-size: 16px;">
            🌍 <strong>Karachi AQI Forecast System</strong>
        </p>
        <p>
            Built with ❤️ by <strong style="color: #60a5fa;">Muhammad Aamir</strong> • Cohort 9
        </p>
        <p style="font-size: 13px; color: #475569;">
            🚀 10 Pearls Shine Intern | AI-Powered MLOps Pipeline
        </p>
        <p style="font-size: 12px; color: #334155; margin-top: 10px;">
            © 2024 All Rights Reserved
        </p>
    </div>
""", unsafe_allow_html=True)