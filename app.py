#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import ccxt
import yfinance as yf
import pandas as pd
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Tuple

import numpy as np
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, time
import pytz
import json
import os
from typing import Dict, Tuple, List
import streamlit as st

# ====================== CONFIGURATION ======================
CONFIG_DIR = "config"
ASSETS_FILE = os.path.join(CONFIG_DIR, "assets.json")
SETTINGS_FILE = os.path.join(CONFIG_DIR, "settings.json")

# Fuseau horaire du Congo (GMT+1)
CONGO_TZ = pytz.timezone("Africa/Brazzaville")

DEFAULT_ASSETS = {
    "crypto": ["BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT"],
    "stocks": ["AAPL", "TSLA", "NVDA", "SPY"],
    "forex": ["EUR/USD", "GBP/USD", "USD/JPY"]
    "Equities": ["AAPL", "MSFT", "NVDA", "NESN.SW", "MC.PA"],
    "Indices": ["SPX", "NDX", "STOXX50E", "FTSE"],
    "Rates": ["US10Y", "US2Y", "DE10Y", "FR10Y"],
    "Credit": ["US HY OAS", "US IG OAS", "EMBI"],
    "FX": ["EUR/USD", "USD/JPY", "GBP/USD", "USD/CHF"],
    "Commodities": ["WTI", "Brent", "Gold", "Copper"],
    "Crypto": ["BTC", "ETH", "SOL", "XRP"],
}

