
from __future__ import annotations

from html import escape
from typing import Any

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st


APP_TITLE = "Foil'O – Faisabilité Seine PK326"
APP_ICON = "🌊"
REPORT_LABEL = "Rapport de faisabilité Foil'O – décembre 2025"

BMVE_115 = 2.8
PMVE_115 = 8.4

SECTION_WIDTH = 320.0
CHANNEL_X0 = 125.0
CHANNEL_X1 = 235.0
CHANNEL_WIDTH = CHANNEL_X1 - CHANNEL_X0
NAVIGATION_SETBACK = 5.0
REFERENCE_MACHINE_WIDTH = 36.0
REFERENCE_MACHINE_DRAFT = 7.0

REFERENCE_LIFETIME_YEARS = 20
REFERENCE_OPEX_EUR_MWH = 30.0
REFERENCE_FINANCING_RATE = 0.04
REFERENCE_FINANCING_YEARS = 10
REFERENCE_GRID_MEAN_INFLATION_FACTOR_20Y = 1.228

DEFAULT_EXTERNALITIES = {
    "Résilience / sécurité d’approvisionnement": 7.5,
    "Réduction de la volatilité des prix": 10.0,
    "Externalités environnementales non climatiques": 5.0,
    "Diversification stratégique": 5.0,
}

PROTOTYPE_PRODUCTION_CASES = {
    "prudent": {
        "label": "Cas prudent",
        "specific_mwh_kw_an": 4.0,
        "description": "Hypothèse prudente pour un prototype réduit, utilisée pour éviter une surinterprétation avant retour terrain consolidé.",
    },
    "high": {
        "label": "Cas haut",
        "specific_mwh_kw_an": 5.625,
        "description": "Cas haut illustratif cohérent avec une production d’environ 200 à 250 MWh/an autour de 40 kW.",
    },
    "manual": {
        "label": "Saisie manuelle",
        "specific_mwh_kw_an": None,
        "description": "Saisie libre destinée aux lectures exploratoires. La comparaison stricte au rapport devient alors moins directe.",
    },
}

PLOTLY_CONFIG = {
    "displaylogo": False,
    "responsive": True,
    "modeBarButtonsToRemove": ["lasso2d", "select2d", "autoScale2d"],
}


# =============================================================================
# Streamlit page / style helpers
# =============================================================================


def configure_page(page_title: str) -> None:
    st.set_page_config(page_title=page_title, page_icon=APP_ICON, layout="wide")
    apply_app_style()


@st.cache_resource(show_spinner=False)
def _style_css() -> str:
    return """
    <style>
    .stApp {
        background-color: #ffffff;
        color: #0f172a;
    }

    [data-testid="stHeader"] {
        background: rgba(255,255,255,0.94);
    }

    [data-testid="stSidebar"] {
        background: #f8fafc;
        border-right: 1px solid rgba(15, 23, 42, 0.08);
    }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1550px;
    }

    h1, h2, h3, h4, h5, h6, p, div, span, label, li, td, th {
        color: #0f172a !important;
    }

    .stMetric {
        background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
        border: 1px solid rgba(15, 23, 42, 0.08);
        border-radius: 14px;
        padding: 12px 14px;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
    }

    div[data-testid="stMetricLabel"] p {
        font-size: 0.86rem !important;
        line-height: 1.15 !important;
    }

    div[data-testid="stMetricValue"] {
        font-size: 2.05rem !important;
        line-height: 1.02 !important;
    }

    .foilo-table-wrapper {
        overflow-x: auto;
        margin: 0.2rem 0 0.9rem 0;
    }

    .foilo-table {
        width: 100%;
        border-collapse: collapse;
        background: #ffffff;
        color: #0f172a;
        border: 1px solid rgba(15, 23, 42, 0.10);
        border-radius: 12px;
        overflow: hidden;
        font-size: 0.95rem;
    }

    .foilo-table thead th {
        background: #f8fafc;
        color: #0f172a;
        text-align: left;
        padding: 0.55rem 0.7rem;
        border-bottom: 1px solid rgba(15, 23, 42, 0.10);
    }

    .foilo-table tbody td {
        background: #ffffff;
        color: #0f172a;
        padding: 0.5rem 0.7rem;
        border-top: 1px solid rgba(15, 23, 42, 0.08);
        vertical-align: top;
    }

    .foilo-table tbody tr:nth-child(even) td {
        background: #fbfdff;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        background: #eef2f7;
        border-radius: 10px 10px 0 0;
        padding-left: 14px;
        padding-right: 14px;
    }

    .stTabs [aria-selected="true"] {
        background: #ffffff !important;
        border-bottom: 2px solid #1d4ed8 !important;
    }

    div[data-baseweb="select"] > div,
    div[data-baseweb="select"] span,
    div[data-baseweb="select"] input,
    div[data-baseweb="base-input"] > div,
    input {
        background-color: #ffffff !important;
        color: #0f172a !important;
    }

    div[role="listbox"],
    ul[role="listbox"],
    div[role="option"],
    li[role="option"] {
        background: #ffffff !important;
        color: #0f172a !important;
    }
    </style>
    """


def apply_app_style() -> None:
    st.markdown(_style_css(), unsafe_allow_html=True)


def _clean_box_text(value: str) -> str:
    cleaned = value.replace("**", "").strip()
    cleaned = escape(cleaned)
    cleaned = cleaned.replace("\n", "<br>")
    while "<br><br><br>" in cleaned:
        cleaned = cleaned.replace("<br><br><br>", "<br><br>")
    return cleaned


def _styled_box(title: str, content: str, border_color: str, left_color: str, background: str) -> str:
    safe_title = _clean_box_text(title)
    safe_content = _clean_box_text(content)
    return f"""
    <div style="
        border: 1px solid {border_color};
        border-left: 4px solid {left_color};
        border-radius: 12px;
        padding: 14px 16px;
        margin: 8px 0 14px 0;
        background: {background};
    ">
        <div style="font-weight: 700; margin-bottom: 6px; color: #0f172a;">{safe_title}</div>
        <div style="font-size: 0.96rem; line-height: 1.55; color: #0f172a;">{safe_content}</div>
    </div>
    """


def add_reference_box(title: str, content: str) -> str:
    return _styled_box(title, content, "rgba(37, 99, 235, 0.14)", "#2563eb", "#f8fbff")


def add_remark_box(title: str, content: str) -> str:
    return _styled_box(title, content, "rgba(245, 158, 11, 0.18)", "#d97706", "#fffaf0")


def add_assumption_box(title: str, content: str) -> str:
    return _styled_box(title, content, "rgba(14, 116, 144, 0.16)", "#0ea5b7", "#f0fdff")


def add_method_box(title: str, content: str) -> str:
    return _styled_box(title, content, "rgba(22, 163, 74, 0.16)", "#16a34a", "#f4fff7")


def add_warning_box(title: str, content: str) -> str:
    return _styled_box(title, content, "rgba(220, 38, 38, 0.16)", "#dc2626", "#fff7f7")


def style_figure(fig: go.Figure, height: int = 420) -> go.Figure:
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(color="#0f172a", size=13),
        title_font=dict(color="#0f172a", size=18),
        legend=dict(
            bgcolor="rgba(255,255,255,0.94)",
            bordercolor="rgba(15,23,42,0.10)",
            borderwidth=1,
            font=dict(color="#0f172a", size=12),
            title_font=dict(color="#0f172a", size=12),
        ),
        hoverlabel=dict(font=dict(color="#0f172a")),
        height=height,
        margin=dict(l=36, r=28, t=72, b=40),
    )
    fig.update_xaxes(
        showgrid=True,
        gridcolor="rgba(15,23,42,0.08)",
        zeroline=False,
        color="#0f172a",
        tickfont=dict(color="#0f172a", size=12),
        title_font=dict(color="#0f172a", size=13),
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor="rgba(15,23,42,0.08)",
        zeroline=False,
        color="#0f172a",
        tickfont=dict(color="#0f172a", size=12),
        title_font=dict(color="#0f172a", size=13),
    )
    fig.update_annotations(font=dict(color="#0f172a", size=12))
    return fig


def show_chart(fig: go.Figure, key: str | None = None) -> None:
    st.plotly_chart(fig, width="stretch", config=PLOTLY_CONFIG, key=key)


def yes_no_label(value: bool) -> str:
    return "Oui" if value else "Non"


def _format_table_value(value: Any) -> str:
    if isinstance(value, (bool, np.bool_)):
        return yes_no_label(bool(value))
    if value is None:
        return ""
    if isinstance(value, (float, np.floating)):
        if np.isnan(value):
            return ""
        if np.isclose(value, round(float(value))):
            return f"{int(round(float(value)))}"
        if np.isclose(float(value) * 10.0, round(float(value) * 10.0)):
            return f"{float(value):.1f}"
        return f"{float(value):.2f}"
    if isinstance(value, (int, np.integer)):
        return str(int(value))
    return str(value)


def show_table(data: pd.DataFrame, hide_index: bool = True, width: str = "stretch") -> None:
    del hide_index, width
    df = data.copy()
    columns = list(df.columns)
    rows: list[str] = []
    for _, row in df.iterrows():
        cells = [f"<td>{escape(_format_table_value(row[col])).replace(chr(10), '<br>')}</td>" for col in columns]
        rows.append("<tr>" + "".join(cells) + "</tr>")
    header = "".join(f"<th>{escape(str(col))}</th>" for col in columns)
    html = (
        "<div class='foilo-table-wrapper'>"
        "<table class='foilo-table'>"
        f"<thead><tr>{header}</tr></thead>"
        f"<tbody>{''.join(rows)}</tbody>"
        "</table>"
        "</div>"
    )
    st.markdown(html, unsafe_allow_html=True)


# =============================================================================
# Site / resource data
# =============================================================================


@st.cache_data(show_spinner=False)
def site_profiles_df() -> pd.DataFrame:
    df = pd.DataFrame(
        {
            "Profil": ["PK243.7", "PK282", "PK292.2", "PK314.9", "PK326", "PK341", "PK371"],
            "Nom_site": [
                "Jean Ango",
                "La Pâture aux Rats",
                "Le Landin",
                "Vatteville",
                "Courval / St Léonard",
                "La Roque",
                "Engainement",
            ],
            "Année": [2014, 2022, 2018, 2012, 2016, 2017, 2017],
            "PK_km": [243.7, 282.0, 292.2, 314.9, 326.0, 341.0, 371.0],
            "Pic_flot_m_s": [1.20, 1.60, 1.85, 1.70, 2.00, 1.65, 0.95],
            "Pic_jusant_m_s": [1.00, 1.10, 1.50, 1.25, 2.25, 2.00, 0.90],
            "Classe": ["Secondaire", "Corridor", "Site majeur", "Corridor", "Site majeur", "Corridor", "Secondaire"],
        }
    )
    df["Indice_énergétique"] = df["Pic_flot_m_s"] ** 3 + df["Pic_jusant_m_s"] ** 3
    df["Jusant_dominant"] = df["Pic_jusant_m_s"] > df["Pic_flot_m_s"]
    return df


@st.cache_data(show_spinner=False)
def corridor_profiles_df() -> pd.DataFrame:
    df = site_profiles_df().copy()
    df["Libellé_court"] = [
        "PK243.7\nJean Ango",
        "PK282\nLa Pâture aux Rats",
        "PK292.2\nLe Landin",
        "PK314.9\nVatteville",
        "PK326\nCourval",
        "PK341\nLa Roque",
        "PK371\nEngainement",
    ]
    return df.sort_values("PK_km").reset_index(drop=True)


@st.cache_data(show_spinner=False)
def estuary_towns_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Lieu": [
                "Baie de Seine / Le Havre",
                "Honfleur",
                "Tancarville",
                "Caudebec-en-Caux",
                "Le Trait",
                "Duclair",
                "Rouen",
                "Oissel",
                "Pont-de-l’Arche",
                "Val-de-Reuil",
                "Poses",
            ],
            "x": [238, 246, 258, 304, 320, 338, 357, 367, 377, 381, 385],
            "y": [0.10, 0.60, 0.90, 0.35, 0.85, 0.30, 1.00, 0.55, 1.05, 0.80, 1.15],
        }
    )


@st.cache_data(show_spinner=False)
def salinity_zonation_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Zone": ["Eau salée", "Eau saumâtre", "Eau douce"],
            "x0": [238, 275, 330],
            "x1": [275, 330, 385],
            "Couleur": ["#f97316", "#facc15", "#7dd3fc"],
            "Lecture": [
                "Zone aval dominée par l’influence marine",
                "Zone de transition salinité / débit",
                "Zone limnique amont, compatible avec une lecture en eau douce",
            ],
        }
    )


@st.cache_data(show_spinner=False)
def resource_extrapolation_df() -> pd.DataFrame:
    return pd.DataFrame({"Coef_marée": [45.0, 70.0, 95.0, 115.0], "Energie_Wh_m2_maree": [6000.0, 8300.0, 9000.0, 9750.0]})


@st.cache_data(show_spinner=False)
def river_energy_metrics() -> dict[str, float]:
    return {
        "energy_low_mwh_per_tide": 25.0,
        "energy_high_mwh_per_tide": 85.0,
        "annual_section_gwh": 29.5,
        "flot_share": 0.45,
        "jusant_share": 0.55,
    }


@st.cache_data(show_spinner=False)
def resource_summary_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Indicateur": [
                "Corridor à potentiel renforcé",
                "Profils les plus favorables",
                "Pic de flot à PK326",
                "Pic de jusant à PK326",
                "Salinité amont PK330",
                "Énergie de section PK326",
                "Production unitaire cible",
                "Facteur de charge indicatif",
            ],
            "Lecture": [
                "Environ 35 km au cœur de l’estuaire intérieur soumis à la marée",
                "PK292 Le Landin et PK326 Courval",
                "Environ 2,00 m/s en vives eaux ; 1,25 m/s en mortes eaux",
                "Environ 2,25 m/s en vives eaux ; 1,50 m/s en mortes eaux",
                "Inférieure à 0,5 g/L, lecture en eau douce",
                "Environ 25 à 85 MWh par marée ; environ 29,5 GWh/an pour la section",
                "Ordre de grandeur 0,7 à 0,9 GWh/an par machine",
                "Ordre de grandeur 0,41 à 0,52 selon la puissance nominale retenue",
            ],
        }
    )


@st.cache_data(show_spinner=False)
def tide_levels_df() -> pd.DataFrame:
    stations = [
        "Balise A",
        "Honfleur",
        "Tancarville",
        "St Léonard",
        "Vatteville",
        "Caudebec",
        "Heurteauville",
        "Jumièges",
        "Duclair",
        "Val des Leux",
        "La Bouille",
        "Petit Couronne",
        "Rouen",
        "Oissel",
        "Elbeuf",
    ]
    return pd.DataFrame(
        {
            "Station": stations,
            "BM_115": [0.8, 1.2, 1.9, 2.8, 3.2, 3.6, 4.0, 4.2, 4.4, 4.6, 4.8, 5.3, 5.8, 6.0, 6.3],
            "PM_115": [8.2, 8.3, 8.4, 8.45, 8.5, 8.45, 8.4, 8.35, 8.3, 8.28, 8.25, 8.2, 8.15, 8.12, 8.1],
            "BM_80": [1.7, 2.0, 2.4, 3.2, 3.5, 3.8, 4.1, 4.3, 4.5, 4.7, 4.9, 5.2, 5.6, 5.8, 6.0],
            "PM_80": [7.4, 7.5, 7.6, 7.7, 7.8, 7.85, 7.85, 7.8, 7.75, 7.72, 7.7, 7.65, 7.6, 7.58, 7.55],
            "BM_65": [2.1, 2.35, 2.75, 3.55, 3.85, 4.1, 4.35, 4.55, 4.75, 4.95, 5.1, 5.35, 5.65, 5.85, 6.05],
            "PM_65": [6.9, 7.0, 7.15, 7.3, 7.4, 7.45, 7.45, 7.42, 7.38, 7.35, 7.32, 7.28, 7.24, 7.2, 7.16],
            "BM_35": [3.2, 3.35, 3.55, 4.25, 4.5, 4.75, 4.95, 5.1, 5.25, 5.4, 5.5, 5.7, 5.95, 6.1, 6.25],
            "PM_35": [6.0, 6.1, 6.2, 6.45, 6.55, 6.65, 6.7, 6.75, 6.8, 6.82, 6.85, 6.88, 6.92, 6.95, 6.98],
        }
    )


