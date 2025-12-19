-- Farmer Dashboard Backend Database Schema
-- Contains 3 main tables for storing farmer inputs, profit calculations, and forecasts

-- Table 1: Farmer Inputs
-- Stores initial farmer input data for crop comparison
CREATE TABLE IF NOT EXISTS farmer_inputs (
    input_id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    farmer_name VARCHAR(100),
    farmer_email VARCHAR(100),
    farmer_location VARCHAR(200),
    
    -- Oil seed crop inputs
    oilseed_name VARCHAR(50) NOT NULL,
    oilseed_area FLOAT NOT NULL CHECK (oilseed_area > 0),
    oilseed_expected_yield FLOAT NOT NULL CHECK (oilseed_expected_yield >= 0),
    oilseed_market_price FLOAT NOT NULL CHECK (oilseed_market_price >= 0),
    oilseed_total_cost_per_hectare FLOAT NOT NULL CHECK (oilseed_total_cost_per_hectare >= 0),
    
    -- Alternative crop inputs
    crop_name VARCHAR(50) NOT NULL,
    crop_area FLOAT NOT NULL CHECK (crop_area > 0),
    crop_expected_yield FLOAT NOT NULL CHECK (crop_expected_yield >= 0),
    crop_market_price FLOAT NOT NULL CHECK (crop_market_price >= 0),
    crop_total_cost_per_hectare FLOAT NOT NULL CHECK (crop_total_cost_per_hectare >= 0),
    
    -- Metadata
    notes TEXT,
    is_archived BOOLEAN DEFAULT 0
);

-- Index on farmer name and crop names for faster queries
CREATE INDEX idx_farmer_inputs_farmer_name ON farmer_inputs(farmer_name);
CREATE INDEX idx_farmer_inputs_crops ON farmer_inputs(oilseed_name, crop_name);
CREATE INDEX idx_farmer_inputs_created_at ON farmer_inputs(created_at);


-- Table 2: Profit Results
-- Stores calculated profit metrics from farmer inputs
CREATE TABLE IF NOT EXISTS profit_results (
    result_id INTEGER PRIMARY KEY AUTOINCREMENT,
    input_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Oil seed profit metrics
    oilseed_total_yield FLOAT NOT NULL,
    oilseed_total_revenue FLOAT NOT NULL,
    oilseed_total_cost FLOAT NOT NULL,
    oilseed_net_profit FLOAT NOT NULL,
    oilseed_profit_margin FLOAT NOT NULL,
    oilseed_roi FLOAT NOT NULL,
    oilseed_profit_per_kg FLOAT NOT NULL,
    
    -- Alternative crop profit metrics
    crop_total_yield FLOAT NOT NULL,
    crop_total_revenue FLOAT NOT NULL,
    crop_total_cost FLOAT NOT NULL,
    crop_net_profit FLOAT NOT NULL,
    crop_profit_margin FLOAT NOT NULL,
    crop_roi FLOAT NOT NULL,
    crop_profit_per_kg FLOAT NOT NULL,
    
    -- Comparison metrics
    more_profitable_crop VARCHAR(50) NOT NULL,
    profit_difference FLOAT NOT NULL,
    roi_difference FLOAT NOT NULL,
    percentage_better FLOAT NOT NULL,
    
    -- Recommendation
    recommended_crop VARCHAR(50),
    recommendation_score FLOAT,
    
    -- Metadata
    notes TEXT,
    FOREIGN KEY (input_id) REFERENCES farmer_inputs(input_id) ON DELETE CASCADE
);

-- Indexes for faster queries
CREATE INDEX idx_profit_results_input_id ON profit_results(input_id);
CREATE INDEX idx_profit_results_created_at ON profit_results(created_at);
CREATE INDEX idx_profit_results_recommended_crop ON profit_results(recommended_crop);


