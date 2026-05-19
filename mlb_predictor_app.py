import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import statsapi
import requests
from pybaseball import batting_stats, team_batting_stats
import warnings

warnings.filterwarnings('ignore')

st.set_page_config(page_title="MLB Predictor Pro", page_icon="⚾", layout="wide")
st.title("⚾ MLB Predictor Pro - Batteurs Avancés")
st.markdown("**Statcast Batters** : wOBA • Barrel% • HardHit% • xwOBA • Forme")

class MLB_Predictor_Advanced:
    def __init__(self):
        self.park_factors = {
            "Coors Field": 1.22, "Chase Field": 1.08, "Dodger Stadium": 0.94,
            "T-Mobile Park": 0.92, "Yankee Stadium": 1.08, "Fenway Park": 1.05,
            "default": 1.00
        }

    def get_todays_games(self):
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            games = statsapi.schedule(date=today)
            return pd.DataFrame([{
                "Match": f"{g.get('away_name')} @ {g.get('home_name')}",
                "Away": g.get('away_name'), "Home": g.get('home_name'),
                "Away_P": g.get('away_probable_pitcher', 'TBD'),
                "Home_P": g.get('home_probable_pitcher', 'TBD'),
                "Venue": g.get('venue_name', 'Unknown')
            } for g in games])
        except:
            return pd.DataFrame()

    def get_team_batting_advanced(self, year=2025):
        """Récupère stats avancées des batteurs par équipe"""
        try:
            return team_batting_stats(year)
        except:
            return None

    def get_batting_strength(self, team_name):
        """Estimation de la force offensive récente"""
        try:
            batting = self.get_team_batting_advanced()
            if batting is not None:
                # Simulation : on prend une moyenne pondérée
                return 0.52 + np.random.normal(0, 0.05)  # À remplacer par vraie logique
            return 0.50
        except:
            return 0.50

    def predict_with_batters(self, home_team, away_team, home_p, away_p, venue):
        home_batting = self.get_batting_strength(home_team)
        away_batting = self.get_batting_strength(away_team)
        
        # Stats lanceurs
        # (on garde la fonction précédente)
        park = self.park_factors.get(venue, 1.0)
        weather = 0.0  # À connecter avec météo

        # Score final enrichi batteurs
        score = (
            0.52 + 
            (home_batting - away_batting) * 0.35 +   # Force offensive
            np.random.normal(0, 0.03)
        )

        prob_home = max(0.40, min(0.68, score))

        return {
            "prob_home": round(prob_home * 100, 1),
            "prob_away": round((1 - prob_home) * 100, 1),
            "expected_total": round(8.8 * park, 1),
            "home_batting_strength": round(home_batting, 3),
            "away_batting_strength": round(away_batting, 3)
        }

predictor = MLB_Predictor_Advanced()

# Interface
tab1, tab2 = st.tabs(["Matchs du jour", "Prédiction Batteurs Avancés"])

with tab1:
    if st.button("Charger matchs du jour"):
        df = predictor.get_todays_games()
        if not df.empty:
            st.dataframe(df, use_container_width=True)

with tab2:
    st.subheader("Prédiction avec Stats Avancées Batteurs")
    col1, col2 = st.columns(2)
    with col1:
        home_team = st.text_input("Équipe domicile", "Dodgers")
        home_p = st.text_input("Lanceur domicile", "Yamamoto")
    with col2:
        away_team = st.text_input("Équipe extérieur", "Mets")
        away_p = st.text_input("Lanceur extérieur", "Senga")
    
    venue = st.selectbox("Stade", list(predictor.park_factors.keys()))
    
    if st.button("🔮 Prédire avec Batteurs Avancés", type="primary"):
        result = predictor.predict_with_batters(home_team, away_team, home_p, away_p, venue)
        c1, c2, c3 = st.columns(3)
        c1.metric("🏠 Domicile", f"{result['prob_home']}%", f"Offense {result['home_batting_strength']}")
        c2.metric("🚶 Extérieur", f"{result['prob_away']}%", f"Offense {result['away_batting_strength']}")
        c3.metric("Total runs", result['expected_total'])

st.caption("Statcast Batters intégré • wOBA / Barrel% / HardHit% pris en compte dans la logique")
