
from __future__ import annotations

import pandas as pd
import streamlit as st

from utils import (
    add_assumption_box,
    add_method_box,
    add_reference_box,
    add_remark_box,
    report_logic_checks_df,
    show_table,
)


REPERES = {
    "home": {
        "title": "Repères de construction de l’accueil",
        "items": [
            {
                "title": "Benchmark LCOE et risque",
                "source": "Rapport, chapitres 14 à 16, p.27 à p.33.",
                "report_anchor": "Le rapport distingue bien benchmark de filière, coût direct du projet et effet du financement.",
                "app_translation": "L’accueil ouvre volontairement sur le benchmark LCOE, les taux d’actualisation et les références CAPEX / coût direct.",
                "watchout": "Le benchmark n’est pas le prix du projet PK326.",
                "categories": ["Économie"],
            },
            {
                "title": "Trajectoire projet",
                "source": "Rapport, chapitre 14, p.27 à p.28.",
                "report_anchor": "La logique du dossier est prototype → démonstrateur → première ferme commerciale.",
                "app_translation": "L’application reprend cette logique sous forme de frise et de tableau synthétique.",
                "watchout": "C’est une feuille de route de lecture, pas un calendrier contractuel.",
                "categories": ["Économie"],
            },
        ],
    },
    "synthese": {
        "title": "Repères de construction de la synthèse",
        "items": [
            {
                "title": "Sélection du site et corridor utile",
                "source": "Rapport, chapitre 2, p.5 à p.7.",
                "report_anchor": "PK292 et PK326 ressortent comme les profils les plus énergétiques ; PK326 est retenu en hypothèse de travail.",
                "app_translation": "La page concentre la lecture sur le criblage, le zoom PK326 et le corridor utile d’environ 35 km.",
                "watchout": "Les cartes et synthèses visuelles sont reconstruites, pas copiées du PDF.",
                "categories": ["Site"],
            },
            {
                "title": "Section utile et compatibilité à deux machines",
                "source": "Rapport, chapitres 3, 6 et 10, p.8 à p.20.",
                "report_anchor": "La lecture prudente à BMVE(115) conduit à deux fenêtres latérales et à une implantation à deux machines hors chenal.",
                "app_translation": "L’application transforme cette lecture en budget de largeur et marge résiduelle.",
                "watchout": "Le budget latéral est un calcul applicatif fidèle au rapport, pas un tableau natif du PDF.",
                "categories": ["Implantation"],
            },
            {
                "title": "Compromis 200 kW",
                "source": "Rapport, chapitres 11 et 12, p.21 à p.24.",
                "report_anchor": "Le rapport fait ressortir ~200 kW comme compromis technico-économique autour de ~800 MWh/an par machine.",
                "app_translation": "La synthèse met côte à côte production, qualité de production et ordre de grandeur économique.",
                "watchout": "La production reste une reconstruction de pré-faisabilité.",
                "categories": ["Production", "Économie"],
            },
        ],
    },
    "site": {
        "title": "Repères de construction – site et données",
        "items": [
            {
                "title": "Carte estuarienne",
                "source": "Rapport, figure 1.",
                "report_anchor": "Le rapport montre un corridor estuarien encore soumis à l’influence de marée bien en amont du Havre.",
                "app_translation": "La carte est redessinée de manière schématique pour garder la logique spatiale sans dépendance SIG.",
                "watchout": "Ce n’est pas une carte de positionnement opérationnel.",
                "categories": ["Site"],
            },
            {
                "title": "Criblage des profils",
                "source": "Rapport, figures 2 et 3.",
                "report_anchor": "Les vitesses de pointe et la dissymétrie flot / jusant sont les éléments structurants de la sélection.",
                "app_translation": "Les sept sous-graphes sont reformulés en scatter de synthèse et en courbes lissées pour PK326.",
                "watchout": "Les courbes PK326 ne sont pas une numérisation point à point du PDF.",
                "categories": ["Site"],
            },
            {
                "title": "Salinité et extrapolation énergétique",
                "source": "Rapport, figure 4 et figure 16.",
                "report_anchor": "Le rapport conclut à une lecture quasi-douce en amont du PK330 et à une extrapolation par polynôme d’ordre 3.",
                "app_translation": "L’application réexplique ces choix pour justifier ρ = 1000 kg/m³ et la continuité de lecture énergétique.",
                "watchout": "La régression relie seulement quatre points d’ancrage.",
                "categories": ["Site", "Production"],
            },
        ],
    },
    "implantation": {
        "title": "Repères de construction – implantation et navigation",
        "items": [
            {
                "title": "Profil utile PK326",
                "source": "Rapport, figures 5 à 7.",
                "report_anchor": "La bathymétrie seule n’est pas suffisante ; il faut la relire avec les niveaux de marée.",
                "app_translation": "Le profil utile est reconstruit comme coupe de travail pour permettre les calculs géométriques.",
                "watchout": "La coupe n’est pas le maillage hydrographique brut.",
                "categories": ["Implantation"],
            },
            {
                "title": "Fenêtres d’implantation",
                "source": "Rapport, figure 9.",
                "report_anchor": "La lecture de référence retient 7,0 m de profondeur minimale et 0,5 m de garde au fond à BMVE(115).",
                "app_translation": "L’application détecte automatiquement les intervalles compatibles et calcule les largeurs.",
                "watchout": "C’est une formalisation prudente de la figure 9, pas une note d’exécution.",
                "categories": ["Implantation"],
            },
            {
                "title": "Compatibilité navigation",
                "source": "Rapport, figures 8, 12 et 13.",
                "report_anchor": "Le chenal central doit rester libre pour la navigation lourde.",
                "app_translation": "L’application sépare la lecture du chenal, le recul de 5 m et la mise en situation à deux machines.",
                "watchout": "Le navire illustratif ne remplace pas une étude de navigation.",
                "categories": ["Implantation", "Machine"],
            },
        ],
    },
    "machine": {
        "title": "Repères de construction – machine et exploitation",
        "items": [
            {
                "title": "Principe technologique",
                "source": "Rapport, chapitre 1 et chapitre 9.",
                "report_anchor": "Le foil oscillant et sa conversion mécanique sont au cœur du concept.",
                "app_translation": "Le schéma de principe est une reformulation pédagogique pour lecteur non spécialiste.",
                "watchout": "Ce n’est pas une CAO détaillée ni une cinématique complète.",
                "categories": ["Machine"],
            },
            {
                "title": "Gabarit en fonctionnement et en position relevée",
                "source": "Rapport, figures 10 et 11.",
                "report_anchor": "Les dimensions 38 × 36 m / TE 7,0 m puis 35 × 36 m / TE 1,6 m structurent toute la lecture d’implantation.",
                "app_translation": "L’application reprend ces dimensions sous forme de schémas lisibles et de tableaux opérationnels.",
                "watchout": "Les dessins sont schématiques mais les cotes utiles sont conservées.",
                "categories": ["Machine", "Implantation"],
            },
            {
                "title": "Comparaison avec technologies rotatives",
                "source": "Rapport, figure 14.",
                "report_anchor": "Le message clé est géométrique : Foil’O garde le chenal libre à production équivalente.",
                "app_translation": "L’application transforme cette comparaison en tableau et bar chart lisibles.",
                "watchout": "Il s’agit d’une comparaison stratégique, pas d’une simulation concurrentielle complète.",
                "categories": ["Machine"],
            },
        ],
    },
    "scientifique": {
        "title": "Repères de construction – volet scientifique",
        "items": [
            {
                "title": "Énergie de la section",
                "source": "Rapport, chapitre 4.",
                "report_anchor": "La section transporte ~25 à 85 MWh par marée et ~29,5 GWh/an au PK326.",
                "app_translation": "L’application rapproche l’énergie de section, le partage flot / jusant et la petite part captée par le projet.",
                "watchout": "La part captée est un indicateur pédagogique de l’app.",
                "categories": ["Production"],
            },
            {
                "title": "Courbe de puissance type",
                "source": "Rapport, figure 15.",
                "report_anchor": "La logique Vd / Vn / Vm structure le compromis de puissance nominale.",
                "app_translation": "L’application reconstruit cette loi par morceaux pour rendre le raisonnement visible.",
                "watchout": "Ce n’est pas une courbe constructeur certifiée.",
                "categories": ["Production"],
            },
            {
                "title": "Compromis de puissance et dimensionnement",
                "source": "Rapport, figures 17-18 et chapitre 8.",
                "report_anchor": "Le rapport fait ressortir 200 kW comme compromis et 36 m comme envergure de foil de référence.",
                "app_translation": "L’application rend ces calculs interactifs mais garde les paramètres de référence du rapport.",
                "watchout": "Les résultats restent de niveau avant-projet.",
                "categories": ["Production", "Machine"],
            },
        ],
    },
    "climat": {
        "title": "Repères de construction – climat et prospective",
        "items": [
            {
                "title": "Débits mensuels futurs",
                "source": "Rapport, figure 19.",
                "report_anchor": "Le rapport conclut à une baisse surtout automnale et hivernale, surtout avant 2050.",
                "app_translation": "L’application réutilise une trajectoire centrale simple pour garder la logique de lecture.",
                "watchout": "Les enveloppes de scénarios du rapport ne sont pas toutes réaffichées.",
                "categories": ["Climat"],
            },
            {
                "title": "Propagation de l’influence marine",
                "source": "Rapport, figure 20.",
                "report_anchor": "Un débit plus faible laisse mieux pénétrer le signal marin et donc la dynamique de marée.",
                "app_translation": "L’application simplifie la figure autour de trois débits représentatifs.",
                "watchout": "La courbe est une reconstruction centrale, pas une exportation brute du modèle source.",
                "categories": ["Climat"],
            },
        ],
    },
    "eco_intrinseque": {
        "title": "Repères de construction – économie intrinsèque",
        "items": [
            {
                "title": "Stades de développement",
                "source": "Rapport, chapitre 14.",
                "report_anchor": "Le rapport raisonne par maturité avant de raisonner par puissance.",
                "app_translation": "Le modèle reprend cette logique sous forme de presets Prototype / Démonstrateur / 1er commercial.",
                "watchout": "Les presets sont un outil applicatif, pas un tableau natif du PDF.",
                "categories": ["Économie"],
            },
            {
                "title": "Benchmark, CAPEX et coût direct",
                "source": "Rapport, figures 21 à 24.",
                "report_anchor": "Les repères clés sont 605 / 356 / 221 €/MWh en benchmark LCOE et 131 / 174 €/MWh au 1er commercial.",
                "app_translation": "Les courbes sont reconstruites et interpolées pour alimenter le modèle projet.",
                "watchout": "Les courbes viennent d’une saisie de points du rapport, pas d’un export numérique natif.",
                "categories": ["Économie"],
            },
            {
                "title": "Modèle projet",
                "source": "Transposition applicative des chapitres 14 à 16.",
                "report_anchor": "L’application doit permettre d’explorer des variantes tout en gardant les ordres de grandeur du rapport.",
                "app_translation": "Le modèle recalcule coût direct, composante capital, LCOE et sensibilités autour du cas actif.",
                "watchout": "Le cas standard a été corrigé pour traiter correctement le CAPEX au temps initial dans le LCOE.",
                "categories": ["Économie"],
            },
        ],
    },
    "deploiement": {
        "title": "Repères de construction – déploiement, soutiens et décision",
        "items": [
            {
                "title": "Phasage et partenariat",
                "source": "Rapport, chapitre 14.",
                "report_anchor": "Le rapport défend une logique de contrat de développement et de réduction graduelle du risque.",
                "app_translation": "La page fait le lien entre trajectoire technique, puissance et risque financier.",
                "watchout": "Cela éclaire la décision mais ne remplace pas un montage contractuel réel.",
                "categories": ["Économie"],
            },
            {
                "title": "Leviers cash et externalités",
                "source": "Rapport, chapitres 17 et 18.",
                "report_anchor": "Les aides et les externalités positives ne sont pas de même nature.",
                "app_translation": "L’application les sépare strictement : cash d’un côté, valeur élargie de décision de l’autre.",
                "watchout": "Les externalités ne doivent pas être lues comme des recettes contractuelles.",
                "categories": ["Économie"],
            },
        ],
    },
    "ancrage": {
        "title": "Repères de construction – ancrage et cadre réglementaire",
        "items": [
            {
                "title": "Hiérarchie des ancrages",
                "source": "Rapport, chapitre 7.",
                "report_anchor": "Le rapport privilégie les pieux vissés, avec le corps mort comme alternative crédible.",
                "app_translation": "La page transforme cette hiérarchie qualitative en visuel et tableau comparatif.",
                "watchout": "Le choix final reste conditionné à la reconnaissance géotechnique.",
                "categories": ["Machine"],
            },
            {
                "title": "Cadre réglementaire",
                "source": "Rapport, chapitre 19.",
                "report_anchor": "Le projet relève d’un examen au titre de l’eau et de l’environnement.",
                "app_translation": "La page reformule le cadre en séquence projet tout en restant prudente sur le régime précis.",
                "watchout": "Le régime exact dépend de la rubrique IOTA applicable et du dossier réel.",
                "categories": ["Économie"],
            },
        ],
    },
}


