# -*- coding: utf-8 -*-
"""
@author: Nicolas Rivet
test the connection to IG API
do some basic operations
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'ig')))

import ig_service as igs
import ig_tools as igt

def main():
    """Main module for testing."""

    #get config for demo API
    proxy_user, proxy_password, api_key, username, password, account = \
    igt.getconfig('demo')

    #login demo API
    service = igs.IGservice(username, password, api_key, account, 'demo',\
                            proxy_user, proxy_password)
    log = service.login()
    print('\n', 'login', '\n', log)

    #get newest bidask
    instrument = 'CS.D.EURUSD.CFD.IP'
    bidask = service.get_bidask(instrument)
    print('\n', 'get_bidask of EURUSD', '\n', bidask)

    #get historical closes
    resolution = 'MINUTE'
    max_size = 10
    closes = service.get_closes(instrument, resolution, max_size)
    print('\n', 'get_closes of EURUSD for the last 10 minutes', '\n', closes)

if __name__ == '__main__':
    main()
    
