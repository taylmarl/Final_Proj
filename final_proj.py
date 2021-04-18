#########################################
##### Name: Taylor Marlin           #####
##### Uniqname:    taylmarl         #####
#########################################

import json
import requests
import sqlite3
import secrets as pysecrets # file with api keys

CACHE_FILENAME = "final_cache.json"
CACHE_DICT = {}

# set up connection with database and establish cursor
conn = sqlite3.connect('Si507Proj.sqlite')
cur = conn.cursor()

# The Zipcode API does not have keys for params access, but
# instead takes a very specifically ordered string of params.
zip_key = pysecrets.zip_api_key
zip_base = f'https://www.zipcodeapi.com/rest/{zip_key}/info.json/'

# The Yelp API takes a typical key format
yelp_key = pysecrets.yelp_api_key
yelp_base = 'https://api.yelp.com/v3/businesses/search'



# SQL Database Caching (CRUD) Statements:

create_zip = '''
    CREATE TABLE IF NOT EXISTS "zipcodes" (
        "Zipcode"   TEXT NOT NULL PRIMARY KEY UNIQUE,
        "City"      TEXT NOT NULL,
        "State"     TEXT NOT NULL,
        "Latitude"  TEXT NOT NULL,
        "Longitude" TEXT NOT NULL,
        "Timezone"  TEXT NOT NULL
    );
'''

create_yelp = '''
    CREATE TABLE IF NOT EXISTS "yelp" (
        "Id"        INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
        "Name"      TEXT NOT NULL,
        "Business Type"     TEXT NOT NULL,
        "Price"     TEXT NOT NULL,
        "Phone"     TEXT NOT NULL,
        "Zipcode"   TEXT NOT NULL,
        "Open Status"  TEXT NOT NULL,
        "Address" TEXT NOT NULL,
        "City"  TEXT NOT NULL,
        "State" TEXT NOT NULL,

        FOREIGN KEY(Zipcode) REFERENCES zipcodes(Zipcode)
    );
'''

insert_zip = '''
    INSERT INTO zipcodes
    VALUES(?, ?, ?, ?, ?, ?)
'''

insert_yelp = '''
    INSERT INTO yelp
    VALUES(NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?)
'''

# General Functions for Dict Caching:

def open_cache():
    ''' Opens the cache file if it exists and loads the JSON into
    the CACHE_DICT dictionary.
    if the cache file doesn't exist, creates a new cache dictionary
    
    Parameters
    ----------
    None
    
    Returns
    -------
    The opened cache: dict
    '''
    try:
        cache_file = open(CACHE_FILENAME, 'r')
        cache_contents = cache_file.read()
        cache_dict = json.loads(cache_contents)
        cache_file.close()
    except:
        cache_dict = {}
    return cache_dict

def save_cache(cache_dict):
    ''' Saves the current state of the cache to disk
    
    Parameters
    ----------
    cache_dict: dict
        The dictionary to save
    
    Returns
    -------
    None
    '''
    dumped_json_cache = json.dumps(cache_dict)
    fw = open(CACHE_FILENAME,"w")
    fw.write(dumped_json_cache)
    fw.close() 

def construct_unique_key(baseurl, params):
    ''' constructs a key that is guaranteed to uniquely and 
    repeatably identify an API request by its baseurl and params

    AUTOGRADER NOTES: To correctly test this using the autograder, use an underscore ("_") 
    to join your baseurl with the params and all the key-value pairs from params
    E.g., baseurl_key1_value1
    
    Parameters
    ----------
    baseurl: string
        The URL for the API endpoint
    params: dict
        A dictionary of param:value pairs
    
    Returns
    -------
    string
        the unique key as a string
    '''
    #TODO Implement function

    param_strings = []
    connector = '_'

     # Using code we covered in lecture to format unique key
    for k in params.keys():
        param_strings.append(f'{k}_{params[k]}')
    param_strings.sort()
    unique_key = baseurl + connector +  connector.join(param_strings)

    return unique_key

# Zip Code Class

