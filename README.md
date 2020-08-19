# My Quantified Self

This is a little project for analyzing running data. It will merge data from Nike+, Strava, and Apple Watch, remove duplicates, and generate some interesting insights from the data. You 

# How to use this project

## Authorize Strava

Go to your Strava account: https://www.strava.com/settings/api. Note the following information:
- your client secret
- your client id

Add this information to the .env file

When this is run for the first time, an authorization window will pop up and ask that you to authorize the app to access your Strava account. This will result in:
- a Strava code
- access token
- refresh token
- your athlete ID

You can also add this information to the .env file to skip this step on subsequent runs.

## Authorize Nike

Nike is much more of a walled garden and requires a little hacking of the Nike APIs to extract your information.

Go to Nike.com and login
Open network tools and look for a request to the Nike API (ttps://api.nike.com). Copy the Authorization:Bearer token from that request.
You can use the same Bearer token here to access their running API which is otherwise private.

Add this information to the .env file

## Export from Apple Health

Go to Apple Health and export a dump of your Health Kit data
It will make a very large XML file. 
Credit to the Quantified Self Ledger (https://github.com/markwk/qs_ledger) for help with the parsing of this file.
Extract your running data from HealthKit by following the instructions in apple-health-data-parser.py

## Data pipeline

There are a few stages in this project:
- Data fetcher: gets data from APIs and saves it to a JSON file
- Data cleaner: merges the data and removes duplicates
- Data analyzer: where analysis can go
- Data visualizer: makes some random matlab plots for fun

# We're ready, let's go!

Run `make init` and then run main.py.
