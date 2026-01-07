from flask import Flask, render_template, request, flash, redirect, url_for, session
from model import db, User, Parking_Lot, ParkingSpot, ReserveParkingSpot 
from werkzeug.security import generate_password_hash, check_password_hash
import jinja2
from datetime import datetime
from sqlalchemy.orm import joinedload
import io, base64, matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # No GUI backend

app=Flask(__name__)


app.config['SECRET_KEY'] = 'your_secret_key'                              #password
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vehicleparking.db'     #path of db  
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False                    #hide errors 
#connect db with flask
db.init_app(app)

@app.route('/')
def home():
    return render_template('home.html')

def create_admin():
    with app.app_context():
        if not User.query.filter_by(role='admin').first():
            admin = User(username='gsharma',
                        full_name="Gayatri Sharma",  
                        email='21f3001157@ds.study.iitm.ac.in',  
                        password=generate_password_hash('admin'), 
                        role='admin')
            db.session.add(admin)
            db.session.commit()

def create_parking_lots():
    with app.app_context():
        if not Parking_Lot.query.first():
            lot1 = Parking_Lot(id=1, prime_location_name='Hi-Tech City', price=10, address='10, Knowledge City, Bio-diversity Signal, Hyderabad', pin_code=501506, max_spots=15)
            lot2 = Parking_Lot(id=2, prime_location_name='Kukattpally', price=15, address='234, Mahindra Ashvita, Hafeezzpet Road, Hyderabad', pin_code=501509, max_spots=10)
            db.session.add_all([lot1, lot2])
            db.session.commit()
        # Create parking spot for lot 2
            for lot in [lot1, lot2]:
                for _ in range(lot.max_spots):
                    spot = ParkingSpot(lot_id=lot.id, status='A')
                    db.session.add(spot)
            db.session.commit()
            # --- Manually set the first spot of lot1 as occupied ---
            spot = ParkingSpot.query.filter_by(lot_id=lot1.id).first()
            if spot:
                spot.status = 'O'
                db.session.commit()

@app.route('/admin-dashboard')
def admin_dashboard():
    # user_id=session.get('user_id')
    # if 'user_id' not in session:
    #     flash('Please log in as admin to access the dashboard.', 'warning')
    #     return redirect(url_for('admin_login'))
    # user = User.query.get(user_id)
    # admin=User.query.get(session['user_id'])
    lots=Parking_Lot.query.filter_by(is_active=True).all()
    return render_template('admin_dashboard.html',lots=lots)


@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        admin= User.query.filter_by(email=email, role='admin').first()

        if admin and check_password_hash(admin.password, password):
            # Successful login
            session['user_id'] = admin.id
            flash('Admin login successful!','success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid admin credentials')
            return render_template('admin_login.html')

    return render_template('admin_login.html')  # Show login form for GET


@app.route('/addlot', methods=['GET', 'POST'])
def add_lot():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    if not user or user.role != 'admin':
        flash("You don't have permission to add a parking lot.", "danger")
        return redirect(url_for('home'))

    if request.method == 'POST':

        prime_location_name=request.form['prime_location_name']
        address=request.form['address']
        pin_code=int(request.form['pin_code'])
        price=int(request.form['price'])
        max_spots=int(request.form['max_spots'])
        
        new_lot = Parking_Lot(
            prime_location_name=prime_location_name,
            address=address,
            pin_code=pin_code,
            price=price,
            max_spots=max_spots,
        )
        db.session.add(new_lot)
        db.session.commit()
    
        for _ in range(max_spots):
            spot = ParkingSpot(lot_id=new_lot.id, status='A')
            db.session.add(spot)
        db.session.commit()

        flash("New parking lot added successfully.", "success")
        return redirect(url_for('admin_dashboard'))
    
    return render_template('add_lot.html')

@app.route('/edit-lot/<int:lot_id>', methods=['GET', 'POST'])
def edit_lot(lot_id):
    parking_lot = Parking_Lot.query.get_or_404(lot_id)
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    if not user or user.role != 'admin':
        flash("You don't have permission to edit this parking lot.", "danger")
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        parking_lot.prime_location_name = request.form['prime_location_name']
        parking_lot.address = request.form['address']
        parking_lot.pin_code = int(request.form['pin_code'])
        parking_lot.price = int(request.form['price'])
        # Do not allow editing max_spots here unless you handle spot creation/deletion logic
        max_spots_raw = request.form.get('max_spots')
        if max_spots_raw:
            new_max_spots = int(max_spots_raw)
            current_spots = len(parking_lot.spots)
            parking_lot.max_spots = new_max_spots

            if new_max_spots > current_spots:
                # Add new spots
                for _ in range(new_max_spots - current_spots):
                    spot = ParkingSpot(lot_id=parking_lot.id, status='A')
                    db.session.add(spot)
            elif new_max_spots < current_spots:
                # Remove available spots only
                available_spots = [spot for spot in parking_lot.spots if spot.status == 'A']
                spots_to_remove = current_spots - new_max_spots
                if spots_to_remove > len(available_spots):
                    flash("Cannot reduce spots below the number of currently occupied spots.", "danger")
                    return redirect(url_for('edit_lot', lot_id=lot_id))
                for spot in available_spots[:spots_to_remove]:
                    db.session.delete(spot)
        db.session.commit()
        flash("Parking lot updated successfully.", "success")
        return redirect(url_for('admin_dashboard'))

    return render_template('edit_lot.html', lot=parking_lot)

