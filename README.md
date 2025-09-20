# klimaFrost
# 🌍 Interaktiv klimavisualisering for norsk geografi (Streamlit + Frost API)

Denne Streamlit-appen henter klimadata fra **Frost API** (Meteorologisk institutt) og visualiserer dem interaktivt. 
Appen kan brukes for å sammenligne klimavariabler (temperatur, nedbør, vind) mellom norske byer.

---

## ✨ Funksjoner

- Velg en eller flere byer (Oslo, Bergen, Trondheim, Tromsø)  
- Velg klimavariabel:  
  - 🌡️ Temperatur (°C)  
  - 🌧️ Nedbør (mm)  
  - 🌬️ Vind (m/s)  
- Velg tidsperiode (årstall) og visning:  
  - **Døgn** → døgnmiddel (eller døgnsum for nedbør)  
  - **Måned** → månedsgjennomsnitt (eller månedssum for nedbør)  
- 📈 Interaktiv graf med sammenligning av byene  
- 💾 Last ned alle grafdata som **CSV** for videre analyse i Excel, GeoGebra m.m.  
- 🗺️ Interaktivt kart med fargekodede verdier og tooltip (viser gjennomsnittsverdien for valgt tidsperiode)

---

## 🔑 Krav

- [Python 3.9+](https://www.python.org/downloads/)  
- [Streamlit](https://streamlit.io/)  
- [pandas](https://pandas.pydata.org/)  
- [requests](https://requests.readthedocs.io/)  
- [pydeck](https://deckgl.readthedocs.io/en/latest/)  

Installer alle avhengigheter med:  
```bash
pip install streamlit pandas requests pydeck
