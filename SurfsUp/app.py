# Import the dependencies.
import numpy as np
import datetime as dt
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################

# Create engine using the `hawaii.sqlite` database file
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# Declare a Base using `automap_base()`
Base = automap_base()
# Use the Base class to reflect the database tables
Base.prepare(autoload_with=engine)

# Assign the measurement class to a variable called `Measurement` and
# the station class to a variable called `Station`
measurement = Base.classes['measurement']
station = Base.classes["station"]

# Create a session
session = Session(engine)


#################################################
# Flask Setup
#################################################

app = Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route('/')
def home():
    return (
        f"Welcome to the Climate Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;"
    )

# Define the precipitation route
@app.route('/api/v1.0/precipitation')
def precipitation():
    # Calculate the date one year from the last date in the dataset.
    one_year_ago = dt.date(*map(int, most_recent_date[0].split('-'))) - dt.timedelta(days=365)

    # Query precipitation data for the last 12 months
    precipitation_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_ago).all()

    # Convert the query results to a dictionary
    precipitation_dict = {date: prcp for date, prcp in precipitation_data}

    return jsonify(precipitation_dict)

# Define the stations route
@app.route('/api/v1.0/stations')
def stations():
    # Query all stations from the dataset
    stations_data = session.query(Station.station).all()

    # Convert the query results to a list
    stations_list = [station[0] for station in stations_data]

    return jsonify(stations_list)

# Define the tobs route
@app.route('/api/v1.0/tobs')
def tobs():
    # Query temperature observations for the most active station in the last 12 months
    temperature_data = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= one_year_ago).all()

    # Convert the query results to a list of dictionaries
    temperature_list = [{'date': date, 'temperature': tobs} for date, tobs in temperature_data]

    return jsonify(temperature_list)

# Define the start and start/end routes
@app.route('/api/v1.0/<start>')
@app.route('/api/v1.0/<start>/<end>')
def temperature_stats(start, end=None):
    # Query temperature statistics based on start and end dates
    if end:
        temperature_stats_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    else:
        temperature_stats_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start).all()

    # Convert the query results to a list of dictionaries
    temperature_stats_list = [{'min_temperature': stats[0], 'avg_temperature': stats[1], 'max_temperature': stats[2]} for stats in temperature_stats_data]

    return jsonify(temperature_stats_list)

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