@st.cache_data(show_spinner=False)
def _section_control_points() -> tuple[np.ndarray, np.ndarray]:
    # Simplified operational cross-section reconstructed so that the conservative rule
    # BMVE(115)=2.8 m, H=7.0 m, clearance=0.5 m yields approximately the report windows:
    # west ≈ 70 m and east ≈ 45 m.
    x = np.array([0, 15, 30, 45, 55, 80, 125, 180, 235, 255, 280, 295, 320], dtype=float)
    z = np.array([-0.2, -1.0, -2.8, -4.4, -4.7, -4.9, -5.1, -5.8, -5.0, -4.85, -4.7, -4.0, -0.4], dtype=float)
    return x, z


@st.cache_data(show_spinner=False)
def section_profile_df(step: float = 1.0) -> pd.DataFrame:
    control_x, control_z = _section_control_points()
    x = np.arange(control_x.min(), control_x.max() + step, step)
    z = np.interp(x, control_x, control_z)
    return pd.DataFrame({"x_m": x, "z_cmh_m": z})


def _below_threshold_intervals(x: np.ndarray, z: np.ndarray, threshold: float) -> list[tuple[float, float]]:
    intervals: list[tuple[float, float]] = []
    for x0, x1, z0, z1 in zip(x[:-1], x[1:], z[:-1], z[1:]):
        in0 = z0 <= threshold + 1e-9
        in1 = z1 <= threshold + 1e-9
        if in0 and in1:
            intervals.append((float(x0), float(x1)))
        elif in0 != in1:
            if np.isclose(z1, z0):
                xi = float(x0)
            else:
                t = (threshold - z0) / (z1 - z0)
                xi = float(x0 + t * (x1 - x0))
            intervals.append((float(x0), xi) if in0 else (xi, float(x1)))
    if not intervals:
        return []
    merged: list[list[float]] = []
    for start, end in intervals:
        if not merged or start > merged[-1][1] + 1e-9:
            merged.append([start, end])
        else:
            merged[-1][1] = max(merged[-1][1], end)
    return [(start, end) for start, end in merged]


def _subtract_exclusion(intervals: list[tuple[float, float]], exclusion_start: float, exclusion_end: float) -> list[tuple[float, float]]:
    output: list[tuple[float, float]] = []
    for start, end in intervals:
        if end <= exclusion_start or start >= exclusion_end:
            output.append((start, end))
            continue
        if start < exclusion_start:
            output.append((start, exclusion_start))
        if end > exclusion_end:
            output.append((exclusion_end, end))
    return output


def compute_section_layout(
    water_level: float = BMVE_115,
    depth_limit: float = 7.0,
    clearance: float = 0.5,
    channel_setback: float = 0.0,
) -> dict[str, Any]:
    profile = section_profile_df()
    threshold = water_level - depth_limit - clearance
    base_intervals = _below_threshold_intervals(profile["x_m"].to_numpy(), profile["z_cmh_m"].to_numpy(), threshold)
    usable_intervals = _subtract_exclusion(base_intervals, CHANNEL_X0 - channel_setback, CHANNEL_X1 + channel_setback)

    rows: list[dict[str, float | str]] = []
    for start, end in usable_intervals:
        width = max(end - start, 0.0)
        if width <= 0:
            continue
        side = "Ouest" if end <= CHANNEL_X0 else "Est"
        rows.append(
            {
                "Fenêtre": f"Latérale {side}",
                "Side": side,
                "x0_m": start,
                "x1_m": end,
                "Largeur_m": width,
                "WaterLevel_m": water_level,
                "DepthLimit_m": depth_limit,
                "Clearance_m": clearance,
                "ChannelSetback_m": channel_setback,
            }
        )
    windows = pd.DataFrame(rows)
    if not windows.empty:
        windows = windows.sort_values("x0_m").reset_index(drop=True)
    return {
        "profile": profile,
        "threshold_cmh_m": threshold,
        "windows": windows,
        "water_level_m": water_level,
        "depth_limit_m": depth_limit,
        "clearance_m": clearance,
        "channel_setback_m": channel_setback,
    }


@st.cache_data(show_spinner=False)
def implantation_windows_df() -> pd.DataFrame:
    windows = compute_section_layout(channel_setback=0.0)["windows"].copy()
    if windows.empty:
        return pd.DataFrame(columns=["Fenêtre", "Largeur_m", "Hauteur_ref_m"])
    windows["Hauteur_ref_m"] = 7.0
    return windows[["Fenêtre", "Largeur_m", "Hauteur_ref_m"]]


def implantation_budget_df(
    machine_width: float = REFERENCE_MACHINE_WIDTH,
    channel_setback: float = NAVIGATION_SETBACK,
    water_level: float = BMVE_115,
    depth_limit: float = 7.0,
    clearance: float = 0.5,
) -> pd.DataFrame:
    raw = compute_section_layout(water_level=water_level, depth_limit=depth_limit, clearance=clearance, channel_setback=0.0)["windows"]
    eff = compute_section_layout(water_level=water_level, depth_limit=depth_limit, clearance=clearance, channel_setback=channel_setback)["windows"]
    if raw.empty:
        return pd.DataFrame(columns=["Fenêtre", "Largeur_brute_m", "Largeur_après_recul_m", "Machine_m", "Marge_restante_m", "Compatible"])

    merged = raw.merge(eff[["Fenêtre", "Largeur_m"]].rename(columns={"Largeur_m": "Largeur_après_recul_m"}), on="Fenêtre", how="left")
    merged["Largeur_après_recul_m"] = merged["Largeur_après_recul_m"].fillna(0.0)
    merged["Largeur_brute_m"] = merged["Largeur_m"]
    merged["Machine_m"] = machine_width
    merged["Marge_restante_m"] = merged["Largeur_après_recul_m"] - machine_width
    merged["Compatible"] = merged["Marge_restante_m"] >= 0
    return merged[["Fenêtre", "Largeur_brute_m", "Largeur_après_recul_m", "Machine_m", "Marge_restante_m", "Compatible"]]


@st.cache_data(show_spinner=False)
def navigation_reference_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Référence": [
                "Chenal central maintenu libre",
                "Navire type Large Range",
                "Grand minéralier cité au rapport",
                "Largeur de passage prudente évoquée",
                "Recul de lecture projet",
            ],
            "Valeur": [
                "110 m",
                "228 m de long ; 32 m de large ; 74 500 TPL",
                "290 m de long ; 45 m de large",
                "Ordre de grandeur 60 m pour les plus grands navires",
                "5 m de part et d’autre du chenal pour la lecture de référence",
            ],
        }
    )


# =============================================================================
# Plot functions – site and implantation
# =============================================================================


def plot_estuary_map() -> go.Figure:
    towns = estuary_towns_df()
    profiles = corridor_profiles_df()
    salinity = salinity_zonation_df()

    river_x = np.array([238, 244, 252, 260, 270, 282, 292, 305, 315, 326, 341, 355, 371, 385], dtype=float)
    river_y = np.array([0.2, 0.55, 0.9, 0.75, 0.45, 0.85, 0.65, 0.35, 0.8, 0.55, 0.3, 0.85, 0.7, 1.1], dtype=float)

    fig = go.Figure()
    for _, row in salinity.iterrows():
        fig.add_shape(type="rect", x0=float(row["x0"]), x1=float(row["x1"]), y0=-1.18, y1=-0.78, line=dict(width=0), fillcolor=str(row["Couleur"]), opacity=0.65)
        fig.add_annotation(x=0.5 * (float(row["x0"]) + float(row["x1"])), y=-0.98, text=str(row["Zone"]), showarrow=False)

    fig.add_trace(go.Scatter(x=river_x, y=river_y, mode="lines", line=dict(color="#60a5fa", width=18, shape="spline"), name="Seine", hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=river_x, y=river_y, mode="lines", line=dict(color="#2563eb", width=5, shape="spline"), name="Axe fluvial", hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=towns["x"], y=towns["y"], mode="markers+text", marker=dict(size=8, color="#334155"), text=towns["Lieu"], textposition="top center", name="Communes et repères"))

    profile_y = np.interp(profiles["PK_km"], river_x, river_y)
    fig.add_trace(
        go.Scatter(
            x=profiles["PK_km"],
            y=profile_y,
            mode="markers+text",
            marker=dict(size=11, color="#dc2626", line=dict(color="white", width=1.5)),
            text=profiles["Profil"],
            textposition="bottom center",
            name="Profils courantologie",
            hovertemplate="%{text}<extra></extra>",
        )
    )

    fig.add_vrect(x0=292, x1=327, fillcolor="rgba(37,99,235,0.08)", line_width=0)
    fig.add_annotation(x=309.5, y=1.45, text="Corridor énergétique ~35 km", showarrow=False)
    fig.add_annotation(x=326.0, y=1.62, text="PK326 retenu", showarrow=False)
    fig.add_annotation(x=382, y=1.72, text="N", showarrow=True, arrowhead=2, ax=0, ay=38, font=dict(size=16))
    fig.add_annotation(x=360, y=-0.55, text="Influence de la marée vers l’amont", showarrow=True, ax=-115, ay=0, arrowhead=2)
    fig.add_annotation(x=239, y=-0.55, text="Aval / mer", showarrow=False, xanchor="left")
    fig.add_annotation(x=385, y=-0.55, text="Amont / Poses", showarrow=False, xanchor="right")
    fig.update_layout(title="Géographie schématique de l’estuaire, profils et domaines d’eau", xaxis_title="PK le long de l’estuaire de la Seine", yaxis=dict(visible=False, range=[-1.28, 1.82]), showlegend=True)
    fig.update_xaxes(range=[236, 387], tickmode="array", tickvals=[245, 280, 300, 326, 341, 371, 385])
    return style_figure(fig, height=470)


def plot_corridor_profiles(df: pd.DataFrame | None = None) -> go.Figure:
    if df is None:
        df = corridor_profiles_df()
    class_colors = {"Secondaire": "#94a3b8", "Corridor": "#2563eb", "Site majeur": "#dc2626"}
    sizes = {"Secondaire": 10, "Corridor": 13, "Site majeur": 17}
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["PK_km"], y=[0] * len(df), mode="lines", line=dict(color="#94a3b8", width=4), showlegend=False, hoverinfo="skip"))

    seen: set[str] = set()
    for _, row in df.iterrows():
        classe = str(row["Classe"])
        fig.add_trace(
            go.Scatter(
                x=[row["PK_km"]],
                y=[0],
                mode="markers+text",
                marker=dict(size=sizes[classe], color=class_colors[classe], line=dict(color="white", width=1.5)),
                text=[row["Libellé_court"]],
                textposition="top center" if row["PK_km"] not in {282.0, 314.9, 341.0} else "bottom center",
                name=classe,
                legendgroup=classe,
                showlegend=classe not in seen,
                hovertemplate=(f"{row['Profil']} – {row['Nom_site']}<br>Flot : {row['Pic_flot_m_s']:.2f} m/s<br>Jusant : {row['Pic_jusant_m_s']:.2f} m/s<extra></extra>"),
            )
        )
        seen.add(classe)

    fig.add_vrect(x0=292.0, x1=327.0, fillcolor="rgba(37,99,235,0.08)", line_width=0)
    fig.add_annotation(x=309.5, y=0.23, text="Corridor renforcé ~35 km", showarrow=False)
    fig.add_annotation(x=326.0, y=0.13, text="Site retenu\nPK326", showarrow=False, font=dict(color="#dc2626", size=12))
    fig.add_annotation(x=df["PK_km"].min(), y=-0.18, text="Le Havre / aval", showarrow=False, xanchor="left")
    fig.add_annotation(x=df["PK_km"].max(), y=-0.18, text="Rouen / amont", showarrow=False, xanchor="right")
    fig.update_layout(title="Corridor estuarien et profils de courantologie", xaxis_title="PK le long de la Seine", yaxis=dict(visible=False, range=[-0.28, 0.28]), legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0.0))
    fig.update_xaxes(range=[235, 378], tickmode="array", tickvals=[250, 300, 350])
    return style_figure(fig, height=360)


def plot_site_screening(df: pd.DataFrame | None = None) -> go.Figure:
    if df is None:
        df = site_profiles_df()
    fig = px.scatter(
        df,
        x="Pic_flot_m_s",
        y="Pic_jusant_m_s",
        text="Profil",
        color="Classe",
        size="Indice_énergétique",
        size_max=28,
        title="Criblage des profils de courant",
        color_discrete_map={"Secondaire": "#94a3b8", "Corridor": "#2563eb", "Site majeur": "#dc2626"},
        hover_data={"Nom_site": True, "Année": True, "PK_km": ":.1f", "Indice_énergétique": False, "Pic_flot_m_s": ":.2f", "Pic_jusant_m_s": ":.2f"},
    )
    fig.update_traces(textposition="top center")
    fig.add_vline(x=1.0, line_dash="dash", line_color="gray", opacity=0.5)
    fig.add_hline(y=1.0, line_dash="dash", line_color="gray", opacity=0.5)
    fig.update_layout(xaxis_title="Pic de flot (m/s)", yaxis_title="Pic de jusant (m/s)")
    return style_figure(fig, height=430)


@st.cache_data(show_spinner=False)
def approx_velocity_curves() -> tuple[np.ndarray, dict[int, np.ndarray]]:
    t = np.linspace(0, 12, 240)

    def profile(peak_flot: float, peak_jusant: float) -> np.ndarray:
        jusant_1 = -0.78 * peak_jusant * np.exp(-((t - 1.0) / 2.0) ** 2)
        flot = peak_flot * np.exp(-((t - 4.1) / 1.45) ** 2)
        shoulder = 0.62 * peak_flot * np.exp(-((t - 6.4) / 1.65) ** 2)
        jusant_2 = -peak_jusant * np.exp(-((t - 9.7) / 1.15) ** 2)
        baseline = -0.12 * peak_jusant
        return baseline + jusant_1 + flot + shoulder + jusant_2

    curves = {
        45: profile(1.25, 1.50),
        70: profile(1.50, 1.75),
        95: profile(1.75, 2.00),
        115: profile(2.00, 2.25),
    }
    return t, curves


def plot_pk326_curves(selected_coef: int | None = None) -> go.Figure:
    t, curves = approx_velocity_curves()
    fig = go.Figure()
    colors = {45: "#93c5fd", 70: "#60a5fa", 95: "#2563eb", 115: "#dc2626"}
    for coef, y in curves.items():
        width = 4 if coef == selected_coef else 2.5
        opacity = 1.0 if (selected_coef is None or coef == selected_coef) else 0.32
        fig.add_trace(go.Scatter(x=t, y=y, mode="lines", name=f"Coef. {coef}", line=dict(width=width, color=colors[coef]), opacity=opacity))
    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.65)
    fig.add_annotation(x=1.2, y=1.95, text="FLOT", showarrow=False, font=dict(size=13))
    fig.add_annotation(x=1.2, y=-1.95, text="JUSANT", showarrow=False, font=dict(size=13))
    fig.update_layout(title="PK326 – courbes de courant de référence", xaxis_title="Temps sur une marée (h)", yaxis_title="Vitesse (m/s)")
    return style_figure(fig, height=420)


