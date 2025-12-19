"""
FORECAST DASHBOARD - Frontend UI with Charts
Add this to app.py as a new route
"""

FORECAST_DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Market Forecast & Crop Recommendations</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
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
            background: white;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            margin-bottom: 30px;
            text-align: center;
        }
        .header h1 {
            color: #667eea;
            font-size: 32px;
            margin-bottom: 10px;
        }
        .header p {
            color: #666;
            font-size: 16px;
        }
        .controls {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }
        .control-group {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        .control-group label {
            display: block;
            font-weight: 600;
            color: #333;
            margin-bottom: 8px;
        }
        .control-group select,
        .control-group input {
            width: 100%;
            padding: 10px;
            border: 2px solid #e0e0e0;
            border-radius: 6px;
            font-size: 14px;
            transition: border-color 0.3s;
        }
        .control-group select:focus,
        .control-group input:focus {
            outline: none;
            border-color: #667eea;
        }
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 6px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }
        .btn:active {
            transform: translateY(0);
        }
        .dashboard {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 30px;
            margin-bottom: 30px;
        }
        .card {
            background: white;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        .card h2 {
            color: #667eea;
            font-size: 20px;
            margin-bottom: 20px;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }
        .chart-container {
            position: relative;
            height: 300px;
            margin-bottom: 20px;
        }
        .metrics {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
        }
        .metric {
            background: #f5f5f5;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }
        .metric-label {
            font-size: 12px;
            color: #999;
            text-transform: uppercase;
            font-weight: 600;
        }
        .metric-value {
            font-size: 22px;
            font-weight: 700;
            color: #667eea;
            margin-top: 5px;
        }
        .recommendation {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 15px;
        }
        .recommendation h3 {
            font-size: 18px;
            margin-bottom: 10px;
        }
        .recommendation p {
            font-size: 14px;
            opacity: 0.9;
        }
        .recommendation.success {
            background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
            color: #333;
        }
        .insight {
            background: #f0f4ff;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 10px;
            border-left: 4px solid #667eea;
        }
        .insight-title {
            font-weight: 600;
            color: #667eea;
            margin-bottom: 5px;
        }
        .insight-value {
            font-size: 14px;
            color: #555;
        }
        .tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            border-bottom: 2px solid #e0e0e0;
        }
        .tab-btn {
            background: none;
            border: none;
            padding: 12px 20px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            color: #999;
            border-bottom: 3px solid transparent;
            transition: all 0.3s;
        }
        .tab-btn.active {
            color: #667eea;
            border-bottom-color: #667eea;
        }
        .tab-content {
            display: none;
        }
        .tab-content.active {
            display: block;
        }
        .comparison-table {
            width: 100%;
            border-collapse: collapse;
        }
        .comparison-table th {
            background: #f5f5f5;
            padding: 12px;
            text-align: left;
            font-weight: 600;
            color: #333;
            border-bottom: 2px solid #ddd;
        }
        .comparison-table td {
            padding: 12px;
            border-bottom: 1px solid #eee;
        }
        .comparison-table tr:hover {
            background: #f9f9f9;
        }
        .comparison-table .crop-name {
            font-weight: 600;
            color: #667eea;
        }
        .loading {
            text-align: center;
            padding: 40px;
            color: #667eea;
            font-size: 18px;
        }
        .error {
            background: #ffebee;
            color: #c62828;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            display: none;
        }
        @media (max-width: 1000px) {
            .dashboard {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌾 Market Forecast & Crop Recommendations</h1>
            <p>ARIMA-based price predictions and oilseed shift recommendations</p>
        </div>

        <div class="error" id="errorMsg"></div>

        <!-- Controls -->
        <div class="controls">
            <div class="control-group">
                <label>Select Crop for Forecast:</label>
                <select id="cropSelect">
                    <option value="groundnut">Groundnut</option>
                    <option value="sunflower">Sunflower</option>
                    <option value="soybean">Soybean</option>
                    <option value="mustard">Mustard</option>
                    <option value="coconut">Coconut</option>
                </select>
            </div>
            <div class="control-group">
                <label>Your Current Crop:</label>
                <select id="currentCropSelect">
                    <option value="wheat">Wheat</option>
                    <option value="rice">Rice</option>
                    <option value="maize">Maize</option>
                    <option value="cotton">Cotton</option>
                </select>
            </div>
            <div class="control-group">
                <label>Land Area (acres):</label>
                <input type="number" id="areaInput" value="5" min="0.25" step="0.25">
            </div>
            <div class="control-group">
                <label>Cost per Acre (₹):</label>
                <input type="number" id="costInput" value="100000" min="10000" step="1000">
            </div>
            <div class="control-group" style="display: flex; align-items: flex-end;">
                <button class="btn" onclick="loadForecast()">📊 Load Forecast</button>
            </div>
        </div>

        <!-- Main Dashboard -->
        <div class="dashboard" id="dashboard" style="display: none;">
            <!-- Forecast Chart -->
            <div class="card">
                <h2>📈 Price Forecast (12 Months)</h2>
                <div class="chart-container">
                    <canvas id="forecastChart"></canvas>
                </div>
                <div class="tabs">
                    <button class="tab-btn active" onclick="switchTab(event, 'metrics')">Metrics</button>
                    <button class="tab-btn" onclick="switchTab(event, 'insights')">Insights</button>
                </div>
                <div id="metrics" class="tab-content active">
                    <div class="metrics">
                        <div class="metric">
                            <div class="metric-label">Current Price</div>
                            <div class="metric-value" id="currentPrice">-</div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">12-Month Avg</div>
                            <div class="metric-value" id="avgPrice">-</div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">Price Change</div>
                            <div class="metric-value" id="priceChange">-</div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">Volatility</div>
                            <div class="metric-value" id="volatility">-</div>
                        </div>
                    </div>
                </div>
                <div id="insights" class="tab-content">
                    <div id="insightsContent"></div>
                </div>
            </div>

            <!-- Recommendations -->
            <div class="card">
                <h2>🎯 Crop Shift Recommendations</h2>
                <div id="recommendationsContent"></div>
            </div>
        </div>

        <!-- Crop Comparison -->
        <div class="card" id="comparisonCard" style="display: none;">
            <h2>🌾 Oilseed Comparison</h2>
            <div class="chart-container">
                <canvas id="comparisonChart"></canvas>
            </div>
            <div style="margin-top: 30px;">
                <table class="comparison-table">
                    <thead>
                        <tr>
                            <th>Crop</th>
                            <th>Avg Price</th>
                            <th>Price Change</th>
                            <th>Est. Profit/Acre</th>
                            <th>Volatility</th>
                        </tr>
                    </thead>
                    <tbody id="comparisonTableBody">
                    </tbody>
                </table>
            </div>
        </div>

        <div id="loading" class="loading" style="display: none;">
            ⏳ Loading forecast data...
        </div>
    </div>

    <script>
        let forecastChart = null;
        let comparisonChart = null;

        async function loadForecast() {
            const crop = document.getElementById('cropSelect').value;
            const loading = document.getElementById('loading');
            const dashboard = document.getElementById('dashboard');
            const errorMsg = document.getElementById('errorMsg');

            loading.style.display = 'block';
            dashboard.style.display = 'none';
            errorMsg.style.display = 'none';

            try {
                // Get forecast
                const forecastRes = await fetch(`/api/forecast/${crop}`);
                const forecastData = await forecastRes.json();

                if (forecastData.status !== 'success') {
                    throw new Error(forecastData.error || 'Failed to load forecast');
                }

                // Get recommendations
                const currentCrop = document.getElementById('currentCropSelect').value;
                const area = parseFloat(document.getElementById('areaInput').value);
                const cost = parseFloat(document.getElementById('costInput').value);

                const recRes = await fetch('/api/recommend-crop-shift', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        current_crop: currentCrop,
                        area_acres: area,
                        cost_per_acre: cost
                    })
                });
                const recData = await recRes.json();

                // Get comparison
                const compRes = await fetch('/api/compare-crops', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        crops: ['groundnut', 'sunflower', 'soybean', 'mustard']
                    })
                });
                const compData = await compRes.json();

                // Update UI
                updateForecastChart(forecastData);
                updateMetrics(forecastData);
                updateInsights(forecastData.insights);
                updateRecommendations(recData, area);
                updateComparisonChart(compData.comparison);
                updateComparisonTable(compData.comparison);

                loading.style.display = 'none';
                dashboard.style.display = 'grid';
                document.getElementById('comparisonCard').style.display = 'block';

            } catch (error) {
                console.error('Error:', error);
                errorMsg.textContent = '❌ Error: ' + error.message;
                errorMsg.style.display = 'block';
                loading.style.display = 'none';
            }
        }

        function updateForecastChart(data) {
            const ctx = document.getElementById('forecastChart').getContext('2d');

            if (forecastChart) {
                forecastChart.destroy();
            }

            forecastChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.months.map(m => `Month ${m}`),
                    datasets: [{
                        label: `${data.crop.toUpperCase()} Price Forecast`,
                        data: data.forecast_prices,
                        borderColor: '#667eea',
                        backgroundColor: 'rgba(102, 126, 234, 0.1)',
                        tension: 0.4,
                        fill: true,
                        pointRadius: 4,
                        pointHoverRadius: 6,
                        pointBackgroundColor: '#667eea'
                    }, {
                        label: 'Upper CI (95%)',
                        data: data.confidence_upper,
                        borderColor: '#84fab0',
                        borderDash: [5, 5],
                        fill: false,
                        tension: 0.4,
                        pointRadius: 0
                    }, {
                        label: 'Lower CI (95%)',
                        data: data.confidence_lower,
                        borderColor: '#f5576c',
                        borderDash: [5, 5],
                        fill: false,
                        tension: 0.4,
                        pointRadius: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: true,
                            position: 'top'
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: false,
                            title: { display: true, text: 'Price (₹/quintal)' }
                        }
                    }
                }
            });
        }

        function updateMetrics(data) {
            const current = data.current_price;
            const avg = Math.round(data.insights.forecast_average);
            const change = data.insights.price_change_12m.toFixed(1);

            document.getElementById('currentPrice').textContent = `₹${current}`;
            document.getElementById('avgPrice').textContent = `₹${avg}`;
            document.getElementById('priceChange').textContent = `${change}%`;
            document.getElementById('volatility').textContent = `₹${data.insights.volatility.toFixed(0)}`;
        }

        function updateInsights(insights) {
            const content = `
                <div class="insight">
                    <div class="insight-title">Market Outlook</div>
                    <div class="insight-value">${insights.market_outlook}</div>
                </div>
                <div class="insight">
                    <div class="insight-title">Recommendation</div>
                    <div class="insight-value">${insights.recommendation}</div>
                </div>
                <div class="insight">
                    <div class="insight-title">Price Range</div>
                    <div class="insight-value">₹${insights.min_forecast_price.toFixed(0)} - ₹${insights.max_forecast_price.toFixed(0)}</div>
                </div>
            `;
            document.getElementById('insightsContent').innerHTML = content;
        }

        function updateRecommendations(data, area) {
            const topCrop = data.top_oilseed;
            if (!topCrop) return;

            const profitIncrease = ((topCrop.estimated_annual_profit - (topCrop.estimated_annual_profit * 0.3)) / (topCrop.estimated_annual_profit * 0.3) * 100).toFixed(0);

            const content = `
                <div class="recommendation success">
                    <h3>🌟 TOP RECOMMENDATION: ${topCrop.crop.toUpperCase()}</h3>
                    <p>Shift to this crop for maximum profit potential</p>
                </div>
                <div class="metrics">
                    <div class="metric">
                        <div class="metric-label">Est. Annual Profit</div>
                        <div class="metric-value">₹${(topCrop.estimated_annual_profit / 100000).toFixed(1)}L</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">Profit per Acre</div>
                        <div class="metric-value">₹${topCrop.profit_per_acre.toLocaleString()}</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">Avg Price (Next 12m)</div>
                        <div class="metric-value">₹${topCrop.avg_price_next_12m}</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">Price Trend</div>
                        <div class="metric-value">${topCrop.price_trend > 0 ? '📈' : '📉'} ${topCrop.price_trend.toFixed(1)}%</div>
                    </div>
                </div>
                <div style="margin-top: 20px; padding: 15px; background: #e3f2fd; border-radius: 8px;">
                    <strong>Other Recommendations:</strong>
                    ${data.recommendations.slice(1, 3).map(r => `
                        <div style="margin-top: 10px; padding: 10px; background: white; border-radius: 6px;">
                            <strong>${r.crop.toUpperCase()}</strong> - Est. Profit: ₹${(r.estimated_annual_profit / 100000).toFixed(1)}L
                        </div>
                    `).join('')}
                </div>
            `;
            document.getElementById('recommendationsContent').innerHTML = content;
        }

        function updateComparisonChart(comparison) {
            const crops = Object.keys(comparison);
            const profits = crops.map(c => {
                const price = comparison[c].avg_price;
                return price * 18 * 5 / 100 - 100000; // Rough estimate
            });

            const ctx = document.getElementById('comparisonChart').getContext('2d');

            if (comparisonChart) {
                comparisonChart.destroy();
            }

            comparisonChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: crops.map(c => c.toUpperCase()),
                    datasets: [{
                        label: 'Avg Price (₹/quintal)',
                        data: crops.map(c => comparison[c].avg_price),
                        backgroundColor: '#667eea',
                        borderRadius: 8
                    }, {
                        label: 'Price Growth (%)',
                        data: crops.map(c => comparison[c].price_growth),
                        backgroundColor: '#764ba2',
                        borderRadius: 8,
                        yAxisID: 'y1'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: { beginAtZero: true },
                        y1: {
                            type: 'linear',
                            position: 'right',
                            beginAtZero: true
                        }
                    },
                    plugins: {
                        legend: { position: 'top' }
                    }
                }
            });
        }

        function updateComparisonTable(comparison) {
            const tbody = document.getElementById('comparisonTableBody');
            tbody.innerHTML = Object.entries(comparison).map(([crop, data]) => `
                <tr>
                    <td class="crop-name">${crop.toUpperCase()}</td>
                    <td>₹${data.avg_price.toFixed(0)}</td>
                    <td>${data.price_growth > 0 ? '📈' : '📉'} ${data.price_growth.toFixed(1)}%</td>
                    <td>₹${((data.avg_price * 18 * 5 / 100) - 100000).toFixed(0)}</td>
                    <td>₹${data.volatility.toFixed(0)}</td>
                </tr>
            `).join('');
        }

        function switchTab(e, tabName) {
            // Hide all tabs
            document.querySelectorAll('.tab-content').forEach(tab => {
                tab.classList.remove('active');
            });
            document.querySelectorAll('.tab-btn').forEach(btn => {
                btn.classList.remove('active');
            });

            // Show selected tab
            document.getElementById(tabName).classList.add('active');
            e.target.classList.add('active');
        }

        // Load forecast on page load
        window.addEventListener('load', () => {
            loadForecast();
        });
    </script>
</body>
</html>
"""
