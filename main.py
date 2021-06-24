import googlemaps

API_KEY = "AIzaSyCI6jyORBIefZtyRCQoNR144dKT9KMXoVA"

map_client = googlemaps.Client(API_KEY)

work_place_address = "Rybacka 9 53-656 Wroclaw Poland"

response = map_client.geocode(work_place_address)
print(response[0]['geometry']['location']['lat'])
print(response[0]['geometry']['location']['lng'])



#def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
 #   print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
#if __name__ == '__main__':
#    print_hi('PyCharm')
