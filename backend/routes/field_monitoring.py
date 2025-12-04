from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from extensions import db
from models import Farmer, IoTDevice, DeviceRequest, SensorReading
from datetime import datetime

fm_bp = Blueprint('field_monitoring', __name__, url_prefix='/field-monitoring')


@fm_bp.route('/')
def dashboard():
    if 'farmer_id_verified' not in session:
        return redirect(url_for('auth.login'))
    # Build initial status to render server-side and avoid a perpetual loading state
    farmer_id = session['farmer_id_verified']
    device = IoTDevice.query.filter_by(farmer_id=farmer_id).first()
    request_rec = DeviceRequest.query.filter_by(farmer_id=farmer_id).order_by(DeviceRequest.created_at.desc()).first()

    init = {
        'has_device': bool(device and device.installed),
        'device': None,
        'last_request': None,
        'readings': []
    }
    if device:
        init['device'] = {
            'id': device.id,
            'serial': device.device_serial,
            'installed': device.installed,
            'installed_at': device.installed_at.isoformat() if device.installed_at else None,
            'location': device.location_description
        }
        if device.installed:
            readings = SensorReading.query.filter_by(device_id=device.id).order_by(SensorReading.received_at.desc()).limit(48).all()
            init['readings'] = [
                {
                    'temperature': r.temperature,
                    'humidity': r.humidity,
                    'soil_moisture': r.soil_moisture,
                    'light': r.light,
                    'probe_temp': r.probe_temp,
                    'received_at': r.received_at.isoformat()
                } for r in readings
            ]

    if request_rec:
        init['last_request'] = {
            'id': request_rec.id,
            'status': request_rec.status,
            'created_at': request_rec.created_at.isoformat()
        }

    return render_template('field_monitoring.html', init=init)


@fm_bp.route('/api/status')
def api_status():
    if 'farmer_id_verified' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    farmer_id = session['farmer_id_verified']

    device = IoTDevice.query.filter_by(farmer_id=farmer_id).first()
    request_rec = DeviceRequest.query.filter_by(farmer_id=farmer_id).order_by(DeviceRequest.created_at.desc()).first()

    status = {
        'has_device': bool(device and device.installed),
        'device': {
            'id': device.id if device else None,
            'serial': device.device_serial if device else None,
            'installed': device.installed if device else False,
            'installed_at': device.installed_at.isoformat() if device and device.installed_at else None,
            'location': device.location_description if device else None
        } if device else None,
        'last_request': {
            'id': request_rec.id,
            'status': request_rec.status,
            'created_at': request_rec.created_at.isoformat()
        } if request_rec else None
    }
    return jsonify(status)


@fm_bp.route('/api/apply', methods=['POST'])
def api_apply():
    if 'farmer_id_verified' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    farmer_id = session['farmer_id_verified']
    data = request.json or {}
    notes = data.get('notes')

    req = DeviceRequest(farmer_id=farmer_id, notes=notes, status='pending')
    db.session.add(req)
    db.session.commit()

    return jsonify({'success': True, 'request_id': req.id})


