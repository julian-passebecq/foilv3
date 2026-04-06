
import streamlit as st

from repere_content import render_reperes
from utils import (
    REFERENCE_LIFETIME_YEARS,
    REFERENCE_OPEX_EUR_MWH,
    add_assumption_box,
    add_reference_box,
    add_remark_box,
    capex_reference_curves_df,
    case_mode_label,
    configure_page,
    current_project_state,
    economic_case_matrix_df,
    get_project_inputs_from_state,
    lcoe_stage_ranges,
    plot_economic_case_matrix,
    plot_lcoe_discount_sensitivity,
    plot_lcoe_ranges,
    plot_power_production_link,
    plot_production_cost_reference,
    plot_project_sensitivity_tornado,
    plot_prototype_production_cases,
    plot_reference_vs_model_band,
    plot_specific_capex,
    plot_stage_capex_curve,
    plot_stage_discount_rates,
    production_cost_reference_df,
    prototype_mode_options,
    reference_cost_record,
    reference_lcoe_record,
    reference_project_presets,
    seed_project_state_defaults,
    show_chart,
    show_table,
    specific_capex_reference_df,
    stages_df,
    sync_stage_defaults,
)

configure_page("4.1 Volet techno-économique – Économie intrinsèque")
seed_project_state_defaults()

st.title("Volet techno-économique – Économie intrinsèque")
st.markdown(
    """
Cette page distingue clairement le benchmark sectoriel, les courbes CAPEX du rapport,
le modèle projet paramétrable et les sensibilités principales.
"""
)

m1, m2, m3, m4 = st.columns(4)
m1.metric("Durée de vie de référence", f"{REFERENCE_LIFETIME_YEARS} ans")
m2.metric("OPEX cible rapport", f"{REFERENCE_OPEX_EUR_MWH:,.0f} €/MWh")
m3.metric("Taux d’actualisation", "13 % / 10 % / 7 %")
m4.metric("Coût direct 1er commercial", "131–174 €/MWh")

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(
    ["Cadre et hypothèses", "Référentiels rapport", "Modèle projet", "Sensibilités", "Cas-types", "Application", "Construction"]
)

with tab1:
    st.subheader("Cadre de lecture")
    st.markdown(
        add_reference_box(
            "Lecture",
            "Le rapport raisonne par stade de développement avant de raisonner par puissance. Cette page conserve cette logique pour éviter une erreur classique : croire qu’il suffit d’augmenter la puissance pour déduire correctement les coûts.",
        ),
        unsafe_allow_html=True,
    )
    show_table(stages_df(), hide_index=True, width="stretch")

    left, right = st.columns(2)
    with left:
        show_chart(plot_lcoe_ranges(lcoe_stage_ranges()), key="eco_lcoe_frame")
    with right:
        show_chart(plot_stage_discount_rates(), key="eco_discount_frame")

    st.markdown(
        add_assumption_box(
            "Hypothèses",
            "Durée de vie cible 20 ans. OPEX cible 30 €/MWh. Cas standard : composante capital lissée sur la vie du projet. Cas financé : lecture du rapport reproduite avec un financement à 100 % sur 10 ans à 4 %.",
        ),
        unsafe_allow_html=True,
    )

with tab2:
    st.subheader("Référentiels repris du rapport")
    left, right = st.columns(2)
    with left:
        show_chart(plot_lcoe_ranges(lcoe_stage_ranges()), key="eco_lcoe_refs")
    with right:
        show_chart(plot_production_cost_reference(production_cost_reference_df()), key="eco_prod_cost_ref")

    left, right = st.columns(2)
    with left:
        show_chart(plot_specific_capex(specific_capex_reference_df()), key="eco_specific_capex")
    with right:
        stage_to_show = st.selectbox("Stade affiché", ["Prototype", "Démonstrateur", "1er commercial"], index=1, key="eco_ref_stage")
        show_chart(plot_stage_capex_curve(capex_reference_curves_df(), stage_to_show), key="eco_stage_capex")

    st.markdown(
        add_remark_box(
            "Méthode",
            "Les courbes CAPEX standard et financé sont reprises comme référentiels issus du rapport. Le cas financé du modèle n’est pas un simple décalage graphique : il passe par le coût total des remboursements sur 10 ans à 4 %.",
        ),
        unsafe_allow_html=True,
    )