DEFAULT_SETTINGS = {
    "theme": "dark",
    "timeframes": ["15m", "1h", "4h", "1d"],
    "default_timeframe": "4h",
    "trading_sessions": {
        "London": {"start": "07:00", "end": "16:00"},
        "New York": {"start": "13:00", "end": "22:00"}
    "default_horizon": "Moyen terme",
    "palette": {
        "background": "#0B0F14",
        "panel": "#111824",
        "panel_alt": "#0F172A",
        "text": "#E2E8F0",
        "muted": "#94A3B8",
        "accent": "#38BDF8",
        "accent_alt": "#22C55E",
        "danger": "#F97316",
        "border": "#1F2A37",
    },
    "risk_per_trade": 0.01,
    "candle_colors": {
        "bullish": "#34C759",  # Vert iOS
        "bearish": "#FF3B30"   # Rouge iOS
    "macro_weights": {
        "growth": 0.2,
        "inflation": 0.2,
        "rates": 0.2,
        "liquidity": 0.15,
        "geopolitics": 0.15,
        "flows": 0.1,
    },
    "ios_colors": {
        "primary": "#007AFF",   # Bleu iOS
        "secondary": "#5856D6", # Violet iOS
        "background": "#F2F2F7", # Gris clair iOS
        "card": "#FFFFFF",      # Blanc iOS
        "text": "#1C1C1E",      # Noir iOS
        "border": "#C6C6C8"     # Gris bordure iOS
    }
}

# ====================== CORE CLASSES ======================
class ICTAnalyzer:
    """Analyseur complet des concepts ICT"""
    def __init__(self, settings: Dict):
        self.settings = settings
        self.congo_tz = pytz.timezone("Africa/Brazzaville")
    
    # ... (keep all other methods unchanged) ...

class TradingDashboard:
    """Interface utilisateur de l'assistant de trading"""
    def __init__(self):
        self._init_data()
        self._setup_ui()
    
    def _init_data(self):
        """Initialise les données et configurations"""
        os.makedirs(CONFIG_DIR, exist_ok=True)
        
        # Crée assets.json si inexistant
        if not os.path.exists(ASSETS_FILE):
            with open(ASSETS_FILE, 'w') as f:
                json.dump(DEFAULT_ASSETS, f, indent=4)
        
        # Crée settings.json si inexistant
        if not os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'w') as f:
                json.dump(DEFAULT_SETTINGS, f, indent=4)
        
        # Charge les assets et settings
        with open(ASSETS_FILE, 'r') as f:
            self.assets = json.load(f)
        
        with open(SETTINGS_FILE, 'r') as f:
            raw_settings = json.load(f)
            self.settings = raw_settings
            
        self.data_fetcher = DataFetcher()
        self.ict_analyzer = ICTAnalyzer(self.settings)
    
    def _setup_ui(self):
        """Configure l'interface utilisateur avec style iOS"""
        st.set_page_config(
            layout="wide", 
            page_title="ICT Trading Assistant Pro",
            page_icon="📊"
        )
        
        self._apply_ios_style()
        self._setup_sidebar()
        
        st.title("📊 Assistant de Trading ICT - Analyse Pré-Marché")
        
        if hasattr(st.session_state, 'analyze_clicked') and st.session_state.analyze_clicked:
            self._perform_analysis()
        else:
            self._display_welcome_screen()
    
    def _apply_ios_style(self):
        """Applique le style iOS"""
        ios_colors = self.settings['ios_colors']
        
        st.markdown(f"""

@dataclass
class MacroSnapshot:
    gdp_growth: float
    inflation: float
    unemployment: float
    policy_rate: float
    cb_balance_sheet: float
    capital_flows: float
    geopolitical_risk: float


@dataclass
class FundamentalsSnapshot:
    revenue_growth: float
    ebit_margin: float
    roe: float
    net_debt_ebitda: float
    current_ratio: float
    valuation: float
    moat_score: float
    management_score: float
    sector_position: float


@dataclass
class MarketSnapshot:
    curve_slope: float
    credit_spread: float
    real_rates: float
    equity_vol: float
    cross_asset_corr: float
    rotation_score: float


# ====================== DATA HELPERS ======================

def _merge_defaults(current: Dict, default: Dict) -> Dict:
    merged = dict(current)
    for key, value in default.items():
        if key not in merged:
            merged[key] = value
        elif isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _merge_defaults(merged[key], value)
    return merged


def _load_json(path: str, default: Dict) -> Dict:
    os.makedirs(CONFIG_DIR, exist_ok=True)
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(default, handle, indent=4)
        return default
    with open(path, "r", encoding="utf-8") as handle:
        current = json.load(handle)
    merged = _merge_defaults(current, default)
    if merged != current:
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(merged, handle, indent=4)
    return merged


# ====================== ANALYTICS ======================

def _normalize(score: float, min_val: float = 0, max_val: float = 100) -> float:
    return max(min((score - min_val) / (max_val - min_val), 1), 0)


def assess_cycle(snapshot: MacroSnapshot) -> Tuple[str, float]:
    growth_score = _normalize(snapshot.gdp_growth, -2, 5)
    inflation_score = 1 - _normalize(snapshot.inflation, 0, 8)
    rates_score = 1 - _normalize(snapshot.policy_rate, 0, 6)
    liquidity_score = _normalize(snapshot.cb_balance_sheet, -5, 5)
    risk_score = 1 - _normalize(snapshot.geopolitical_risk, 0, 10)
    flows_score = _normalize(snapshot.capital_flows, -5, 5)

    composite = (
        growth_score * 0.25
        + inflation_score * 0.2
        + rates_score * 0.2
        + liquidity_score * 0.15
        + risk_score * 0.1
        + flows_score * 0.1
    )

    if composite >= 0.7:
        regime = "Expansion disciplinée"
    elif composite >= 0.55:
        regime = "Fin de cycle / Pic"
    elif composite >= 0.4:
        regime = "Décélération contrôlée"
    else:
        regime = "Récession / Stress"
    return regime, composite


def assess_fundamentals(snapshot: FundamentalsSnapshot) -> Tuple[str, str, float]:
    profitability = _normalize(snapshot.ebit_margin, 5, 40)
    growth = _normalize(snapshot.revenue_growth, -5, 20)
    quality = _normalize(snapshot.roe, 5, 30)
    leverage = 1 - _normalize(snapshot.net_debt_ebitda, 0, 4)
    liquidity = _normalize(snapshot.current_ratio, 0.8, 2.5)
    valuation = 1 - _normalize(snapshot.valuation, 8, 28)
    moat = _normalize(snapshot.moat_score, 1, 5)
    management = _normalize(snapshot.management_score, 1, 5)
    sector = _normalize(snapshot.sector_position, 1, 5)

    score = (
        profitability * 0.15
        + growth * 0.15
        + quality * 0.15
        + leverage * 0.1
        + liquidity * 0.1
        + valuation * 0.15
        + moat * 0.1
        + management * 0.05
        + sector * 0.05
    )

    if score >= 0.8:
        rating = "AAA"
        decision = "Accumuler"
    elif score >= 0.65:
        rating = "AA"
        decision = "Conserver"
    elif score >= 0.5:
        rating = "A"
        decision = "Réduire"
    elif score >= 0.35:
        rating = "BBB"
        decision = "Réduire"
    else:
        rating = "C/D"
        decision = "Short"

    return rating, decision, score


def assess_market(snapshot: MarketSnapshot) -> Tuple[str, float]:
    curve = _normalize(snapshot.curve_slope, -2, 2)
    spreads = 1 - _normalize(snapshot.credit_spread, 150, 600)
    real_rates = 1 - _normalize(snapshot.real_rates, -1, 3)
    vol = 1 - _normalize(snapshot.equity_vol, 10, 40)
    corr = 1 - _normalize(snapshot.cross_asset_corr, 0.2, 0.9)
    rotation = _normalize(snapshot.rotation_score, 1, 5)

    risk_score = (
        curve * 0.2
        + spreads * 0.2
        + real_rates * 0.15
        + vol * 0.15
        + corr * 0.15
        + rotation * 0.15
    )

    posture = "Risk-On contrôlé" if risk_score >= 0.6 else "Risk-Off défensif"
    return posture, risk_score


def build_allocation(risk_score: float, cycle_score: float) -> Dict[str, float]:
    base = {
        "Actions": 0.35,
        "Taux": 0.25,
        "Crédit": 0.15,
        "Matières premières": 0.1,
        "FX": 0.1,
        "Alternatifs": 0.05,
    }
    tilt = (risk_score - 0.5) * 0.2 + (cycle_score - 0.5) * 0.15
    base["Actions"] = max(min(base["Actions"] + tilt, 0.5), 0.2)
    base["Taux"] = max(min(base["Taux"] - tilt, 0.4), 0.15)
    base["Crédit"] = max(min(base["Crédit"] + tilt / 2, 0.25), 0.1)
    residual = 1 - sum(base.values())
    base["Alternatifs"] = max(base["Alternatifs"] + residual, 0.03)
    return base


def build_scenarios(score: float) -> pd.DataFrame:
    central = max(min(0.5 + (score - 0.5) * 0.2, 0.65), 0.35)
    upside = max(min(0.25 + (score - 0.5) * 0.1, 0.35), 0.15)
    downside = 1 - central - upside
    scenarios = pd.DataFrame(
        {
            "Scénario": ["Central", "Haussier", "Baissier"],
            "Probabilité": [central, upside, downside],
            "Narratif": [
                "Alignement macro-fondamental cohérent, risque contenu.",
                "Catalyseur positif, compression des primes de risque.",
                "Choc exogène, resserrement financier agressif.",
            ],
        }
    )
    return scenarios


# ====================== UI ======================


def apply_theme(settings: Dict) -> None:
    palette = settings["palette"]
    st.set_page_config(
        layout="wide",
        page_title="Institutional Fundamental Engine",
        page_icon="🧭",
    )
    st.markdown(
        f"""
        <style>
        :root {{
            --primary: {ios_colors['primary']};
            --secondary: {ios_colors['secondary']};
            --background: {ios_colors['background']};
            --card-bg: {ios_colors['card']};
            --text: {ios_colors['text']};
            --border: {ios_colors['border']};
            --bg: {palette['background']};
            --panel: {palette['panel']};
            --panel-alt: {palette['panel_alt']};
            --text: {palette['text']};
            --muted: {palette['muted']};
            --accent: {palette['accent']};
            --accent-alt: {palette['accent_alt']};
            --danger: {palette['danger']};
            --border: {palette['border']};
        }}
        
        body {{
            background-color: var(--background);
            background-color: var(--bg);
            color: var(--text);
        }}
        
        .main {{
            background-color: var(--background);
            background-color: var(--bg);
            color: var(--text);
            font-family: -apple-system, BlinkMacSystemFont, sans-serif;
        }}
        
        .sidebar .sidebar-content {{
            background-color: var(--card-bg);
            border-right: 1px solid var(--border);
        h1, h2, h3, h4 {{
            color: var(--text);
            font-family: "Inter", "SF Pro Display", sans-serif;
        }}
        
        .stButton>button {{
            background-color: var(--primary);
            border: none;
            color: white;
        .stTextInput > div > div > input,
        .stSelectbox > div > div,
        .stSlider > div {{
            background-color: var(--panel);
            color: var(--text);
            border-radius: 10px;
            padding: 10px 24px;
            font-weight: 500;
            font-size: 16px;
        }}
        
        .stAlert {{
            background-color: var(--card-bg);
            border-radius: 14px;
            border: 1px solid var(--border);
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        
        .stTextInput>div>div>input {{
        .stButton > button {{
            background-color: var(--accent);
            color: #081018;
            border-radius: 10px;
            border: 1px solid var(--border);
            border: none;
            font-weight: 600;
        }}
        
        .stSelectbox>div>div {{
            border-radius: 10px;
        .panel {{
            background: var(--panel);
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 16px;
            margin-bottom: 16px;
        }}
        
        .css-1aumxhk {{
            color: var(--text) !important;
        }}
        
        /* Cards style */
        .custom-card {{
            background-color: var(--card-bg);
            border-radius: 12px;
            padding: 15px;
            margin-bottom: 15px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        .panel-alt {{
            background: var(--panel-alt);
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 16px;
            margin-bottom: 16px;
        }}
        .tag {{
            display: inline-block;
            padding: 4px 10px;
            border-radius: 999px;
            background: rgba(56, 189, 248, 0.15);
            color: var(--accent);
            font-size: 12px;
            letter-spacing: 0.6px;
            text-transform: uppercase;
        }}
        
        /* Section headers */
        .section-header {{
            font-size: 20px;
        .metric {{
            font-size: 22px;
            font-weight: 600;
            margin-bottom: 15px;
            color: var(--text);
        }}
        .muted {{
            color: var(--muted);
        }}
        </style>
        """, unsafe_allow_html=True)
    
    def _setup_sidebar(self):
        """Configure la barre latérale avec style iOS"""
        with st.sidebar:
            st.image("https://i.imgur.com/JQ6wB2n.png", width=120)
            st.title("Configuration")
            
            # Sélection de l'actif
            self.asset_category = st.selectbox(
                "Catégorie d'actif",
                list(self.assets.keys()),
                key="asset_category"
            )
            
            self.selected_symbol = st.selectbox(
                "Actif",
                self.assets[self.asset_category],
                key="asset_select"
        """,
        unsafe_allow_html=True,
    )


def sidebar_controls(assets: Dict, settings: Dict) -> Dict:
    with st.sidebar:
        st.markdown("## 🧭 Comité d'investissement")
        asset_class = st.selectbox("Univers", list(assets.keys()))
        asset = st.selectbox("Actif ciblé", assets[asset_class])
        horizon = st.selectbox(
            "Horizon",
            ["Court terme", "Moyen terme", "Long terme"],
            index=["Court terme", "Moyen terme", "Long terme"].index(
                settings["default_horizon"]
            ),
        )
        risk_budget = st.slider("Budget de risque (vol annualisée)", 5, 25, 12)
        conviction = st.slider("Conviction fondamentale", 1, 5, 3)
        st.markdown("---")
        st.markdown("### Paramètres macro pondérés")
        macro_weights = settings["macro_weights"]
        w_growth = st.slider("Croissance", 0.05, 0.3, macro_weights["growth"], 0.05)
        w_infl = st.slider("Inflation", 0.05, 0.3, macro_weights["inflation"], 0.05)
        w_rates = st.slider("Taux", 0.05, 0.3, macro_weights["rates"], 0.05)
        w_liq = st.slider("Liquidité", 0.05, 0.25, macro_weights["liquidity"], 0.05)
        w_geo = st.slider("Géopolitique", 0.05, 0.25, macro_weights["geopolitics"], 0.05)
        w_flows = st.slider("Flux", 0.05, 0.2, macro_weights["flows"], 0.05)
        total = w_growth + w_infl + w_rates + w_liq + w_geo + w_flows
        if total != 0:
            normalized = {
                "growth": w_growth / total,
                "inflation": w_infl / total,
                "rates": w_rates / total,
                "liquidity": w_liq / total,
                "geopolitics": w_geo / total,
                "flows": w_flows / total,
            }
        else:
            normalized = macro_weights

    return {
        "asset_class": asset_class,
        "asset": asset,
        "horizon": horizon,
        "risk_budget": risk_budget,
        "conviction": conviction,
        "macro_weights": normalized,
    }


def macro_inputs() -> MacroSnapshot:
    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    st.markdown("<span class='tag'>Macro</span>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        gdp = st.slider("Croissance PIB (%)", -2.0, 6.0, 2.2, 0.1)
        inflation = st.slider("Inflation (%)", 0.0, 10.0, 3.4, 0.1)
        unemployment = st.slider("Chômage (%)", 2.0, 12.0, 4.5, 0.1)
    with col2:
        policy = st.slider("Taux directeur (%)", 0.0, 7.0, 4.75, 0.05)
        balance = st.slider("Bilan BC (variation %)", -5.0, 5.0, -0.8, 0.1)
        flows = st.slider("Flux de capitaux (z-score)", -5.0, 5.0, 0.4, 0.1)
    with col3:
        geopolitics = st.slider("Risque géopolitique (0-10)", 0.0, 10.0, 6.2, 0.1)
        st.markdown(
            f"<p class='muted'>Heure Congo: {datetime.now(CONGO_TZ).strftime('%H:%M')}</p>",
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)
    return MacroSnapshot(
        gdp_growth=gdp,
        inflation=inflation,
        unemployment=unemployment,
        policy_rate=policy,
        cb_balance_sheet=balance,
        capital_flows=flows,
        geopolitical_risk=geopolitics,
    )


def fundamentals_inputs() -> FundamentalsSnapshot:
    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    st.markdown("<span class='tag'>Fondamentaux</span>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        rev = st.slider("Croissance CA (%)", -5.0, 30.0, 8.0, 0.5)
        margin = st.slider("Marge EBIT (%)", 5.0, 45.0, 22.0, 0.5)
        roe = st.slider("ROE (%)", 5.0, 35.0, 18.0, 0.5)
    with col2:
        leverage = st.slider("Dette nette / EBITDA", 0.0, 5.0, 1.4, 0.1)
        liquidity = st.slider("Current ratio", 0.6, 3.0, 1.6, 0.1)
        valuation = st.slider("PER / EV-EBITDA", 8.0, 35.0, 18.0, 0.5)
    with col3:
        moat = st.slider("Moat (1-5)", 1.0, 5.0, 4.0, 0.1)
        management = st.slider("Management (1-5)", 1.0, 5.0, 3.8, 0.1)
        sector = st.slider("Position sectorielle (1-5)", 1.0, 5.0, 3.5, 0.1)
    st.markdown("</div>", unsafe_allow_html=True)
    return FundamentalsSnapshot(
        revenue_growth=rev,
        ebit_margin=margin,
        roe=roe,
        net_debt_ebitda=leverage,
        current_ratio=liquidity,
        valuation=valuation,
        moat_score=moat,
        management_score=management,
        sector_position=sector,
    )


def market_inputs() -> MarketSnapshot:
    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    st.markdown("<span class='tag'>Marchés</span>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        curve = st.slider("Pente courbe (10Y-2Y)", -2.0, 2.0, -0.4, 0.1)
        spreads = st.slider("Spread crédit (pb)", 150, 650, 320, 10)
    with col2:
        real_rates = st.slider("Taux réels (%)", -1.0, 4.0, 1.2, 0.1)
        vol = st.slider("Volatilité actions (%)", 10.0, 45.0, 19.0, 0.5)
    with col3:
        corr = st.slider("Corrélation cross-asset", 0.2, 0.9, 0.55, 0.05)
        rotation = st.slider("Rotation sectorielle (1-5)", 1.0, 5.0, 3.0, 0.1)
    st.markdown("</div>", unsafe_allow_html=True)
    return MarketSnapshot(
        curve_slope=curve,
        credit_spread=spreads,
        real_rates=real_rates,
        equity_vol=vol,
        cross_asset_corr=corr,
        rotation_score=rotation,
    )


def allocation_chart(weights: Dict[str, float]) -> go.Figure:
    labels = list(weights.keys())
    values = [round(v * 100, 2) for v in weights.values()]
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.55)])
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=10, b=10),
        font=dict(color="#E2E8F0"),
        showlegend=True,
    )
    return fig


def scenario_chart(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure(
        data=[
            go.Bar(
                x=df["Scénario"],
                y=df["Probabilité"] * 100,
                marker_color=["#38BDF8", "#22C55E", "#F97316"],
            )
            
            # Sélection du timeframe
            self.selected_timeframe = st.selectbox(
                "Intervalle",
                self.settings['timeframes'],
                index=self.settings['timeframes'].index(
                    self.settings['default_timeframe']
                )
        ]
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=20, b=10),
        yaxis_title="Probabilité (%)",
        font=dict(color="#E2E8F0"),
    )
    return fig


def main() -> None:
    assets = _load_json(ASSETS_FILE, DEFAULT_ASSETS)
    settings = _load_json(SETTINGS_FILE, DEFAULT_SETTINGS)

    apply_theme(settings)
    controls = sidebar_controls(assets, settings)

    st.title("Analyse Fondamentale & Gestion d'Actifs")
    st.markdown(
        "Institutional-grade allocation engine. Piloté comme un comité d'investissement."
    )

    macro_snapshot = macro_inputs()
    fundamentals_snapshot = fundamentals_inputs()
    market_snapshot = market_inputs()

    cycle_regime, cycle_score = assess_cycle(macro_snapshot)
    rating, decision, fundamental_score = assess_fundamentals(fundamentals_snapshot)
    market_posture, risk_score = assess_market(market_snapshot)

    allocation = build_allocation(risk_score, cycle_score)
    scenarios = build_scenarios((fundamental_score + risk_score) / 2)

    st.markdown("<div class='panel-alt'>", unsafe_allow_html=True)
    st.markdown("<span class='tag'>Synthèse</span>", unsafe_allow_html=True)
    cols = st.columns(4)
    cols[0].markdown(
        f"<div class='metric'>{cycle_regime}</div><div class='muted'>Cycle global</div>",
        unsafe_allow_html=True,
    )
    cols[1].markdown(
        f"<div class='metric'>{market_posture}</div><div class='muted'>Posture risque</div>",
        unsafe_allow_html=True,
    )
    cols[2].markdown(
        f"<div class='metric'>{rating}</div><div class='muted'>Notation interne</div>",
        unsafe_allow_html=True,
    )
    cols[3].markdown(
        f"<div class='metric'>{decision}</div><div class='muted'>Décision</div>",
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    col_left, col_right = st.columns([1.1, 0.9])

    with col_left:
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.markdown("<span class='tag'>Thèse d'investissement</span>", unsafe_allow_html=True)
        st.write(
            f"**Actif**: {controls['asset']} ({controls['asset_class']})  \
**Horizon**: {controls['horizon']}  \
**Budget de risque**: {controls['risk_budget']}% vol  \
**Conviction**: {controls['conviction']}/5"
        )
        st.markdown(
            "**Thèse structurée**  \n"
            "- Priorité à la préservation du capital, exposition calibrée par le cycle et les spreads.  \n"
            "- Les fondamentaux restent filtrés par la qualité, la liquidité du bilan et la valorisation relative.  \n"
            "- Risque principal : choc macro et resserrement supplémentaire des conditions financières."
        )
        st.markdown(
            "**Catalyseurs suivis**  \n"
            "- Surprise de croissance / inflation.  \n"
            "- Réallocation des flux internationaux.  \n"
            "- Révision des bénéfices et guidance sectorielle."
        )
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.markdown("<span class='tag'>Scénarios</span>", unsafe_allow_html=True)
        st.plotly_chart(scenario_chart(scenarios), width="stretch")
        for _, row in scenarios.iterrows():
            st.markdown(
                f"**{row['Scénario']} ({row['Probabilité']*100:.1f}%)** — {row['Narratif']}"
            )
            
            # Bouton d'analyse avec style iOS
            if st.button("🔍 Analyser le Marché", key="analyze_btn"):
                st.session_state.analyze_clicked = True
                st.rerun()
            
            st.markdown("---")
            
            # Heures de trading
            st.subheader("🕒 Sessions de Trading")
            
            # Afficher les heures des sessions de trading en temps Congo
            london_start = self.settings['trading_sessions']['London']['start']
            london_end = self.settings['trading_sessions']['London']['end']
            ny_start = self.settings['trading_sessions']['New York']['start']
            ny_end = self.settings['trading_sessions']['New York']['end']
            
            st.markdown(f"""
            <div class="custom-card">
                <p><strong>Londres</strong>: {london_start}-{london_end}</p>
                <p><strong>New York</strong>: {ny_start}-{ny_end}</p>
                <p><strong>Heure Congo</strong>: {datetime.now(CONGO_TZ).strftime("%H:%M")}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Gestion des actifs
            with st.expander("📋 Gérer les actifs"):
                new_asset = st.text_input("Ajouter un nouvel actif")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("➕ Ajouter") and new_asset:
                        if self.asset_category not in self.assets:
                            self.assets[self.asset_category] = []
                        self.assets[self.asset_category].append(new_asset)
                        self._save_assets()
                        st.success(f"Actif {new_asset} ajouté !")
                with col2:
                    if st.button("🗑️ Supprimer"):
                        if self.selected_symbol in self.assets[self.asset_category]:
                            self.assets[self.asset_category].remove(self.selected_symbol)
                            self._save_assets()
                            st.success(f"Actif {self.selected_symbol} supprimé !")
                            st.rerun()
    
    def _create_ios_card(self, title: str, content: str):
        """Crée une carte avec style iOS"""
        return f"""
        <div class="custom-card">
            <h3 style="margin: 0 0 10px 0; color: var(--primary);">{title}</h3>
            <p style="margin: 0; color: var(--text); white-space: pre-wrap;">{content}</p>
        </div>
        """
    
    def _display_pre_market_analysis(self, analysis: Dict):
        """Affiche l'analyse pré-marché avec style iOS"""
        st.subheader("🔍 Analyse Pré-Marché ICT")
        
        cols = st.columns(4)
        
        # Hauts/Bas égaux
        with cols[0]:
            eh_val = analysis['equal_highs_lows']['equal_highs']
            el_val = analysis['equal_highs_lows']['equal_lows']
            
            eh_text = f"Haut: {eh_val:.2f}" if eh_val is not None else "N/A"
            el_text = f"Bas: {el_val:.2f}" if el_val is not None else "N/A"
            
            st.markdown(self._create_ios_card(
                "📏 Hauts et bas égaux",
                f"{'✅ Détecté' if analysis['equal_highs_lows']['is_equal_high'] or analysis['equal_highs_lows']['is_equal_low'] else '❌ Non détecté'}\n{eh_text}\n{el_text}"
            ), unsafe_allow_html=True)
        
        # ... (rest of the methods remain similar but use _create_ios_card) ...

# ... (keep DataFetcher class and main execution unchanged) ...
        st.markdown("</div>", unsafe_allow_html=True)

    with col_right:
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.markdown("<span class='tag'>Allocation</span>", unsafe_allow_html=True)
        st.plotly_chart(allocation_chart(allocation), width="stretch")
        allocation_table = pd.DataFrame(
            {"Classe": allocation.keys(), "Poids": [f"{v*100:.1f}%" for v in allocation.values()]}
        )
        st.dataframe(allocation_table, hide_index=True, width="stretch")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.markdown("<span class='tag'>Lecture hedge fund</span>", unsafe_allow_html=True)
        st.markdown(
            "- Détection d'inefficiences via dispersion des multiples et compression des spreads.  \n"
            "- Asymétrie recherchée : convexité positive et catalyseur à horizon court.  \n"
            "- Arbitrage relatif privilégié lorsque corrélation > 0.6."
        )
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='panel-alt'>", unsafe_allow_html=True)
    st.markdown("<span class='tag'>Tableau de décision</span>", unsafe_allow_html=True)
    decision_matrix = pd.DataFrame(
        {
            "Pilier": [
                "Macro global",
                "Fondamentaux",
                "Marchés",
                "Gestion du risque",
                "Catalyseurs",
            ],
            "Lecture": [
                cycle_regime,
                f"Score {fundamental_score:.2f} | {rating}",
                market_posture,
                f"Budget {controls['risk_budget']}% vol",
                "Positionnement surveillé",
            ],
            "Impact": [
                "Allocation",
                "Sélection",
                "Timing",
                "Taille de position",
                "Couverture",
            ],
        }
    )
    st.dataframe(decision_matrix, hide_index=True, width="stretch")
    st.markdown("</div>", unsafe_allow_html=True)

    st.info(
        "Cette application fournit un cadre d'analyse institutionnelle. Les paramètres sont à ajuster "
        "par un comité d'investissement et validés par la gestion des risques."
    )


if __name__ == "__main__":
    main()
