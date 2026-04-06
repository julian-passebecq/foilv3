
import pandas as pd
import streamlit as st

from utils import add_reference_box, configure_page, show_table

configure_page("1.1 Sommaire rapport")

st.title("Sommaire rapport")
st.markdown(
    """
Cette page donne le repérage rapide entre les chapitres du rapport, les pages PDF et les pages de l’application.
Le détail chapitre par chapitre reste sur la page `Résumé rapport`.
"""
)

st.markdown(
    add_reference_box(
        "Correspondance",
        "Le tableau ci-dessous reprend le fil du rapport, les pages PDF associées et l’endroit principal où la matière est relue dans l’application.",
    ),
    unsafe_allow_html=True,
)

show_table(
    pd.DataFrame(
        {
            "Chapitre": [str(i) for i in range(1, 20)],
            "Titre": [
                "Principe technologique",
                "Données principales du site",
                "Section du fleuve au droit du site choisi",
                "Énergie du fleuve",
                "Contraintes de navigation",
                "Section exploitable et conditions de sécurité",
                "Solutions d’ancrage",
                "Dimensions caractéristiques des hydroliennes possibles",
                "Présentation de l’hydrolienne",
                "Mise en situation et comparaison",
                "Données et hypothèses pour quantifier la production",
                "Quantification de la production et qualité",
                "Tendance évolutive avec le changement climatique",
                "Introduction pour l’évaluation économique",
                "Choix de la métrique économique et pilotage",
                "Résultats des projections économiques",
                "Externalités positives",
                "Leviers de soutien mobilisable",
                "Aspect réglementaire",
            ],
            "Pages rapport": [
                "p.4",
                "p.5 à p.7",
                "p.8 à p.9",
                "p.10",
                "p.11",
                "p.12 à p.13",
                "p.14 à p.15",
                "p.16",
                "p.17 à p.18",
                "p.19 à p.20",
                "p.21 à p.22",
                "p.23 à p.24",
                "p.25 à p.26",
                "p.27 à p.28",
                "p.29 à p.31",
                "p.32 à p.33",
                "p.34 à p.35",
                "p.36 à p.37",
                "p.38",
            ],
            "Pages application": [
                "Machine, Volet scientifique",
                "Site et données, Synthèse",
                "Implantation et navigation",
                "Volet scientifique, Synthèse",
                "Implantation et navigation",
                "Implantation et navigation, Synthèse",
                "Ancrage et cadre réglementaire",
                "Volet scientifique, Machine",
                "Machine et exploitation",
                "Machine et exploitation, Implantation et navigation",
                "Volet scientifique",
                "Volet scientifique, Synthèse",
                "Climat et prospective",
                "Économie intrinsèque, Déploiement",
                "Économie intrinsèque",
                "Économie intrinsèque",
                "Déploiement, soutiens et décision",
                "Déploiement, soutiens et décision",
                "Ancrage et cadre réglementaire",
            ],
        }
    ),
    hide_index=True,
    width="stretch",
)
