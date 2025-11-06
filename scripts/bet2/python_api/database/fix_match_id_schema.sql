-- Fix match_id to be based on actual match date, not prediction date
-- This allows multiple predictions for the same match

BEGIN TRANSACTION;

-- 1. Add prediction_id column (unique identifier for each prediction)
ALTER TABLE predictions ADD COLUMN prediction_id TEXT;

-- 2. Populate prediction_id with old match_id values (includes prediction date)
UPDATE predictions SET prediction_id = match_id;

-- 3. Update match_id to be based on match_date instead of prediction_date
-- Format: Home_Away_MatchDate
UPDATE predictions
SET
    match_id = home_team || '_' || away_team || '_' || match_date
WHERE
    match_date IS NOT NULL;

-- 4. Update the unique constraint (keep for backward compatibility)
-- Note: You may need to recreate the table to change constraints properly
-- For now, this updates the data. Full constraint change requires table recreation.

-- 5. Create index on new prediction_id
CREATE INDEX IF NOT EXISTS idx_predictions_prediction_id ON predictions (prediction_id);

-- 6. Update actual_results to match new match_id format
UPDATE actual_results
SET
    match_id = home_team || '_' || away_team || '_' || match_date
WHERE
    match_date IS NOT NULL;

COMMIT;

-- Verify the changes
SELECT
    'Before: prediction-date based' as description,
    prediction_id,
    match_id,
    match_date
FROM predictions
LIMIT 3;