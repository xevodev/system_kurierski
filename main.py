from urllib.parse import urlencode
import requests
import mysql.connector

#API key
api_file = open("api_key", "r")
GOOGLE_API_KEY = api_file.read()
api_file.close()

#Konwerter tupli na string
def convertTuple(tup):
    str = ' '.join(tup)
    return str

#MySQL
mydb = mysql.connector.connect(
    host="localhost",
    user="root",#input("Wprowadz login: "),
    password="xsw2!QAZ",#input("Wprowadz haslo: "),
    database="system_kurierski"
)

mycursor = mydb.cursor()

mycursor.execute("SELECT ulica, nr_ulica, kod_pocztowy, miasto, kraj FROM adresy")

myresult = mycursor.fetchall()

adresy = []

for x in myresult:
  adresy.append(convertTuple(x))

#GoogleMaps Client
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

    def next_travel_time(self, next_location):
        endpoint = f"https://maps.googleapis.com/maps/api/distancematrix/{self.data_format}"
        params = f"origins={self.lat},{self.lng}&destinations={next_location.lat},{next_location.lng}&key={self.api_key}"
        url = f"{endpoint}?{params}"
        r = requests.get(url)
        if r.status_code not in range(200,299):
            return {}
        time = r.json()['rows'][0]['elements'][0]['duration']['text']
        distance = r.json()['rows'][0]['elements'][0]['distance']['text']
        return time, distance

client = GoogleMapsClient(api_key=GOOGLE_API_KEY, address=adresy[0])
client2 = GoogleMapsClient(api_key=GOOGLE_API_KEY, address=adresy[6])

print(client.next_travel_time(client2))

# print(client.lat, client.lng)
# print(client2.lat, client2.lng)

