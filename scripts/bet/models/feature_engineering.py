"""
Feature Engineering Module
Generates features from raw match data for model training
"""

import pandas as pd
import numpy as np
from datetime import datetime
import sys
sys.path.append('/var/www/html/pyethone/scripts/bet')
from config.config import *


class FeatureEngineer:
    """
    Feature engineering for football match prediction
    """
    
    def __init__(self, matches_df):
        """
        Initialize with match data
        
        Args:
            matches_df: DataFrame with historical match data
        """
        self.df = matches_df.copy()
        # Try to parse dates with multiple formats
        try:
            self.df['Date'] = pd.to_datetime(self.df['Date'], format='%d/%m/%Y')
        except ValueError:
            self.df['Date'] = pd.to_datetime(self.df['Date'], format='mixed', dayfirst=True)
        self.df = self.df.sort_values('Date').reset_index(drop=True)
        
        # Calculate league averages
        self._calculate_league_averages()
    
    def _calculate_league_averages(self):
        """Calculate league-wide averages for normalization"""
        self.league_avg_home_goals = self.df['FTHG'].mean()
        self.league_avg_away_goals = self.df['FTAG'].mean()
        self.league_avg_total_goals = (self.df['FTHG'] + self.df['FTAG']).mean()
        self.league_avg_home_win_rate = (self.df['FTR'] == 'H').mean()
        
        print(f"League averages calculated:")
        print(f"  Home goals: {self.league_avg_home_goals:.2f}")
        print(f"  Away goals: {self.league_avg_away_goals:.2f}")
        print(f"  Total goals: {self.league_avg_total_goals:.2f}")
        print(f"  Home win rate: {self.league_avg_home_win_rate:.2%}")
    
    def _calculate_team_form(self, team, date, home_away='all'):
        """
        Calculate team form metrics
        
        Args:
            team: Team name
            date: Current match date
            home_away: 'home', 'away', or 'all'
        
        Returns:
            Dict with form metrics
        """
        past = self.df[self.df['Date'] < date].copy()
        
        if home_away == 'home':
            team_matches = past[past['HomeTeam'] == team].tail(FORM_WINDOW)
            wins = (team_matches['FTR'] == 'H').sum()
            draws = (team_matches['FTR'] == 'D').sum()
            goals_scored = team_matches['FTHG'].mean()
            goals_conceded = team_matches['FTAG'].mean()
            clean_sheets = (team_matches['FTAG'] == 0).sum()
            
        elif home_away == 'away':
            team_matches = past[past['AwayTeam'] == team].tail(FORM_WINDOW)
            wins = (team_matches['FTR'] == 'A').sum()
            draws = (team_matches['FTR'] == 'D').sum()
            goals_scored = team_matches['FTAG'].mean()
            goals_conceded = team_matches['FTHG'].mean()
            clean_sheets = (team_matches['FTHG'] == 0).sum()
            
        else:  # all matches
            home_matches = past[past['HomeTeam'] == team]
            away_matches = past[past['AwayTeam'] == team]
            all_matches = pd.concat([home_matches, away_matches]).tail(FORM_WINDOW)
            
            # Count wins/draws from recent matches only
            home_wins = (all_matches[all_matches['HomeTeam'] == team]['FTR'] == 'H').sum()
            away_wins = (all_matches[all_matches['AwayTeam'] == team]['FTR'] == 'A').sum()
            wins = home_wins + away_wins
            
            draws = (all_matches['FTR'] == 'D').sum()
            
            # Calculate goals from recent matches
            recent_home = all_matches[all_matches['HomeTeam'] == team]
            recent_away = all_matches[all_matches['AwayTeam'] == team]
            
            goals_scored = (recent_home['FTHG'].sum() + recent_away['FTAG'].sum()) / len(all_matches) if len(all_matches) > 0 else 0
            goals_conceded = (recent_home['FTAG'].sum() + recent_away['FTHG'].sum()) / len(all_matches) if len(all_matches) > 0 else 0
            
            clean_sheets_home = (recent_home['FTAG'] == 0).sum()
            clean_sheets_away = (recent_away['FTHG'] == 0).sum()
            clean_sheets = clean_sheets_home + clean_sheets_away
            
            team_matches = all_matches
        
        matches_played = len(team_matches)
        
        # Calculate advanced metrics
        win_rate = wins / matches_played if matches_played > 0 else 0
        draw_rate = draws / matches_played if matches_played > 0 else 0
        clean_sheet_rate = clean_sheets / matches_played if matches_played > 0 else 0
        
        # League-adjusted ratings
        attack_strength = goals_scored / self.league_avg_home_goals if self.league_avg_home_goals > 0 else 1.0
        defense_strength = goals_conceded / self.league_avg_home_goals if self.league_avg_home_goals > 0 else 1.0
        
        return {
            'win_rate': win_rate,
            'draw_rate': draw_rate,
            'goals_per_match': goals_scored,
            'goals_conceded_per_match': goals_conceded,
            'clean_sheet_rate': clean_sheet_rate,
            'matches_played': matches_played,
            'attack_strength': attack_strength,  # NEW
            'defense_strength': defense_strength  # NEW
        }
    
    def _calculate_odds_performance(self, team, date, home_away='all'):
        """
        Calculate how team performs relative to bookmaker expectations
        
        Args:
            team: Team name
            date: Current match date
            home_away: 'home', 'away', or 'all'
        
        Returns:
            Dict with odds performance metrics
        """
        past = self.df[self.df['Date'] < date].copy()
        
        if home_away == 'home':
            team_matches = past[past['HomeTeam'] == team].tail(FORM_WINDOW)
            
            # When favorite (low odds), how often did they win?
            favorite_matches = team_matches[
                (team_matches['AvgH'] < team_matches['AvgD']) & 
                (team_matches['AvgH'] < team_matches['AvgA'])
            ]
            favorite_wins = (favorite_matches['FTR'] == 'H').sum()
            favorite_rate = favorite_wins / len(favorite_matches) if len(favorite_matches) > 0 else 0.5
            
            # When underdog (high odds), how often did they win?
            underdog_matches = team_matches[team_matches['AvgH'] > team_matches['AvgA']]
            underdog_wins = (underdog_matches['FTR'] == 'H').sum()
            underdog_rate = underdog_wins / len(underdog_matches) if len(underdog_matches) > 0 else 0.3
            
            # Overall reliability (result matched odds expectation)
            reliable_count = 0
            for _, match in team_matches.iterrows():
                is_favorite = match['AvgH'] < min(match['AvgD'], match['AvgA'])
                won = match['FTR'] == 'H'
                
                if (is_favorite and won) or (not is_favorite and not won):
                    reliable_count += 1
            
            reliability = reliable_count / len(team_matches) if len(team_matches) > 0 else 0.5
            
        elif home_away == 'away':
            team_matches = past[past['AwayTeam'] == team].tail(FORM_WINDOW)
            
            favorite_matches = team_matches[
                (team_matches['AvgA'] < team_matches['AvgD']) & 
                (team_matches['AvgA'] < team_matches['AvgH'])
            ]
            favorite_wins = (favorite_matches['FTR'] == 'A').sum()
            favorite_rate = favorite_wins / len(favorite_matches) if len(favorite_matches) > 0 else 0.5
            
            underdog_matches = team_matches[team_matches['AvgA'] > team_matches['AvgH']]
            underdog_wins = (underdog_matches['FTR'] == 'A').sum()
            underdog_rate = underdog_wins / len(underdog_matches) if len(underdog_matches) > 0 else 0.3
            
            reliable_count = 0
            for _, match in team_matches.iterrows():
                is_favorite = match['AvgA'] < min(match['AvgD'], match['AvgH'])
                won = match['FTR'] == 'A'
                
                if (is_favorite and won) or (not is_favorite and not won):
                    reliable_count += 1
            
            reliability = reliable_count / len(team_matches) if len(team_matches) > 0 else 0.5
            
        else:  # all matches
            reliability = 0.5
            favorite_rate = 0.5
            underdog_rate = 0.3
        
        return {
            'odds_reliability': reliability,
            'favorite_win_rate': favorite_rate,
            'underdog_win_rate': underdog_rate
        }
    
    def _calculate_h2h(self, home_team, away_team, date):
        """
        Calculate head-to-head statistics
        
        Returns:
            Dict with H2H metrics
        """
        past = self.df[self.df['Date'] < date]
        
        # All matches between these teams
        h2h = past[
            ((past['HomeTeam'] == home_team) & (past['AwayTeam'] == away_team)) |
            ((past['HomeTeam'] == away_team) & (past['AwayTeam'] == home_team))
        ].tail(H2H_WINDOW)
        
        if len(h2h) == 0:
            return {
                'h2h_matches': 0,
                'h2h_home_wins': 0,
                'h2h_draws': 0,
                'h2h_away_wins': 0,
                'h2h_avg_goals': self.league_avg_total_goals
            }
        
        # Count results
        home_wins = len(h2h[(h2h['HomeTeam'] == home_team) & (h2h['FTR'] == 'H')])
        home_wins += len(h2h[(h2h['AwayTeam'] == home_team) & (h2h['FTR'] == 'A')])
        
        away_wins = len(h2h[(h2h['AwayTeam'] == away_team) & (h2h['FTR'] == 'A')])
        away_wins += len(h2h[(h2h['HomeTeam'] == away_team) & (h2h['FTR'] == 'H')])
        
        draws = (h2h['FTR'] == 'D').sum()
        avg_goals = (h2h['FTHG'] + h2h['FTAG']).mean()
        
        return {
            'h2h_matches': len(h2h),
            'h2h_home_wins': home_wins,
            'h2h_draws': draws,
            'h2h_away_wins': away_wins,
            'h2h_avg_goals': avg_goals
        }
    
    def _calculate_referee_stats(self, referee, date):
        """Calculate referee card statistics"""
        past = self.df[self.df['Date'] < date]
        ref_matches = past[past['Referee'] == referee].tail(20)
        
        if len(ref_matches) == 0:
            return {
                'ref_avg_yellow': 3.0,
                'ref_avg_red': 0.2
            }
        
        return {
            'ref_avg_yellow': ref_matches[['HY', 'AY']].sum(axis=1).mean(),
            'ref_avg_red': ref_matches[['HR', 'AR']].sum(axis=1).mean()
        }
    
    def create_features(self):
        """
        Generate feature dataset from raw matches
        
        Returns:
            DataFrame with engineered features
        """
        print("Generating features...")
        
        # Add temporal weight (more recent = higher weight)
        self.df['temporal_weight'] = self.df.index / len(self.df)
        self.df['temporal_weight'] = self.df['temporal_weight'].apply(lambda x: TEMPORAL_DECAY ** (1 - x))
        
        features_list = []
        
        for idx, row in self.df.iterrows():
            if idx % 100 == 0:
                print(f"Processing match {idx}/{len(self.df)}...")
            
            home_team = row['HomeTeam']
            away_team = row['AwayTeam']
            date = row['Date']
            referee = row.get('Referee', 'Unknown')
            
            # Skip early matches without sufficient history
            if idx < 20:
                continue
            
            # Calculate all components
            home_form = self._calculate_team_form(home_team, date, 'home')
            away_form = self._calculate_team_form(away_team, date, 'away')
            home_overall = self._calculate_team_form(home_team, date, 'all')
            away_overall = self._calculate_team_form(away_team, date, 'all')
            home_odds_perf = self._calculate_odds_performance(home_team, date, 'home')
            away_odds_perf = self._calculate_odds_performance(away_team, date, 'away')
            h2h = self._calculate_h2h(home_team, away_team, date)
            ref_stats = self._calculate_referee_stats(referee, date)
            
            # Matchup-specific features
            expected_home_goals = home_form['attack_strength'] * away_form['defense_strength'] * self.league_avg_home_goals
            expected_away_goals = away_form['attack_strength'] * home_form['defense_strength'] * self.league_avg_away_goals
            
            # Compile features
            features = {
                # Match identifiers
                'match_id': idx,
                'home_team': home_team,
                'away_team': away_team,
                'date': date,
                'season': row['Season'],
                'temporal_weight': row['temporal_weight'],
                
                # Home team form
                'home_form_win_rate': home_form['win_rate'],
                'home_form_draw_rate': home_form['draw_rate'],
                'home_form_goals_scored': home_form['goals_per_match'],
                'home_form_goals_conceded': home_form['goals_conceded_per_match'],
                'home_form_clean_sheet_rate': home_form['clean_sheet_rate'],
                'home_attack_strength': home_form['attack_strength'],
                'home_defense_strength': home_form['defense_strength'],
                
                # Away team form
                'away_form_win_rate': away_form['win_rate'],
                'away_form_draw_rate': away_form['draw_rate'],
                'away_form_goals_scored': away_form['goals_per_match'],
                'away_form_goals_conceded': away_form['goals_conceded_per_match'],
                'away_form_clean_sheet_rate': away_form['clean_sheet_rate'],
                'away_attack_strength': away_form['attack_strength'],
                'away_defense_strength': away_form['defense_strength'],
                
                # Overall form
                'home_overall_win_rate': home_overall['win_rate'],
                'away_overall_win_rate': away_overall['win_rate'],
                
                # Odds performance
                'home_odds_reliability': home_odds_perf['odds_reliability'],
                'home_favorite_win_rate': home_odds_perf['favorite_win_rate'],
                'home_underdog_win_rate': home_odds_perf['underdog_win_rate'],
                'away_odds_reliability': away_odds_perf['odds_reliability'],
                'away_favorite_win_rate': away_odds_perf['favorite_win_rate'],
                'away_underdog_win_rate': away_odds_perf['underdog_win_rate'],
                
                # Head to head
                'h2h_matches': h2h['h2h_matches'],
                'h2h_home_win_rate': h2h['h2h_home_wins'] / h2h['h2h_matches'] if h2h['h2h_matches'] > 0 else 0.46,
                'h2h_draw_rate': h2h['h2h_draws'] / h2h['h2h_matches'] if h2h['h2h_matches'] > 0 else 0.25,
                'h2h_avg_goals': h2h['h2h_avg_goals'],
                
                # Matchup features
                'expected_home_goals': expected_home_goals,
                'expected_away_goals': expected_away_goals,
                'expected_total_goals': expected_home_goals + expected_away_goals,
                'attack_defense_diff': home_form['attack_strength'] - away_form['defense_strength'],
                
                # Referee
                'ref_avg_yellow': ref_stats['ref_avg_yellow'],
                'ref_avg_red': ref_stats['ref_avg_red'],
                
                # Target variables
                'outcome': row['FTR'],
                'home_goals': row['FTHG'],
                'away_goals': row['FTAG'],
                'total_goals': row['FTHG'] + row['FTAG'],
                'total_cards': row.get('HY', 0) + row.get('AY', 0),
                'home_cards': row.get('HY', 0),
                'away_cards': row.get('AY', 0)
            }
            
            features_list.append(features)
        
        features_df = pd.DataFrame(features_list)

        # Fill missing values with league averages
        features_df['home_attack_strength'] = features_df['home_attack_strength'].fillna(1.0)
        features_df['home_defense_strength'] = features_df['home_defense_strength'].fillna(1.0)
        features_df['away_attack_strength'] = features_df['away_attack_strength'].fillna(1.0)
        features_df['away_defense_strength'] = features_df['away_defense_strength'].fillna(1.0)
        features_df['home_form_goals_scored'] = features_df['home_form_goals_scored'].fillna(self.league_avg_home_goals)
        features_df['home_form_goals_conceded'] = features_df['home_form_goals_conceded'].fillna(self.league_avg_away_goals)
        features_df['away_form_goals_scored'] = features_df['away_form_goals_scored'].fillna(self.league_avg_away_goals)
        features_df['away_form_goals_conceded'] = features_df['away_form_goals_conceded'].fillna(self.league_avg_home_goals)
        features_df['expected_home_goals'] = features_df['expected_home_goals'].fillna(self.league_avg_home_goals)
        features_df['expected_away_goals'] = features_df['expected_away_goals'].fillna(self.league_avg_away_goals)
        features_df['expected_total_goals'] = features_df['expected_total_goals'].fillna(self.league_avg_total_goals)
        features_df['attack_defense_diff'] = features_df['attack_defense_diff'].fillna(0.0)

        
        print(f"\nGenerated {len(features_df)} feature rows")
        print(f"Feature columns: {len(features_df.columns)}")
        
        return features_df

        
        print(f"\nGenerated {len(features_df)} feature rows")
        print(f"Feature columns: {len(features_df.columns)}")
        
        return features_df


# Main execution
if __name__ == "__main__":
    print("Loading match data...")
    matches = pd.read_csv(MATCHES_FILE)
    
    print(f"Loaded {len(matches)} matches")
    
    engineer = FeatureEngineer(matches)
    features = engineer.create_features()
    
    # Save to processed data
    output_file = PROCESSED_DATA
    features.to_csv(output_file, index=False)
    
    print(f"\nFeatures saved to: {output_file}")
    print(f"Shape: {features.shape}")
    print(f"\nSample features:")
    print(features.head(3))
