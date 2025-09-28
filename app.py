import streamlit as st
import pandas as pd
import plotly.express as px

st.title("📅 KAMENŠKOVA-Split – Stroški po mesecih (Kamenškova 28, stanovanje 10)")

# -----------------------
# Konfiguracija
# -----------------------
meseci = ["Januar", "Februar", "Marec", "April", "Maj", "Junij",
          "Julij", "Avgust", "September", "Oktober", "November", "December"]

kategorije = [
    "Mariborski vodovod (VODA)",
    "Nigrad (KOMUNALNE OBVEZNOSTI)",
    "Energija plus (ELEKTRIKA)",
    "Upravnik SZ Maribor (obratovalni stroški)",
    "Upravnik SZ Maribor (rezervni sklad)",
    "A1 (INTERNET)"
]

# Vnaprej kodirani uporabniki
uporabniki = ["Ni plačano", "Klemen", "Urška"]

# -----------------------
# Vnos po mesecih
# -----------------------
vnosi = {}
tabs = st.tabs(meseci)

for i, mesec in enumerate(meseci):
    with tabs[i]:
        st.subheader(f"{mesec}")
        vnosi[mesec] = {}
        for kategorija in kategorije:
            placnik = st.selectbox(f"Kdo plača {kategorija}?", uporabniki, key=f"{mesec}_{kategorija}_placnik")
            znesek = st.number_input(f"Znesek za {kategorija} (€)", min_value=0.0, value=0.0, step=0.01,
                                     key=f"{mesec}_{kategorija}_znesek")
            vnosi[mesec][kategorija] = {"placnik": placnik, "znesek": znesek}

# -----------------------
# Izračun in prikaz
# -----------------------
if st.button("Izračunaj"):
    data = []
    skupni_uporabniki = {u: 0 for u in uporabniki if u != "Ni plačano"}

    for mesec, kat_vnosi in vnosi.items():
        for kategorija, info in kat_vnosi.items():
            vrstica = {
                "Mesec": mesec,
                "Kategorija": kategorija,
                "Plačnik": info["placnik"],
                "Znesek": info["znesek"]
            }
            data.append(vrstica)
            if info["placnik"] != "Ni plačano":
                skupni_uporabniki[info["placnik"]] += info["znesek"]

    df = pd.DataFrame(data)

    st.subheader("📋 Povzetek po mesecih in kategorijah")
    st.dataframe(df)

    # Pie chart po plačnikih
    st.subheader("🍰 Skupni stroški po uporabnikih")
    if sum(skupni_uporabniki.values()) > 0:
        fig_pie = px.pie(names=list(skupni_uporabniki.keys()), values=list(skupni_uporabniki.values()),
                         title="Skupni stroški po uporabnikih")
        st.plotly_chart(fig_pie)
    else:
        st.warning("Ni plačanih stroškov za prikaz.")

    # Line chart po kategorijah
    st.subheader("📈 Nihanje stroškov po kategorijah skozi leto")
    df_chart = df.copy()
    df_chart.loc[df_chart["Plačnik"] == "Ni plačano", "Znesek"] = 0  # ni plačano = 0
    df_line = df_chart.pivot_table(index="Mesec", columns="Kategorija", values="Znesek", aggfunc="sum").fillna(0)
    st.line_chart(df_line)

    # Skupni letni povzetek
    st.subheader("📅 Skupni letni povzetek")
    skupno_leto = sum(skupni_uporabniki.values())
    povprecje = skupno_leto / len(skupni_uporabniki)
    st.write(f"Skupno plačano: {skupno_leto:.2f} € | Povprečje na uporabnika: {povprecje:.2f} €")
    for u, znesek in skupni_uporabniki.items():
        dolguje = povprecje - znesek
        if dolguje > 0:
            st.success(f"{u} dolguje: {dolguje:.2f} €")
        else:
            st.info(f"{u} nima dolga")
