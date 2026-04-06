
import pandas as pd
import streamlit as st

from utils import (
    BMVE_115,
    CHANNEL_WIDTH,
    NAVIGATION_SETBACK,
    PMVE_115,
    REFERENCE_MACHINE_WIDTH,
    add_assumption_box,
    add_method_box,
    add_reference_box,
    add_remark_box,
    annual_mwh_from_nominal_power,
    capacity_factor_from_nominal_power,
    anchoring_options_df,
    capex_reference_curves_df,
    climate_monthly_flow_df,
    configure_page,
    deployment_phase_df,
    dimensionnement_foil,
    draw_machine_schema,
    draw_oscillating_foil_principle,
    equivalent_full_load_hours_from_nominal_power,
    externalities_ranges_df,
    implantation_windows_df,
    lcoe_stage_ranges,
    machine_operating_points_df,
    marine_signal_df,
    plot_anchoring_priority,
    plot_capture_share_indicator,
    plot_climate_flows,
    plot_development_roadmap,
    plot_estuary_map,
    plot_externalities_ranges,
    plot_lcoe_ranges,
    plot_load_factor_curve,
    plot_marine_signal,
    plot_navigation_clearance,
    plot_power_curve,
    plot_production_cost_reference,
    plot_production_tradeoff,
    plot_regulatory_process,
    plot_river_energy_section,
    plot_section_profile,
    plot_site_screening,
    plot_stage_capex_curve,
    plot_stage_discount_rates,
    plot_support_capex_ranges,
    plot_support_revenue_ranges,
    plot_technology_comparison,
    plot_tide_levels,
    plot_two_machine_profile,
    plot_window_budget,
    production_cost_reference_df,
    production_curve_df,
    regulatory_process_df,
    regulatory_summary_df,
    report_logic_checks_df,
    resource_summary_df,
    show_chart,
    show_table,
    site_profiles_df,
    stages_df,
    support_capex_ranges_df,
    support_revenue_ranges_df,
    technology_comparison_df,
    technology_principles_df,
    tide_levels_df,
)

configure_page("1.2 Résumé rapport")

