# -*- coding: utf-8 -*-
from icecream import ic
import random
import json
from datetime import datetime, timedelta

def init_db(app, db, Athlete, Performance):
    ic("creating db....")
    with app.app_context():
        db.create_all()
        
        # Add some sample data if the database is empty
        if not Athlete.query.first():
            athlete_list = ['John Doe', 'Jane Doe']
            for athlete in athlete_list: 
                sample_athlete = Athlete(
                    name=athlete,
                    sport='Track and Field',
                    team='City Athletics'
                )
                db.session.add(sample_athlete)
                
                note_list = ['Tail Wind', 'Wet Track', 'Sunny Day', 'Finals Race', 'Heavy Rain']
                
                
                for i in range(5):
                    result = round(random.uniform(10.5,11.5), 2)
                    notes = random.choice(note_list)
                    date=datetime.today() - timedelta(days=i)
                    # Add a sample performance
                    sample_performance = Performance(
                        athlete=sample_athlete,
                        event_type='sprint_100m',
                        result=result,
                        date=date,
                        notes=notes
                    )
                    
                    db.session.add(sample_performance)
                db.session.commit()
                
def generate_chart_data(performances):
    labels = []
    data = []
    for performance in performances:
        labels.append(performance.date.strftime("%Y-%m-%d") + " " + performance.notes)
        data.append(performance.result)
    
    return labels, data