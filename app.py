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
POLICY_DATA_DIR = "policy_data"
st.set_page_config(page_title="Terminal", layout="wide")

# 🗂️ Onglets principaux
tab_main, tab_secondary = st.tabs(["DMX", "Interest rates expectations"])

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
    <h1 style='text-align: center; margin-bottom: 30px'>
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
                tickvals=df_plot["label"][::10],
                ticktext=df_plot["label"][::10],
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
                tickvals=lots_plot["label"][::10],
                ticktext=lots_plot["label"][::10],
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
                tickvals=pos_plot["label"][::10],
                ticktext=pos_plot["label"][::10],
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

# 🔽 Onglet 2 : Interest Rates Expectations
with tab_secondary:
    st.markdown("""
    <h1 style='text-align: center;  margin-bottom: 30px'>
        <span style='color: white;'>Interest Rate </span>
        <span style='color: #01c49f;'>Expectations</span>
    </h1>
    """, unsafe_allow_html=True)

    try:
        df_policy = pd.read_csv(os.path.join(POLICY_DATA_DIR, "central_banks_overview.csv"))
    except FileNotFoundError:
        st.warning("Fichier 'central_banks_overview.csv' non trouvé dans le dossier 'policy_data/'.")
        st.stop()

    # Mapping drapeaux par banque (emoji pour simplifier)
    flags = {
        "FED": "🇺🇸", "ECB": "🇪🇺", "BOE": "🇬🇧", "BOC": "🇨🇦",
        "RBA": "🇦🇺", "RBNZ": "🇳🇿", "SNB": "🇨🇭", "BOJ": "🇯🇵"
    }

    df_policy = df_policy.sort_values(by="Bank")

    # En-têtes de colonnes stylisées
    header_cols = st.columns([2, 1.2, 1.2, 1.2, 1.8, 1.2])
    headers = ["Central Bank", "Next Move", "Change By", "Probability", "Next Meeting", "Current Rate"]
    for col, title in zip(header_cols, headers):
        col.markdown(f"<span style='font-size:14px; font-weight:600; color: gray;'>{title}</span>", unsafe_allow_html=True)

    for _, row in df_policy.iterrows():
        bank = row["Bank"]
        flag = flags.get(bank, "")
        next_move = row['Next move']
        change_by = f"{row['Change by']}%"
        prob = f"{row['Probability']}%"
        meeting = row['Next meeting date']
        rate = f"{float(row['Current rate']):.2f}%"

        # Texte formaté avec padding plus large pour alignement parfait
        label = f"""
```text
{flag} {bank:<30}            {next_move:<17}            {change_by:<18}            {prob:<17}            {meeting:<33}            {rate}
```"""

        with st.expander(label):
            col_left, col_right = st.columns(2)

            # ====== 📊 Graph 1: Probabilité entre les deux issues les plus probables
            with col_left:
                try:
                    # Nettoyage et conversion des valeurs en float
                    rate = float(str(row["Current rate"]).replace("%", ""))
                    change_by = float(str(row["Change by"]).replace("%", ""))
                    other_change = float(str(row["Other change by"]).replace("%", ""))
                    other_prob = float(row['Other probability'])
                    main_prob = float(row['Probability'])

                    # Calcul des taux après changement
                    probable_rate = rate + change_by
                    other_rate = rate + other_change

                    # Libellés pour le graphe
                    next_move = row['Next move']
                    other_move = row['Other move']
                    main_text = f"{next_move} to {probable_rate:.2f}%"
                    other_text = f"{other_move} at {other_rate:.2f}%"

                    # Création du graphique
                    fig = go.Figure()

                    fig.add_trace(go.Bar(
                        x=[main_text],
                        y=[main_prob],
                        name="Most Likely",
                        marker=dict(
                            color='rgba(0, 196, 159, 0.6)',  # ✅ turquoise translucide
                            line=dict(color='rgb(0, 196, 159)', width=1)  # ✅ même couleur mais opaque pour le contour
                        ),
                        text=[f"{main_prob:.2f}%"],
                        textposition='auto',
                        textfont=dict(color="white")
                    ))

                    fig.add_trace(go.Bar(
                        x=[other_text],
                        y=[other_prob],
                        name="Alternative",
                        marker=dict(
                            color='rgba(148, 202, 130, 0.6)',  # ✅ vert translucide
                            line=dict(color='rgb(148, 202, 130)', width=1)  # ✅ même couleur en opaque
                        ),
                        text=[f"{other_prob:.2f}%"],
                        textposition='auto',
                        textfont=dict(color="white")
                    ))

                    fig.update_layout(
                        title="Probability Between Most Probable Outcomes",
                        yaxis=dict(ticksuffix="%", range=[0, 100]),
                        paper_bgcolor="#0e1117",
                        plot_bgcolor="#0e1117",
                        font=dict(color='white'),
                        height=400
                    )

                    st.plotly_chart(fig, use_container_width=True)

                except Exception as e:
                    st.warning(f"Erreur lors du chargement des probabilités alternatives : {e}")

            with col_right:
                stir_path = os.path.join(POLICY_DATA_DIR, f"{bank}_STIR.csv")
                try:
                    df_stir = pd.read_csv(stir_path)
                    df_stir = df_stir.rename(columns={"Week Ago": "A Week Ago", "Now": "Current"})

                    # 🔎 Valeurs dynamiques pour y-axis
                    combined = pd.concat([df_stir["Current"], df_stir["A Week Ago"]])
                    min_val = combined.min()
                    max_val = combined.max()

                    # ⬇️ Petite marge dynamique
                    y_min = max(-0.5, round(min_val - 0.15, 2))
                    y_max = round(max_val + 0.1, 2)

                    fig = go.Figure()

                    # 🟢 A Week Ago Area
                    fig.add_trace(go.Scatter(
                        x=df_stir["Date"],
                        y=df_stir["A Week Ago"],
                        fill='tozeroy',
                        fillcolor='rgba(148, 202, 130, 0.2)',
                        mode='lines+markers',
                        line=dict(color="#a0e49f", width=1),
                        line_shape="spline",
                        name='A Week Ago'
                    ))

                    # 🔵 Current Area
                    fig.add_trace(go.Scatter(
                        x=df_stir["Date"],
                        y=df_stir["Current"],
                        fill='tozeroy',
                        fillcolor='rgba(0, 214, 198, 0.2)',
                        mode='lines+markers',
                        line=dict(color="#00d6c6", width=1),
                        line_shape="spline",
                        name='Current'
                    ))

                    # ✍️ Annotations propres
                    for i in range(len(df_stir)):
                        fig.add_annotation(
                            x=df_stir["Date"][i], y=df_stir["Current"][i],
                            text=f"{df_stir['Current'][i]:.2f}%",
                            showarrow=False, yshift=-12,
                            font=dict(color="white", size=12)
                        )
                        fig.add_annotation(
                            x=df_stir["Date"][i], y=df_stir["A Week Ago"][i],
                            text=f"{df_stir['A Week Ago'][i]:.2f}%",
                            showarrow=False, yshift=12,
                            font=dict(color="white", size=12)
                        )

                    fig.update_layout(
                        title="Implied Interest Rate",
                        yaxis=dict(title="Implied Interest Rate", ticksuffix="%", range=[y_min, y_max]),
                        paper_bgcolor="#0e1117",
                        plot_bgcolor="#0e1117",
                        font=dict(color='white'),
                        height=400,
                        legend=dict(orientation="h", x=0.5, xanchor="center", y=1.1)
                    )

                    st.plotly_chart(fig, use_container_width=True)

                except FileNotFoundError:
                    st.warning(f"Fichier STIR non trouvé pour {bank}.")


