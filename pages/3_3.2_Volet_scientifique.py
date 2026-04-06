
import streamlit as st

from repere_content import render_reperes
from utils import (
    add_assumption_box,
    add_reference_box,
    capacity_factor_from_nominal_power,
    configure_page,
    dimensionnement_foil,
    equivalent_full_load_hours_from_nominal_power,
    plot_capture_share_indicator,
    plot_flot_jusant_share,
    plot_load_factor_curve,
    plot_power_curve,
    plot_production_tradeoff,
    plot_prototype_production_cases,
    plot_resource_energy_fit,
    plot_river_energy_section,
    plot_specific_productivity_curve,
    production_curve_df,
    project_capture_share_df,
    resource_extrapolation_df,
    show_chart,
    show_table,
)

configure_page("3.2 Volet scientifique")

st.title("Volet scientifique")
st.markdown(
    """
Cette page relie l’énergie de la veine d’eau, la logique de courbe de puissance,
le compromis de puissance nominale et le dimensionnement géométrique du foil.
"""
)

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Énergie du fleuve", "Hypothèses de production", "Production et qualité", "Dimensionnement", "Application", "Construction"])

with tab1:
    st.subheader("Énergie de la section et ordre de grandeur de l’extraction")
    left, right = st.columns(2)
    with left:
        show_chart(plot_resource_energy_fit(), key="sci_energy_fit")
    with right:
        show_chart(plot_river_energy_section(), key="sci_energy_section")

    left, right = st.columns(2)
    with left:
        show_chart(plot_flot_jusant_share(), key="sci_share")
    with right:
        show_chart(plot_capture_share_indicator(power_kw=200.0, machine_count=2), key="sci_capture")

    show_table(resource_extrapolation_df(), hide_index=True, width="stretch")
    show_table(project_capture_share_df(power_kw=200.0, machine_count=2), hide_index=True, width="stretch")

    st.markdown(
        add_reference_box(
            "Lecture",
            "L’énergie transitant dans la section de PK326 est très supérieure à celle captée par deux machines. Cela confirme que le rapport raisonne correctement en ordre de grandeur : on évalue d’abord l’intensité de la veine d’eau, puis seulement la petite fraction qu’un projet peut en extraire.",
        ),
        unsafe_allow_html=True,
    )

with tab2:
    st.subheader("Courbe de puissance et hypothèses du rapport")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        v_start = st.slider("Vd (m/s)", 0.3, 0.8, 0.5, 0.05)
    with c2:
        v_nom = st.slider("Vn (m/s)", 1.4, 2.2, 1.8, 0.05)
    with c3:
        v_max = st.slider("Vm (m/s)", 2.0, 2.5, 2.25, 0.05)
    with c4:
        p_nom = st.slider("Pn (kW)", 100, 300, 200, 10)

    show_chart(plot_power_curve(v_start=v_start, v_nom=v_nom, v_max=v_max, p_nom=p_nom), key="sci_power_curve")

    st.markdown(
        add_assumption_box(
            "Hypothèses",
            "Le rapport propose Vd = 0,5 m/s, Vm = 2,25 m/s et un facteur de puissance moyen Cp pris à 0,57 pour une configuration bi-foil en série, faute de campagne expérimentale dédiée complète. Cette hypothèse reste technologique tant qu’elle n’est pas consolidée par essais dédiés.",
        ),
        unsafe_allow_html=True,
    )

with tab3:
    st.subheader("Compromis de puissance nominale et qualité de production")
    df_prod = production_curve_df()
    left, right = st.columns(2)
    with left:
        show_chart(plot_production_tradeoff(df_prod), key="sci_prod")
    with right:
        show_chart(plot_load_factor_curve(df_prod), key="sci_fc")

    show_chart(plot_specific_productivity_curve(df_prod), key="sci_specific")
    show_chart(plot_prototype_production_cases(40.0, selected_mode="prudent"), key="sci_proto_case")

    selected_power = st.slider("Puissance nominale lue sur les courbes (kW)", 100, 300, 200, 10)
    row = df_prod.iloc[(df_prod["Pn_kW"] - selected_power).abs().argsort()[:1]]
    m1, m2, m3 = st.columns(3)
    m1.metric("Production annuelle", f"{float(row['Production_annuelle_MWh'].iloc[0]):.0f} MWh/an")
    m2.metric("Facteur de charge", f"{capacity_factor_from_nominal_power(selected_power):.2f}")
    m3.metric("Heures équivalentes", f"{equivalent_full_load_hours_from_nominal_power(selected_power):.0f} h/an")

    st.markdown(
        add_reference_box(
            "Compromis",
            "Le rapport ne cherche pas la puissance maximale instantanée mais un compromis. Quand la puissance nominale augmente, la production continue de croître mais avec rendements décroissants, tandis que le facteur de charge et la productivité spécifique baissent. La zone autour de 200 kW reste donc la lecture la plus équilibrée.",
        ),
        unsafe_allow_html=True,
    )

with tab4:
    st.subheader("Dimensionnement géométrique du foil")
    st.latex(r"\frac{2H_o}{c} + \frac{E}{c} = \frac{H_m}{c}")
    st.latex(r"L = A \cdot c")

    with st.expander("Exploration des paramètres", expanded=True):
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            Hm = st.slider("Hm (m)", 6.5, 8.0, 7.0, 0.1)
        with c2:
            two_ho_over_c = st.slider("2Ho / c", 2.5, 3.5, 3.0, 0.05)
        with c3:
            e_over_c = st.slider("E / c", 0.60, 1.00, 0.85, 0.05)
        with c4:
            aspect_ratio = st.slider("Allongement A", 15.0, 24.0, 20.0, 0.5)

    dims = dimensionnement_foil(Hm=Hm, two_ho_over_c=two_ho_over_c, e_over_c=e_over_c, aspect_ratio=aspect_ratio)
    d1, d2, d3, d4, d5 = st.columns(5)
    d1.metric("Corde c", f"{dims['c']:.2f} m")
    d2.metric("Amplitude 2Ho", f"{dims['amplitude']:.2f} m")
    d3.metric("Enfoncement E", f"{dims['E']:.2f} m")
    d4.metric("Profondeur à l’axe", f"{dims['axis_depth']:.2f} m")
    d5.metric("Envergure L", f"{dims['L']:.2f} m")

    st.markdown(
        add_assumption_box(
            "Hypothèses",
            "Le rapport retient pour une première lecture 2Ho/c = 3,0, E/c = 0,85 et un allongement A = 20 pour une configuration Duale. On obtient alors une corde d’environ 1,8 m, une amplitude de 5,4 m, un enfoncement de 1,5 m et une envergure de 36 m.",
        ),
        unsafe_allow_html=True,
    )

with tab5:
    render_reperes("scientifique", mode="application")

with tab6:
    render_reperes("scientifique", mode="construction")
