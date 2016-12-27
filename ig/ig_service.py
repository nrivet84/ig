# -*- coding: utf-8 -*-
"""
@author: Nicolas Rivet
"""

import json
import urllib.request as req
import requests



class IGservice():
    """
    methods to use IG API services
    """
    _base_urls = {
        'demo':'https://demo-api.ig.com/gateway/deal',
        'live':'https://api.ig.com/gateway/deal'
        }
    base_url = None
    base_header = {}
    trading_header = {}

    def __init__(self, username, password, api_key, account, account_type='demo',\
                 proxy_user='', proxy_password=''):
        """Initialise the class IGservice.

        Keyword arguments:
        username -- IG identifier
        password -- IG password
        api_key -- key previously created, see labs.ig.com
        account -- denomination of the account
        account_type -- "demo" (by default) or "live"
        """
        self.username = username
        self.password = password
        self.api_key = api_key
        self.account = account
        try:
            self.url = self._base_urls[account_type.lower()]
        except:
            raise Exception('invalid account_type: "demo" or "live"')
        self.base_header['X-IG-API-KEY'] = api_key
        self.base_header['Content-Type'] = 'application/json; charset=UTF-8'
        #set up proxy
        self.proxy = req.getproxies()
        if self.proxy != '':
            if proxy_user != '' and proxy_password != '':
                proxy_authen = proxy_user + ':'+ proxy_password + '@'
                for key in self.proxy:
                    self.proxy[key] = self.proxy[key].split('//')[0] + \
                    '//' + proxy_authen + \
                    self.proxy[key].split('//')[1]

    def login(self):
        """Connect to the IG service.

        Return:
        response -- object returns by the authentication, includes the token
        response2 -- object returns by the confirmation of the account
        response3 -- "get accounts" object
        """
        #get security token
        api_endpoint = self.url + '/session'
        api_body = {}
        api_body['identifier'] = self.username
        api_body['password'] = self.password
        api_body['encryptedPassword'] = False
        api_header = self.base_header

        response = requests.post(api_endpoint,
                                 data=json.dumps(api_body),
                                 headers=api_header,
                                 proxies=self.proxy)

        #modify trading_header according to the security token
        self.trading_header = {}
        self.trading_header['X-IG-API-KEY'] = self.api_key
        self.trading_header['X-SECURITY-TOKEN'] = response.headers['X-SECURITY-TOKEN']
        self.trading_header['CST'] = response.headers['CST']

        #confirm current account
        api_endpoint = self.url + '/session'
        api_body = {}
        api_body['accountId'] = self.account
        api_body['defaultAccount'] = True
        api_header = self.trading_header
        response2 = requests.put(api_endpoint,
                                 data=json.dumps(api_body),
                                 headers=api_header,
                                 proxies=self.proxy)

        #get accounts
        api_endpoint = self.url + '/accounts'
        response3 = requests.get(api_endpoint,
                                 headers=api_header,
                                 proxies=self.proxy)
        return response, response2, response3

    def get_bidask(self, instrument):
        """Get current bid/ask of an instrument.

        Keyword argument:
        instrument

        Return:
        bid
        ask
        """
        api_endpoint = self.url + '/markets'
        api_endpoint = api_endpoint + '/' + instrument
        api_header = self.trading_header
        api_header['Version'] = '3'
        response = requests.get(api_endpoint, headers=api_header, proxies=self.proxy)
        market = response.json()
        bid = market['snapshot']['bid']
        ask = market['snapshot']['offer']
        return bid, ask

    def get_closes(self, instrument, resolution, max_size):
        """Get latest closes according to a given frequency.

        Keyword arguments:
        instrument
        resolution -- frequency "SECOND", "MINUTE", ...
        max_size -- number of points

        Return:
        bid -- historical bids
        ask -- historical bids
        response -- object returns by the request, includes historical OHiLoC
        """
        api_endpoint = self.url + '/prices'
        api_endpoint = api_endpoint + '/' + instrument
        api_endpoint = api_endpoint + '?resolution='+ resolution
        api_endpoint = api_endpoint + '&max=' + str(max_size)
        api_endpoint = api_endpoint + '&pageSize=' + str(max_size)
        api_header = self.trading_header
        api_header['Version'] = '3'
        response = requests.get(api_endpoint, headers=api_header, proxies=self.proxy)
        prices = response.json()['prices']
        bid = []
        ask = []
        for i in range(int(max_size)):
            bid.append(prices[i]['closePrice']['bid'])
            ask.append(prices[i]['closePrice']['ask'])
        return bid, ask, response

    def create_position_market(self, instrument, direction, size, ccy):
        """Create a position at market price.

        forceOpen @ True,
        guaranteedStop @ False

        Keyword arguments:
        instrument
        direction -- 'BUY' or 'SELL'
        size
        ccy -- ISO currency format

        Return:
        deal_id
        """
        api_endpoint = self.url + '/positions/otc'
        api_body = {'epic':instrument,
                    'expiry':'-',
                    'direction':direction.upper(),
                    'size':str(size),
                    'orderType':'MARKET',
                    'guaranteedStop':False,
                    'forceOpen':True,
                    'currencyCode':ccy.upper()}
        api_header = self.base_header
        api_header['Version'] = '2'

        response = requests.post(api_endpoint,
                                 data=json.dumps(api_body),
                                 headers=api_header,
                                 proxies=self.proxy)
        try:
            deal_ref = response.json()['deal_reference']
        except:
            raise Exception('fail to create a position', response.json()['errorCode'])

        api_endpoint = self.url + '/deal/confirms'
        api_endpoint = api_endpoint + '/' + deal_ref
        api_header = self.base_header
        api_header['Version'] = '2'
        response = requests.get(api_endpoint,
                                headers=api_header,
                                proxies=self.proxy)
        try:
            deal_id = response.json()['deal_id']
        except:
            raise Exception('fail to get a confirmation of the trade', response.json()['errorCode'])

        return deal_id

    def close_all_positions(self):
        """Close all current open positions at market price."""

        api_endpoint = self.url + '/positions'
        api_header = self.base_header
        api_header['Version'] = '2'

        response = requests.get(api_endpoint,
                                headers=api_header,
                                proxies=self.proxy)

        output = []
        if str(response) == '<Response [405]>':
            return output
        else:
            positions = response.json()['positions']
            for i in range(len(positions)):
                deal_id = positions[i]['position']['deal_id']
                direction = positions[i]['position']['direction']
                size = positions[i]['position']['size']
                if direction == 'BUY':
                    direction = 'SELL'
                elif direction == 'SELL':
                    direction = 'BUY'
                output.append(self.close_position_market(deal_id, direction, size))

    def close_position_market(self, deal_id, direction, size):
        """Close a given position at market price.

        expiry @ None

        Return:
        deal_reference
        """

        api_endpoint = self.url + '/positions/otc'
        api_body = {'deal_id':deal_id,
                    'direction':direction,
                    'size':size,
                    'orderType':'MARKET',
                    'expiry':None}
        api_header = self.base_header
        api_header['Version'] = '1'
        api_header['_method'] = 'DELETE'

        response = requests.post(api_endpoint,
                                 data=json.dumps(api_body),
                                 headers=api_header,
                                 proxies=self.proxy)
        try:
            deal_ref = response.json()['deal_reference']
        except:
            raise Exception('fail to close a position, deal_id:', direction, deal_id,
                            response.json()['errorCode'])
        return deal_ref
