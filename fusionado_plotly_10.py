import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ============================
# ESTILO STREAMLIT
# ============================
st.set_page_config(page_title='Panorama de Energía Eléctrica en México', layout='wide')

# CSS para estilo llamativo
st.markdown("""
<style>
/* Fondo degradado */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
    color: white;
    font-family: 'Segoe UI', sans-serif;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #141e30, #243b55);
    color: white;
}

/* Títulos principales */
h1 {
    text-align: center;
    color: #00FFAA;
    font-size: 52px !important;
    font-weight: bold;
    margin-bottom: 40px;
    text-shadow: 1px 1px 5px black;
}

/* Subtítulos */
h2, h3, h4 {
    text-align: center;
    color: #00FFFF !important;
    font-size: 28px !important;
    margin-bottom: 20px;
}

/* Separadores */
hr {
    border: 0;
    height: 1px;
    background: #555;
    margin: 40px 0;
}

/* Bloques */
.main .block-container {
    padding-top: 15px;
    padding-left: 40px;
    padding-right: 40px;
    padding-bottom: 40px;
}

/* Texto */
a, p, label {
    color: #EEE !important;
    font-size: 16px;
}

/* Botones */
.stButton>button {
    background: linear-gradient(to right, #0072ff, #00c6ff);
    color: white;
    border: none;
    border-radius: 10px;
    padding: 0.6em 1.2em;
    font-weight: bold;
    transition: 0.3s;
}
.stButton>button:hover {
    background: linear-gradient(to right, #00c6ff, #0072ff);
    transform: scale(1.05);
}
</style>
""", unsafe_allow_html=True)


# ============================
# TITULO GENERAL
# ============================
st.markdown("<h1>Panorama de Energía Eléctrica en México</h1>", unsafe_allow_html=True)

# ============================
# CARGA DATOS Y PREPARACIÓN
# ============================
data = pd.read_csv("Consumo de energia electrica por entidad federativa.csv", skiprows=8, index_col=0)
if "Total Nacional (1)" in data.index:
    Total_consumido = data.loc["Total Nacional (1)"]
data = data.iloc[3:-8, :]
data.index.name = "Estado"
cols_numeric = pd.to_numeric(data.columns, errors="coerce")
mask_cols = ~pd.isna(cols_numeric)
df_consumo = data.loc[:, mask_cols].copy()
df_consumo.columns = cols_numeric[mask_cols].astype(int)
years_consumo_anim = df_consumo.columns.astype(str)

gen = pd.read_csv("Generación bruta de energía eléctrica por entidad federativa.csv", skiprows=7, index_col=0)
gen.index.name = "Estado"
gen = gen.iloc[1:30, :]
if "Morelos" in gen.index:
    gen.loc["Morelos"] = gen.loc["Morelos"].fillna(method="ffill")
gen = gen.iloc[:, :-3]
n_years = gen.shape[1] // 12
df_generacion = pd.DataFrame(index=gen.index)
for i in range(n_years):
    block = gen.iloc[:, i*12:(i+1)*12]
    df_generacion[2002 + i] = block.sum(axis=1)
df_generacion.columns = df_generacion.columns.astype(int)

# ============================
# GRAFICAS (1 a 7)
# ============================

# ======================================================
# GRÁFICA 1: ANIMACIÓN CONSUMO 2006–2024
# ======================================================
st.markdown('---')
fig = go.Figure()
year0_str = years_consumo_anim[0]
d0 = df_consumo[int(year0_str)].sort_values(ascending=True)
fig.add_trace(go.Bar(
    x=d0.values, y=d0.index, orientation='h',
    marker=dict(color=d0.values, colorscale="Oranges", line=dict(color="black", width=1.5)),
    name="Consumo"
))
frames = []
for y_str in years_consumo_anim:
    y = int(y_str)
    d = df_consumo[y].sort_values(ascending=True)
    frames.append(go.Frame(
        data=[go.Bar(
            x=d.values, y=d.index, orientation="h",
            marker=dict(color=d.values, colorscale="Oranges", line=dict(color="black", width=1.5)),
            name="Consumo"
        )],
        name=y_str
    ))
