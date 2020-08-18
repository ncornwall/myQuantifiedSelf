This is a little project for analysing running data. It will merge data from Nike, Strava, and Apple Watch, remove duplicates, and generate some interesting insights from the merged data.

# How to use this project:

## Authorize Strava

Go to your Strava account: https://www.strava.com/settings/api
Note the following information:
- your client secret
- your client id
Add this information to the data fetcher

## Authorize Nike

Go to Nike.com and login
Open network tools and look for some request to the Nike API. Copy the refresh token from that request.
You can use the same refresh token here to access their running API which is otherwise private.
Add this information to the data fetcher

## Export from Apple Health

Go to Apple Health and export a dump of your health kit data
It will make a very large XML file. 
You will need to clean it up using the apple-health-data-parser.py

## Data pipeline

There are a few stages in this project:
- Data fetcher - gets data from APIs and saves it
- Data cleaner - merges the data and removes duplicates
- Data analyzer - where analysis can go
- Data visualizer - makes some random matlab plots

# We're ready, let's go!

Clone the project, do a `make init` and then run main.py.