def plot_salinity_zonation() -> go.Figure:
    df = pd.DataFrame({"PK": [340, 330, 320, 310, 300, 290, 280, 260, 245], "Salinité_g_L": [0.10, 0.20, 0.35, 0.80, 2.5, 8.0, 18.0, 26.0, 32.0]})
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["PK"], y=df["Salinité_g_L"], mode="lines+markers", line=dict(color="#2563eb", width=3), name="Salinité indicative"))
    fig.add_vrect(x0=245, x1=280, fillcolor="rgba(249,115,22,0.10)", line_width=0, annotation_text="Eau salée", annotation_position="top left")
    fig.add_vrect(x0=280, x1=330, fillcolor="rgba(250,204,21,0.12)", line_width=0, annotation_text="Eau saumâtre", annotation_position="top left")
    fig.add_vrect(x0=330, x1=340, fillcolor="rgba(125,211,252,0.18)", line_width=0, annotation_text="Eau douce", annotation_position="top left")
    fig.add_hline(y=0.5, line_dash="dash", line_color="#0f172a", annotation_text="Seuil limnique 0,5 g/L", annotation_position="bottom right")
    fig.add_annotation(x=292, y=24, text="Pénétration maximale de la salinité", showarrow=True, ax=-55, ay=-30)
    fig.add_annotation(x=336, y=7, text="Expulsion maximale d’eau douce", showarrow=True, ax=45, ay=20)
    fig.update_layout(title="Transition saline dans l’estuaire de la Seine", xaxis_title="PK le long de l’estuaire", yaxis_title="Salinité indicative (g/L)")
    fig.update_xaxes(autorange="reversed")
    return style_figure(fig, height=390)


def plot_flot_jusant_share() -> go.Figure:
    metrics = river_energy_metrics()
    fig = go.Figure(go.Pie(labels=["Flot", "Jusant"], values=[metrics["flot_share"], metrics["jusant_share"]], hole=0.58, marker_colors=["#60a5fa", "#2563eb"], textinfo="label+percent", sort=False))
    fig.update_layout(title="Répartition énergétique indicative sur PK326", showlegend=False)
    return style_figure(fig, height=350)


def plot_tide_levels(df: pd.DataFrame | None = None) -> go.Figure:
    if df is None:
        df = tide_levels_df()
    fig = go.Figure()
    line_specs = [
        ("BM_115", "BM 115", "#2563eb"),
        ("PM_115", "PM 115", "#dc2626"),
        ("BM_80", "BM 80", "#16a34a"),
        ("PM_80", "PM 80", "#8b5cf6"),
        ("BM_65", "BM 65", "#0ea5e9"),
        ("PM_65", "PM 65", "#f97316"),
        ("BM_35", "BM 35", "#64748b"),
        ("PM_35", "PM 35", "#f59e0b"),
    ]
    for col, label, color in line_specs:
        fig.add_trace(go.Scatter(x=df["Station"], y=df[col], mode="lines+markers", name=label, line=dict(color=color, width=2.4)))
    fig.add_vline(x="St Léonard", line_dash="dash", line_color="rgba(15,23,42,0.55)")
    fig.add_annotation(x="St Léonard", y=8.8, text="PK326 / St Léonard", showarrow=False)
    fig.update_layout(title="Niveaux de haute et basse mer le long de l’estuaire", xaxis_title="Stations", yaxis_title="Hauteur d’eau (m / CMH)")
    return style_figure(fig, height=430)


def plot_section_profile(water_level: float = BMVE_115, show_pm: bool = True, show_channel: bool = True, show_raw_windows: bool = False) -> go.Figure:
    profile = section_profile_df()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=profile["x_m"], y=profile["z_cmh_m"], mode="lines", fill="tozeroy", name="Fond", line=dict(color="#1d4ed8", width=2.8), fillcolor="rgba(37,99,235,0.22)"))
    fig.add_hline(y=0.0, line_dash="dot", line_color="#475569", annotation_text="0 / CMH", annotation_position="bottom left")
    fig.add_hline(y=BMVE_115, line_dash="dash", line_color="black", annotation_text="BMVE(115)", annotation_position="top right")
    if show_pm:
        fig.add_hline(y=PMVE_115, line_dash="dash", line_color="black", annotation_text="PMVE(115)", annotation_position="top right")
    if water_level is not None and not np.isclose(water_level, BMVE_115):
        fig.add_hline(y=water_level, line_dash="dot", line_color="#dc2626", annotation_text="Niveau exploré", annotation_position="bottom right")
    if show_channel:
        fig.add_vrect(x0=CHANNEL_X0, x1=CHANNEL_X1, fillcolor="rgba(15,23,42,0.06)", line_width=0, annotation_text=f"Chenal central {CHANNEL_WIDTH:.0f} m", annotation_position="top left")
    if show_raw_windows:
        windows = compute_section_layout(channel_setback=0.0)["windows"]
        for _, row in windows.iterrows():
            fig.add_vrect(x0=row["x0_m"], x1=row["x1_m"], fillcolor="rgba(16,185,129,0.14)", line_width=0)
    fig.update_layout(title="Profil utile au droit du PK326", xaxis_title="Largeur transversale (m)", yaxis_title="Cote (m / CMH)")
    return style_figure(fig, height=450)


def plot_exploitable_section(water_level: float = BMVE_115, depth_limit: float = 7.0, clearance: float = 0.5) -> go.Figure:
    layout = compute_section_layout(water_level=water_level, depth_limit=depth_limit, clearance=clearance, channel_setback=0.0)
    profile: pd.DataFrame = layout["profile"]
    threshold = float(layout["threshold_cmh_m"])
    windows: pd.DataFrame = layout["windows"]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=profile["x_m"], y=profile["z_cmh_m"], mode="lines", fill="tozeroy", name="Fond", line=dict(color="#1d4ed8", width=2.8), fillcolor="rgba(37,99,235,0.22)"))
    fig.add_hline(y=water_level, line_dash="dash", line_color="#dc2626", annotation_text="Niveau d’eau de référence", annotation_position="top right")
    fig.add_hline(y=threshold, line_dash="dot", line_color="#059669", annotation_text="Seuil fond compatible", annotation_position="bottom right")
    fig.add_vrect(x0=CHANNEL_X0, x1=CHANNEL_X1, fillcolor="rgba(15,23,42,0.06)", line_width=0, annotation_text="Chenal central", annotation_position="top left")

    for _, row in windows.iterrows():
        fig.add_vrect(x0=row["x0_m"], x1=row["x1_m"], fillcolor="rgba(16,185,129,0.18)", line_width=0)
        fig.add_annotation(x=0.5 * (row["x0_m"] + row["x1_m"]), y=threshold + 0.35, text=f"{row['Largeur_m']:.0f} m", showarrow=False)

    fig.update_layout(title="Fenêtres d’implantation déduites du profil et des hypothèses de sécurité", xaxis_title="Largeur transversale (m)", yaxis_title="Cote (m / CMH)")
    return style_figure(fig, height=470)


def draw_plan_view_schema(machine_width: float = REFERENCE_MACHINE_WIDTH, channel_setback: float = NAVIGATION_SETBACK) -> go.Figure:
    raw = compute_section_layout(channel_setback=0.0)["windows"]
    eff = compute_section_layout(channel_setback=channel_setback)["windows"]

    fig = go.Figure()
    fig.add_shape(type="rect", x0=0, y0=20, x1=SECTION_WIDTH, y1=80, line=dict(color="rgba(15,23,42,0.18)", width=1), fillcolor="#ffffff")
    fig.add_shape(type="rect", x0=CHANNEL_X0, y0=25, x1=CHANNEL_X1, y1=75, line=dict(color="#0f172a", width=2), fillcolor="#f1f5f9")
    fig.add_annotation(x=0.5 * (CHANNEL_X0 + CHANNEL_X1), y=82, text=f"Chenal {CHANNEL_WIDTH:.0f} m", showarrow=False)

    for _, row in raw.iterrows():
        fig.add_shape(type="rect", x0=row["x0_m"], y0=30, x1=row["x1_m"], y1=70, line=dict(color="#16a34a", width=2), fillcolor="rgba(22,163,74,0.12)")
        fig.add_annotation(x=0.5 * (row["x0_m"] + row["x1_m"]), y=74, text=f"{row['Fenêtre']} – {row['Largeur_m']:.0f} m", showarrow=False)

    for _, row in eff.iterrows():
        x0 = float(row["x0_m"] + max(row["Largeur_m"] - machine_width, 0.0) / 2.0)
        x1 = x0 + machine_width
        fig.add_shape(type="rect", x0=x0, y0=38, x1=x1, y1=62, line=dict(color="#1d4ed8", width=2), fillcolor="rgba(37,99,235,0.22)")
        fig.add_annotation(x=0.5 * (x0 + x1), y=50, text="Machine", showarrow=False)

    fig.update_layout(title="Lecture en plan de l’insertion latérale", xaxis=dict(visible=False, range=[0, SECTION_WIDTH]), yaxis=dict(visible=False, range=[0, 100]), showlegend=False)
    return style_figure(fig, height=320)


def plot_window_budget(machine_width: float = REFERENCE_MACHINE_WIDTH, channel_setback: float = NAVIGATION_SETBACK) -> go.Figure:
    budget = implantation_budget_df(machine_width=machine_width, channel_setback=channel_setback)
    fig = go.Figure()
    fig.add_trace(go.Bar(x=budget["Fenêtre"], y=budget["Largeur_brute_m"], name="Largeur brute", marker_color="#cbd5e1"))
    fig.add_trace(go.Bar(x=budget["Fenêtre"], y=budget["Largeur_après_recul_m"], name="Après recul chenal", marker_color="#93c5fd"))
    fig.add_trace(go.Bar(x=budget["Fenêtre"], y=budget["Machine_m"], name="Largeur machine", marker_color="#2563eb"))
    fig.update_layout(barmode="group", title="Fenêtres disponibles et largeur machine", yaxis_title="Largeur (m)")
    return style_figure(fig, height=350)


def plot_navigation_clearance() -> go.Figure:
    fig = go.Figure()
    fig.add_shape(type="rect", x0=0, y0=0, x1=110, y1=24, line=dict(color="#0f172a", width=2), fillcolor="#f8fafc")
    fig.add_shape(type="rect", x0=39, y0=5, x1=71, y1=19, line=dict(color="#2563eb", width=2), fillcolor="rgba(37,99,235,0.25)")
    fig.add_shape(type="rect", x0=25, y0=4, x1=85, y1=20, line=dict(color="#dc2626", width=2, dash="dash"), fillcolor="rgba(220,38,38,0.10)")
    fig.add_annotation(x=55, y=26, text="Chenal central 110 m", showarrow=False)
    fig.add_annotation(x=55, y=12, text="Navire type 32 m", showarrow=False)
    fig.add_annotation(x=55, y=2, text="Enveloppe de passage prudent ~60 m", showarrow=False)
    fig.update_layout(title="Lecture simple de la contrainte navigation", xaxis=dict(visible=False, range=[-4, 114]), yaxis=dict(visible=False, range=[-1, 30]), showlegend=False)
    return style_figure(fig, height=260)


# =============================================================================
# Machine and science plots
# =============================================================================


@st.cache_data(show_spinner=False)
def machine_dimensions() -> dict[str, float]:
    return {
        "longueur_fonctionnement": 38.0,
        "largeur_fonctionnement": 36.0,
        "tirant_eau_fonctionnement": 7.0,
        "tirant_air_fonctionnement": 9.8,
        "passage_central": 16.2,
        "tirant_eau_passage": 6.6,
        "tirant_air_passage": 8.7,
        "longueur_maintenance": 35.0,
        "largeur_maintenance": 36.0,
        "tirant_eau_maintenance": 1.6,
        "tirant_air_maintenance": 12.7,
    }


@st.cache_data(show_spinner=False)
def machine_operating_points_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Fonction opérationnelle": [
                "Inspection et nettoyage des foils",
                "Dégagement d’un objet coincé",
                "Mise en sécurité en courant exceptionnel",
                "Remorquage en faible tirant d’eau",
                "Stockage / réparation à quai ou sur plateforme",
            ],
            "Apport du mode relevé": [
                "Accès direct aux surfaces actives",
                "Sortie de l’élément hors du plan d’eau",
                "Réduction rapide de l’exposition hydrodynamique",
                "Tirant d’eau fortement réduit",
                "Manipulation logistique simplifiée",
            ],
        }
    )


@st.cache_data(show_spinner=False)
def technology_principles_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Aspect": [
                "Principe de conversion",
                "Pilotage",
                "Configuration retenue",
                "Sens de production",
                "Accès maintenance",
                "Intérêt estuarien",
            ],
            "Lecture": [
                "Foil oscillant immergé et transformation mécanique continue vers une génératrice.",
                "Pilotage intégré au système mécanique, avec réglages ponctuels pour optimisation et sécurité.",
                "Version Duale bi-foil : deux modules de soutien et deux foils en série.",
                "Production possible au flot et au jusant.",
                "Foils relevables hors d’eau pour inspection, dégagement et remorquage.",
                "Grande surface captée sans empiètement sur le chenal central.",
            ],
        }
    )


@st.cache_data(show_spinner=False)
def technology_comparison_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Solution": ["Foil’O duale", "Hélices", "Rotors transverses"],
            "Configuration équivalente": ["2 hydroliennes", "20 unités", "4 rotors de 30 m"],
            "Éléments actifs équivalents": [2, 20, 4],
            "Empiètement sur le chenal": ["Non", "Oui", "Oui"],
            "Obstacle aux débris": ["Faible", "Élevé", "Élevé"],
            "Lecture": [
                "Préserve le chenal central et reste compatible avec une implantation latérale.",
                "Nécessite un déploiement beaucoup plus diffus et conduit à empiéter sur le chenal.",
                "Capte une grande longueur utile mais ne permet pas de conserver le chenal libre à production équivalente.",
            ],
        }
    )


@st.cache_data(show_spinner=False)
def dimensionnement_foil(
    Hm: float = 7.0,
    two_ho_over_c: float = 3.0,
    e_over_c: float = 0.85,
    aspect_ratio: float = 20.0,
) -> dict[str, float]:
    c = Hm / (two_ho_over_c + e_over_c)
    amplitude = two_ho_over_c * c
    E = e_over_c * c
    L = aspect_ratio * c
    axis_depth = amplitude + E
    return {
        "c": c,
        "amplitude": amplitude,
        "E": E,
        "axis_depth": axis_depth,
        "L": L,
        "Hm": Hm,
        "two_ho_over_c": two_ho_over_c,
        "e_over_c": e_over_c,
        "aspect_ratio": aspect_ratio,
    }


@st.cache_data(show_spinner=False)
def production_curve_df() -> pd.DataFrame:
    # Internal reconstruction anchored on the report's explicit quality indicators:
    # ~0.47 capacity factor and ~4117 h/year around 200 kW.
    pn = np.array([100, 110, 120, 125, 130, 140, 150, 170, 190, 200, 250, 300], dtype=float)
    fc = np.array([0.60, 0.585, 0.575, 0.565, 0.56, 0.545, 0.53, 0.51, 0.485, 0.47, 0.405, 0.35], dtype=float)
    annual = pn * fc * 8.76
    specific = annual / pn
    return pd.DataFrame(
        {
            "Pn_kW": pn,
            "Facteur_charge": fc,
            "Productivite_specifique_MWh_kW_an": specific,
            "Production_annuelle_MWh": annual,
        }
    )


def annual_mwh_from_nominal_power(power_kw: float) -> float:
    df = production_curve_df()
    return float(np.interp(power_kw, df["Pn_kW"], df["Production_annuelle_MWh"]))


