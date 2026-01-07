import streamlit as st
import pandas as pd
import requests
import base64
from functools import lru_cache

st.set_page_config(
    page_title="Players",
    page_icon="⛹️‍♂️",
    layout="wide"
)

df_data = st.session_state["data"]

st.sidebar.markdown("Filtros")

# -----------------------------
# Helper: URL -> base64 (com cache)
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
            content_type = (r.headers.get("Content-Type") or "").lower()
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


# 1) Filtro de posição
posicoes = sorted(df_data["Position"].dropna().unique())
posicao = st.sidebar.multiselect("Selecione a posição", posicoes, default=posicoes)

df_filtrado = df_data[df_data["Position"].isin(posicao)]

# 2) Clubes DEPENDEM do filtro de posição
clubes = sorted(df_filtrado["Club"].dropna().unique())
clube = st.sidebar.selectbox("Selecione um Clube", clubes)

# 3) Jogadores DEPENDEM de posição + clube
df_players = df_filtrado[df_filtrado["Club"] == clube]
jogadores = sorted(df_players["Name"].dropna().unique())
jogador = st.sidebar.selectbox("Selecione um Jogador", jogadores)

player_stats = df_data[df_data["Name"] == jogador].iloc[0]

photo_b64 = url_to_base64(player_stats["Photo"])
if photo_b64:
    st.image(photo_b64, width=160)
else:
    st.warning("Não foi possível carregar a foto do jogador.")

st.title(player_stats["Name"])

# -----------------------------
# -----------------------------
st.markdown(f"**Clube:** {player_stats['Club']}")
st.markdown(f"**Posição:** {player_stats['Position']}")

col1, col2, col3 = st.columns(3)
col1.markdown(f"**Idade:** {player_stats['Age']}")
col2.markdown(f"**Altura:** {player_stats['Height(cm.)']/100:.2f} m")
col3.markdown(f"**Peso:** {player_stats['Weight(lbs.)']*0.45359237:.2f} kg")

st.divider()

st.subheader(f"Overall: {player_stats['Overall']}")
st.progress(int(player_stats["Overall"]))

col1, col2, col3 = st.columns(3)
col1.metric(label="Valor de mercado", value=f"£{player_stats['Value(£)']:.2f}")
col2.metric(label="Remuneração Semanal", value=f"£{player_stats['Wage(£)']:.2f}")
col3.metric(label="Cláusula de rescisão", value=f"£{player_stats['Release Clause(£)']:.2f}")


