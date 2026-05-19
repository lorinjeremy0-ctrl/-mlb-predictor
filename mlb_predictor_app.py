import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import statsapi
import requests
import warnings

warnings.filterwarnings('ignore')

st.set_page_config(page_title="MLB Predictor Pro", page_icon="⚾", layout="wide")

st.title("⚾ MLB Predictor Pro")
st.markdown("**Clique sur un match** pour voir la prédiction immédiate")

class MLB_Predictor:
    def __init__(self):
        self.park_factors = {
            "Coors Field": 1.22, "Chase Field": 1.08, "Yankee Stadium": 1.08,
            "Dodger Stadium": 0.94, "T-Mobile Park": 0.92, "Oracle Park": 0.93,
            "loanDepot park": 0.95, "Fenway Park": 1.05, "Wrigley Field": 1.04,
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
                    "Away": g.get('away_name'),
                    "Home": g.get('home_name'),
                    "Away_Pitcher": g.get('away_probable_pitcher', 'TBD'),
                    "Home_Pitcher": g.get('home_probable_pitcher', 'TBD'),
                    "Venue": g.get('venue_name', 'Unknown')
                })
            return pd.DataFrame(data)
        except:
            return pd.DataFrame()

    def get_pitcher_stats(self, name):
        if not name or name == "TBD":
            return 4.20, 4.20
        try:
            people = statsapi.get("people", {"search": name})['people']
            if people:
                pid = people[0]['id']
                stats = statsapi.player_stats(pid, "pitching", "season")
                if stats and stats.get('stats'):
                    s = stats['stats'][0]['splits'][0]['stat']
                    return float(s.get('era', 4.20)), float(s.get('fip', 4.20))
        except:
            pass
        return 4.20, 4.20

    def predict(self, home_team, away_team, home_p, away_p, venue):
        home_era, home_fip = self.get_pitcher_stats(home_p)
        away_era, away_fip = self.get_pitcher_stats(away_p)
        park = self.park_factors.get(venue, 1.0)

        score = 0.525 + (away_fip - home_fip) * 0.09 + (park - 1.0) * 0.5
        prob_home = max(0.40, min(0.68, score + np.random.normal(0, 0.025)))

        return {
            "prob_home": round(prob_home * 100, 1),
            "prob_away": round((1 - prob_home) * 100, 1),
            "expected_total": round(8.8 * park, 1),
            "home_fip": round(home_fip, 2),
            "away_fip": round(away_fip, 2)
        }

predictor = MLB_Predictor()

# Sidebar
with st.sidebar:
    st.header("Configuration")
    st.text_input("Clé OpenWeatherMap (optionnelle)", type="password", key="weather_key")

# ==================== MATCHS CLICABLES ====================
st.subheader("Matchs du jour - Clique pour prédire")

df = predictor.get_todays_games()

if df.empty:
    st.warning("Aucun match aujourd'hui ou erreur de connexion.")
else:
    # Affichage des matchs sous forme de boutons cliquables
    for idx, row in df.iterrows():
        col1, col2 = st.columns([4, 1])
        with col1:
            if st.button(f"⚾ {row['Match']} - {row['Venue']}", key=f"btn_{idx}"):
                st.session_state.selected_match = idx
        with col2:
            st.write("")

    # Affichage de la prédiction du match sélectionné
    if 'selected_match' in st.session_state:
        game = df.iloc[st.session_state.selected_match]
        st.markdown("---")
        st.success(f"**Prédiction pour : {game['Match']}**")
        
        result = predictor.predict(
            game["Home"], game["Away"], 
            game["Home_Pitcher"], game["Away_Pitcher"], 
            game["Venue"]
        )
        
        col1, col2, col3 = st.columns(3)
        col1.metric("🏠 Victoire Domicile", f"{result['prob_home']}%", f"FIP {result['home_fip']}")
        col2.metric("🚶 Victoire Extérieur", f"{result['prob_away']}%", f"FIP {result['away_fip']}")
        col3.metric("Total points attendu", result['expected_total'])
        
        if result['prob_home'] > 57:
            st.success("🔥 **Favori : Domicile**")
        elif result['prob_home'] < 46:
            st.success("🔥 **Favori : Extérieur**")
        else:
            st.info("Match équilibré")

st.caption("Clique sur un match ci-dessus pour voir la prédiction instantanée")