with tab3:
    st.subheader("Modèle projet")
    presets = reference_project_presets()

    left, right = st.columns(2)
    with left:
        stage_selected = st.selectbox(
            "Stade",
            ["Prototype", "Démonstrateur", "1er commercial"],
            index=["Prototype", "Démonstrateur", "1er commercial"].index(st.session_state["project_stage"]),
            key="project_stage_selector",
        )
        if stage_selected != st.session_state["project_stage"]:
            sync_stage_defaults(stage_selected)

        preset = presets[st.session_state["project_stage"]]

        if st.session_state["project_stage"] == "1er commercial":
            st.session_state["project_machine_count"] = st.slider(
                "Nombre de machines",
                min_value=3,
                max_value=7,
                value=int(st.session_state["project_machine_count"]),
                step=1,
                key="project_machine_count_slider",
            )
        else:
            st.session_state["project_machine_count"] = 1
            st.caption("1 machine retenue pour ce stade")

        st.session_state["project_machine_power_kw"] = st.slider(
            "Puissance nominale par machine (kW)",
            min_value=int(preset["machine_power_min"]),
            max_value=int(preset["machine_power_max"]),
            value=int(st.session_state["project_machine_power_kw"]),
            step=int(preset["machine_power_step"]),
            key="project_machine_power_slider",
        )

        if st.session_state["project_stage"] == "Prototype":
            st.session_state["project_prototype_mode"] = st.radio(
                "Base de production prototype",
                options=list(prototype_mode_options().keys()),
                format_func=lambda key: prototype_mode_options()[key],
                index=list(prototype_mode_options().keys()).index(st.session_state.get("project_prototype_mode", "prudent")),
                key="project_prototype_mode_radio",
            )
            preview_inputs = get_project_inputs_from_state()
            if st.session_state["project_prototype_mode"] == "manual":
                st.session_state["project_manual_annual_mwh"] = st.number_input(
                    "Production annuelle prototype (MWh/an)",
                    min_value=1.0,
                    max_value=5000.0,
                    value=float(st.session_state["project_manual_annual_mwh"]),
                    step=10.0,
                    key="project_manual_annual_mwh_input_proto",
                )
            else:
                st.info(f"Production prototype retenue : {preview_inputs['annual_mwh']:,.0f} MWh/an")
        else:
            st.session_state["project_link_production"] = st.toggle(
                "Lier automatiquement la production à la puissance",
                value=bool(st.session_state["project_link_production"]),
                key="project_link_production_toggle",
            )
            preview_inputs = get_project_inputs_from_state()
            if st.session_state["project_link_production"]:
                st.info(f"Production calculée automatiquement : {preview_inputs['annual_linked_mwh']:,.0f} MWh/an")
            else:
                st.session_state["project_manual_annual_mwh"] = st.number_input(
                    "Production annuelle (MWh/an)",
                    min_value=1.0,
                    max_value=50000.0,
                    value=float(st.session_state["project_manual_annual_mwh"]),
                    step=50.0,
                    key="project_manual_annual_mwh_input",
                )

        st.session_state["project_case_mode"] = st.radio(
            "Cas économique",
            ["standard", "financed"],
            horizontal=True,
            index=0 if st.session_state["project_case_mode"] == "standard" else 1,
            key="project_case_mode_radio",
        )

    with right:
        st.session_state["project_capex_adjust_pct"] = st.slider(
            "Ajustement CAPEX vs référence (%)",
            min_value=-30,
            max_value=30,
            value=int(st.session_state["project_capex_adjust_pct"]),
            step=1,
            key="project_capex_adjust_slider",
        )
        st.session_state["project_opex"] = st.slider(
            "OPEX (€/MWh)",
            min_value=15.0,
            max_value=40.0,
            value=float(st.session_state["project_opex"]),
            step=0.5,
            key="project_opex_slider",
        )
        st.session_state["project_years"] = st.slider(
            "Durée de vie (ans)",
            min_value=10,
            max_value=30,
            value=int(st.session_state["project_years"]),
            step=1,
            key="project_years_slider",
        )
        st.session_state["project_discount_pct"] = st.slider(
            "Taux d’actualisation (%)",
            min_value=4.0,
            max_value=14.0,
            value=float(st.session_state["project_discount_pct"]),
            step=0.5,
            key="project_discount_pct_slider",
        )

    inputs = get_project_inputs_from_state()
    state = current_project_state()
    reference_direct = reference_cost_record(str(state["stage"]), str(state["case_mode"]))
    reference_lcoe = reference_lcoe_record(str(state["stage"]))

    m1, m2, m3, m4, m5, m6 = st.columns(6)
    m1.metric("Puissance totale", f"{float(state['total_power_kw']):,.0f} kW")
    m2.metric("Production annuelle", f"{float(state['annual_mwh']):,.0f} MWh/an")
    m3.metric("CAPEX de référence", f"{float(state['capex_used_keur']):,.0f} k€")
    m4.metric("Coût total du capital", f"{float(state['capital_cost_total_eur'])/1000:,.0f} k€")
    m5.metric("Coût direct projet", f"{float(state['direct_cost_eur_mwh']):,.1f} €/MWh")
    m6.metric("LCOE projet", f"{float(state['lcoe_eur_mwh']):,.1f} €/MWh")

    n1, n2, n3, n4, n5 = st.columns(5)
    n1.metric("Machines", f"{int(state['machine_count'])}")
    n2.metric("Puissance / machine", f"{float(state['machine_power_kw']):,.0f} kW")
    n3.metric("Facteur de charge", f"{float(state['capacity_factor']):.2f}")
    n4.metric("Heures équivalentes", f"{float(state['equivalent_full_load_hours']):,.0f} h/an")
    n5.metric("Base de production", str(inputs["production_basis_short"]))

    st.markdown(add_reference_box("Base de production", str(inputs["production_basis_note"])), unsafe_allow_html=True)

    if str(state["case_mode"]) == "financed":
        st.markdown(
            add_assumption_box(
                "Cas financé",
                "Le modèle applique la logique du rapport : le cas financé utilise la courbe de CAPEX financé comme principal, puis calcule le coût total des remboursements sur 10 ans à 4 %.",
            ),
            unsafe_allow_html=True,
        )

    left, right = st.columns(2)
    with left:
        if str(state["stage"]) == "Prototype":
            show_chart(
                plot_prototype_production_cases(
                    float(state["machine_power_kw"]),
                    selected_mode=str(inputs["prototype_mode"]),
                    selected_annual_mwh=float(state["annual_mwh"]),
                ),
                key="eco_proto_cases",
            )
        else:
            show_chart(
                plot_power_production_link(str(state["stage"]), float(state["machine_power_kw"]), int(state["machine_count"])),
                key="eco_power_prod_link",
            )
    with right:
        show_chart(
            plot_stage_capex_curve(
                capex_reference_curves_df(),
                str(state["stage"]),
                selected_power_kw=float(state["total_power_kw"]),
                selected_mode=str(state["case_mode"]),
                selected_capex_keur=float(state["capex_used_keur"]),
            ),
            key="eco_stage_capex_selected",
        )

    left, right = st.columns(2)
    with left:
        show_chart(
            plot_reference_vs_model_band(
                reference_direct["low"],
                reference_direct["mean"],
                reference_direct["high"],
                float(state["direct_cost_eur_mwh"]),
                title=f"Coût direct – projet vs rapport ({case_mode_label(str(state['case_mode']))})",
            ),
            key="eco_direct_vs_ref",
        )
    with right:
        show_chart(
            plot_reference_vs_model_band(
                reference_lcoe["central_low"],
                reference_lcoe["mean"],
                reference_lcoe["central_high"],
                float(state["lcoe_eur_mwh"]),
                title="LCOE – projet vs benchmark sectoriel",
            ),
            key="eco_lcoe_vs_ref",
        )

