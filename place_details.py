import requests
from bs4 import BeautifulSoup
import json

# Function to scrape place details
def scrape_place_details(place_url):
    response = requests.get(place_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    places_section = soup.find_all('div', class_='ptv-item')
    places_to_visit = []
    for card in places_section[:5]:
        place_name = card.find('p').text
        places_to_visit.append(place_name)

    place_desc = soup.find_all('div', class_='readMoreText compact')[0].find("p").text
    want_div = soup.find_all('div', class_='accordion')[0]

    return {
        'place_desc': place_desc,
        'want_div': str(want_div),
        'places_to_visit': places_to_visit
    }

# Scrape placelist data
url = "https://aiweb-80256-default-rtdb.firebaseio.com/.json"
placelist = []

try:
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    for key in data.keys():
        if key == "banglore":
            placelist.append("bangalore")
            continue
        if key != "coord":
            placelist.append(key)
except requests.exceptions.HTTPError as err:
    print(f"HTTP Error: {err}")
except Exception as err:
    print(f"Error: {err}")

# Scraping place details and storing in places_data dictionary
places_data = {}

for place in placelist:
    place_url = "https://www.holidify.com/places/" + place
    place_details = scrape_place_details(place_url)
    places_data[place] = place_details

# Convert places_data to JSON object
json_data = json.dumps(places_data)

# Add data to Firebase Realtime Database
database_url = 'https://placedata-a62fd-default-rtdb.firebaseio.com/placedata.json'  # Replace with your Firebase Realtime Database URL

try:
    response = requests.put(database_url, json_data)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        print('Data added to Firebase Realtime Database successfully.')
    else:
        print('Error occurred while adding data to Firebase Realtime Database:', response.status_code)
except requests.exceptions.RequestException as err:
    print('Error occurred during the request:', err)
