import requests
import json
from enum import Enum
from pathlib import Path
import xml.etree.ElementTree as ET
import pandas as pd
import xml.etree.ElementTree
import webbrowser

class ActivitySource(Enum):
    STRAVA = "strava"
    NIKE = "nike"
    APPLE = "apple"

class JsonRunDataRequestor():

    def __init__(self):

        self.strava_client_id = "17083"
        self.strava_client_secret = "9c4e8fbc7844f583b26888c6898e7d546e5adc3c"
        self.strava_code="1fa1472483c87e8a61081a67d66680e5ec0c8e6f"

        self.strava_refresh_token="1c6e10fadf51ddfbe7ab0512d901f408a96d4ceb"
        self.strava_access_token="4f20b91ad94b3be438b2a6ba038d346577d3f137"
        self.strava_athlete_id=6473758
        self.strava_token_expiry=None

        self.strava_callback_domain = "http://localhost"
        self.strava_scope= "activity:read_all,activity:write"

        self.nike_access_token = "eyJhbGciOiJSUzI1NiIsImtpZCI6IjYzMjdkOGU4LWNlNmMtNGI0MC1iYTdmLTRmYmI0OTM4Zjc4NnNpZyJ9.eyJ0cnVzdCI6MTAwLCJpYXQiOjE1NzA5ODkwMDEsImV4cCI6MTU3MDk5MjYwMSwiaXNzIjoib2F1dGgyYWNjIiwianRpIjoiMTIyMTNlOWEtM2Y0Zi00YTRlLTlkZTgtY2VmOTU2NDdlMTY5IiwibGF0IjoxNTcwODU1NzIyLCJhdWQiOiJjb20ubmlrZS5kaWdpdGFsIiwic3ViIjoiY29tLm5pa2UuY29tbWVyY2UubmlrZWRvdGNvbS53ZWIiLCJzYnQiOiJuaWtlOmFwcCIsInNjcCI6WyJuaWtlLmRpZ2l0YWwiXSwicHJuIjoiOTU3MTQ5ODU4NiIsInBydCI6Im5pa2U6cGx1cyJ9.QX0ojC9mji6YzUJRVoTSNDy28nYusCcDpqs7QsTMX3OLsid19rNA7abTbNWzn7BnCwjNEjWV_md4oTXHaYn7DZVHoAjxAeRKJw1evA4L1STpICCYxHAlU-xm-vm4yb0RAvZp5TmtRF2JyK-xK9PFANccCVovyQuNxCfcPRLBlHxfFC68OFwpdSuU83qJ5HhMDYMj7r1OBbMM_i85VcD7vLd-hmGDPI-XoACBkJwaFg5u4S5AxP1wH_hu3l4J1sIihq-6r_FFihmKsadYSgJLXaKHsJeQnahOWjgmosVTruXyZNF_gq0j5qyDaOQ3kXdEy6FADVUd5WYvrDYA0kHy5Q"

        if (self.strava_code == None):
            self.do_strava_auth()

        if (self.strava_athlete_id == None 
            or self.strava_access_token == None 
            or self.strava_refresh_token == None):
            requestor.do_strava_oauth()

    def get(self, url, allow_redirects = False, params = None, bearer_token = None):
        headers=None
        if bearer_token:
            headers = {'Authorization': 'Bearer {}'.format(bearer_token)}

        print("making a GET to {} with headers {} params {}".format(url, headers, params))
        response = requests.get(url, headers=headers, allow_redirects=allow_redirects, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception("bad response from GET {}".format(response.status_code))

    def post(self, url, payload = None):
        print("making a post to " + url)
        response = requests.post(url)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception("bad response from post {}".format(response.status_code))

    def do_strava_auth(self):
        strava_auth_url = ("https://www.strava.com/oauth/authorize?"
                    "client_id={}&"
                    "redirect_uri={}&"
                    "response_type=code&"
                    "scope={}").format(
                        self.strava_client_id, 
                        self.strava_callback_domain, 
                        self.strava_scope)
        # # print("Please go to the following url: {}".format(strava_auth_url))
        webbrowser.open_new(strava_auth_url)
        print("You will need a code from the following.")
        self.strava_code = input("What's the code you get at this redirect? ")

    def do_strava_oauth(self):
        strava_oAuth_url = ("https://www.strava.com/oauth/token?"
                    "client_id={}&"
                    "client_secret={}&"
                    "code={}&"
                    "grant_type=authorization_code").format(
                        self.strava_client_id, 
                        self.strava_client_secret, 
                        self.strava_code)
        json = self.post(strava_oAuth_url)
        self.strava_save_tokens(json)

    def strava_save_tokens(self, response):
        self.strava_refresh_token = response["refresh_token"]
        self.strava_access_token = response["access_token"]
        self.strava_athlete_id = response["athlete"]["id"]
        self.strava_token_expiry = response["expires_at"]
        print("Save these tokens for local dev...")
        print("Access token: " + self.strava_access_token)
        print("Refresh token: " + self.strava_refresh_token)
        print(f"Athlete id: {self.strava_athlete_id}")

    def get_json_activities(self, activity_type):  
        if activity_type == ActivitySource.STRAVA:
            filename = 'data/STRAVA_paginated_activity.txt'
        elif activity_type == ActivitySource.NIKE:
            filename = 'data/NIKE_paginated_activity_single_list.txt'
        
        activities = self.get_json_from_file(filename)

        if activities:
            print(f"Using cached activities for {activity_type}")
        else:
            print(f"Fetching new activities for {activity_type}")
            if activity_type == ActivitySource.STRAVA:
                activities = self.get_all_strava_pages()
            elif activity_type == ActivitySource.NIKE:
                url = ("https://api.nike.com/sport/v3/me/activities/after_time/0")
                first_page = self.get(url, bearer_token=self.nike_access_token)
                activities = self.get_all_subsequent_nike_pages(first_page)
            self.save_json_to_file(filename, activities)
        return activities
    
    def get_nike_additional_metrics(self):
        filename = "data/NIKE_detailed_activities.txt"
        detailed_activities = self.get_json_from_file(filename)
        if detailed_activities:
            print('Fetching nike detailed activities from file')
            return detailed_activities

        print("Fetching nike detailed activities from API")
        
        activities = self.get_json_activities(ActivitySource.NIKE)
        nike_detailed_activities = []
        for activity in activities:
            activity_id = activity['id']
            url = f"https://api.nike.com/sport/v3/me/activity/{activity_id}?metrics=ALL"
            detailed_activity = self.get(url, bearer_token=self.nike_access_token)
            nike_detailed_activities.append(detailed_activity)
        self.save_json_to_file("NIKE_detailed_activities.txt", nike_detailed_activities)

    def get_all_strava_pages(self):            
        url = ("https://www.strava.com/api/v3/athlete/activities")
        params = {'page': 1}
        all_pages = []
        while (True):
            this_page = self.get(url, bearer_token=self.strava_access_token, params=params)
            if (len(this_page) == 0):
                print('Fetched {} pages from strava'.format(params['page']))
                break
            all_pages.extend(this_page)
            params['page'] += 1
        return all_pages

    def get_all_subsequent_nike_pages(self, first_page):
        all_items = []
        all_items.extend(first_page['activities'])
        this_page = first_page
        while(True):
            if 'paging' in this_page and 'after_id' in this_page['paging']:
                after_id = this_page['paging']['after_id']
                url=f"https://api.nike.com/sport/v3/me/activities/after_id/{after_id}"
                new_page = self.get(url, bearer_token=self.nike_access_token) 
                all_items.extend(new_page['activities'])
                this_page = new_page
            else:
                break
        return all_items

    def save_json_to_file(self, filename, json_to_save):
        with open(filename, 'w+') as f:
            json.dump(json_to_save, f, ensure_ascii=False, indent=4)

    def get_json_from_file(self, filename):
        Path(filename).touch(exist_ok=True)
        with open(filename, 'r+') as f:
            try:
                return json.load(f)
            except json.decoder.JSONDecodeError:
                print("Nothing in the file")
                return None
            
requestor = JsonRunDataRequestor()

# requestor.do_strava_oauth()
# requestor.get_activities(ActivityType.STRAVA)
# requestor.get_and_save_activities(ActivityType.STRAVA)
# activities = requestor.get_activities(ActivityType.NIKE)
# requestor.get_nike_additional_metrics()
