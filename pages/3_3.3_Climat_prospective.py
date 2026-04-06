
import streamlit as st

from repere_content import render_reperes
from utils import (
    add_reference_box,
    add_remark_box,
    climate_monthly_flow_df,
    configure_page,
    marine_signal_df,
    plot_climate_flows,
    plot_marine_signal,
    show_chart,
)

configure_page("3.3 Climat et prospective")

st.title("Climat et prospective")
st.markdown(
    """
Cette page reprend la partie prospective du rapport : évolution saisonnière des débits de Seine
et effet du débit sur la propagation de l’influence marine dans l’estuaire.
"""
)

m1, m2, m3 = st.columns(3)
m1.metric("Lecture principale", "Débits froids en baisse")
m2.metric("Point clé pour PK326", "Potentiel non dégradé")
m3.metric("Conclusion du rapport", "Légère hausse possible")

tab1, tab2, tab3, tab4 = st.tabs(["Débits de la Seine", "Propagation marine", "Application", "Construction"])

with tab1:
    st.subheader("Évolution saisonnière des débits")
    st.markdown(
        add_reference_box(
            "Lecture",
            "Les simulations reprises dans le rapport montrent surtout une baisse des débits en période automnale et hivernale. Le décrochage principal intervient avant 2050, puis s’amplifie moins fortement ensuite.",
        ),
        unsafe_allow_html=True,
    )
    show_chart(plot_climate_flows(climate_monthly_flow_df()), key="climate_flows")

    c1, c2, c3 = st.columns(3)
    c1.metric("Hiver présent", "≈ 780–800 m³/s")
    c2.metric("Hiver 2050", "≈ 500–650 m³/s")
    c3.metric("Été / début automne", "ordre de grandeur proche")

with tab2:
    st.subheader("Effet du débit sur la propagation de l’influence marine")
    st.markdown(
        add_reference_box(
            "Lecture",
            "Quand le débit est faible, l’onde de marée et l’élévation marine se conservent beaucoup mieux vers l’amont. Quand le débit est fort, l’amortissement devient nettement plus marqué, surtout au-delà de PK300.",
        ),
        unsafe_allow_html=True,
    )
    show_chart(plot_marine_signal(marine_signal_df()), key="climate_marine")

    c1, c2, c3 = st.columns(3)
    c1.metric("Débit faible", "signal très conservé")
    c2.metric("Débit intermédiaire", "atténuation progressive")
    c3.metric("Débit fort", "amortissement marqué")

st.markdown(
    add_remark_box(
        "Conclusion",
        "Le rapport conclut que le changement climatique n’est pas un facteur de dégradation du potentiel hydrolien à PK326. L’application conserve cette conclusion, mais sans la sur-vendre : elle reste dépendante du modèle hydro-estuarien mobilisé par le rapport.",
    ),
    unsafe_allow_html=True,
)

with tab3:
    render_reperes("climat", mode="application")

with tab4:
    render_reperes("climat", mode="construction")
