from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    full_name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    role = db.Column(db.String, nullable=False, default="user")
    
    reservations = db.relationship('ReserveParkingSpot', back_populates='user')

class Parking_Lot(db.Model):
    __tablename__ = "parkinglot"

    id = db.Column(db.Integer, primary_key=True)
    prime_location_name = db.Column(db.String, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    address = db.Column(db.String, nullable=False)
    pin_code = db.Column(db.Integer, nullable=False)
    max_spots = db.Column(db.Integer, default=100)
    is_active = db.Column(db.Boolean, default=True)

    spots = db.relationship('ParkingSpot', back_populates='lot', lazy=True)

class ParkingSpot(db.Model):
    __tablename__ = "parkingspot"

    id = db.Column(db.Integer, primary_key=True)
    lot_id = db.Column(db.Integer, db.ForeignKey('parkinglot.id'), nullable=False)
    status = db.Column(db.String(1), nullable=False, default='A')       # A = Available, O = Occupied
    customer_id = db.Column(db.Integer, nullable=True)
    vehicle_number = db.Column(db.String, nullable=True)
    date_time_of_parking = db.Column(db.DateTime, nullable=True)
    estimated_parking_cost = db.Column(db.Float, nullable=True)                            
                                                      
    lot = db.relationship('Parking_Lot', back_populates='spots')
    reservations = db.relationship('ReserveParkingSpot', back_populates='spot', cascade="all, delete-orphan")
class ReserveParkingSpot(db.Model):
    __tablename__ = "reservespot"

    id = db.Column(db.Integer, primary_key=True)
    spot_id = db.Column(db.Integer, db.ForeignKey('parkingspot.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    vehicle_number = db.Column(db.String, nullable=True) 
    parking_timestamp = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    leaving_timestamp = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now(), nullable=True)
    cost_per_unit = db.Column(db.Float, nullable=False)
    total_cost = db.Column(db.Float, nullable=True)
    status = db.Column(db.String(20), default='active')
    

    # Relationship
    user = db.relationship('User', back_populates='reservations')
    spot = db.relationship('ParkingSpot', back_populates='reservations')
   
