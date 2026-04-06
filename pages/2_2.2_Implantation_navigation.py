
import streamlit as st

from repere_content import render_reperes
from utils import (
    BMVE_115,
    NAVIGATION_SETBACK,
    REFERENCE_MACHINE_WIDTH,
    add_assumption_box,
    add_reference_box,
    add_remark_box,
    compute_section_layout,
    configure_page,
    draw_plan_view_schema,
    implantation_budget_df,
    navigation_reference_df,
    plot_exploitable_section,
    plot_navigation_clearance,
    plot_section_profile,
    plot_tide_levels,
    plot_two_machine_profile,
    plot_window_budget,
    show_chart,
    tide_levels_df,
    yes_no_label,
    show_table,
)

configure_page("2.2 Implantation et navigation")

st.title("Implantation, section utile et navigation")
st.markdown(
    """
Cette page reprend la lecture du profil PK326, les niveaux d’eau, les hypothèses de sécurité,
la logique de recul par rapport au chenal et la mise en situation à deux machines.
"""
)

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    ["Bathymétrie et marée", "Section exploitable", "Insertion latérale", "Mise en situation", "Application", "Construction"]
)

with tab1:
    st.subheader("Niveaux d’eau et profil utile")
    st.markdown(
        add_reference_box(
            "Lecture",
            "Les niveaux d’eau et la bathymétrie sont lus ensemble pour reconstruire la section utile au droit de PK326. La référence de dimensionnement reste la basse mer de vive-eau 115, afin de conserver une lecture prudente de la profondeur disponible hors chenal.",
        ),
        unsafe_allow_html=True,
    )
    left, right = st.columns(2)
    with left:
        show_chart(plot_tide_levels(tide_levels_df()), key="imp_tides")
    with right:
        show_chart(plot_section_profile(show_raw_windows=True), key="imp_profile")

with tab2:
    st.subheader("Lecture paramétrable de la section exploitable")
    st.markdown(
        add_assumption_box(
            "Hypothèses",
            "La conclusion de référence du rapport repose sur BMVE(115), 7,0 m de profondeur minimale d’exploitation et 0,5 m de garde au fond. Les curseurs ci-dessous permettent de tester la robustesse géométrique de cette conclusion sans modifier la logique générale du dossier.",
        ),
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        water_level = st.slider("Niveau d’eau de référence (m / CMH)", 2.6, 3.2, BMVE_115, 0.05)
    with c2:
        depth_limit = st.slider("Profondeur minimale d’exploitation (m)", 6.5, 7.5, 7.0, 0.1)
    with c3:
        clearance = st.slider("Garde au fond (m)", 0.3, 0.8, 0.5, 0.1)

    show_chart(plot_exploitable_section(water_level=water_level, depth_limit=depth_limit, clearance=clearance), key="imp_exploitable")

    raw_layout = compute_section_layout(water_level=water_level, depth_limit=depth_limit, clearance=clearance, channel_setback=0.0)
    raw_windows = raw_layout["windows"]
    if raw_windows.empty:
        st.warning("Avec ces paramètres, aucune fenêtre latérale exploitable n’est détectée sur cette lecture de section.")
    else:
        show_table(raw_windows[["Fenêtre", "Largeur_m", "WaterLevel_m", "DepthLimit_m", "Clearance_m"]], hide_index=True, width="stretch")

with tab3:
    st.subheader("Insertion latérale compatible avec le chenal")
    setback = st.slider("Recul retenu par rapport au chenal (m)", 0.0, 10.0, NAVIGATION_SETBACK, 0.5)

    left, right = st.columns(2)
    with left:
        show_chart(draw_plan_view_schema(machine_width=REFERENCE_MACHINE_WIDTH, channel_setback=setback), key="imp_plan")
        show_chart(plot_navigation_clearance(), key="imp_clearance")
    with right:
        show_chart(plot_window_budget(machine_width=REFERENCE_MACHINE_WIDTH, channel_setback=setback), key="imp_budget")
        show_table(navigation_reference_df(), hide_index=True, width="stretch")

    budget = implantation_budget_df(machine_width=REFERENCE_MACHINE_WIDTH, channel_setback=setback)
    compatible = bool(budget["Compatible"].all()) if not budget.empty else False
    show_table(budget, hide_index=True, width="stretch")

    m1, m2, m3 = st.columns(3)
    m1.metric("Compatibilité 2 machines", yes_no_label(compatible))
    m2.metric("Largeur machine", f"{REFERENCE_MACHINE_WIDTH:.0f} m")
    m3.metric("Recul projet", f"{setback:.1f} m")

with tab4:
    st.subheader("Mise en situation à deux machines")
    left, right = st.columns(2)
    with left:
        show_chart(plot_two_machine_profile(show_ship=False), key="imp_two_machines")
    with right:
        show_chart(plot_two_machine_profile(show_ship=True, ship_width=24.0), key="imp_ship")

    st.markdown(
        add_reference_box(
            "Lecture",
            "La lecture combinée du profil, des niveaux d’eau et du gabarit machine conduit à une conclusion stable : le chenal central reste dédié à la navigation et l’implantation peut se raisonner sur les deux bandes latérales, avec un recul supplémentaire de 5 m dans la mise en situation de référence.",
        ),
        unsafe_allow_html=True,
    )

st.markdown(
    add_remark_box(
        "Profil",
        "Le rapport contient une figure bathymétrique brute de levé hydrographique. Sans le maillage source complet, l’application exploite sa conséquence utile : le profil de section dérivé et la logique de fenêtre d’implantation.",
    ),
    unsafe_allow_html=True,
)

with tab5:
    render_reperes("implantation", mode="application")

with tab6:
    render_reperes("implantation", mode="construction")
