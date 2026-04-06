
import streamlit as st

from repere_content import render_reperes
from utils import (
    add_assumption_box,
    add_reference_box,
    add_remark_box,
    configure_page,
    plot_corridor_profiles,
    plot_estuary_map,
    plot_pk326_curves,
    plot_resource_energy_fit,
    plot_salinity_zonation,
    plot_site_screening,
    resource_extrapolation_df,
    resource_summary_df,
    show_chart,
    site_profiles_df,
    show_table,
)

configure_page("2.1 Site et données")

st.title("Site, données et lecture de la ressource")
st.markdown(
    """
Cette page couvre les éléments de site du rapport : géographie estuarienne, positionnement des profils,
criblage courantologique, focalisation sur PK326 et lecture de la salinité.
"""
)

tab1, tab2, tab3, tab4, tab5 = st.tabs(["Géographie", "Courants", "Milieu et énergie", "Application", "Construction"])

with tab1:
    st.subheader("Géographie estuarienne et profils transmis")
    st.markdown(
        add_reference_box(
            "Lecture",
            "Les profils transmis se répartissent entre Le Havre et Rouen, dans la partie de Seine encore soumise à l’influence de la marée. La zone la plus intéressante se concentre autour d’un corridor d’environ 35 km entre PK292 et PK326.",
        ),
        unsafe_allow_html=True,
    )
    left, right = st.columns([1.2, 1.0])
    with left:
        show_chart(plot_estuary_map(), key="site_map")
    with right:
        show_chart(plot_corridor_profiles(), key="site_corridor")

    show_table(
        site_profiles_df()[["Profil", "Nom_site", "Année", "PK_km", "Pic_flot_m_s", "Pic_jusant_m_s", "Classe"]],
        hide_index=True,
        width="stretch",
    )

    st.markdown(
        add_remark_box(
            "Carte",
            "La carte est une reconstruction schématique fidèle au message de la figure 1 du rapport. Elle est volontairement légère pour rester robuste dans Streamlit, sans dépendre de couches cartographiques externes.",
        ),
        unsafe_allow_html=True,
    )

with tab2:
    st.subheader("Criblage des profils et zoom sur PK326")
    left, right = st.columns(2)
    with left:
        show_chart(plot_site_screening(site_profiles_df()), key="site_screening")
    with right:
        coef = st.selectbox("Coefficient de marée affiché", [45, 70, 95, 115], index=3)
        show_chart(plot_pk326_curves(selected_coef=coef), key="site_pk326")

    st.markdown(
        add_reference_box(
            "Lecture",
            "Le Landin apparaît comme le profil aux courbes les plus pleines, tandis que Courval présente les pics les plus élevés. La sélection de PK326 combine vitesses élevées, dominance du jusant et section utile compatible avec la navigation.",
        ),
        unsafe_allow_html=True,
    )

with tab3:
    st.subheader("Salinité, eau douce et extrapolation énergétique")
    left, right = st.columns(2)
    with left:
        show_chart(plot_salinity_zonation(), key="site_salinity")
    with right:
        show_chart(plot_resource_energy_fit(), key="site_energy_fit")

    show_table(resource_extrapolation_df(), hide_index=True, width="stretch")
    show_table(resource_summary_df(), hide_index=True, width="stretch")

    st.markdown(
        add_assumption_box(
            "Hypothèses",
            "La masse volumique de l’eau est prise à 1000 kg/m³ sur les sites amont retenus, car la salinité est considérée comme très faible en amont du PK330. L’extrapolation énergétique annuelle est ensuite construite à partir de quatre points de coefficient de marée, via une régression polynomiale d’ordre 3 propre à PK326.",
        ),
        unsafe_allow_html=True,
    )

with tab4:
    render_reperes("site", mode="application")

with tab5:
    render_reperes("site", mode="construction")