def analyze_field_status(readings, farmer):
    """Analyze sensor readings and return field status with recommendations."""
    if not readings:
        return {
            'overall_status': 'No Data',
            'status_color': '#999',
            'metrics': {},
            'recommendations': ['Waiting for sensor data...']
        }
    
    # Get latest reading
    latest = readings[0]
    
    # Calculate averages over last 48 readings
    temps = [r.temperature for r in readings if r.temperature is not None]
    hums = [r.humidity for r in readings if r.humidity is not None]
    soils = [r.soil_moisture for r in readings if r.soil_moisture is not None]
    lights = [r.light for r in readings if r.light is not None]
    
    avg_temp = sum(temps) / len(temps) if temps else None
    avg_hum = sum(hums) / len(hums) if hums else None
    avg_soil = sum(soils) / len(soils) if soils else None
    avg_light = sum(lights) / len(lights) if lights else None
    
    recommendations = []
    issues = []
    
    # Soil Moisture Analysis (critical for oilseeds)
    if avg_soil is not None:
        if avg_soil < 30:
            issues.append('Low Soil Moisture')
            recommendations.append('🚨 Soil is dry! Irrigation needed. Check your water supply.')
        elif avg_soil > 80:
            issues.append('High Soil Moisture')
            recommendations.append('⚠️ Soil moisture is high. Ensure proper drainage to prevent root rot.')
        else:
            recommendations.append('✓ Soil moisture is optimal for growth.')
    
    # Temperature Analysis (oilseeds prefer 20-30°C)
    if avg_temp is not None:
        if avg_temp < 15:
            issues.append('Low Temperature')
            recommendations.append('⚠️ Temperature is low. Growth may slow down.')
        elif avg_temp > 35:
            issues.append('High Temperature')
            recommendations.append('⚠️ Temperature is high. Ensure adequate water supply to prevent stress.')
        else:
            recommendations.append('✓ Temperature range is good for crop growth.')
    
    # Humidity Analysis
    if avg_hum is not None:
        if avg_hum < 30:
            recommendations.append('⚠️ Low humidity. May increase evaporation—ensure regular watering.')
        elif avg_hum > 85:
            recommendations.append('⚠️ High humidity. Watch for fungal diseases. Ensure good ventilation.')
        else:
            recommendations.append('✓ Humidity levels are healthy.')
    
    # Light Analysis
    if avg_light is not None:
        if avg_light < 300:  # Assuming 0-1023 range
            recommendations.append('⚠️ Low light levels. Consider weather patterns and pruning if needed.')
        else:
            recommendations.append('✓ Light exposure is sufficient for photosynthesis.')
    
    # Overall status
    if len(issues) == 0:
        overall_status = 'Healthy'
        status_color = '#27ae60'  # Green
    elif len(issues) == 1:
        overall_status = 'Caution'
        status_color = '#f39c12'  # Orange
    else:
        overall_status = 'Attention Needed'
        status_color = '#e74c3c'  # Red
    
    return {
        'overall_status': overall_status,
        'status_color': status_color,
        'metrics': {
            'temperature': f'{avg_temp:.1f}°C' if avg_temp else '-',
            'humidity': f'{avg_hum:.0f}%' if avg_hum else '-',
            'soil_moisture': f'{avg_soil:.0f}%' if avg_soil else '-',
            'light': f'{avg_light:.0f}' if avg_light else '-'
        },
        'issues': issues,
        'recommendations': recommendations
    }


@fm_bp.route('/api/readings')
def api_readings():
    """Return the latest 48 readings with field status analysis."""
    if 'farmer_id_verified' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    farmer_id = session['farmer_id_verified']

    farmer = Farmer.query.get(farmer_id)
    device = IoTDevice.query.filter_by(farmer_id=farmer_id, installed=True).first()
    if not device:
        return jsonify({'error': 'No installed device'}), 404

    readings = SensorReading.query.filter_by(device_id=device.id).order_by(SensorReading.received_at.desc()).limit(48).all()
    out = [
        {
            'temperature': r.temperature,
            'humidity': r.humidity,
            'soil_moisture': r.soil_moisture,
            'light': r.light,
            'probe_temp': r.probe_temp,
            'received_at': r.received_at.isoformat()
        } for r in readings
    ]
    
    # Get field status analysis
    status = analyze_field_status(readings, farmer)
    
    return jsonify({
        'device': {'id': device.id, 'serial': device.device_serial}, 
        'readings': out,
        'field_status': status
    })


@fm_bp.route('/api/push', methods=['POST'])
def api_push():
    """Endpoint for IoT device to push readings (simple auth omitted here)."""
    data = request.json or {}
    serial = data.get('device_serial')
    if not serial:
        return jsonify({'error': 'missing serial'}), 400
    device = IoTDevice.query.filter_by(device_serial=serial).first()
    if not device:
        return jsonify({'error': 'device not found'}), 404

    r = SensorReading(
        device_id=device.id,
        temperature=data.get('temperature'),
        humidity=data.get('humidity'),
        soil_moisture=data.get('soil_moisture'),
        light=data.get('light'),
        probe_temp=data.get('probe_temp')
    )
    db.session.add(r)
    db.session.commit()
    return jsonify({'success': True})
