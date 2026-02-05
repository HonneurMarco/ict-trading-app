#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import ccxt
import yfinance as yf
import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
from datetime import datetime, time
import pytz
import json
import os
from typing import Dict, Tuple, List

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
}

DEFAULT_SETTINGS = {
    "theme": "dark",
    "timeframes": ["15m", "1h", "4h", "1d"],
    "default_timeframe": "4h",
    "trading_sessions": {
        "London": {"start": "07:00", "end": "16:00"},
        "New York": {"start": "13:00", "end": "22:00"}
    },
    "risk_per_trade": 0.01,
    "candle_colors": {
        "bullish": "#34C759",  # Vert iOS
        "bearish": "#FF3B30"   # Rouge iOS
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
        <style>
        :root {{
            --primary: {ios_colors['primary']};
            --secondary: {ios_colors['secondary']};
            --background: {ios_colors['background']};
            --card-bg: {ios_colors['card']};
            --text: {ios_colors['text']};
            --border: {ios_colors['border']};
        }}
        
        body {{
            background-color: var(--background);
        }}
        
        .main {{
            background-color: var(--background);
            color: var(--text);
            font-family: -apple-system, BlinkMacSystemFont, sans-serif;
        }}
        
        .sidebar .sidebar-content {{
            background-color: var(--card-bg);
            border-right: 1px solid var(--border);
        }}
        
        .stButton>button {{
            background-color: var(--primary);
            border: none;
            color: white;
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
            border-radius: 10px;
            border: 1px solid var(--border);
        }}
        
        .stSelectbox>div>div {{
            border-radius: 10px;
            border: 1px solid var(--border);
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
            border: 1px solid var(--border);
        }}
        
        /* Section headers */
        .section-header {{
            font-size: 20px;
            font-weight: 600;
            margin-bottom: 15px;
            color: var(--text);
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
            )
            
            # Sélection du timeframe
            self.selected_timeframe = st.selectbox(
                "Intervalle",
                self.settings['timeframes'],
                index=self.settings['timeframes'].index(
                    self.settings['default_timeframe']
                )
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