fig.frames = frames

fig.update_layout(
    template="plotly_dark",
    plot_bgcolor="black",
    paper_bgcolor="black",
    title=dict(text="Evolución del Consumo Eléctrico por Estado (2006–2024)", x=0.5, xanchor="center", font=dict(size=22, color="white")),
    xaxis_title=dict(text="Consumo (GWh)", font=dict(size=18, color="white")),
    yaxis_title=dict(text="Estado", font=dict(size=18, color="white")),
    yaxis=dict(tickfont=dict(size=12, color="white"), gridcolor="rgba(255,255,255,0.1)"),
    xaxis=dict(gridcolor="rgba(255,255,255,0.1)"),
    height=900, bargap=0.15,
    sliders=[{
        "steps": [{"args": [[y_str], {"frame": {"duration": 500, "redraw": True}, "mode": "immediate","transition": {"duration": 300}}], "label": y_str, "method": "animate"} for y_str in years_consumo_anim],
        "x": 0.1, "y": -0.08, "len": 0.8,
        "currentvalue": {"prefix": "Año: ", "font": {"size": 18, "color": "white"}}
    }],
    updatemenus=[{
        "type": "buttons", "showactive": False, "x": 1.05, "y": 1.15,
        "buttons": [
            {"label": "▶ Play", "method": "animate",
             "args": [None, {"frame": {"duration": 700, "redraw": True}, "fromcurrent": True,"transition": {"duration": 400, "easing": "quadratic-in-out"}}]},
            {"label": "⏸ Pause", "method": "animate",
             "args": [[None], {"frame": {"duration": 0, "redraw": False},"mode": "immediate", "transition": {"duration": 0}}]}
        ]
    }]
)
st.plotly_chart(fig, use_container_width=True)



# ======================================================
# GRÁFICA 2: ANIMACIÓN GENERACIÓN 2002–2024
# ======================================================
# ======================================================
# GRÁFICA 2: ANIMACIÓN GENERACIÓN 2002–2024 (sin fila "Total")
# ======================================================
st.markdown('---')
years_full = list(df_generacion.columns)

# Filtrar filas que contengan "Total"
data_slice_full = df_generacion[~df_generacion.index.str.contains("Total", case=False)].copy()

fig = go.Figure()
year0 = years_full[0]
d0 = data_slice_full[year0].dropna().sort_values(ascending=True)
fig.add_trace(go.Bar(
    x=d0.values, y=d0.index, orientation='h',
    marker=dict(color=d0.values, colorscale="Blues", line=dict(color="black", width=1.5)),
    name="Generación"
))

frames = []
for year in years_full:
    d = data_slice_full[year].dropna().sort_values(ascending=True)
    frames.append(go.Frame(
        data=[go.Bar(
            x=d.values, y=d.index, orientation='h',
            marker=dict(color=d.values, colorscale="Blues", line=dict(color="black", width=1.5)),
            name="Generación"
        )],
        name=str(year)
    ))
fig.frames = frames

