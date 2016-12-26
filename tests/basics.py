# -*- coding: utf-8 -*-
"""
@author: Nicolas Rivet
test the connection to IG API
do some basic operations
"""

from ig.ig_service import IGservice as igs
import ig.ig_tools as igt

def main():
    """Main module for testing."""
    
    #get config for demo API
    proxy_user, proxy_password, api_key, username, password, account = \
    igt.getconfig('demo')
    
    #login demo API
    service=igs(username, password, api_key, account, 'demo')
    log=igs.login(service)
    print(log[0])
    
    #get newest bidask
    instrument='CS.D.EURUSD.CFD.IP'
    bidask=igs.get_bidask(service, instrument)
    print(bidask)
    
    #get historical closes
    resolution='MINUTE'
    max_size=10
    closes=igs.get_closes(service, instrument, resolution, max_size)
    print(closes)
    
if __name__ == '__main__':
    main()