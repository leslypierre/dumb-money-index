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
DATA_DIR = "data"

# 🖥️ Setup Streamlit
st.set_page_config(page_title="Dumb Money Index [DXM]", layout="wide")
st.markdown("""
<h1 style='text-align: center;'>
    <span style='color: white;'>Dumb Money Index </span>
    <span style='color: orange;'>[DXM]</span>
</h1>
""", unsafe_allow_html=True)

# 📌 Charger la liste des paires dispo (fichiers CSV)
if not os.path.exists(DATA_DIR):
    st.error("Le dossier 'data/' n'existe pas. Lance le script collect_sentiment.py d'abord.")
    st.stop()

csv_files = [f for f in os.listdir(DATA_DIR) if f.endswith("_sentiment.csv")]
pairs = sorted([f.replace("_sentiment.csv", "") for f in csv_files])

if not pairs:
    st.warning("Aucune paire disponible. Attends que les données soient collectées.")
    st.stop()

selected_pair = st.selectbox("Choisir une paire :", pairs)
csv_url = f"https://raw.githubusercontent.com/leslypierre/dumb-money-index/main/data/{selected_pair}_sentiment.csv"
print(csv_url)
st.write("📎 URL utilisée :", csv_url)  # Debug temporaire

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
st.caption(f"📅 Dernière mise à jour : {latest['timestamp'].values[0]}")

# 📊 Display graphique
col1, col2 = st.columns([1, 2])

# 🍩 Donut Chart
with col1:
    donut_fig = go.Figure(data=[go.Pie(
        labels=["Long", "Short"],
        values=[long_pct, short_pct],
        hole=0.6,
        marker=dict(colors=["#00c49f", "#ff004d"]),
        textinfo="label+percent",
        textcolor='white',
        insidetextorientation='auto',
        hoverinfo="label+percent"
    )])

    donut_fig.update_layout(
        showlegend=False,
        margin=dict(t=20, b=20, l=10, r=10),
        paper_bgcolor="#0e1117",
        plot_bgcolor="#0e1117",
        font=dict(color="white"),
        height=300
    )

    st.markdown(f"""
    <h3>
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
    df_plot["label"] = df_plot["day"] + " " + df_plot["time"]

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
            tickvals=df_plot["label"],
            ticktext=df_plot["label"],
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
        legend=dict(
            bgcolor="#1a1c23",
            bordercolor="white",
            borderwidth=1
        )
    )

    st.markdown(f"""
    <h3>
        <span style='color: white;'>DMX </span>
        <span style='color: orange;'>[{selected_pair} — Bar Chart (1h)]</span>
    </h3>
    """, unsafe_allow_html=True)

    st.plotly_chart(fig, use_container_width=True)

# 🧾 Tableau de données
st.subheader("Données récentes")
st.dataframe(
    df.tail(10).style.set_properties(**{
        'font-size': '12px',
        'text-align': 'center'
    }),
    height=200,
    use_container_width=True
)




