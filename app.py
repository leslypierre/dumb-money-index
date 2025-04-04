import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import os
from datetime import datetime

# 🌙 Thème matplotlib dark
plt.rcParams['axes.facecolor'] = '#0e1117'
plt.rcParams['figure.facecolor'] = '#0e1117'
plt.rcParams['savefig.facecolor'] = '#0e1117'
plt.rcParams['text.color'] = 'white'
plt.rcParams['xtick.color'] = 'white'
plt.rcParams['ytick.color'] = 'white'
plt.rcParams['axes.labelcolor'] = 'white'
plt.rcParams['legend.labelcolor'] = 'white'

# 📁 Dossier où sont stockés les CSV
DATA_DIR = "data_sentiment"

st.set_page_config(page_title="Terminal", layout="wide")

# 🗂️ Onglets principaux
tab_main, tab_secondary = st.tabs(["DMX", "Economic calendar"])

PAIRS = [
    "AUDCAD", "AUDCHF", "AUDJPY", "AUDNZD", "AUDUSD",
    "CADCHF", "CADJPY", "CHFJPY",
    "EURAUD", "EURCAD", "EURCHF", "EURGBP", "EURJPY", "EURNZD", "EURUSD",
    "GBPAUD", "GBPCAD", "GBPCHF", "GBPJPY", "GBPNZD", "GBPUSD",
    "NZDCAD", "NZDCHF", "NZDJPY", "NZDUSD",
    "USDCAD", "USDCHF", "USDJPY"
]
pairs = sorted(PAIRS)

