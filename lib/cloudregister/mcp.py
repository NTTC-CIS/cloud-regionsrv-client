import configparser
import logging
import requests
import sys

def generateRegionSrvArgs():
    """Cloud Region Server Client API plugin call"""
    cfg = get_config()
    try:
        geo = cfg.get('instance','region')
    except configparser.NoOptionError:
        geo = determine_closest_region(cfg)

    return "regionHint=" + geo

def get_config(configFile=None):
    """Read configuration file and return a config object"""
    if not configFile:
        configFile = '/etc/regionserverclnt.cfg'
    cfg = configparser.RawConfigParser()
    try:
        parsed = cfg.read(configFile)
    except:
        print('Could not parse configuration file %s' % configFile)
        type, value, tb = sys.exc_info()
        logging.warning(value.message)
        sys.exit(1)
    if not parsed:
        logging.warning('Error parsing config file: %s' % configFile)
        sys.exit(1)
    return cfg

def determine_closest_region(cfg):
    """Determine closest and fastest servers by finding the lowest latency"""
    api = cfg.get('server','api')
    servers = cfg.get('server','regionsrv').split(',')
    results = []
    for x in range(0, len(servers)):
        try:
            result = requests.get('https://' + servers[x] + '/' + api)
            results.append(result.elapsed)
        except requests.exceptions.ConnectionError:
            pass
        except requests.exceptions.SSLError:
            pass

    try:
        i = results.index(min(results))
    except ValueError:
        return ''

    if servers[i][0:3] == 'rgn':
        geo = servers[i][3:5]
    else:
        geo = servers[i][0:2]

    return geo