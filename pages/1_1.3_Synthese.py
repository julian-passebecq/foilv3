
import streamlit as st

from repere_content import render_reperes
from utils import (
    BMVE_115,
    CHANNEL_WIDTH,
    NAVIGATION_SETBACK,
    PMVE_115,
    REFERENCE_MACHINE_WIDTH,
    add_assumption_box,
    add_reference_box,
    configure_page,
    deployment_phase_df,
    implantation_budget_df,
    implantation_windows_df,
    plot_capture_share_indicator,
    plot_development_roadmap,
    plot_flot_jusant_share,
    plot_pk326_curves,
    plot_production_cost_reference,
    plot_production_tradeoff,
    plot_section_profile,
    plot_site_screening,
    production_cost_reference_df,
    production_curve_df,
    resource_summary_df,
    show_chart,
    show_table,
    site_profiles_df,
    yes_no_label,
)

def figure_note(title: str, text: str) -> None:
    st.markdown(add_reference_box(title, text), unsafe_allow_html=True)


configure_page("1.3 Synthèse")

st.title("Synthèse décisionnelle")
tab_main, tab_app, tab_build = st.tabs(["Lecture", "Application", "Construction"])

with tab_main:
    annual_200 = 823
    fc_200 = 0.47
    hours_200 = 4117

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Site de référence", "PK326")
    m2.metric("BMVE / PMVE 115", f"{BMVE_115:.1f} / {PMVE_115:.1f} m / CMH")
    m3.metric("Chenal central", f"{CHANNEL_WIDTH:.0f} m")
    m4.metric("Largeur machine", f"{REFERENCE_MACHINE_WIDTH:.0f} m")
    m5.metric("Corridor utile", "≈ 35 km")

    n1, n2, n3, n4, n5 = st.columns(5)
    n1.metric("2 machines", yes_no_label(True))
    n2.metric("Production repère", f"{annual_200:.0f} MWh/an")
    n3.metric("Facteur de charge", f"{fc_200:.2f}")
    n4.metric("Heures équivalentes", f"{hours_200:.0f} h/an")
    n5.metric("Coût direct 1er commercial", "131–174 €/MWh")

    st.markdown(
        add_reference_box(
            "Synthèse",
            "Le rapport retient PK326 comme hypothèse de travail, montre qu’une implantation latérale hors chenal reste faisable, place le compromis machine autour de 200 kW, puis ouvre une lecture économique structurée par stade de développement.",
        ),
        unsafe_allow_html=True,
    )

    left, right = st.columns(2)
    with left:
        figure_note(
            "Figure de synthèse — sélection du site",
            "Le premier graphique condense le criblage des profils transmis et rappelle pourquoi PK326 a été retenu.",
        )
        show_chart(plot_site_screening(site_profiles_df()), key="syn_sites")
    with right:
        figure_note(
            "Figure de synthèse — lecture de PK326",
            "La courbe PK326 rappelle les vitesses élevées et la dominance du jusant.",
        )
        show_chart(plot_pk326_curves(selected_coef=115), key="syn_pk326")

    st.divider()

    left, right = st.columns([1.05, 0.95])
    with left:
        figure_note(
            "Figure de synthèse — section utile",
            "Cette coupe résume la logique géométrique du dossier : c’est la basse mer défavorable qui calibre la profondeur disponible et la faisabilité hors chenal.",
        )
        show_chart(plot_section_profile(show_raw_windows=True), key="syn_section")
    with right:
        st.markdown(
            add_reference_box(
                "Lecture de l’implantation",
                "Les tableaux traduisent la figure 9 en budget de largeur : fenêtres latérales disponibles, marge restante après recul du chenal et compatibilité de deux machines.",
            ),
            unsafe_allow_html=True,
        )
        show_table(implantation_windows_df(), hide_index=True, width="stretch")
        budget = implantation_budget_df(machine_width=REFERENCE_MACHINE_WIDTH, channel_setback=NAVIGATION_SETBACK)
        show_table(budget, hide_index=True, width="stretch")

        compatible = bool(budget["Compatible"].all()) if not budget.empty else False
        west_margin = float(budget.loc[budget["Fenêtre"] == "Latérale Ouest", "Marge_restante_m"].sum()) if not budget.empty else 0.0
        east_margin = float(budget.loc[budget["Fenêtre"] == "Latérale Est", "Marge_restante_m"].sum()) if not budget.empty else 0.0

        c1, c2, c3 = st.columns(3)
        c1.metric("Compatibilité 2 machines", yes_no_label(compatible))
        c2.metric("Marge Ouest", f"{west_margin:.0f} m")
        c3.metric("Marge Est", f"{east_margin:.0f} m")

    st.divider()

    left, right = st.columns(2)
    with left:
        figure_note(
            "Figure de synthèse — compromis de puissance",
            "La courbe de production rappelle pourquoi la zone autour de 200 kW est privilégiée.",
        )
        show_chart(plot_production_tradeoff(production_curve_df()), key="syn_prod")
    with right:
        figure_note(
            "Figure de synthèse — repère économique",
            "Ce graphique rappelle l’ordre de grandeur intrinsèque du coût direct par stade, avant soutiens.",
        )
        show_chart(plot_production_cost_reference(production_cost_reference_df()), key="syn_prod_cost")

    left, center, right = st.columns([1.0, 0.95, 0.95])
    with left:
        figure_note(
            "Figure de synthèse — jusant / flot",
            "Le jusant apporte davantage d’énergie que le flot, ce qui est important compte tenu de la loi en V³.",
        )
        show_chart(plot_flot_jusant_share(), key="syn_share")
    with center:
        figure_note(
            "Figure de synthèse — part captée",
            "Cette jauge met en regard la ressource de section et ce que deux machines récupèrent réellement.",
        )
        show_chart(plot_capture_share_indicator(power_kw=200.0, machine_count=2), key="syn_capture")
    with right:
        figure_note(
            "Figure de synthèse — trajectoire projet",
            "Après la faisabilité site + machine, le projet se lit en prototype, démonstrateur puis première ferme commerciale.",
        )
        show_chart(plot_development_roadmap(deployment_phase_df()), key="syn_roadmap")

    show_table(resource_summary_df(), hide_index=True, width="stretch")

    st.markdown(
        add_assumption_box(
            "Hypothèses",
            "Lecture de section à BMVE(115), profondeur minimale d’exploitation 7,0 m, garde au fond 0,5 m, recul supplémentaire de 5 m par rapport au chenal, gabarit machine de 36 m de largeur et 7 m de tirant d’eau. Le repère économique repris ici est le coût direct intrinsèque avant soutiens.",
        ),
        unsafe_allow_html=True,
    )

with tab_app:
    render_reperes("synthese", mode="application")

with tab_build:
    render_reperes("synthese", mode="construction")
