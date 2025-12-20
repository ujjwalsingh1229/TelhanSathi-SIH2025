"""
ENHANCED FORECAST DASHBOARD - Real-time location-based oilseed recommendations
Shows time series data with charts for farmers
Features:
- Location-aware price predictions
- Real-time best oilseed recommendations
- Beautiful time series visualizations
- Farmer-friendly insights and trends
"""

from flask import Flask, render_template_string, request, jsonify
from forecast_engine import ForecastEngine
import json
from datetime import datetime, timedelta
import numpy as np

# Initialize forecast engine
engine = ForecastEngine()

# ============================================================
# ENHANCED FORECAST DASHBOARD - HTML WITH INTERACTIVE CHARTS
# ============================================================

ENHANCED_DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📊 Farmer Forecast Dashboard - Location Based</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .header {
            background: rgba(255, 255, 255, 0.95);
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            margin-bottom: 30px;
        }
        
        .header h1 {
            color: #333;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .header h1::before {
            content: "📍";
            font-size: 32px;
        }
        
        .controls {
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
            margin-bottom: 20px;
        }
        
        .control-group {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }
        
        label {
            color: #555;
            font-weight: 600;
            font-size: 14px;
        }
        
        input, select {
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 14px;
            font-family: inherit;
            transition: all 0.3s;
        }
        
        input:focus, select:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        button {
            padding: 12px 30px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            font-size: 14px;
            align-self: flex-end;
        }
        
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
        }
        
        button:active {
            transform: translateY(0);
        }
        
        .content {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-bottom: 30px;
        }
        
        @media (max-width: 1200px) {
            .content {
                grid-template-columns: 1fr;
            }
        }
        
        .card {
            background: rgba(255, 255, 255, 0.95);
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }
        
        .card h2 {
            color: #333;
            margin-bottom: 20px;
            font-size: 20px;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }
        
        .chart-container {
            position: relative;
            height: 400px;
            margin-bottom: 20px;
        }
        
        .recommendation-box {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 20px;
        }
        
        .recommendation-box h3 {
            font-size: 18px;
            margin-bottom: 10px;
        }
        
        .recommendation-box .crop-name {
            font-size: 24px;
            font-weight: bold;
            margin: 10px 0;
        }
        
        .recommendation-box .metrics {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin-top: 15px;
            font-size: 14px;
        }
        
        .metric-item {
            background: rgba(255, 255, 255, 0.2);
            padding: 12px;
            border-radius: 8px;
        }
        
        .metric-label {
            opacity: 0.9;
            font-size: 12px;
        }
        
        .metric-value {
            font-size: 18px;
            font-weight: bold;
            margin-top: 5px;
        }
        
        .recommendations-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }
        
        .recommendation-item {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 10px;
            border-left: 4px solid #667eea;
            transition: all 0.3s;
        }
        
        .recommendation-item:hover {
            transform: translateY(-5px);
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        }
        
        .recommendation-item h4 {
            color: #667eea;
            margin-bottom: 10px;
            font-size: 16px;
        }
        
        .rec-metric {
            display: flex;
            justify-content: space-between;
            padding: 5px 0;
            font-size: 13px;
            border-bottom: 1px solid #ddd;
        }
        
        .rec-metric:last-child {
            border-bottom: none;
        }
        
        .rec-label {
            color: #666;
        }
        
        .rec-value {
            font-weight: bold;
            color: #333;
        }
        
        .location-badge {
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 13px;
            margin-top: 10px;
        }
        
        .trend-indicator {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
            margin-left: 10px;
        }
        
        .trend-up {
            background: #d4edda;
            color: #155724;
        }
        
        .trend-down {
            background: #f8d7da;
            color: #721c24;
        }
        
        .trend-neutral {
            background: #e7e7e7;
            color: #333;
        }
        
        .loading {
            text-align: center;
            padding: 40px;
            color: #999;
        }
        
        .loading-spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .error {
            background: #f8d7da;
            color: #721c24;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #f5c6cb;
        }
        
        .success {
            background: #d4edda;
            color: #155724;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #c3e6cb;
        }
        
        .info-box {
            background: #d1ecf1;
            color: #0c5460;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #bee5eb;
            margin-bottom: 20px;
        }
        
        .comparison-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }
        
        .comparison-table th {
            background: #667eea;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }
        
        .comparison-table td {
            padding: 12px;
            border-bottom: 1px solid #ddd;
        }
        
        .comparison-table tr:hover {
            background: #f8f9fa;
        }
        
        .no-data {
            text-align: center;
            padding: 40px;
            color: #999;
            font-size: 16px;
        }
        
        .full-width {
            grid-column: 1 / -1;
        }
        
        .footer {
            background: rgba(255, 255, 255, 0.95);
            padding: 20px;
            border-radius: 15px;
            text-align: center;
            color: #666;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- HEADER -->
        <div class="header">
            <h1>🌾 Farmer Forecast Dashboard - Location Based</h1>
            <p style="color: #666; margin-bottom: 20px;">Get personalized oilseed recommendations for your location with real-time market insights</p>
            
            <!-- CONTROLS -->
            <div class="controls">
                <div class="control-group" style="flex: 1; min-width: 200px;">
                    <label for="location">📍 Select Your Location:</label>
                    <select id="location">
                        <option value="">-- Choose Location --</option>
                        <option value="maharashtra">Maharashtra (+5% premium)</option>
                        <option value="karnataka">Karnataka (+8% premium)</option>
                        <option value="madhya_pradesh">Madhya Pradesh (+2% premium)</option>
                        <option value="andhra_pradesh">Andhra Pradesh (+3% premium)</option>
                        <option value="punjab">Punjab (-2% lower)</option>
                        <option value="rajasthan">Rajasthan (-5% lower)</option>
                        <option value="bihar">Bihar (-3% lower)</option>
                        <option value="uttar_pradesh">Uttar Pradesh (-1% lower)</option>
                    </select>
                </div>
                
                <div class="control-group" style="flex: 1; min-width: 200px;">
                    <label for="current_crop">🌾 Current Crop (Optional):</label>
                    <input type="text" id="current_crop" placeholder="e.g., wheat, cotton" value="wheat">
                </div>
                
                <div class="control-group" style="flex: 1; min-width: 150px;">
                    <label for="area_acres">📐 Area (Acres):</label>
                    <input type="number" id="area_acres" placeholder="5" value="5" min="1" max="1000">
                </div>
                
                <div class="control-group" style="flex: 1; min-width: 150px;">
                    <label for="cost_per_acre">💰 Cost per Acre (₹):</label>
                    <input type="number" id="cost_per_acre" placeholder="100000" value="100000" min="10000" max="500000">
                </div>
                
                <button onclick="getRecommendations()" style="margin-top: 22px;">🔍 Get Recommendations</button>
            </div>
        </div>
        
        <!-- MAIN CONTENT -->
        <div id="content" class="content">
            <div class="loading">
                <div class="loading-spinner"></div>
                <p>Loading forecast data...</p>
            </div>
        </div>
        
        <!-- FOOTER -->
        <div class="footer">
            <p>💡 Tip: Select your location for accurate price recommendations based on regional market conditions</p>
            <p style="margin-top: 10px; font-size: 12px;">Last updated: <span id="timestamp"></span></p>
        </div>
    </div>

    <script>
        // Update timestamp
        function updateTimestamp() {
            const now = new Date();
            document.getElementById('timestamp').innerText = now.toLocaleString();
        }
        updateTimestamp();

        // Get recommendations from API
        async function getRecommendations() {
            const location = document.getElementById('location').value;
            const current_crop = document.getElementById('current_crop').value || 'wheat';
            const area_acres = parseFloat(document.getElementById('area_acres').value) || 5;
            const cost_per_acre = parseFloat(document.getElementById('cost_per_acre').value) || 100000;

            if (!location) {
                showError('Please select your location first!');
                return;
            }

            showLoading();

            try {
                const response = await fetch('/api/location-based-forecast', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        location: location,
                        current_crop: current_crop,
                        area_acres: area_acres,
                        cost_per_acre: cost_per_acre
                    })
                });

                const data = await response.json();

                if (data.status === 'success') {
                    displayRecommendations(data, location);
                } else {
                    showError('Error: ' + (data.message || 'Unknown error'));
                }
            } catch (error) {
                showError('Failed to fetch recommendations: ' + error.message);
            }
        }

        // Display recommendations with charts
        function displayRecommendations(data, location) {
            const contentDiv = document.getElementById('content');
            let html = '';

            // Top recommendation
            if (data.top_oilseed) {
                const top = data.top_oilseed;
                const trendClass = top.price_trend > 10 ? 'trend-up' : (top.price_trend < 0 ? 'trend-down' : 'trend-neutral');
                const trendText = top.price_trend > 10 ? '📈 UPTREND' : (top.price_trend < 0 ? '📉 DOWNTREND' : '→ STABLE');

                html += `
                    <div class="card full-width">
                        <h2>🏆 Top Recommendation for Your Location</h2>
                        <div class="recommendation-box">
                            <h3>Best Oilseed to Grow:</h3>
                            <div class="crop-name">${top.crop.toUpperCase()}</div>
                            <span class="trend-indicator ${trendClass}">${trendText} ${top.price_trend.toFixed(1)}%</span>
                            <div class="metrics">
                                <div class="metric-item">
                                    <div class="metric-label">Current Price</div>
                                    <div class="metric-value">₹${top.avg_price_12m.toFixed(0)}/Qt</div>
                                </div>
                                <div class="metric-item">
                                    <div class="metric-label">Est. Annual Profit</div>
                                    <div class="metric-value">₹${top.estimated_profit.toFixed(0)}</div>
                                </div>
                                <div class="metric-item">
                                    <div class="metric-label">Profit/Acre</div>
                                    <div class="metric-value">₹${top.profit_per_acre.toFixed(0)}</div>
                                </div>
                                <div class="metric-item">
                                    <div class="metric-label">Market Outlook</div>
                                    <div class="metric-value">${top.market_outlook}</div>
                                </div>
                            </div>
                            <div class="location-badge">📍 Location Premium: +${((top.location_price_multiplier - 1) * 100).toFixed(0)}%</div>
                        </div>
                    </div>
                `;
            }

            // Price trend chart
            if (data.recommendations && data.recommendations.length > 0) {
                html += `
                    <div class="card">
                        <h2>📈 Price Forecasts - Next 12 Months</h2>
                        <div class="chart-container">
                            <canvas id="priceChart"></canvas>
                        </div>
                    </div>
                `;
            }

            // Comparison chart
            html += `
                <div class="card">
                    <h2>💰 Profit Comparison</h2>
                    <div class="chart-container">
                        <canvas id="profitChart"></canvas>
                    </div>
                </div>
            `;

            // Recommendations table
            if (data.recommendations && data.recommendations.length > 0) {
                html += `
                    <div class="card full-width">
                        <h2>🌾 Top 3 Oilseed Recommendations</h2>
                        <div class="recommendations-grid">
                `;

                data.recommendations.forEach((rec, index) => {
                    const trendClass = rec.price_trend > 10 ? 'trend-up' : (rec.price_trend < 0 ? 'trend-down' : 'trend-neutral');
                    html += `
                        <div class="recommendation-item">
                            <h4>#${index + 1} - ${rec.crop.toUpperCase()}</h4>
                            <div class="rec-metric">
                                <span class="rec-label">Price/Qt:</span>
                                <span class="rec-value">₹${rec.avg_price_12m.toFixed(0)}</span>
                            </div>
                            <div class="rec-metric">
                                <span class="rec-label">Profit/Year:</span>
                                <span class="rec-value">₹${(rec.estimated_profit / 100000).toFixed(1)}L</span>
                            </div>
                            <div class="rec-metric">
                                <span class="rec-label">Price Trend:</span>
                                <span class="rec-value ${trendClass}">${rec.price_trend.toFixed(1)}%</span>
                            </div>
                            <div class="rec-metric">
                                <span class="rec-label">Suitable:</span>
                                <span class="rec-value">${rec.suitable_for_location ? '✅ Yes' : '⚠️ No'}</span>
                            </div>
                            <div class="rec-metric">
                                <span class="rec-label">Outlook:</span>
                                <span class="rec-value" style="font-size: 11px;">${rec.market_outlook}</span>
                            </div>
                        </div>
                    `;
                });

                html += `
                        </div>
                    </div>
                `;
            }

            // Suitable crops info
            if (data.suitable_crops_for_location) {
                html += `
                    <div class="card full-width">
                        <h2>🎯 Suitable Crops for ${location.toUpperCase()}</h2>
                        <div class="info-box">
                            Best oilseeds for your region: <strong>${data.suitable_crops_for_location.join(', ').toUpperCase()}</strong>
                        </div>
                    </div>
                `;
            }

            contentDiv.innerHTML = html;

            // Draw charts
            if (data.recommendations && data.recommendations.length > 0) {
                drawPriceChart(data.recommendations);
                drawProfitChart(data.recommendations);
            }

            updateTimestamp();
        }

        // Draw price forecast chart
        function drawPriceChart(recommendations) {
            const ctx = document.getElementById('priceChart');
            if (!ctx) return;

            const months = Array.from({ length: 12 }, (_, i) => `M${i + 1}`);
            const datasets = recommendations.map((rec, index) => {
                const colors = [
                    { border: '#667eea', bg: 'rgba(102, 126, 234, 0.1)' },
                    { border: '#764ba2', bg: 'rgba(118, 75, 162, 0.1)' },
                    { border: '#f093fb', bg: 'rgba(240, 147, 251, 0.1)' }
                ];
                
                const color = colors[index] || colors[0];
                return {
                    label: rec.crop.toUpperCase(),
                    data: rec.forecast_prices || [],
                    borderColor: color.border,
                    backgroundColor: color.bg,
                    tension: 0.4,
                    fill: true,
                    pointRadius: 5,
                    pointHoverRadius: 7,
                    borderWidth: 2
                };
            });

            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: months,
                    datasets: datasets
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'top',
                            labels: {
                                usePointStyle: true,
                                padding: 15,
                                font: { size: 13, weight: 'bold' }
                            }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: false,
                            ticks: { callback: function(value) { return '₹' + value; } }
                        }
                    }
                }
            });
        }

        // Draw profit comparison chart
        function drawProfitChart(recommendations) {
            const ctx = document.getElementById('profitChart');
            if (!ctx) return;

            const crops = recommendations.map(r => r.crop.toUpperCase());
            const profits = recommendations.map(r => r.estimated_profit);

            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: crops,
                    datasets: [{
                        label: 'Estimated Annual Profit (₹)',
                        data: profits,
                        backgroundColor: [
                            'rgba(102, 126, 234, 0.8)',
                            'rgba(118, 75, 162, 0.8)',
                            'rgba(240, 147, 251, 0.8)'
                        ],
                        borderColor: [
                            '#667eea',
                            '#764ba2',
                            '#f093fb'
                        ],
                        borderWidth: 2,
                        borderRadius: 8
                    }]
                },
                options: {
                    indexAxis: 'y',
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false }
                    },
                    scales: {
                        x: {
                            ticks: { callback: function(value) { return '₹' + (value / 100000).toFixed(0) + 'L'; } }
                        }
                    }
                }
            });
        }

        // Show loading state
        function showLoading() {
            document.getElementById('content').innerHTML = `
                <div style="grid-column: 1 / -1;" class="loading">
                    <div class="loading-spinner"></div>
                    <p>Analyzing market data for your location...</p>
                </div>
            `;
        }

        // Show error message
        function showError(message) {
            document.getElementById('content').innerHTML = `
                <div style="grid-column: 1 / -1;" class="error">
                    ❌ ${message}
                </div>
            `;
        }

        // Load on page load
        window.addEventListener('load', function() {
            // Try to auto-load if they've selected location before
            const location = document.getElementById('location').value;
            if (location) {
                getRecommendations();
            } else {
                document.getElementById('content').innerHTML = `
                    <div style="grid-column: 1 / -1;" class="info-box">
                        👋 Welcome to the Farmer Forecast Dashboard! Select your location above to get personalized oilseed recommendations.
                    </div>
                `;
            }
        });

        // Allow Enter key to submit
        document.addEventListener('keypress', function(event) {
            if (event.key === 'Enter') {
                getRecommendations();
            }
        });
    </script>
