from flask import Blueprint, render_template, session, redirect, url_for, jsonify, request
from extensions import db
from models import Scheme, SubsidyApplication, Farmer

subsidies_bp = Blueprint("subsidies", __name__, url_prefix="/subsidies")


@subsidies_bp.route("/list")
def subsidies_list():
    """Display list of all subsidies and schemes"""
    if "farmer_id_verified" not in session:
        return redirect(url_for("auth.login"))
    
    return render_template("subsidies_list.html")


@subsidies_bp.route("/api/list")
def api_subsidies_list():
    """API endpoint to get all active schemes/subsidies as JSON"""
    if "farmer_id_verified" not in session:
        return jsonify({"error": "Not logged in"}), 401
    
    schemes = Scheme.query.filter_by(is_active=True).all()
    
    return jsonify([scheme.to_dict() for scheme in schemes])


@subsidies_bp.route("/api/recommended")
def api_subsidies_recommended():
    """API endpoint to get recommended schemes for the farmer"""
    if "farmer_id_verified" not in session:
        return jsonify({"error": "Not logged in"}), 401
    
    schemes = Scheme.query.filter_by(is_active=True, is_recommended=True).all()
    
    return jsonify([scheme.to_dict() for scheme in schemes])


@subsidies_bp.route("/detail/<scheme_id>")
def subsidies_detail(scheme_id):
    """Display details of a specific subsidy"""
    if "farmer_id_verified" not in session:
        return redirect(url_for("auth.login"))
    
    scheme = Scheme.query.get_or_404(scheme_id)
    
    return render_template("subsidies_detail.html", scheme_id=scheme_id)


@subsidies_bp.route("/api/detail/<scheme_id>")
def api_subsidies_detail(scheme_id):
    """API endpoint to get subsidy details as JSON"""
    if "farmer_id_verified" not in session:
        return jsonify({"error": "Not logged in"}), 401
    
    scheme = Scheme.query.get_or_404(scheme_id)
    
    return jsonify(scheme.to_dict())


@subsidies_bp.route("/api/apply/<scheme_id>", methods=["POST"])
def api_apply_scheme(scheme_id):
    """API endpoint to apply for a scheme"""
    if "farmer_id_verified" not in session:
        return jsonify({"error": "Not logged in"}), 401
    
    farmer_id = session["farmer_id_verified"]
    scheme = Scheme.query.get_or_404(scheme_id)
    
    # Create subsidy application
    application = SubsidyApplication(
        farmer_id=farmer_id,
        scheme_id=scheme_id,
        status="Applied",
        application_data=request.get_json().get("data", "{}")
    )
    
    db.session.add(application)
    db.session.commit()
    
    return jsonify({
        "success": True,
        "application_id": application.id,
        "message": f"Successfully applied for {scheme.name}"
    }), 201


@subsidies_bp.route("/api/my-applications")
def api_my_applications():
    """API endpoint to get farmer's subsidy applications"""
    if "farmer_id_verified" not in session:
        return jsonify({"error": "Not logged in"}), 401
    
    farmer_id = session["farmer_id_verified"]
    applications = SubsidyApplication.query.filter_by(farmer_id=farmer_id).all()
    
    result = []
    for app in applications:
        result.append({
            'id': app.id,
            'scheme_id': app.scheme_id,
            'scheme_name': app.scheme.name if app.scheme else 'Unknown',
            'status': app.status,
            'application_date': app.application_date.isoformat() if app.application_date else None,
            'approved_amount': app.approved_amount,
            'approval_date': app.approval_date.isoformat() if app.approval_date else None
        })
    
    return jsonify(result)
