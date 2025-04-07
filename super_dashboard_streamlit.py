import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

st.set_page_config(page_title="📊 Super Dashboard Interattiva", layout="wide")
st.title("📊 Super Dashboard con Grafici Interattivi")

uploaded_file = st.sidebar.file_uploader("📂 Carica un file Excel", type=["xlsx"])
if uploaded_file:
    df = pd.read_excel(uploaded_file)

    st.sidebar.markdown("### 🎯 Filtri")
    lower_columns = [col.lower() for col in df.columns]
    if any("data" in col for col in lower_columns):
        date_col = next((col for col in df.columns if "data" in col.lower()), None)
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        min_date, max_date = df[date_col].min(), df[date_col].max()
        date_range = st.sidebar.date_input("📅 Filtro per data", [min_date, max_date])
        df = df[(df[date_col] >= pd.to_datetime(date_range[0])) & (df[date_col] <= pd.to_datetime(date_range[1]))]

    st.header("🥧 Grafico a Torta")
    numeric_cols = df.select_dtypes(include=['number']).columns
    cat_cols = df.select_dtypes(exclude=['number']).columns

    if len(cat_cols) > 0 and len(numeric_cols) > 0:
        pie_col = st.selectbox("Categoria", options=cat_cols)
        val_col = st.selectbox("Valore", options=numeric_cols)
        pie_chart = px.pie(df, names=pie_col, values=val_col, title="Distribuzione a Torta", hole=0.4)
        st.plotly_chart(pie_chart, use_container_width=True)

    st.header("📈 Statistiche")
    if len(numeric_cols) > 0:
        col = st.selectbox("📌 Colonna numerica", numeric_cols)
        st.write(df[col].describe())

        st.subheader("📊 Istogramma")
        hist = px.histogram(df, x=col, nbins=20, title=f"Distribuzione di {col}")
        st.plotly_chart(hist, use_container_width=True)

        st.subheader("📈 Box Plot")
        box = px.box(df, y=col, title=f"Boxplot di {col}")
        st.plotly_chart(box, use_container_width=True)

    st.header("🧮 Modifica tabella")
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_default_column(editable=True, resizable=True)
    grid_options = gb.build()
    grid_response = AgGrid(
        df,
        gridOptions=grid_options,
        update_mode=GridUpdateMode.MODEL_CHANGED,
        fit_columns_on_grid_load=True,
        theme="alpine"
    )
    edited_df = grid_response["data"]

    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        edited_df.to_excel(writer, index=False)
    st.download_button(
        "⬇️ Scarica Excel",
        data=output.getvalue(),
        file_name="dati_modificati.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.info("Carica un file Excel per iniziare.")
