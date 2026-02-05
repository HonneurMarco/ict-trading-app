 #!/usr/bin/env python3
 # -*- coding: utf-8 -*-
 
-import ccxt
-import yfinance as yf
+import hashlib
+from dataclasses import dataclass
+from typing import Dict, List
+
 import pandas as pd
-import numpy as np
-import streamlit as st
 import plotly.graph_objects as go
-from datetime import datetime, time
-import pytz
-import json
-import os
-from typing import Dict, Tuple, List
-
-# ====================== CONFIGURATION ======================
-CONFIG_DIR = "config"
-ASSETS_FILE = os.path.join(CONFIG_DIR, "assets.json")
-SETTINGS_FILE = os.path.join(CONFIG_DIR, "settings.json")
-
-# Fuseau horaire du Congo (GMT+1)
-CONGO_TZ = pytz.timezone("Africa/Brazzaville")
-
-DEFAULT_ASSETS = {
-    "crypto": ["BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT"],
-    "stocks": ["AAPL", "TSLA", "NVDA", "SPY"],
-    "forex": ["EUR/USD", "GBP/USD", "USD/JPY"]
+import streamlit as st
+
+
+ASSET_UNIVERSE = {
+    "Actions": ["AAPL", "MSFT", "NVDA", "TSLA", "LVMH.PA"],
+    "Indices": ["SPX", "NDX", "EUROSTOXX50", "NIKKEI225"],
+    "Obligations": ["US10Y", "US2Y", "BUND10Y", "OAT10Y"],
+    "Devises": ["EUR/USD", "USD/JPY", "GBP/USD", "USD/CNH"],
+    "Matières premières": ["Brent", "WTI", "Gold", "Copper"],
+    "Crypto": ["BTC", "ETH", "SOL", "XRP"],
 }
 
-DEFAULT_SETTINGS = {
-    "theme": "dark",
-    "timeframes": ["15m", "1h", "4h", "1d"],
-    "default_timeframe": "4h",
-    "trading_sessions": {
-        "London": {"start": "07:00", "end": "16:00"},
-        "New York": {"start": "13:00", "end": "22:00"}
-    },
-    "risk_per_trade": 0.01,
-    "candle_colors": {
-        "bullish": "#34C759",  # Vert iOS
-        "bearish": "#FF3B30"   # Rouge iOS
-    },
-    "ios_colors": {
-        "primary": "#007AFF",   # Bleu iOS
-        "secondary": "#5856D6", # Violet iOS
-        "background": "#F2F2F7", # Gris clair iOS
-        "card": "#FFFFFF",      # Blanc iOS
-        "text": "#1C1C1E",      # Noir iOS
-        "border": "#C6C6C8"     # Gris bordure iOS
-    }
+THEME = {
+    "bg": "#0B0F1A",
+    "panel": "#111827",
+    "panel_alt": "#0F172A",
+    "text": "#E5E7EB",
+    "muted": "#9CA3AF",
+    "accent": "#3B82F6",
+    "accent_alt": "#6366F1",
+    "positive": "#10B981",
+    "negative": "#EF4444",
+    "warning": "#F59E0B",
 }
 
-# ====================== CORE CLASSES ======================
-class ICTAnalyzer:
-    """Analyseur complet des concepts ICT"""
-    def __init__(self, settings: Dict):
-        self.settings = settings
-        self.congo_tz = pytz.timezone("Africa/Brazzaville")
-    
-    # ... (keep all other methods unchanged) ...
-
-class TradingDashboard:
-    """Interface utilisateur de l'assistant de trading"""
-    def __init__(self):
-        self._init_data()
-        self._setup_ui()
-    
-    def _init_data(self):
-        """Initialise les données et configurations"""
-        os.makedirs(CONFIG_DIR, exist_ok=True)
-        
-        # Crée assets.json si inexistant
-        if not os.path.exists(ASSETS_FILE):
-            with open(ASSETS_FILE, 'w') as f:
-                json.dump(DEFAULT_ASSETS, f, indent=4)
-        
-        # Crée settings.json si inexistant
-        if not os.path.exists(SETTINGS_FILE):
-            with open(SETTINGS_FILE, 'w') as f:
-                json.dump(DEFAULT_SETTINGS, f, indent=4)
-        
-        # Charge les assets et settings
-        with open(ASSETS_FILE, 'r') as f:
-            self.assets = json.load(f)
-        
-        with open(SETTINGS_FILE, 'r') as f:
-            raw_settings = json.load(f)
-            self.settings = raw_settings
-            
-        self.data_fetcher = DataFetcher()
-        self.ict_analyzer = ICTAnalyzer(self.settings)
-    
-    def _setup_ui(self):
-        """Configure l'interface utilisateur avec style iOS"""
-        st.set_page_config(
-            layout="wide", 
-            page_title="ICT Trading Assistant Pro",
-            page_icon="📊"
-        )
-        
-        self._apply_ios_style()
-        self._setup_sidebar()
-        
-        st.title("📊 Assistant de Trading ICT - Analyse Pré-Marché")
-        
-        if hasattr(st.session_state, 'analyze_clicked') and st.session_state.analyze_clicked:
-            self._perform_analysis()
-        else:
-            self._display_welcome_screen()
-    
-    def _apply_ios_style(self):
-        """Applique le style iOS"""
-        ios_colors = self.settings['ios_colors']
-        
-        st.markdown(f"""
+
+@dataclass
+class MacroFactor:
+    label: str
+    signal: str
+    weight: float
+    score: int
+
+
+@dataclass
+class Scenario:
+    name: str
+    probability: float
+    narrative: str
+
+
+@dataclass
+class ThesisBlock:
+    title: str
+    content: str
+
+
+def _stable_seed(text: str) -> int:
+    digest = hashlib.md5(text.encode("utf-8")).hexdigest()[:8]
+    return int(digest, 16)
+
+
+def _score_to_rating(score: int) -> str:
+    if score >= 85:
+        return "AAA"
+    if score >= 75:
+        return "AA"
+    if score >= 65:
+        return "A"
+    if score >= 55:
+        return "BBB"
+    if score >= 45:
+        return "BB"
+    if score >= 35:
+        return "B"
+    return "D"
+
+
+def _score_to_decision(score: int) -> str:
+    if score >= 75:
+        return "Accumuler"
+    if score >= 60:
+        return "Conserver"
+    if score >= 45:
+        return "Réduire"
+    return "Short"
+
+
+def _make_macro_factors(seed: int) -> List[MacroFactor]:
+    base_scores = [70, 64, 59, 61, 56, 67]
+    labels = [
+        "Cycle économique",
+        "Politique monétaire",
+        "Inflation",
+        "Croissance PIB",
+        "Flux de capitaux",
+        "Risque géopolitique",
+    ]
+    signals = [
+        "Expansion tardive",
+        "Restrictive mais prévisible",
+        "Désinflation graduelle",
+        "Croissance sous tendance",
+        "Flux sélectifs",
+        "Tensions régionales persistantes",
+    ]
+    weights = [0.2, 0.2, 0.15, 0.15, 0.15, 0.15]
+
+    adjustment = (seed % 11) - 5
+    factors = []
+    for label, signal, weight, base in zip(labels, signals, weights, base_scores):
+        score = max(35, min(90, base + adjustment))
+        factors.append(MacroFactor(label, signal, weight, score))
+    return factors
+
+
+def _weighted_score(factors: List[MacroFactor]) -> int:
+    return int(sum(f.weight * f.score for f in factors))
+
+
+def _fundamental_metrics(seed: int) -> Dict[str, str]:
+    adj = (seed % 9) - 4
+    roe = 17.5 + adj
+    margin = 22.5 + (adj // 2)
+    leverage = 1.4 + (adj / 20)
+    growth = 7.5 + (adj / 2)
+    valuation = 21 + adj
+    fcf = 12 + (adj / 3)
+    return {
+        "ROE": f"{roe:.1f}%",
+        "Marge opérationnelle": f"{margin:.1f}%",
+        "FCF yield": f"{fcf:.1f}%",
+        "Levier net": f"{leverage:.2f}x",
+        "Croissance CA 3a": f"{growth:.1f}%",
+        "EV/EBITDA": f"{valuation:.1f}x",
+    }
+
+
+def _market_signals(seed: int) -> Dict[str, str]:
+    adj = (seed % 7) - 3
+    curve = 12 + adj
+    credit = 135 + adj * 5
+    corr = 0.55 + adj * 0.02
+    vol = 18 + adj
+    return {
+        "Pente de courbe": f"{curve:.1f} pb",
+        "Spread crédit": f"{credit} pb",
+        "Corrélation cross-asset": f"{corr:.2f}",
+        "Volatilité implicite": f"{vol:.1f}%",
+        "Régime": "Risk-on sélectif",
+    }
+
+
+def _portfolio_metrics(seed: int) -> Dict[str, str]:
+    adj = (seed % 5) - 2
+    sharpe = 1.05 + adj * 0.1
+    sortino = 1.35 + adj * 0.12
+    drawdown = 8.5 + adj
+    diversification = 0.6 + adj * 0.02
+    liquidity = 2.4 + adj * 0.1
+    return {
+        "Sharpe": f"{sharpe:.2f}",
+        "Sortino": f"{sortino:.2f}",
+        "Max drawdown": f"-{drawdown:.1f}%",
+        "Diversification effective": f"{diversification:.2f}",
+        "Budget liquidité": f"{liquidity:.2f}x",
+    }
+
+
+def _hedge_signals(seed: int) -> Dict[str, str]:
+    adj = (seed % 6) - 3
+    asym = 1.3 + adj * 0.1
+    catalyst = "Résultats + guidance" if seed % 2 == 0 else "Macro surprise + positioning"
+    stress = "Moderate" if seed % 3 == 0 else "Elevated"
+    return {
+        "Asymétrie rendement/risque": f"{asym:.2f}",
+        "Inefficiences détectées": "Dispersion + microstructure",
+        "Catalyseur": catalyst,
+        "Stress de liquidité": stress,
+    }
+
+
+def _scenarios(seed: int) -> List[Scenario]:
+    base = seed % 10
+    central = 55 + (base - 5)
+    bull = 25 - (base - 5) // 2
+    bear = 100 - central - bull
+    return [
+        Scenario("Scénario central", central, "Normalisation progressive et croissance modérée."),
+        Scenario("Scénario haussier", bull, "Désinflation rapide et regain d'appétit au risque."),
+        Scenario("Scénario baissier", bear, "Choc de liquidité et stress de crédit."),
+    ]
+
+
+def _thesis_blocks(seed: int) -> List[ThesisBlock]:
+    risk_focus = "corrélations élevées" if seed % 2 == 0 else "fragilité du crédit"
+    return [
+        ThesisBlock(
+            "Thèse d'investissement",
+            "Prime de qualité justifiée par la résilience cash-flow et le pricing power.",
+        ),
+        ThesisBlock(
+            "Risques prioritaires",
+            f"Durcissement financier, {risk_focus}, liquidité asymétrique.",
+        ),
+        ThesisBlock(
+            "Catalyseurs",
+            "Normalisation macro, re-rating sélectif, rotation vers actifs défensifs.",
+        ),
+    ]
+
+
+def _layout_style() -> None:
+    st.set_page_config(page_title="Institutional Fundamental Command", layout="wide")
+    st.markdown(
+        f"""
         <style>
-        :root {{
-            --primary: {ios_colors['primary']};
-            --secondary: {ios_colors['secondary']};
-            --background: {ios_colors['background']};
-            --card-bg: {ios_colors['card']};
-            --text: {ios_colors['text']};
-            --border: {ios_colors['border']};
+        body, .stApp {{
+            background-color: {THEME['bg']};
+            color: {THEME['text']};
+            font-family: "Inter", "Segoe UI", sans-serif;
         }}
-        
-        body {{
-            background-color: var(--background);
+        .block-container {{
+            padding-top: 2rem;
         }}
-        
-        .main {{
-            background-color: var(--background);
-            color: var(--text);
-            font-family: -apple-system, BlinkMacSystemFont, sans-serif;
+        .panel {{
+            background: {THEME['panel']};
+            border: 1px solid #1F2937;
+            border-radius: 16px;
+            padding: 16px;
+            margin-bottom: 16px;
         }}
-        
-        .sidebar .sidebar-content {{
-            background-color: var(--card-bg);
-            border-right: 1px solid var(--border);
+        .panel h3 {{
+            margin: 0 0 10px 0;
+            color: {THEME['text']};
         }}
-        
-        .stButton>button {{
-            background-color: var(--primary);
-            border: none;
-            color: white;
+        .metric-pill {{
+            background: {THEME['panel_alt']};
             border-radius: 10px;
-            padding: 10px 24px;
-            font-weight: 500;
-            font-size: 16px;
+            padding: 12px;
+            border: 1px solid #1F2937;
         }}
-        
-        .stAlert {{
-            background-color: var(--card-bg);
-            border-radius: 14px;
-            border: 1px solid var(--border);
-            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
+        .muted {{
+            color: {THEME['muted']};
         }}
-        
-        .stTextInput>div>div>input {{
-            border-radius: 10px;
-            border: 1px solid var(--border);
-        }}
-        
-        .stSelectbox>div>div {{
-            border-radius: 10px;
-            border: 1px solid var(--border);
-        }}
-        
-        .css-1aumxhk {{
-            color: var(--text) !important;
+        .decision {{
+            font-size: 20px;
+            font-weight: 700;
         }}
-        
-        /* Cards style */
-        .custom-card {{
-            background-color: var(--card-bg);
-            border-radius: 12px;
-            padding: 15px;
-            margin-bottom: 15px;
-            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
-            border: 1px solid var(--border);
+        .rating {{
+            font-size: 24px;
+            font-weight: 700;
         }}
-        
-        /* Section headers */
-        .section-header {{
-            font-size: 20px;
-            font-weight: 600;
-            margin-bottom: 15px;
-            color: var(--text);
+        .sidebar .sidebar-content {{
+            background-color: {THEME['panel']};
         }}
         </style>
-        """, unsafe_allow_html=True)
-    
-    def _setup_sidebar(self):
-        """Configure la barre latérale avec style iOS"""
-        with st.sidebar:
-            st.image("https://i.imgur.com/JQ6wB2n.png", width=120)
-            st.title("Configuration")
-            
-            # Sélection de l'actif
-            self.asset_category = st.selectbox(
-                "Catégorie d'actif",
-                list(self.assets.keys()),
-                key="asset_category"
+        """,
+        unsafe_allow_html=True,
+    )
+
+
+def _metric_grid(metrics: Dict[str, str]) -> None:
+    cols = st.columns(len(metrics))
+    for col, (label, value) in zip(cols, metrics.items()):
+        with col:
+            st.markdown(
+                f"""
+                <div class="metric-pill">
+                    <div class="muted" style="font-size:12px;">{label}</div>
+                    <div style="font-size:18px; font-weight:600;">{value}</div>
+                </div>
+                """,
+                unsafe_allow_html=True,
+            )
+
+
+def _header_kpis(composite_score: int, rating: str, decision: str, horizon: str) -> None:
+    kpi_cols = st.columns(4)
+    kpi_data = [
+        ("Score composite", f"{composite_score}/100"),
+        ("Notation interne", rating),
+        ("Décision", decision),
+        ("Horizon", horizon),
+    ]
+    for col, (label, value) in zip(kpi_cols, kpi_data):
+        with col:
+            st.markdown(
+                f"""
+                <div class="panel">
+                    <div class="muted" style="font-size:12px;">{label}</div>
+                    <div style="font-size:22px; font-weight:700;">{value}</div>
+                </div>
+                """,
+                unsafe_allow_html=True,
             )
-            
-            self.selected_symbol = st.selectbox(
-                "Actif",
-                self.assets[self.asset_category],
-                key="asset_select"
+
+
+def _macro_tab(macro_factors: List[MacroFactor], macro_score: int) -> None:
+    st.markdown("<div class='panel'><h3>Analyse macroéconomique globale</h3></div>", unsafe_allow_html=True)
+    macro_df = pd.DataFrame(
+        {
+            "Facteur": [f.label for f in macro_factors],
+            "Signal": [f.signal for f in macro_factors],
+            "Poids": [f.weight for f in macro_factors],
+            "Score": [f.score for f in macro_factors],
+        }
+    )
+    st.dataframe(macro_df, width="stretch")
+    fig = go.Figure(
+        data=[
+            go.Bar(
+                x=macro_df["Facteur"],
+                y=macro_df["Score"],
+                marker_color=THEME["accent"],
+            )
+        ]
+    )
+    fig.update_layout(
+        height=320,
+        plot_bgcolor=THEME["panel"],
+        paper_bgcolor=THEME["panel"],
+        font_color=THEME["text"],
+        yaxis=dict(range=[0, 100]),
+    )
+    st.plotly_chart(fig, width="stretch")
+    st.markdown(
+        f"<div class='panel'><div class='muted'>Score macro pondéré</div><div style='font-size:20px;font-weight:600;'>{macro_score}/100</div></div>",
+        unsafe_allow_html=True,
+    )
+
+
+def _fundamentals_tab(seed: int) -> None:
+    st.markdown("<div class='panel'><h3>Analyse fondamentale entreprises/actifs</h3></div>", unsafe_allow_html=True)
+    _metric_grid(_fundamental_metrics(seed))
+    st.markdown(
+        """
+        <div class="panel">
+            <h4>Diagnostic qualitatif</h4>
+            <ul>
+                <li>Moat : différenciation prix/qualité et leadership technologique.</li>
+                <li>Management : discipline capitalistique et amélioration du mix.</li>
+                <li>Risque : sensibilité aux conditions de financement globales.</li>
+            </ul>
+        </div>
+        """,
+        unsafe_allow_html=True,
+    )
+
+
+def _markets_tab(seed: int) -> None:
+    st.markdown("<div class='panel'><h3>Analyse des marchés financiers</h3></div>", unsafe_allow_html=True)
+    _metric_grid(_market_signals(seed))
+    st.markdown(
+        """
+        <div class="panel">
+            <h4>Lecture du régime de marché</h4>
+            <p>La corrélation reste élevée, signal d'allocation prudente et d'arbitrages ciblés.</p>
+        </div>
+        """,
+        unsafe_allow_html=True,
+    )
+
+
+def _portfolio_tab(seed: int) -> None:
+    st.markdown("<div class='panel'><h3>Gestion de portefeuille institutionnelle</h3></div>", unsafe_allow_html=True)
+    _metric_grid(_portfolio_metrics(seed))
+    alloc_df = pd.DataFrame(
+        {
+            "Segment": ["Core", "Satellite", "Hedges", "Cash"],
+            "Allocation": [45, 25, 20, 10],
+        }
+    )
+    fig_alloc = go.Figure(
+        data=[
+            go.Pie(
+                labels=alloc_df["Segment"],
+                values=alloc_df["Allocation"],
+                hole=0.55,
+                marker=dict(colors=[THEME["accent"], THEME["accent_alt"], THEME["warning"], THEME["muted"]]),
+            )
+        ]
+    )
+    fig_alloc.update_layout(
+        height=320,
+        plot_bgcolor=THEME["panel"],
+        paper_bgcolor=THEME["panel"],
+        font_color=THEME["text"],
+        legend_orientation="h",
+    )
+    st.plotly_chart(fig_alloc, width="stretch")
+
+
+def _hedge_tab(seed: int) -> None:
+    st.markdown("<div class='panel'><h3>Comportement hedge fund</h3></div>", unsafe_allow_html=True)
+    _metric_grid(_hedge_signals(seed))
+    st.markdown(
+        """
+        <div class="panel">
+            <h4>Arbitrages et inefficiences</h4>
+            <ul>
+                <li>Relative value : dispersion extrême intra-secteur.</li>
+                <li>Macro : asymétrie favorable en cas de repli des taux réels.</li>
+                <li>Contrarian : consensus encore fragile sur la trajectoire de croissance.</li>
+            </ul>
+        </div>
+        """,
+        unsafe_allow_html=True,
+    )
+
+
+def _decision_tab(seed: int, rating: str, decision: str) -> None:
+    st.markdown("<div class='panel'><h3>Thèse d'investissement structurée</h3></div>", unsafe_allow_html=True)
+    scenarios = _scenarios(seed)
+    scenario_df = pd.DataFrame(
+        {
+            "Scénario": [s.name for s in scenarios],
+            "Probabilité": [s.probability for s in scenarios],
+            "Narratif": [s.narrative for s in scenarios],
+        }
+    )
+    fig_scenarios = go.Figure(
+        data=[
+            go.Bar(
+                x=scenario_df["Scénario"],
+                y=scenario_df["Probabilité"],
+                marker_color=THEME["accent"],
             )
-            
-            # Sélection du timeframe
-            self.selected_timeframe = st.selectbox(
-                "Intervalle",
-                self.settings['timeframes'],
-                index=self.settings['timeframes'].index(
-                    self.settings['default_timeframe']
-                )
+        ]
+    )
+    fig_scenarios.update_layout(
+        height=280,
+        plot_bgcolor=THEME["panel"],
+        paper_bgcolor=THEME["panel"],
+        font_color=THEME["text"],
+        yaxis=dict(range=[0, 100], ticksuffix="%"),
+    )
+    st.plotly_chart(fig_scenarios, width="stretch")
+    st.dataframe(scenario_df, width="stretch")
+
+    thesis_blocks = _thesis_blocks(seed)
+    cols = st.columns(len(thesis_blocks))
+    for col, block in zip(cols, thesis_blocks):
+        with col:
+            st.markdown(
+                f"""
+                <div class="panel">
+                    <h4>{block.title}</h4>
+                    <p class="muted">{block.content}</p>
+                </div>
+                """,
+                unsafe_allow_html=True,
             )
-            
-            # Bouton d'analyse avec style iOS
-            if st.button("🔍 Analyser le Marché", key="analyze_btn"):
-                st.session_state.analyze_clicked = True
-                st.rerun()
-            
-            st.markdown("---")
-            
-            # Heures de trading
-            st.subheader("🕒 Sessions de Trading")
-            
-            # Afficher les heures des sessions de trading en temps Congo
-            london_start = self.settings['trading_sessions']['London']['start']
-            london_end = self.settings['trading_sessions']['London']['end']
-            ny_start = self.settings['trading_sessions']['New York']['start']
-            ny_end = self.settings['trading_sessions']['New York']['end']
-            
-            st.markdown(f"""
-            <div class="custom-card">
-                <p><strong>Londres</strong>: {london_start}-{london_end}</p>
-                <p><strong>New York</strong>: {ny_start}-{ny_end}</p>
-                <p><strong>Heure Congo</strong>: {datetime.now(CONGO_TZ).strftime("%H:%M")}</p>
-            </div>
-            """, unsafe_allow_html=True)
-            
-            # Gestion des actifs
-            with st.expander("📋 Gérer les actifs"):
-                new_asset = st.text_input("Ajouter un nouvel actif")
-                col1, col2 = st.columns(2)
-                with col1:
-                    if st.button("➕ Ajouter") and new_asset:
-                        if self.asset_category not in self.assets:
-                            self.assets[self.asset_category] = []
-                        self.assets[self.asset_category].append(new_asset)
-                        self._save_assets()
-                        st.success(f"Actif {new_asset} ajouté !")
-                with col2:
-                    if st.button("🗑️ Supprimer"):
-                        if self.selected_symbol in self.assets[self.asset_category]:
-                            self.assets[self.asset_category].remove(self.selected_symbol)
-                            self._save_assets()
-                            st.success(f"Actif {self.selected_symbol} supprimé !")
-                            st.rerun()
-    
-    def _create_ios_card(self, title: str, content: str):
-        """Crée une carte avec style iOS"""
-        return f"""
-        <div class="custom-card">
-            <h3 style="margin: 0 0 10px 0; color: var(--primary);">{title}</h3>
-            <p style="margin: 0; color: var(--text); white-space: pre-wrap;">{content}</p>
+
+    st.markdown(
+        f"""
+        <div class="panel">
+            <div class="rating">Notation interne : {rating}</div>
+            <div class="decision" style="color:{THEME['accent']};">Décision : {decision}</div>
         </div>
+        """,
+        unsafe_allow_html=True,
+    )
+
+
+def main() -> None:
+    _layout_style()
+
+    st.sidebar.title("Allocation Intelligence")
+    asset_class = st.sidebar.selectbox("Classe d'actifs", list(ASSET_UNIVERSE.keys()))
+    asset = st.sidebar.selectbox("Actif", ASSET_UNIVERSE[asset_class])
+    horizon = st.sidebar.selectbox("Horizon", ["Court terme", "Moyen terme", "Long terme"], index=1)
+    risk_budget = st.sidebar.slider("Budget de risque", 1, 10, 6)
+
+    seed = _stable_seed(f"{asset_class}-{asset}-{horizon}-{risk_budget}")
+    macro_factors = _make_macro_factors(seed)
+    macro_score = _weighted_score(macro_factors)
+    fundamental_score = max(40, min(90, macro_score + (seed % 7) - 3))
+    market_score = max(35, min(90, macro_score + (seed % 9) - 4))
+    portfolio_score = max(35, min(90, macro_score + (seed % 5) - 2))
+    hedge_score = max(35, min(90, macro_score + (seed % 11) - 5))
+
+    composite_score = int(
+        0.25 * macro_score
+        + 0.3 * fundamental_score
+        + 0.2 * market_score
+        + 0.15 * portfolio_score
+        + 0.1 * hedge_score
+    )
+
+    rating = _score_to_rating(composite_score)
+    decision = _score_to_decision(composite_score)
+
+    st.markdown(
         """
-    
-    def _display_pre_market_analysis(self, analysis: Dict):
-        """Affiche l'analyse pré-marché avec style iOS"""
-        st.subheader("🔍 Analyse Pré-Marché ICT")
-        
-        cols = st.columns(4)
-        
-        # Hauts/Bas égaux
-        with cols[0]:
-            eh_val = analysis['equal_highs_lows']['equal_highs']
-            el_val = analysis['equal_highs_lows']['equal_lows']
-            
-            eh_text = f"Haut: {eh_val:.2f}" if eh_val is not None else "N/A"
-            el_text = f"Bas: {el_val:.2f}" if el_val is not None else "N/A"
-            
-            st.markdown(self._create_ios_card(
-                "📏 Hauts et bas égaux",
-                f"{'✅ Détecté' if analysis['equal_highs_lows']['is_equal_high'] or analysis['equal_highs_lows']['is_equal_low'] else '❌ Non détecté'}\n{eh_text}\n{el_text}"
-            ), unsafe_allow_html=True)
-        
-        # ... (rest of the methods remain similar but use _create_ios_card) ...
-
-# ... (keep DataFetcher class and main execution unchanged) ...
+        <div class="panel">
+            <h2>Fonds d'investissement — Tableau de commandement fondamental</h2>
+            <div class="muted">Décisions structurées. Priorité à la préservation du capital.</div>
+        </div>
+        """,
+        unsafe_allow_html=True,
+    )
+
+    _header_kpis(composite_score, rating, decision, horizon)
+
+    tabs = st.tabs(
+        [
+            "Vue macro",
+            "Fondamentaux",
+            "Marchés",
+            "Portefeuille",
+            "Hedge fund",
+            "Décision",
+        ]
+    )
+
+    with tabs[0]:
+        _macro_tab(macro_factors, macro_score)
+
+    with tabs[1]:
+        _fundamentals_tab(seed)
+
+    with tabs[2]:
+        _markets_tab(seed)
+
+    with tabs[3]:
+        _portfolio_tab(seed)
+
+    with tabs[4]:
+        _hedge_tab(seed)
+
+    with tabs[5]:
+        _decision_tab(seed, rating, decision)
+
+
+if __name__ == "__main__":
+    main()


