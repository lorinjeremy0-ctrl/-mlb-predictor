import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import statsapi
import warnings

warnings.filterwarnings('ignore')

st.set_page_config(page_title="MLB Predictor", page_icon="⚾", layout="wide")

st.title("⚾ MLB Predictor Pro")
st.markdown("**Prédictions MLB en temps réel • Tous les stades**")

# ====================== CLASSE ======================
class MLB_Predictor:
    def __init__(self):
        # Tous les stades MLB (mise à jour 2026)
        self.park_factors = {
            "Coors Field": 1.22,
            "Chase Field": 1.08,
            "Yankee Stadium": 1.08,
            "Fenway Park": 1.05,
            "Wrigley Field": 1.04,
            "Great American Ball Park": 1.10,
            "Globe Life Field": 1.05,
            "Citizens Bank Park": 1.04,
            "American Family Field": 1.02,
            "Rogers Centre": 1.03,
            "Dodger Stadium": 0.94,
            "T-Mobile Park": 0.92,
            "Oracle Park": 0.93,
            "loanDepot park": 0.95,
            "Petco Park": 0.93,
            "Angel Stadium": 0.98,
            "Oakland Coliseum": 0.96,
            "Progressive Field": 0.97,
            "Comerica Park": 0.98,
            "Target Field": 0.99,
            "Guaranteed Rate Field": 1.06,
            "Minute Maid Park": 1.03,
            "Nationals Park": 0.98,
            "Citi Field": 0.97,
            "Busch Stadium": 0.96,
            "PNC Park": 0.94,
            "Truist Park": 1.02,
            "Kauffman Stadium": 1.00,
            "Tropicana Field": 0.97,
            "Sutter Health Park": 1.05,   # Sacramento (nouvelle équipe)
            "default": 1.00
        }

    def get_todays_games(self):
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            games = statsapi.schedule(date=today)
            data = []
            for g in games:
                data.append({
                    "Match": f"{g.get('away_name','?')} @ {g.get('home_name','?')}",
                    "Lanceur Away": g.get('away_probable_pitcher', 'TBD'),
                    "Lanceur Home": g.get('home_probable_pitcher', 'TBD'),
                    "Stade": g.get('venue_name', 'Unknown')
                })
            return pd.DataFrame(data)
        except Exception as e:
            st.error(f"Erreur API MLB : {str(e)[:120]}")
            return pd.DataFrame()

    def predict_simple(self, home_pitcher, away_pitcher, venue):
        park = self.park_factors.get(venue, 1.0)
        prob_home = 0.535 + (park - 1.0) * 0.35   # Avantage domicile + effet stade
        prob_home = max(0.35, min(0.75, prob_home))
        
        return {
            "prob_home": round(prob_home * 100, 1),
            "expected_total": round(8.8 * park, 1)
        }

predictor = MLB_Predictor()

# ====================== INTERFACE ======================
tab1, tab2 = st.tabs(["📅 Matchs du jour", "🔮 Prédiction manuelle"])

with tab1:
    if st.button("Charger les matchs du jour"):
        with st.spinner("Connexion à l'API MLB..."):
            df = predictor.get_todays_games()
            if not df.empty:
                st.dataframe(df, use_container_width=True)
                st.success(f"{len(df)} match(s) aujourd'hui")
            else:
                st.warning("Aucun match ou erreur de connexion")

with tab2:
    st.subheader("Prédiction manuelle")
    col1, col2 = st.columns(2)
    with col1:
        home_p = st.text_input("Lanceur Domicile", "Yamamoto")
    with col2:
        away_p = st.text_input("Lanceur Extérieur", "Senga")
    
    # Liste complète des stades
   
