
import pandas as pd
import streamlit as st

from repere_content import render_reperes
from utils import (
    add_assumption_box,
    add_reference_box,
    case_mode_label,
    compute_support_scenario,
    configure_page,
    current_project_state,
    deployment_phase_df,
    economic_case_matrix_df,
    externalites_default,
    externalities_ranges_df,
    plot_decision_waterfall,
    plot_development_roadmap,
    plot_economic_case_matrix,
    plot_externalities_ranges,
    plot_remaining_cost_bars,
    plot_stage_power_risk,
    plot_support_capex_ranges,
    plot_support_revenue_ranges,
    plot_support_scenario_comparison,
    plot_support_value_breakdown,
    relative_cost_vs_grid_inflation,
    seed_project_state_defaults,
    show_chart,
    stage_power_risk_df,
    support_capex_ranges_df,
    support_revenue_ranges_df,
    support_scenario_presets,
    support_scenarios_matrix_df,
    show_table,
)

configure_page("4.2 Volet techno-économique – Déploiement, soutiens et décision")
seed_project_state_defaults()

def apply_support_preset(name: str) -> None:
    preset = support_scenario_presets()[name]
    st.session_state["aid_capex_pct_v3"] = int(preset["aid_capex_pct"])
    st.session_state["territorial_pct_v3"] = int(preset["territorial_pct"])
    st.session_state["support_prod_v3"] = int(preset["support_prod"])
    st.session_state["cee_v3"] = int(preset["cee"])
    st.session_state["resilience_v3"] = float(preset["resilience"])
    st.session_state["volatility_v3"] = float(preset["volatility"])
    st.session_state["environment_v3"] = float(preset["environment"])
    st.session_state["diversification_v3"] = float(preset["diversification"])

if "support_preset_name_v3" not in st.session_state:
    st.session_state["support_preset_name_v3"] = "Central"
if "support_preset_applied_v3" not in st.session_state:
    apply_support_preset("Central")
    st.session_state["support_preset_applied_v3"] = "Central"

st.title("Volet techno-économique – Déploiement, soutiens et décision")
st.markdown(
    """
Cette page s’appuie sur la même base projet que la page d’économie intrinsèque,
mais sépare clairement les leviers cash des externalités de décision.
"""
)

base_state = current_project_state()
m1, m2, m3, m4 = st.columns(4)
m1.metric("Base projet active", str(base_state["stage"]))
m2.metric("Puissance totale", f"{float(base_state['total_power_kw']):,.0f} kW")
m3.metric("Coût direct intrinsèque", f"{float(base_state['direct_cost_eur_mwh']):,.1f} €/MWh")
m4.metric("Cas économique", case_mode_label(str(base_state["case_mode"])).capitalize())

tab1, tab2, tab3, tab4, tab5 = st.tabs(["Phasage et partenariat", "Soutiens et externalités", "Conclusion", "Application", "Construction"])

with tab1:
    st.subheader("Phasage et logique de partenariat")
    st.markdown(
        add_reference_box(
            "Lecture",
            "Le projet se lit en trois stades : prototype, démonstrateur puis première ferme commerciale. Le partenariat recherché relève d’une logique de contrat de développement : réduction graduelle du risque, adaptation au site et montée en maturité avant industrialisation.",
        ),
        unsafe_allow_html=True,
    )
    left, right = st.columns([1.1, 1.0])
    with left:
        show_chart(plot_development_roadmap(deployment_phase_df()), key="support_roadmap")
    with right:
        show_chart(plot_stage_power_risk(stage_power_risk_df()), key="support_risk")

    show_table(deployment_phase_df()[["Stade", "TRL", "Puissance_typique", "Objectif", "Décision_gate"]], hide_index=True, width="stretch")

    partner_df = pd.DataFrame(
        {
            "Volet site / partenaire": [
                "Accès au site et aux données d’entrée",
                "Cofinancement des étapes amont",
                "Expression du besoin et validation des cas d’usage",
            ],
            "Volet technologie": [
                "Conception et adaptation de la machine",
                "Montée en maturité et industrialisation",
                "Consolidation des données de production et d’exploitation",
            ],
        }
    )
    show_table(partner_df, hide_index=True, width="stretch")

