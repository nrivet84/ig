# -*- coding: utf-8 -*-
"""
@author: Nicolas Rivet
"""

import configparser


def getconfig(account_type='demo'):
    """ from a file 'config.ini' get configuration to use IG API
    ---
    Keyword argument:
    account_type -- "demo" (by default) or "live"
    ---
    Return:
    proxy user
    proxy password
    API key
    IG identifier
    IG password
    IG account
    """
    config = configparser.ConfigParser()
    config.read('config.ini')


    return config['proxy']['user'], config['proxy']['password'], \
    config[account_type]['key'], \
    config[account_type]['identifier'], \
    config[account_type]['password'], \
    config[account_type]['account']

def main():
    return None

if __name__ == '__main__':
    main()