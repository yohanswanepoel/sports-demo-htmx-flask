# app.py
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from icecream import ic
import random
import utils 
import json

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

if not os.getenv("DATABASE_URL"):
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
else:
    DB_URL = os.getenv("DATABASE_URL")
    DB_USER = os.getenv("DB_USER","username")
    DB_PASSWORD = os.getenv("DB_PASSWORD","password")
    app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_URL}/athlete_tracker'

# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Athlete(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    sport = db.Column(db.String(50), nullable=False)
    team = db.Column(db.String(100))
    performances = db.relationship('Performance', backref='athlete', lazy=True)

class Performance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    athlete_id = db.Column(db.Integer, db.ForeignKey('athlete.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    event_type = db.Column(db.String(50), nullable=False)
    result = db.Column(db.Float, nullable=False)
    notes = db.Column(db.Text)
    

@app.route('/')
def index():
    return render_template('base.html')

@app.route('/athletes')
def athletes():
    athletes = Athlete.query.all()
    return render_template('hx_athletes.html', athletes=athletes)

@app.route('/athlete/<int:id>')
def athlete_profile(id):
    athlete = Athlete.query.get_or_404(id)
    return render_template('hx_athlete_profile.html', athlete=athlete)

@app.route('/athlete_performance/<int:id>')
def athlete_performance(id):
    performances = db.session.query(Performance).filter(Performance.athlete_id == id)
    return render_template('hx_performance_list.html', performances=performances)

@app.route('/athlete_chart/<int:id>')
def athlete_charts(id):
    performances = db.session.query(Performance).filter(Performance.athlete_id == id).order_by(Performance.date.desc())
    labels, times = utils.generate_chart_data(performances)
    
    return render_template('hx_charts.html', labels=json.dumps(labels), times=json.dumps(times))

@app.route('/add_performance', methods=['POST'])
def add_performance():
    data = request.form
    athlete_id = data['athlete_id']
    new_performance = Performance(
        athlete_id=data['athlete_id'],
        event_type=data['event_type'],
        result=float(data['result']),
        notes=data.get('notes', '')
    )
    db.session.add(new_performance)
    db.session.commit()
    
    athlete = Athlete.query.get_or_404(athlete_id)
    return render_template('hx_athlete_profile.html', athlete=athlete)


utils.init_db(app, db, Athlete, Performance)
        
        
        
if __name__ == '__main__':
    app.run(host="0.0.0.0", port="8080")