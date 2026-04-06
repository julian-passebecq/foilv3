
import streamlit as st

from repere_content import render_reperes
from utils import (
    REFERENCE_LIFETIME_YEARS,
    REFERENCE_OPEX_EUR_MWH,
    add_assumption_box,
    add_reference_box,
    capex_reference_curves_df,
    configure_page,
    deployment_phase_df,
    lcoe_stage_ranges,
    plot_development_roadmap,
    plot_lcoe_ranges,
    plot_production_cost_reference,
    plot_stage_capex_curve,
    plot_stage_discount_rates,
    production_cost_reference_df,
    show_chart,
    show_table,
)


def figure_note(title: str, text: str) -> None:
    st.markdown(add_reference_box(title, text), unsafe_allow_html=True)


configure_page("Accueil")

st.title("Foil'O Seine PK326")
st.subheader("Vue d’ensemble économique et trajectoire projet")

m1, m2, m3 = st.columns(3)
m1.metric("Site de référence", "PK326")
m2.metric("Puissance repère", "200 kW / machine")
m3.metric("Durée de vie", f"{REFERENCE_LIFETIME_YEARS} ans")

m4, m5, m6 = st.columns(3)
m4.metric("OPEX cible", f"{REFERENCE_OPEX_EUR_MWH:,.0f} €/MWh")
m5.metric("Taux d’actualisation", "13 / 10 / 7 %")
m6.metric("Coût direct 1er commercial", "131–174 €/MWh")

tab_main, tab_app, tab_build = st.tabs(["Vue", "Application", "Construction"])

with tab_main:
    st.markdown(
        add_reference_box(
            "Fil directeur",
            "Le rapport raisonne d’abord par maturité de projet : prototype, démonstrateur puis première ferme commerciale. Cette page garde cette logique et se concentre sur le benchmark sectoriel, les repères CAPEX / coût direct et la trajectoire de déploiement.",
        ),
        unsafe_allow_html=True,
    )

    left, right = st.columns(2)
    with left:
        figure_note(
            "Benchmark sectoriel",
            "Le premier graphique montre les plages de LCOE du secteur par stade de maturité. Il sert de benchmark de filière et non de prix direct du projet PK326.",
        )
        show_chart(plot_lcoe_ranges(lcoe_stage_ranges()), key="home_lcoe")
    with right:
        figure_note(
            "Pilotage du risque",
            "Le second graphique rappelle les taux d’actualisation retenus par le rapport. Ils matérialisent la baisse du risque avec la maturité technologique.",
        )
        show_chart(plot_stage_discount_rates(), key="home_discount")

    left, right = st.columns(2)
    with left:
        figure_note(
            "CAPEX de référence",
            "La courbe présente les ordres de grandeur de CAPEX par stade. Ici, l’accent est mis sur le premier commercial pour fixer un repère décisionnel immédiat.",
        )
        show_chart(
            plot_stage_capex_curve(
                capex_reference_curves_df(),
                "1er commercial",
                selected_power_kw=1000.0,
                selected_mode="financed",
                selected_capex_keur=9450.0,
            ),
            key="home_capex",
        )
    with right:
        figure_note(
            "Coût direct de production",
            "Le repère économique le plus lisible du rapport est repris ici : au premier commercial, le coût direct ressort autour de 131 €/MWh hors financement et 174 €/MWh avec financement.",
        )
        show_chart(plot_production_cost_reference(production_cost_reference_df()), key="home_prod_cost")

    left, right = st.columns([1.05, 0.95])
    with left:
        figure_note(
            "Étapes du projet",
            "La frise reprend la logique du rapport : chaque stade a un objectif, une taille typique et une fonction de réduction progressive du risque.",
        )
        show_chart(plot_development_roadmap(deployment_phase_df()), key="home_roadmap")
    with right:
        st.markdown(
            add_assumption_box(
                "Repères par stade",
                "Le tableau rappelle que la puissance seule ne suffit pas : il faut lire ensemble maturité, objectif de stade et ticket de projet.",
            ),
            unsafe_allow_html=True,
        )
        show_table(
            deployment_phase_df()[["Stade", "TRL", "Puissance_typique", "Objectif"]],
            hide_index=True,
            width="stretch",
        )

with tab_app:
    render_reperes("home", mode="application")

with tab_build:
    render_reperes("home", mode="construction")