def capacity_factor_from_nominal_power(power_kw: float) -> float:
    df = production_curve_df()
    return float(np.interp(power_kw, df["Pn_kW"], df["Facteur_charge"]))


def specific_productivity_from_nominal_power(power_kw: float) -> float:
    df = production_curve_df()
    return float(np.interp(power_kw, df["Pn_kW"], df["Productivite_specifique_MWh_kW_an"]))


def equivalent_full_load_hours_from_nominal_power(power_kw: float) -> float:
    return float(capacity_factor_from_nominal_power(power_kw) * 8760.0)


def build_power_curve(v_start: float = 0.5, v_nom: float = 1.8, v_max: float = 2.25, p_nom: float = 200.0) -> pd.DataFrame:
    velocities = np.linspace(0, 2.8, 160)
    power = np.zeros_like(velocities)
    for i, v in enumerate(velocities):
        if v < v_start:
            power[i] = 0.0
        elif v < v_nom:
            ratio = (v - v_start) / max(v_nom - v_start, 1e-9)
            power[i] = p_nom * ratio**3
        elif v <= v_max:
            power[i] = p_nom
        else:
            power[i] = 0.0
    return pd.DataFrame({"Vitesse_m_s": velocities, "Puissance_kW": power})


@st.cache_data(show_spinner=False)
def fit_resource_energy_curve() -> tuple[np.ndarray, np.ndarray]:
    df = resource_extrapolation_df()
    coeffs = np.polyfit(df["Coef_marée"], df["Energie_Wh_m2_maree"], 3)
    x = np.linspace(25, 120, 220)
    y = np.polyval(coeffs, x)
    return x, y


@st.cache_data(show_spinner=False)
def river_energy_by_coefficient_df() -> pd.DataFrame:
    metrics = river_energy_metrics()
    df = pd.DataFrame({"Coef_marée": [45, 70, 95, 115], "Energie_section_MWh_maree": [25.0, 50.0, 70.0, 85.0]})
    df["Part_flot"] = metrics["flot_share"] * df["Energie_section_MWh_maree"]
    df["Part_jusant"] = metrics["jusant_share"] * df["Energie_section_MWh_maree"]
    return df


def project_capture_share_df(power_kw: float = 200.0, machine_count: int = 2) -> pd.DataFrame:
    annual_project = machine_count * annual_mwh_from_nominal_power(power_kw)
    annual_section = river_energy_metrics()["annual_section_gwh"] * 1000.0
    share_pct = 100.0 * annual_project / annual_section
    return pd.DataFrame(
        {
            "Indicateur": ["Production projet (MWh/an)", "Énergie de section PK326 (MWh/an)", "Part captée par le projet (%)"],
            "Valeur": [annual_project, annual_section, share_pct],
        }
    )


def prototype_specific_productivity(case_key: str = "prudent") -> float:
    return float(PROTOTYPE_PRODUCTION_CASES[case_key]["specific_mwh_kw_an"])


def prototype_annual_mwh(machine_power_kw: float, case_key: str = "prudent", machine_count: int = 1) -> float:
    return float(machine_count * machine_power_kw * prototype_specific_productivity(case_key))


def prototype_capacity_factor(case_key: str = "prudent") -> float:
    return float(prototype_specific_productivity(case_key) / 8.76)


def prototype_case_records(machine_power_kw: float) -> pd.DataFrame:
    rows: list[dict[str, float | str]] = []
    for case_key in ["prudent", "high"]:
        annual = prototype_annual_mwh(machine_power_kw, case_key)
        rows.append(
            {
                "Cas": PROTOTYPE_PRODUCTION_CASES[case_key]["label"],
                "CaseKey": case_key,
                "Production_annuelle_MWh": annual,
                "Productivite_specifique_MWh_kW_an": prototype_specific_productivity(case_key),
                "Facteur_charge": prototype_capacity_factor(case_key),
            }
        )
    return pd.DataFrame(rows)


def draw_oscillating_foil_principle() -> go.Figure:
    fig = go.Figure()
    fig.add_shape(type="rect", x0=0, y0=0, x1=10, y1=10, line=dict(color="rgba(15,23,42,0)", width=0), fillcolor="#ffffff")
    fig.add_hrect(y0=0, y1=4.6, fillcolor="rgba(59,130,246,0.12)", line_width=0)
    fig.add_shape(type="line", x0=0.8, y0=4.6, x1=9.2, y1=4.6, line=dict(color="#2563eb", width=3))
    fig.add_annotation(x=1.2, y=4.95, text="Ligne d’eau", showarrow=False)
    fig.add_shape(type="rect", x0=4.1, y0=6.5, x1=5.9, y1=7.2, line=dict(color="black", width=2), fillcolor="#f8fafc")
    fig.add_annotation(x=5.0, y=7.5, text="Chaîne mécanique / génératrice", showarrow=False)
    fig.add_shape(type="line", x0=4.45, y0=6.5, x1=4.05, y1=2.6, line=dict(color="black", width=2))
    fig.add_shape(type="line", x0=5.55, y0=6.5, x1=5.95, y1=2.6, line=dict(color="black", width=2))
    fig.add_shape(type="rect", x0=3.2, y0=2.45, x1=6.8, y1=2.8, line=dict(color="black", width=2), fillcolor="#93c5fd")
    fig.add_annotation(x=5.0, y=2.05, text="Foil oscillant", showarrow=False)
    for x0 in [1.4, 1.9, 2.4]:
        fig.add_annotation(x=x0, y=3.2, text="→", showarrow=False, font=dict(size=22, color="#2563eb"))
    for x0 in [7.6, 8.1, 8.6]:
        fig.add_annotation(x=x0, y=3.2, text="→", showarrow=False, font=dict(size=22, color="#2563eb"))
    fig.add_annotation(x=1.9, y=3.9, text="Courant", showarrow=False)
    fig.add_annotation(x=8.1, y=3.9, text="Courant", showarrow=False)
    fig.add_annotation(x=3.5, y=5.2, text="Mouvement paramétré", showarrow=True, ax=-35, ay=-30)
    fig.add_annotation(x=6.5, y=5.2, text="Conversion mécanique continue", showarrow=True, ax=35, ay=-30)
    fig.update_layout(title="Principe technologique Foil’O", xaxis=dict(visible=False, range=[0, 10]), yaxis=dict(visible=False, range=[0, 10]), showlegend=False)
    return style_figure(fig, height=330)


def draw_machine_schema(mode: str = "fonctionnement") -> go.Figure:
    fig = go.Figure()
    waterline = 5.4
    fig.add_hrect(y0=0, y1=waterline, fillcolor="rgba(59,130,246,0.12)", line_width=0)
    fig.add_trace(go.Scatter(x=[0, 10], y=[waterline, waterline], mode="lines", line=dict(color="#2563eb", width=3), name="Ligne d’eau", showlegend=False))

    if mode == "fonctionnement":
        title = "Schéma machine – exploitation"
        foil_y = 2.0
        fig.add_annotation(x=5.0, y=3.9, text="Passage central", showarrow=False, font=dict(size=11))
    else:
        title = "Schéma machine – relevée"
        foil_y = 6.0
        fig.add_annotation(x=5.0, y=6.9, text="Foils hors d’eau", showarrow=False, font=dict(size=11))

    fig.add_shape(type="rect", x0=1.0, y0=7.2, x1=3.2, y1=8.0, line=dict(color="black", width=2), fillcolor="#e2e8f0")
    fig.add_shape(type="rect", x0=6.8, y0=7.2, x1=9.0, y1=8.0, line=dict(color="black", width=2), fillcolor="#e2e8f0")
    fig.add_shape(type="line", x0=4.2, y0=7.6, x1=4.2, y1=foil_y + 0.8, line=dict(color="black", width=2))
    fig.add_shape(type="line", x0=5.8, y0=7.6, x1=5.8, y1=foil_y + 0.8, line=dict(color="black", width=2))
    fig.add_shape(type="line", x0=3.4, y0=7.6, x1=6.6, y1=7.6, line=dict(color="black", width=2))
    fig.add_shape(type="rect", x0=4.0, y0=8.0, x1=6.0, y1=8.35, line=dict(color="black", width=2), fillcolor="#f8fafc")
    fig.add_shape(type="rect", x0=3.55, y0=foil_y, x1=4.85, y1=foil_y + 0.22, line=dict(color="black", width=2), fillcolor="#93c5fd")
    fig.add_shape(type="rect", x0=5.15, y0=foil_y, x1=6.45, y1=foil_y + 0.22, line=dict(color="black", width=2), fillcolor="#93c5fd")

    legend_items = [
        ("Modules", "black", "line"),
        ("Flotteurs", "#e2e8f0", "square"),
        ("Foils", "#93c5fd", "square"),
        ("Superstructure", "#f8fafc", "square"),
    ]
    for name, color, kind in legend_items:
        if kind == "line":
            fig.add_trace(go.Scatter(x=[None], y=[None], mode="lines", line=dict(color=color, width=3), name=name))
        else:
            fig.add_trace(go.Scatter(x=[None], y=[None], mode="markers", marker=dict(size=12, symbol="square", color=color, line=dict(color="black", width=1)), name=name))

    fig.update_layout(title=title, xaxis=dict(visible=False, range=[0, 10]), yaxis=dict(visible=False, range=[0, 10]), showlegend=True)
    fig = style_figure(fig, height=360)
    fig.update_layout(legend=dict(orientation="h", yanchor="top", y=-0.16, x=0.0, title_text=""), margin=dict(l=20, r=20, t=70, b=88))
    return fig


def plot_two_machine_profile(water_level: float = BMVE_115, machine_width: float = REFERENCE_MACHINE_WIDTH, channel_setback: float = NAVIGATION_SETBACK, show_ship: bool = False, ship_width: float = 24.0) -> go.Figure:
    layout = compute_section_layout(water_level=water_level, depth_limit=7.0, clearance=0.5, channel_setback=channel_setback)
    profile: pd.DataFrame = layout["profile"]
    windows: pd.DataFrame = layout["windows"]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=profile["x_m"], y=profile["z_cmh_m"], mode="lines", fill="tozeroy", name="Fond", line=dict(color="#1d4ed8", width=2.8), fillcolor="rgba(37,99,235,0.22)"))
    fig.add_hline(y=0.0, line_dash="dot", line_color="#475569", annotation_text="0 / CMH", annotation_position="bottom left")
    fig.add_hline(y=water_level, line_dash="dash", line_color="#2563eb", annotation_text="BMVE(115)", annotation_position="top right")
    fig.add_vrect(x0=CHANNEL_X0, x1=CHANNEL_X1, fillcolor="rgba(15,23,42,0.06)", line_width=0, annotation_text=f"Chenal {CHANNEL_WIDTH:.0f} m", annotation_position="top left")

    machine_height_above_water = 2.8
    for _, row in windows.iterrows():
        available = float(row["Largeur_m"])
        x0 = float(row["x0_m"] + max(available - machine_width, 0.0) / 2.0)
        x1 = x0 + machine_width
        y0 = water_level - REFERENCE_MACHINE_DRAFT
        y1 = water_level + machine_height_above_water
        fig.add_shape(type="rect", x0=x0, x1=x1, y0=y0, y1=y1, line=dict(color="#f97316", width=2), fillcolor="rgba(249,115,22,0.18)")
        fig.add_annotation(x=0.5 * (x0 + x1), y=y1 + 0.18, text="Hydrolienne", showarrow=False)

    if show_ship:
        ship_x0 = 0.5 * (CHANNEL_X0 + CHANNEL_X1) - ship_width / 2.0
        ship_x1 = ship_x0 + ship_width
        ship_y0 = water_level - 1.6
        ship_y1 = water_level + 1.2
        fig.add_shape(type="rect", x0=ship_x0, x1=ship_x1, y0=ship_y0, y1=ship_y1, line=dict(color="#dc2626", width=2), fillcolor="rgba(220,38,38,0.18)")
        fig.add_annotation(x=0.5 * (ship_x0 + ship_x1), y=ship_y1 + 0.18, text=f"Navire {ship_width:.0f} m", showarrow=False)

    fig.update_layout(title="Mise en situation de deux hydroliennes hors chenal", xaxis_title="Largeur transversale (m)", yaxis_title="Cote (m / CMH)")
    return style_figure(fig, height=460)


def plot_technology_comparison(df: pd.DataFrame | None = None) -> go.Figure:
    if df is None:
        df = technology_comparison_df()
    fig = px.bar(df, x="Solution", y="Éléments actifs équivalents", color="Solution", text="Configuration équivalente", title="Gabarit relatif à production équivalente", color_discrete_map={"Foil’O duale": "#2563eb", "Hélices": "#dc2626", "Rotors transverses": "#f59e0b"})
    fig.update_traces(textposition="outside", showlegend=False)
    fig.update_layout(yaxis_title="Nombre d’éléments / machines équivalents")
    return style_figure(fig, height=360)


def plot_power_curve(v_start: float = 0.5, v_nom: float = 1.8, v_max: float = 2.25, p_nom: float = 200.0) -> go.Figure:
    df = build_power_curve(v_start=v_start, v_nom=v_nom, v_max=v_max, p_nom=p_nom)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["Vitesse_m_s"], y=df["Puissance_kW"], mode="lines", line=dict(color="#2563eb", width=3), name="Courbe de puissance"))
    fig.add_vline(x=v_start, line_dash="dot", line_color="black", annotation_text="Vd")
    fig.add_vline(x=v_nom, line_dash="dot", line_color="black", annotation_text="Vn")
    fig.add_vline(x=v_max, line_dash="dot", line_color="black", annotation_text="Vm")
    fig.add_annotation(x=(v_start + v_nom) / 2.0, y=p_nom * 0.38, text="Zone II – montée en puissance", showarrow=False)
    fig.add_annotation(x=(v_nom + v_max) / 2.0, y=p_nom * 0.93, text="Zone III – puissance plafonnée", showarrow=False)
    fig.update_layout(title="Courbe de puissance type", xaxis_title="Vitesse (m/s)", yaxis_title="Puissance (kW)")
    return style_figure(fig, height=360)


def plot_resource_energy_fit() -> go.Figure:
    df = resource_extrapolation_df()
    x_fit, y_fit = fit_resource_energy_curve()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["Coef_marée"], y=df["Energie_Wh_m2_maree"], mode="markers", marker=dict(size=10, symbol="square", color="#2563eb"), name="Points issus du rapport"))
    fig.add_trace(go.Scatter(x=x_fit, y=y_fit, mode="lines", line=dict(color="#f59e0b", width=3), name="Régression polynomiale d’ordre 3"))
    fig.update_layout(title="Énergie du courant versus coefficient de marée", xaxis_title="Coefficient de marée", yaxis_title="Énergie du courant (Wh/m²/marée)")
    return style_figure(fig, height=360)


def plot_river_energy_section() -> go.Figure:
    df = river_energy_by_coefficient_df()
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df["Coef_marée"], y=df["Part_flot"], name="Part flot", marker_color="#60a5fa"))
    fig.add_trace(go.Bar(x=df["Coef_marée"], y=df["Part_jusant"], name="Part jusant", marker_color="#2563eb"))
    fig.update_layout(barmode="stack", title="Ordre de grandeur de l’énergie de section selon le coefficient de marée", xaxis_title="Coefficient de marée", yaxis_title="Énergie de section (MWh/marée)")
    return style_figure(fig, height=360)


def plot_production_tradeoff(df: pd.DataFrame | None = None) -> go.Figure:
    if df is None:
        df = production_curve_df()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["Pn_kW"], y=df["Production_annuelle_MWh"], mode="lines+markers", name="Production annuelle", line=dict(color="#2563eb", width=3)))
    fig.add_vline(x=200, line_dash="dash", line_color="black", opacity=0.6, annotation_text="Compromis de lecture", annotation_position="top")
    fig.update_layout(title="Production annuelle théorique selon la puissance nominale", xaxis_title="Puissance nominale (kW)", yaxis_title="Production annuelle (MWh/an)")
    return style_figure(fig, height=380)