class Zipcode:
    '''location information associated with a zipcode.

    Instance Attributes
    -------------------
    zipcode: string
        the 5-digit zip-code of a location

    latitude: string
        the latitudinal coordinates for a given zipcode or city/state location

    longitude: string
        the longitudinal coordinates for a given zipcode or city/state location

    city: string

    state: string
        the state that a given zipcode is from

    timezone: string
        abbreviaton for the timezone of a given zipcode
    '''
    def __init__(self, zipcode, latitude, longitude, city, state, timezone):
        '''
        Initalize instance of Zipcode according to class spec
        '''
        self.zipcode = zipcode
        self.latitude = latitude
        self.longitude = longitude
        self.city = city
        self.state = state
        self.timezone = timezone


    def info(self):
        '''
        Return nicely formatted information about Zipcode object.
        '''
        # From https://stackoverflow.com/questions/45965007/multiline-f-string-in-python
        # python strings will concatenate in return statements when not comma-separated.
        return (
            f"The zipcode {self.zipcode} represents {self.city}, {self.state}. \n"
            f"It has (lat, long) coordinates of: ({self.latitude}, {self.longitude}). \n"
            f"It falls into the {self.timezone} timezone."
        )

# Zip Code API Functions

def zip_make_request(search_url):
    '''Make a request to the Zipcode API using the baseurl and params

    Parameters
    ----------
    search_url: string
        The URL for a specific Zipcode API search.
        The zipcode API does not have keys for params, 
        so each term must be appended in order. (zipcode/degrees).

    Returns
    -------
    dict
        the data returned from making the request in the form of 
        a dictionary
    '''

    # Make request and return dict results
    response = requests.get(search_url)
    results = response.json()
    return results

def zip_make_request_with_cache(search_url, zipcode):
    '''Check the cache for a saved result for this baseurl+params:values
    combo. If the result is found, return it. Otherwise send a new
    request, save it, then return it.

    AUTOGRADER NOTES: To test your use of caching in the autograder, please do the following:
    If the result is in your cache, print "fetching cached data"
    If you request a new result using make_request(), print "making new request"

    Do no include the print statements in your return statement. Just print them as appropriate.
    This, of course, does not ensure that you correctly retrieved that data from your cache,
    but it will help us to see if you are appropriately attempting to use the cache.

    Parameters
    ----------
    baseurl: string
        The URL for the API endpoint
    hashtag: string
        The hashtag to search for
    count: integer
        The number of results you request from Twitter
    api_label: string
        A string of either "yelp" or "zip" to
        differentiate between keys needed

    Returns
    -------
    dict
        the results of the query as a dictionary loaded from cache
        JSON
    '''
    CACHE_DICT = open_cache()

    # Using our unique key function to save and search keys in our cache
    query_url = f'{search_url}{zipcode}/degrees'

    # See if this query has already been done (and is saved in cache)
    if query_url in CACHE_DICT.keys():
        print('fetching cached data')
        return CACHE_DICT[query_url]

    # If query is not in cache, make new get request,
    # save in cache & return data from cache
    else:
        print('making new request')
        CACHE_DICT[query_url] = zip_make_request(query_url)
        save_cache(CACHE_DICT)
        return CACHE_DICT[query_url]

# Yelp Fusion Class (?)

# Yelp Fusion API Functions

if __name__ == "__main__":
    conn.execute(create_yelp)
    conn.execute(create_zip)
    conn.commit()
    # Zip API example for access

    # resp = zip_make_request_with_cache(zip_base, '48109')
    # print(resp)

    # Yelp API example for access

    # resp = requests.get(yelp_base,params={'latitude':37.786882,
    #                                         'longitude':-122.399972}, headers={'Authorization': 'Bearer {}'.format(yelp_key)})
    # print(resp.json())


    # conn.execute(insert_zip, ['48109', 'Ann Arbor', 'MI', '3838.3', '38383.3', 'EST'])
    # conn.execute(insert_yelp, ['ben & jerrys', 'ice cream', '$$', '734-xxx-xxxx', '48109', 'open', 'state st', 'ann arbor', 'MI'])
    # conn.commit()

