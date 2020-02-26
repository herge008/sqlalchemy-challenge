# Import Dependencies
from flask import Flask, jsonify
import datetime as dt
import pandas as pd
import numpy as np
import sqlalchemy
from sqlalchemy import create_engine, func, inspect
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
import matplotlib.pyplot as plt
from matplotlib import style
style.use('fivethirtyeight')

# Setup DB
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
Measurement = Base.classes.measurement
Station = Base.classes.station

# Setup Flask
app = Flask(__name__)

# Routes
app = Flask(__name__)
@app.route("/")
def Home():
    return (
        "<h2>List of Paths</h2><ul><li>/api/v1.0/precipitation</li><li>/api/v1.0/stations</li><li>/api/v1.0/tobs</li><li>/api/v1.0/&lt;start&gt;</li><li>/api/v1.0/&lt;start&gt;/&lt;end&gt;</li></ul>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    result = session.query(Measurement.date, Measurement.prcp).all()
    session.close()

    dict_prcp = {}
    for date, time in result:
        dict_prcp[date] = time
    return jsonify(dict_prcp)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    result = session.query(Measurement.station).group_by(
        Measurement.station).all()
    session.close()

    ls_station = []
    for station in result:
        ls_station.append(station[0])
    return jsonify(ls_station)


@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    latest_date = session.query(Measurement.date).order_by(
        Measurement.date.desc()).first()
    latest_date = latest_date[0]
    latest_date = dt.datetime.strptime(latest_date, '%Y-%m-%d').date()
    result = session.query(Measurement.date, Measurement.tobs).filter(
        Measurement.date >= latest_date - dt.timedelta(days=365)).all()
    session.close()

    ls_tobs = []
    for tobs in result:
        ls_tobs.append(tobs[1])
    return jsonify(ls_tobs)


@app.route("/api/v1.0/<start>", defaults={'end': None})
@app.route("/api/v1.0/<start>/<end>")
def dates(start, end):
    if end == None:
        session = Session(engine)
        start = dt.datetime.strptime(start, "%Y-%m-%d").date()
        result = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(
            Measurement.tobs)).filter(Measurement.date >= start).all()
        session.close()

    else:
        session = Session(engine)
        start = dt.datetime.strptime(start, "%Y-%m-%d").date()
        end = dt.datetime.strptime(end, "%Y-%m-%d").date()
        result = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(
            Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
        session.close()

    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