fig.update_layout(
    template="plotly_dark",
    plot_bgcolor="black",
    paper_bgcolor="black",
    title=dict(text=f"Generación Eléctrica por Estado {years_full[0]}–{years_full[-1]}", x=0.5, xanchor="center", font=dict(size=28, color="white")),
    xaxis=dict(title=dict(text="Generación (MWh)", font=dict(size=22, color="white")), tickfont=dict(size=16, color="white"), gridcolor="rgba(255,255,255,0.1)"),
    yaxis=dict(title=dict(text="Estado", font=dict(size=22, color="white")), tickfont=dict(size=12, color="white"), gridcolor="rgba(255,255,255,0.1)"),
    height=900, bargap=0.15,
    sliders=[{
        "steps": [{"args": [[str(y)], {"frame": {"duration": 500, "redraw": True},"mode": "immediate","transition": {"duration": 300}}],"label": str(y), "method": "animate"} for y in years_full],
        "x": 0.1, "y": -0.08, "len": 0.8,
        "currentvalue": {"prefix": "Año: ", "font": {"size": 18, "color": "white"}}
    }],
    updatemenus=[{
        "type": "buttons", "showactive": False, "x": 1.05, "y": 1.15,
        "buttons": [
            {"label": "▶ Play", "method": "animate", "args": [None, {"frame": {"duration": 700, "redraw": True}, "fromcurrent": True,"transition": {"duration": 400, "easing": "quadratic-in-out"}}]},
            {"label": "⏸ Pause", "method": "animate", "args": [[None], {"frame": {"duration": 0, "redraw": False},"mode": "immediate"}]}
        ]
    }]
)
st.plotly_chart(fig, use_container_width=True)




# ======================================================
# GRÁFICA 3: CONSUMO vs GENERACIÓN POR ESTADO, ANUAL
# ======================================================
# ======================================================
# GRÁFICA 3: CONSUMO vs GENERACIÓN POR ESTADO, ANUAL
# ======================================================
st.markdown('---')
st.subheader("Consumo vs Generación por Estado – Animación anual (2002–2024)")
df_consumo_mwh = df_consumo.copy() * 1000
consumo_long = df_consumo_mwh.reset_index().melt(id_vars="Estado", var_name="Año", value_name="Consumo")
generacion_long = df_generacion.reset_index().melt(id_vars="Estado", var_name="Año", value_name="Generacion")
consumo_long["Año"] = consumo_long["Año"].astype(int)
generacion_long["Año"] = generacion_long["Año"].astype(int)
df_comb = pd.merge(consumo_long, generacion_long, on=["Estado", "Año"], how="outer")
years_comb = sorted(df_comb["Año"].dropna().unique().tolist())

if years_comb:
    fig = go.Figure()
    y0 = years_comb[0]
    df_y0 = df_comb[df_comb["Año"] == y0]
    dbar = df_y0.dropna(subset=["Consumo"]).sort_values("Consumo", ascending=True)
    fig.add_trace(go.Bar(
        x=dbar["Consumo"], y=dbar["Estado"], orientation="h", name="Consumo (MWh)",
        marker=dict(color="rgba(52,152,219,0.85)", line=dict(color="rgba(41,128,185,1)", width=1.2)),
        hovertemplate="<b>%{y}</b><br>Consumo: %{x:,.0f} MWh<extra></extra>"
    ))
    dgen = df_y0.dropna(subset=["Generacion"])
    fig.add_trace(go.Scatter(
        x=dgen["Generacion"], y=dgen["Estado"], mode="markers", name="Generación (MWh)",
        marker=dict(color="rgba(241,196,15,1)", size=12, symbol="diamond", line=dict(color="black", width=1)),
        hovertemplate="<b>%{y}</b><br>Generación: %{x:,.0f} MWh<extra></extra>"
    ))
    frames = []
    for y in years_comb:
        df_y = df_comb[df_comb["Año"] == y]
        dbar = df_y.dropna(subset=["Consumo"]).sort_values("Consumo", ascending=True)
        dgen = df_y.dropna(subset=["Generacion"])
        frames.append(go.Frame(data=[
            go.Bar(x=dbar["Consumo"], y=dbar["Estado"], orientation="h", name="Consumo (MWh)",
                   marker=dict(color="rgba(52,152,219,0.85)", line=dict(color="rgba(41,128,185,1)", width=1.2))),
            go.Scatter(x=dgen["Generacion"], y=dgen["Estado"], mode="markers", name="Generación (MWh)",
                       marker=dict(color="rgba(241,196,15,1)", size=12, symbol="diamond", line=dict(color="black", width=1)))
        ], name=str(y)))
    fig.frames = frames

    fig.update_layout(
        template="plotly_dark",
        plot_bgcolor="black",
        paper_bgcolor="black",
        title=dict(text=f"Consumo vs Generación Eléctrica por Estado – {years_comb[0]}–{years_comb[-1]}", x=0.5, xanchor="center", font=dict(size=26, color="white")),
        xaxis=dict(title="MWh", tickfont=dict(size=14, color="white"), showgrid=True, gridcolor="rgba(255,255,255,0.1)"),
        yaxis=dict(title="Estados", tickfont=dict(size=14, color="white"), gridcolor="rgba(255,255,255,0.1)"),
        legend=dict(font=dict(size=14, color="white"), bgcolor="rgba(0,0,0,0.5)", bordercolor="rgba(255,255,255,0.2)", borderwidth=1),
        height=900,
        sliders=[{
            "steps": [{"args": [[str(y)], {"frame": {"duration": 500, "redraw": True}, "mode": "immediate"}],
                       "label": str(y), "method": "animate"} for y in years_comb],
            "x": 0.1, "y": -0.06, "len": 0.8,
            "currentvalue": {"prefix": "Año: ", "font": {"size": 18, "color": "white"}}
        }],
        updatemenus=[{
            "type": "buttons", "x": 1.05, "y": 1.15,
            "buttons": [
                {"label": "▶ Play", "method": "animate", "args": [None, {"frame": {"duration": 700, "redraw": True}, "fromcurrent": True}]},
                {"label": "⏸ Pause", "method": "animate", "args": [[None], {"frame": {"duration": 0, "redraw": False}, "mode": "immediate"}]}
            ]
        }]
    )
    st.plotly_chart(fig, use_container_width=True)


