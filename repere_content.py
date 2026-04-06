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


def _item(
    *,
    section: str,
    title: str,
    source: str,
    description: str,
    report_data: list[str],
    construction: list[str],
    app_choices: list[str],
    python_functions: str,
    python_datasets: str,
    python_rendering: str,
    pipeline: str,
    physics: list[str] | None = None,
    watchouts: list[str] | None = None,
    status: str = "reconstruction contrainte",
    missing_in_report: str = "",
    risk: str = "",
    categories: list[str] | None = None,
) -> dict[str, object]:
    return {
        "section": section,
        "title": title,
        "source": source,
        "description": description,
        "report_data": report_data,
        "construction": construction,
        "app_choices": app_choices,
        "python_functions": python_functions,
        "python_datasets": python_datasets,
        "python_rendering": python_rendering,
        "pipeline": pipeline,
        "physics": physics or [],
        "watchouts": watchouts or [],
        "status": status,
        "missing_in_report": missing_in_report,
        "risk": risk,
        "categories": categories or [],
    }


REPERES = {
    "home": {
        "intro": "Cet onglet documente la manière dont la page d’accueil a été construite à partir des repères économiques les plus structurants du rapport, sans refaire toute la démonstration site par site.",
        "items": [
            _item(
                section="Vue",
                title="Vue d’ensemble benchmark et risque",
                source="Rapport p.29 à p.31 — chapitre 15, figure 21.",
                description="Bloc de cadrage économique qui pose d’emblée la différence entre benchmark de filière, coût du risque et lecture par maturité.",
                report_data=[
                    "Référence de benchmark commercial initial : 221 ± 76 €/MWh.",
                    "Taux d’actualisation retenus : 13 % prototype, 10 % démonstrateur, 7 % premier commercial.",
                    "Durée de vie cible : 20 ans ; OPEX cible : 30 €/MWh.",
                ],
                construction=[
                    "La page d’accueil n’ouvre pas par la carte ou par la coupe du site : elle ouvre volontairement par la lecture de risque et de benchmark, parce que c’est le point qui structure les chapitres 14 à 16.",
                    "Le benchmark LCOE et les taux d’actualisation sont montrés ensemble pour rappeler que la maturité technologique pèse autant que la puissance installée dans la lecture du coût.",
                    "L’accueil sert donc de sas économique : on voit d’abord le cadre de benchmark, puis seulement les références CAPEX et coût direct du projet.",
                ],
                app_choices=[
                    "La conversion en €(2025) et le cadre européen ne sont pas refaits dans l’application : ils sont repris comme résultat du rapport.",
                    "L’accueil ne mélange pas benchmark, aides et externalités afin d’éviter les contre-lectures dès la première page.",
                ],
                python_functions="`lcoe_stage_ranges()`, `plot_lcoe_ranges()`, `stages_df()`, `plot_stage_discount_rates()`.",
                python_datasets="`lcoe_stage_ranges()` contient les 3 stades, leurs moyennes, bornes centrales et bornes externes ; `stages_df()` porte les 3 taux d’actualisation retenus par le rapport.",
                python_rendering="`go.Box` pour le benchmark LCOE et `px.line` pour les taux d’actualisation, avec juxtaposition volontaire des deux lectures.",
                pipeline="Recopie des repères LCOE et des taux du rapport -> structuration en tables -> rendu de deux figures complémentaires sur la même page.",
                physics=[
                    "Le point économique repris ici est qu’un coût énergétique se lit toujours dans un cadre d’hypothèses financières et de maturité, jamais comme un nombre isolé.",
                ],
                watchouts=[
                    "Le benchmark de filière n’est pas le coût direct du projet PK326 ; il sert uniquement de repère sectoriel.",
                ],
                status="transposition chiffrée fidèle",
                missing_in_report="Le rapport donne déjà les valeurs consolidées mais pas la structure tabulaire directement exploitable par Plotly.",
                risk="Risque de sur-interprétation : faible, tant que le benchmark est bien lu comme benchmark de filière et non comme prix projet.",
                categories=["Économie"],
            ),
            _item(
                section="Vue",
                title="Vue d’ensemble CAPEX, financement et coût direct",
                source="Rapport p.32 à p.33 — chapitre 16, figures 22, 23 et 24.",
                description="Bloc qui met en regard les courbes CAPEX du rapport et le repère de coût direct du premier commercial.",
                report_data=[
                    "Cas standard premier commercial : 131 €/MWh.",
                    "Cas financé premier commercial : 174 €/MWh.",
                    "CAPEX financé lu avec un crédit couvrant 100 % du CAPEX sur 10 ans à 4 %.",
                ],
                construction=[
                    "L’accueil juxtapose les courbes CAPEX et le coût direct pour montrer le cœur du chapitre 16 : le capital n’est pas la même chose que le coût final du MWh produit.",
                    "Le cas financé est maintenu séparé parce que l’écart 131 / 174 €/MWh ne vient pas d’un simple décalage graphique mais d’un calcul de remboursement.",
                    "La courbe CAPEX affichée sur l’accueil est volontairement centrée sur le 1er commercial car c’est le stade auquel le rapport donne le repère décisionnel le plus lisible.",
                ],
                app_choices=[
                    "Les bandes ±30 % restent des plages de référence et non des promesses de résultat.",
                    "Le point sélectionné sur la courbe est figé sur un cas représentatif pour éviter une page d’accueil trop paramétrique.",
                ],
                python_functions="`capex_reference_curves_df()`, `plot_stage_capex_curve()`, `production_cost_reference_df()`, `plot_production_cost_reference()`.",
                python_datasets="`capex_reference_curves_df()` stocke les points standard et financés par stade et par puissance ; `production_cost_reference_df()` stocke les coûts directs standard / financé par stade.",
                python_rendering="Bandes `go.Scatter` pour le CAPEX, puis `go.Bar` groupé avec barres d’erreur pour le coût direct.",
                pipeline="Saisie des points de lecture issus des figures 22 à 24 -> reconstruction de bandes continues -> affichage du repère de coût direct à côté.",
                physics=[
                    "Le coût direct résulte de la combinaison capital + exploitation + production ; l’accueil rappelle cette articulation sans refaire le modèle complet.",
                ],
                watchouts=[
                    "Les courbes sont des références de pré-faisabilité ; elles ne valent ni devis ni offre industrielle.",
                ],
                status="reconstruction contrainte",
                missing_in_report="Le rapport donne des courbes mais pas une table numérique consolidée ; l’application saisit des points de lecture puis reconstruit les bandes.",
                risk="Risque de sur-interprétation : faible à moyen. Les ordres de grandeur sont solides, mais quelques écarts d’arrondi de lecture de courbe peuvent subsister.",
                categories=["Économie"],
            ),
            _item(
                section="Vue",
                title="Vue d’ensemble trajectoire projet",
                source="Rapport p.27 à p.28 — chapitre 14 ; prolongement décisionnel p.34 à p.37.",
                description="Bloc qui résume la logique prototype → démonstrateur → premier commercial et son rôle dans la décision.",
                report_data=[
                    "Prototype : 30–50 kW, TRL 6–7.",
                    "Démonstrateur : 150–250 kW, TRL 7–8.",
                    "1ère ferme commerciale : environ 5 machines, autour de 1 MW, TRL 8–9.",
                ],
                construction=[
                    "Le dernier bloc de l’accueil montre la montée en maturité, parce que le rapport explique les coûts par stade et non par seule montée en puissance installée.",
                    "La frise et le tableau associés sont une reformulation applicative du chapitre 14 : objectifs, TRL, taille typique et gate de décision.",
                    "Le lien avec les chapitres 17 et 18 reste volontairement implicite sur l’accueil ; les soutiens et externalités sont laissés aux pages dédiées.",
                ],
                app_choices=[
                    "La page d’accueil s’arrête volontairement à la trajectoire de déploiement et ne pousse pas encore les curseurs d’aide ou d’externalités.",
                ],
                python_functions="`deployment_phase_df()`, `plot_development_roadmap()`, `show_table()`.",
                python_datasets="`deployment_phase_df()` contient `Stade`, `TRL`, `Puissance_typique`, `Objectif`, `Décision_gate`, `Position`.",
                python_rendering="Frise `go.Scatter` annotée + tableau de synthèse HTML.",
                pipeline="Extraction textuelle du chapitre 14 -> structuration en table -> rendu d’une frise et d’un tableau cohérents.",
                physics=[
                    "Le rapport lie la baisse du risque à la montée en maturité ; l’accueil garde cette logique comme fil directeur.",
                ],
                watchouts=[
                    "Cette trajectoire reste un cadre de lecture ; le montage contractuel réel viendra plus tard.",
                ],
                status="schéma de lecture applicatif",
                missing_in_report="Le rapport est surtout textuel sur ce point et ne fournit pas une frise prête à l’emploi.",
                risk="Risque de sur-interprétation : modéré. La matière vient bien du rapport, mais la frise est une reformulation éditoriale.",
                categories=["Économie"],
            ),
        ],
    },
    "synthese": {
        "intro": "La synthèse décisionnelle croise plusieurs chapitres du rapport. Elle ne remplace pas leur lecture détaillée mais explique pourquoi les mêmes repères reviennent ensemble sur une page courte.",
        "items": [
            _item(
                section="Lecture",
                title="Bloc site et ressource",
                source="Rapport p.5 à p.7 — chapitre 2, figures 1 à 4.",
                description="Le haut de la page Synthèse rappelle pourquoi PK326 est retenu et quels ordres de grandeur de courant sont utilisés.",
                report_data=[
                    "PK326 : flot jusqu’à 2,00 m/s en vives eaux et 1,25 m/s en mortes eaux ; jusant jusqu’à 2,25 m/s en vives eaux et 1,50 m/s en mortes eaux.",
                    "Corridor utile de l’ordre de 35 km entre les deux meilleurs profils PK292 et PK326.",
                    "Le Landin a les courbes les plus pleines ; Courval a les pics les plus élevés.",
                ],
                construction=[
                    "Le scatter de criblage et le zoom PK326 ne servent pas à relire tous les profils ; ils servent à refaire rapidement la sélection du site dans un format plus lisible que la planche multi-graphes du PDF.",
                    "La page retient explicitement Courval comme hypothèse de travail parce que le rapport bascule ensuite toutes les démonstrations de section, machine et production sur ce profil.",
                    "Le corridor utile est ramené à quelques repères visuels pour garder une lecture courte sans perdre l’argument spatial du rapport.",
                ],
                app_choices=[
                    "Le classement visuel repose sur les pics et sur la dominance du jusant, pas sur la réaffichage des sept chroniques complètes sur la page de synthèse.",
                ],
                python_functions="`site_profiles_df()`, `plot_site_screening()`, `plot_pk326_curves()`.",
                python_datasets="`site_profiles_df()` porte les 7 profils, leurs pics de flot / jusant, PK, année, classe et indice énergétique ; `approx_velocity_curves()` reconstruit les 4 courbes Courval.",
                python_rendering="`px.scatter` pour le criblage et `go.Scatter` multi-courbes pour le zoom PK326.",
                pipeline="Saisie des profils du corridor -> calcul d’un indicateur de tri -> restitution du zoom PK326 par courbes lissées contraintes par les pics du rapport.",
                physics=[
                    "La dominance du jusant est conservée car elle pèse fortement sur l’énergie via la loi en V³.",
                ],
                watchouts=[
                    "Le bloc de synthèse résume le criblage ; il ne remplace pas la lecture détaillée des figures 2 et 3.",
                ],
                status="reconstruction contrainte",
                missing_in_report="Le rapport ne fournit pas un scatter synthétique unique ; il montre une mosaïque de sous-graphes et un zoom séparé sur Courval.",
                risk="Risque de sur-interprétation : moyen. Les ordres de grandeur sont fidèles, mais le visuel final est une composition applicative.",
                categories=["Site"],
            ),
            _item(
                section="Lecture",
                title="Bloc section et implantation latérale",
                source="Rapport p.8 à p.13 — chapitres 3 et 6 ; figures 6, 7 et 9.",
                description="Bloc qui explique pourquoi la page Synthèse affiche directement les fenêtres latérales et la compatibilité de deux machines.",
                report_data=[
                    "Niveau de référence défavorable : BMVE(115).",
                    "Profondeur minimale d’exploitation : 7,0 m à partir de BMVE(115).",
                    "Fenêtres de la figure 9 : 70 m × 7 m à bâbord et 45 m × 7 m à tribord.",
                ],
                construction=[
                    "La page reprend la coupe utile et la transforme en budget de largeur : largeur brute, largeur après recul, largeur machine, marge restante.",
                    "Le tableau de marge n’existe pas tel quel dans le rapport : c’est une formalisation applicative du raisonnement géométrique de la figure 9.",
                    "La compatibilité à deux machines est calculée à partir des deux bandes latérales, pas supposée a priori.",
                ],
                app_choices=[
                    "Le recul de 5 m vis-à-vis du chenal est gardé comme marge de lecture projet dans la mise en situation de référence.",
                ],
                python_functions="`section_profile_df()`, `compute_section_layout()`, `implantation_windows_df()`, `implantation_budget_df()`.",
                python_datasets="Profil utile reconstruit `x_m / z_cmh_m`, fenêtres latérales calculées, budget de largeur après recul et marge restante face à 36 m de largeur machine.",
                python_rendering="Coupe `go.Scatter` avec zones mises en évidence + tableaux HTML pour fenêtres et budget.",
                pipeline="Lecture de la coupe utile -> calcul du seuil fond compatible -> extraction des intervalles latéraux -> comparaison à la largeur machine.",
                physics=[
                    "La section est calibrée sur la basse mer la plus pénalisante, car c’est elle qui fixe le tirant d’eau réellement disponible.",
                ],
                watchouts=[
                    "Les marges calculées dans l’app restent des marges de pré-faisabilité, pas un implant d’exécution.",
                ],
                status="reconstruction contrainte",
                missing_in_report="Le rapport montre la logique géométrique mais pas le tableau numérique de budget latéral ; cette table est calculée dans l’application.",
                risk="Risque de sur-interprétation : moyen. La logique est fidèle, mais les marges exactes dépendent de la coupe de travail reconstruite.",
                categories=["Implantation"],
            ),
            _item(
                section="Lecture",
                title="Bloc production et part captée",
                source="Rapport p.10 puis p.21 à p.24 — chapitres 4, 11 et 12.",
                description="Bloc qui met côte à côte l’énergie de la section et la production cible d’une hydrolienne pour éviter de confondre ressource brute et énergie récupérée.",
                report_data=[
                    "Énergie de section : environ 25 à 85 MWh par marée, soit ~29,5 GWh/an.",
                    "Production cible : environ 800 MWh/an par machine autour de 200 kW.",
                    "Le jusant est plus énergétique que le flot.",
                ],
                construction=[
                    "La jauge de part captée est un ajout de l’application : elle compare la production unitaire lue sur les courbes à l’énergie annuelle de section du chapitre 4.",
                    "Le but n’est pas d’introduire une nouvelle métrique du rapport, mais de rendre tangible l’écart d’échelle entre la ressource du fleuve et l’extraction du projet.",
                    "La synthèse illustre deux machines parce que c’est le cas de mise en situation retenu par le rapport au PK326.",
                ],
                app_choices=[
                    "L’application évite ici toute confusion entre énergie transitant dans la section et énergie effectivement récupérée par une machine ou par deux machines.",
                ],
                python_functions="`river_energy_metrics()`, `plot_flot_jusant_share()`, `plot_capture_share_indicator()`, `production_curve_df()`.",
                python_datasets="Ordres de grandeur de section, partage flot / jusant, courbe de production annuelle par puissance nominale.",
                python_rendering="Barres empilées et jauges en `go.Pie`, plus tableau récapitulatif HTML.",
                pipeline="Reprise des ordres de grandeur du chapitre 4 -> recalcul de la production projet autour de 200 kW -> comparaison ressource / extraction.",
                physics=[
                    "La logique du rapport est conservée : on estime d’abord l’énergie cinétique disponible dans la veine d’eau, puis la fraction qu’un capteur borné par Vd, Vn et Vm peut récupérer.",
                ],
                watchouts=[
                    "La part captée est un indicateur pédagogique créé pour l’application ; ce n’est pas une formule explicitement donnée dans le PDF.",
                ],
                status="schéma de lecture applicatif",
                missing_in_report="Le rapport ne donne pas de jauge de capture prête à l’emploi ; il faut croiser le chapitre 4 et les figures de production pour l’obtenir.",
                risk="Risque de sur-interprétation : moyen. L’indicateur est utile pour la pédagogie, mais il ne remplace pas une modélisation d’extraction plus fine.",
                categories=["Production"],
            ),
            _item(
                section="Lecture",
                title="Bloc économie et trajectoire projet",
                source="Rapport p.27 à p.33 — chapitres 14 à 16 ; figures 21 à 24.",
                description="Bloc qui ajoute à la Synthèse le repère de coût direct premier commercial et la lecture par stades de déploiement qui figuraient auparavant dans la vue exécutive du résumé rapport.",
                report_data=[
                    "Coût direct premier commercial : 131 €/MWh hors financement et 174 €/MWh avec financement.",
                    "Lecture par stades : prototype, démonstrateur, première ferme commerciale.",
                    "Taux d’actualisation de lecture : 13 %, 10 %, 7 % selon la maturité.",
                ],
                construction=[
                    "La page Synthèse récupère deux éléments de cadrage décisionnel : le coût direct de 1er commercial et la roadmap prototype → démonstrateur → première ferme commerciale.",
                    "Le coût direct est gardé dans une forme compacte, car le rôle de la Synthèse n’est pas de refaire toute la page économique mais de rappeler le repère 131–174 €/MWh et sa signification.",
                    "La roadmap est ajoutée pour relier la faisabilité technique du site à la trajectoire projet envisagée par le rapport.",
                ],
                app_choices=[
                    "La Synthèse n’affiche pas encore les soutiens et externalités pour ne pas mélanger économie intrinsèque et économie élargie.",
                ],
                python_functions="`production_cost_reference_df()`, `plot_production_cost_reference()`, `deployment_phase_df()`, `plot_development_roadmap()`.",
                python_datasets="Repères de coût direct par stade, table de déploiement par TRL, puissance typique et gate de décision.",
                python_rendering="`go.Bar` pour le repère économique, frise `go.Scatter` pour la trajectoire projet.",
                pipeline="Extraction des repères 131 / 174 €/MWh et de la trajectoire de développement -> mise en forme compacte sur la page de synthèse.",
                physics=[
                    "La maturité technologique reste ici un paramètre de lecture aussi important que la puissance installée.",
                ],
                watchouts=[
                    "Ce bloc complète la lecture courte du dossier ; le modèle économique détaillé reste dans les pages techno-économiques.",
                ],
                status="transposition chiffrée fidèle",
                missing_in_report="Le rapport donne bien les chiffres et la logique de phase, mais pas cette composition synthétique sur une même page.",
                risk="Risque de sur-interprétation : faible à moyen. Les chiffres sont fidèles, la composition est applicative.",
                categories=["Économie"],
            ),
        ],
    },
    "site": {
        "intro": "Ici, chaque remarque doit permettre de comprendre comment la page Site a été reconstruite à partir du début du rapport : géographie, profils, courbes Courval, salinité et extrapolation énergétique.",
        "items": [
            _item(
                section="Géographie",
                title="Figure 1 — Géographie de l’estuaire et profils",
                source="Rapport p.5 — chapitre 2, figure 1 : ‘Géographie de l’estuaire de la Seine, positionnement des profils et des principales communes’.",
                description="Graphique de contexte qui montre l’axe estuarien, les communes de repère, les PK de mesure et la transition vers l’amont sous influence de marée.",
                report_data=[
                    "Communes repères reprises : Le Havre, Honfleur, Tancarville, Caudebec-en-Caux, Le Trait, Duclair, Rouen, Oissel, Pont-de-l’Arche, Val-de-Reuil, Poses.",
                    "PK repris : 243.7, 282, 292.2, 314.9, 326, 341, 371.",
                    "Phrase structurante reprise du texte : hors embouchure, l’influence de marée sur la Seine se fait sentir sur ~150 km.",
                ],
                construction=[
                    "La carte de l’application est une reconstruction légère du schéma du rapport : polyligne de Seine, communes repères, PK transmis par Haropa Port et bande de lecture salinité / influence de marée.",
                    "Le graphique n’utilise pas de fond cartographique externe, car l’objectif n’est pas la précision topographique mais la logique du dossier : situer PK326 dans un estuaire intérieur encore soumis à la marée.",
                    "Le corridor énergétique est surligné parce que le rapport articule ensuite tous les choix autour des profils PK292 et PK326.",
                ],
                app_choices=[
                    "Positions et courbure du fleuve simplifiées pour une lecture robuste dans Streamlit.",
                    "Le bandeau salinité / influence de marée est synthétique : il traduit l’idée du rapport sans reconstituer toute la figure originale.",
                ],
                python_functions="`estuary_towns_df()`, `corridor_profiles_df()`, `salinity_zonation_df()`, `plot_estuary_map()`.",
                python_datasets="Communes repères, profils PK, zonation salinité et polyligne schématique interne de la Seine.",
                python_rendering="`go.Scatter` + `shapes` pour le fleuve, les repères, les profils et les bandes salinité / influence de marée.",
                pipeline="Extraction des repères spatiaux du rapport -> construction d’une polyligne estuarienne schématique -> placement des communes et profils -> ajout du corridor utile.",
                physics=[
                    "Le concept physique important ici est que la Seine reste un estuaire de marée loin vers l’amont ; c’est ce qui rend un projet hydrolien possible dans une zone qui paraît visuellement fluviale.",
                ],
                watchouts=[
                    "Cette carte sert au raisonnement spatial. Elle n’est pas utilisable comme plan de positionnement précis.",
                ],
                status="schéma de lecture applicatif",
                missing_in_report="Le rapport ne fournit ni coordonnées géographiques exploitables ni géométrie vectorielle du fond cartographique.",
                risk="Risque de sur-interprétation : moyen. La logique spatiale est fidèle, mais la géométrie est volontairement schématique.",
                categories=["Site"],
            ),
            _item(
                section="Géographie",
                title="Figure 2 — Criblage des 7 profils de courantologie",
                source="Rapport p.5 à p.6 — chapitre 2, figure 2 : ‘Données de courantologie transmises pour différents profils entre Rouen et Le Havre’.",
                description="Graphique de sélection qui résume quels profils sont faibles, intermédiaires ou majeurs dans le corridor étudié.",
                report_data=[
                    "Le rapport dit que 4 profils sur 7 dépassent largement ±1,0 m/s sur environ 60 km entre ~PK290 et ~PK350.",
                    "Le rapport isole deux profils majeurs : Le Landin PK292 et Courval PK326.",
                    "Les valeurs de pics utilisées dans l’application sont des lectures synthétiques cohérentes avec la figure 2 et avec les chiffres explicitement donnés ensuite pour PK326.",
                ],
                construction=[
                    "Le rapport montre une mosaïque de 7 sous-graphes. L’application la traduit en un scatter plus lisible basé sur deux grandeurs comparables d’un profil à l’autre : pic de flot et pic de jusant.",
                    "Cette transformation est volontaire : on ne cherche pas à redessiner les 7 sous-graphes, mais à rendre la hiérarchie énergétique immédiate pour l’utilisateur.",
                    "Le classement ‘Secondaire / Corridor / Site majeur’ est une reformulation applicative du commentaire du rapport.",
                ],
                app_choices=[
                    "La comparaison repose sur les pics et non sur l’intégrale temporelle complète de chaque courbe.",
                ],
                python_functions="`site_profiles_df()`, `plot_site_screening()`.",
                python_datasets="Table des 7 profils avec `Pic_flot_m_s`, `Pic_jusant_m_s`, `PK_km`, `Classe`, `Indice_énergétique`.",
                python_rendering="`px.scatter` avec seuils ±1,0 m/s et taille de point liée à l’indice énergétique.",
                pipeline="Lecture des profils du rapport -> saisie des pics -> calcul d’un indice énergétique simple -> restitution dans un graphique de screening.",
                physics=[
                    "Ce visuel garde le critère énergétique principal du rapport : l’amplitude de courant, surtout lorsqu’elle dépasse durablement ±1,0 m/s.",
                ],
                watchouts=[
                    "Le scatter sert à sélectionner. Il ne doit pas être lu comme un substitut détaillé des graphes marégraphiques d’origine.",
                ],
                status="reconstruction contrainte",
                missing_in_report="Le rapport ne fournit pas de tableau synthétique commun des 7 profils ; il montre seulement une planche multi-graphes.",
                risk="Risque de sur-interprétation : moyen. Le classement est robuste, mais la forme temporelle de chaque courbe n’apparaît plus ici.",
                categories=["Site"],
            ),
            _item(
                section="Courants",
                title="Figure 3 — Courbes type de courant à Courval PK326",
                source="Rapport p.6 — chapitre 2, figure 3 : ‘Courbes type de courant à Courval (pk 326) pour différents coefficients de marée et un débit de Seine compris entre 250 et 350 m³/s’.",
                description="Reconstruction lissée des courbes type de courant à PK326, destinée à montrer la chronologie d’une marée, l’ordre des coefficients 45 à 115 et surtout la dissymétrie flot / jusant qui rend Courval intéressant.",
                report_data=[
                    "Débit de Seine associé à la figure : entre 250 et 350 m³/s.",
                    "Flot : 1,25 m/s en mortes eaux et 2,00 m/s en vives eaux.",
                    "Jusant : 1,50 m/s en mortes eaux et 2,25 m/s en vives eaux.",
                ],
                construction=[
                    "L’application trace quatre courbes lissées pour les coefficients 45, 70, 95 et 115. Elles sont reconstruites pour reproduire la logique du rapport : départ en jusant, inversion rapide, plateau de flot, retour au jusant plus énergique.",
                    "Les courbes ne viennent pas d’une numérisation point par point du PDF. Elles sont reconstruites pour conserver les pics, l’ordre des coefficients et la dissymétrie flot / jusant explicitée par le texte.",
                    "Le sélecteur de coefficient sert uniquement à mettre en évidence une courbe ; il ne change aucune hypothèse de fond.",
                ],
                app_choices=[
                    "Reconstruction volontairement lissée pour garder la lecture du rapport sans prétendre restituer l’enregistrement brut ADCP.",
                ],
                python_functions="`approx_velocity_curves()`, `plot_pk326_curves()`.",
                python_datasets="Axe temps `0–12 h` et quatre séries de vitesse reconstruites à partir des pics explicites du rapport.",
                python_rendering="`go.Scatter` multi-courbes avec mise en avant d’un coefficient sélectionné.",
                pipeline="Reprise des pics flot / jusant fournis par le rapport -> reconstruction d’une forme de marée lissée -> affichage comparatif des 4 coefficients.",
                physics=[
                    "Le rapport explique que le jusant est plus constant et plus élevé du fait du débit du fleuve qui s’y ajoute ; cette dissymétrie est conservée dans l’application.",
                    "Cette différence est importante parce que l’énergie cinétique varie comme V³.",
                ],
                watchouts=[
                    "Le graphe de l’application traduit le comportement, pas la mesure brute horodatée.",
                ],
                status="reconstruction contrainte",
                missing_in_report="Le rapport donne les coefficients et les pics extrêmes, mais pas la série temporelle numérique complète de chaque courbe.",
                risk="Risque de sur-interprétation : moyen à élevé si on lit la courbe comme une mesure brute. Il faut la lire comme une reconstruction contrainte.",
                categories=["Site"],
            ),
            _item(
                section="Milieu et énergie",
                title="Figure 4 — Salinité et hypothèse d’eau douce",
                source="Rapport p.7 — chapitre 2, figure 4 : ‘Variabilité de la salinité dans l’estuaire de la Seine’.",
                description="Graphique qui justifie l’hypothèse de masse volumique 1000 kg/m³ et une lecture plus favorable de durabilité au PK326.",
                report_data=[
                    "Le rapport indique que la salinité en amont du PK330 est extrêmement faible, inférieure à 0,5 g/L.",
                    "Le rapport en déduit une masse volumique de 1000 kg/m³ pour les calculs.",
                    "La donnée est aussi mobilisée comme argument favorable pour la durabilité des structures immergées.",
                ],
                construction=[
                    "L’application traduit la carte longitudinale de salinité en un profil simple selon le PK afin de rendre explicite la zone limnique amont et le seuil important autour de PK330.",
                    "Le visuel sert surtout à expliquer la décision de calcul : au PK326 et en amont, l’eau est traitée comme quasi douce dans le modèle énergétique.",
                ],
                app_choices=[
                    "Le gradient de salinité est simplifié en lecture longitudinale ; la cartographie détaillée aval n’est pas reconstituée.",
                ],
                python_functions="`plot_salinity_zonation()`.",
                python_datasets="Profil longitudinal simplifié `PK / Salinité_g_L` et seuil limnique 0,5 g/L.",
                python_rendering="Courbe `go.Scatter` + bandes colorées par domaine de salinité.",
                pipeline="Reprise de la conclusion physique du rapport -> traduction en profil longitudinal simplifié -> mise en évidence du seuil limnique.",
                physics=[
                    "Le lien physique retenu est double : densité de l’eau pour la formule de puissance, et environnement limnique plus favorable à la durabilité des structures que la zone saline aval.",
                ],
                watchouts=[
                    "Ce graphe ne fait pas une hydrodynamique saline complète ; il sert à justifier une hypothèse de calcul du rapport.",
                ],
                status="schéma de lecture applicatif",
                missing_in_report="Le rapport donne une carte de zonation mais pas une table longitudinale numérique directement exploitable.",
                risk="Risque de sur-interprétation : modéré. La conclusion physique est fidèle, mais le profil longitudinal est simplifié.",
                categories=["Site"],
            ),
            _item(
                section="Milieu et énergie",
                title="Figure 16 — Extrapolation énergétique selon le coefficient de marée",
                source="Rapport p.21 — chapitre 11, figure 16 : ‘Exemple de résultat de l’extrapolation mathématique utilisée pour définir l’énergie de la veine d’eau’.",
                description="Graphique qui explique comment l’application passe de quatre coefficients documentés à une ressource annuelle continue.",
                report_data=[
                    "Quatre points repris : coefficients 45, 70, 95 et 115.",
                    "Énergie du courant reconstruite : environ 6000, 8300, 9000 et 9750 Wh/m²/marée.",
                    "Le rapport indique une régression polynomiale d’ordre 3 avec R² = 1 sur les quatre points transmis.",
                ],
                construction=[
                    "Le rapport ne donne que quatre coefficients documentés au PK326. L’application reprend cette logique et ajuste un polynôme d’ordre 3 sur quatre points pour reconstituer une courbe continue énergie/coefficient.",
                    "La courbe affichée dans l’app est donc une interpolation à partir des points du rapport, pas une nouvelle base de mesure.",
                    "Le tableau sous le graphe rappelle explicitement quels sont les quatre points utilisés, pour que la construction reste transparente.",
                ],
                app_choices=[
                    "L’application garde exactement la même famille de modèle que le rapport : polynôme d’ordre 3 propre au profil PK326.",
                ],
                python_functions="`resource_extrapolation_df()`, `fit_resource_energy_curve()`, `plot_resource_energy_fit()`.",
                python_datasets="Les 4 couples coefficient -> énergie saisis dans `resource_extrapolation_df()`.",
                python_rendering="Points en marqueurs carrés + courbe continue `go.Scatter` issue du polynôme d’ordre 3.",
                pipeline="Saisie des 4 points visibles -> ajustement polynomiale -> échantillonnage d’une courbe continue -> affichage simultané des points et du fit.",
                physics=[
                    "Le lien physique amont reste la formule de puissance cinétique P = 1/2 ρ S V³, ensuite intégrée sur la durée d’une marée pour obtenir une énergie.",
                ],
                watchouts=[
                    "R² = 1 signifie seulement que quatre points sont exactement rejoints par un polynôme d’ordre 3 ; cela ne transforme pas la courbe en vérité universelle hors de ce cadre.",
                ],
                status="reconstruction contrainte",
                missing_in_report="Le rapport ne donne que quatre points et une équation de régression, pas une série continue déjà échantillonnée.",
                risk="Risque de sur-interprétation : moyen. La logique est fidèle, mais la continuité entre les points reste une interpolation.",
                categories=["Site", "Production"],
            ),
        ],
    },
    "implantation": {
        "intro": "Ces remarques documentent la chaîne exacte de construction de la page Implantation : niveaux d’eau, profil utile, règle de profondeur, budget latéral puis mise en situation.",
        "items": [
            _item(
                section="Bathymétrie et marée",
                title="Figure 6 — Niveaux de haute et basse mer",
                source="Rapport p.8 à p.9 — chapitre 3, figure 6 : ‘Niveaux de Haute et Basse Mer (0/CMH) pour différents coefficients de marée et pour un débit de la Seine à Poses de 400 m³/s’.",
                description="Graphique longitudinal qui donne, station par station, les niveaux de BM et PM pour plusieurs coefficients de marée, afin de pouvoir ajouter une hauteur d’eau réelle au fond bathymétrique.",
                report_data=[
                    "Débit de référence de la figure : 400 m³/s à Poses.",
                    "Stations reprises : Balise A, Honfleur, Tancarville, St Léonard, Vatteville, Caudebec, Heurteauville, Jumièges, Duclair, Val des Leux, La Bouille, Petit Couronne, Rouen, Oissel, Elbeuf.",
                    "Lecture PK326 / St Léonard : BMVE(115) ≈ 2,8 m / CMH et PMVE(115) ≈ 8,4 m / CMH.",
                ],
                construction=[
                    "L’application reconstruit explicitement les familles de courbes BM / PM pour les coefficients 115, 80, 65 et 35, car ce sont elles qui servent ensuite à dimensionner la coupe utile au PK326.",
                    "Le visuel est construit comme une courbe par station, non comme un simple rappel des deux chiffres BMVE / PMVE à PK326, afin de montrer que ces chiffres viennent bien d’une lecture le long de l’estuaire.",
                    "Le point de lecture important pour la suite est St Léonard / PK326, matérialisé comme repère spécifique.",
                ],
                app_choices=[
                    "Les courbes de l’application sont une restitution lisible de la figure 6 ; elles servent surtout à verrouiller les niveaux utilisés ensuite dans la coupe utile.",
                ],
                python_functions="`tide_levels_df()`, `plot_tide_levels()`.",
                python_datasets="`tide_levels_df()` contient `Station`, `BM_115`, `PM_115`, `BM_80`, `PM_80`, `BM_65`, `PM_65`, `BM_35`, `PM_35`.",
                python_rendering="Huit traces `go.Scatter` lignes + marqueurs, avec un `vline` et une annotation sur St Léonard / PK326.",
                pipeline="Lecture station par station des courbes BM / PM du rapport -> saisie du tableau -> tracé direct des huit séries sans interpolation supplémentaire.",
                physics=[
                    "Le rapport souligne que le débit du fleuve influe sur le marnage mais de façon marginale à ce niveau de lecture ; l’application garde donc la figure 6 comme référence principale des niveaux d’eau.",
                ],
                watchouts=[
                    "Le graphe n’est pas une base de marée opérationnelle pour l’exploitation ; il sert à reconstruire le raisonnement de faisabilité du rapport.",
                ],
                status="reconstruction contrainte",
                missing_in_report="Le rapport donne une figure multi-courbes par station, mais pas un tableau numérique prêt à tracer ou à recalculer.",
                risk="Risque de sur-interprétation : modéré tant qu’on garde en tête la différence entre données reprises littéralement et données reconstruites.",
                categories=["Implantation"],
            ),
            _item(
                section="Bathymétrie et marée",
                title="Figure 7 — Profil utile construit à partir de la bathymétrie et du marnage",
                source="Rapport p.8 à p.9 — chapitre 3, figures 5 puis 7 : profil PK ~326,7 construit à partir des données bathymétriques et des données de niveaux de marée.",
                description="Graphique de coupe transversale qui transforme un levé bathymétrique technique en profil exploitable pour navigation et implantation.",
                report_data=[
                    "Bathymétrie précise transmise pour PK326, octobre 2025.",
                    "Référence bathymétrique : 0 / CMH.",
                    "Chenal central : 110 m.",
                    "Surcote à ajouter au fond bathymétrique à PK326 : environ 2,8 m aux plus basses eaux et 8,4 m aux plus hautes eaux pour coefficient 115.",
                ],
                construction=[
                    "L’application ne redessine pas le maillage hydrographique de la figure 5. Elle reprend sa conséquence utile : la coupe transversale opérationnelle déjà reconstruite en figure 7 dans le rapport.",
                    "Sur cette coupe, l’app réaffiche 0/CMH, BMVE(115), PMVE(115) et le chenal central 110 m, car ce sont les quatre repères qui structurent toute la logique d’implantation.",
                    "La forme du fond est volontairement simplifiée en profil continu : l’objectif est de raisonner implantation, pas de faire un traitement hydrographique complet.",
                ],
                app_choices=[
                    "La coupe affichée dans l’application suit le profil utile du rapport, avec une géométrie lissée pour permettre les calculs de fenêtres exploitables.",
                ],
                python_functions="`_section_control_points()`, `section_profile_df()`, `plot_section_profile()`.",
                python_datasets="Profil utile `x_m / z_cmh_m` reconstruit à partir de points de contrôle internes ; constantes `BMVE_115`, `PMVE_115`, `CHANNEL_X0`, `CHANNEL_X1`.",
                python_rendering="Coupe `go.Scatter` remplie vers 0/CMH + lignes de niveau + rectangle du chenal.",
                pipeline="Lecture de la coupe utile du rapport -> définition de points de contrôle représentatifs -> interpolation linéaire à pas constant -> affichage des repères de niveau et du chenal.",
                physics=[
                    "Le rapport rappelle que la bathymétrie seule ne donne pas la hauteur d’eau réelle : il faut lui superposer le marnage pour raisonner tirant d’eau disponible.",
                ],
                watchouts=[
                    "La coupe de l’application n’est pas un levé exhaustif ; c’est une coupe de travail pour la pré-faisabilité.",
                ],
                status="reconstruction contrainte",
                missing_in_report="Le rapport montre le maillage bathymétrique brut et la coupe utile, mais ne fournit pas un profil numérique continu prêt à être recalculé.",
                risk="Risque de sur-interprétation : moyen à élevé si on lit la coupe comme une bathymétrie brute ; il faut la lire comme un profil utile reconstruit.",
                categories=["Implantation"],
            ),
            _item(
                section="Section exploitable",
                title="Figure 9 — Fenêtres d’implantation et règle de profondeur",
                source="Rapport p.12 à p.13 — chapitre 6, figure 9 : ‘Limite d’implantation selon les hypothèses proposées’.",
                description="Graphique qui traduit en géométrie les hypothèses de sécurité retenues par le rapport pour délimiter la partie du profil réellement exploitable.",
                report_data=[
                    "Hypothèse clé : profondeur minimale d’exploitation 7,0 m à partir de BMVE(115).",
                    "Marge conservée vis-à-vis du fond : plus de 0,5 m pour intégrer un batillage.",
                    "Rectangles de la figure 9 : 70 m × 7 m à bâbord et 45 m × 7 m à tribord.",
                ],
                construction=[
                    "Dans le rapport, la conclusion est montrée par deux rectangles d’implantation. Dans l’application, cette logique est rendue calculable : on prend le profil utile, on impose un niveau d’eau de référence, une profondeur minimale d’exploitation et une garde au fond, puis on calcule les intervalles latéraux compatibles.",
                    "Autrement dit, l’app transforme le rectangle-limite du PDF en règle géométrique explicite, afin que l’utilisateur voie ce qui vient du rapport et ce qui vient du calcul applicatif.",
                    "Le tableau de fenêtres et le budget de largeur sont donc des produits de l’application, mais ils appliquent strictement les hypothèses du rapport.",
                ],
                app_choices=[
                    "L’outil interactif autorise la variation du niveau d’eau, de la profondeur limite et de la garde au fond pour tester la robustesse de la conclusion du rapport.",
                    "Le recul de 5 m par rapport au chenal est traité séparément comme marge projet supplémentaire dans la lecture de référence.",
                ],
                python_functions="`compute_section_layout()`, `_below_threshold_intervals()`, `_subtract_exclusion()`, `plot_exploitable_section()`.",
                python_datasets="Profil utile calculé, `threshold_cmh_m`, fenêtres latérales `x0_m / x1_m / Largeur_m` et paramètres `water_level`, `depth_limit`, `clearance`.",
                python_rendering="Coupe `go.Scatter` avec `vrect` sur les fenêtres et annotations de largeur.",
                pipeline="Calcul du seuil fond compatible = niveau d’eau - profondeur minimale - garde -> détection des intervalles compatibles -> retrait de la zone du chenal -> affichage des fenêtres.",
                physics=[
                    "La logique physique est celle du tirant d’eau disponible en condition défavorable. Le rapport précise aussi qu’en théorie le battement des foils peut être réduit ou arrêté temporairement si la hauteur d’eau devient insuffisante.",
                ],
                watchouts=[
                    "La fenêtre calculée par l’application n’est pas un nouvel avis de faisabilité ; c’est une reformulation mathématisée de la prudence retenue dans le rapport.",
                ],
                status="reconstruction contrainte",
                missing_in_report="Le rapport donne les hypothèses et les rectangles finaux, mais pas la procédure numérique complète reliant automatiquement le profil aux fenêtres latérales.",
                risk="Risque de sur-interprétation : moyen. La règle est fidèle, mais les largeurs exactes reposent sur la coupe de travail reconstruite.",
                categories=["Implantation"],
            ),
            _item(
                section="Mise en situation",
                title="Navigation, recul au chenal et mise en situation à deux machines",
                source="Rapport p.10 à p.11 puis p.19 à p.20 — chapitre 5, figure 8 ; chapitre 10, figures 12 à 14.",
                description="Ensemble de visuels qui montre pourquoi le chenal central reste libre et comment deux machines sont placées latéralement hors trafic.",
                report_data=[
                    "Le rapport mentionne des navires Large Range de 228 m × 32 m et des minéraliers de 290 m × 45 m transitant régulièrement.",
                    "Passage prudent évoqué pour les très grands navires : de l’ordre de 60 m.",
                    "Figures 12 et 13 : deux hydroliennes latérales hors chenal au PK326, en BMVE(115).",
                ],
                construction=[
                    "Le schéma de navigation simplifie la contrainte du chapitre 5 : le chenal central est laissé libre car le rapport juge son exploitation incompatible avec le trafic lourd.",
                    "La mise en situation reprend ensuite le gabarit machine des figures 10 et 11, puis le place de part et d’autre du chenal dans la coupe utile, avec un recul latéral de lecture de 5 m utilisé dans la version de référence de l’application.",
                    "La version avec navire dans le profil est un outil pédagogique : elle matérialise la compatibilité visuelle, mais le navire illustratif de 24 m n’est pas le gabarit dimensionnant du trafic maximal.",
                ],
                app_choices=[
                    "Le budget latéral après recul est calculé pour comparer directement largeur utile et largeur machine de 36 m.",
                ],
                python_functions="`draw_plan_view_schema()`, `implantation_budget_df()`, `plot_window_budget()`, `plot_two_machine_profile()`, `plot_navigation_clearance()`.",
                python_datasets="Fenêtres brutes et après recul, largeur machine 36 m, recul projet 5 m, navire illustratif 24 m.",
                python_rendering="Schémas en `shapes`, budget latéral en barres groupées, mise en situation en coupe par rectangles sur la coupe du fleuve.",
                pipeline="Reprise des contraintes de navigation -> calcul des marges après recul -> placement des machines dans les fenêtres latérales -> illustration avec et sans navire.",
                physics=[
                    "La contrainte n’est pas hydrodynamique seulement ; elle est aussi géométrique et de sécurité de navigation. C’est pourquoi l’application sépare bien énergie théorique du chenal et implantation réellement acceptable.",
                ],
                watchouts=[
                    "Le navire rouge dans l’app sert à lire une compatibilité, pas à valider une navigation réelle.",
                ],
                status="schéma de lecture applicatif",
                missing_in_report="Le rapport donne les gabarits et les mises en situation, mais pas un modèle paramétrique de recul et de budget latéral.",
                risk="Risque de sur-interprétation : moyen. La compatibilité de principe est bien montrée, mais l’étude de navigation réelle reste hors du champ de l’application.",
                categories=["Implantation", "Machine"],
            ),
        ],
    },
    "machine": {
        "intro": "Ces remarques expliquent comment la page Machine transforme la description technologique et les figures de présentation en visuels de lecture opérationnelle.",
        "items": [
            _item(
                section="Principe et gabarit",
                title="Principe technologique Foil’O",
                source="Rapport p.4 puis p.17 — chapitre 1 et chapitre 9.",
                description="Schéma de principe qui explique le mouvement d’un foil oscillant et sa conversion mécanique vers une génératrice.",
                report_data=[
                    "Description textuelle reprise : mise en oscillation d’un hydrofoil immergé dans un courant et transformation du mouvement, via un système mécanique breveté, en rotation continue pour une génératrice.",
                    "Le rapport insiste sur le pilotage paramétrique du battement et sur l’absence de structure fixe extérieure soutenant le plan porteur dans la configuration proposée.",
                ],
                construction=[
                    "Ce schéma n’existe pas tel quel dans le rapport : il synthétise la description textuelle du chapitre 1 et la logique d’ensemble des figures 10 et 11 pour rendre le principe lisible à un lecteur non spécialiste.",
                    "Le dessin montre volontairement peu d’éléments : ligne d’eau, foil, supports, chaîne mécanique. Le but n’est pas la fidélité CAO mais la compréhension du principe de récupération d’énergie.",
                ],
                app_choices=[
                    "Schéma interprétatif, volontairement simplifié et non dépendant de détails brevetaires.",
                ],
                python_functions="`draw_oscillating_foil_principle()`, `technology_principles_df()`.",
                python_datasets="Table textuelle des principes technologiques + schéma construit directement en `shapes` Plotly.",
                python_rendering="Schéma fonctionnel avec `go.Figure`, `shapes` et annotations.",
                pipeline="Extraction textuelle du principe -> organisation des points clés dans une table -> dessin d’un schéma fonctionnel simplifié.",
                physics=[
                    "Le principe physique repris est la capture d’une partie de l’énergie cinétique du courant par un foil oscillant, puis sa conversion mécanique en électricité.",
                ],
                watchouts=[
                    "Ce visuel explique le principe ; il ne documente pas toute la cinématique ni tous les organes mécaniques décrits comme brevetés par le rapport.",
                ],
                status="schéma de lecture applicatif",
                missing_in_report="Le rapport est surtout textuel sur ce point et ne fournit pas un schéma pédagogique simplifié prêt à l’emploi.",
                risk="Risque de sur-interprétation : moyen. Le principe est fidèle, mais le dessin reste un support pédagogique.",
                categories=["Machine"],
            ),
            _item(
                section="Principe et gabarit",
                title="Figure 10 — Gabarit machine en fonctionnement",
                source="Rapport p.17 — chapitre 9, figure 10 : ‘Présentation de l’hydrolienne en fonctionnement’.",
                description="Schéma volumétrique de restitution de la machine de référence du rapport, avec exactement les dimensions utiles qui structurent ensuite les pages Implantation et Synthèse.",
                report_data=[
                    "Longueur : 38,0 m.",
                    "Largeur : 36,0 m.",
                    "Tirant d’eau maximal : 7,0 m ; tirant d’air : 9,8 m.",
                    "Passage central : largeur 16,2 m ; tirant d’eau maximal 6,6 m ; tirant d’air maximal 8,7 m.",
                ],
                construction=[
                    "Le rapport fournit une CAO à quatre vues. L’application en extrait ce qui sert réellement au raisonnement de faisabilité : longueur, largeur, tirant d’eau, tirant d’air et passage central.",
                    "Le schéma de l’application est donc une reconstruction volumétrique simple destinée à rendre ces dimensions immédiatement visibles dans l’app.",
                    "Quand l’app parle d’implantation, de marges latérales ou de compatibilité à deux machines, elle parle bien de cette machine-là et pas d’un proxy dimensionnel différent.",
                ],
                app_choices=[
                    "Le mode ‘Fonctionnement’ de l’application réaffiche uniquement les cotes utiles à la faisabilité ; il ne reproduit pas la CAO complète de la figure 10.",
                ],
                python_functions="`machine_dimensions()`, `draw_machine_schema(mode='fonctionnement')`, `machine_operating_points_df()`.",
                python_datasets="Dictionnaire centralisant les dimensions en fonctionnement et tableau des points opérationnels.",
                python_rendering="Schéma machine par `shapes` Plotly, complété par métriques Streamlit et tableaux HTML.",
                pipeline="Reprise des cotes du rapport -> centralisation dans `machine_dimensions()` -> dessin simplifié du gabarit en fonctionnement.",
                physics=[
                    "Le rapport décrit ici une configuration Duale bi-foil : deux modules de soutien, deux foils en série et production possible au flot comme au jusant.",
                ],
                watchouts=[
                    "Le schéma n’est pas une vue d’ingénierie détaillée ; il sert de gabarit de lecture pour les autres pages.",
                ],
                status="transposition chiffrée fidèle",
                missing_in_report="Le rapport donne les dimensions et la CAO, mais pas une structure applicative simplifiée en shapes Plotly.",
                risk="Risque de sur-interprétation : faible à moyen. Les cotes utiles sont fidèles ; seule la forme graphique est simplifiée.",
                categories=["Machine", "Implantation"],
            ),
            _item(
                section="Exploitation",
                title="Figure 11 — Position relevée sécurité / maintenance",
                source="Rapport p.17 à p.18 — chapitre 9, figure 11 : ‘Position de Sécurité, d’entretien ou de remorquage’.",
                description="Visuel qui montre pourquoi le mode relevé est traité comme une fonction d’exploitation majeure et non comme un détail de présentation.",
                report_data=[
                    "Longueur : 35,0 m.",
                    "Largeur : 36,0 m.",
                    "Tirant d’eau : 1,6 m ; tirant d’air : 12,7 m.",
                    "Fonctions citées : inspection, dégagement d’objet, sécurité, remorquage en faible profondeur, stockage / réparation.",
                ],
                construction=[
                    "L’application propose un second mode d’affichage pour la machine afin de faire apparaître clairement la différence géométrique entre exploitation et position relevée.",
                    "Le tableau comparatif sous le schéma sert à matérialiser ce que le rapport explique par texte : la machine change fortement de tirant d’eau et de tirant d’air lorsqu’elle relève ses foils.",
                    "Le mode relevé est traité comme un mode d’exploitation à part entière car c’est aussi un argument économique et opérationnel fort du rapport.",
                ],
                app_choices=[
                    "La page machine donne au mode relevé la même visibilité qu’au mode fonctionnement pour éviter de le faire passer pour un détail secondaire.",
                ],
                python_functions="`machine_dimensions()`, `draw_machine_schema(mode='maintenance')`, `machine_operating_points_df()`.",
                python_datasets="Dimensions de maintenance et tableau des usages opérationnels associés.",
                python_rendering="Même squelette graphique que le mode fonctionnement, avec foils relevés et annotations spécifiques.",
                pipeline="Reprise des cotes de la figure 11 -> représentation simplifiée en position relevée -> tableau des conséquences opérationnelles.",
                physics=[
                    "Le bénéfice physique du mode relevé est de diminuer très fortement l’exposition hydrodynamique et le tirant d’eau lorsque l’on n’est plus en phase de production.",
                ],
                watchouts=[
                    "L’application montre l’état relevé, pas la séquence mécanique complète du relevage.",
                ],
                status="transposition chiffrée fidèle",
                missing_in_report="Le rapport donne les cotes et l’idée du relevage, mais pas la comparaison interactive des deux états dans l’application.",
                risk="Risque de sur-interprétation : faible à moyen. Les cotes sont fidèles, la représentation mécanique est volontairement simplifiée.",
                categories=["Machine"],
            ),
            _item(
                section="Comparaison",
                title="Figure 14 — Comparaison avec hélices et rotors",
                source="Rapport p.19 à p.20 — chapitre 10, figure 14 : ‘Comparaison géométrique de solutions à production égale et à même tirant d’eau’.",
                description="Visuel comparatif qui justifie l’intérêt géométrique de Foil’O dans un profil contraint par un chenal de navigation.",
                report_data=[
                    "Hypothèses pour les hélices : Cp = 0,404 ; diamètre D = 6,0 m ; espacement minimal = 25 % de D.",
                    "Hypothèses pour les rotors transverses : Cp = 0,31 ; diamètre D = 6,0 m ; espacement minimal = 60 % de D.",
                    "Le rapport indique qu’il faut 10 hydroliennes à hélice pour la puissance d’une hydrolienne Foil’O, donc 20 pour deux machines ; et 4 rotors de 30 m pour deux machines Foil’O équivalentes.",
                ],
                construction=[
                    "L’application ne refait pas une simulation concurrentielle complète. Elle reprend le message géométrique du rapport et le traduit en nombre d’éléments actifs équivalents et en empiètement sur la section.",
                    "Le tableau associé explicite ce qui vient du texte du rapport : pour une capacité productive comparable, les solutions rotatives deviennent beaucoup plus diffuses dans le profil.",
                ],
                app_choices=[
                    "Le graphique compare des configurations équivalentes en production à l’échelle du profil, pas des rendements théoriques isolés.",
                ],
                python_functions="`technology_comparison_df()`, `plot_technology_comparison()`.",
                python_datasets="Table de comparaison : solution, configuration équivalente, éléments actifs équivalents, empiètement sur le chenal, obstacle aux débris.",
                python_rendering="Bar chart + tableau comparatif HTML.",
                pipeline="Extraction des hypothèses de comparaison -> structuration en tableau -> restitution visuelle de l’empiètement relatif et du nombre d’éléments.",
                physics=[
                    "Le point physique clé repris du rapport est qu’une grande surface active peut être captée par le concept Foil’O sans multiplier les obstacles dans la section comme le font les systèmes rotatifs comparés.",
                ],
                watchouts=[
                    "La comparaison est géométrique et stratégique. Elle ne vaut pas re-simulation détaillée de technologies concurrentes.",
                ],
                status="schéma de lecture applicatif",
                missing_in_report="Le rapport donne une comparaison de principe, mais pas un tableau numérique concurrentiel prêt à afficher.",
                risk="Risque de sur-interprétation : moyen. La conclusion géométrique est fidèle, mais l’application ne re-simule pas les technologies concurrentes.",
                categories=["Machine"],
            ),
        ],
    },
    "scientifique": {
        "intro": "Ces remarques expliquent comment la page scientifique a été construite à partir des chapitres 4, 8, 11 et 12 du rapport.",
        "items": [
            _item(
                section="Énergie du fleuve",
                title="Chapitre 4 — Énergie de la veine d’eau et énergie de section",
                source="Rapport p.10 — chapitre 4 : ‘Énergie du fleuve’.",
                description="Graphiques qui distinguent l’énergie brute transitant dans la section du fleuve et l’énergie qu’un projet hydrolien peut réellement prélever.",
                report_data=[
                    "Formule donnée au rapport : Pve(t,C) = 1/2 × ρ × S × V(t,C)^3.",
                    "Masse volumique retenue : 1000 kg/m³.",
                    "Section moyenne utilisée : ~3565 m² au niveau médian.",
                    "Énergie de section : environ 85 à 25 MWh par marée et ~29,5 GWh/an.",
                ],
                construction=[
                    "L’application repart de la formule de puissance cinétique donnée dans le rapport et de la lecture énergétique selon le coefficient de marée, puis transforme cela en un graphe d’énergie de section empilé flot / jusant.",
                    "Le but n’est pas de refaire tout le calcul du rapport en CFD, mais de rendre explicite la chaîne de calcul : vitesse -> énergie par m² et par marée -> énergie de section -> comparaison au projet.",
                    "La jauge de part captée par le projet est un ajout de l’application pour matérialiser l’écart d’échelle entre la ressource du fleuve et la production des machines.",
                ],
                app_choices=[
                    "Les barres par coefficient sont construites comme ordres de grandeur cohérents avec la plage 25–85 MWh/marée donnée par le rapport.",
                    "La part captée est calculée pour deux machines de référence, en cohérence avec la mise en situation du rapport.",
                ],
                python_functions="`river_energy_metrics()`, `river_energy_by_coefficient_df()`, `project_capture_share_df()`, `plot_river_energy_section()`, `plot_capture_share_indicator()`.",
                python_datasets="Constantes énergétiques de section, répartition flot / jusant, production projet et part captée.",
                python_rendering="Barres empilées pour l’énergie de section et jauge `go.Pie` pour la part captée.",
                pipeline="Reprise des ordres de grandeur du chapitre 4 -> ventilation flot / jusant -> comparaison à la production des machines de référence.",
                physics=[
                    "La loi en V³ est centrale : une petite hausse de vitesse modifie fortement la puissance cinétique disponible.",
                    "Le rapport insiste aussi sur le fait qu’il s’agit d’une approximation de section moyenne, car la distribution spatiale V(t,C,x,z) n’est pas connue.",
                ],
                watchouts=[
                    "L’application reprend volontairement un calcul d’ordre de grandeur. Elle ne prétend pas remplacer une intégration détaillée de la vitesse sur toute la section.",
                ],
                status="schéma de lecture applicatif",
                missing_in_report="Le rapport donne les ordres de grandeur et la formule, mais pas une comparaison visuelle directe et homogène entre ressource de section et extraction projet.",
                risk="Risque de sur-interprétation : moyen. Le raisonnement est fidèle, mais il reste de niveau ordre de grandeur.",
                categories=["Production"],
            ),
            _item(
                section="Hypothèses de production",
                title="Figure 15 — Courbe de puissance type du capteur",
                source="Rapport p.21 — chapitre 11, figure 15 : ‘Formule et courbe de récupération type d’un capteur d’énergie cinétique’.",
                description="Graphique générique qui explique comment le capteur passe d’une loi cinétique en V³ à une production plafonnée par la puissance nominale.",
                report_data=[
                    "Vitesse de démarrage retenue : Vd = 0,5 m/s.",
                    "Vitesse d’arrêt retenue en première hypothèse : Vm = 2,25 m/s.",
                    "Coefficient de puissance moyen retenu : Cp = 0,57.",
                ],
                construction=[
                    "L’application construit une courbe pièce par pièce : zéro avant Vd, montée cubique jusqu’à Vn, plateau à Pn entre Vn et Vm, puis arrêt au-delà de Vm.",
                    "Ce tracé n’est pas numérisé à partir de la figure du rapport ; c’est une reformulation pédagogique de la logique I / II / III / IV décrite dans le PDF.",
                    "Les curseurs Vd, Vn, Vm et Pn servent à faire sentir le compromis constructeur, mais la valeur de référence affichée correspond aux hypothèses du rapport.",
                ],
                app_choices=[
                    "La courbe affichée est volontairement générique : elle explique la logique de saturation, pas une loi constructeur certifiée.",
                ],
                python_functions="`build_power_curve()`, `plot_power_curve()`.",
                python_datasets="DataFrame `Vitesse_m_s / Puissance_kW` calculé sur une grille régulière de vitesses.",
                python_rendering="Courbe `go.Scatter` avec lignes verticales `Vd`, `Vn`, `Vm` et annotations de zone.",
                pipeline="Choix des paramètres de vitesse et de puissance -> génération d’une loi par morceaux -> affichage pédagogique de la courbe type.",
                physics=[
                    "Formule reprise du rapport : P = 1/2 × ρ × S × Cp × V(t,C)^3, ensuite bornée par Vd, Vn et Vm.",
                ],
                watchouts=[
                    "Le graphe n’est pas un test de performance machine. Il sert à comprendre la structure des calculs des figures 16 à 18.",
                ],
                status="schéma de lecture applicatif",
                missing_in_report="Le rapport donne une figure conceptuelle et des hypothèses de seuils, mais pas une table numérique vitesse -> puissance.",
                risk="Risque de sur-interprétation : modéré. La logique est fidèle, mais la courbe reste une reformulation pédagogique.",
                categories=["Production"],
            ),
            _item(
                section="Production et qualité",
                title="Figures 17 et 18 — Production annuelle, facteur de charge et productivité spécifique",
                source="Rapport p.23 à p.24 — chapitre 12, figures 17 et 18.",
                description="Ensemble de courbes re-tracé à partir du jeu de points du rapport pour montrer le vrai compromis de choix de puissance nominale.",
                report_data=[
                    "Plage de puissance étudiée : 100 à 300 kW.",
                    "Production annuelle d’environ 500 à 900 MWh/an par machine sur cette plage.",
                    "À 200 kW : production autour de 800 MWh/an, facteur de charge > 0,47 et environ 4117 h/an équivalent pleine puissance.",
                    "Le rapport souligne qu’entre 250 et 300 kW le gain n’est que d’environ 25 MWh, contre ~180 MWh entre 100 et 150 kW.",
                ],
                construction=[
                    "L’application reprend le jeu de points du rapport pour tracer trois courbes ensemble : production annuelle, facteur de charge et productivité spécifique.",
                    "C’est important car le rapport ne choisit pas 200 kW à partir d’une seule courbe ; il le choisit parce que la production continue d’augmenter mais de moins en moins, tandis que la qualité d’usage de la puissance installée baisse.",
                    "L’utilisateur peut déplacer un curseur de puissance pour relire exactement la zone 100–300 kW traitée dans le rapport.",
                ],
                app_choices=[
                    "Les courbes de l’application reprennent les points du rapport et les relient proprement ; elles n’extrapolent pas au-delà de la plage utile du PDF.",
                    "L’app corrige aussi l’unité éditoriale lorsque le PDF écrit ‘MW’ alors que le raisonnement de la figure et le contexte montrent qu’il faut lire des MWh/an.",
                ],
                python_functions="`production_curve_df()`, `annual_mwh_from_nominal_power()`, `capacity_factor_from_nominal_power()`, `specific_productivity_from_nominal_power()`, `plot_production_tradeoff()`, `plot_load_factor_curve()`, `plot_specific_productivity_curve()`.",
                python_datasets="Table `Pn_kW`, `Facteur_charge`, `Production_annuelle_MWh`, `Productivite_specifique_MWh_kW_an`.",
                python_rendering="Trois courbes `go.Scatter` lignes + marqueurs, plus métriques Streamlit du point sélectionné.",
                pipeline="Saisie des points du rapport -> calcul des variables dérivées -> interpolation entre points -> affichage conjoint des trois lectures de compromis.",
                physics=[
                    "Le compromis vient du fait qu’une machine plus ‘haute en nominal’ capte mieux les pointes, mais passe une part plus faible du temps à puissance nominale, d’où la baisse du facteur de charge et de la productivité spécifique.",
                ],
                watchouts=[
                    "Le rapport lui-même rappelle que ces résultats restent théoriques tant que Cp et la distribution de vitesse dans le profil ne sont pas consolidés.",
                ],
                status="reconstruction contrainte",
                missing_in_report="Le rapport montre des courbes et des points repères, mais pas une table numérique exportable complète prête à être manipulée dans l’application.",
                risk="Risque de sur-interprétation : moyen. Le compromis 200 kW est robuste, mais les courbes restent des reconstructions de pré-développement.",
                categories=["Production"],
            ),
            _item(
                section="Dimensionnement",
                title="Chapitre 8 — Dimensionnement géométrique du foil",
                source="Rapport p.16 — chapitre 8 : ‘Dimensions caractéristiques des hydroliennes possibles’.",
                description="Bloc qui montre comment l’envergure 36 m et la corde ~1,8 m ne sont pas choisies arbitrairement mais déduites de rapports adimensionnels et d’une profondeur disponible Hm.",
                report_data=[
                    "Hypothèses adimensionnelles retenues : 2Ho/c = 3,00 ; E/c = 0,85 ; A = 20.",
                    "Profondeur maximale de travail utilisée : Hm ≈ 7,0 m.",
                    "Résultat rapporté : c ≈ 1,82 m ; amplitude 2Ho ≈ 5,4 m ; E ≈ 1,5 m ; profondeur à l’axe ≈ 6,9 m ; L ≈ 36,0 m.",
                ],
                construction=[
                    "L’application reprend exactement les deux relations écrites dans le rapport et les rend interactives : d’une part la relation entre profondeur disponible Hm, amplitude de battement et enfoncement, d’autre part la relation entre allongement et envergure.",
                    "Le but est que l’utilisateur voie que le gabarit machine affiché plus loin découle d’un calcul, et non d’une simple illustration CAO.",
                ],
                app_choices=[
                    "Les curseurs laissent varier Hm et les rapports adimensionnels, mais la position de référence est celle du rapport.",
                ],
                python_functions="`dimensionnement_foil()`.",
                python_datasets="Dictionnaire de sortie : `c`, `amplitude`, `E`, `axis_depth`, `L`, plus les paramètres d’entrée.",
                python_rendering="Métriques Streamlit et formules LaTeX, sans figure complexe supplémentaire.",
                pipeline="Reprise des équations du rapport -> recalcul direct des dimensions -> exposition interactive des grandeurs calculées.",
                physics=[
                    "Relations reprises : 2Ho/c + E/c = Hm/c et L = A × c.",
                    "Le rapport rappelle que ces rapports pourront évoluer en avant-projet ; ils doivent donc être lus comme un premier dimensionnement compatible avec la technologie Duale.",
                ],
                watchouts=[
                    "Ce module explique le dimensionnement du concept. Il ne remplace pas un calcul structurel détaillé des foils et des appuis.",
                ],
                status="transposition chiffrée fidèle",
                missing_in_report="Le rapport donne les équations et la solution de référence, mais pas un module de recalcul interactif.",
                risk="Risque de sur-interprétation : faible à moyen. Les équations sont fidèles ; l’interactivité ne doit pas faire oublier qu’il s’agit d’un premier dimensionnement.",
                categories=["Production", "Machine"],
            ),
        ],
    },
    "climat": {
        "intro": "Ces remarques expliquent comment la page Climat reprend la logique prospective du rapport sans prétendre la réactualiser par d’autres sources.",
        "items": [
            _item(
                section="Débits de la Seine",
                title="Figure 19 — Débits mensuels présents, 2050 et 2100",
                source="Rapport p.25 — chapitre 13, figure 19 : ‘Simulation des débits mensuels de la Seine pour différentes échelles de temps’.",
                description="Graphique de traduction hydraulique du changement climatique pour le projet : il ramène la prospective du rapport à la variable utile pour PK326, le débit saisonnier de la Seine.",
                report_data=[
                    "Le rapport conclut à une baisse nette des débits surtout en périodes automnale et hivernale.",
                    "Il précise que le décrochage principal apparaît avant 2050 puis s’amplifie peu ensuite.",
                    "La période printemps-été reste du même ordre de grandeur que le présent selon la lecture du rapport.",
                ],
                construction=[
                    "Le PDF montre des enveloppes de scénarios et des moyennes d’ensemble. L’application n’en garde que les trois courbes centrales Présent / 2050 / 2100 pour rendre la lecture stratégique immédiate.",
                    "Autrement dit, l’app simplifie la figure 19 : elle ne recopie pas les enveloppes min/max ni les écarts-types, elle en extrait le message central qui alimente la suite du raisonnement du rapport.",
                ],
                app_choices=[
                    "Les valeurs mensuelles présentes dans l’application sont des reconstructions centrales cohérentes avec la forme de la figure 19, non une extraction fine des enveloppes de modèle.",
                ],
                python_functions="`climate_monthly_flow_df()`, `plot_climate_flows()`.",
                python_datasets="Trois séries mensuelles `Présent`, `2050`, `2100`.",
                python_rendering="Graphique multi-courbes `go.Scatter` lignes + marqueurs.",
                pipeline="Lecture du signal central du rapport -> ressaisie de trois chroniques mensuelles cohérentes -> tracé des tendances présentes et futures.",
                physics=[
                    "Le rapport utilise ce graphe pour montrer qu’une baisse du débit du fleuve réduit son opposition à la marée sur une partie importante de l’année.",
                ],
                watchouts=[
                    "Les enveloppes de dispersion du PDF ne sont pas reprises ; seule la tendance centrale est gardée.",
                ],
                status="reconstruction contrainte",
                missing_in_report="Le rapport donne des courbes et des enveloppes, mais pas de séries numériques complètes ni les jeux de données des modèles source.",
                risk="Risque de sur-interprétation : moyen à élevé si on lit les séries comme une sortie brute de modèle. Elles doivent être lues comme des reconstructions centrales.",
                categories=["Climat"],
            ),
            _item(
                section="Propagation marine",
                title="Figure 20 — Propagation de l’influence marine selon le débit",
                source="Rapport p.26 — chapitre 13, figure 20 : ‘Impact de l’élévation du niveau marin sur le niveau de pleine mer le long de l’estuaire de la Seine’.",
                description="Graphique mécaniste qui explique pourquoi une baisse du débit de Seine peut conserver, voire renforcer, la propagation de l’influence marine vers l’amont.",
                report_data=[
                    "Débits repris : 400, 1200 et 2000 m³/s à Poses.",
                    "Le rapport montre qu’à faible débit la surcote marine se propage beaucoup plus loin dans l’estuaire.",
                    "Il montre au contraire une forte atténuation amont quand le débit du fleuve est élevé.",
                ],
                construction=[
                    "La figure du rapport distingue plusieurs débits et plusieurs coefficients de marée. L’application simplifie cette lecture pour mettre l’accent sur le paramètre jugé dominant par le rapport : le débit à Poses.",
                    "Le graphe de l’application garde donc trois familles de courbes représentatives — 400, 1200 et 2000 m³/s — afin que la logique reste lisible sans surcharger la page.",
                ],
                app_choices=[
                    "L’application met l’accent sur l’effet du débit et n’expose pas séparément toutes les variantes de coefficient de marée de la figure originale.",
                ],
                python_functions="`marine_signal_df()`, `plot_marine_signal()`.",
                python_datasets="Séries par PK pour `Q400_m3_s`, `Q1200_m3_s`, `Q2000_m3_s`.",
                python_rendering="Graphique multi-courbes `go.Scatter` avec axe des PK inversé.",
                pipeline="Lecture des courbes dominantes du rapport -> ressaisie de trois familles par débit -> affichage comparatif aval / amont.",
                physics=[
                    "Le rapport résume deux mécanismes : 1) le débit du fleuve amortit l’onde de marée ; 2) la hausse du niveau marin augmente la profondeur disponible et réduit les pertes par frottement sur le fond.",
                ],
                watchouts=[
                    "La courbe de l’application est une reconstruction centrale, pas une exportation brute du modèle hydro-estuarien source.",
                ],
                status="reconstruction contrainte",
                missing_in_report="Le rapport donne des courbes et un mécanisme, mais pas une table numérique directement exploitable pour chaque PK et chaque cas.",
                risk="Risque de sur-interprétation : moyen à élevé si on lit les points comme une donnée brute. Il faut les lire comme une restitution centrale du mécanisme du rapport.",
                categories=["Climat"],
            ),
        ],
    },
    "eco_intrinseque": {
        "intro": "Ces remarques décrivent comment la page Économie intrinsèque reprend le cadre économique du rapport et le transforme en modèle paramétrable sans changer sa logique.",
        "items": [
            _item(
                section="Cadre et hypothèses",
                title="Chapitre 14 — Phasage par stade de développement",
                source="Rapport p.27 à p.28 — chapitre 14 : ‘Introduction pour l’évaluation économique’.",
                description="Tableau qui rappelle que le rapport raisonne d’abord par maturité de projet, puis seulement par puissance installée.",
                report_data=[
                    "Prototype réduit : 30–50 kW, TRL 6–7.",
                    "Démonstrateur : 150–250 kW, TRL 7–8.",
                    "1ère ferme commerciale : environ 5 machines, autour de 1 MW installé, TRL 8–9.",
                ],
                construction=[
                    "L’application transforme le texte du chapitre 14 en trois presets de projet : Prototype, Démonstrateur, 1er commercial.",
                    "Chaque preset fixe une plage de puissance cohérente, un nombre de machines de référence et un taux d’actualisation correspondant au stade de risque du rapport.",
                    "C’est ce choix qui évite de mélanger dans un même modèle des objets économiques qui n’ont pas la même maturité.",
                ],
                app_choices=[
                    "Le prototype est traité à part dans l’application, car la courbe 100–300 kW de production du rapport n’est pas adaptée à un objet 30–50 kW.",
                ],
                python_functions="`stages_df()`, `reference_project_presets()`, `seed_project_state_defaults()`, `sync_stage_defaults()`.",
                python_datasets="Tables de stades, presets de puissance, nombre de machines et paramètres par défaut du modèle projet.",
                python_rendering="Tableaux Streamlit et logique de presets ; pas de visuel unique natif du rapport.",
                pipeline="Extraction textuelle du chapitre 14 -> structuration en presets pilotant le modèle projet -> utilisation dans les onglets de la page économique.",
                physics=[],
                watchouts=[
                    "Cette structuration ne calcule rien à elle seule ; elle sert à empêcher les contre-lectures économiques.",
                ],
                status="schéma de lecture applicatif",
                missing_in_report="Le rapport est textuel sur le phasage et ne fournit pas de presets directement réutilisables dans l’interface.",
                risk="Risque de sur-interprétation : faible à moyen. La logique de fond est fidèle ; la forme preset est applicative.",
                categories=["Économie"],
            ),
            _item(
                section="Référentiels rapport",
                title="Figure 21 — Benchmark LCOE et taux d’actualisation",
                source="Rapport p.29 à p.31 — chapitre 15, figure 21.",
                description="Graphiques qui distinguent benchmark sectoriel et paramètres financiers de pilotage du risque.",
                report_data=[
                    "1er stade : 605 ± 178 €/MWh.",
                    "2nd stade : 356 ± 119 €/MWh.",
                    "Stade commercial initial : 221 ± 76 €/MWh.",
                    "Taux d’actualisation retenus : 13 % prototype, 10 % démonstrateur, 7 % quasi-maturité / premier commercial.",
                ],
                construction=[
                    "L’application reprend la figure 21 comme benchmark de filière, pas comme coût propre de Foil’O.",
                    "Elle la met volontairement à côté des taux d’actualisation 13 %, 10 % et 7 % pour que l’utilisateur voie que le risque de maturité est un paramètre structurant du modèle.",
                    "Les valeurs affichées dans l’application sont les valeurs déjà converties en €(2025) et cadre européen par le rapport ; l’app n’ajoute pas une nouvelle conversion.",
                ],
                app_choices=[
                    "Le benchmark LCOE reste séparé du coût direct projet, pour éviter de faire dire au benchmark sectoriel ce qu’il ne dit pas.",
                ],
                python_functions="`lcoe_stage_ranges()`, `plot_lcoe_ranges()`, `stages_df()`, `plot_stage_discount_rates()`.",
                python_datasets="Plages LCOE par stade et taux d’actualisation par maturité.",
                python_rendering="`go.Box` pour le benchmark et `px.line` pour le risque financier.",
                pipeline="Saisie des repères benchmark et des taux -> structuration en tables -> affichage parallèle des deux vues.",
                physics=[],
                watchouts=[
                    "Le LCOE de la filière ne doit pas être lu comme le prix direct du MWh Foil’O sur le site.",
                ],
                status="transposition chiffrée fidèle",
                missing_in_report="Le rapport donne les valeurs consolidées mais pas la structure de boxplot ni la juxtaposition immédiate avec les taux.",
                risk="Risque de sur-interprétation : faible tant que benchmark et coût projet restent bien séparés.",
                categories=["Économie"],
            ),
            _item(
                section="Référentiels rapport",
                title="Figures 22, 23 et 24 — CAPEX standard, CAPEX financé et coût direct",
                source="Rapport p.32 à p.33 — chapitre 16, figures 22, 23 et 24.",
                description="Ensemble de courbes de référence qui structure la partie économique de l’application : CAPEX standard, CAPEX financé, CAPEX spécifique et coût direct de production.",
                report_data=[
                    "Hypothèses de base rappelées : durée de vie 20 ans ; OPEX 30 €/MWh ; crédit 100 % du CAPEX sur 10 ans à 4 % dans le cas financé.",
                    "Figure 24 : premier commercial à 131 €/MWh hors financement et 174 €/MWh avec financement.",
                    "Figure 22 : courbes de CAPEX par stade, standard et financé, avec bandes ±30 %.",
                ],
                construction=[
                    "L’application reprend les courbes de CAPEX par stade comme courbes de référence, puis les couple à une production annuelle et à un OPEX pour reconstruire un coût direct projet paramétrable.",
                    "Le point important est le cas financé : l’app ne se contente pas d’afficher une courbe ‘financed’. Elle reprend le principal financé puis calcule le coût total des remboursements sur 10 ans à 4 %, afin de rester cohérente avec la logique du rapport et avec l’écart 131 / 174 €/MWh au premier commercial.",
                    "La figure de CAPEX spécifique par kW est gardée séparée parce qu’elle répond à une autre question que la figure de CAPEX total : l’économie d’échelle du capital intensif.",
                ],
                app_choices=[
                    "Les bandes ±30 % sont conservées comme plages de référence, non comme garantie de résultat.",
                    "L’utilisateur peut appliquer un ajustement CAPEX autour de la référence pour tester la sensibilité du projet sans sortir du cadre du rapport.",
                ],
                python_functions="`capex_reference_curves_df()`, `specific_capex_reference_df()`, `production_cost_reference_df()`, `plot_stage_capex_curve()`, `plot_specific_capex()`, `plot_production_cost_reference()`, `interpolate_capex_reference()`, `loan_annual_payment()`, `loan_total_payment()`.",
                python_datasets="Points CAPEX standard / financé par stade, CAPEX spécifique dérivé, coûts directs standard / financé.",
                python_rendering="Bandes `go.Scatter`, courbes spécifiques `go.Scatter` et barres groupées `go.Bar` avec erreurs.",
                pipeline="Lecture des points de puissance et de coût du rapport -> reconstruction de bandes -> calculs dérivés CAPEX spécifique et coût direct.",
                physics=[],
                watchouts=[
                    "Ces courbes sont des repères de pré-faisabilité. Elles ne valent ni devis ni offre industrielle.",
                ],
                status="reconstruction contrainte",
                missing_in_report="Le rapport donne des courbes et des plages, mais pas une table numérique consolidée unique pour tous les stades, puissances, bornes et variantes standard / financé.",
                risk="Risque de sur-interprétation : faible à moyen. Les points structurants sont fidèles ; de petits écarts peuvent subsister via arrondis et interpolation.",
                categories=["Économie"],
            ),
            _item(
                section="Modèle projet / Sensibilités",
                title="Modèle projet et sensibilités",
                source="Transposition applicative des chapitres 14 à 16.",
                description="Bloc propre à l’application qui permet d’explorer des variantes cohérentes sans réécrire toute la logique du rapport.",
                report_data=[
                    "La production liée est construite à partir des figures 17 et 18 pour les stades démonstrateur et commercial.",
                    "Pour le prototype, l’application emploie des cas de productivité spécifiques séparés, car le rapport ne fournit pas une courbe dédiée 30–50 kW de même nature.",
                ],
                construction=[
                    "Le modèle prend comme entrées : stade, puissance par machine, nombre de machines, mode standard ou financé, CAPEX relatif, OPEX, durée de vie et taux d’actualisation.",
                    "La production est soit liée automatiquement aux courbes du rapport, soit saisie manuellement pour explorer un cas particulier ; cette distinction est explicitement signalée dans l’interface.",
                    "Les graphes de sensibilité montrent ensuite quels paramètres bougent le plus le coût direct et le LCOE autour du cas actif.",
                ],
                app_choices=[
                    "Le modèle et les sensibilités sont des outils ajoutés dans l’application pour la discussion ; ils ne sont pas des tableaux du rapport d’origine.",
                    "Le calcul standard du LCOE a été corrigé pour traiter le CAPEX au temps initial, sans dégrader la lecture globale du rapport.",
                ],
                python_functions="`get_project_inputs_from_state()`, `project_state()`, `current_project_state()`, `plot_reference_vs_model_band()`, `plot_project_sensitivity_tornado()`, `plot_lcoe_discount_sensitivity()`, `plot_power_production_link()`.",
                python_datasets="État Streamlit du projet actif + références CAPEX / production / coûts relues depuis `utils.py`.",
                python_rendering="Métriques Streamlit, graphiques de comparaison et sensibilités Plotly.",
                pipeline="Relire les entrées utilisateur -> relier ou non la production aux courbes du rapport -> recalculer coût direct et LCOE -> faire varier une hypothèse à la fois pour les sensibilités.",
                physics=[],
                watchouts=[
                    "Le modèle reste fidèle au cadre du rapport, mais il simplifie nécessairement un calendrier financier réel et un montage de dette complet.",
                ],
                status="schéma de lecture applicatif",
                missing_in_report="Le rapport ne donne pas de modèle interactif prêt à l’emploi, ni de matrice de sensibilités recalculable à la volée.",
                risk="Risque de sur-interprétation : modéré. Le moteur est cohérent avec le rapport, mais il produit des sorties applicatives qui n’existent pas telles quelles dans le PDF.",
                categories=["Économie"],
            ),
        ],
    },
    "deploiement": {
        "intro": "Ces remarques décrivent comment la page Déploiement prolonge l’économie intrinsèque vers une lecture de décision plus large, sans mélanger les natures de valeur.",
        "items": [
            _item(
                section="Phasage et partenariat",
                title="Phasage et partenariat",
                source="Rapport p.27 à p.28 — chapitre 14 : cadre de partenariat, contrat de développement, phasage du projet.",
                description="Visuels qui traduisent le chapitre 14 en feuille de route lisible : montée en maturité, réduction du risque et points de passage décisionnels.",
                report_data=[
                    "Stades : prototype, démonstrateur, 1ère ferme commerciale.",
                    "Taux d’actualisation associés : 13 %, 10 %, 7 %.",
                    "Logique contractuelle mentionnée : co-développement, partage du risque et financement partiel du développement par le partenaire site / client.",
                ],
                construction=[
                    "La roadmap de l’application n’est pas une relecture libre : elle reformule le contrat de développement en trois stades opérationnels avec gates de décision visibles.",
                    "Le diagramme puissance / risque met côte à côte la montée en puissance typique et la baisse du taux d’actualisation, parce que c’est exactement cette logique que le rapport porte dans sa partie économique.",
                ],
                app_choices=[
                    "La roadmap simplifie la contractualisation réelle en quelques étapes lisibles ; elle sert à structurer la décision, pas à figer un montage contractuel final.",
                ],
                python_functions="`deployment_phase_df()`, `stage_power_risk_df()`, `plot_development_roadmap()`, `plot_stage_power_risk()`.",
                python_datasets="Stades de développement, puissance typique, TRL, taux d’actualisation.",
                python_rendering="Frise `go.Scatter` annotée et graphique croisé puissance / risque.",
                pipeline="Structuration du chapitre 14 -> création d’une roadmap -> croisement avec la baisse du risque financier.",
                physics=[],
                watchouts=[
                    "Ce bloc parle de trajectoire projet, pas encore d’équilibre économique final.",
                ],
                status="schéma de lecture applicatif",
                missing_in_report="Le rapport expose le phasage et le partenariat, mais pas une frise ni un diagramme puissance / risque prêts à l’emploi.",
                risk="Risque de sur-interprétation : modéré. Le cadre est fidèle, mais la représentation graphique est applicative.",
                categories=["Économie"],
            ),
            _item(
                section="Soutiens et externalités",
                title="Leviers cash — aides, soutien production, CEE, soutiens territoriaux",
                source="Rapport p.36 à p.37 — chapitre 18 : ‘Leviers de soutien mobilisable’.",
                description="Graphiques qui isolent ce qui agit réellement sur le cash-flow du projet.",
                report_data=[
                    "Aides CAPEX : 20 à 50 % du CAPEX éligible.",
                    "Soutien à la production : 50 à 150 €/MWh.",
                    "CEE : 5 à 20 €/MWh quand mobilisables.",
                    "Soutiens territoriaux : 5 à 15 % du CAPEX.",
                ],
                construction=[
                    "L’application reprend les plages du rapport et les transforme en curseurs. Les aides CAPEX et soutiens territoriaux sont appliqués uniquement à la composante capital du coût direct, pas à tout le coût du MWh : c’est un point important de construction.",
                    "Le soutien à la production et les CEE sont ensuite ajoutés comme leviers aval en €/MWh. La page les sépare des externalités positives pour éviter toute confusion entre recette et valeur stratégique.",
                ],
                app_choices=[
                    "Les pourcentages CAPEX sont convertis en €/MWh en utilisant la composante capital du cas économique actif ; c’est une construction applicative destinée à parler le même langage que le coût direct.",
                ],
                python_functions="`support_capex_ranges_df()`, `support_revenue_ranges_df()`, `compute_support_scenario()`, `plot_support_capex_ranges()`, `plot_support_revenue_ranges()`, `plot_support_value_breakdown()`.",
                python_datasets="Plages de soutiens CAPEX, leviers revenus et contributions recalculées du scénario actif.",
                python_rendering="Barres d’intervalle et breakdown en `px.bar`.",
                pipeline="Saisie des fourchettes du rapport -> conversion des % CAPEX en €/MWh via la composante capital -> ajout des soutiens revenus.",
                physics=[],
                watchouts=[
                    "Les curseurs représentent des ordres de grandeur indicatifs du rapport. Ils ne valent pas éligibilité acquise.",
                ],
                status="schéma de lecture applicatif",
                missing_in_report="Le rapport donne les fourchettes, mais pas un moteur homogénéisé en €/MWh pour comparer plusieurs scénarios.",
                risk="Risque de sur-interprétation : modéré. Les plages sont fidèles, mais leur conversion dépend du cas projet actif.",
                categories=["Économie"],
            ),
            _item(
                section="Soutiens et externalités",
                title="Externalités positives — valeur élargie de décision",
                source="Rapport p.34 à p.35 — chapitre 17 : ‘Prise en compte des externalités positives et évaluations’.",
                description="Graphique qui reprend les quatre familles d’externalités du rapport sans les faire passer pour des recettes contractuelles.",
                report_data=[
                    "Résilience et sécurité d’approvisionnement : 5–10 €/MWh.",
                    "Réduction de la volatilité des prix : 5–15 €/MWh.",
                    "Externalités environnementales non climatiques : 3–8 €/MWh.",
                    "Diversification stratégique : 3–7 €/MWh.",
                ],
                construction=[
                    "L’application garde une séparation stricte entre leviers cash et externalités positives. C’est précisément pour éviter le brouillage de lecture : une externalité ne doit pas être lue comme un prix de vente ou une subvention.",
                    "Les quatre postes sont affichés séparément, puis additionnés seulement dans une lecture élargie de décision.",
                ],
                app_choices=[
                    "La page traite ces valeurs comme ‘valeur de décision’ et non comme ‘cash’. C’est un choix de structure central de l’application.",
                ],
                python_functions="`externalities_ranges_df()`, `plot_externalities_ranges()`.",
                python_datasets="Table à quatre postes `Poste / Min / Max`.",
                python_rendering="Barres horizontales d’intervalle en `go.Bar`.",
                pipeline="Saisie directe des 4 postes du rapport -> affichage en intervalles -> réemploi dans le scénario de décision.",
                physics=[],
                watchouts=[
                    "La monétisation de ces postes est plus fragile que celle d’un CAPEX ou d’un OPEX ; elle sert à élargir la décision, pas à contractualiser un revenu.",
                ],
                status="transposition chiffrée fidèle",
                missing_in_report="Le rapport donne déjà les ordres de grandeur ; l’application les remet seulement sous forme graphique distincte des leviers cash.",
                risk="Risque de sur-interprétation : faible à moyen. Les fourchettes sont fidèles, mais leur usage doit rester décisionnel et non contractuel.",
                categories=["Économie"],
            ),
            _item(
                section="Conclusion",
                title="Waterfall de décision",
                source="Synthèse applicative des chapitres 16, 17 et 18.",
                description="Graphique propre à l’application qui met en séquence coût intrinsèque, aides, leviers cash et valeur élargie.",
                report_data=[
                    "Base utilisée : coût direct issu du chapitre 16, soutiens du chapitre 18, externalités du chapitre 17.",
                    "Lecture réseau inflationné 20 ans : ajout applicatif cohérent avec le passage du rapport qui rappelle que le coût relatif dépend aussi de l’évolution du prix d’achat réseau.",
                ],
                construction=[
                    "Le waterfall n’est pas une figure du rapport : il est construit pour rendre visible la logique de lecture correcte du dossier. On part du coût direct intrinsèque, on applique d’abord les aides CAPEX, puis les soutiens revenus, puis seulement les externalités positives.",
                    "Cette séquence est importante : elle évite de mélanger dès le départ ce qui relève du projet intrinsèque et ce qui relève d’une politique de soutien ou d’un bénéfice stratégique élargi.",
                ],
                app_choices=[
                    "La comparaison à un achat réseau inflationné est explicitement laissée comme lecture de contexte, pas comme prix contractuel.",
                ],
                python_functions="`compute_support_scenario()`, `relative_cost_vs_grid_inflation()`, `plot_decision_waterfall()`, `support_scenarios_matrix_df()`, `plot_support_scenario_comparison()`.",
                python_datasets="Résultat détaillé du scénario de soutien actif et matrice de scénarios types.",
                python_rendering="`go.Waterfall` + graphique comparatif de scénarios.",
                pipeline="Calculer coût initial, aides CAPEX, soutiens cash, externalités -> ordonner les effets -> afficher le passage du coût intrinsèque à la lecture élargie.",
                physics=[],
                watchouts=[
                    "Le waterfall aide la décision. Il ne remplace ni un business plan complet ni un montage juridique de soutien.",
                ],
                status="schéma de lecture applicatif",
                missing_in_report="Le rapport donne les briques de décision séparément, mais pas une figure waterfall déjà construite.",
                risk="Risque de sur-interprétation : modéré. L’outil est très utile, mais il reste une composition analytique de l’application.",
                categories=["Économie"],
            ),
        ],
    },
    "ancrage": {
        "intro": "Ces remarques expliquent comment la page Ancrage / Réglementaire convertit les chapitres 7 et 19 du rapport en visuels de lecture projet.",
        "items": [
            _item(
                section="Ancrage",
                title="Chapitre 7 — Hiérarchie des solutions d’ancrage",
                source="Rapport p.14 à p.15 — chapitre 7 : ‘Solutions d’ancrage’.",
                description="Graphique comparatif qui transforme la liste textuelle du rapport en hiérarchie de lecture entre les options possibles.",
                report_data=[
                    "Le rapport exclut en première analyse le duc d’Albe.",
                    "Il juge le corps mort envisageable et potentiellement économique.",
                    "Il donne un avantage à la solution pieux vissés dans le contexte supposé du site : efforts de traction importants et fond probablement constitué d’alluvions sur roche crayeuse.",
                ],
                construction=[
                    "Le rapport décrit plusieurs solutions : duc d’Albe, corps mort, pieux vissés, caisson de succion et solution mixte. L’application les convertit en tableau comparatif et en barre de priorité relative pour rendre la préférence du rapport immédiatement lisible.",
                    "Le score de priorité n’est pas une donnée du rapport ; c’est une traduction de son raisonnement qualitatif, où les pieux vissés arrivent en tête et le corps mort reste une alternative solide.",
                ],
                app_choices=[
                    "La ‘priorité relative’ est un indicateur applicatif pour hiérarchiser visuellement des conclusions textuelles du rapport.",
                ],
                python_functions="`anchoring_options_df()`, `plot_anchoring_priority()`.",
                python_datasets="Table des solutions d’ancrage avec `Solution`, `Priorité_relative`, `Lecture`, `Positionnement`.",
                python_rendering="Barres horizontales `px.bar` + tableau HTML.",
                pipeline="Extraction textuelle des solutions et de la conclusion du rapport -> structuration dans un tableau -> affichage d’une hiérarchie lisible.",
                physics=[
                    "Le rapport rattache le choix d’ancrage à la nature du fond et à la reprise d’efforts de traction, pas seulement à une préférence technologique abstraite.",
                ],
                watchouts=[
                    "Aucune solution n’est validée sans reconnaissance géotechnique. La page restitue une préférence de faisabilité, pas un design d’ancrage final.",
                ],
                status="schéma de lecture applicatif",
                missing_in_report="Le rapport est surtout textuel et ne fournit pas de hiérarchie déjà structurée en objets numériques.",
                risk="Risque de sur-interprétation : modéré. La hiérarchie est fidèle à l’esprit du rapport, mais le score reste un score éditorial.",
                categories=["Machine"],
            ),
            _item(
                section="Cadre réglementaire",
                title="Chapitre 19 — Séquence administrative et réglementaire",
                source="Rapport p.38 — chapitre 19 : ‘Aspect réglementaire’.",
                description="Schéma qui transforme le texte réglementaire en séquence projet lisible : cadrage, dossier, instruction, consultation, décision.",
                report_data=[
                    "Référence au cadre IOTA et à l’autorisation environnementale.",
                    "Nécessité d’un dossier démontrant l’absence d’atteinte notable à la qualité de l’eau, au libre écoulement, à la santé publique et aux écosystèmes aquatiques.",
                    "Possibilité d’enquête publique selon la taille et les impacts du projet.",
                ],
                construction=[
                    "L’application prend le texte du chapitre 19 et le reformule en chaîne d’étapes, car le rapport est très textuel sur ce point. Le but est de montrer qu’après la faisabilité technique, le projet passe par une logique d’autorisation environnementale structurée.",
                    "Le tableau associé résume les blocs réglementaires les plus utiles pour un lecteur projet : base juridique, procédure cible, contenu du dossier, milieux aquatiques, consultation.",
                ],
                app_choices=[
                    "Le schéma linéaire est un outil de lecture. Le rapport ne le fournit pas sous forme de diagramme.",
                    "L’application garde une formulation prudente sur le régime exact : il dépend de la rubrique IOTA applicable, du dossier réel et des impacts du projet.",
                ],
                python_functions="`regulatory_process_df()`, `regulatory_summary_df()`, `plot_regulatory_process()`, `show_table()`.",
                python_datasets="Séquence ordonnée des étapes administratives + tableau de synthèse réglementaire.",
                python_rendering="Frise `go.Scatter` annotée + tableau HTML.",
                pipeline="Extraction textuelle du chapitre 19 -> structuration en étapes et blocs -> affichage d’une séquence projet lisible.",
                physics=[],
                watchouts=[
                    "Cette page ne fait pas de veille juridique actualisée exhaustive ; elle conserve le cadre décrit par le rapport tout en reformulant prudemment le régime applicable.",
                ],
                status="schéma de lecture applicatif",
                missing_in_report="Le rapport est textuel et ne fournit pas de séquence visuelle ni de tableau réglementaire déjà structurés.",
                risk="Risque de sur-interprétation : modéré. La logique de dossier est fidèle, mais le détail juridique devra être revu en avant-projet réel.",
                categories=["Économie"],
            ),
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


def _join_text(values: list[str]) -> str:
    return " ".join(value.strip() for value in values if value).strip()


def _numbered_text(values: list[str]) -> str:
    if not values:
        return ""
    return " ".join(f"{index + 1}. {value.strip()}" for index, value in enumerate(values) if value)


def _overview_df(page_key: str) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for item in REPERES.get(page_key, {}).get("items", []):
        rows.append(
            {
                "Section": item["section"],
                "Élément": item["title"],
                "Source rapport": item["source"],
                "Repères rapport": len(item.get("report_data", [])),
                "Points de vigilance": len(item.get("watchouts", [])),
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


def _status_box(item: dict[str, object]) -> str | None:
    status = str(item.get("status", "reconstruction contrainte"))
    missing = str(item.get("missing_in_report", "")).strip()
    procedure = _numbered_text(list(item.get("construction", [])))
    risk = str(item.get("risk", "")).strip()

    if status == "transposition chiffrée fidèle":
        return None
    if status == "schéma de lecture applicatif":
        content = (
            "Cet élément doit être lu comme un schéma de lecture ou une composition applicative, et non comme une reproduction au trait près d’une figure source. "
            f"{missing} Procédure suivie : {procedure} {risk}"
        ).strip()
        return add_remark_box("Fidélité au rapport", content)

    content = (
        "Ce visuel reste proche du rapport sur ses repères structurants, mais il ne provient pas d’une table numérique complète. "
        f"{missing} Procédure suivie : {procedure} {risk}"
    ).strip()
    return add_remark_box("Fidélité au rapport", content)


def _data_source_df(item: dict[str, object]) -> pd.DataFrame:
    report_data = _join_text(list(item.get("report_data", [])))
    construction = _join_text(list(item.get("construction", [])))
    app_choices = _join_text(list(item.get("app_choices", [])))
    watchouts = _join_text(list(item.get("watchouts", [])))
    missing = str(item.get("missing_in_report", "")).strip()
    risk = str(item.get("risk", "")).strip()

    rows = [
        {
            "Type de donnée": "Données reprises du rapport",
            "Méthode": "Extraction manuelle du rapport",
            "Détail": report_data,
            "Remarque": "Les repères structurants, chiffres et formulations de référence sont repris directement du rapport avant toute reformulation applicative.",
        },
        {
            "Type de donnée": "Données reconstruites dans l’application",
            "Méthode": "Reconstruction ou calcul applicatif",
            "Détail": construction,
            "Remarque": app_choices or "L’application reformule le matériau source pour obtenir un objet lisible et calculable dans Streamlit.",
        },
        {
            "Type de donnée": "Repères chiffrés / textuels utilisés",
            "Méthode": "Lecture ciblée du rapport",
            "Détail": report_data,
            "Remarque": "Cette ligne rassemble les chiffres, phrases ou hypothèses qui servent d’ancrage de cohérence au visuel et aux calculs.",
        },
        {
            "Type de donnée": "Pourquoi une reconstruction était nécessaire",
            "Méthode": "Choix de restitution applicative",
            "Détail": app_choices or construction,
            "Remarque": "Le rapport ne fournit pas toujours une table numérique ou un visuel directement réutilisable dans Streamlit ; l’application doit donc reconstruire une partie de l’objet final.",
        },
        {
            "Type de donnée": "Ce qui manquait dans le rapport pour une reprise directe",
            "Méthode": "Diagnostic de reproductibilité",
            "Détail": missing,
            "Remarque": "Cette ligne dit explicitement pourquoi l’application n’a pas pu se contenter d’une recopie brute du rapport.",
        },
        {
            "Type de donnée": "Comment la reconstruction a été faite concrètement",
            "Méthode": "Procédure appliquée dans l’app",
            "Détail": _numbered_text(list(item.get("construction", []))),
            "Remarque": "Le but est de documenter la méthode de fabrication quand le rapport n’offrait pas directement la donnée finale sous forme exploitable.",
        },
        {
            "Type de donnée": "Statut du visuel dans l’application",
            "Méthode": "Qualification critique",
            "Détail": str(item.get("status", "")),
            "Remarque": risk,
        },
    ]
    if watchouts:
        rows.append(
            {
                "Type de donnée": "Portée / vigilance de lecture",
                "Méthode": "Lecture critique",
                "Détail": watchouts,
                "Remarque": "Ces points disent ce qu’il ne faut pas faire dire au visuel ou au calcul dans l’application.",
            }
        )
    return pd.DataFrame(rows)


def _construction_logic_df(item: dict[str, object]) -> pd.DataFrame:
    rows = [
        {
            "Bloc": "Correspondance exacte des items Python",
            "Lecture": f"{item['python_functions']} Rôle précis de ce bloc dans la page : {item['description']}",
        },
        {
            "Bloc": "Fonctions / objets appelés",
            "Lecture": f"{item['python_functions']} Ce couple fonctions / objets sert concrètement à : {_join_text(list(item.get('construction', [])))}",
        },
        {
            "Bloc": "Valeurs / hypothèses injectées",
            "Lecture": _join_text(list(item.get("report_data", []))),
        },
        {
            "Bloc": "Sortie produite pour la page",
            "Lecture": f"{item['description']} Usage dans la page : {_join_text(list(item.get('construction', [])))}",
        },
        {
            "Bloc": "DataFrames / constantes / colonnes",
            "Lecture": f"{item['python_datasets']} Repères rapport injectés dans ces structures : {_join_text(list(item.get('report_data', [])))}",
        },
        {
            "Bloc": "Rendu Plotly / Streamlit",
            "Lecture": item["python_rendering"],
        },
        {
            "Bloc": "Pipeline de construction",
            "Lecture": f"{item['pipeline']} Choix d’implémentation dans le pipeline : {_join_text(list(item.get('app_choices', [])))}",
        },
        {
            "Bloc": "Ajustement / approximation technique",
            "Lecture": _join_text(list(item.get("watchouts", []))) or "Pas d’ajustement critique supplémentaire signalé pour ce bloc.",
        },
    ]
    return pd.DataFrame(rows)


def _construction_sheet_df(item: dict[str, object]) -> pd.DataFrame:
    rows = [
        {"Aspect": "Type exact de visuel applicatif", "Détail": str(item.get("status", "")).replace("schéma de lecture applicatif", "Schéma de lecture applicatif").replace("reconstruction contrainte", "Reconstruction contrainte").replace("transposition chiffrée fidèle", "Transposition chiffrée fidèle")},
        {"Aspect": "Source rapport", "Détail": item["source"]},
        {"Aspect": "Structure de lecture du visuel d’origine", "Détail": item["description"]},
        {"Aspect": "Ce que montrait l’original", "Détail": item["description"]},
        {"Aspect": "Ce que l’application garde strictement", "Détail": _join_text(list(item.get("report_data", [])))},
        {"Aspect": "Ce que l’application simplifie ou ajoute", "Détail": f"{_join_text(list(item.get('app_choices', [])))} Reconstruction retenue : {_join_text(list(item.get('construction', [])))}".strip()},
        {"Aspect": "Pourquoi ce format a été retenu", "Détail": item["description"]},
        {"Aspect": "Transformation dans l’application", "Détail": f"{_join_text(list(item.get('construction', [])))} {_join_text(list(item.get('app_choices', [])))}".strip()},
        {"Aspect": "Statut de la restitution", "Détail": str(item.get("status", ""))},
        {"Aspect": "Ce qu’il ne faut pas sur-interpréter", "Détail": str(item.get("risk", "")).strip()},
    ]
    if item.get("watchouts"):
        rows.append({"Aspect": "Portée / vigilance de lecture", "Détail": _join_text(list(item.get("watchouts", [])))})
    return pd.DataFrame(rows)


def _render_list(title: str, values: list[str]) -> None:
    if not values:
        return
    st.markdown(f"**{title}**")
    for value in values:
        st.markdown(f"- {value}")


def render_reperes_application(page_key: str) -> None:
    config = REPERES.get(page_key)
    if not config:
        st.info("Aucun repère configuré pour cette page.")
        return

    intro = str(config.get("intro", "")).strip()
    if intro:
        st.markdown(add_method_box("Comment lire cet onglet", intro), unsafe_allow_html=True)

    overview = _overview_df(page_key)
    item_count = len(config["items"])
    source_count = len({item["source"] for item in config["items"]})
    watchout_count = sum(len(item.get("watchouts", [])) for item in config["items"])

    m1, m2, m3 = st.columns(3)
    m1.metric("Éléments couverts", str(item_count))
    m2.metric("Sources rapport", str(source_count))
    m3.metric("Points de vigilance", str(watchout_count))

    if not overview.empty:
        show_table(overview, hide_index=True, width="stretch")

    checks = _filtered_logic_checks(page_key)
    if not checks.empty:
        st.markdown(
            add_assumption_box(
                "Contrôles de cohérence utiles à cette page",
                "Les lignes ci-dessous vérifient que la reconstruction applicative retombe sur les ordres de grandeur structurants du rapport. `OK` signifie concordance directe ; `OK (arrondi)` signale un écart explicable par les arrondis ou la simplification graphique retenue dans l’application.",
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

    labeled_options = {f"{item['section']} — {item['title']}": item for item in config["items"]}
    selected = st.selectbox(
        "Choisir un élément du rapport à détailler",
        list(labeled_options.keys()),
        key=f"{page_key}_repere_select",
    )
    item = labeled_options[selected]

    st.markdown(add_reference_box("Référence rapport", str(item["source"])), unsafe_allow_html=True)
    st.markdown(add_method_box("Ce que cet élément montre", str(item["description"])), unsafe_allow_html=True)
    status_box = _status_box(item)
    if status_box:
        st.markdown(status_box, unsafe_allow_html=True)

    st.markdown("**Source des données**")
    show_table(_data_source_df(item), hide_index=True, width="stretch")
    st.markdown("**Construction technique (Python)**")
    show_table(_construction_logic_df(item), hide_index=True, width="stretch")
    st.markdown("**Lecture rapport / transformation**")
    show_table(_construction_sheet_df(item), hide_index=True, width="stretch")

    physics = list(item.get("physics", []))
    if physics:
        _render_list("Logique physique ou formule reprise", physics)

    watchouts = list(item.get("watchouts", []))
    if watchouts:
        st.markdown(add_remark_box("Point d’attention", "<br>".join(watchouts)), unsafe_allow_html=True)


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
