from dtmapi import DTMApi

# Initialize the API client with your subscription key
# for Api keu use the .env file and load it with dotenv
import os
from dotenv import load_dotenv
#from requests import api
load_dotenv()
api = DTMApi(subscription_key=os.getenv("DTMAPI_SUBSCRIPTION_KEY"))
#api = DTMApi(subscription_key="9a142d3a489a45fab4ddf1a5d538ab56")

# Get all available countries
all_countries = api.get_all_countries()
all_countries.head()

# Get all operations
all_operations = api.get_all_operations()
all_operations.head()

# Get IDP Admin 0 (country-level) data for Ethiopia, rounds 1-10
idp_admin0_data = api.get_idp_admin0_data(
    CountryName='Ethiopia',
    FromRoundNumber=1,
    ToRoundNumber=10
)
idp_admin0_data.head()

# Get IDP Admin 1 (state/province-level) data with date filtering
idp_admin1_data = api.get_idp_admin1_data(
    CountryName='Sudan',
    Admin1Name="Blue Nile",
    FromReportingDate='2020-01-01',
    ToReportingDate='2024-08-15'
)
idp_admin1_data.head()

# Get IDP Admin 2 (district-level) data by operation
idp_admin2_data = api.get_idp_admin2_data(
    Operation="Displacement due to conflict",
    CountryName='Lebanon'
)
idp_admin2_data.head()
#export to csv
idp_admin2_data.to_csv("idp_admin2_data.csv", index=False)
# print the full API url
print (idp_admin2_data)