with tab2:
    st.subheader("Soutiens mobilisables et externalités positives")
    st.markdown(
        add_assumption_box(
            "Lecture",
            "Les aides CAPEX et soutiens à la production sont des leviers cash. Les externalités positives ne sont pas des recettes : elles élargissent la décision mais ne doivent pas être confondues avec un prix contractuel.",
        ),
        unsafe_allow_html=True,
    )

    ref_tab, active_tab, compare_tab = st.tabs(["Références", "Scénario actif", "Scénarios"])

    with ref_tab:
        left, right = st.columns(2)
        with left:
            show_chart(plot_support_capex_ranges(support_capex_ranges_df()), key="support_capex_ranges")
        with right:
            show_chart(plot_support_revenue_ranges(support_revenue_ranges_df()), key="support_revenue_ranges")
        show_chart(plot_externalities_ranges(externalities_ranges_df()), key="support_externalities_ranges")

    with active_tab:
        presets = support_scenario_presets()
        preset_name = st.selectbox(
            "Scénario type",
            ["Personnalisé", *presets.keys()],
            index=["Personnalisé", *presets.keys()].index(st.session_state.get("support_preset_name_v3", "Central")),
            key="support_preset_name_v3",
        )
        if preset_name != st.session_state.get("support_preset_applied_v3") and preset_name != "Personnalisé":
            apply_support_preset(preset_name)
            st.session_state["support_preset_applied_v3"] = preset_name

        defaults = externalites_default()
        left, right = st.columns([0.95, 1.05])
        with left:
            with st.expander("Paramètres leviers cash", expanded=True):
                aid_capex_pct = st.slider("Aides CAPEX (%)", 20, 50, int(st.session_state.get("aid_capex_pct_v3", 30)), 1, key="aid_capex_pct_v3")
                territorial_pct = st.slider("Soutiens territoriaux / portuaires (%)", 5, 15, int(st.session_state.get("territorial_pct_v3", 5)), 1, key="territorial_pct_v3")
                support_prod = st.slider("Soutien à la production (€/MWh)", 50, 150, int(st.session_state.get("support_prod_v3", 80)), 5, key="support_prod_v3")
                cee = st.slider("CEE (€/MWh)", 5, 20, int(st.session_state.get("cee_v3", 10)), 1, key="cee_v3")
            with st.expander("Paramètres de valeur élargie", expanded=True):
                resilience = st.slider("Résilience et sécurité d’approvisionnement (€/MWh)", 5.0, 10.0, float(st.session_state.get("resilience_v3", defaults["Résilience / sécurité d’approvisionnement"])), 0.5, key="resilience_v3")
                volatility = st.slider("Réduction de la volatilité des prix (€/MWh)", 5.0, 15.0, float(st.session_state.get("volatility_v3", defaults["Réduction de la volatilité des prix"])), 0.5, key="volatility_v3")
                environment = st.slider("Externalités environnementales non climatiques (€/MWh)", 3.0, 8.0, float(st.session_state.get("environment_v3", defaults["Externalités environnementales non climatiques"])), 0.5, key="environment_v3")
                diversification = st.slider("Diversification stratégique (€/MWh)", 3.0, 7.0, float(st.session_state.get("diversification_v3", defaults["Diversification stratégique"])), 0.5, key="diversification_v3")

        support_result = compute_support_scenario(
            direct_cost_initial=float(base_state["direct_cost_eur_mwh"]),
            capital_component_eur_mwh=float(base_state["capital_component_eur_mwh"]),
            aid_capex_pct=float(aid_capex_pct),
            territorial_pct=float(territorial_pct),
            support_prod=float(support_prod),
            cee=float(cee),
            resilience=float(resilience),
            volatility=float(volatility),
            environment=float(environment),
            diversification=float(diversification),
        )
        grid_relative = relative_cost_vs_grid_inflation(float(base_state["direct_cost_eur_mwh"]), years=20, annual_growth=0.02)

        with right:
            r1, r2, r3, r4 = st.columns(4)
            r1.metric("Composante capital", f"{float(base_state['capital_component_eur_mwh']):,.1f} €/MWh")
            r2.metric("Aides CAPEX", f"{float(support_result['capex_reduction']):,.1f} €/MWh")
            r3.metric("Leviers cash aval", f"{float(support_result['revenue_supports']):,.1f} €/MWh")
            r4.metric("Valeur élargie", f"{float(support_result['positive_externalities']):,.1f} €/MWh")
            show_chart(plot_decision_waterfall(float(base_state["direct_cost_eur_mwh"]), support_result, grid_relative_cost=grid_relative), key="support_active_waterfall")

        left2, right2 = st.columns(2)
        with left2:
            show_chart(plot_support_value_breakdown(support_result["contrib_df"]), key="support_breakdown")
        with right2:
            show_chart(
                plot_remaining_cost_bars(
                    float(base_state["direct_cost_eur_mwh"]),
                    float(support_result["cost_after_capex"]),
                    float(support_result["cash_residual_cost"]),
                    float(support_result["decision_equivalent_cost"]),
                ),
                key="support_remaining",
            )

        c1, c2, c3 = st.columns(3)
        c1.metric("Après aides CAPEX", f"{float(support_result['cost_after_capex']):,.1f} €/MWh")
        c2.metric("Après leviers cash", f"{float(support_result['cash_residual_cost']):,.1f} €/MWh")
        c3.metric("Lecture élargie", f"{float(support_result['decision_equivalent_cost']):,.1f} €/MWh")

    with compare_tab:
        scenario_df = support_scenarios_matrix_df(base_state)
        show_chart(plot_support_scenario_comparison(scenario_df), key="support_compare")
        show_table(
            scenario_df.rename(
                columns={
                    "Coût_initial_EUR_MWh": "Coût initial (€/MWh)",
                    "Après_aides_EUR_MWh": "Après aides (€/MWh)",
                    "Après_leviers_cash_EUR_MWh": "Après leviers cash (€/MWh)",
                    "Lecture_élargie_EUR_MWh": "Lecture élargie (€/MWh)",
                    "Leviers_totaux_EUR_MWh": "Leviers totaux (€/MWh)",
                }
            ),
            hide_index=True,
            width="stretch",
        )

