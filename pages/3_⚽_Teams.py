import streamlit as st
import pandas as pd
import requests
import base64
from functools import lru_cache

st.set_page_config(
    page_title="Teams",
    page_icon="🏆",
    layout="wide"
)

df_data = st.session_state["data"]

clubes = sorted(df_data["Club"].dropna().unique())
clube = st.sidebar.selectbox("Selecione um Clube", clubes)

df_filtered = df_data[df_data["Club"] == clube].set_index("Name")

st.image(df_filtered.iloc[0]["Club Logo"])
st.markdown(f"## {clube}")

columns = ["Age","Photo","Flag","Overall","Value(£)",
           "Wage(£)","Joined","Height(cm.)","Weight(lbs.)",
           "Contract Valid Until","Release Clause(£)"]

# -----------------------------
# Só para imagens: URL -> base64 (com cache)
# -----------------------------
@lru_cache(maxsize=20000)
def url_to_base64(url: str):
    if not isinstance(url, str) or not url.strip():
        return None

    u = url.strip()

    if u.startswith("//"):
        u = "https:" + u

    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(u, headers=headers, timeout=8)
        if r.status_code == 200:
            content_type = r.headers.get("Content-Type", "").lower()

            # tenta inferir tipo; fallback pra png
            if "jpeg" in content_type or "jpg" in content_type:
                mime = "image/jpeg"
            elif "webp" in content_type:
                mime = "image/webp"
            else:
                mime = "image/png"

            b64 = base64.b64encode(r.content).decode("utf-8")
            return f"data:{mime};base64,{b64}"
    except Exception:
        return None

    return None

df_show = df_filtered[columns].copy()

# converte só as colunas de imagem
for c in ["Photo", "Flag"]:
    if c in df_show.columns:
        df_show[c] = df_show[c].map(url_to_base64)

st.dataframe(
    df_show,
    column_config={
        "Overall": st.column_config.ProgressColumn(
            "Overall", format="%d", min_value=0, max_value=100
        ),
        "Wage(£)": st.column_config.ProgressColumn(
            "Weekly Wage",
            format="£%d",
            min_value=0,
            max_value=int(df_filtered["Wage(£)"].max()) if df_filtered["Wage(£)"].notna().any() else 0
        ),
        "Photo": st.column_config.ImageColumn("Photo"),
        "Flag": st.column_config.ImageColumn("Country"),
    },
    use_container_width=True,
)
