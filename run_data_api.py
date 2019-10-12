import requests
import json
from enum import Enum
from pathlib import Path

class ActivityType(Enum):
    STRAVA = "strava"
    NIKE = "nike"
    APPLE = "apple"

class RunDataRequestor():

    def __init__(self):

        self.strava_code="640bc0d5307f42a8ca73ec115b0f6ea51bad1a7b"

        self.strava_refresh_token = "1c6e10fadf51ddfbe7ab0512d901f408a96d4ceb"
        self.strava_access_token =  "2476ff395ab3a850a94acb8b8d1ea0c593182d8d"
       
        self.strava_athlete_id = "6473758"
        self.strava_client_id = "17083"
        self.strava_client_secret = "9c4e8fbc7844f583b26888c6898e7d546e5adc3c"

        self.strava_callback_domain = "http://localhost"
        self.strava_scope= "activity:read_all,activity:write"

        self.nike_access_token = "eyJhbGciOiJSUzI1NiIsImtpZCI6IjYzMjdkOGU4LWNlNmMtNGI0MC1iYTdmLTRmYmI0OTM4Zjc4NnNpZyJ9.eyJ0cnVzdCI6MTAwLCJpYXQiOjE1NzA5MTE1MzMsImV4cCI6MTU3MDkxNTEzMywiaXNzIjoib2F1dGgyYWNjIiwianRpIjoiYWM5NjA1ZjQtYmM2Yi00NzRkLThlMGUtMTI5NTgxODM0YjVhIiwibGF0IjoxNTcwODU1NzIyLCJhdWQiOiJjb20ubmlrZS5kaWdpdGFsIiwic3ViIjoiY29tLm5pa2UuY29tbWVyY2UubmlrZWRvdGNvbS53ZWIiLCJzYnQiOiJuaWtlOmFwcCIsInNjcCI6WyJuaWtlLmRpZ2l0YWwiXSwicHJuIjoiOTU3MTQ5ODU4NiIsInBydCI6Im5pa2U6cGx1cyJ9.E_3uMRbJCCoUaH0eV6MvlNp9YgA7tbTN4HwVxcKSIqN1lvxJgqd5LWf6OCDvCL4VXDeIVi2ZiIN6vLEaefM8HE0CfsD2sVqLpVgObdMZAv7tBMM7bxeZ88ZtsJcZQgU0He7jfXkettRLr8JPdWr1uD6HjV4mNwxf94Wa_jEzqdLwdHAv3OBc4rvBfWSXUgiRZIBseprjQOeTg4Zzk0FUaEzI2DwN_e8brIvB54Hfz5aBftwYFZAwTffwUszL65TNDmXdieQmFa3l_w_lInDgLhxDCOFIgjeq17uThgCSj-cuBHtCrPNm__6cUpUTJ3aWIt-ur8DpL_fDHWS9dY82pw"

    def get(self, url, allow_redirects = False, params = None, bearer_token = None):
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
        print("Access token: " + self.strava_access_token)
        print("Refresh token: " + self.strava_refresh_token)

    def get_activities(self, activity_type):  
        if activity_type == ActivityType.STRAVA:
            filename = 'data/STRAVA_paginated_activity.txt'
        elif activity_type == ActivityType.NIKE:
            filename = 'data/NIKE_paginated_activity.txt'
        
        activities = self.get_json_from_file(filename)

        if activities:
            print(f"Using cached activities for {activity_type}")
        else:
            print(f"Fetching new activities for {activity_type}")
            if activity_type == ActivityType.STRAVA:
                activities = self.get_all_strava_pages()
            elif activity_type == ActivityType.NIKE:
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
        
        activities = self.get_activities(ActivityType.NIKE)
        nike_detailed_activities = []
        for page in activities:
            for activity in page['activities']:
                activity_id = activity['id']
                url = f"https://api.nike.com/sport/v3/me/activity/{activity_id}?metrics=ALL"
                detailed_activity = self.get(url, bearer_token=self.nike_access_token)
                nike_detailed_activities.append(detailed_activity)
        self.save_json_to_file("NIKE_detailed_activities.txt", nike_detailed_activities)

    def get_all_strava_pages(self):            
        url = ("https://www.strava.com/api/v3/athlete/activities")
        params = {'page': 0}
        all_pages = []
        while (True):
            this_page = self.get(url, bearer_token=self.strava_access_token, params=params)
            if (len(this_page) == 0):
                print('Fetched {} pages from strava'.format(params['page']))
                break
            all_pages.append(this_page)
            params['page'] += 1
        return all_pages

    def get_all_subsequent_nike_pages(self, first_page):
        pages = [first_page]
        this_page = pages[0]
        while(True):
            if 'paging' in this_page and 'after_id' in this_page['paging']:
                after_id = this_page['paging']['after_id']
                url=f"https://api.nike.com/sport/v3/me/activities/after_id/{after_id}"
                new_page = self.get(url, bearer_token=self.nike_access_token) 
                pages.append(new_page)
                this_page = new_page
            else:
                break
        return pages

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
requestor = RunDataRequestor()
# requestor.do_strava_auth()
# requestor.do_strava_oauth()
requestor.get_activities(ActivityType.STRAVA)
# requestor.get_and_save_activities(ActivityType.STRAVA)
# activities = requestor.get_and_save_activities(ActivityType.NIKE)

# requestor.get_nike_additional_metrics()