from flask import Blueprint, render_template, jsonify, session
from datetime import datetime, timedelta
import random
from models import Farmer

weather_bp = Blueprint('weather', __name__, url_prefix='/weather')


@weather_bp.route('/')
def dashboard():
    # simple page; JS will fetch forecast
    if 'farmer_id_verified' not in session:
        from flask import redirect, url_for
        return redirect(url_for('auth.login'))
    return render_template('weather.html')


def generate_forecast_for_location(district=None, lat=None, lon=None, days=7):
    """
    Stub weather forecast generator.
    Uses deterministic randomness seeded from district or lat/lon to create plausible day forecasts.
    Returns a list of days with date, summary, temp_min, temp_max, precipitation_mm, wind_kmh.
    """
    seed_val = 0
    if district:
        seed_val = sum(ord(c) for c in district)
    elif lat and lon:
        seed_val = int((abs(lat) + abs(lon)) * 1000)
    else:
        seed_val = int(datetime.utcnow().timestamp())

    rnd = random.Random(seed_val)
    out = []
    today = datetime.utcnow().date()
    for i in range(days):
        d = today + timedelta(days=i)
        # base temps vary mildly
        base = 25 + (rnd.random() * 8 - 2)
        tmax = round(base + rnd.uniform(2, 6), 1)
        tmin = round(base - rnd.uniform(2, 6), 1)
        precip_chance = rnd.random()
        if precip_chance > 0.8:
            summary = 'Heavy rain'
            precip = round(rnd.uniform(10, 60),1)
        elif precip_chance > 0.6:
            summary = 'Light rain'
            precip = round(rnd.uniform(1, 10),1)
        elif precip_chance > 0.4:
            summary = 'Cloudy'
            precip = 0.0
        else:
            summary = 'Sunny'
            precip = 0.0
        wind = round(rnd.uniform(5, 25),1)
        out.append({
            'date': d.isoformat(),
            'summary': summary,
            'temp_min': tmin,
            'temp_max': tmax,
            'precip_mm': precip,
            'wind_kmh': wind
        })
    return out


@weather_bp.route('/api/forecast')
def api_forecast():
    if 'farmer_id_verified' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    farmer_id = session['farmer_id_verified']
    farmer = Farmer.query.filter_by(id=farmer_id).first()
    district = None
    if farmer:
        district = getattr(farmer, 'district', None)

    forecast = generate_forecast_for_location(district=district, lat=None, lon=None, days=7)
    return jsonify({'location': district or 'your area', 'forecast': forecast})