CHAPTERS = [
    {
        "id": "ch1",
        "number": 1,
        "title": "Principe technologique",
        "pages": "p.4",
        "app_pages": "Machine, Volet scientifique",
        "summary": "Foil’O repose sur un foil oscillant immergé qui transforme un mouvement alternatif en rotation continue vers la génératrice.",
        "importance": "Ce chapitre fonde toute la suite : grande surface active, architecture compacte et possibilité d’implantation en zone estuarienne contrainte.",
        "key_points": [
            "Foil oscillant plutôt que pales rotatives.",
            "Pilotage paramétrique du battement.",
            "Architecture compacte et organes sensibles isolés du milieu.",
        ],
        "figures": "Chapitre surtout textuel, réinterprété dans l’application par des schémas de principe.",
        "formulas": [],
    },
    {
        "id": "ch2",
        "number": 2,
        "title": "Données principales du site",
        "pages": "p.5 à p.7",
        "app_pages": "Site et données, Synthèse",
        "summary": "Sept profils sont comparés entre Le Havre et Rouen ; un corridor d’environ 35 km autour de PK292 et PK326 ressort nettement.",
        "importance": "C’est le chapitre de sélection du site : toute la démonstration bascule ensuite sur PK326.",
        "key_points": [
            "4 profils sur 7 dépassent largement ±1,0 m/s.",
            "PK292 a les courbes les plus pleines ; PK326 a les pics les plus élevés.",
            "En amont de PK330, la lecture en eau quasi douce est justifiée.",
        ],
        "figures": "Figures 1 à 4 : géographie estuarienne, criblage des profils, zoom PK326, salinité.",
        "formulas": [],
    },
    {
        "id": "ch3",
        "number": 3,
        "title": "Section du fleuve au droit du site choisi",
        "pages": "p.8 à p.9",
        "app_pages": "Implantation et navigation",
        "summary": "La bathymétrie PK326 et les niveaux de marée sont combinés pour produire un profil utile du fleuve.",
        "importance": "Sans cette lecture, on ne peut ni dimensionner l’implantation ni discuter la compatibilité avec la navigation.",
        "key_points": [
            "Bathymétrie référencée au 0 / CMH.",
            "BMVE(115) ≈ 2,8 m / CMH et PMVE(115) ≈ 8,4 m / CMH.",
            "Le chenal central de 110 m doit être conservé.",
        ],
        "figures": "Figures 5 à 7 : bathymétrie brute, niveaux d’eau, profil utile reconstitué.",
        "formulas": [],
    },
    {
        "id": "ch4",
        "number": 4,
        "title": "Énergie du fleuve",
        "pages": "p.10",
        "app_pages": "Volet scientifique, Synthèse",
        "summary": "L’énergie cinétique transitant dans toute la section de PK326 est évaluée pour cadrer la ressource brute du site.",
        "importance": "Le message clé est de ne pas confondre énergie de section et énergie récupérée par le projet.",
        "key_points": [
            "Énergie de section ≈ 25 à 85 MWh par marée.",
            "Ordre de grandeur annuel ≈ 29,5 GWh.",
            "Le jusant est plus énergétique que le flot.",
        ],
        "figures": "Chapitre calculatoire repris ensuite dans plusieurs graphiques de l’application.",
        "formulas": [r"P_{ve}(t,C)=\frac{1}{2}\rho S V(t,C)^3"],
    },
    {
        "id": "ch5",
        "number": 5,
        "title": "Contraintes de navigation",
        "pages": "p.11",
        "app_pages": "Implantation et navigation",
        "summary": "Le trafic lourd de la Seine impose de conserver le chenal central libre.",
        "importance": "C’est le verrou non énergétique du dossier : un bon site hydrolien n’est exploitable que s’il reste compatible avec la navigation réelle.",
        "key_points": [
            "Trafic de grands navires jusqu’à Rouen.",
            "Le chenal central n’est pas la zone de déploiement retenue.",
            "La faisabilité se joue hors chenal.",
        ],
        "figures": "Figure 8 et discussion de trafic.",
        "formulas": [],
    },
    {
        "id": "ch6",
        "number": 6,
        "title": "Section exploitable et conditions de sécurité",
        "pages": "p.12 à p.13",
        "app_pages": "Implantation et navigation, Synthèse",
        "summary": "Les fenêtres latérales de déploiement sont déduites à partir de BMVE(115), d’une profondeur minimale de 7 m et d’une garde au fond de 0,5 m.",
        "importance": "La faisabilité quitte ici le registre du principe pour devenir une lecture géométrique concrète.",
        "key_points": [
            "Fenêtre bâbord ≈ 70 × 7 m.",
            "Fenêtre tribord ≈ 45 × 7 m.",
            "Lecture volontairement prudente sur basse mer défavorable.",
        ],
        "figures": "Figure 9 et lecture de marge latérale.",
        "formulas": [],
    },
    {
        "id": "ch7",
        "number": 7,
        "title": "Solutions d’ancrage",
        "pages": "p.14 à p.15",
        "app_pages": "Ancrage et cadre réglementaire",
        "summary": "Plusieurs solutions d’ancrage sont comparées pour immobiliser une machine flottante soumise à une forte traînée.",
        "importance": "Le chapitre ne valide pas un design final, mais fixe la direction d’avant-projet.",
        "key_points": [
            "Duc d’Albe écarté en première analyse.",
            "Pieux vissés jugés les plus adaptés au contexte supposé.",
            "Reconnaissance géotechnique indispensable avant validation.",
        ],
        "figures": "Chapitre textuel, reformulé dans l’application en hiérarchie visuelle.",
        "formulas": [],
    },
    {
        "id": "ch8",
        "number": 8,
        "title": "Dimensions caractéristiques des hydroliennes possibles",
        "pages": "p.16",
        "app_pages": "Volet scientifique, Machine",
        "summary": "Le gabarit de la machine est dimensionné à partir de la profondeur disponible et de rapports adimensionnels propres à la technologie.",
        "importance": "Le gabarit n’est pas arbitraire : il résulte d’un premier calcul géométrique cohérent avec la section exploitable au PK326.",
        "key_points": [
            "Hypothèses 2Ho/c = 3,0 ; E/c = 0,85 ; A = 20.",
            "Corde d’environ 1,8 m.",
            "Envergure d’environ 36 m.",
        ],
        "figures": "Chapitre calculatoire, prolongé dans l’application par un module interactif.",
        "formulas": [r"\frac{2H_o}{c}+\frac{E}{c}=\frac{H_m}{c}", r"L=A \cdot c"],
    },
    {
        "id": "ch9",
        "number": 9,
        "title": "Présentation de l’hydrolienne",
        "pages": "p.17 à p.18",
        "app_pages": "Machine et exploitation",
        "summary": "La machine est présentée en fonctionnement puis en position relevée afin de montrer deux états réellement utiles à l’exploitation.",
        "importance": "Cette partie relie gabarit, opérabilité et sûreté d’exploitation.",
        "key_points": [
            "Machine en fonctionnement : 38 × 36 m, tirant d’eau 7,0 m.",
            "Machine relevée : tirant d’eau 1,6 m.",
            "Inspection, sécurité, remorquage et maintenance facilités.",
        ],
        "figures": "Figures 10 et 11.",
        "formulas": [],
    },
    {
        "id": "ch10",
        "number": 10,
        "title": "Mise en situation et comparaison",
        "pages": "p.19 à p.20",
        "app_pages": "Machine et exploitation, Implantation et navigation",
        "summary": "Deux hydroliennes sont placées latéralement hors chenal puis comparées à des technologies concurrentes à production équivalente.",
        "importance": "Le chapitre fait la jonction entre la géométrie de la machine et la géométrie du fleuve.",
        "key_points": [
            "Deux machines restent compatibles avec un chenal central libre.",
            "Le navire reste dans le corridor de navigation.",
            "Les solutions rotatives deviennent beaucoup plus diffuses dans la section.",
        ],
        "figures": "Figures 12 à 14.",
        "formulas": [],
    },
    {
        "id": "ch11",
        "number": 11,
        "title": "Données et hypothèses pour quantifier la production",
        "pages": "p.21 à p.22",
        "app_pages": "Volet scientifique",
        "summary": "Les hypothèses de récupération d’énergie, les vitesses de fonctionnement et la relation vitesse-puissance sont posées ici.",
        "importance": "C’est le socle de toute la partie production du dossier.",
        "key_points": [
            "Vd = 0,5 m/s et Vm = 2,25 m/s en première hypothèse.",
            "Cp moyen retenu à 0,57.",
            "Exploration de plusieurs puissances nominales entre 100 et 300 kW.",
        ],
        "figures": "Figures 15 et 16.",
        "formulas": [r"P=\frac{1}{2}\rho S C_p V^3"],
    },
    {
        "id": "ch12",
        "number": 12,
        "title": "Quantification de la production et qualité",
        "pages": "p.23 à p.24",
        "app_pages": "Volet scientifique, Synthèse",
        "summary": "Autour de 200 kW, la machine conserve une production élevée tout en évitant une dégradation trop rapide du facteur de charge.",
        "importance": "C’est le chapitre du compromis de puissance nominale.",
        "key_points": [
            "Production annuelle ≈ 700 à 900 MWh/an par machine.",
            "Facteur de charge ≈ 0,41 à 0,52.",
            "Lecture de compromis autour de 200 kW.",
        ],
        "figures": "Figures 17 et 18.",
        "formulas": [],
    },
    {
        "id": "ch13",
        "number": 13,
        "title": "Tendance évolutive avec le changement climatique",
        "pages": "p.25 à p.26",
        "app_pages": "Climat et prospective",
        "summary": "La baisse saisonnière des débits ne conduit pas ici à une dégradation du potentiel à PK326 ; elle peut aller dans un sens légèrement favorable.",
        "importance": "Le chapitre vérifie que le climat n’invalide pas la logique hydrolienne du site retenu.",
        "key_points": [
            "Décrochage principal avant 2050.",
            "Baisse surtout marquée en automne-hiver.",
            "Débit plus faible = opposition moindre à la marée.",
        ],
        "figures": "Figures 19 et 20.",
        "formulas": [],
    },
    {
        "id": "ch14",
        "number": 14,
        "title": "Introduction pour l’évaluation économique",
        "pages": "p.27 à p.28",
        "app_pages": "Économie intrinsèque, Déploiement",
        "summary": "L’analyse économique est structurée par stade de développement, avec une logique de contrat de développement.",
        "importance": "La maturité devient ici un paramètre aussi important que la puissance installée.",
        "key_points": [
            "Trois stades : prototype, démonstrateur, premier commercial.",
            "Le risque technologique conditionne les hypothèses économiques.",
            "Le partenariat site / technologie fait partie de la logique du modèle.",
        ],
        "figures": "Chapitre surtout textuel, traduit dans l’application en presets et frise.",
        "formulas": [],
    },
    {
        "id": "ch15",
        "number": 15,
        "title": "Choix de la métrique économique et pilotage",
        "pages": "p.29 à p.31",
        "app_pages": "Économie intrinsèque",
        "summary": "Le benchmark LCOE sectoriel est distingué du coût direct propre au projet et relié aux taux d’actualisation retenus selon la maturité.",
        "importance": "Ce chapitre empêche les contre-lectures économiques.",
        "key_points": [
            "Repères de benchmark : 605 / 356 / 221 €/MWh.",
            "Taux d’actualisation : 13 %, 10 % et 7 %.",
            "Risque technologique et financement sont pilotés explicitement.",
        ],
        "figures": "Figure 21.",
        "formulas": [r"LCOE=\frac{\sum_{t=0}^{N}\frac{Cost_t}{(1+r)^t}}{\sum_{t=1}^{N}\frac{E_t}{(1+r)^t}}"],
    },
    {
        "id": "ch16",
        "number": 16,
        "title": "Résultats des projections économiques",
        "pages": "p.32 à p.33",
        "app_pages": "Économie intrinsèque",
        "summary": "Les projections donnent des courbes de CAPEX et un coût direct de production par stade.",
        "importance": "C’est la sortie chiffrée centrale du dossier économique.",
        "key_points": [
            "CAPEX par stade avec bandes d’incertitude.",
            "Lecture spécifique par kW pour montrer l’économie d’échelle.",
            "1er commercial : 131 €/MWh hors financement et 174 €/MWh avec financement.",
        ],
        "figures": "Figures 22 à 24.",
        "formulas": [],
    },
    {
        "id": "ch17",
        "number": 17,
        "title": "Externalités positives",
        "pages": "p.34 à p.35",
        "app_pages": "Déploiement, soutiens et décision",
        "summary": "Quatre familles d’externalités positives viennent enrichir la décision sans être confondues avec des recettes contractuelles.",
        "importance": "Le chapitre élargit la décision au-delà du coût brut du MWh.",
        "key_points": [
            "Résilience énergétique : 5 à 10 €/MWh.",
            "Volatilité des prix : 5 à 15 €/MWh.",
            "Valeur élargie totale : environ 15 à 40 €/MWh.",
        ],
        "figures": "Synthèse indicative des externalités positives.",
        "formulas": [],
    },
    {
        "id": "ch18",
        "number": 18,
        "title": "Leviers de soutien mobilisable",
        "pages": "p.36 à p.37",
        "app_pages": "Déploiement, soutiens et décision",
        "summary": "Les aides CAPEX, soutiens à la production, CEE et soutiens territoriaux constituent les principaux leviers d’équilibre économique.",
        "importance": "Le chapitre explique pourquoi la compétitivité du projet ne se lit pas uniquement au coût intrinsèque du MWh.",
        "key_points": [
            "Aides CAPEX : 20 à 50 % du CAPEX.",
            "Soutien à la production : 50 à 150 €/MWh.",
            "CEE et soutiens territoriaux comme compléments possibles.",
        ],
        "figures": "Synthèse indicative des leviers de soutien.",
        "formulas": [],
    },
    {
        "id": "ch19",
        "number": 19,
        "title": "Aspect réglementaire",
        "pages": "p.38",
        "app_pages": "Ancrage et cadre réglementaire",
        "summary": "Le dossier se clôt par une synthèse réglementaire centrée sur l’eau, l’environnement et les incidences à documenter.",
        "importance": "La faisabilité n’est pas seulement technique : elle doit aussi devenir administrativement soutenable.",
        "key_points": [
            "Logique eau / environnement et incidences sur les milieux.",
            "Dossier à constituer sur eau, écoulement, milieux et usages.",
            "Participation du public selon le régime applicable.",
        ],
        "figures": "Chapitre textuel, reformulé dans l’application en séquence projet prudente.",
        "formulas": [],
    },
]

