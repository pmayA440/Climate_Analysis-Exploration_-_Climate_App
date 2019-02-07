
# coding: utf-8

# In[1]:


get_ipython().run_line_magic('matplotlib', 'inline')
from matplotlib import style
style.use('fivethirtyeight')
import matplotlib.pyplot as plt


# In[2]:


import numpy as np
import pandas as pd


# In[3]:


import datetime as dt


# # Reflect Tables into SQLAlchemy ORM

# In[4]:


# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect


# In[7]:


engine = create_engine("sqlite:///hawaii.sqlite")


# In[8]:


# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)


# In[9]:


# We can view all of the classes that automap found
Base.classes.keys()


# In[10]:


# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station


# In[11]:


# Create our session (link) from Python to the DB
session = Session(engine)


# # Exploratory Climate Analysis

# In[12]:


inspector = inspect(engine)
columns = inspector.get_columns('measurement')
for c in columns:
    print(c['name'], c["type"])


# In[13]:


# Design a query to retrieve the last 12 months of precipitation data and plot the results
# Calculate the date 1 year ago from the last data point in the database
Last_Date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
Last_Date


# In[16]:


# Perform a query to retrieve the data and precipitation scores
df = session.query(Measurement.date,Measurement.prcp).    filter(Measurement.date > "2016-08-23").all()

# Save the query results as a Pandas DataFrame and set the index to the date column
df = pd.DataFrame(df, columns=['Date', 'Precipitation'])
df.set_index('Date', inplace=True)

# Sort the dataframe by date
df.sort_values(by='Date')
df.head()


# In[17]:


# Use Pandas Plotting with Matplotlib to plot the data
#plot data
fig, ax = plt.subplots(figsize=(15,7))
df.plot.bar(ax=ax,color='b')
plt.style.use('ggplot')
ax.set_ylabel('Inches')
plt.legend(loc="center")
plt.show()


# In[19]:


# Use Pandas to calcualte the summary statistics for the precipitation data
df.describe()


# ![describe](Images/describe.png)

# In[20]:


# Design a query to show how many stations are available in this dataset?
Stations = session.query(Station).count()
Stations


# In[21]:


# What are the most active stations? (i.e. what stations have the most rows)?
# List the stations and the counts in descending order.
Active_Stations = session.query(func.count(Measurement.prcp),Measurement.station).    group_by(Measurement.station).    order_by(func.count(Measurement.prcp).desc()).all()
Active_Stations


# In[22]:


# Using the station id from the previous query, calculate the lowest temperature recorded, 
# highest temperature recorded, and average temperature most active station?
Lowest_Temp = session.query(func.min(Measurement.tobs)).                filter(Station.station == "USC00519281").all()

Highest_Temp = session.query(func.max(Measurement.tobs)).                filter(Station.station == "USC00519281").all()

Average_Temp = session.query(func.avg(Measurement.tobs)).                filter(Station.station == "USC00519281").all()

print(f'Temps: Lowest {Lowest_Temp}, Highest {Highest_Temp}, Average {Average_Temp}') 


# In[23]:


# Choose the station with the highest number of temperature observations.
# Query the last 12 months of temperature observation data for this station and plot the results as a histogram
USC00519281 = session.query(Measurement.tobs).    filter(Measurement.station == "USC00519281").    filter(Measurement.date > "2016-08-23").all()

USC00519281 = pd.DataFrame(USC00519281, columns=['Temp'])

USC00519281.head(15)


# In[24]:


_ = plt.hist(USC00519281['Temp'], bins=12, color="lightblue") 
_ = plt.ylabel('Frequency')
_ = plt.legend(['tobs'])
plt.show()


# ![precipitation](Images/station-histogram.png)

# In[25]:


# This function called `calc_temps` will accept start date and end date in the format '%Y-%m-%d' 
# and return the minimum, average, and maximum temperatures for that range of dates
def calc_temps(start_date, end_date):
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """
    
    return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

# function usage example
print(calc_temps('2012-02-28', '2012-03-05'))


# In[26]:


# Use your previous function `calc_temps` to calculate the tmin, tavg, and tmax 
# for your trip using the previous year's data for those same dates.
trip = calc_temps('2016-08-23', '2017-08-23')
print(calc_temps('2016-08-23', '2017-08-23'))


# In[31]:


# Plot the results from your previous query as a bar chart. 
# Use "Trip Avg Temp" as your Title
# Use the average temperature for the y value
# Use the peak-to-peak (tmax-tmin) value as the y error bar (yerr)

fig, ax = plt.subplots()

x = range(len(trip))
ax.boxplot(trip, patch_artist=True)
ax.set_title('Trip Avg Temp')
fig.tight_layout()
plt.show()


# In[28]:


# Calculate the rainfall per weather station for your trip dates using the previous year's matching dates.
# Sort this in descending order by precipitation amount and list the station, name, latitude, longitude, and elevation

Rainfall_Station = session.query(Station.station, Station.name,                                  Station.latitude, Station.longitude, Station.elevation,                                 func.sum(Measurement.prcp)).    filter(Station.station == Measurement.station).    filter(Measurement.date > "2016-08-23").    group_by(Station.station).    order_by(func.sum(Measurement.prcp).desc()).all()


Rainfall_Station = pd.DataFrame(Rainfall_Station, columns=['Station', 'Name', 'Lat', 'Lng', 'Elevation', 'Total Prcp'])
Rainfall_Station


# In[73]:


# Step 2: Climate App
# Use and setup FLASK to create routes

from flask import Flask, jsonify

app = Flask(__name__)


# In[ ]:


# Create routes
# Home page
@app.route("/")
def home():
    # List all routes that are available
    print("Server received request for 'Home' page")
    return (
        f"Welcome to my Cimate API!<br/>"
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
    print("_____")


# * `/api/v1.0/stations`
# * Return a JSON list of stations from the dataset.

# * `/api/v1.0/tobs`
# * query for the dates and temperature observations from a year from the last data point.
# * Return a JSON list of Temperature Observations (tobs) for the previous year.

# * `/api/v1.0/<start>` and `/api/v1.0/<start>/<end>`
# * Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
# * When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date.
# * When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates between the start and end date inclusive.



# In[ ]:


# Main behavior
if __name__ == "__main__":
    app.run(debug=True)

