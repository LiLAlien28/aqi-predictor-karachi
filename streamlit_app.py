"""
Karachi AQI Forecast — Production Dashboard
Author: Muhammad Aamir | 10 Pearls Shine Internship, Cohort 9

A multi-horizon Air Quality Index forecasting dashboard with model
transparency (metrics, feature importance, SHAP explainability) built
on top of a FastAPI + MongoDB inference backend.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import requests
from datetime import datetime

# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="Karachi AQI Forecast | Muhammad Aamir",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==========================================================
# CONSTANTS
# ==========================================================

BASE_URL = "https://aqi-predictor-karachi-production.up.railway.app"
FORECAST_URL = f"{BASE_URL}/forecast"
BEST_MODEL_URL = f"{BASE_URL}/models/best"
METRICS_URL = f"{BASE_URL}/models/metrics"
FEATURE_URL = f"{BASE_URL}/features/importance?horizon=1"
SHAP_URL = f"{BASE_URL}/forecast/shap"

AQI_BANDS = [
    (0, 50, "Good", "#00e396", "Air quality is satisfactory; minimal risk."),
    (51, 100, "Moderate", "#ffd54f", "Acceptable, but sensitive individuals should watch prolonged exposure."),
    (101, 150, "Unhealthy (Sensitive Groups)", "#ff9f43", "Sensitive groups may experience health effects."),
    (151, 200, "Unhealthy", "#ff6b6b", "Everyone may begin to experience health effects."),
    (201, 300, "Very Unhealthy", "#c44dff", "Health alert — everyone may experience more serious effects."),
    (301, 500, "Hazardous", "#8b0000", "Health warning of emergency conditions."),
]

# ==========================================================
# THEME / CSS
# ==========================================================

st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

        html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

        .stApp {
            background: radial-gradient(circle at top left, #131a2b 0%, #0a0e17 55%, #05070c 100%);
            color: #e8ecf3;
        }

        section[data-testid="stSidebar"] {
            background: rgba(10, 14, 23, 0.96);
            border-right: 1px solid rgba(255,255,255,0.06);
        }

        h1, h2, h3, h4 { color: #f4f6fb !important; font-weight: 700 !important; letter-spacing: -0.01em; }

        p, span, label, .stMarkdown { color: #c3c9d6; }

        .card {
            background: rgba(255,255,255,0.035);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 18px;
            padding: 22px 24px;
            margin: 8px 0;
            box-shadow: 0 10px 30px rgba(0,0,0,0.35);
        }

        .badge {
            padding: 5px 14px;
            border-radius: 999px;
            font-size: 12.5px;
            font-weight: 700;
            display: inline-block;
            letter-spacing: 0.02em;
        }

        .metric-box {
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 14px;
            padding: 18px;
            text-align: center;
            height: 100%;
        }
        .metric-value { font-size: 30px; font-weight: 800; color: #6dd3ff; }
        .metric-label { color: #8b93a7; font-size: 12.5px; text-transform: uppercase; letter-spacing: 0.06em; margin-top: 2px; }

        .section-tag {
            display: inline-block;
            background: rgba(109, 211, 255, 0.12);
            color: #6dd3ff;
            border: 1px solid rgba(109, 211, 255, 0.25);
            border-radius: 8px;
            padding: 3px 10px;
            font-size: 11.5px;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            margin-bottom: 6px;
        }

        .divider {
            border: none;
            height: 1px;
            background: linear-gradient(to right, transparent, rgba(255,255,255,0.12), transparent);
            margin: 34px 0 26px 0;
        }

        .footer {
            text-align: center;
            color: #5b6478;
            padding: 30px 0 12px 0;
            border-top: 1px solid rgba(255,255,255,0.06);
            margin-top: 34px;
            font-size: 13px;
        }
        .footer a { color: #6dd3ff; text-decoration: none; font-weight: 600; }
        .footer a:hover { text-decoration: underline; }

        .stButton > button {
            border-radius: 9px;
            font-weight: 600;
            border: 1px solid rgba(255,255,255,0.12);
        }

        .shap-pos { color: #ff6b6b; font-weight: 700; font-family: 'JetBrains Mono', monospace; }
        .shap-neg { color: #43e6a0; font-weight: 700; font-family: 'JetBrains Mono', monospace; }

        .sidebar-author {
            text-align: center;
            padding: 14px 0 4px 0;
            border-top: 1px solid rgba(255,255,255,0.06);
            margin-top: 18px;
        }
        .sidebar-author .name { color: #6dd3ff; font-weight: 700; font-size: 15px; }
        .sidebar-author .cohort { color: #8b93a7; font-size: 12px; }
    </style>
""", unsafe_allow_html=True)

