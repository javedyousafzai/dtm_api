from dtmapi import DTMApi

# Initialize the API client with your subscription key
# for Api keu use the .env file and load it with dotenv
import os
from dotenv import load_dotenv
#from requests import api
load_dotenv()
api = DTMApi(subscription_key=os.getenv("DTMAPI_SUBSCRIPTION_KEY"),api_version="v3")

# Fetch data with demographic disaggregation
data = api.get_idp_admin0_data(CountryName="Pakistan")
print(data)