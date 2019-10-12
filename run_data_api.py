import requests
import json
from enum import Enum
from pathlib import Path

class ActivityType(Enum):
    STRAVA = "strava"
    NIKE = "nike"
    APPLE = "apple"

class RunDataApiRequestor():

    def __init__(self):

        self.strava_code="640bc0d5307f42a8ca73ec115b0f6ea51bad1a7b"

        self.strava_refresh_token = "1c6e10fadf51ddfbe7ab0512d901f408a96d4ceb"
        self.strava_access_token =  "6fe6e50a8194efdd78e0229269b466f6a8786350"
       
        self.strava_athlete_id = "6473758"
        self.strava_client_id = "17083"
        self.strava_client_secret = "9c4e8fbc7844f583b26888c6898e7d546e5adc3c"

        self.strava_callback_domain = "http://localhost"
        self.strava_scope= "activity:read_all,activity:write"

        self.nike_access_token = "eyJhbGciOiJSUzI1NiIsImtpZCI6IjYzMjdkOGU4LWNlNmMtNGI0MC1iYTdmLTRmYmI0OTM4Zjc4NnNpZyJ9.eyJ0cnVzdCI6MTAwLCJpYXQiOjE1NzA4NTkzOTAsImV4cCI6MTU3MDg2Mjk5MCwiaXNzIjoib2F1dGgyYWNjIiwianRpIjoiNmIwYTJmOTUtZGI2Ni00ZTk1LTkxZWEtZjE4MWJlNGQxNzg3IiwibGF0IjoxNTcwODU1NzIyLCJhdWQiOiJjb20ubmlrZS5kaWdpdGFsIiwic3ViIjoiY29tLm5pa2UuY29tbWVyY2UubmlrZWRvdGNvbS53ZWIiLCJzYnQiOiJuaWtlOmFwcCIsInNjcCI6WyJuaWtlLmRpZ2l0YWwiXSwicHJuIjoiOTU3MTQ5ODU4NiIsInBydCI6Im5pa2U6cGx1cyJ9.WnmBKUKj4Rt8STu1wMJmhfaHGTo-iQy6Sd4T3H0BaURr_hCzIO2WADabTIhUqYbdCHEoVCP0rmlrIdWCvUz6Whxj3uQ-sUB3AAZZUdhHxsSBUA0WoTuh8GUiWAc8OayAP-R4ORJN5chv2v1Q3mMNZh2Y5WG2yhQmLfgRt4S8azoNcPyAkaoePBkF-AXHPkyd_zTmUVsqgB58sRoxlDAVtSLX6SBNmx5IgsEyDZXYNm7I0qhncDfcyDMU7Azij0MIwYoZZQmoi0OvfOXTt0syGPSr17fo6--VPqqSJwHINXejH2cFIxdTkiuTKaY70s95GJBYp6Is_TLedK-5FBk_Ng"

    def get(self, url, headers = None, allow_redirects = False):
        print("making a get to {} with {}".format(url, headers))
        response = requests.get(url, headers=headers, allow_redirects=allow_redirects)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception("bad response from post {}".format(response.status_code))

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
        print("Please authorize at the following url: {}".format(strava_auth_url))
        print("You will need a code from this its redirect.")

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

    def strava_refresh_access_token(self):
        strava_oAuth_url = ("https://www.strava.com/oauth/token?"
                    "refresh_token={}&"
                    "grant_type=refresh_token").format(self.strava_refresh_token)
        json = self.post(strava_oAuth_url)
        self.strava_save_tokens(json)

    def strava_save_tokens(self, response):
        self.strava_refresh_token = response["refresh_token"]
        self.strava_access_token = response["access_token"]
        self.strava_athlete_id = response["athlete"]["id"]
        print("Save these tokens...")
        print("Access token:" + self.strava_access_token)
        print("Refresh token:" + self.strava_refresh_token)

    def get_and_save_activities(self, activity_type):        
        activities = self.get_json_from_file(activity_type.name)
        if activities == None:
            print(f"Fetching new activities for {activity_type}")
            if activity_type == ActivityType.STRAVA:
                headers = {'Authorization': 'Bearer {}'.format(self.strava_access_token)}
                url = ("https://www.strava.com/api/v3/athlete/activities")
                activities = self.get(url, headers=headers)
            elif activity_type == ActivityType.NIKE:
                headers = {'Authorization': 'Bearer {}'.format(self.nike_access_token)}
                url = ("https://api.nike.com/sport/v3/me/activities/after_time/0")
                activities = self.get(url, headers=headers)            
            self.save_json_to_file(activity_type.name, activities)
        else:
            print(f"Using cached activities for {activity_type}")
        return json.dumps(activities)
    
    def niki_paginate(self, activities):
        if activities['paging']:
            print('paging')
            # url="https://api.nike.com/sport/v3/me/activities/after_id/${after_id}"

    def save_json_to_file(self, filename, json_to_save):
        filename = f'{filename}_activity.txt'
        with open(filename, 'w+') as f:
            json.dump(json_to_save, f, ensure_ascii=False, indent=4)

    def get_json_from_file(self, filename):
        filename = f'{filename}_activity.txt'
        Path(filename).touch(exist_ok=True)
        with open(filename, 'r+') as f:
            try:
                return json.dumps(json.load(f))
            except json.decoder.JSONDecodeError:
                print("Nothing in the file")
                return None

    # def get_and_save_activities(self, activity_type, headers, url):
    #     filename = f'{activity_type.name}_activities.txt'
    #     with open(filename, 'w+') as f:
    #         try:
    #             return json.dumps(json.load(f))
    #         except json.decoder.JSONDecodeError:
    #             activities = self.get(url, headers=headers)
    #             json.dump(activities, f, ensure_ascii=False, indent=4)
    #             return json.dumps(activities)


# http GET "https://www.strava.com/api/v3/activities/{id}?include_all_efforts=" "Authorization: Bearer [[token]]"
requestor = RunDataApiRequestor()
# requestor.do_strava_auth()
# requestor.do_strava_oauth()
# requestor.get_and_save_activities(ActivityType.STRAVA)
activities = requestor.get_and_save_activities(ActivityType.NIKE)
requestor.niki_paginate(activities)
