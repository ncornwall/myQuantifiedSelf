import logging
import os
from dotenv import load_dotenv
from utils import get, post, get_json_from_file, save_json_to_file, isBlank

import webbrowser

class StravaFetcher():
    """
    Fetches data from Strava APIs
    Strava APIs require a strava_client_id, strava_client_secret, and strava_code
    Strava code can be generated from the auth step
    """

    def __init__(self):

        load_dotenv(verbose=True)

        self.strava_client_id = os.getenv("STRAVA_CLIENT_ID")
        self.strava_client_secret = os.getenv("STRAVA_CLIENT_SECRET")
        self.strava_code = os.getenv("STRAVA_CODE")

        self.strava_refresh_token = os.getenv("STRAVA_REFRESH_TOKEN")
        self.strava_access_token = os.getenv("STRAVA_ACCESS_TOKEN")
        self.strava_athlete_id = os.getenv("STRAVA_ATHLETE_ID")
        self.strava_token_expiry=None

        self.strava_callback_domain = os.getenv("STRAVA_CALLBACK", "http://localhost")
        self.strava_scope= "activity:read_all,activity:write"
        
        self.dir = "data/"
        self.activities_filename = 'data/STRAVA_activities.txt'

    def fetch_strava_activities(self, refresh_cache=False):
        """Fetches all Strava activities. If they are saved in a JSON file, it will use that as the source,
        otherwise will fetch all activities from the API.

        Args:
            refresh_cache (bool, optional): Will force a refresh of the data in saved JSON files. Defaults to False.
        """
        activities = get_json_from_file(self.dir, self.activities_filename)

        if activities and not refresh_cache:
            logging.info(f"Using cached activities for Strava data")
            return activities

        logging.info(f"Fetching new activities for Strava data")
        try:
            self.authorize_strava()
            activities = self.get_all_strava_pages()
            save_json_to_file(self.activities_filename, activities)
            return activities
        except Exception:
            logging.exception("Something went wrong, could not fetch Strava data")

    def authorize_strava(self):
        """Check the environment to see if we have all required tokens. 
        If not not, let's do some oauth.
        """
        if isBlank(self.strava_code):
            self.do_strava_oauth_authorization()
        elif (isBlank(self.strava_access_token) 
            or isBlank(self.strava_refresh_token)):
            self.do_strava_oauth_token_exchange()
        else:
            logging.info("Using Strava tokens from the environment.")

    def do_strava_oauth_authorization(self):
        """Popup a browser window in order to Strava code from the user.
        """
        strava_auth_url = ("https://www.strava.com/oauth/authorize?"
                    f"client_id={self.strava_client_id}&"
                    f"redirect_uri={self.strava_callback_domain}&"
                    "response_type=code&"
                    f"scope={self.strava_scope}")
        print(
            "I'm opening up a browser window. If you're running this from within a Docker container, "
            "you'll need to open it yourself. \nPlease open the url:"
            f"\n {strava_auth_url}")
        webbrowser.open_new(strava_auth_url)
        logging.info("Requesting strava code from the user")
        self.strava_code = input(("\n\nAfter authorization, you've been redirected to a url that looks like \n"
            "\"http://localhost/?state=&code=<YOUR STRAVA CODE HERE>&scope=read,activity:write,activity:read_all\"" 
            "\nI need the value from the 'code' query parameter. Please enter your Strava code now: "))

        if isBlank(self.strava_code):
            raise Exception("User was not able to provide valid Strava code.")

        logging.info("Save this to the .env file to skip this auth step in the future.")
        logging.info(f"STRAVA_CODE={self.strava_code}")

    def do_strava_oauth_token_exchange(self):
        strava_oAuth_url = (f"https://www.strava.com/api/v3/oauth/token?"
                    f"client_id={self.strava_client_id}&"
                    f"client_secret={self.strava_client_secret}&"
                    f"code={self.strava_code}&"
                    "grant_type=authorization_code")
        json = post(strava_oAuth_url)
        self.strava_parse_and_save_tokens(json)

    def strava_parse_and_save_tokens(self, response):
        self.strava_refresh_token = response["refresh_token"]
        self.strava_access_token = response["access_token"]
        self.strava_athlete_id = response["athlete"]["id"]
        self.strava_token_expiry = response["expires_at"]

        if (isBlank(self.strava_access_token) or isBlank(self.strava_refresh_token)):
            raise Exception("Could not parse Strava tokens, cannot fetch further Strava data.")

        logging.info("Save these tokens to the .env file to skip this auth step in the future.")

        logging.info(f"STRAVA_ACCESS_TOKEN={self.strava_access_token}")
        logging.info(f"STRAVA_REFRESH_TOKEN={self.strava_refresh_token}")
        logging.info(f"STRAVA_ATHLETE_ID={self.strava_athlete_id}")

    def get_all_strava_pages(self):
        """
        Fetches paginated data from strava and merges the pages into a single list
        """

        url = ("https://www.strava.com/api/v3/athlete/activities")
        params = {'page': 1}
        all_pages = []
        while (True):
            this_page = get(url, bearer_token=self.strava_access_token, params=params)
            if (len(this_page) == 0):
                logging.info('Fetched {} pages from strava'.format(params['page']))
                break
            all_pages.extend(this_page)
            params['page'] += 1
        return all_pages