@app.route('/delete-lot/<int:lot_id>', methods=['GET', 'POST'])
def delete_lot(lot_id):
    parking_lot = Parking_Lot.query.get_or_404(lot_id)
    user_id = session.get('user_id')
    user = User.query.get(user_id)

    # Permission check
    if not user or (user.role != 'admin' and parking_lot.user_id != 1):
        flash("You don't have permission to delete this parking lot.", "danger")
        return redirect(url_for('home'))

    # Block delete if there are any currently occupied spots
    occupied_spots = [spot for spot in parking_lot.spots if spot.status == 'O']

    if request.method == 'POST':
        if occupied_spots:
            flash("Cannot delete lot. It has occupied spots.", "warning")
            return redirect(url_for('admin_dashboard'))

        # Soft delete: Mark lot as inactive
        parking_lot.is_active = False
        db.session.commit()

        flash("Parking Lot has been disabled. Historical data is preserved.", "success")
        return redirect(url_for('admin_dashboard'))

    return render_template('delete_lot.html', lot=parking_lot, occupied_count=len(occupied_spots))

@app.route('/lot/<int:lot_id>/spots')
def lot_spot_details(lot_id):
    parking_lot = Parking_Lot.query.get_or_404(lot_id)
    return render_template('lot_spots.html', parking_lot=parking_lot)

@app.route('/spot/<int:spot_id>', methods=['GET', 'POST'])
def view_spot(spot_id):
    spot = ParkingSpot.query.get_or_404(spot_id)
    return render_template('view_spot.html', spot=spot)

@app.route('/spot/<int:spot_id>/details')
def occupied_spot_details(spot_id):
    spot = ParkingSpot.query.get_or_404(spot_id)
    if spot.status != 'O':
        return redirect(url_for('view_spot', spot_id=spot_id))
    return render_template('occupied_spot_details.html', spot=spot)

@app.route('/logout')
def logout():
    session.clear()
    return render_template('user_logout.html')

@app.route('/book_spot/<int:lot_id>', methods=['GET', 'POST'])
def book_spot(lot_id):
    lot = Parking_Lot.query.get_or_404(lot_id)
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    
    # Find the first available spot in this lot
    available_spot = ParkingSpot.query.filter_by(lot_id=lot_id, status='A').first()

    if request.method == 'POST':
        if not available_spot:
            flash("No available spots in this lot.", "danger")
            return redirect(url_for('user_dashboard'))

        vehicle_number = request.form.get('vehicle_number')
        # Mark the spot as occupied and record details
        available_spot.status = 'O'
        available_spot.customer_id = user.id
        available_spot.vehicle_number = vehicle_number
        available_spot.date_time_of_parking = datetime.now()

        reserve = ReserveParkingSpot(
            spot_id=available_spot.id,
            user_id=user.id,
            vehicle_number=vehicle_number,
            parking_timestamp=datetime.now(),
            cost_per_unit=lot.price,
            status='active'
        )
        db.session.add(reserve)
        db.session.commit()

        flash(f"Spot #{available_spot.id} booked successfully!", "success")
        return redirect(url_for('user_dashboard'))
    return render_template('book_spot.html', lot=lot, spot=available_spot, user=user, available=bool(available_spot))

@app.route('/release/<int:reserve_id>', methods=['GET','POST'])
def release_spot(reserve_id):
    reserve = ReserveParkingSpot.query.get_or_404(reserve_id)
    spot = ParkingSpot.query.get(reserve.spot_id)

    if reserve.status == 'inactive':
        flash("Spot already released.", "info")
        return redirect(url_for('user_dashboard'))

    reserve.leaving_timestamp = datetime.now()
    duration = (reserve.leaving_timestamp - reserve.parking_timestamp).total_seconds() / 60
    reserve.total_cost = round(duration * reserve.cost_per_unit, 2)
    reserve.status = 'inactive'

    if spot:
        spot.status = 'A'
        spot.customer_id = None
        spot.vehicle_number = None
        spot.date_time_of_parking = None

    db.session.commit()

    return redirect(url_for('release_confirmation', reserve_id=reserve.id))  # ✅ this line

