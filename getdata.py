import requests
import json

class RunDataApiRequestor():

    def __init__(self):
        self.refresh_token = "1c6e10fadf51ddfbe7ab0512d901f408a96d4ceb"
        self.access_token =  "71437b42db374d767663d71f8e9a7a676a5748ca"
        self.athlete_id = "6473758"

        self.strava_client_id = "17083"
        self.strava_code="f0e32cc2d75e854965dee4e4c12981a91a725437"
        self.strava_client_secret = "9c4e8fbc7844f583b26888c6898e7d546e5adc3c"

        self.strava_callback_domain = "http://localhost"
        self.strava_scope= "activity:read_all,activity:write"

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
        self.refresh_token = json["refresh_token"]
        self.access_token = json["access_token"]
        self.athlete_id = json["athlete"]["id"]

        print(self.refresh_token)
        print(self.access_token)

    def refresh_access_token(self):
        strava_oAuth_url = ("https://www.strava.com/oauth/token?"
                    "refresh_token={}&"
                    "grant_type=refresh_token").format(self.refresh_token)

        json = self.post(strava_oAuth_url)
        self.refresh_token = json["refresh_token"]
        self.access_token = json["access_token"]
        self.athlete_id = json["athlete"]["id"]

        print(self.refresh_token)
        print(self.access_token)

    def get_activites(self):
        headers = {'Authorization': 'Bearer {}'.format(self.access_token)}
        strava_get_activities_url = ("https://www.strava.com/api/v3/athlete/activities")
        response = self.get(strava_get_activities_url, headers=headers)

# http GET "https://www.strava.com/api/v3/activities/{id}?include_all_efforts=" "Authorization: Bearer [[token]]"

requestor = RunDataApiRequestor()
# requestor.do_strava_auth()
# requestor.do_strava_oauth()
requestor.get_activites()


