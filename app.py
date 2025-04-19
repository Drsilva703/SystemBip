import os
import logging
from flask import Flask, render_template, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Database setup
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# Configure database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize database
db.init_app(app)

@app.route('/')
def index():
    """Render the main application page"""
    return render_template('index.html')

# API endpoints
@app.route('/api/volumes', methods=['GET'])
def get_volumes():
    """Get all volumes from database"""
    from models import Volume
    volumes = Volume.query.all()
    result = []
    for volume in volumes:
        result.append({
            'id': volume.id,
            'barcode': volume.barcode,
            'branchId': volume.branch_id,
            'orderId': volume.order_id,
            'volumeId': volume.volume_id,
            'scannedAt': volume.scanned_at.isoformat()
        })
    return jsonify(result)

@app.route('/api/volumes', methods=['POST'])
def add_volume():
    """Add a new volume to database"""
    from models import Volume
    data = request.json
    
    # Check if volume already exists
    existing = Volume.query.filter_by(barcode=data['barcode']).first()
    if existing:
        return jsonify({'success': False, 'message': 'Volume já existe', 'isDuplicate': True}), 400
    
    # Create new volume
    volume = Volume(
        barcode=data['barcode'],
        branch_id=data['branchId'],
        order_id=data['orderId'],
        volume_id=data['volumeId']
    )
    
    db.session.add(volume)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'id': volume.id,
        'scannedAt': volume.scanned_at.isoformat()
    })

@app.route('/api/volumes/<barcode>', methods=['DELETE'])
def delete_volume(barcode):
    """Delete a volume from database"""
    from models import Volume
    volume = Volume.query.filter_by(barcode=barcode).first()
    
    if not volume:
        return jsonify({'success': False, 'message': 'Volume não encontrado'}), 404
    
    db.session.delete(volume)
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/api/volumes/clear', methods=['DELETE'])
def clear_volumes():
    """Clear all volumes from database"""
    from models import Volume, BranchTotal
    
    Volume.query.delete()
    BranchTotal.query.delete()
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/api/branches/total', methods=['POST'])
def set_branch_total():
    """Set total volume count for a branch"""
    from models import BranchTotal
    data = request.json
    
    # Check if branch total already exists
    branch_total = BranchTotal.query.filter_by(branch_id=data['branchId']).first()
    
    if branch_total:
        branch_total.total_volumes = data['totalVolumes']
    else:
        branch_total = BranchTotal(
            branch_id=data['branchId'],
            total_volumes=data['totalVolumes']
        )
        db.session.add(branch_total)
    
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/api/branches/total/<branch_id>', methods=['GET'])
def get_branch_total(branch_id):
    """Get total volume count for a branch"""
    from models import BranchTotal
    branch_total = BranchTotal.query.filter_by(branch_id=branch_id).first()
    
    if not branch_total:
        return jsonify({'success': False, 'totalVolumes': None}), 404
    
    return jsonify({
        'success': True,
        'branchId': branch_total.branch_id,
        'totalVolumes': branch_total.total_volumes
    })

# Initialize database and create tables
with app.app_context():
    # Import models to register with SQLAlchemy
    import models
    db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
