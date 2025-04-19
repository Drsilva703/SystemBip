from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from app import db

class Volume(db.Model):
    """Volume model representing a scanned barcode"""
    __tablename__ = 'volumes'
    
    id = Column(Integer, primary_key=True)
    barcode = Column(String(50), unique=True, nullable=False)
    branch_id = Column(String(10), nullable=False)
    order_id = Column(String(10), nullable=False) 
    volume_id = Column(String(10), nullable=False)
    scanned_at = Column(DateTime, default=datetime.utcnow)
    
    def __init__(self, barcode, branch_id, order_id, volume_id):
        self.barcode = barcode
        self.branch_id = branch_id
        self.order_id = order_id
        self.volume_id = volume_id
        
    def __repr__(self):
        return f"<Volume {self.barcode}>"

class BranchTotal(db.Model):
    """Model to store total volumes for each branch"""
    __tablename__ = 'branch_totals'
    
    id = Column(Integer, primary_key=True)
    branch_id = Column(String(10), unique=True, nullable=False)
    total_volumes = Column(Integer, nullable=False)
    
    def __init__(self, branch_id, total_volumes):
        self.branch_id = branch_id
        self.total_volumes = total_volumes
        
    def __repr__(self):
        return f"<BranchTotal {self.branch_id}: {self.total_volumes}>"