# ==========================================================
# HELPERS
# ==========================================================

@st.cache_data(ttl=300, show_spinner=False)
def fetch_json(url: str, timeout: int = 30):
    """GET a URL and return parsed JSON, or None on any failure."""
    try:
        resp = requests.get(url, timeout=timeout)
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return None


def aqi_band(value: float):
    for lo, hi, label, color, note in AQI_BANDS:
        if lo <= value <= hi:
            return label, color, note
    return "Hazardous", "#8b0000", AQI_BANDS[-1][4]


def render_gauge(value, title_html):
    label, color, _ = aqi_band(value)
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        number={'font': {'size': 40, 'color': color}},
        title={'text': title_html, 'font': {'size': 15, 'color': '#c3c9d6'}},
        gauge={
            'axis': {'range': [0, 300], 'tickcolor': '#5b6478', 'tickfont': {'color': '#8b93a7'}},
            'bar': {'color': color, 'thickness': 0.28},
            'bgcolor': 'rgba(255,255,255,0.02)',
            'borderwidth': 0,
            'steps': [
                {'range': [0, 50], 'color': 'rgba(0,227,150,0.12)'},
                {'range': [50, 100], 'color': 'rgba(255,213,79,0.12)'},
                {'range': [100, 150], 'color': 'rgba(255,159,67,0.12)'},
                {'range': [150, 200], 'color': 'rgba(255,107,107,0.12)'},
                {'range': [200, 300], 'color': 'rgba(196,77,255,0.12)'},
            ],
        }
    ))
    fig.update_layout(
        height=290,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#e8ecf3",
        margin=dict(l=20, r=20, t=60, b=10),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.markdown(
        f"<div style='text-align:center;margin-top:-10px;'>"
        f"<span class='badge' style='background:{color}22;color:{color};border:1px solid {color}55;'>{label}</span>"
        f"</div>",
        unsafe_allow_html=True,
    )


def normalize_shap_response(raw):
    """
    Backend SHAP payloads can vary in shape across iterations of the API.
    This normalizes several plausible shapes into a single DataFrame with
    columns: feature, shap_value, feature_value (optional).
    Returns (df, base_value) or (None, None) if it can't be parsed.
    """
    if not raw:
        return None, None

    base_value = raw.get("base_value") or raw.get("expected_value") or raw.get("base") or 0

    candidates = None
    for key in ("shap_values", "features", "explanation", "contributions"):
        if key in raw and isinstance(raw[key], list):
            candidates = raw[key]
            break

    if candidates is None:
        return None, None

    rows = []
    for item in candidates:
        if isinstance(item, dict):
            name = item.get("feature") or item.get("name")
            val = item.get("shap_value") or item.get("value") or item.get("importance")
            fval = item.get("feature_value") if "feature_value" in item else item.get("input_value")
            if name is not None and val is not None:
                rows.append({"feature": name, "shap_value": float(val), "feature_value": fval})

    if not rows:
        return None, None

    df = pd.DataFrame(rows)
    return df, base_value


# ==========================================================
# SIDEBAR
# ==========================================================

with st.sidebar:
    st.markdown("""
        <div style="text-align:center; padding: 18px 0 8px 0;">
            <div style="font-size:44px;">🌍</div>
            <h2 style="margin:8px 0 2px 0;">Karachi AQI</h2>
            <p style="color:#8b93a7; font-size:13.5px; margin:0;">Multi-Horizon Forecast System</p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr class='divider' style='margin:16px 0;'>", unsafe_allow_html=True)

    st.markdown("##### 📊 System Status")
    status_ping = fetch_json(f"{BASE_URL}/")
    if status_ping is not None:
        st.markdown(
            "<div style='display:flex;align-items:center;gap:8px;'>"
            "<span style='width:9px;height:9px;border-radius:50%;background:#00e396;display:inline-block;'></span>"
            "<span style='color:#8b93a7;font-size:13.5px;'>API Operational</span></div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            "<div style='display:flex;align-items:center;gap:8px;'>"
            "<span style='width:9px;height:9px;border-radius:50%;background:#ff6b6b;display:inline-block;'></span>"
            "<span style='color:#8b93a7;font-size:13.5px;'>API Unreachable</span></div>",
            unsafe_allow_html=True,
        )

    st.markdown("<hr class='divider' style='margin:16px 0;'>", unsafe_allow_html=True)

    st.markdown("##### ⚙️ Dashboard Sections")
    st.markdown("""
    - 📅 3-day AQI forecast
    - 📈 Forecast trend & health advisory
    - 🏆 Production model benchmark
    - 📊 Global feature importance
    - 🔍 SHAP prediction explainability
    """)

    st.markdown("<hr class='divider' style='margin:16px 0;'>", unsafe_allow_html=True)

    if st.button("🔄 Refresh data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.markdown("""
        <div class="sidebar-author">
            <div class="name">👨‍💻 Muhammad Aamir</div>
            <div class="cohort">10 Pearls Shine · Cohort 9</div>
        </div>
    """, unsafe_allow_html=True)

# ==========================================================
# HEADER
# ==========================================================

st.markdown("""
    <div style="padding: 18px 0 6px 0;">
        <h1 style="font-size: 44px; margin:0;">🌍 Karachi AQI Forecast</h1>
        <p style="color:#8b93a7; font-size:17px; margin:6px 0 0 0;">
            Multi-horizon air quality prediction with model transparency and SHAP explainability
        </p>
        <p style="color:#5b6478; font-size:13.5px; margin-top:4px;">
            Muhammad Aamir · 10 Pearls Shine Internship · Cohort 9
        </p>
    </div>
""", unsafe_allow_html=True)

st.markdown("<hr class='divider'>", unsafe_allow_html=True)

# ==========================================================
# FETCH FORECAST (required — stop if unavailable)
# ==========================================================

with st.spinner("Connecting to inference backend..."):
    results = fetch_json(FORECAST_URL)

if results is None:
    st.error(
        "🚨 **Backend unavailable.** The FastAPI inference service on Railway did not "
        "respond. This can happen on cold start — please retry in a few seconds."
    )
    if st.button("🔄 Retry Connection"):
        st.cache_data.clear()
        st.rerun()
    st.stop()

try:
    forecast_dates = [results["1_day"]["date"], results["2_day"]["date"], results["3_day"]["date"]]
    forecast_values = [results["1_day"]["value"], results["2_day"]["value"], results["3_day"]["value"]]
except (KeyError, TypeError):
    st.error("🚨 Forecast payload from the backend was in an unexpected format.")
    st.json(results)
    st.stop()

# ==========================================================
# FORECAST GAUGES
# ==========================================================

st.markdown("<span class='section-tag'>Forecast</span>", unsafe_allow_html=True)
st.markdown("## 📅 3-Day AQI Outlook")

cols = st.columns(3)
for i, col in enumerate(cols):
    with col:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        render_gauge(forecast_values[i], f"Day {i+1} · {forecast_dates[i]}")
        st.markdown("</div>", unsafe_allow_html=True)

# ==========================================================
# TREND CHART
# ==========================================================

st.markdown("<hr class='divider'>", unsafe_allow_html=True)
st.markdown("<span class='section-tag'>Trend</span>", unsafe_allow_html=True)
st.markdown("## 📈 Forecast Trajectory")

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=forecast_dates, y=forecast_values,
    mode='lines+markers',
    line=dict(color="#6dd3ff", width=4),
    marker=dict(size=13, color="#6dd3ff", line=dict(color="#0a0e17", width=2)),
    name="AQI Forecast",
    fill='tozeroy',
    fillcolor='rgba(109, 211, 255, 0.08)',
))
for lo, hi, label, color, _ in AQI_BANDS[:5]:
    fig.add_hline(y=hi, line_dash="dot", line_color=color, opacity=0.45,
                   annotation_text=label, annotation_font_color=color, annotation_font_size=11)

fig.update_layout(
    height=430,
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(255,255,255,0.015)",
    font_color="#e8ecf3",
    xaxis_title="Date", yaxis_title="AQI",
    hovermode="x unified",
    legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
    xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
    yaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
)
st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

# ---- Health advisory ----
st.markdown("<hr class='divider'>", unsafe_allow_html=True)
st.markdown("<span class='section-tag'>Advisory</span>", unsafe_allow_html=True)
st.markdown("## 🚨 Health Advisory")

max_aqi = max(forecast_values)
label, color, note = aqi_band(max_aqi)

adv1, adv2 = st.columns([1, 2])
with adv1:
    st.markdown(f"""
        <div class="metric-box">
            <div class="metric-label">Peak AQI (3-day)</div>
            <div class="metric-value" style="color:{color};">{max_aqi:.0f}</div>
            <div style="margin-top:8px;"><span class='badge' style='background:{color}22;color:{color};border:1px solid {color}55;'>{label}</span></div>
        </div>
    """, unsafe_allow_html=True)
with adv2:
    st.markdown(f"""
        <div class="card" style="border-left: 4px solid {color};">
            <strong style="color:{color};">{label}</strong> — {note}
        </div>
    """, unsafe_allow_html=True)

# ==========================================================
# BEST PRODUCTION MODEL
# ==========================================================

st.markdown("<hr class='divider'>", unsafe_allow_html=True)
st.markdown("<span class='section-tag'>Model</span>", unsafe_allow_html=True)
st.markdown("## 🏆 Production Model")

best_model_data = fetch_json(BEST_MODEL_URL)

if best_model_data and "model" in best_model_data:
    best_model = best_model_data["model"]
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(f"""
            <div class="metric-box">
                <div class="metric-label">Model</div>
                <div style="font-size:19px; font-weight:700; color:#6dd3ff; margin-top:4px;">{best_model.get("model_name", "N/A")}</div>
            </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
            <div class="metric-box">
                <div class="metric-label">RMSE</div>
                <div class="metric-value">{round(best_model.get("rmse", 0), 2)}</div>
            </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
            <div class="metric-box">
                <div class="metric-label">R² Score</div>
                <div class="metric-value">{round(best_model.get("r2", 0), 3)}</div>
            </div>""", unsafe_allow_html=True)
    with c4:
        r2 = best_model.get("r2", 0)
        if r2 > 0.8:
            status, scolor = "✅ Strong Fit", "#00e396"
        elif r2 > 0.6:
            status, scolor = "⚠️ Moderate Fit", "#ffd54f"
        else:
            status, scolor = "❌ Needs Work", "#ff6b6b"
        st.markdown(f"""
            <div class="metric-box">
                <div class="metric-label">Performance</div>
                <div style="font-size:18px; font-weight:700; color:{scolor}; margin-top:4px;">{status}</div>
            </div>""", unsafe_allow_html=True)
else:
    st.warning("⚠️ Best model details unavailable from the registry.")

# ---- Model benchmark across horizons (from README-documented metrics endpoint) ----
metrics_data = fetch_json(METRICS_URL)
if metrics_data:
    rows = metrics_data.get("models") or metrics_data.get("metrics") or (metrics_data if isinstance(metrics_data, list) else None)
    if rows:
        with st.expander("📋 View full model benchmark across horizons"):
            df_metrics = pd.DataFrame(rows)
            st.dataframe(df_metrics, use_container_width=True, hide_index=True)

# ==========================================================
# FEATURE IMPORTANCE
# ==========================================================

st.markdown("<hr class='divider'>", unsafe_allow_html=True)
st.markdown("<span class='section-tag'>Interpretability</span>", unsafe_allow_html=True)
st.markdown("## 📊 Global Feature Importance")
st.caption("Which features the production model relies on most, aggregated across all predictions (e.g. Gini / permutation importance).")

feature_data = fetch_json(FEATURE_URL)

if feature_data and "features" in feature_data:
    df_feat = pd.DataFrame(feature_data["features"])
    df_feat = df_feat.sort_values("importance", ascending=False).head(12)

    colors = ["#6dd3ff" if i < 3 else "#4f8fd4" if i < 6 else "#5b6478" for i in range(len(df_feat))]

    fig_imp = go.Figure(go.Bar(
        x=df_feat["importance"], y=df_feat["feature"],
        orientation="h", marker_color=colors,
        text=df_feat["importance"].round(3), textposition="outside",
        textfont=dict(color="#c3c9d6"),
    ))
    fig_imp.update_layout(
        height=460,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(255,255,255,0.015)",
        font_color="#e8ecf3",
        yaxis=dict(autorange="reversed", title=None, gridcolor="rgba(255,255,255,0.05)"),
        xaxis=dict(title="Importance Score", gridcolor="rgba(255,255,255,0.05)"),
        margin=dict(l=10, r=40, t=20, b=20),
    )
    st.plotly_chart(fig_imp, use_container_width=True, config={"displayModeBar": False})

    top3 = ", ".join(df_feat["feature"].head(3).tolist())
    st.info(f"📌 **Insight:** The strongest predictors are **{top3}** — consistent with lag and rolling-window features carrying most of the temporal signal, as noted in the EDA.")
else:
    st.warning("⚠️ Feature importance unavailable from the backend.")

# ==========================================================
# SHAP EXPLAINABILITY
# ==========================================================

st.markdown("<hr class='divider'>", unsafe_allow_html=True)
st.markdown("<span class='section-tag'>Explainability</span>", unsafe_allow_html=True)
st.markdown("## 🔍 SHAP: Why This Prediction?")
st.caption(
    "SHAP (SHapley Additive exPlanations) breaks the current 1-day forecast down into "
    "per-feature contributions — showing exactly how much each input pushed the prediction "
    "above or below the model's baseline (average) output."
)

shap_raw = fetch_json(SHAP_URL)
df_shap, base_value = normalize_shap_response(shap_raw)

if df_shap is not None and not df_shap.empty:
    df_shap["abs_val"] = df_shap["shap_value"].abs()
    df_shap = df_shap.sort_values("abs_val", ascending=True).tail(12)

    bar_colors = ["#ff6b6b" if v > 0 else "#43e6a0" for v in df_shap["shap_value"]]

    fig_shap = go.Figure(go.Bar(
        x=df_shap["shap_value"], y=df_shap["feature"],
        orientation="h", marker_color=bar_colors,
        text=df_shap["shap_value"].round(3), textposition="outside",
        textfont=dict(color="#c3c9d6"),
    ))
    fig_shap.add_vline(x=0, line_color="rgba(255,255,255,0.25)", line_width=1)
    fig_shap.update_layout(
        height=460,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(255,255,255,0.015)",
        font_color="#e8ecf3",
        yaxis=dict(title=None, gridcolor="rgba(255,255,255,0.05)"),
        xaxis=dict(title="SHAP value (impact on predicted AQI)", gridcolor="rgba(255,255,255,0.05)"),
        margin=dict(l=10, r=40, t=20, b=20),
        title=dict(text=f"Base value: {round(float(base_value), 2) if base_value else 'N/A'}  →  Predicted AQI: {forecast_values[0]:.0f}",
                    font=dict(size=13, color="#8b93a7")),
    )
    st.plotly_chart(fig_shap, use_container_width=True, config={"displayModeBar": False})

    top_pos = df_shap.sort_values("shap_value", ascending=False).head(1)
    top_neg = df_shap.sort_values("shap_value", ascending=True).head(1)
    leg1, leg2 = st.columns(2)
    with leg1:
        if not top_pos.empty and top_pos["shap_value"].iloc[0] > 0:
            st.markdown(f"<span class='shap-pos'>▲ {top_pos['feature'].iloc[0]}</span> pushed AQI **up** the most (+{top_pos['shap_value'].iloc[0]:.2f})", unsafe_allow_html=True)
    with leg2:
        if not top_neg.empty and top_neg["shap_value"].iloc[0] < 0:
            st.markdown(f"<span class='shap-neg'>▼ {top_neg['feature'].iloc[0]}</span> pushed AQI **down** the most ({top_neg['shap_value'].iloc[0]:.2f})", unsafe_allow_html=True)

    with st.expander("📄 Raw SHAP contribution table"):
        st.dataframe(
            df_shap[["feature", "shap_value"] + (["feature_value"] if "feature_value" in df_shap.columns else [])]
            .sort_values("shap_value", ascending=False),
            use_container_width=True, hide_index=True,
        )
else:
    st.warning(
        "⚠️ SHAP explanation is currently unavailable from `/forecast/shap`. "
        "The panel will populate automatically once the endpoint returns data — "
        "falling back to global feature importance above in the meantime."
    )

# ==========================================================
# METHODOLOGY / ABOUT
# ==========================================================

st.markdown("<hr class='divider'>", unsafe_allow_html=True)
st.markdown("<span class='section-tag'>About</span>", unsafe_allow_html=True)
st.markdown("## 🧠 How This System Works")

m1, m2, m3 = st.columns(3)
with m1:
    st.markdown("""
        <div class="card">
            <h4>📥 Data</h4>
            <p style="font-size:14px;">5 months of historical AQI + live weather data (Open-Meteo), aligned hourly and stored in a MongoDB feature store.</p>
        </div>
    """, unsafe_allow_html=True)
with m2:
    st.markdown("""
        <div class="card">
            <h4>🛠️ Features</h4>
            <p style="font-size:14px;">Lag features (t-1, t-3, t-6, t-24, t-48), rolling mean/std, hour-of-day and day-of-week encodings, and weather interactions.</p>
        </div>
    """, unsafe_allow_html=True)
with m3:
    st.markdown("""
        <div class="card">
            <h4>🤖 Modeling</h4>
            <p style="font-size:14px;">Independent models per horizon (24h / 48h / 72h) — Random Forest, Gradient Boosting, Ridge — best model selected by RMSE/R² and served via FastAPI.</p>
        </div>
    """, unsafe_allow_html=True)

# ==========================================================
# FOOTER
# ==========================================================

st.markdown("<hr class='divider'>", unsafe_allow_html=True)
st.markdown(f"""
    <div class="footer">
        <p style="font-size:15px;">🌍 <strong>Karachi AQI Forecast System</strong></p>
        <p>Built by <a href="https://www.linkedin.com/in/moaamir28/" target="_blank">Muhammad Aamir</a> ·
           10 Pearls Shine Internship, Cohort 9 ·
           <a href="https://github.com/LiLAlien28/aqi-predictor-karachi" target="_blank">Source on GitHub</a></p>
        <p style="font-size:12px; color:#3d4457; margin-top:8px;">
            Last refreshed {datetime.now().strftime('%Y-%m-%d %H:%M')} · © 2026
        </p>
    </div>
""", unsafe_allow_html=True)
