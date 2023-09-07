# Import the dependencies

import datetime as dt
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################

# reflect an existing database into a new model

# Create SQLAlchemy engine to connect to existing database
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Create a base for automapped classes
Base = automap_base()

# Reflect the database into the model
Base.prepare(engine, reflect=True)

# Access the reflected classes
measurement = Base.classes.measurement
station = Base.classes.station

if __name__ == "__main__":
    # Create a session
    session = Session(engine)

    # Run the app in debug mode
    app.run(debug=True)

#################################################
# Flask Setup
#################################################

from flask import Flask, jsonify

# Define the Flask app
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

# Define the homepage route
@app.route("/")
def home():
    return (
        "Welcome to the Climate App API for Homework Challenge 10!<br/><br/>"
        "Available Routes:<br/>"
        "/api/v1.0/precipitation<br/>"
        "/api/v1.0/stations<br/>"
        "/api/v1.0/tobs<br/>"
        "/api/v1.0/start<br/>"
        "/api/v1.0/start/end"
    )
# Define the precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create a session
    session = Session(engine)

    # Calculate the date one year ago from the most recent date in the database
    most_recent_date = session.query(func.max(measurement.date)).scalar()
    most_recent_date = datetime.strptime(most_recent_date, "%Y-%m-%d")
    one_year_ago = most_recent_date - timedelta(days=365)

    # Query for the last 12 months of temperature data
    results = session.query(measurement.date, measurement.prcp).filter(measurement.date >= one_year_ago).all()

    # Close the session
    session.close()

    # Create a dictionary with date as the key and precipitation as the value
    precipitation_data = {date: prcp for date, prcp in results}

    return jsonify(precipitation_data)

# Define the /api/v1.0/stations route
@app.route("/api/v1.0/stations")
def stations():
    # Create a session
    session = Session(engine)

    # Stations from the dataset
    results = session.query(Base.classes.station.station).all()

    # Convert the results to a list
    stations_list = [station[0] for station in results]

    # Close the session
    session.close()

    return jsonify(stations_list)

# Define the /api/v1.0/tobs route
@app.route("/api/v1.0/tobs")
def tobs():
    # Create a session
    session = Session(engine)

    # Find the most active station
    most_active_station = session.query(Base.classes.measurement.station).\
        group_by(Base.classes.measurement.station).\
        order_by(func.count(Base.classes.measurement.station).desc()).first()[0]

    # Calculate the date one year from the last date in the dataset
    most_recent_date = session.query(func.max(Base.classes.measurement.date)).scalar()
    one_year_ago = (dt.datetime.strptime(most_recent_date, "%Y-%m-%d") - dt.timedelta(days=365)).strftime("%Y-%m-%d")

    # Temperature observations for the most active station in the last 12 months
    results = session.query(Base.classes.measurement.date, Base.classes.measurement.tobs).\
        filter(Base.classes.measurement.station == most_active_station).\
        filter(Base.classes.measurement.date >= one_year_ago).all()

    # Close the session
    session.close()

    # Convert the results to a list of dictionaries
    tobs_list = [{"Date": date, "Temperature (F)": tobs} for date, tobs in results]

    return jsonify(tobs_list)

# Define the /api/v1.0/<start> and /api/v1.0/<start>/<end> routes
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def temperature_stats(start, end=None):
    # Create a session
    session = Session(engine)

    # Query the minimum, average, and maximum temperature for the specified date range
    if end:
        results = session.query(
            func.min(Base.classes.measurement.tobs),
            func.avg(Base.classes.measurement.tobs),
            func.max(Base.classes.measurement.tobs)
        ).\
        filter(Base.classes.measurement.date >= start).\
        filter(Base.classes.measurement.date <= end).all()
    else:
        results = session.query(
            func.min(Base.classes.measurement.tobs),
            func.avg(Base.classes.measurement.tobs),
            func.max(Base.classes.measurement.tobs)
        ).\
        filter(Base.classes.measurement.date >= start).all()

    # Close the session
    session.close()

    # Convert the results to a list of dictionaries
    temperature_stats_list = [{
        "Minimum Temperature (F)": result[0],
        "Average Temperature (F)": result[1],
        "Maximum Temperature (F)": result[2]
    } for result in results]

    return jsonify(temperature_stats_list)

