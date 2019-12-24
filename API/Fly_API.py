import requests
import json
from amadeus import Client, ResponseError, Location
from geopy.geocoders import Nominatim


def find_airport_by_coordinates(lat, lon):
    request_string = f'https://ourairportapi.com/nearest/{lat},{lon}?expand=true&iataOnly=true&max=1'
    response = requests.get(request_string)
    res = json.loads(response.text)
    return res['results'][0]['iata']


class Fly:
    def __init__(self):
        f = open("API/code.txt", "r")
        code = f.read()
        self.amadeus = Client(
            client_id='JzlFRuOgo0pT42JHNoAVjOs8WKWxYvSq',
            client_secret=code
        )

    def lat_lon_by_city(self, city):
        geolocator = Nominatim(user_agent="ITC_DM")
        location = geolocator.geocode(city, timeout=2)
        latitude = location.latitude
        longitude = location.longitude
        return latitude,longitude

    def find_airport_by_city_name(self, city):
        geolocator = Nominatim(user_agent="ITC_DM")
        location = geolocator.geocode(city, timeout=2)
        latitude = location.latitude
        longitude = location.longitude
        return find_airport_by_coordinates(latitude, longitude)

    def _better_price(self, response):
        price = 1000_000
        departure = ''
        arrival = ''
        for resp in response.result['data']:
            if float(resp['offerItems'][0]['price']['total']) < price:
                price = float(resp['offerItems'][0]['price']['total'])
            return price

    def travel_price(self, from_airport, to_airport, date, cheapest=True):
        """find cheapest price (cheapest=True) or shortest flight (cheapest=False) """
        try:
            response = self.amadeus.shopping.flight_offers.get(origin=from_airport, destination=to_airport,
                                                               departureDate=date)
        except ResponseError as error:
            print(error)
            return ''

        price = 1000_000
        if cheapest:
            price = self._better_price(response)
        else:
            min_time = 365 * 24 * 60 * 60
            for resp in response.result['data']:
                for segm in resp['offerItems'][0]['services'][0]['segments']:
                    days = float(segm['flightSegment']['duration'].split('DT')[0])
                    hour = float(segm['flightSegment']['duration'].split('DT')[1].split('H')[0])
                    minutes = float(segm['flightSegment']['duration'][:-1].split('DT')[1].split('H')[1])
                    duration = (days * 24 + hour) * 60 + minutes
                    if duration < min_time or \
                            (duration == min_time and float(resp['offerItems'][0]['price']['total']) < price):
                        min_time = duration
                        price = float(resp['offerItems'][0]['price']['total'])
        return price

    def flight_cheapest_date_search(self, origin, destination):
        try:
            response = self.amadeus.shopping.flight_dates.get(origin=origin, destination=destination)
            return [{'departureDate': i['departureDate'], 'returnDate': i['returnDate'], 'price': i['price']['total']}
                    for i in response.result['data']]

        except ResponseError as error:
            print(error)
