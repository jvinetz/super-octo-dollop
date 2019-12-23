import requests
import json


class Currency:
    def __init__(self, base):
        self.base = base
        self.response = requests.get(f'https://api.exchangeratesapi.io/latest?base={base}')
        self.res = json.loads(self.response.text)

    def get_rate(self, second_currency):
        return self.res['rates'][second_currency]

    def get_list_currencies(self):
        if 'error' in self.res:
            return []
        return list(self.res['rates'].keys())


'''tmp = Currency('ILSs')
print(tmp.get_list_currencies())'''