with tab4:
    st.subheader("Sensibilités")
    st.markdown(
        add_reference_box(
            "Sensibilités",
            "Le coût direct dépend surtout de la composante capital, de la production annuelle, de l’OPEX et de la durée de vie. Le LCOE reste très sensible au taux d’actualisation.",
        ),
        unsafe_allow_html=True,
    )
    inputs = get_project_inputs_from_state()
    left, right = st.columns(2)
    with left:
        show_chart(plot_project_sensitivity_tornado(inputs), key="eco_tornado")
    with right:
        show_chart(plot_lcoe_discount_sensitivity(inputs), key="eco_discount_sensitivity")

with tab5:
    st.subheader("Cas-types couverts")
    cases_df = economic_case_matrix_df()
    left, right = st.columns(2)
    with left:
        show_chart(plot_economic_case_matrix(cases_df, metric="Coût_direct_EUR_MWh"), key="eco_cases_direct")
    with right:
        show_chart(plot_economic_case_matrix(cases_df, metric="LCOE_EUR_MWh"), key="eco_cases_lcoe")

    show_table(
        cases_df.rename(
            columns={
                "Puissance_totale_kW": "Puissance totale (kW)",
                "Production_annuelle_MWh": "Production annuelle (MWh/an)",
                "CAPEX_kEUR": "CAPEX de référence (k€)",
                "Capital_total_EUR": "Coût total du capital (€)",
                "Coût_direct_EUR_MWh": "Coût direct (€/MWh)",
                "LCOE_EUR_MWh": "LCOE (€/MWh)",
            }
        ),
        hide_index=True,
        width="stretch",
    )

with tab6:
    render_reperes("eco_intrinseque", mode="application")

with tab7:
    render_reperes("eco_intrinseque", mode="construction")