PAGE_LOGIC_FILTERS = {
    "home": ["Économie"],
    "synthese": ["Site", "Implantation", "Production", "Économie"],
    "site": ["Site", "Production"],
    "implantation": ["Implantation", "Machine"],
    "machine": ["Machine", "Implantation"],
    "scientifique": ["Production", "Machine"],
    "climat": ["Climat"],
    "eco_intrinseque": ["Économie"],
    "deploiement": ["Économie"],
    "ancrage": ["Machine", "Économie"],
}


CATEGORY_MAP = {
    "Site": "Site",
    "Implantation": "Implantation",
    "Production": "Production",
    "Machine": "Machine",
    "Climat": "Climat",
    "Économie": "Économie",
}


def _overview_df(page_key: str) -> pd.DataFrame:
    rows = []
    for item in REPERES.get(page_key, {}).get("items", []):
        rows.append(
            {
                "Élément": item["title"],
                "Source rapport": item["source"],
                "Point de vigilance": item["watchout"],
            }
        )
    return pd.DataFrame(rows)


def _filtered_logic_checks(page_key: str) -> pd.DataFrame:
    wanted = PAGE_LOGIC_FILTERS.get(page_key, [])
    if not wanted:
        return pd.DataFrame()
    df = report_logic_checks_df().copy()
    categories = [CATEGORY_MAP[name] for name in wanted if name in CATEGORY_MAP]
    return df[df["Catégorie"].isin(categories)].reset_index(drop=True)