CHAPTER_BY_ID = {chapter["id"]: chapter for chapter in CHAPTERS}


def render_summary_block(chapter: dict[str, object]) -> None:
    st.markdown("**Points clés**")
    for item in chapter["key_points"]:
        st.markdown(f"- {item}")


def render_chapter_visuals(chapter_id: str) -> None:
    if chapter_id == "ch1":
        left, right = st.columns(2)
        with left:
            show_chart(draw_oscillating_foil_principle(), key="guide_ch1_principle")
        with right:
            show_table(technology_principles_df(), hide_index=True, width="stretch")
        return

    if chapter_id == "ch2":
        left, right = st.columns([1.1, 0.9])
        with left:
            show_chart(plot_estuary_map(), key="guide_ch2_map")
        with right:
            show_chart(plot_site_screening(site_profiles_df()), key="guide_ch2_screening")
        return

    if chapter_id == "ch3":
        left, right = st.columns(2)
        with left:
            show_chart(plot_tide_levels(tide_levels_df()), key="guide_ch3_tides")
        with right:
            show_chart(plot_section_profile(show_raw_windows=True), key="guide_ch3_section")
        return

    if chapter_id == "ch4":
        show_chart(plot_river_energy_section(), key="guide_ch4_energy")
        return

    if chapter_id == "ch5":
        left, right = st.columns(2)
        with left:
            show_chart(plot_navigation_clearance(), key="guide_ch5_nav")
        with right:
            show_chart(plot_window_budget(machine_width=REFERENCE_MACHINE_WIDTH, channel_setback=NAVIGATION_SETBACK), key="guide_ch5_budget")
        return

    if chapter_id == "ch6":
        left, right = st.columns(2)
        with left:
            show_chart(plot_window_budget(machine_width=REFERENCE_MACHINE_WIDTH, channel_setback=NAVIGATION_SETBACK), key="guide_ch6_windows")
        with right:
            show_table(implantation_windows_df(), hide_index=True, width="stretch")
        return

    if chapter_id == "ch7":
        left, right = st.columns(2)
        with left:
            show_chart(plot_anchoring_priority(anchoring_options_df()), key="guide_ch7_anchor")
        with right:
            show_table(anchoring_options_df(), hide_index=True, width="stretch")
        return

    if chapter_id == "ch8":
        dims = dimensionnement_foil()
        left, right = st.columns([0.9, 1.1])
        with left:
            show_table(
                pd.DataFrame(
                    {
                        "Grandeur": ["Corde c", "Amplitude 2Ho", "Enfoncement E", "Profondeur à l’axe", "Envergure L"],
                        "Valeur": [f"{dims['c']:.2f} m", f"{dims['amplitude']:.2f} m", f"{dims['E']:.2f} m", f"{dims['axis_depth']:.2f} m", f"{dims['L']:.2f} m"],
                    }
                ),
                hide_index=True,
                width="stretch",
            )
        with right:
            show_chart(draw_machine_schema(mode="fonctionnement"), key="guide_ch8_machine")
        return

    if chapter_id == "ch9":
        left, right = st.columns(2)
        with left:
            show_chart(draw_machine_schema(mode="fonctionnement"), key="guide_ch9_run")
        with right:
            show_chart(draw_machine_schema(mode="maintenance"), key="guide_ch9_maint")
        show_table(machine_operating_points_df(), hide_index=True, width="stretch")
        return

    if chapter_id == "ch10":
        left, right = st.columns(2)
        with left:
            show_chart(plot_two_machine_profile(show_ship=True, ship_width=24.0), key="guide_ch10_implant")
        with right:
            show_chart(plot_technology_comparison(technology_comparison_df()), key="guide_ch10_compare")
        return

    if chapter_id == "ch11":
        show_chart(plot_power_curve(v_start=0.5, v_nom=1.8, v_max=2.25, p_nom=200.0), key="guide_ch11_power")
        return

    if chapter_id == "ch12":
        left, right = st.columns(2)
        with left:
            show_chart(plot_production_tradeoff(production_curve_df()), key="guide_ch12_prod")
        with right:
            show_chart(plot_load_factor_curve(production_curve_df()), key="guide_ch12_fc")
        return

    if chapter_id == "ch13":
        left, right = st.columns(2)
        with left:
            show_chart(plot_climate_flows(climate_monthly_flow_df()), key="guide_ch13_climate")
        with right:
            show_chart(plot_marine_signal(marine_signal_df()), key="guide_ch13_marine")
        return

    if chapter_id == "ch14":
        left, right = st.columns(2)
        with left:
            show_chart(plot_development_roadmap(deployment_phase_df()), key="guide_ch14_roadmap")
        with right:
            show_table(stages_df(), hide_index=True, width="stretch")
        return

    if chapter_id == "ch15":
        left, right = st.columns(2)
        with left:
            show_chart(plot_lcoe_ranges(lcoe_stage_ranges()), key="guide_ch15_lcoe")
        with right:
            show_chart(plot_stage_discount_rates(), key="guide_ch15_discount")
        return

    if chapter_id == "ch16":
        left, right = st.columns(2)
        with left:
            show_chart(plot_stage_capex_curve(capex_reference_curves_df(), "1er commercial"), key="guide_ch16_capex")
        with right:
            show_chart(plot_production_cost_reference(production_cost_reference_df()), key="guide_ch16_cost")
        return

    if chapter_id == "ch17":
        show_chart(plot_externalities_ranges(externalities_ranges_df()), key="guide_ch17_externalities")
        return

    if chapter_id == "ch18":
        left, right = st.columns(2)
        with left:
            show_chart(plot_support_capex_ranges(support_capex_ranges_df()), key="guide_ch18_capex_support")
        with right:
            show_chart(plot_support_revenue_ranges(support_revenue_ranges_df()), key="guide_ch18_revenue_support")
        return

    if chapter_id == "ch19":
        left, right = st.columns(2)
        with left:
            show_chart(plot_regulatory_process(regulatory_process_df()), key="guide_ch19_reg")
        with right:
            show_table(regulatory_summary_df(), hide_index=True, width="stretch")
        return


