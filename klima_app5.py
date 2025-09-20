# -*- coding: utf-8 -*-
"""
Created on Thu Sep 18 18:47:51 2025

@author: johvik
"""
import streamlit as st
import requests
import pandas as pd
import pydeck as pdk

# Sett inn din egen Client ID fra Frost her:
CLIENT_ID = "46ab53e9-2390-4138-a5e9-c8b4f33ad09d"

# Byer og tilhørende Frost-stasjons-ID-er og posisjoner
steder = {
    "Oslo": {"id": "SN18700", "lat": 59.91, "lon": 10.75},
    "Bergen": {"id": "SN50540", "lat": 60.39, "lon": 5.32},
    "Trondheim": {"id": "SN68860", "lat": 63.43, "lon": 10.39},
    "Tromsø": {"id": "SN90450", "lat": 69.65, "lon": 18.96},
}

# Tilgjengelige klimavariabler
variabler = {
    "Temperatur (°C)": ("air_temperature", "°C"),
    "Nedbør (mm)": ("precipitation_amount", "mm"),
    "Vind (m/s)": ("wind_speed", "m/s"),
}


def hent_døgnverdier(stasjon_id, variabel, start_år, slutt_år):
    """Hent døgnverdier for en gitt stasjon og variabel"""
    endpoint = "https://frost.met.no/observations/v0.jsonld"

    if variabel == "precipitation_amount":
        agg_fun = "sum"
    else:
        agg_fun = "mean"

    params = {
        "sources": stasjon_id,
        "elements": f"{agg_fun}({variabel} P1D)",
        "referencetime": f"{start_år}-01-01/{slutt_år}-12-31",
    }

    r = requests.get(endpoint, params=params, auth=(CLIENT_ID, ""))
    if r.status_code != 200:
        st.error(f"Feil ved henting for {stasjon_id}: {r.status_code}")
        return None

    data = r.json().get("data", [])
    if not data:
        return None

    records = []
    for entry in data:
        time = entry["referenceTime"]
        for obs in entry.get("observations", []):
            records.append({"time": time, "value": obs["value"]})

    if not records:
        return None

    df = pd.DataFrame(records)
    df["time"] = pd.to_datetime(df["time"])
    df = df.set_index("time").sort_index()

    # Hvis flere sensorer samme dag → ta gjennomsnitt
    df = df.groupby(df.index).mean()

    return df


# --- Streamlit App ---
st.title("🌍 Klimadata fra Frost API")

st.sidebar.header("Innstillinger")
valgte_byer = st.sidebar.multiselect("Velg byer:", list(steder.keys()), default=["Oslo"])
variabel_label = st.sidebar.selectbox("Velg klimavariabel:", list(variabler.keys()))
variabel, enhet = variabler[variabel_label]
start_år, slutt_år = st.sidebar.slider("Velg tidsperiode:", 2000, 2024, (2010, 2020))
visning = st.sidebar.radio("Velg visning:", ["Døgn", "Måned"])

dfs = []
for by, info in steder.items():
    if by in valgte_byer:
        df = hent_døgnverdier(info["id"], variabel, start_år, slutt_år)
        if df is not None:
            if visning == "Måned":
                if variabel == "precipitation_amount":
                    df = df.resample("M").sum()
                else:
                    df = df.resample("M").mean()
                df.index = df.index.strftime("%Y-%m")
            else:
                df = df.resample("D").mean()
            df = df.rename(columns={"value": by})
            dfs.append(df)

if dfs:
    combined = pd.concat(dfs, axis=1)

    if variabel == "precipitation_amount":
        visningslabel = "Døgnsum" if visning == "Døgn" else "Månedssum"
    else:
        visningslabel = "Døgnmiddel" if visning == "Døgn" else "Månedsgjennomsnitt"

    st.subheader(f"{variabel_label} – {visningslabel} ({start_år}-{slutt_år})")
    st.line_chart(combined)

    # --- Last ned som CSV ---
    st.download_button(
        label="💾 Last ned data som CSV",
        data=combined.to_csv().encode("utf-8"),
        file_name=f"klimadata_{variabel}_{start_år}_{slutt_år}.csv",
        mime="text/csv",
    )

    # --- Kart ---
    st.subheader("Byenes posisjoner")
    kartdata = []
    for by in valgte_byer:
        if by in combined.columns:
            gjennomsnittsverdi = combined[by].mean()
            kartdata.append({
                "lat": steder[by]["lat"],
                "lon": steder[by]["lon"],
                "by": by,
                "value": round(gjennomsnittsverdi, 1),
                "enhet": enhet
            })
    df_kart = pd.DataFrame(kartdata)

    vmin = df_kart["value"].min()
    vmax = df_kart["value"].max()

    def skaler_farge(v):
        if vmax == vmin:
            return [255, 0, 0, 160]
        r = int(255 * (v - vmin) / (vmax - vmin))
        b = 255 - r
        return [r, 0, b, 160]

    df_kart["color"] = df_kart["value"].apply(skaler_farge)

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=df_kart,
        get_position='[lon, lat]',
        get_fill_color="color",
        get_radius=50000,
        pickable=True
    )

    view_state = pdk.ViewState(latitude=63, longitude=10, zoom=4)
    st.pydeck_chart(pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip={"text": "{by}: {value} {enhet}"}
    ))
else:
    st.warning("Ingen data tilgjengelig for valgte byer.")