# ======================================================
# GRÁFICA 4: CONSUMO TOTAL NACIONAL (título centrado)
# ======================================================
st.markdown('---')

consumo_total_anual = df_consumo.sum(axis=0)
anios = consumo_total_anual.index.tolist()
generacion = consumo_total_anual.values

hover_text = []
for year, value in zip(anios, generacion):
    if year == 2024:
        hover_text.append(f"Año: {year}<br>Consumo: {value:,.0f} GWh<br>Causa: Sequía, Calor Extremo y Alta demanda vs Capacidad Insuficiente")
    else:
        hover_text.append(f"Año: {year}<br>Consumo: {value:,.0f} GWh")

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=anios,
    y=generacion,
    mode='lines+markers',
    name='Consumo eléctrico',
    line=dict(color='lime', width=3),
    marker=dict(color='white', size=8, line=dict(color='lime', width=2)),
    text=hover_text,
    hoverinfo='text'
))

fig.update_layout(
    title=dict(
        text="Consumo Eléctrico Total Nacional (2006–2024)",
        x=0.5,               # Centrado
        xanchor='center',
        font=dict(size=30, color='white')
    ),
    xaxis=dict(
        title=dict(text="Año", font=dict(size=24, color='white')),
        tickfont=dict(size=18, color='white')
    ),
    yaxis=dict(
        title=dict(text="Consumo (GWh)", font=dict(size=24, color='white')),
        tickfont=dict(size=18, color='white')
    ),
    plot_bgcolor='black',
    paper_bgcolor='black',
    legend=dict(font=dict(color='white'), bgcolor='black')
)
st.plotly_chart(fig, use_container_width=True)

# ======================================================
# GRÁFICA 5: GENERACIÓN TOTAL NACIONAL (título centrado)
# ======================================================
st.markdown('---')

Generacion_total_nacional = df_generacion.sum(axis=0)
anios = Generacion_total_nacional.index
generacion = Generacion_total_nacional.values

