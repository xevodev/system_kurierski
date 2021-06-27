from urllib.parse import urlencode
import requests

API_KEY = "AIzaSyCI6jyORBIefZtyRCQoNR144dKT9KMXoVA"

work_place_address = "Zaułek Rogoziński 145 51-116 Wroclaw Poland"

def extract_lat_lng(address, data_format = "json"):
    endpoint = f"https://maps.googleapis.com/maps/api/geocode/{data_format}"
    params = {"address": address, "key": API_KEY}
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
    return latlng.get("lat"), latlng.get("lng")

print(extract_lat_lng(work_place_address))
