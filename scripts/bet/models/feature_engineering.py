"""
Feature Engineering Module
Creates predictive features from raw match data
"""

import pandas as pd
import numpy as np
from datetime import datetime
import sys
sys.path.append('/var/www/html/pyethone/scripts/bet')
from config.config import *


class FeatureEngineer:
    """
    Generates features for football match prediction including:
    - Team form (recent performance)
    - Home/away splits
    - Head-to-head history
    - Goal scoring patterns
    - Cards history by referee
    """
    
    def __init__(self, matches_df):
        """
        Initialize with match dataframe
        
        Args:
            matches_df: DataFrame with match history
        """
        self.df = matches_df.copy()
        self._prepare_data()
    
    def _prepare_data(self):
        """Convert dates and sort chronologically"""
        # Convert date column to datetime
        self.df['Date'] = pd.to_datetime(self.df['Date'], format='%m/%d/%Y', errors='coerce')
        
        # Sort by date
        self.df = self.df.sort_values('Date').reset_index(drop=True)
        
        # Add temporal weight (more recent = higher weight)
        self.df['temporal_weight'] = self._calculate_temporal_weights()
    
    def _calculate_temporal_weights(self):
        """
        Calculate exponential weights favoring recent matches
        Most recent season gets weight=1.5, decreasing exponentially
        """
        seasons = sorted(self.df['Season'].unique(), reverse=True)
        weights = {}
        
        for idx, season in enumerate(seasons):
            # Most recent: 1.5, then decay by 0.85
            weights[season] = RECENT_MATCHES_WEIGHT * (0.85 ** idx)
        
        return self.df['Season'].map(weights)
    
    def _calculate_team_form(self, team, date, home_away='all'):
        """
        Calculate team form: win/draw/loss rate in last N matches
        
        Args:
            team: Team name
            date: Current match date
            home_away: 'home', 'away', or 'all'
        
        Returns:
            Dict with form metrics
        """
        # Get past matches before this date
        past = self.df[self.df['Date'] < date].copy()
        
        if home_away == 'home':
            team_matches = past[past['HomeTeam'] == team].tail(FORM_WINDOW)
            wins = (team_matches['FTR'] == 'H').sum()
            draws = (team_matches['FTR'] == 'D').sum()
            goals_scored = team_matches['FTHG'].mean()
            goals_conceded = team_matches['FTAG'].mean()
            
        elif home_away == 'away':
            team_matches = past[past['AwayTeam'] == team].tail(FORM_WINDOW)
            wins = (team_matches['FTR'] == 'A').sum()
            draws = (team_matches['FTR'] == 'D').sum()
            goals_scored = team_matches['FTAG'].mean()
            goals_conceded = team_matches['FTHG'].mean()
            
        else:  # all matches
            home_matches = past[past['HomeTeam'] == team]
            away_matches = past[past['AwayTeam'] == team]
            all_matches = pd.concat([home_matches, away_matches]).tail(FORM_WINDOW)
            
            home_wins = (home_matches['FTR'] == 'H').sum()
            away_wins = (away_matches['FTR'] == 'A').sum()
            wins = home_wins + away_wins
            
            draws = ((home_matches['FTR'] == 'D').sum() + 
                    (away_matches['FTR'] == 'D').sum())
            
            goals_scored = (home_matches['FTHG'].sum() + 
                          away_matches['FTAG'].sum()) / len(all_matches) if len(all_matches) > 0 else 0
            
            goals_conceded = (home_matches['FTAG'].sum() + 
                            away_matches['FTHG'].sum()) / len(all_matches) if len(all_matches) > 0 else 0
        
        matches_played = len(team_matches) if home_away != 'all' else len(all_matches)
        
        return {
            'win_rate': wins / matches_played if matches_played > 0 else 0,
            'draw_rate': draws / matches_played if matches_played > 0 else 0,
            'goals_per_match': goals_scored,
            'goals_conceded_per_match': goals_conceded,
            'matches_played': matches_played
        }
    
    def _calculate_h2h(self, home_team, away_team, date):
        """
        Calculate head-to-head statistics
        
        Returns:
            Dict with H2H metrics
        """
        past = self.df[self.df['Date'] < date]
        
        # Matches between these two teams
        h2h = past[
            ((past['HomeTeam'] == home_team) & (past['AwayTeam'] == away_team)) |
            ((past['HomeTeam'] == away_team) & (past['AwayTeam'] == home_team))
        ].tail(H2H_WINDOW)
        
        if len(h2h) == 0:
            return {
                'h2h_matches': 0,
                'h2h_home_wins': 0,
                'h2h_away_wins': 0,
                'h2h_draws': 0,
                'h2h_avg_goals': 0
            }
        
        # Count results when home_team was actually home
        home_as_home = h2h[h2h['HomeTeam'] == home_team]
        away_as_away = h2h[h2h['AwayTeam'] == home_team]
        
        home_wins = (home_as_home['FTR'] == 'H').sum() + (away_as_away['FTR'] == 'A').sum()
        away_wins = (home_as_home['FTR'] == 'A').sum() + (away_as_away['FTR'] == 'H').sum()
        draws = (h2h['FTR'] == 'D').sum()
        
        avg_goals = (h2h['FTHG'] + h2h['FTAG']).mean()
        
        return {
            'h2h_matches': len(h2h),
            'h2h_home_wins': home_wins,
            'h2h_away_wins': away_wins,
            'h2h_draws': draws,
            'h2h_avg_goals': avg_goals
        }
    
    def _calculate_referee_stats(self, referee, date):
        """
        Calculate referee card-giving tendencies
        
        Returns:
            Dict with referee metrics
        """
        if pd.isna(referee):
            return {
                'ref_avg_yellow': 3.0,  # League average defaults
                'ref_avg_red': 0.2,
                'ref_matches': 0
            }
        
        past = self.df[(self.df['Date'] < date) & (self.df['Referee'] == referee)]
        
        if len(past) == 0:
            return {
                'ref_avg_yellow': 3.0,
                'ref_avg_red': 0.2,
                'ref_matches': 0
            }
        
        # Total cards per match
        avg_yellow = (past['HY'].fillna(0) + past['AY'].fillna(0)).mean()
        avg_red = (past['HR'].fillna(0) + past['AR'].fillna(0)).mean()
        
        return {
            'ref_avg_yellow': avg_yellow,
            'ref_avg_red': avg_red,
            'ref_matches': len(past)
        }
    
    def create_features(self):
        """
        Main method: Generate all features for each match
        
        Returns:
            DataFrame with engineered features
        """
        features_list = []
        
        print("Generating features for {} matches...".format(len(self.df)))
        
        for idx, row in self.df.iterrows():
            if idx % 100 == 0:
                print(f"Processing match {idx}/{len(self.df)}")
            
            home_team = row['HomeTeam']
            away_team = row['AwayTeam']
            date = row['Date']
            referee = row['Referee']
            
            # Skip early matches with insufficient history
            if idx < 20:
                continue
            
            # Calculate all feature components
            home_form = self._calculate_team_form(home_team, date, 'home')
            away_form = self._calculate_team_form(away_team, date, 'away')
            home_overall = self._calculate_team_form(home_team, date, 'all')
            away_overall = self._calculate_team_form(away_team, date, 'all')
            h2h = self._calculate_h2h(home_team, away_team, date)
            ref_stats = self._calculate_referee_stats(referee, date)
            
            # Compile feature dictionary
            features = {
                # Match identifiers
                'match_id': idx,
                'home_team': home_team,
                'away_team': away_team,
                'date': date,
                'season': row['Season'],
                'temporal_weight': row['temporal_weight'],
                
                # Home team form (home matches only)
                'home_form_win_rate': home_form['win_rate'],
                'home_form_draw_rate': home_form['draw_rate'],
                'home_form_goals_scored': home_form['goals_per_match'],
                'home_form_goals_conceded': home_form['goals_conceded_per_match'],
                
                # Away team form (away matches only)
                'away_form_win_rate': away_form['win_rate'],
                'away_form_draw_rate': away_form['draw_rate'],
                'away_form_goals_scored': away_form['goals_per_match'],
                'away_form_goals_conceded': away_form['goals_conceded_per_match'],
                
                # Overall team form
                'home_overall_win_rate': home_overall['win_rate'],
                'away_overall_win_rate': away_overall['win_rate'],
                
                # Head-to-head
                'h2h_matches': h2h['h2h_matches'],
                'h2h_home_win_rate': h2h['h2h_home_wins'] / h2h['h2h_matches'] if h2h['h2h_matches'] > 0 else 0.33,
                'h2h_draw_rate': h2h['h2h_draws'] / h2h['h2h_matches'] if h2h['h2h_matches'] > 0 else 0.33,
                'h2h_avg_goals': h2h['h2h_avg_goals'],
                
                # Referee tendencies
                'ref_avg_yellow': ref_stats['ref_avg_yellow'],
                'ref_avg_red': ref_stats['ref_avg_red'],
                
                # Bookmaker odds (as features - market intelligence)
                'odds_home': row.get('AvgH', np.nan),
                'odds_draw': row.get('AvgD', np.nan),
                'odds_away': row.get('AvgA', np.nan),
                'odds_over25': row.get('Avg>2.5', np.nan),
                
                # Target variables (what we want to predict)
                'target_result': row['FTR'],  # H/D/A
                'target_home_goals': row['FTHG'],
                'target_away_goals': row['FTAG'],
                'target_total_goals': row['FTHG'] + row['FTAG'],
                'target_home_cards': row.get('HY', 0) + row.get('HR', 0),
                'target_away_cards': row.get('AY', 0) + row.get('AR', 0),
                'target_total_cards': (row.get('HY', 0) + row.get('HR', 0) + 
                                      row.get('AY', 0) + row.get('AR', 0))
            }
            
            features_list.append(features)
        
        features_df = pd.DataFrame(features_list)
        
        print(f"\nFeature engineering complete!")
        print(f"Generated {len(features_df)} training samples with {len(features_df.columns)} features")
        
        return features_df


# Quick test function
if __name__ == "__main__":
    print("Loading match data...")
    matches = pd.read_csv(MATCHES_FILE)
    
    print(f"Loaded {len(matches)} matches")
    
    engineer = FeatureEngineer(matches)
    features = engineer.create_features()
    
    # Save processed features
    os.makedirs(os.path.dirname(PROCESSED_DATA), exist_ok=True)
    features.to_csv(PROCESSED_DATA, index=False)
    
    print(f"\nFeatures saved to: {PROCESSED_DATA}")
    print("\nSample features:")
    print(features.head(3))