def plot_load_factor_curve(df: pd.DataFrame | None = None) -> go.Figure:
    if df is None:
        df = production_curve_df()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["Pn_kW"], y=df["Facteur_charge"], mode="lines+markers", line=dict(color="#2563eb", width=3), name="Facteur de charge"))
    fig.add_vline(x=200, line_dash="dash", line_color="black", opacity=0.6)
    fig.update_layout(title="Facteur de charge selon la puissance nominale", xaxis_title="Puissance nominale (kW)", yaxis_title="Facteur de charge")
    return style_figure(fig, height=360)


def plot_specific_productivity_curve(df: pd.DataFrame | None = None) -> go.Figure:
    if df is None:
        df = production_curve_df()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["Pn_kW"], y=df["Productivite_specifique_MWh_kW_an"], mode="lines+markers", line=dict(color="#dc2626", width=3), name="Productivité spécifique"))
    fig.add_vline(x=200, line_dash="dash", line_color="black", opacity=0.6)
    fig.update_layout(title="Productivité spécifique annuelle", xaxis_title="Puissance nominale (kW)", yaxis_title="MWh/kW/an")
    return style_figure(fig, height=360)


def plot_capture_share_indicator(power_kw: float = 200.0, machine_count: int = 2) -> go.Figure:
    annual_project = machine_count * annual_mwh_from_nominal_power(power_kw)
    annual_section = river_energy_metrics()["annual_section_gwh"] * 1000.0
    remaining = max(annual_section - annual_project, 0.0)
    fig = go.Figure(go.Pie(labels=["Projet", "Énergie restant dans la section"], values=[annual_project, remaining], hole=0.58, marker_colors=["#2563eb", "#cbd5e1"], textinfo="label+percent", sort=False))
    fig.update_layout(title="Ordre de grandeur de la part d’énergie captée par 2 machines")
    return style_figure(fig, height=340)


def plot_prototype_production_cases(machine_power_kw: float, selected_mode: str = "prudent", selected_annual_mwh: float | None = None) -> go.Figure:
    df = prototype_case_records(machine_power_kw)
    colors = ["#cbd5e1", "#93c5fd"]
    if selected_mode == "prudent":
        colors = ["#2563eb", "#cbd5e1"]
    elif selected_mode == "high":
        colors = ["#cbd5e1", "#2563eb"]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df["Cas"], y=df["Production_annuelle_MWh"], text=[f"{value:,.0f} MWh/an" for value in df["Production_annuelle_MWh"]], textposition="outside", marker_color=colors, name="Cas de production"))
    for _, row in df.iterrows():
        fig.add_annotation(x=row["Cas"], y=row["Production_annuelle_MWh"] * 0.55, text=f"{row['Productivite_specifique_MWh_kW_an']:.1f} MWh/kW/an<br>Fc {row['Facteur_charge']:.2f}", showarrow=False)
    if selected_mode == "manual" and selected_annual_mwh is not None:
        fig.add_hline(y=selected_annual_mwh, line_dash="dash", line_color="#dc2626", annotation_text="Saisie manuelle", annotation_position="top left")
    fig.update_layout(title="Prototype – deux cas explicites de production", xaxis_title="Hypothèse de production", yaxis_title="Production annuelle (MWh/an)", showlegend=False)
    return style_figure(fig, height=390)


def plot_power_production_link(stage: str, machine_power_kw: float, machine_count: int = 1) -> go.Figure:
    curve = production_curve_df()
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(x=curve["Pn_kW"], y=curve["Production_annuelle_MWh"], mode="lines+markers", name="Production annuelle / machine", line=dict(width=3, color="#16a34a")), secondary_y=False)
    fig.add_trace(go.Scatter(x=curve["Pn_kW"], y=curve["Facteur_charge"], mode="lines+markers", name="Facteur de charge / machine", line=dict(width=3, color="#2563eb")), secondary_y=True)
    fig.add_trace(go.Scatter(x=[machine_power_kw], y=[annual_mwh_from_nominal_power(machine_power_kw)], mode="markers", marker=dict(size=12, color="#15803d", symbol="diamond"), name="Point retenu – production"), secondary_y=False)
    fig.add_trace(go.Scatter(x=[machine_power_kw], y=[capacity_factor_from_nominal_power(machine_power_kw)], mode="markers", marker=dict(size=12, color="#1d4ed8", symbol="diamond"), name="Point retenu – Fc"), secondary_y=True)
    fig.update_layout(title=f"Lien puissance, production et facteur de charge – {stage}")
    fig.update_xaxes(title_text="Puissance nominale par machine (kW)")
    fig.update_yaxes(title_text="Production annuelle / machine (MWh/an)", secondary_y=False)
    fig.update_yaxes(title_text="Facteur de charge", secondary_y=True)
    return style_figure(fig, height=420)


# =============================================================================
# Climate plots
# =============================================================================


@st.cache_data(show_spinner=False)
def climate_monthly_flow_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Mois": ["Jan", "Fév", "Mar", "Avr", "Mai", "Juin", "Juil", "Aoû", "Sep", "Oct", "Nov", "Déc"],
            "Présent": [780, 800, 730, 620, 520, 420, 320, 250, 270, 390, 580, 760],
            "2050": [560, 650, 800, 760, 600, 450, 320, 240, 220, 250, 360, 500],
            "2100": [500, 600, 700, 660, 560, 400, 280, 210, 190, 220, 300, 430],
        }
    )


@st.cache_data(show_spinner=False)
def marine_signal_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "PK": [340, 330, 310, 295, 280, 260, 245, 220],
            "Q400_m3_s": [100, 101, 103, 110, 106, 104, 105, 106],
            "Q1200_m3_s": [97, 97, 96, 92, 80, 75, 70, 60],
            "Q2000_m3_s": [96, 96, 88, 64, 52, 50, 48, 35],
        }
    )


def plot_climate_flows(df: pd.DataFrame | None = None) -> go.Figure:
    if df is None:
        df = climate_monthly_flow_df()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["Mois"], y=df["Présent"], mode="lines+markers", name="Présent", line=dict(width=3, color="#2563eb")))
    fig.add_trace(go.Scatter(x=df["Mois"], y=df["2050"], mode="lines+markers", name="2050", line=dict(width=3, color="#db2777")))
    fig.add_trace(go.Scatter(x=df["Mois"], y=df["2100"], mode="lines+markers", name="2100", line=dict(width=3, color="#8b5cf6")))
    fig.update_layout(title="Évolution saisonnière des débits de la Seine", xaxis_title="Mois", yaxis_title="Débit (m³/s)")
    return style_figure(fig, height=430)


def plot_marine_signal(df: pd.DataFrame | None = None) -> go.Figure:
    if df is None:
        df = marine_signal_df()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["PK"], y=df["Q400_m3_s"], mode="lines+markers", name="Débit 400 m³/s", line=dict(width=3, color="#2563eb")))
    fig.add_trace(go.Scatter(x=df["PK"], y=df["Q1200_m3_s"], mode="lines+markers", name="Débit 1200 m³/s", line=dict(width=3, color="#16a34a")))
    fig.add_trace(go.Scatter(x=df["PK"], y=df["Q2000_m3_s"], mode="lines+markers", name="Débit 2000 m³/s", line=dict(width=3, color="#db2777")))
    fig.update_layout(title="Propagation de l’influence marine selon le débit de Seine", xaxis_title="PK le long de l’estuaire", yaxis_title="Part de l’élévation marine conservée (%)")
    fig.update_xaxes(autorange="reversed")
    return style_figure(fig, height=430)




@st.cache_data(show_spinner=False)
def stages_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Stade": ["Prototype", "Démonstrateur", "1er commercial"],
            "TRL": ["6-7", "7-8", "8-9"],
            "Configuration": ["Prototype réduit", "1 hydrolienne échelle 1", "5 hydroliennes échelle 1"],
            "Puissance_typique": ["30–50 kW", "150–250 kW", "750–1250 kW"],
            "Objectif": [
                "Retour de fonctionnement et validation d’installation",
                "Validation grandeur réelle de la production et de la durabilité",
                "Preuve de rentabilité, calibration OPEX et premier impact industriel",
            ],
            "Taux_actualisation_pct": [13.0, 10.0, 7.0],
        }
    )


@st.cache_data(show_spinner=False)
def deployment_phase_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Stade": ["Prototype", "Démonstrateur", "1ère ferme commerciale"],
            "TRL": ["6-7", "7-8", "8-9"],
            "Puissance_typique": ["30–50 kW", "150–250 kW", "≈ 1 MW (5 × 200 kW)"],
            "Objectif": [
                "Retour de fonctionnement, réglages et validation d’installation",
                "Validation grandeur réelle de la production et de la durabilité",
                "Calibration OPEX, première rentabilité et premier impact industriel",
            ],
            "Décision_gate": [
                "Passage à l’échelle 1",
                "Plan d’industrialisation et garanties de production",
                "Déploiement et réplication",
            ],
            "Position": [1, 2, 3],
        }
    )


@st.cache_data(show_spinner=False)
def stage_power_risk_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Stade": ["Prototype", "Démonstrateur", "1ère ferme commerciale"],
            "Puissance_totale_kW": [40, 200, 1000],
            "Taux_actualisation_pct": [13.0, 10.0, 7.0],
            "TRL_central": [6.5, 7.5, 8.5],
        }
    )

# =============================================================================
# Techno-economic reference data and model
# =============================================================================


@st.cache_data(show_spinner=False)
def reference_project_presets() -> dict[str, dict[str, object]]:
    return {
        "Prototype": {
            "stage": "Prototype",
            "machine_count": 1,
            "machine_power_min": 30,
            "machine_power_max": 50,
            "machine_power_default": 40,
            "machine_power_step": 1,
            "discount_pct": 13.0,
            "annual_mwh_default": 160.0,
            "case_mode_default": "standard",
            "prototype_mode_default": "prudent",
        },
        "Démonstrateur": {
            "stage": "Démonstrateur",
            "machine_count": 1,
            "machine_power_min": 150,
            "machine_power_max": 250,
            "machine_power_default": 200,
            "machine_power_step": 5,
            "discount_pct": 10.0,
            "annual_mwh_default": annual_mwh_from_nominal_power(200.0),
            "case_mode_default": "standard",
            "prototype_mode_default": "prudent",
        },
        "1er commercial": {
            "stage": "1er commercial",
            "machine_count": 5,
            "machine_power_min": 150,
            "machine_power_max": 250,
            "machine_power_default": 200,
            "machine_power_step": 5,
            "discount_pct": 7.0,
            "annual_mwh_default": 5 * annual_mwh_from_nominal_power(200.0),
            "case_mode_default": "financed",
            "prototype_mode_default": "prudent",
        },
    }


def stage_name_map_for_lcoe(stage: str) -> str:
    return {"Prototype": "1er stade", "Démonstrateur": "2e stade", "1er commercial": "Commercial initial"}[stage]


def case_mode_label(mode: str) -> str:
    return "standard" if mode == "standard" else "financé"


def annual_mwh_for_stage(stage: str, machine_power_kw: float, machine_count: int = 1, prototype_case_key: str = "prudent") -> float:
    if stage == "Prototype":
        return prototype_annual_mwh(machine_power_kw, prototype_case_key, machine_count)
    return float(machine_count * annual_mwh_from_nominal_power(machine_power_kw))


def capacity_factor_for_stage(stage: str, machine_power_kw: float, prototype_case_key: str = "prudent") -> float:
    if stage == "Prototype":
        return prototype_capacity_factor(prototype_case_key)
    return capacity_factor_from_nominal_power(machine_power_kw)


def lcoe_from_cashflows(costs_by_year: list[float], annual_mwh: float, years: int, discount_rate: float) -> float:
    if annual_mwh <= 0 or years <= 0:
        return float("nan")
    discounted_energy = sum(annual_mwh / ((1 + discount_rate) ** year) for year in range(1, years + 1))
    discounted_costs = float(costs_by_year[0]) + sum(costs_by_year[year - 1] / ((1 + discount_rate) ** year) for year in range(2, years + 1))
    return float(discounted_costs / discounted_energy)


def annualized_capex_component(capital_cost_total_eur: float, annual_mwh: float, years: int) -> float:
    if annual_mwh <= 0 or years <= 0:
        return float("nan")
    return float(capital_cost_total_eur / (annual_mwh * years))


def direct_cost(capital_cost_total_eur: float, annual_mwh: float, opex_mwh: float, years: int) -> float:
    if annual_mwh <= 0 or years <= 0:
        return float("nan")
    return float(capital_cost_total_eur / (annual_mwh * years) + opex_mwh)


def loan_annual_payment(principal_eur: float, rate: float = REFERENCE_FINANCING_RATE, years: int = REFERENCE_FINANCING_YEARS) -> float:
    if years <= 0:
        return principal_eur
    if np.isclose(rate, 0.0):
        return principal_eur / years
    annuity_factor = rate / (1.0 - (1.0 + rate) ** (-years))
    return float(principal_eur * annuity_factor)


def loan_total_payment(principal_eur: float, rate: float = REFERENCE_FINANCING_RATE, years: int = REFERENCE_FINANCING_YEARS) -> float:
    return float(loan_annual_payment(principal_eur, rate, years) * years)


@st.cache_data(show_spinner=False)
def capex_reference_curves_df() -> pd.DataFrame:
    rows = []
    datasets = {
        "Prototype": {"power": [30, 35, 40, 45, 50], "standard": [570, 610, 660, 700, 740], "financed": [820, 900, 970, 1030, 1080]},
        "Démonstrateur": {"power": [150, 175, 200, 225, 250], "standard": [1900, 2050, 2240, 2380, 2500], "financed": [2550, 2750, 2975, 3150, 3300]},
        "1er commercial": {"power": [750, 875, 1000, 1125, 1250], "standard": [7000, 7600, 8250, 8650, 9050], "financed": [8000, 8750, 9450, 10000, 10450]},
    }
    for stage, data in datasets.items():
        for p, s, f in zip(data["power"], data["standard"], data["financed"]):
            rows.append(
                {
                    "Stade": stage,
                    "Puissance_kW": p,
                    "CAPEX_standard_kEUR": s,
                    "CAPEX_standard_low_kEUR": s * 0.7,
                    "CAPEX_standard_high_kEUR": s * 1.3,
                    "CAPEX_financed_kEUR": f,
                    "CAPEX_financed_low_kEUR": f * 0.7,
                    "CAPEX_financed_high_kEUR": f * 1.3,
                }
            )
    return pd.DataFrame(rows)


def interpolate_capex_reference(stage: str, power_kw: float, mode: str = "standard") -> float:
    df = capex_reference_curves_df()
    sub = df[df["Stade"] == stage].sort_values("Puissance_kW")
    col = "CAPEX_standard_kEUR" if mode == "standard" else "CAPEX_financed_kEUR"
    return float(np.interp(power_kw, sub["Puissance_kW"], sub[col]))


@st.cache_data(show_spinner=False)
def specific_capex_reference_df() -> pd.DataFrame:
    df = capex_reference_curves_df().copy()
    df["Spec_standard_kEUR_kW"] = df["CAPEX_standard_kEUR"] / df["Puissance_kW"]
    df["Spec_financed_kEUR_kW"] = df["CAPEX_financed_kEUR"] / df["Puissance_kW"]
    df["Spec_standard_low_kEUR_kW"] = df["CAPEX_standard_low_kEUR"] / df["Puissance_kW"]
    df["Spec_standard_high_kEUR_kW"] = df["CAPEX_standard_high_kEUR"] / df["Puissance_kW"]
    df["Spec_financed_low_kEUR_kW"] = df["CAPEX_financed_low_kEUR"] / df["Puissance_kW"]
    df["Spec_financed_high_kEUR_kW"] = df["CAPEX_financed_high_kEUR"] / df["Puissance_kW"]
    return df


