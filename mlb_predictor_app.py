import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import statsapi
import warnings

warnings.filterwarnings('ignore')

st.set_page_config(page_title="MLB Predictor", page_icon="⚾", layout="wide")

st.title("⚾ MLB Predictor Pro")
st.markdown("**Prédictions MLB • Tous les stades disponibles**")

class MLB_Predictor:
    def __init__(self):
        self.park_factors = {
            "Angel Stadium": 0.98,
            "American Family Field": 1.02,
            "Busch Stadium": 0.96,
            "Chase Field": 1.08,
            "Citi Field": 0.97,
            "Citizens Bank Park": 1.04,
            "Comerica Park": 0.98,
            "Coors Field": 1.22,
            "Dodger Stadium": 0.94,
            "Fenway Park": 1.05,
            "Globe Life Field": 1.05,
            "Great American Ball Park": 1.10,
            "Guaranteed Rate Field": 1.06,
            "Kauffman Stadium": 1.00,
            "loanDepot park": 0.95,
            "Minute Maid Park": 1.03,
            "Nationals Park": 0.98,
            "Oakland Coliseum": 0.96,
            "Oracle Park": 0.93,
            "Petco Park": 0.93,
            "PNC Park": 0.94,
            "Progressive Field": 0.97,
            "Rogers Centre": 1.03,
            "Sutter Health Park": 1.05,
            "Target Field": 0.99,
            "T-Mobile Park": 0.92,
            "Truist Park": 1.02,
            "Tropicana Field": 0.97,
            "Wrigley Field": 1.04,
            "Yankee Stadium": 1.08,
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
            st.error(f"Erreur API MLB : {str(e)[:100]}")
            return pd.DataFrame()

    def predict_simple(self, venue):
        park = self.park_factors.get(venue, 1.0)
        prob_home = 0.54 + (park - 1.0) * 0.35
        prob_home = max(0.35, min(0.75, prob_home))
        return {
            "prob_home": round(prob_home * 100, 1),
            "expected_total": round(8.8 * park, 1)
        }

predictor = MLB_Predictor()

tab1, tab2 = st.tabs(["📅 Matchs du jour", "🔮 Prédiction manuelle"])

with tab1:
    if st.button("Charger les matchs du jour"):
        with st.spinner("Connexion à l'API MLB..."):
            df = predictor.get_todays_games()
            if not df.empty:
                st.dataframe(df, use_container_width=True)
                st.success(f"{len(df)} match(s) trouvé(s)")
            else:
                st.warning("Aucun match aujourd'hui ou erreur API")

with tab2:
    st.subheader("Prédiction manuelle")
    
    # Liste des stades triée
    stadium_list = sorted(list(predictor.park_factors.keys()))
    venue = st.selectbox("Sélectionner le Stade", stadium_list)
    
    col1, col2 = st.columns(2)
    with col1:
        home_p = st.text_input("Lanceur Domicile", "Yamamoto")
    with col2:
        away_p = st.text_input("Lanceur Extérieur", "Senga")
    
    if st.button("🔮 Prédire ce match", type="primary"):
        result = predictor.predict_simple(venue)
        col_a, col_b = st.columns(2)
        col_a.metric("🏠 Victoire Domicile", f"{result['prob_home']}%")
        col_b.metric("Total points attendu", result['expected_total'])
        st.success("Prédiction terminée !")

st.caption("✅ 30 stades MLB disponibles • Version mobile optimisée")