def render_logic_audit() -> None:
    checks = report_logic_checks_df()

    st.markdown(
        add_method_box(
            "Comment lire cet audit",
            "Ces contrôles ne remplacent pas le rapport source. Ils vérifient seulement que l’application retombe sur ses ordres de grandeur structurants et signale explicitement les arrondis ou simplifications assumés.",
        ),
        unsafe_allow_html=True,
    )

    show_table(checks, hide_index=True, width="stretch")

    st.markdown("**Formules pivots utilisées dans le raisonnement**")
    st.latex(r"P_{ve}(t,C)=\frac{1}{2}\rho S V(t,C)^3")
    st.latex(r"P=\frac{1}{2}\rho S C_p V^3")
    st.latex(r"\frac{2H_o}{c}+\frac{E}{c}=\frac{H_m}{c}\qquad;\qquad L=A\cdot c")
    st.latex(r"LCOE=\frac{\sum_{t=0}^{N}\frac{Cost_t}{(1+r)^t}}{\sum_{t=1}^{N}\frac{E_t}{(1+r)^t}}")

    st.markdown(
        add_assumption_box(
            "Limites assumées par l’application",
            "La reconstruction reste volontairement simplifiée par rapport au rapport complet : courbes de courant lissées, profil de section reconstruit à partir de la coupe utile, lecture économique fondée sur des courbes de référence et non sur un devis détaillé.",
        ),
        unsafe_allow_html=True,
    )


st.title("Résumé rapport")

chapter_id = st.selectbox(
    "Choisir un chapitre du rapport",
    options=[chapter["id"] for chapter in CHAPTERS],
    format_func=lambda value: f"{CHAPTER_BY_ID[value]['number']} — {CHAPTER_BY_ID[value]['title']}",
    index=0,
)

chapter = CHAPTER_BY_ID[chapter_id]

st.subheader(f"{chapter['number']} — {chapter['title']}")
st.markdown(
    add_reference_box(
        "Repérage",
        f"Chapitre {chapter['number']} · {chapter['pages']} · Pages liées dans l’application : {chapter['app_pages']}",
    ),
    unsafe_allow_html=True,
)

st.markdown(f"{chapter['summary']}\n\n{chapter['importance']}")
render_summary_block(chapter)

st.markdown(
    add_method_box("Figure(s) et matériau du chapitre", str(chapter["figures"])),
    unsafe_allow_html=True,
)

if chapter["formulas"]:
    st.markdown("**Formule(s) ou relation(s) clé(s)**")
    for formula in chapter["formulas"]:
        st.latex(formula)

render_chapter_visuals(chapter_id)

with st.expander("Audit logique de reconstruction", expanded=False):
    render_logic_audit()
