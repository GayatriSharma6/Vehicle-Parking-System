# 🚗 Reliable Spaces — Smart Parking Reservation System

A full-stack web application designed to reserve and manage parking spots for four-wheelers in high-traffic zones, enabling real-time tracking, analytics, and efficient parking lot operations.

---

## 📌 Problem Statement
Urban areas face inefficient parking utilization due to lack of real-time visibility and data-driven decision making. **Reliable Spaces** addresses this by enabling seamless parking reservations and operational analytics for administrators.

---

## 🎯 Key Features

### 👤 User Features
- User registration and secure login
- View available parking lots and parking spots
- Reserve and release parking spots
- Secure session management

### 🛠️ Admin Features
- Add, edit, and delete parking lots
- Manage parking spot details
- View parking usage summaries
- Analyze parking utilization and profitability

### 📊 Analytics
- Server-side analytical charts
- Visual summaries using Matplotlib
- Supports data-driven operational decisions

---

## 🧱 Tech Stack

- **Backend:** Python 3.x, Flask  
- **Database:** Flask-SQLAlchemy (ORM)  
- **Frontend:** HTML5, CSS3, Bootstrap 5  
- **Templating:** Jinja2  
- **Analytics:** Matplotlib  

---

## 🏗️ Architecture Overview

- **app.py** — Application logic and routing  
- **model.py** — Database models (ORM)  
- **templates/** — Jinja2 HTML templates  
- **static/** — CSS and images  
- **database.db** — SQLite database


The application follows a modular Flask architecture, ensuring clean separation of backend logic, database models, and frontend presentation for scalability and maintainability.

---

## 🗄️ Database Schema & Relationships

- **User ↔ ReserveParkingSpot:** One-to-Many  
- **Parking Lot ↔ Parking Spot:** One-to-Many  
- **Parking Spot ↔ ReserveParkingSpot:** One-to-Many  

### Design Considerations
- Normalized schema to avoid redundancy
- Foreign key constraints for data integrity
- Encrypted storage of sensitive data
- Flexible schema to support reserved and walk-in parking

---

## ▶️ Demo Video

📽️ Application Walkthrough:  
https://drive.google.com/file/d/1JmEXImfCwpLxELtRiFJWIsVW_5adenOm/view

---

## 🚀 Future Enhancements
- Real-time parking availability
- Advanced analytics dashboards
- Payment gateway integration
- Improved mobile responsiveness

---

## 🧪 Skills Demonstrated
- Full-stack web development
- Backend system design
- Database modeling with ORM
- Analytics and data visualization
- Operations-focused application design

---

## 📄 License
This project is intended for academic and demonstration purposes.
