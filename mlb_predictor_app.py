import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import statsapi
import warnings

warnings.filterwarnings('ignore')

st.set_page_config(page_title="MLB Predictor", page_icon="⚾", layout="wide")

st.title("⚾ MLB Predictor Pro")
st.markdown("**Prédictions MLB en temps réel**")

# ====================== CLASSE SIMPLIFIÉE ======================
class MLB_Predictor:
    def __init__(self):
        self.park_factors = {
            "Coors Field": 1.22, "Dodger Stadium": 0.94, "Yankee Stadium": 1.08,
            "Fenway Park": 1.05, "Wrigley Field": 1.04, "default": 1.0
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

    def predict_simple(self, home_pitcher, away_pitcher, venue):
        park = self.park_factors.get(venue, 1.0)
        # Simulation simple
        prob_home = 0.54 + (park - 1.0) * 0.3
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
                st.success(f"{len(df)} match(s) trouvé(s) aujourd'hui")
            else:
                st.warning("Aucun match aujourd'hui ou erreur API")

with tab2:
    st.subheader("Prédiction rapide")
    col1, col2 = st.columns(2)
    with col1:
        home_p = st.text_input("Lanceur Domicile", "Yamamoto")
    with col2:
        away_p = st.text_input("Lanceur Extérieur", "Senga")
    
    venue = st.selectbox("Stade", list(predictor.park_factors.keys()))
    
    if st.button("🔮 Prédire", type="primary"):
        result = predictor.predict_simple(home_p, away_p, venue)
        col_a, col_b = st.columns(2)
        col_a.metric("Probabilité Victoire Domicile", f"{result['prob_home']}%")
        col_b.metric("Total points attendu", result['expected_total'])
        st.success("Prédiction terminée !")

st.caption("Version simplifiée et stable pour mobile • Mise à jour mai 2026")
