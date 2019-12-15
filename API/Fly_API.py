import requests
import json
from amadeus import Client, ResponseError , Location

'''from pyairports.airports import Airports

airports = Airports()
airports.airport_iata(iata) # namedtuple(airport, [name, city, country, iata, icao, lat, lon, alt, tz, dst, tzdb]) or AirportNotFoundException
airports.other_iata(iata)   # namedtuple(other, [iata, name, country, subdiv, type, lat, lon]) or AirportNotFoundException
airports.lookup(iata)


'''





class Currency():
    def __init__(self, base):
        self.base = base
        headers = {"mode": "sandbox"}
        query = {"TripType": "R", "NoOfAdults": 1, "NoOfChilds": 0, "NoOfInfants": 0, "ClassType": "Economy",
                 "OriginDestination": [{"Origin": "JFK", "Destination": "LHR", "TravelDate": "04/23/2020"},
                                       {"Origin": "LHR", "Destination": "JFK", "TravelDate": "04/28/2020"}],
                 "Currency": "USD"}
        self.response = requests.post('https://dev-sandbox-api.airhob.com/sandboxapi/flights/v1.3/search', query,
                                      headers=headers)
        self.res = json.loads(self.response.text)
        print(self.res)

    def get_rate(self, second_currency):
        return self.res['rates'][second_currency]


amadeus = Client(
    client_id='JzlFRuOgo0pT42JHNoAVjOs8WKWxYvSq',
    client_secret='SEWG9UjsCqqxtN5T'
)


def amadeus_request(req):
    try:
        response = req
        print(response.data)
    except ResponseError as error:
        print(error)


#amadeus_request(amadeus.reference_data.urls.checkin_links.get(airlineCode='BA'))
#amadeus_request(amadeus.shopping.flight_offers.get(origin='TLV', destination='CDG', departureDate='2020-01-01'))
#amadeus_request(amadeus.reference_data.locations.airports.get(longitude=2.3488, latitude=48.8534))
#amadeus_request(amadeus.reference_data.location('LFPG').get())


amadeus_request(amadeus.travel.analytics.air_traffic.booked.get(originCityCode='MAD', period='2017-08')
)
#amadeus_request()
'''reponse = requests.get('https://test.api.amadeus.com/v1/reference-data/locations/airports?latitude=49.0000&longitude=2.55',amadeus)
res = json.loads(reponse.text)
print(res)'''

try:
    '''
    What relevant airports are there around a specific location?
    '''
    response = amadeus.reference_data.locations.airports.get(
        longitude=49.000, latitude=2.55)

    for r in response.data:
        print(r['subType'], r['name'], r['detailedName'], r['address'])
except ResponseError as error:
    print(error)