import numpy as np

import datetime as dt
from datetime import timedelta

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

#reflect database and tables
Base = automap_base()
Base.prepare(autoload_with=engine)

Station = Base.classes.station
Measurement = Base.classes.measurement

#flask
app = Flask(__name__)

                      
#routes

@app.route("/")
def welcome():
    """List all available routes."""
    return(
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/startdate<br/>"
        f"/api/v1.0/startdate/enddate"

    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)

    """list of dates and precipitation"""
    query = session.query(Measurement.date, Measurement.prcp).all()

    session.close()

    #dictionary for precipitation
    PRCP = []
    for date, prcp in query:
        date_prcp_dict = {}
        date_prcp_dict["date"] = date
        date_prcp_dict["prcp"] = prcp
        PRCP.append(date_prcp_dict)

    return jsonify(PRCP)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)

    """list of stations"""

    query = session.query(Station.station, Station.name).all()

    session.close()

    stations = []
    for station, name in query:
        stations_dict = {}
        stations_dict["station"] = station
        stations_dict["name"] = name
        stations.append(stations_dict)

    return jsonify(stations)




@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    """most active station"""

    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    date_query = (dt.datetime.strptime(last_date[0], "%Y-%m-%d") - dt.timedelta(days=365)).strftime('%Y-%m-%d')


    most_active = session.query(Measurement.station,func.count(Measurement.station)).\
        group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).first()
    
    
    result = session.query(Measurement.tobs).filter(Measurement.date >=date_query).filter(Measurement.station == most_active[0]).all()

    session.close()


    most_active_station = list(np.ravel(result))

    return jsonify(most_active_station)



@app.route("/api/v1.0/<start>")
def start_date(start):
    session = Session(engine)

    """list of the minimum temperature, the average temperature, and the maximum temperature for a specified start"""
    query = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).all()
    
    session.close()

    #create dictionary
    data = []
    for date, min, avg, max in query:
        data_dict = {}
        data_dict["Date"] = date
        data_dict["TMIN"] = min
        data_dict["TAVG"] = avg
        data_dict["TMAX"] = max
    data.append(data_dict)

    return jsonify(data)



@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    session = Session(engine)

    """list of the minimum temperature, the average temperature, and the maximum temperature for a specified start-end range."""
    query = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    
    session.close()

    data = []
    for min, avg, max in query:
        data_dict = {}
        data_dict["TMIN"] = min
        data_dict["TAVG"] = avg
        data_dict["TMAX"] = max
        data.append(data_dict)

    return jsonify(data)


if __name__ == '__main__':
    app.run(debug=True)
