from urllib.parse import urlencode
import requests
import mysql.connector
import os

#Pobranie klucza API z pliku
api_file = open("api_key", "r")
GOOGLE_API_KEY = api_file.read()
api_file.close()

#Funkcja czyszczaca ekran konsoli
def cls():
    os.system('cls' if os.name=='nt' else 'clear')

#Funkcja sluzaca do konwertowania tupli na lancuch znakow
def convert_tuple(tup):
    str = ' '.join(tup)
    return str

#Funkcja sluzaca do polaczenia z baza MySQL oraz pobrania adresow do listy
def extract_addresses_from_database():
    #Pobranie loginu i hasla od uzytwonika i polaczenie z baza danych system_kurierski
    mydb = mysql.connector.connect(
        host="localhost",
        user=input("Wprowadz login: "),
        password=input("Wprowadz haslo: "),
        database="system_kurierski"
    )

    print("----------------------------------")
    print("Pobieranie adresow z bazy danych...")

    #Utworzenie kursora wskazujcego na baze danych
    mycursor = mydb.cursor()

    #Wyslanie zapytania SQL do bazy danych
    mycursor.execute("SELECT ulica, nr_ulica, kod_pocztowy, miasto, kraj FROM adresy")

    #Zapisanie wyniku zapytania w zmiennej myresult
    myresult = mycursor.fetchall()

    data = []

    #Konwersja wynikow zapytania z tupli na lancuchy znakow
    for x in myresult:
      data.append(convert_tuple(x))

    #Zwrocenie listy adresow
    return data

#Utworzenie klasy sluzacej do komunikacji z Google Maps API
class GoogleMapsClient(object):
    #Zmienne klasy
    lat = lng = None
    data_format = "json"
    location_query = None
    api_key = None

    #Utworzenie konstruktora klasy (metody inicjalizacyjnej)
    def __init__(self, api_key=None, address=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if api_key == None:
            raise Exception("API key is required")
        self.api_key = api_key
        self.location_query = address
        if self.location_query != None:
            self.extract_lat_lng()

    #Metoda sluzaca do pobrania dlugosci i szerokosci geograficznej za pomoca Geocoding API
    def extract_lat_lng(self):
        #Przygotowanie adresu URL uzytego do wykonania zapytania HTTP
        endpoint = f"https://maps.googleapis.com/maps/api/geocode/{self.data_format}"
        params = {"address": self.location_query, "key": self.api_key}
        url_params = urlencode(params)
        url = f"{endpoint}?{url_params}"
        #Wyslanie zapytania do Geocoding API za pomaca protokolu HTTP
        r = requests.get(url)
        #Sprawdzenie czy zapytanie HTTP powiodlo sie
        if r.status_code not in range(200,299):
            return {}
        #Przypisanie wartosci otrzymanych przez plik JSON do zmiennej
        latlng = r.json()["results"][0]["geometry"]["location"]
        lat, lng = latlng.get("lat"), latlng.get("lng")
        #Przypisanie wartosci do zmiennych obiektu
        self.lat = lat
        self.lng = lng
        return lat, lng

    #Metoda sluzaca do wyliczenia najlepszej drogi do nastepnego punktu przy pomocy Distance Matrix API
    def next_travel_time(self, next_location):
        #Przygotowanie adresu URL do wykonania zapytania HTTP
        endpoint = f"https://maps.googleapis.com/maps/api/distancematrix/{self.data_format}"
        params = f"origins={self.lat},{self.lng}&destinations={next_location.lat},{next_location.lng}&key={self.api_key}"
        url = f"{endpoint}?{params}"
        #Wyslanie zapytania do Geocoding API za pomaca protokolu HTTP
        r = requests.get(url)
        #Sprawdzenie czy zapytanie HTTP powiodlo sie
        if r.status_code not in range(200,299):
            return {}
        #Przypisanie wartosci otrzymanych przez plik JSON do zmiennych
        time = r.json()['rows'][0]['elements'][0]['duration']['text']
        distance = r.json()['rows'][0]['elements'][0]['distance']['text']
        #Zwrocenie czasu oraz odleglosci do nastepnego punktu
        return time, distance

#Funkcja sluzaca do utworzenia obiektow z adresami uzyskanymi z bazy danych
def object_creation(data):
    clients = []
    for i in range(len(data)):
        tmp = GoogleMapsClient(api_key=GOOGLE_API_KEY, address=data[i])
        clients.append(tmp)
    return clients

#Glowna funkcja programu
def main():
    cls()
    print("System kurierski v0.1")
    print("----------------------------------")
    #Pobranie adresow z bazy danych
    adresy = extract_addresses_from_database()
    #Utworzenie listy lokalizacji z adresami
    locations = object_creation(adresy)
    print("----------------------------------")
    print(f"Adres poczatkowy: {locations[0].location_query}")
    input("Wcisnij ENTER aby przejsc do nastepnego punktu...")
    #Petla wypisujace kolejne lokalizacje do dostarczenia paczek
    for i in range(len(locations)-1):
        cls()
        print(locations[i].location_query, " --> ", locations[i+1].location_query)
        #Wyznaczenie czasu i odleglosci do pokonania do nastepnej lokalizacji
        czas_i_odleglosc = locations[i].next_travel_time(locations[i+1])
        print("Czas podrozy: ", czas_i_odleglosc[0], " Odleglosc: ", czas_i_odleglosc[1])
        input("Wcisnij ENTER aby przejsc do nastepnego punktu...")
    cls()
    input("Wszystkie przesylki dostarczone. Wcisnij ENTER aby zakonczyc program...")


if __name__ == "__main__":
    main()