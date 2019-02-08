# Step 2: Climate App
# Use and setup FLASK to create routes
# Dependencies 
import numpy as np
import pandas as pd
import datetime as dt
from flask import Flask, jsonify


app = Flask(__name__)

# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# We can view all of the classes that automap found
Base.classes.keys()

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)




# Create routes
# Home page
@app.route("/")
def home():
    # List all routes that are available
    print("Server received request for 'Home' page")
    return (
        f"Welcome to my Climate API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end<br/>"
        )

#/api/v1.0/precipitation`
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Convert the query results to a Dictionary using `date` as the key and `prcp` as the value.
    # Return the JSON representation of your dictionary.
	# Perform a query to retrieve the data and precipitation scores
	df = session.query(Measurement.date,Measurement.prcp).\
	    filter(Measurement.date >= "2016-08-23").all()

	# Save the query results as a Pandas DataFrame and set the index to the date column
	df = pd.DataFrame(df, columns=['Date', 'Precipitation'])
	df.set_index('Date', inplace=True)

	# Sort the dataframe by date
	df.sort_values(by='Date')

	return jsonify(df.to_dict())

# * `/api/v1.0/stations`
@app.route("/api/v1.0/stations")
def stations():
    # Return a JSON list of stations from the dataset.
    stations = session.query(Measurement.station).\
    group_by(Measurement.station).all()
                  
    return jsonify(stations)

# * `/api/v1.0/tobs`
@app.route("/api/v1.0/tobs")
def tobs():
# * query for the dates and temperature observations from a year from the last data point.
# * Return a JSON list of Temperature Observations (tobs) for the previous year.
    tobs = session.query(Measurement.date,Measurement.tobs).\
    filter(Measurement.station == "USC00519281").\
    filter(Measurement.date > "2016-08-23").all()
                    
    return jsonify(tobs)

# * `/api/v1.0/<start>` 
@app.route("/api/v1.0/<start>")
def start():
# * Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
# * When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates between the start and end date inclusive.
	def calc_temps(start):

		return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).all()

	return jsonify(calc_temps(start))


# * `/api/v1.0/<start>/<end>`
@app.route("/api/v1.0/<start>/<end>")
def startandend():
# * Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
# * When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates between the start and end date inclusive.
	def calc_temps(start, end):

		return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()

	return jsonify(calc_temps(start, end))


# Main behavior
if __name__ == "__main__":
    app.run(debug=True)    