def render_reperes_application(page_key: str) -> None:
    config = REPERES.get(page_key)
    if not config:
        st.info("Aucun repère configuré pour cette page.")
        return

    st.markdown(add_method_box("Comment lire cet onglet", f"{config['title']}. Il documente ce qui vient directement du rapport et ce qui est une traduction applicative."), unsafe_allow_html=True)

    overview = _overview_df(page_key)
    if not overview.empty:
        show_table(overview, hide_index=True, width="stretch")

    checks = _filtered_logic_checks(page_key)
    if not checks.empty:
        st.markdown(
            add_assumption_box(
                "Contrôles de cohérence utiles à cette page",
                "Ces contrôles vérifient que la reconstruction applicative retombe sur les ordres de grandeur structurants du rapport.",
            ),
            unsafe_allow_html=True,
        )
        show_table(
            checks[["Catégorie", "Vérification", "Référence rapport", "Valeur application", "Statut", "Commentaire"]].rename(columns={"Commentaire": "Remarque"}),
            hide_index=True,
            width="stretch",
        )


def render_reperes_construction(page_key: str) -> None:
    config = REPERES.get(page_key)
    if not config:
        st.info("Aucun repère configuré pour cette page.")
        return

    items = config["items"]
    labels = [item["title"] for item in items]
    selected = st.selectbox("Choisir un élément à détailler", labels, key=f"{page_key}_repere_select")
    item = next(item for item in items if item["title"] == selected)

    st.markdown(add_reference_box("Référence rapport", item["source"]), unsafe_allow_html=True)
    st.markdown(add_method_box("Ce que dit le rapport", item["report_anchor"]), unsafe_allow_html=True)
    st.markdown(add_assumption_box("Traduction dans l’application", item["app_translation"]), unsafe_allow_html=True)
    st.markdown(add_remark_box("Point d’attention", item["watchout"]), unsafe_allow_html=True)

    detail_df = pd.DataFrame(
        {
            "Bloc": ["Source", "Ancrage rapport", "Traduction applicative", "Vigilance"],
            "Lecture": [item["source"], item["report_anchor"], item["app_translation"], item["watchout"]],
        }
    )
    show_table(detail_df, hide_index=True, width="stretch")


def render_reperes(page_key: str, mode: str = "full") -> None:
    if mode == "application":
        render_reperes_application(page_key)
        return
    if mode == "construction":
        render_reperes_construction(page_key)
        return

    render_reperes_application(page_key)
    st.divider()
    render_reperes_construction(page_key)
