# Football Prediction System - Model Information & Training Parameters

## Overview

This document explains the machine learning models used in the system, the training procedures, and key parameters.

## Models Included

The system currently uses multiple specialized models, all based on XGBoost:

| Model Name      | Task Description                                   |
|-----------------|--------------------------------------------------|
| `1x2`                | Predict match result: Home Win, Draw, or Away Win|
| `1x`, `12`, `x2`   | Predict combined outcomes (double chance)        |
| `over_05`, `over_15`, `over_25` | Match total goals over specified thresholds |
| `team_over_05`, `team_over_15`, `team_over_25` | Team-specific goal-scoring over thresholds   |
| `cards`         | Predict total match cards (regression)            |
| `team_cards`    | Predict cards per team (regression)                |

## Training Overview

- Features include team recent form, home/away splits, head-to-head history, referee stats, and bookmaker odds.
- Temporal weighting is applied, giving recent matches higher weight.
- Models are trained using historical CSV data processed by `feature_engineering.py`.
- Training performed by `train_models.py` using XGBoost with early stopping and validation split.

## Key Training Parameters (config/config.py)

| Parameter                                 | Value      | Description                           |
|----------------------------------|------------|-------------------------------------|
| `N_ESTIMATORS`                      | 1000        | Number of trees in boosting          |
| `LEARNING_RATE`                    | 0.01          | Boosting learning rate                 |
| `MAX_DEPTH`                          | 5               | Maximum tree depth                     |
| `TEST_SIZE`                              | 0.15          | Fraction for validation split          |
| `RECENT_MATCHES_WEIGHT`  | 1.5           | Weight multiplier for most recent season |
| `FORM_WINDOW`                    | 5             | Number of recent matches used for form  |
| `H2H_WINDOW`                      | 10            | Number of head-to-head matches considered|

## Model Storage

- Trained models are saved as `.pkl` files in `models/saved_models/`.
- Metadata including feature columns and training date is saved for loading during prediction.

## Extending Models

- The modular design allows adding secondary models, e.g., neural networks or ensembles.
- Additional features can be incorporated by modifying `feature_engineering.py`.
- Retraining scripts accommodate new models without impacting existing ones.

## Notes

- Models produce probabilistic outputs enabling odds calculation.
- Regression models output numeric predictions for cards.
- Models can be retrained after each match day using provided API or CLI commands.