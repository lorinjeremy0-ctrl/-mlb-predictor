import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import statsapi
import requests
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="MLB Predictor Pro", page_icon="⚾", layout="wide")
st.title("⚾ MLB Predictor Pro")
st.markdown("**API MLB Officielle • Prédictions en temps réel**")

class MLB_Predictor:
    def __init__(self):
        self.park_factors = {
            "Coors Field": 1.22, "Chase Field": 1.08, "Dodger Stadium": 0.94,
            "T-Mobile Park": 0.92, "loanDepot park": 0.95, "Yankee Stadium": 1.08,
            "Fenway Park": 1.05, "Wrigley Field": 1.04, "Oracle Park": 0.93,
            "default": 1.0
        }

    def get_todays_games(self):
        today = datetime.now().strftime("%Y-%m-%d")
        try:
            games = statsapi.schedule(date=today)
            data = []
            for g in games:
                data.append({
                    "away_team": g.get('away_name', 'TBD'),
                    "away_abbr": g.get('away_abbreviation', ''),
                    "home_team": g.get('home_name', 'TBD'),
                    "home_abbr": g.get('home_abbreviation', ''),
                    "away_pitcher": g.get('away_probable_pitcher', 'TBD'),
                    "home_pitcher": g.get('home_probable_pitcher', 'TBD'),
                    "venue": g.get('venue_name', 'Unknown'),
                    "status": g.get('status', 'Preview')
                })
            return pd.DataFrame(data)
        except Exception as e:
            st.error(f"Erreur API MLB : {e}")
            return pd.DataFrame()

    def get_pitcher_era(self, pitcher_name: str):
        if pitcher_name in ["TBD", "", None]:
            return 4.20
        try:
            people = statsapi.get("people", {"search": pitcher_name})['people']
            if people:
                pid = people[0]['id']
                stats = statsapi.player_stats(pid, "pitching", "season")
                if stats and stats.get('stats'):
                    era = stats['stats'][0]['splits'][0]['stat'].get('era', '4.20')
                    return float(era)
        except:
            pass
        return 4.20

    def get_last_5(self, team_id: int):
        try:
            end = datetime.now()
            start = end - timedelta(days=20)
            games = statsapi.schedule(start_date=start.strftime("%m/%d/%Y"),
                                      end_date=end.strftime("%m/%d/%Y"), team=team_id)
            results = []
            for g in sorted(games, key=lambda x: x.get('game_date',''), reverse=True)[:5]:
                if g.get('home_id') == team_id:
                    results.append('W' if g.get('home_score',0) > g.get('away_score',0) else 'L')
                else:
                    results.append('W' if g.get('away_score',0) > g.get('home_score',0) else 'L')
            return results if results else ['W','L','W','L','W']
        except:
            return ['W','L','W','L','W']

    def predict(self, home_team, away_team, home_pitcher, away_pitcher, venue, last5_home, last5_away):
        home_era = self.get_pitcher_era(home_pitcher)
        away_era = self.get