with tab3:
    st.subheader("Conclusion de décision")
    support_result = compute_support_scenario(
        direct_cost_initial=float(base_state["direct_cost_eur_mwh"]),
        capital_component_eur_mwh=float(base_state["capital_component_eur_mwh"]),
        aid_capex_pct=float(st.session_state.get("aid_capex_pct_v3", 30)),
        territorial_pct=float(st.session_state.get("territorial_pct_v3", 5)),
        support_prod=float(st.session_state.get("support_prod_v3", 80)),
        cee=float(st.session_state.get("cee_v3", 10)),
        resilience=float(st.session_state.get("resilience_v3", 7.5)),
        volatility=float(st.session_state.get("volatility_v3", 10.0)),
        environment=float(st.session_state.get("environment_v3", 5.0)),
        diversification=float(st.session_state.get("diversification_v3", 5.0)),
    )
    grid_relative = relative_cost_vs_grid_inflation(float(base_state["direct_cost_eur_mwh"]), years=20, annual_growth=0.02)

    left, right = st.columns([1.15, 1.0])
    with left:
        show_chart(plot_decision_waterfall(float(base_state["direct_cost_eur_mwh"]), support_result, grid_relative_cost=grid_relative), key="decision_waterfall")
    with right:
        show_chart(plot_economic_case_matrix(economic_case_matrix_df(), metric="Coût_direct_EUR_MWh"), key="support_case_matrix")

    c1, c2, c3 = st.columns(3)
    c1.metric("Coût direct intrinsèque", f"{float(base_state['direct_cost_eur_mwh']):,.1f} €/MWh")
    c2.metric("Après leviers cash", f"{float(support_result['cash_residual_cost']):,.1f} €/MWh")
    c3.metric("Coût relatif vs achat réseau inflationné", f"{grid_relative:,.1f} €/MWh")

    st.markdown(
        add_reference_box(
            "Décision",
            "La décision peut être lue sur trois plans distincts : le coût intrinsèque du projet, le coût après leviers cash effectivement mobilisables, puis la lecture élargie incluant la résilience et les externalités positives. Garder ces trois plans séparés évite de confondre un soutien contractuel avec une valeur stratégique.",
        ),
        unsafe_allow_html=True,
    )

with tab4:
    render_reperes("deploiement", mode="application")

with tab5:
    render_reperes("deploiement", mode="construction")