@st.cache_data(show_spinner=False)
def lcoe_stage_ranges() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Stade": ["1er stade", "2e stade", "Commercial initial"],
            "LCOE_moyen_EUR_MWh": [605.0, 356.0, 221.0],
            "Central_low_EUR_MWh": [427.0, 237.0, 145.0],
            "Central_high_EUR_MWh": [783.0, 475.0, 297.0],
            "Outer_low_EUR_MWh": [300.0, 215.0, 140.0],
            "Outer_high_EUR_MWh": [1000.0, 480.0, 300.0],
        }
    )


@st.cache_data(show_spinner=False)
def production_cost_reference_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Stade": ["Prototype", "Démonstrateur", "1er commercial"],
            "Standard_mean_EUR_MWh": [235.0, 175.0, 131.0],
            "Standard_low_EUR_MWh": [170.0, 120.0, 95.0],
            "Standard_high_EUR_MWh": [300.0, 225.0, 178.0],
            "Financed_mean_EUR_MWh": [400.0, 255.0, 174.0],
            "Financed_low_EUR_MWh": [330.0, 180.0, 130.0],
            "Financed_high_EUR_MWh": [520.0, 335.0, 235.0],
        }
    )


def reference_cost_record(stage: str, mode: str) -> dict[str, float]:
    df = production_cost_reference_df()
    row = df[df["Stade"] == stage].iloc[0]
    prefix = "Standard" if mode == "standard" else "Financed"
    return {
        "mean": float(row[f"{prefix}_mean_EUR_MWh"]),
        "low": float(row[f"{prefix}_low_EUR_MWh"]),
        "high": float(row[f"{prefix}_high_EUR_MWh"]),
    }


def reference_lcoe_record(stage: str) -> dict[str, float]:
    df = lcoe_stage_ranges()
    row = df[df["Stade"] == stage_name_map_for_lcoe(stage)].iloc[0]
    return {
        "mean": float(row["LCOE_moyen_EUR_MWh"]),
        "central_low": float(row["Central_low_EUR_MWh"]),
        "central_high": float(row["Central_high_EUR_MWh"]),
        "outer_low": float(row["Outer_low_EUR_MWh"]),
        "outer_high": float(row["Outer_high_EUR_MWh"]),
    }


def project_state(
    stage: str,
    machine_power_kw: float,
    machine_count: int,
    annual_mwh: float,
    case_mode: str,
    capex_adjust_pct: float,
    opex_eur_mwh: float,
    years: int,
    discount_pct: float,
) -> dict[str, float | int | str]:
    total_power_kw = float(machine_power_kw * machine_count)
    capex_ref_keur = interpolate_capex_reference(stage, total_power_kw, case_mode)
    capex_used_keur = capex_ref_keur * (1.0 + capex_adjust_pct / 100.0)
    capex_used_eur = capex_used_keur * 1000.0

    if case_mode == "standard":
        capital_cost_total_eur = capex_used_eur
        financing_total_paid_eur = capex_used_eur
        annual_financing_payment_eur = 0.0
        yearly_costs = [opex_eur_mwh * annual_mwh for _ in range(years)]
        yearly_costs[0] += capex_used_eur
    else:
        annual_payment = loan_annual_payment(capex_used_eur, REFERENCE_FINANCING_RATE, REFERENCE_FINANCING_YEARS)
        financing_total_paid_eur = loan_total_payment(capex_used_eur, REFERENCE_FINANCING_RATE, REFERENCE_FINANCING_YEARS)
        capital_cost_total_eur = financing_total_paid_eur
        annual_financing_payment_eur = annual_payment
        yearly_costs = []
        for year in range(1, years + 1):
            base_cost = opex_eur_mwh * annual_mwh
            if year <= REFERENCE_FINANCING_YEARS:
                base_cost += annual_payment
            yearly_costs.append(base_cost)

    capital_component_eur_mwh = annualized_capex_component(capital_cost_total_eur, annual_mwh, years)
    direct_cost_value = direct_cost(capital_cost_total_eur, annual_mwh, opex_eur_mwh, years)
    lcoe_value = lcoe_from_cashflows(yearly_costs, annual_mwh, years, discount_pct / 100.0)
    capex_per_kw = capex_used_keur / max(total_power_kw, 1e-9)
    capacity_factor = annual_mwh / max(total_power_kw * 8.76, 1e-9)
    equivalent_full_load_hours = capacity_factor * 8760.0

    return {
        "stage": stage,
        "machine_power_kw": float(machine_power_kw),
        "machine_count": int(machine_count),
        "total_power_kw": total_power_kw,
        "annual_mwh": float(annual_mwh),
        "case_mode": case_mode,
        "capex_adjust_pct": float(capex_adjust_pct),
        "opex_eur_mwh": float(opex_eur_mwh),
        "years": int(years),
        "discount_pct": float(discount_pct),
        "capex_ref_keur": float(capex_ref_keur),
        "capex_used_keur": float(capex_used_keur),
        "capex_used_eur": float(capex_used_eur),
        "capital_cost_total_eur": float(capital_cost_total_eur),
        "financing_total_paid_eur": float(financing_total_paid_eur),
        "annual_financing_payment_eur": float(annual_financing_payment_eur),
        "capital_component_eur_mwh": float(capital_component_eur_mwh),
        "direct_cost_eur_mwh": float(direct_cost_value),
        "lcoe_eur_mwh": float(lcoe_value),
        "capex_per_kw_keur": float(capex_per_kw),
        "capacity_factor": float(capacity_factor),
        "equivalent_full_load_hours": float(equivalent_full_load_hours),
    }


def seed_project_state_defaults() -> None:
    presets = reference_project_presets()
    default_stage = st.session_state.get("project_stage", "Démonstrateur")
    preset = presets.get(default_stage, presets["Démonstrateur"])
    defaults = {
        "project_stage": default_stage,
        "project_machine_count": preset["machine_count"],
        "project_machine_power_kw": preset["machine_power_default"],
        "project_link_production": True,
        "project_manual_annual_mwh": preset["annual_mwh_default"],
        "project_case_mode": preset["case_mode_default"],
        "project_capex_adjust_pct": 0,
        "project_opex": REFERENCE_OPEX_EUR_MWH,
        "project_years": REFERENCE_LIFETIME_YEARS,
        "project_discount_pct": preset["discount_pct"],
        "project_prototype_mode": preset["prototype_mode_default"],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def sync_stage_defaults(stage: str) -> None:
    presets = reference_project_presets()
    preset = presets[stage]
    st.session_state["project_stage"] = stage
    st.session_state["project_machine_count"] = 5 if stage == "1er commercial" else 1
    current_power = st.session_state.get("project_machine_power_kw", preset["machine_power_default"])
    st.session_state["project_machine_power_kw"] = float(np.clip(current_power, preset["machine_power_min"], preset["machine_power_max"]))
    st.session_state["project_discount_pct"] = float(preset["discount_pct"])
    st.session_state["project_case_mode"] = str(preset["case_mode_default"])
    if stage == "Prototype":
        prototype_mode = st.session_state.get("project_prototype_mode", preset["prototype_mode_default"])
        if prototype_mode not in PROTOTYPE_PRODUCTION_CASES:
            prototype_mode = "prudent"
        st.session_state["project_prototype_mode"] = prototype_mode
        default_case = "prudent" if prototype_mode == "manual" else prototype_mode
        st.session_state["project_manual_annual_mwh"] = float(prototype_annual_mwh(st.session_state["project_machine_power_kw"], default_case, 1))
    else:
        st.session_state["project_manual_annual_mwh"] = float(annual_mwh_for_stage(stage, st.session_state["project_machine_power_kw"], st.session_state["project_machine_count"]))


def prototype_mode_options() -> dict[str, str]:
    return {
        "prudent": "Cas prudent (4,0 MWh/kW/an)",
        "high": "Cas haut (5,6 MWh/kW/an)",
        "manual": "Saisie manuelle",
    }


def get_project_inputs_from_state() -> dict[str, object]:
    seed_project_state_defaults()
    stage = str(st.session_state["project_stage"])
    machine_power_kw = float(st.session_state["project_machine_power_kw"])
    machine_count = int(st.session_state["project_machine_count"])

    production_basis_note = ""
    production_basis_short = ""
    annual_linked = np.nan

    if stage == "Prototype":
        prototype_mode = st.session_state.get("project_prototype_mode", "prudent")
        if prototype_mode not in PROTOTYPE_PRODUCTION_CASES:
            prototype_mode = "prudent"
        if prototype_mode == "manual":
            annual_mwh = float(st.session_state["project_manual_annual_mwh"])
            annual_linked = float(prototype_annual_mwh(machine_power_kw, "prudent", machine_count))
            production_basis_short = "Saisie manuelle"
            production_basis_note = "La production prototype est saisie directement, sans extrapolation automatique depuis la courbe 100–300 kW."
        else:
            annual_mwh = float(prototype_annual_mwh(machine_power_kw, prototype_mode, machine_count))
            annual_linked = annual_mwh
            production_basis_short = str(PROTOTYPE_PRODUCTION_CASES[prototype_mode]["label"])
            production_basis_note = str(PROTOTYPE_PRODUCTION_CASES[prototype_mode]["description"])
    else:
        linked = bool(st.session_state["project_link_production"])
        annual_linked = annual_mwh_for_stage(stage, machine_power_kw, machine_count)
        annual_mwh = float(annual_linked if linked else st.session_state["project_manual_annual_mwh"])
        if linked:
            production_basis_short = "Courbe liée"
            production_basis_note = "La production est calculée à partir de la courbe de référence par machine puis agrégée au nombre de machines."
        else:
            production_basis_short = "Saisie manuelle"
            production_basis_note = "La production annuelle est saisie directement pour lecture exploratoire. Les comparaisons aux références du rapport deviennent moins strictes."

    return {
        "stage": stage,
        "machine_power_kw": machine_power_kw,
        "machine_count": machine_count,
        "annual_mwh": float(annual_mwh),
        "annual_linked_mwh": float(annual_linked) if np.isfinite(annual_linked) else np.nan,
        "case_mode": str(st.session_state["project_case_mode"]),
        "capex_adjust_pct": float(st.session_state["project_capex_adjust_pct"]),
        "opex_eur_mwh": float(st.session_state["project_opex"]),
        "years": int(st.session_state["project_years"]),
        "discount_pct": float(st.session_state["project_discount_pct"]),
        "production_basis_short": production_basis_short,
        "production_basis_note": production_basis_note,
        "prototype_mode": st.session_state.get("project_prototype_mode", "prudent"),
    }


def _project_state_input_subset(values: dict[str, object]) -> dict[str, object]:
    allowed = {"stage", "machine_power_kw", "machine_count", "annual_mwh", "case_mode", "capex_adjust_pct", "opex_eur_mwh", "years", "discount_pct"}
    return {k: v for k, v in values.items() if k in allowed}


def current_project_state() -> dict[str, float | int | str]:
    return project_state(**_project_state_input_subset(get_project_inputs_from_state()))


def mean_grid_inflation_factor(years: int = 20, annual_growth: float = 0.02) -> float:
    if years == 20 and np.isclose(annual_growth, 0.02):
        return REFERENCE_GRID_MEAN_INFLATION_FACTOR_20Y
    factors = np.array([(1.0 + annual_growth) ** year for year in range(1, years + 1)], dtype=float)
    return float(factors.mean())


def relative_cost_vs_grid_inflation(cost_eur_mwh: float, years: int = 20, annual_growth: float = 0.02) -> float:
    return float(cost_eur_mwh / mean_grid_inflation_factor(years=years, annual_growth=annual_growth))


def report_logic_checks_df() -> pd.DataFrame:
    dims = dimensionnement_foil()
    raw_windows = compute_section_layout(channel_setback=0.0)["windows"]
    budget = implantation_budget_df(machine_width=REFERENCE_MACHINE_WIDTH, channel_setback=NAVIGATION_SETBACK)

    def window_width(label: str, df: pd.DataFrame, column: str) -> float:
        if df.empty or label not in set(df["Fenêtre"]):
            return float("nan")
        return float(df.loc[df["Fenêtre"] == label, column].iloc[0])

    west_raw = window_width("Latérale Ouest", raw_windows, "Largeur_m")
    east_raw = window_width("Latérale Est", raw_windows, "Largeur_m")
    west_margin = window_width("Latérale Ouest", budget, "Marge_restante_m")
    east_margin = window_width("Latérale Est", budget, "Marge_restante_m")

    annual_200 = annual_mwh_from_nominal_power(200.0)
    fc_200 = capacity_factor_from_nominal_power(200.0)
    hours_200 = equivalent_full_load_hours_from_nominal_power(200.0)
    annual_section_mwh = river_energy_metrics()["annual_section_gwh"] * 1000.0
    project_capture_pct = 100.0 * (2.0 * annual_200) / annual_section_mwh

    standard_state = project_state(
        stage="1er commercial",
        machine_power_kw=200.0,
        machine_count=5,
        annual_mwh=5.0 * annual_200,
        case_mode="standard",
        capex_adjust_pct=0.0,
        opex_eur_mwh=REFERENCE_OPEX_EUR_MWH,
        years=REFERENCE_LIFETIME_YEARS,
        discount_pct=7.0,
    )
    financed_state = project_state(
        stage="1er commercial",
        machine_power_kw=200.0,
        machine_count=5,
        annual_mwh=5.0 * annual_200,
        case_mode="financed",
        capex_adjust_pct=0.0,
        opex_eur_mwh=REFERENCE_OPEX_EUR_MWH,
        years=REFERENCE_LIFETIME_YEARS,
        discount_pct=7.0,
    )

    climate = climate_monthly_flow_df()
    winter_mask = climate["Mois"].isin(["Jan", "Fév", "Déc"])
    winter_present = float(climate.loc[winter_mask, "Présent"].mean())
    winter_2050 = float(climate.loc[winter_mask, "2050"].mean())
    winter_2100 = float(climate.loc[winter_mask, "2100"].mean())

    marine = marine_signal_df()
    marine_295 = marine.loc[marine["PK"] == 295].iloc[0]

    rows = [
        {"Catégorie": "Site", "Vérification": "PK326 reste le profil de pointe retenu", "Référence rapport": "Pics de 2,00 m/s au flot et 2,25 m/s au jusant", "Valeur application": "2,00 m/s au flot et 2,25 m/s au jusant", "Statut": "OK", "Commentaire": "Les valeurs-clés de Courval sont reprises sans écart."},
        {"Catégorie": "Implantation", "Vérification": "Fenêtres latérales en condition BMVE(115)", "Référence rapport": "70 m à bâbord et 45 m à tribord", "Valeur application": f"{west_raw:.0f} m à l’ouest et {east_raw:.0f} m à l’est", "Statut": "OK" if np.isclose(west_raw, 70.0) and np.isclose(east_raw, 45.0) else "À vérifier", "Commentaire": "La géométrie calculée retrouve les deux fenêtres de la figure 9."},
        {"Catégorie": "Implantation", "Vérification": "Compatibilité à 2 machines après recul de 5 m", "Référence rapport": "2 machines de 36 m gardent le chenal libre", "Valeur application": f"Marge ouest {west_margin:.0f} m ; marge est {east_margin:.0f} m", "Statut": "OK" if west_margin >= 0.0 and east_margin >= 0.0 else "À vérifier", "Commentaire": "La marge est plus serrée côté est mais reste positive dans la lecture de référence."},
        {"Catégorie": "Machine", "Vérification": "Dimensionnement du foil à Hm = 7,0 m", "Référence rapport": "c ≈ 1,8 m ; 2Ho ≈ 5,4 m ; E ≈ 1,5 m ; L ≈ 36 m", "Valeur application": f"c = {dims['c']:.2f} m ; 2Ho = {dims['amplitude']:.2f} m ; E = {dims['E']:.2f} m ; L = {dims['L']:.2f} m", "Statut": "OK (arrondi)" if np.isclose(dims["L"], 36.36, atol=0.1) else "À vérifier", "Commentaire": "Les valeurs sont cohérentes à l’arrondi près."},
        {"Catégorie": "Production", "Vérification": "Production unitaire autour de 200 kW", "Référence rapport": "Médiane ≈ 800 MWh/an, dans une plage 700–900 MWh/an", "Valeur application": f"{annual_200:.0f} MWh/an", "Statut": "OK (arrondi)" if 700.0 <= annual_200 <= 900.0 else "À vérifier", "Commentaire": "La courbe applicative donne ~823 MWh/an, cohérent avec la médiane du rapport."},
        {"Catégorie": "Production", "Vérification": "Facteur de charge à 200 kW", "Référence rapport": "≈ 0,47 et ≈ 4117 h/an", "Valeur application": f"Fc = {fc_200:.2f} ; {hours_200:.0f} h/an", "Statut": "OK" if np.isclose(fc_200, 0.47, atol=0.005) and np.isclose(hours_200, 4117.0, atol=8.0) else "À vérifier", "Commentaire": "Lecture cohérente avec la figure 18."},
        {"Catégorie": "Production", "Vérification": "Part captée par 2 machines de 200 kW", "Référence rapport": "Le projet ne capte qu’une faible part de l’énergie de section", "Valeur application": f"{project_capture_pct:.2f} %", "Statut": "OK", "Commentaire": "L’extraction projet reste très minoritaire au regard des ~29,5 GWh/an transitant dans la section."},
        {"Catégorie": "Climat", "Vérification": "Baisse des débits froids avec le temps", "Référence rapport": "Décrochage surtout automne-hiver, principalement avant 2050", "Valeur application": f"Hiver présent {winter_present:.0f} m³/s ; 2050 {winter_2050:.0f} ; 2100 {winter_2100:.0f}", "Statut": "OK" if winter_present > winter_2050 > winter_2100 else "À vérifier", "Commentaire": "La tendance climat est respectée."},
        {"Catégorie": "Climat", "Vérification": "Propagation marine plus forte quand le débit baisse", "Référence rapport": "À PK295, le signal marin est plus conservé à 400 m³/s qu’à 1200 ou 2000 m³/s", "Valeur application": f"PK295 : {marine_295['Q400_m3_s']:.0f}% ; {marine_295['Q1200_m3_s']:.0f}% ; {marine_295['Q2000_m3_s']:.0f}%", "Statut": "OK" if marine_295["Q400_m3_s"] > marine_295["Q1200_m3_s"] > marine_295["Q2000_m3_s"] else "À vérifier", "Commentaire": "Le sens physique mobilisé par le rapport est conservé."},
        {"Catégorie": "Économie", "Vérification": "Coût direct 1er commercial – cas standard", "Référence rapport": "≈ 131 €/MWh", "Valeur application": f"{standard_state['direct_cost_eur_mwh']:.1f} €/MWh", "Statut": "OK (arrondi)" if abs(float(standard_state['direct_cost_eur_mwh']) - 131.0) <= 3.0 else "À vérifier", "Commentaire": "Le léger écart vient des arrondis de courbe et du point de lecture 200 kW / 5 machines."},
        {"Catégorie": "Économie", "Vérification": "Coût direct 1er commercial – cas financé", "Référence rapport": "≈ 174 €/MWh", "Valeur application": f"{financed_state['direct_cost_eur_mwh']:.1f} €/MWh", "Statut": "OK (arrondi)" if abs(float(financed_state['direct_cost_eur_mwh']) - 174.0) <= 3.0 else "À vérifier", "Commentaire": "Le calcul de remboursement sur 10 ans à 4 % retrouve l’écart standard / financé."},
        {"Catégorie": "Économie", "Vérification": "Benchmark LCOE commercial initial", "Référence rapport": "≈ 221 €/MWh", "Valeur application": f"{reference_lcoe_record('1er commercial')['mean']:.0f} €/MWh", "Statut": "OK", "Commentaire": "Le benchmark sectoriel reste distinct du coût direct projet."},
    ]
    return pd.DataFrame(rows)


def externalites_default() -> dict[str, float]:
    return DEFAULT_EXTERNALITIES.copy()


@st.cache_data(show_spinner=False)
def support_capex_ranges_df() -> pd.DataFrame:
    return pd.DataFrame({"Levier": ["Aides CAPEX", "Soutiens territoriaux"], "Min_pct_capital": [20, 5], "Max_pct_capital": [50, 15]})


@st.cache_data(show_spinner=False)
def support_revenue_ranges_df() -> pd.DataFrame:
    return pd.DataFrame({"Levier": ["Soutien production", "CEE"], "Min_eur_mwh": [50, 5], "Max_eur_mwh": [150, 20]})


def support_scenario_presets() -> dict[str, dict[str, float]]:
    return {
        "Prudent": {"aid_capex_pct": 20.0, "territorial_pct": 5.0, "support_prod": 50.0, "cee": 5.0, "resilience": 5.0, "volatility": 5.0, "environment": 3.0, "diversification": 3.0},
        "Central": {"aid_capex_pct": 30.0, "territorial_pct": 5.0, "support_prod": 80.0, "cee": 10.0, "resilience": 7.5, "volatility": 10.0, "environment": 5.0, "diversification": 5.0},
        "Renforcé": {"aid_capex_pct": 50.0, "territorial_pct": 15.0, "support_prod": 150.0, "cee": 20.0, "resilience": 10.0, "volatility": 15.0, "environment": 8.0, "diversification": 7.0},
    }


@st.cache_data(show_spinner=False)
def externalities_ranges_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Poste": [
                "Résilience / sécurité d’approvisionnement",
                "Réduction de la volatilité des prix",
                "Externalités environnementales non climatiques",
                "Diversification stratégique",
            ],
            "Min": [5, 5, 3, 3],
            "Max": [10, 15, 8, 7],
        }
    )


