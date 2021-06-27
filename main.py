from urllib.parse import urlencode
import requests

#API key
api_file = open("api_key", "r")
GOOGLE_API_KEY = api_file.read()
api_file.close()

work_place_address = "Zaułek Rogoziński 145 51-116 Wroclaw Poland"

class GoogleMapsClient(object):
    lat = lng = None
    data_format = "json"
    location_query = None
    api_key = None

    def __init__(self, api_key=None, address=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if api_key == None:
            raise Exception("API key is required")
        self.api_key = api_key
        self.location_query = address
        if self.location_query != None:
            self.extract_lat_lng()

    def extract_lat_lng(self):
        endpoint = f"https://maps.googleapis.com/maps/api/geocode/{self.data_format}"
        params = {"address": self.location_query, "key": self.api_key}
        url_params = urlencode(params)
        url = f"{endpoint}?{url_params}"
        r = requests.get(url)
        if r.status_code not in range(200,299):
            return {}
        latlng = {}
        try:
            latlng = r.json()["results"][0]["geometry"]["location"]
        except:
            pass
        lat, lng = latlng.get("lat"), latlng.get("lng")
        self.lat = lat
        self.lng = lng
        return lat, lng

client = GoogleMapsClient(api_key=GOOGLE_API_KEY, address=work_place_address)

print(client.lat, client.lng)