hover_text = [f"Año: {year}<br>Generación: {value:,.0f} MWh" for year, value in zip(anios, generacion)]

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=anios,
    y=generacion,
    mode='lines+markers',
    name='Generación eléctrica',
    line=dict(color='orange', width=3),
    marker=dict(color='yellow', size=8, line=dict(color='orange', width=2)),
    text=hover_text,
    hoverinfo='text'
))

fig.update_layout(
    title=dict(
        text=f"Evolución de la Generación Eléctrica Total Nacional ({anios[0]}–{anios[-1]})",
        x=0.5,               # Centrado
        xanchor='center',
        font=dict(size=30, color='white')
    ),
    xaxis=dict(
        title=dict(text="Año", font=dict(size=24, color='white')),
        tickfont=dict(size=18, color='white')
    ),
    yaxis=dict(
        title=dict(text="Generación (MWh)", font=dict(size=24, color='white')),
        tickfont=dict(size=18, color='white')
    ),
    plot_bgcolor='black',
    paper_bgcolor='black',
    legend=dict(font=dict(color='white'), bgcolor='black')
)
st.plotly_chart(fig, use_container_width=True)


# ======================================================
# GRÁFICA 6: CONSUMO PROMEDIO
# ======================================================
st.markdown('---')
media_producida = df_consumo.mean(axis=1).sort_values(ascending=True)

fig = go.Figure(go.Bar(
    x=media_producida.values,
    y=media_producida.index,
    orientation='h',
    marker=dict(color=media_producida.values, colorscale='Oranges', line=dict(color='black', width=1.5))
))

fig.update_layout(
    template="plotly_dark",
    plot_bgcolor="black",
    paper_bgcolor="black",
    title=dict(
        text="Consumo Promedio de Energía por Estado",
        x=0.5, xanchor='center', font=dict(size=24, color="white")
    ),
    xaxis_title=dict(text="Consumo (GWh)", font=dict(size=22, color="white")),
    yaxis_title=dict(text="Estado", font=dict(size=22, color="white")),
    xaxis=dict(tickfont=dict(color="white"), gridcolor="rgba(255,255,255,0.1)"),
    yaxis=dict(tickfont=dict(color="white"), gridcolor="rgba(255,255,255,0.1)"),
    height=900,
    bargap=0.15
)

st.plotly_chart(fig, use_container_width=True)


# ======================================================
# GRÁFICA 7: GENERACIÓN PROMEDIO SIN FILAS DE TOTAL
# ======================================================
# ======================================================
# GRÁFICA 7: GENERACIÓN PROMEDIO SIN FILAS DE TOTAL
# ======================================================
st.markdown('---')

# Filtrar cualquier fila que contenga 'Total' en el índice
df_generacion_sin_total = df_generacion[~df_generacion.index.str.contains("Total", case=False)]

# Calcular media por estado
media_total = df_generacion_sin_total.mean(axis=1).sort_values(ascending=True)

# Crear la figura
fig = go.Figure(go.Bar(
    x=media_total.values,
    y=media_total.index,
    orientation='h',
    marker=dict(color=media_total.values, colorscale='Blues', line=dict(color='black', width=1.5))
))

# Layout con tema oscuro y textos blancos
fig.update_layout(
    template="plotly_dark",
    plot_bgcolor="black",
    paper_bgcolor="black",
    title=dict(
        text=f"Generación Eléctrica Promedio por Estado ({df_generacion.columns.min()}–{df_generacion.columns.max()})",
        x=0.5, xanchor='center', font=dict(size=24, color="white")
    ),
    xaxis_title=dict(text="Generación (MWh)", font=dict(size=22, color="white")),
    yaxis_title=dict(text="Estado", font=dict(size=22, color="white")),
    xaxis=dict(tickfont=dict(color="white"), gridcolor="rgba(255,255,255,0.1)"),
    yaxis=dict(tickfont=dict(color="white"), gridcolor="rgba(255,255,255,0.1)"),
    height=900,
    bargap=0.15
)

st.plotly_chart(fig, use_container_width=True)