</body>
</html>
"""

def create_forecast_dashboard_routes(app):
    """
    Create Flask routes for enhanced forecast dashboard
    """
    
    @app.route('/forecast-dashboard-enhanced')
    def forecast_dashboard_enhanced_view():
        """Render enhanced forecast dashboard with real-time location-based features"""
        return render_template_string(ENHANCED_DASHBOARD_HTML)
    
    @app.route('/api/location-forecast-realtime/<location>')
    def location_forecast_realtime(location):
        """
        Real-time forecast data for a location
        Updates every time called with latest predictions
        """
        try:
            # Get all oilseed forecasts for the location
            oilseeds = ['groundnut', 'sunflower', 'soybean', 'mustard', 'coconut']
            forecasts = []
            
            for crop in oilseeds:
                forecast_data = engine.forecast_arima(crop, months_ahead=12, location=location)
                insights = engine.get_market_insights(crop, location=location)
                
                forecasts.append({
                    'crop': crop,
                    'location': location,
                    'forecast_prices': forecast_data['forecast'],
                    'historical_prices': forecast_data['historical'][-12:],  # Last 12 months
                    'lower_ci': forecast_data['lower_ci'],
                    'upper_ci': forecast_data['upper_ci'],
                    'current_price': float(forecast_data['historical'][-1]),
                    'avg_price': float(np.array(forecast_data['forecast']).mean()),
                    'price_trend': float((forecast_data['forecast'][-1] - forecast_data['forecast'][0]) / forecast_data['forecast'][0] * 100),
                    'location_multiplier': forecast_data['location_multiplier'],
                    'insights': insights
                })
            
            return jsonify({
                'status': 'success',
                'location': location,
                'timestamp': datetime.now().isoformat(),
                'forecasts': forecasts
            })
        
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500
    
    @app.route('/api/oilseed-comparison/<location>')
    def oilseed_comparison(location):
        """
        Compare all oilseeds for a specific location
        Shows time series and profitability
        """
        try:
            oilseeds = ['groundnut', 'sunflower', 'soybean', 'mustard', 'coconut']
            comparison = []
            
            for crop in oilseeds:
                forecast = engine.forecast_arima(crop, months_ahead=12, location=location)
                prices = np.array(forecast['forecast'])
                
                comparison.append({
                    'crop': crop,
                    'current_price': float(forecast['historical'][-1]),
                    'forecast_avg': float(prices.mean()),
                    'forecast_min': float(prices.min()),
                    'forecast_max': float(prices.max()),
                    'forecast_prices': forecast['forecast'],
                    'price_trend': float((prices[-1] - prices[0]) / prices[0] * 100),
                    'volatility': float(prices.std() / prices.mean() * 100),
                    'location_multiplier': forecast['location_multiplier'],
                    'suitable': crop in engine.oilseed_zones.get(location.lower(), [])
                })
            
            # Sort by forecast_avg price (high to low)
            comparison.sort(key=lambda x: x['forecast_avg'], reverse=True)
            
            return jsonify({
                'status': 'success',
                'location': location,
                'location_multiplier': engine.location_multipliers.get(location.lower(), 1.0),
                'comparison': comparison,
                'best_crop': comparison[0]['crop'] if comparison else None,
                'best_price': comparison[0]['forecast_avg'] if comparison else None
            })
        
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500
    
    @app.route('/api/timeseries-analysis/<crop>/<location>')
    def timeseries_analysis(crop, location):
        """
        Detailed time series analysis for one crop in one location
        Shows patterns, trends, seasonality
        """
        try:
            forecast_data = engine.forecast_arima(crop, months_ahead=12, location=location)
            insights = engine.get_market_insights(crop, location=location)
            
            historical = forecast_data['historical']
            forecast = forecast_data['forecast']
            
            # Calculate trend components
            recent_6m = np.array(historical[-6:])
            trend = (recent_6m[-1] - recent_6m[0]) / 6  # ₹ per month
            
            # Calculate seasonality strength
            std_dev = np.std(forecast)
            mean_val = np.mean(forecast)
            seasonality_strength = (std_dev / mean_val) * 100
            
            return jsonify({
                'status': 'success',
                'crop': crop,
                'location': location,
                'historical_prices': historical.tolist(),
                'forecast_prices': forecast,
                'lower_ci': forecast_data['lower_ci'],
                'upper_ci': forecast_data['upper_ci'],
                'current_price': float(historical[-1]),
                'avg_price': float(np.mean(forecast)),
                'trend_direction': 'UP' if trend > 0 else 'DOWN',
                'trend_magnitude': float(abs(trend)),  # ₹ per month
                'seasonality_strength': float(seasonality_strength),
                'volatility': float(np.std(forecast) / np.mean(forecast) * 100),
                'forecast_change_12m': float((forecast[-1] - forecast[0]) / forecast[0] * 100),
                'location_multiplier': forecast_data['location_multiplier'],
                'insights': insights
            })
        
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500


# Export function for use in main app
__all__ = ['ENHANCED_DASHBOARD_HTML', 'create_forecast_dashboard_routes']