@app.route('/release_confirmation/<int:reserve_id>')
def release_confirmation(reserve_id):
    reserve = ReserveParkingSpot.query.get_or_404(reserve_id)
    return render_template('release_spot.html', reserve=reserve)


@app.route('/users')
def users():
    users = User.query.filter(User.role != 'admin').all()
    # For each user, find the spot they are using (if any)
    user_histories = []
    for user in users:
        reservations = ReserveParkingSpot.query.filter_by(user_id=user.id).order_by(ReserveParkingSpot.parking_timestamp.desc()).all()
        user_histories.append({
            'user': user,
            'reservations': reservations
        })
    return render_template('user_details.html', user_histories=user_histories)

@app.route('/summary')
def summary():
    lots = Parking_Lot.query.all()
    lot_names = [lot.prime_location_name for lot in lots]
    total_spots = [lot.max_spots for lot in lots]
    occupied_spots = [len([spot for spot in lot.spots if spot.status == 'O']) for lot in lots]
    available_spots = [len([spot for spot in lot.spots if spot.status == 'A']) for lot in lots]

    # Create the bar chart
    fig, ax = plt.subplots(figsize=(8, 5))
    x = range(len(lot_names))
    ax.bar(x, total_spots, width=0.2, label='Total Spots', align='center')
    ax.bar([i + 0.2 for i in x], occupied_spots, width=0.2, label='Occupied', align='center', color='red')
    ax.bar([i + 0.4 for i in x], available_spots, width=0.2, label='Available', align='center', color='green')
    ax.set_xticks([i + 0.2 for i in x])
    ax.set_xticklabels(lot_names)
    ax.set_ylabel('Number of Spots')
    ax.set_title('Parking Lot Spot Summary')
    ax.legend()

    # Save plot to a PNG in memory
    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format='png')
    buf.seek(0)
    chart_data = base64.b64encode(buf.getvalue()).decode()
    plt.close(fig)

    return render_template('summary_admin.html', chart_data=chart_data)

@app.route('/user-register', methods=['GET','POST'])
def user_register():
    if request.method == 'POST':
        username = request.form['username']
        full_name = request.form['full_name']
        email = request.form['email']
        password = request.form['password']
        role = request.form.get('role', 'user')

        new_user = User(username=username,
                        email=email, 
                        full_name=full_name,
                        password=generate_password_hash(password), 
                        role=role)
        
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('user_login'))
    return render_template('user_register.html')

@app.route('/user-dashboard', methods=['GET', 'POST']) 
def user_dashboard():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    lots=Parking_Lot.query.filter_by(is_active=True).all()
    for lot in lots:
        lot.available = any(spot.status == 'A' for spot in lot.spots)
        
    vehicle_number = None
    query = ReserveParkingSpot.query.options(
        joinedload(ReserveParkingSpot.spot).joinedload(ParkingSpot.lot)
    ).filter_by(user_id=user_id)

    if request.method == 'POST':
        vehicle_number = request.form.get('vehicle_number')
        if vehicle_number:
            query = query.filter_by(vehicle_number=vehicle_number)
    parking_history = query.all()

    lot_names = []
    lot_counts = []
    lot_id_to_name = {lot.id: lot.prime_location_name for lot in lots}
    lot_booking_count = {}
    for record in parking_history:
        lot_name = lot_name = record.spot.lot.prime_location_name if record.spot and record.spot.lot else "N/A"
        lot_booking_count[lot_name] = lot_booking_count.get(lot_name, 0) + 1
    for lot_name, count in lot_booking_count.items():
        lot_names.append(lot_name)
        lot_counts.append(count)
    
    fig, ax = plt.subplots(figsize=(5, 3))
    ax.bar(lot_names, lot_counts, color="#42a5f5")
    ax.set_ylabel("Bookings")
    ax.set_xlabel("Parking Lot")
    ax.set_title("Your Bookings per Parking Lot")
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    chart_data = base64.b64encode(buf.getvalue()).decode()
    plt.close(fig)

    return render_template(
        'user_dashboard.html',
        lots=lots,
        parking_history=parking_history,
        user=user,
        vehicle_number=vehicle_number,
        chart_data=chart_data
    )

@app.route('/user-login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash('Login successful!', 'success')
            return redirect(url_for('user_dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('user_login.html')


with app.app_context():                                   #create and initialize DB
    db.create_all()


if __name__=='__main__':
    create_admin()
    create_parking_lots()
    app.run(debug=True)    