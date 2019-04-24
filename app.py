import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
import datetime as datetime



#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date<br/>"
        f"/api/v1.0/start_date/end_date<br/>"
    )


@app.route("/api/v1.0/precipitation")
def prcps():
    """Convert the query results to a Dictionary using date as the key and prcp as the value.
    Return the JSON representation of your dictionary."""
    # Query all prcps
    results = session.query(Measurement.date, Measurement.prcp).all()

    # Create a dictionary from the row data and append to a list of all_prcps
    all_prcps = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        all_prcps.append(prcp_dict)

    return jsonify(all_prcps)


@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations from the dataset."""
    # Query all stations
    results = session.query(Station.name).all()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    """Query for the dates and temperature observations from a year from the last data point.
    Return a JSON list of Temperature Observations (tobs) for the previous year."""
    # Query all tobs
    # max_date = measurement_df['date'].max()
    max_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    max_date = max_date[0]
    max_date_convert = datetime.datetime.strptime(max_date, "%Y-%m-%d")
    start_date_convert = max_date_convert - datetime.timedelta(weeks=52)
    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date > start_date_convert).all()

    # Convert list of tuples into normal list
    all_tobs = list(np.ravel(results))

    return jsonify(all_tobs)

@app.route("/api/v1.0/<start>")
def start(start=None):
    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start range.
    When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date."""
    # Query all min, avg, max temps
    results = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).group_by(Measurement.date).all()
    
    # Convert list of tuples into normal list
    all_start = list(np.ravel(results))

    return jsonify(all_start)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start=None, end=None):
    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start-end range.
    When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive."""
     # Query all min, avg, max temps
    results = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).group_by(Measurement.date).all()
    
    # Convert list of tuples into normal list
    all_start_end = list(np.ravel(results))

    return jsonify(all_start_end)


if __name__ == '__main__':
    app.run(debug=True)