-- Table 3: Forecast Results
-- Stores ARIMA forecast results (12-month predictions with confidence intervals)
CREATE TABLE IF NOT EXISTS forecast_results (
    forecast_id INTEGER PRIMARY KEY AUTOINCREMENT,
    result_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Oil seed forecast (12 months)
    oilseed_month_1_forecast FLOAT, oilseed_month_1_lower FLOAT, oilseed_month_1_upper FLOAT,
    oilseed_month_2_forecast FLOAT, oilseed_month_2_lower FLOAT, oilseed_month_2_upper FLOAT,
    oilseed_month_3_forecast FLOAT, oilseed_month_3_lower FLOAT, oilseed_month_3_upper FLOAT,
    oilseed_month_4_forecast FLOAT, oilseed_month_4_lower FLOAT, oilseed_month_4_upper FLOAT,
    oilseed_month_5_forecast FLOAT, oilseed_month_5_lower FLOAT, oilseed_month_5_upper FLOAT,
    oilseed_month_6_forecast FLOAT, oilseed_month_6_lower FLOAT, oilseed_month_6_upper FLOAT,
    oilseed_month_7_forecast FLOAT, oilseed_month_7_lower FLOAT, oilseed_month_7_upper FLOAT,
    oilseed_month_8_forecast FLOAT, oilseed_month_8_lower FLOAT, oilseed_month_8_upper FLOAT,
    oilseed_month_9_forecast FLOAT, oilseed_month_9_lower FLOAT, oilseed_month_9_upper FLOAT,
    oilseed_month_10_forecast FLOAT, oilseed_month_10_lower FLOAT, oilseed_month_10_upper FLOAT,
    oilseed_month_11_forecast FLOAT, oilseed_month_11_lower FLOAT, oilseed_month_11_upper FLOAT,
    oilseed_month_12_forecast FLOAT, oilseed_month_12_lower FLOAT, oilseed_month_12_upper FLOAT,
    
    -- Oil seed forecast summary
    oilseed_average_forecast FLOAT NOT NULL,
    oilseed_forecast_std FLOAT NOT NULL,
    oilseed_forecast_aic FLOAT,
    
    -- Alternative crop forecast (12 months)
    crop_month_1_forecast FLOAT, crop_month_1_lower FLOAT, crop_month_1_upper FLOAT,
    crop_month_2_forecast FLOAT, crop_month_2_lower FLOAT, crop_month_2_upper FLOAT,
    crop_month_3_forecast FLOAT, crop_month_3_lower FLOAT, crop_month_3_upper FLOAT,
    crop_month_4_forecast FLOAT, crop_month_4_lower FLOAT, crop_month_4_upper FLOAT,
    crop_month_5_forecast FLOAT, crop_month_5_lower FLOAT, crop_month_5_upper FLOAT,
    crop_month_6_forecast FLOAT, crop_month_6_lower FLOAT, crop_month_6_upper FLOAT,
    crop_month_7_forecast FLOAT, crop_month_7_lower FLOAT, crop_month_7_upper FLOAT,
    crop_month_8_forecast FLOAT, crop_month_8_lower FLOAT, crop_month_8_upper FLOAT,
    crop_month_9_forecast FLOAT, crop_month_9_lower FLOAT, crop_month_9_upper FLOAT,
    crop_month_10_forecast FLOAT, crop_month_10_lower FLOAT, crop_month_10_upper FLOAT,
    crop_month_11_forecast FLOAT, crop_month_11_lower FLOAT, crop_month_11_upper FLOAT,
    crop_month_12_forecast FLOAT, crop_month_12_lower FLOAT, crop_month_12_upper FLOAT,
    
    -- Alternative crop forecast summary
    crop_average_forecast FLOAT NOT NULL,
    crop_forecast_std FLOAT NOT NULL,
    crop_forecast_aic FLOAT,
    
    -- Forecast comparison
    more_stable_forecast VARCHAR(50),
    stability_ratio FLOAT,
    
    -- Confidence level
    confidence_level FLOAT DEFAULT 0.95,  -- 95% confidence interval
    
    -- Metadata
    notes TEXT,
    FOREIGN KEY (result_id) REFERENCES profit_results(result_id) ON DELETE CASCADE
);