with tab_main :
    # 🖥️ Setup Streamlit
    st.markdown("""
    <h1 style='text-align: center;'>
        <span style='color: white;'>Dumb Money Index </span>
        <span style='color: orange;'>[DXM]</span>
    </h1>
    """, unsafe_allow_html=True)

    selected_pair = st.selectbox("Choisir une paire :", pairs)
    csv_url = f"https://raw.githubusercontent.com/leslypierre/dumb-money-index/main/data_sentiment/{selected_pair}_sentiment.csv"

    try:
        df = pd.read_csv(csv_url)
    except FileNotFoundError:
        st.warning("Aucune donnée trouvée pour cette paire.")
        st.stop()

    # 🔍 Dernier point de données
    latest = df[df["timestamp"] == df["timestamp"].max()]
    long_pct = latest["long_pct"].values[0]
    short_pct = latest["short_pct"].values[0]

    # ℹ️ Info date dernière mise à jour
    last_update = pd.to_datetime(latest["timestamp"].values[0])
    formatted_update = last_update.strftime("%Y-%m-%d %H:%M")
    st.caption(f"📅 Dernière mise à jour : {formatted_update}")

    # 📊 Display graphique
    col1, col2, col3, col4 = st.columns([1.8, 2, 2, 2])

    # 🍩 Donut Chart
    with col1:
        donut_fig = go.Figure(data=[go.Pie(
            labels=["Long", "Short"],
            values=[long_pct, short_pct],
            hole=0.6,
            marker=dict(colors=["#00c49f", "#ff004d"]),
            textinfo='percent+label',
            textposition='outside',
            textfont=dict(color='white', size=12),
            pull=[0, 0.05],
            automargin=True  # ✅ Pour forcer l'espace autour
        )])

        donut_fig.update_layout(
            showlegend=False,
            width=250,
            height=250,
            margin=dict(t=30, b=30, l=30, r=30),  # ✅ Ajout de marges plus grandes
            paper_bgcolor="#0e1117",
            plot_bgcolor="#0e1117"
        )

        st.markdown(f"""
        <h3  style='font-size:18px;'>
            <span style='color: white;'>DMX </span>
            <span style='color: orange;'>[{selected_pair} — Percentage Chart]</span>
        </h3>
        """, unsafe_allow_html=True)

        st.plotly_chart(donut_fig, use_container_width=True)

    # 📈 Bar Chart (avec ligne 0 et symétrie)
    with col2:
        df_plot = df.tail(50).copy()
        df_plot["day"] = df_plot["timestamp"].str[:10]
        df_plot["time"] = df_plot["timestamp"].str[11:]
        df_plot["label"] = pd.to_datetime(df_plot["timestamp"]).dt.strftime("%m-%d %H:%M")

        df_plot["long_pct"] = df_plot["long_pct"].clip(upper=100)
        df_plot["short_pct"] = df_plot["short_pct"].clip(upper=100)
        df_plot["total"] = df_plot["long_pct"] + df_plot["short_pct"]
        df_plot.loc[df_plot["total"] > 100, "long_pct"] = 100 - df_plot["short_pct"]

        fig = go.Figure()

        # Shorts en négatif (sous 0)
        fig.add_trace(go.Bar(
            x=df_plot["label"],
            y=-df_plot["short_pct"],
            name="Short",
            marker_color="#ff004d",
            hovertemplate="%{x}<br>%{y}% Short<extra></extra>"
        ))

        # Longs en positif
        fig.add_trace(go.Bar(
            x=df_plot["label"],
            y=df_plot["long_pct"],
            name="Long",
            marker_color="#00c49f",
            hovertemplate="%{x}<br>%{y}% Long<extra></extra>",
        ))

        fig.update_layout(
            xaxis=dict(
                type='category',  # Obligatoire pour traiter les labels comme des catégories
                tickmode='array',
                tickvals=df_plot["label"][::6],
                ticktext=df_plot["label"][::6],
                tickangle=45  # Incline un peu pour éviter chevauchement
            ),
            shapes=[
                dict(
                    type="line",
                    xref="paper",
                    x0=0,
                    x1=1,
                    yref="y",
                    y0=0,
                    y1=0,
                    line=dict(color="orange", width=2, dash="solid")
                )
            ],
            barmode='relative',
            bargap=0.05,  # Ajuste l'espacement entre les barres
            bargroupgap=0.0,  # Aucun espace entre les groupes de barres
            plot_bgcolor="#0e1117",
            paper_bgcolor="#0e1117",
            font=dict(color='white'),
            margin=dict(l=10, r=10, t=30, b=60),
            height=300,
            showlegend=False
        )

        st.markdown(f"""
                <h3  style='font-size:18px;'>
                    <span style='color: white;'>DMX </span>
                    <span style='color: orange;'>[{selected_pair} — Bar Chart (4h)]</span>
                </h3>
                """, unsafe_allow_html=True)

        st.plotly_chart(fig, use_container_width=True)

    with col3:
        lots_plot = df.tail(50).copy()
        lots_plot["label"] = lots_plot["timestamp"].str[5:16]  # format "MM-DD HH:MM"

        fig_lots = go.Figure()
        fig_lots.add_trace(go.Scatter(
            x=lots_plot["label"],
            y=lots_plot["long_lots"],
            mode="lines+markers",
            name="Long",
            line=dict(color="#00c49f"),
            fill='tozeroy',
            hovertemplate="%{x}<br>%{y} Lots Long<extra></extra>"
        ))

        fig_lots.add_trace(go.Scatter(
            x=lots_plot["label"],
            y=lots_plot["short_lots"],
            mode="lines+markers",
            name="Short",
            line=dict(color="#ff004d"),
            fill='tozeroy',
            hovertemplate="%{x}<br>%{y} Lots Short<extra></extra>"
        ))

        fig_lots.update_layout(
            xaxis=dict(
                type='category',
                tickmode='array',
                tickvals=lots_plot["label"][::6],
                ticktext=lots_plot["label"][::6],
                tickangle=45
            ),
            paper_bgcolor="#0e1117",
            plot_bgcolor="#0e1117",
            font=dict(color='white'),
            margin=dict(t=40, b=40, l=20, r=20),
            height=300,
            showlegend=True,
            legend=dict(orientation="h", y=1.1, x=0)
        )

        st.markdown(f"""
            <h3  style='font-size:18px;'>
                <span style='color: white;'>DMX </span>
                <span style='color: orange;'>[{selected_pair} — Lots Chart]</span>
            </h3>
            """, unsafe_allow_html=True)
        st.plotly_chart(fig_lots, use_container_width=True)

    with col4:
        pos_plot = df.tail(50).copy()
        pos_plot["label"] = pos_plot["timestamp"].str[5:16]

        fig_pos = go.Figure()
        fig_pos.add_trace(go.Scatter(
            x=pos_plot["label"],
            y=pos_plot["long_pos"],
            mode="lines+markers",
            name="Long",
            line=dict(color="#00c49f"),
            fill='tozeroy',
            hovertemplate="%{x}<br>%{y} Positions Long<extra></extra>"
        ))

        fig_pos.add_trace(go.Scatter(
            x=pos_plot["label"],
            y=pos_plot["short_pos"],
            mode="lines+markers",
            name="Short",
            line=dict(color="#ff004d"),
            fill='tozeroy',
            hovertemplate="%{x}<br>%{y} Positions Short<extra></extra>"
        ))

        fig_pos.update_layout(
            xaxis=dict(
                type='category',
                tickmode='array',
                tickvals=pos_plot["label"][::6],
                ticktext=pos_plot["label"][::6],
                tickangle=45
            ),
            paper_bgcolor="#0e1117",
            plot_bgcolor="#0e1117",
            font=dict(color='white'),
            margin=dict(t=40, b=40, l=20, r=20),
            height=300,
            showlegend=True,
            legend=dict(orientation="h", y=1.1, x=0)
        )

        st.markdown(f"""
            <h3  style='font-size:18px;'>
                <span style='color: white;'>DMX </span>
                <span style='color: orange;'>[{selected_pair} — Positions Chart]</span>
            </h3>
            """, unsafe_allow_html=True)
        st.plotly_chart(fig_pos, use_container_width=True)