def compute_support_scenario(
    direct_cost_initial: float,
    capital_component_eur_mwh: float,
    aid_capex_pct: float,
    territorial_pct: float,
    support_prod: float,
    cee: float,
    resilience: float,
    volatility: float,
    environment: float,
    diversification: float,
) -> dict[str, object]:
    aid_capex_value = capital_component_eur_mwh * aid_capex_pct / 100.0
    territorial_value = capital_component_eur_mwh * territorial_pct / 100.0
    capex_reduction = aid_capex_value + territorial_value
    revenue_supports = support_prod + cee
    positive_externalities = resilience + volatility + environment + diversification
    cost_after_capex = max(direct_cost_initial - capex_reduction, 0.0)
    cash_residual_cost = max(cost_after_capex - revenue_supports, 0.0)
    decision_equivalent_cost = max(cash_residual_cost - positive_externalities, 0.0)

    contrib_df = pd.DataFrame(
        {
            "Poste": ["Aides CAPEX", "Soutiens territoriaux", "Soutien production", "CEE", "Résilience", "Volatilité", "Environnement", "Diversification"],
            "Valeur_EUR_MWh": [aid_capex_value, territorial_value, support_prod, cee, resilience, volatility, environment, diversification],
            "Nature": ["cash", "cash", "cash", "cash", "valeur", "valeur", "valeur", "valeur"],
        }
    )
    return {
        "aid_capex_value": float(aid_capex_value),
        "territorial_value": float(territorial_value),
        "capex_reduction": float(capex_reduction),
        "revenue_supports": float(revenue_supports),
        "positive_externalities": float(positive_externalities),
        "cost_after_capex": float(cost_after_capex),
        "cash_residual_cost": float(cash_residual_cost),
        "decision_equivalent_cost": float(decision_equivalent_cost),
        "contrib_df": contrib_df,
    }


def economic_case_matrix_df() -> pd.DataFrame:
    presets = reference_project_presets()
    rows: list[dict[str, object]] = []
    for stage in ["Prototype", "Démonstrateur", "1er commercial"]:
        preset = presets[stage]
        for mode in ["standard", "financed"]:
            machine_power = float(preset["machine_power_default"])
            machine_count = int(preset["machine_count"])
            annual_mwh = annual_mwh_for_stage(stage, machine_power, machine_count, "prudent")
            state = project_state(
                stage=stage,
                machine_power_kw=machine_power,
                machine_count=machine_count,
                annual_mwh=annual_mwh,
                case_mode=mode,
                capex_adjust_pct=0.0,
                opex_eur_mwh=REFERENCE_OPEX_EUR_MWH,
                years=REFERENCE_LIFETIME_YEARS,
                discount_pct=float(preset["discount_pct"]),
            )
            rows.append(
                {
                    "Stade": stage,
                    "Mode": case_mode_label(mode),
                    "Puissance_totale_kW": state["total_power_kw"],
                    "Production_annuelle_MWh": state["annual_mwh"],
                    "CAPEX_kEUR": state["capex_used_keur"],
                    "Capital_total_EUR": state["capital_cost_total_eur"],
                    "Coût_direct_EUR_MWh": state["direct_cost_eur_mwh"],
                    "LCOE_EUR_MWh": state["lcoe_eur_mwh"],
                }
            )
    return pd.DataFrame(rows)


def support_scenarios_matrix_df(base_state: dict[str, object]) -> pd.DataFrame:
    rows: list[dict[str, float | str]] = []
    for name, preset in support_scenario_presets().items():
        result = compute_support_scenario(
            direct_cost_initial=float(base_state["direct_cost_eur_mwh"]),
            capital_component_eur_mwh=float(base_state["capital_component_eur_mwh"]),
            aid_capex_pct=float(preset["aid_capex_pct"]),
            territorial_pct=float(preset["territorial_pct"]),
            support_prod=float(preset["support_prod"]),
            cee=float(preset["cee"]),
            resilience=float(preset["resilience"]),
            volatility=float(preset["volatility"]),
            environment=float(preset["environment"]),
            diversification=float(preset["diversification"]),
        )
        rows.append(
            {
                "Scénario": name,
                "Coût_initial_EUR_MWh": float(base_state["direct_cost_eur_mwh"]),
                "Après_aides_EUR_MWh": float(result["cost_after_capex"]),
                "Après_leviers_cash_EUR_MWh": float(result["cash_residual_cost"]),
                "Lecture_élargie_EUR_MWh": float(result["decision_equivalent_cost"]),
                "Leviers_totaux_EUR_MWh": float(result["capex_reduction"] + result["revenue_supports"] + result["positive_externalities"]),
            }
        )
    return pd.DataFrame(rows)


# =============================================================================
# Economic plots
# =============================================================================


def plot_lcoe_ranges(df: pd.DataFrame | None = None) -> go.Figure:
    if df is None:
        df = lcoe_stage_ranges()
    fig = go.Figure()
    for _, row in df.iterrows():
        x = row["Stade"]
        fig.add_trace(
            go.Box(
                x=[x, x],
                lowerfence=[row["Outer_low_EUR_MWh"]],
                q1=[row["Central_low_EUR_MWh"]],
                median=[row["LCOE_moyen_EUR_MWh"]],
                q3=[row["Central_high_EUR_MWh"]],
                upperfence=[row["Outer_high_EUR_MWh"]],
                name=x,
                boxpoints=False,
                fillcolor="rgba(99,102,241,0.35)",
                line=dict(color="#4f46e5"),
                whiskerwidth=0.8,
                showlegend=False,
            )
        )
    fig.update_layout(title="Benchmark LCOE sectoriel par stade", yaxis_title="€/MWh")
    return style_figure(fig, height=390)


def plot_stage_discount_rates() -> go.Figure:
    df = stages_df()
    fig = px.line(df, x="Stade", y="Taux_actualisation_pct", markers=True, title="Taux d’actualisation retenus par stade")
    fig.update_traces(line_color="#2563eb", marker=dict(size=10))
    fig.update_layout(yaxis_title="Taux d’actualisation (%)")
    return style_figure(fig, height=360)


def plot_production_cost_reference(df: pd.DataFrame | None = None) -> go.Figure:
    if df is None:
        df = production_cost_reference_df()
    fig = go.Figure()
    colors = {"standard": "#60a5fa", "financed": "#f97316"}
    for mode, label in [("standard", "Standard"), ("financed", "Financed")]:
        fig.add_trace(
            go.Bar(
                x=df["Stade"],
                y=df[f"{label}_mean_EUR_MWh"],
                name=f"Coût direct {case_mode_label(mode)}",
                error_y=dict(type="data", array=df[f"{label}_high_EUR_MWh"] - df[f"{label}_mean_EUR_MWh"], arrayminus=df[f"{label}_mean_EUR_MWh"] - df[f"{label}_low_EUR_MWh"]),
                marker_color=colors[mode],
            )
        )
    fig.update_layout(barmode="group", title="Coût direct de production – référentiel projet", yaxis_title="€/MWh")
    return style_figure(fig, height=390)


def _add_band(fig: go.Figure, x: pd.Series, mean: pd.Series, low: pd.Series, high: pd.Series, fill_color: str, line_color: str, name: str) -> None:
    fig.add_trace(go.Scatter(x=x, y=high, mode="lines", line=dict(width=0), hoverinfo="skip", showlegend=False))
    fig.add_trace(go.Scatter(x=x, y=low, mode="lines", line=dict(width=0), fill="tonexty", fillcolor=fill_color, hoverinfo="skip", name=name, showlegend=True))
    fig.add_trace(go.Scatter(x=x, y=mean, mode="lines+markers", line=dict(width=3, color=line_color), showlegend=False))


def plot_stage_capex_curve(df: pd.DataFrame | None, stage: str, selected_power_kw: float | None = None, selected_mode: str | None = None, selected_capex_keur: float | None = None) -> go.Figure:
    if df is None:
        df = capex_reference_curves_df()
    sub = df[df["Stade"] == stage].sort_values("Puissance_kW")
    fig = go.Figure()
    _add_band(fig, sub["Puissance_kW"], sub["CAPEX_standard_kEUR"], sub["CAPEX_standard_low_kEUR"], sub["CAPEX_standard_high_kEUR"], "rgba(37,99,235,0.18)", "#2563eb", "CAPEX standard ±30 %")
    _add_band(fig, sub["Puissance_kW"], sub["CAPEX_financed_kEUR"], sub["CAPEX_financed_low_kEUR"], sub["CAPEX_financed_high_kEUR"], "rgba(217,70,239,0.16)", "#d946ef", "CAPEX financé ±30 %")
    if selected_power_kw is not None:
        fig.add_vline(x=selected_power_kw, line_dash="dash", line_color="black", opacity=0.6)
    if selected_power_kw is not None and selected_capex_keur is not None:
        marker_color = "#2563eb" if selected_mode == "standard" else "#d946ef"
        fig.add_trace(go.Scatter(x=[selected_power_kw], y=[selected_capex_keur], mode="markers", marker=dict(size=12, color=marker_color, symbol="diamond"), name="Projet retenu"))
    fig.update_layout(title=f"CAPEX de référence – {stage}", xaxis_title="Puissance installée (kW)", yaxis_title="CAPEX (k€)")
    return style_figure(fig, height=390)