-- Indexes for faster queries
CREATE INDEX idx_forecast_results_result_id ON forecast_results(result_id);
CREATE INDEX idx_forecast_results_created_at ON forecast_results(created_at);


-- Create views for common queries

-- View: Latest profit results for each farmer
CREATE VIEW IF NOT EXISTS latest_profit_results AS
SELECT 
    f.farmer_name,
    f.farmer_email,
    p.created_at,
    p.oilseed_name,
    p.crop_name,
    p.oilseed_net_profit,
    p.crop_net_profit,
    p.recommended_crop,
    p.recommendation_score
FROM farmer_inputs f
INNER JOIN profit_results p ON f.input_id = p.input_id
WHERE p.created_at = (
    SELECT MAX(p2.created_at)
    FROM profit_results p2
    WHERE p2.input_id = f.input_id
);


-- View: Profit comparison summary
CREATE VIEW IF NOT EXISTS profit_comparison_summary AS
SELECT 
    p.oilseed_name,
    p.crop_name,
    COUNT(*) as comparison_count,
    AVG(p.oilseed_net_profit) as avg_oilseed_profit,
    AVG(p.crop_net_profit) as avg_crop_profit,
    MAX(CASE WHEN p.recommended_crop = p.oilseed_name THEN 1 ELSE 0 END) as oilseed_recommended_count,
    MAX(CASE WHEN p.recommended_crop = p.crop_name THEN 1 ELSE 0 END) as crop_recommended_count
FROM profit_results p
GROUP BY p.oilseed_name, p.crop_name;


-- View: Forecast stability summary
CREATE VIEW IF NOT EXISTS forecast_stability_summary AS
SELECT 
    f.oilseed_name,
    f.crop_name,
    fr.oilseed_forecast_std,
    fr.crop_forecast_std,
    fr.more_stable_forecast,
    fr.stability_ratio,
    fr.created_at
FROM forecast_results fr
INNER JOIN profit_results f ON fr.result_id = f.result_id;


-- Stored Procedures / Triggers (if using SQLite, use triggers)

-- Trigger to update updated_at timestamp when farmer_inputs is modified
CREATE TRIGGER IF NOT EXISTS update_farmer_inputs_timestamp
AFTER UPDATE ON farmer_inputs
BEGIN
    UPDATE farmer_inputs SET updated_at = CURRENT_TIMESTAMP
    WHERE input_id = NEW.input_id;
END;


-- Trigger to update updated_at timestamp when profit_results is modified
CREATE TRIGGER IF NOT EXISTS update_profit_results_timestamp
AFTER UPDATE ON profit_results
BEGIN
    UPDATE profit_results SET updated_at = CURRENT_TIMESTAMP
    WHERE result_id = NEW.result_id;
END;


-- Trigger to update updated_at timestamp when forecast_results is modified
CREATE TRIGGER IF NOT EXISTS update_forecast_results_timestamp
AFTER UPDATE ON forecast_results
BEGIN
    UPDATE forecast_results SET updated_at = CURRENT_TIMESTAMP
    WHERE forecast_id = NEW.forecast_id;
END;


-- Sample data for testing (commented out - uncomment to use)
-- INSERT INTO farmer_inputs (farmer_name, farmer_email, farmer_location,
--                            oilseed_name, oilseed_area, oilseed_expected_yield, oilseed_market_price, oilseed_total_cost_per_hectare,
--                            crop_name, crop_area, crop_expected_yield, crop_market_price, crop_total_cost_per_hectare)
-- VALUES ('Rajesh Sharma', 'rajesh@example.com', 'Maharashtra',
--         'Soybean', 2, 2000, 60, 45000,
--         'Maize', 2, 5000, 25, 36000);
