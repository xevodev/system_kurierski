from urllib.parse import urlencode
import requests
import mysql.connector

#API key
api_file = open("api_key", "r")
GOOGLE_API_KEY = api_file.read()
api_file.close()

#Konwerter tupli na string
def convert_tuple(tup):
    str = ' '.join(tup)
    return str

def extract_addresses_from_database():
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",#input("Wprowadz login: "),
        password="xsw2!QAZ",#input("Wprowadz haslo: "),
        database="system_kurierski"
    )

    print("Pobieranie adresow z bazy danych...")

    mycursor = mydb.cursor()

    mycursor.execute("SELECT ulica, nr_ulica, kod_pocztowy, miasto, kraj FROM adresy")

    myresult = mycursor.fetchall()

    data = []

    for x in myresult:
      data.append(convert_tuple(x))

    print("Pobrano adresy \u2713")

    return data

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

def object_creation(data):
    clients = []
    for i in range(len(data)):
        tmp = GoogleMapsClient(api_key=GOOGLE_API_KEY, address=data[i])
        clients.append(tmp)
    return clients

def main():
    print("System kurierski v0.1")
    print("----------------------------------")
    adresy = extract_addresses_from_database()
    locations = object_creation(adresy)
    print("----------------------------------")
    print(f"Adres poczatkowy: {locations[0].location_query}")
    for i in range(len(locations)-1):
        print(locations[i+1].location_query)



if __name__ == "__main__":
    main()