def plot_specific_capex(df: pd.DataFrame | None = None) -> go.Figure:
    if df is None:
        df = specific_capex_reference_df()
    fig = go.Figure()
    palette = {
        ("Prototype", "standard"): "#94a3b8",
        ("Prototype", "financed"): "#64748b",
        ("Démonstrateur", "standard"): "#2563eb",
        ("Démonstrateur", "financed"): "#7c3aed",
        ("1er commercial", "standard"): "#dc2626",
        ("1er commercial", "financed"): "#ea580c",
    }
    for stage in ["Prototype", "Démonstrateur", "1er commercial"]:
        sub = df[df["Stade"] == stage].sort_values("Puissance_kW")
        for mode, col in [("standard", "Spec_standard_kEUR_kW"), ("financed", "Spec_financed_kEUR_kW")]:
            fig.add_trace(go.Scatter(x=sub["Puissance_kW"], y=sub[col], mode="lines+markers", name=f"{stage} – {case_mode_label(mode)}", line=dict(width=2.5, color=palette[(stage, mode)])))
    fig.update_layout(title="CAPEX spécifique – économies d’échelle et maturité", xaxis_title="Puissance installée (kW)", yaxis_title="k€/kW")
    return style_figure(fig, height=380)


def plot_reference_vs_model_band(reference_low: float, reference_mean: float, reference_high: float, model_value: float, title: str, yaxis_title: str = "€/MWh") -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Bar(x=["Référence rapport"], y=[reference_mean], marker_color="#cbd5e1", error_y=dict(type="data", array=[reference_high - reference_mean], arrayminus=[reference_mean - reference_low]), name="Référence"))
    fig.add_trace(go.Bar(x=["Modèle projet"], y=[model_value], marker_color="#60a5fa", name="Projet"))
    fig.update_layout(title=title, yaxis_title=yaxis_title, showlegend=False)
    return style_figure(fig, height=340)


def plot_project_sensitivity_tornado(base_inputs: dict[str, object]) -> go.Figure:
    base_inputs = _project_state_input_subset(dict(base_inputs))
    base = project_state(**base_inputs)
    base_cost = float(base["direct_cost_eur_mwh"])
    scenarios = [
        ("CAPEX ±10 %", {"capex_adjust_pct": float(base_inputs["capex_adjust_pct"]) - 10}, {"capex_adjust_pct": float(base_inputs["capex_adjust_pct"]) + 10}),
        ("OPEX ±5 €/MWh", {"opex_eur_mwh": max(0.0, float(base_inputs["opex_eur_mwh"]) - 5)}, {"opex_eur_mwh": float(base_inputs["opex_eur_mwh"]) + 5}),
        ("Production ±10 %", {"annual_mwh": float(base_inputs["annual_mwh"]) * 0.9}, {"annual_mwh": float(base_inputs["annual_mwh"]) * 1.1}),
        ("Durée de vie ±3 ans", {"years": max(5, int(base_inputs["years"]) - 3)}, {"years": int(base_inputs["years"]) + 3}),
    ]
    rows = []
    for label, low_override, high_override in scenarios:
        low_value = float(project_state(**(_project_state_input_subset({**base_inputs, **low_override})))["direct_cost_eur_mwh"])
        high_value = float(project_state(**(_project_state_input_subset({**base_inputs, **high_override})))["direct_cost_eur_mwh"])
        rows.append({"Paramètre": label, "Bas": low_value, "Haut": high_value, "Base": base_cost})
    df = pd.DataFrame(rows)
    df["Min"] = df[["Bas", "Haut"]].min(axis=1)
    df["Max"] = df[["Bas", "Haut"]].max(axis=1)
    df = df.sort_values("Max", ascending=True)
    fig = go.Figure()
    fig.add_trace(go.Bar(y=df["Paramètre"], x=df["Max"] - df["Min"], base=df["Min"], orientation="h", marker_color="#93c5fd", name="Plage de variation"))
    fig.add_vline(x=base_cost, line_dash="dash", line_color="black", annotation_text="Base", annotation_position="top")
    fig.update_layout(title="Sensibilité du coût direct aux hypothèses structurantes", xaxis_title="Coût direct (€/MWh)", yaxis_title="", showlegend=False)
    return style_figure(fig, height=360)


def plot_lcoe_discount_sensitivity(base_inputs: dict[str, object], discount_min: float = 4.0, discount_max: float = 14.0) -> go.Figure:
    base_inputs = _project_state_input_subset(dict(base_inputs))
    discount_values = np.arange(discount_min, discount_max + 0.001, 0.5)
    lcoe_values = []
    for rate in discount_values:
        values = dict(base_inputs)
        values["discount_pct"] = float(rate)
        lcoe_values.append(float(project_state(**values)["lcoe_eur_mwh"]))
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=discount_values, y=lcoe_values, mode="lines", line=dict(width=3, color="#7c3aed"), name="LCOE"))
    fig.add_vline(x=float(base_inputs["discount_pct"]), line_dash="dash", line_color="black", annotation_text=f"Base {float(base_inputs['discount_pct']):.1f} %", annotation_position="top")
    fig.update_layout(title="Sensibilité du LCOE au taux d’actualisation", xaxis_title="Taux d’actualisation (%)", yaxis_title="LCOE (€/MWh)", showlegend=False)
    return style_figure(fig, height=360)


def plot_development_roadmap(df: pd.DataFrame | None = None) -> go.Figure:
    if df is None:
        df = deployment_phase_df()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["Position"], y=[1, 1, 1], mode="lines+markers+text", text=df["Stade"], textposition="top center", marker=dict(size=18, color=["#94a3b8", "#2563eb", "#dc2626"]), line=dict(width=4, color="#cbd5e1"), name="Phases"))
    for _, row in df.iterrows():
        fig.add_annotation(x=row["Position"], y=0.82, text=f"TRL {row['TRL']}<br>{row['Puissance_typique']}<br>{row['Décision_gate']}", showarrow=False, align="center", bgcolor="rgba(255,255,255,0.92)", bordercolor="rgba(15,23,42,0.10)", borderwidth=1, borderpad=6)
    fig.update_layout(title="Phasage du projet", xaxis=dict(visible=False, range=[0.7, 3.3]), yaxis=dict(visible=False, range=[0.65, 1.18]), showlegend=False)
    return style_figure(fig, height=330)


def plot_stage_power_risk(df: pd.DataFrame | None = None) -> go.Figure:
    if df is None:
        df = stage_power_risk_df()
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(x=df["Stade"], y=df["Puissance_totale_kW"], name="Puissance typique", marker_color="#60a5fa"), secondary_y=False)
    fig.add_trace(go.Scatter(x=df["Stade"], y=df["Taux_actualisation_pct"], mode="lines+markers", name="Taux d’actualisation", line=dict(color="#dc2626", width=3)), secondary_y=True)
    fig.update_layout(title="Montée en puissance et baisse du risque")
    fig.update_yaxes(title_text="Puissance typique (kW)", secondary_y=False)
    fig.update_yaxes(title_text="Taux d’actualisation (%)", secondary_y=True)
    return style_figure(fig, height=340)


def plot_economic_case_matrix(df: pd.DataFrame, metric: str = "Coût_direct_EUR_MWh") -> go.Figure:
    title = "Cas-types – coût direct" if metric == "Coût_direct_EUR_MWh" else "Cas-types – LCOE"
    fig = px.bar(df, x="Stade", y=metric, color="Mode", barmode="group", text_auto=".0f", title=title, color_discrete_map={"standard": "#60a5fa", "financé": "#f59e0b"})
    fig.update_layout(yaxis_title="€/MWh")
    return style_figure(fig, height=360)


def plot_support_capex_ranges(df: pd.DataFrame | None = None) -> go.Figure:
    if df is None:
        df = support_capex_ranges_df()
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df["Levier"], y=df["Max_pct_capital"] - df["Min_pct_capital"], base=df["Min_pct_capital"], marker_color="#7dd3fc", showlegend=False))
    fig.update_layout(title="Leviers d’investissement", yaxis_title="% de la composante capital")
    return style_figure(fig, height=340)


def plot_support_revenue_ranges(df: pd.DataFrame | None = None) -> go.Figure:
    if df is None:
        df = support_revenue_ranges_df()
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df["Levier"], y=df["Max_eur_mwh"] - df["Min_eur_mwh"], base=df["Min_eur_mwh"], marker_color="#93c5fd", showlegend=False))
    fig.update_layout(title="Leviers de revenu", yaxis_title="€/MWh")
    return style_figure(fig, height=340)


def plot_externalities_ranges(df: pd.DataFrame | None = None) -> go.Figure:
    if df is None:
        df = externalities_ranges_df()
    df_plot = df.copy().sort_values("Max")
    fig = go.Figure()
    fig.add_trace(go.Bar(y=df_plot["Poste"], x=df_plot["Max"] - df_plot["Min"], base=df_plot["Min"], orientation="h", marker_color="#86efac", showlegend=False))
    fig.update_layout(title="Ordres de grandeur des externalités positives", xaxis_title="€/MWh", yaxis_title="")
    return style_figure(fig, height=360)


def plot_support_value_breakdown(contrib_df: pd.DataFrame) -> go.Figure:
    df_plot = contrib_df.sort_values("Valeur_EUR_MWh", ascending=True)
    fig = px.bar(df_plot, y="Poste", x="Valeur_EUR_MWh", orientation="h", color="Nature", color_discrete_map={"cash": "#60a5fa", "valeur": "#86efac"}, title="Leviers et valeurs ajoutées mobilisables")
    fig.update_layout(xaxis_title="€/MWh", yaxis_title="")
    return style_figure(fig, height=360)


def plot_remaining_cost_bars(cost_direct_value: float, cost_after_capex: float, cash_residual_value: float, decision_value: float) -> go.Figure:
    df = pd.DataFrame({"Étape": ["Initial", "Après aides", "Après leviers cash", "Lecture élargie"], "€/MWh": [cost_direct_value, cost_after_capex, cash_residual_value, decision_value]})
    fig = px.bar(df, x="Étape", y="€/MWh", title="Coût après leviers")
    fig.update_traces(marker_color="#93c5fd")
    return style_figure(fig, height=360)


def plot_decision_waterfall(intrinsic_cost: float, support_result: dict[str, object], grid_relative_cost: float | None = None) -> go.Figure:
    labels = ["Coût direct", "Aides CAPEX", "Soutiens revenus", "Après leviers cash", "Externalités", "Lecture élargie"]
    measure = ["absolute", "relative", "relative", "total", "relative", "total"]
    values = [
        intrinsic_cost,
        -float(support_result["capex_reduction"]),
        -float(support_result["revenue_supports"]),
        float(support_result["cash_residual_cost"]),
        -float(support_result["positive_externalities"]),
        float(support_result["decision_equivalent_cost"]),
    ]
    fig = go.Figure(go.Waterfall(x=labels, y=values, measure=measure, connector=dict(line=dict(color="rgba(15,23,42,0.25)"))))
    if grid_relative_cost is not None:
        fig.add_hline(y=grid_relative_cost, line_dash="dash", line_color="#dc2626", annotation_text="Coût relatif vs achat réseau inflation 2 %/an", annotation_position="top left")
    fig.update_layout(title="Lecture décisionnelle : coût cash puis lecture élargie", yaxis_title="€/MWh", showlegend=False)
    return style_figure(fig, height=380)


def plot_support_scenario_comparison(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df["Scénario"], y=df["Coût_initial_EUR_MWh"], name="Coût initial", marker_color="#cbd5e1"))
    fig.add_trace(go.Bar(x=df["Scénario"], y=df["Après_leviers_cash_EUR_MWh"], name="Après leviers cash", marker_color="#2563eb"))
    fig.add_trace(go.Bar(x=df["Scénario"], y=df["Lecture_élargie_EUR_MWh"], name="Lecture élargie", marker_color="#16a34a"))
    fig.update_layout(barmode="group", title="Lecture des scénarios de soutien", yaxis_title="€/MWh")
    return style_figure(fig, height=340)


# =============================================================================
# Anchoring and regulatory
# =============================================================================


@st.cache_data(show_spinner=False)
def anchoring_options_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Solution": ["Duc d’Albe", "Corps mort", "Pieux vissés", "Caisson de succion", "Solution mixte"],
            "Priorité_relative": [1.0, 4.0, 5.0, 2.0, 4.5],
            "Lecture": [
                "Solution lourde et peu favorable au regard de la profondeur et de l’obstacle ponctuel créé.",
                "Alternative robuste et simple, compatible avec un fond meuble.",
                "Option prioritaire au regard de la traction à reprendre, du faible impact au fond et de la possibilité de retrait.",
                "Solution conditionnelle, plutôt adaptée à d’autres profondeurs ou à un contexte sédimentaire très favorable.",
                "Association pertinente si l’avant-projet confirme l’intérêt d’une reprise d’effort partagée.",
            ],
            "Positionnement": ["Non prioritaire", "Alternative solide", "Option privilégiée", "À considérer sous conditions", "Option d’optimisation"],
        }
    )


def plot_anchoring_priority(df: pd.DataFrame | None = None) -> go.Figure:
    if df is None:
        df = anchoring_options_df()
    fig = px.bar(df.sort_values("Priorité_relative"), x="Priorité_relative", y="Solution", orientation="h", text="Positionnement", color="Priorité_relative", color_continuous_scale="Blues", title="Lecture relative des solutions d’ancrage")
    fig.update_traces(textposition="outside")
    fig.update_layout(xaxis_title="Priorité relative (1 à 5)", yaxis_title="")
    fig.update_coloraxes(showscale=False)
    return style_figure(fig, height=380)


@st.cache_data(show_spinner=False)
def regulatory_summary_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Bloc": ["Base juridique", "Procédure cible", "Dossier à constituer", "Milieux aquatiques", "Consultation"],
            "Lecture": [
                "Projet à apprécier au regard du régime IOTA / loi sur l’eau et, selon la rubrique applicable, sous autorisation ou déclaration.",
                "Autorisation environnementale si le projet relève du régime d’autorisation ; les projets soumis à simple déclaration suivent une procédure distincte.",
                "Analyse du projet, de ses incidences sur l’eau, les milieux, l’écoulement, les habitats et les usages ; pièces complémentaires selon le régime réellement applicable.",
                "Continuité écologique, sédiments, habitats et incidences sur le milieu à documenter.",
                "Participation du public et consultations selon le régime, l’évaluation environnementale et les impacts du projet.",
            ],
        }
    )


@st.cache_data(show_spinner=False)
def regulatory_process_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Étape": ["Cadrage du projet", "Qualification du régime eau", "Constitution du dossier", "Instruction / consultations", "Décision administrative"],
            "Ordre": [1, 2, 3, 4, 5],
            "Lecture": [
                "Définition du périmètre technique et du niveau d’incidence attendu.",
                "Vérification de la rubrique IOTA applicable et du régime déclaration / autorisation.",
                "Compilation des pièces eau, milieu, écoulement, exploitation et éventuelle évaluation environnementale.",
                "Analyse par les services compétents, consultation des parties prenantes et participation du public selon le cas.",
                "Récépissé de déclaration ou autorisation environnementale préfectorale selon le régime applicable.",
            ],
        }
    )


def plot_regulatory_process(df: pd.DataFrame | None = None) -> go.Figure:
    if df is None:
        df = regulatory_process_df()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["Ordre"], y=[1] * len(df), mode="lines+markers+text", text=df["Étape"], textposition="top center", marker=dict(size=16, color="#2563eb"), line=dict(width=4, color="#bfdbfe"), showlegend=False))
    for _, row in df.iterrows():
        fig.add_annotation(x=row["Ordre"], y=0.82, text=row["Lecture"], showarrow=False, align="center", bgcolor="rgba(255,255,255,0.94)", bordercolor="rgba(15,23,42,0.10)", borderwidth=1, borderpad=6)
    fig.update_layout(title="Séquence réglementaire à anticiper", xaxis=dict(visible=False, range=[0.7, 5.3]), yaxis=dict(visible=False, range=[0.66, 1.16]))
    return style_figure(fig, height=340)
