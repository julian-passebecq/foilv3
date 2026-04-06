
import streamlit as st

from repere_content import render_reperes
from utils import (
    add_assumption_box,
    add_reference_box,
    anchoring_options_df,
    configure_page,
    plot_anchoring_priority,
    plot_regulatory_process,
    regulatory_process_df,
    regulatory_summary_df,
    show_chart,
    show_table,
)

configure_page("5.1 Ancrage et cadre réglementaire")

st.title("Ancrage et cadre réglementaire")
st.markdown(
    """
Cette page complète la lecture du rapport sur deux volets qui conditionnent la suite du projet :
principe d’ancrage et séquence administrative / réglementaire à anticiper.
"""
)

tab1, tab2, tab3, tab4 = st.tabs(["Ancrage", "Cadre réglementaire", "Application", "Construction"])

with tab1:
    st.subheader("Lecture des solutions d’ancrage")
    st.markdown(
        add_reference_box(
            "Lecture",
            "Le rapport privilégie une solution d’ancrage par pieux vissés avec ligne de mouillage permanente. Le corps mort reste une alternative robuste. Le duc d’Albe est écarté en première lecture.",
        ),
        unsafe_allow_html=True,
    )

    anchors = anchoring_options_df()
    left, right = st.columns(2)
    with left:
        show_chart(plot_anchoring_priority(anchors), key="anchor_priority")
    with right:
        show_table(anchors, hide_index=True, width="stretch")

    st.markdown(
        add_assumption_box(
            "Sol",
            "La priorité donnée aux pieux vissés suppose un contexte compatible avec des alluvions fluviatiles et une reprise de traction importante. Cette conclusion doit être confirmée par reconnaissance géotechnique avant avant-projet.",
        ),
        unsafe_allow_html=True,
    )

with tab2:
    st.subheader("Cadre administratif et réglementaire")
    st.markdown(
        add_reference_box(
            "Périmètre",
            "Le rapport rappelle qu’un projet exploitant l’énergie d’un cours d’eau relève d’un cadre administratif spécifique. L’application reformule ce point de manière prudente : le projet doit être qualifié au regard de la nomenclature IOTA et suivre ensuite le régime réellement applicable.",
        ),
        unsafe_allow_html=True,
    )

    show_chart(plot_regulatory_process(regulatory_process_df()), key="reg_process")
    show_table(regulatory_summary_df(), hide_index=True, width="stretch")

with tab3:
    render_reperes("ancrage", mode="application")

with tab4:
    render_reperes("ancrage", mode="construction")
