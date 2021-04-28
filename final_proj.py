#########################################
##### Name: Taylor Marlin           #####
##### Uniqname:    taylmarl         #####
#########################################

import json
import requests
import sqlite3
import secrets as pysecrets # file with api keys
from flask import Flask, render_template, request

app = Flask(__name__)

CACHE_FILENAME = "final_cache.json"
CACHE_DICT = {}


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
        "Latitude"  TEXT NOT NULL,
        "Longitude" TEXT NOT NULL,
        "City"      TEXT NOT NULL,
        "State"     TEXT NOT NULL,
        "Timezone"  TEXT NOT NULL
    );
'''

create_yelp = '''
    CREATE TABLE IF NOT EXISTS "yelp" (
        "Name"      TEXT NOT NULL,
        "Zipcode"   TEXT NOT NULL,
        "Business_Type"     TEXT NOT NULL,
        "Phone"     TEXT NOT NULL,
        "Address" TEXT NOT NULL,
        "Reviews"  TEXT NOT NULL,
        "Rating"   TEXT NOT NULL,
        "Price"     TEXT NOT NULL,
        "Link"      TEXT NOT NULL PRIMARY KEY UNIQUE,

        FOREIGN KEY(Zipcode) REFERENCES zipcodes(Zipcode)
    );
'''

insert_zip = '''
    INSERT OR IGNORE INTO zipcodes
    VALUES(?, ?, ?, ?, ?, ?)
'''

insert_yelp = '''
    INSERT OR IGNORE INTO yelp
    VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)
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
    if 'error_code' in results.keys():
        return None
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

def get_zip_instance(json_results):
    '''Parse Zipcode API results and print location information.
    
    Parameters
    ----------
    json_results: dict
        dictionary containing response from Zipcode API
    '''
    if json_results is None:
        return None

    if 'zip_code' in json_results.keys():
        zipcode = json_results['zip_code']
    else:
        zipcode = 'No Zipcode'

    if 'lat' in json_results.keys():
        latitude = json_results['lat']
    else:
        latitude = 'No Latitude'

    if 'lng' in json_results.keys():
        longitude = json_results['lng']
    else:
        longitude = 'No Longitude'

    if 'city' in json_results.keys():
        city = json_results['city']
    else:
        city = 'No City'

    if 'state' in json_results.keys():
        state = json_results['state']
    else:
        state = 'No State'

    if 'timezone' in json_results.keys():
        if 'timezone_abbr' in json_results['timezone'].keys():
            timezone = json_results['timezone']['timezone_abbr']
        else:
            timezone = 'No Timezone'
    else:
        timezone = 'No Timezone'


    return Zipcode(zipcode, latitude, longitude, city, state, timezone)

# Yelp Fusion Class

class Yelp:
    '''information associated with yelp businesses.

    Instance Attributes
    -------------------
    name: string
        the name of the business

    zipcode: int
        zipcode of business

    bus_type: string
        the title or alias denoting the type of business

    phone: string
        the phone number for a business

    address: string
        the street address of a given business

    reviews: list
        abbreviaton for the timezone of a given zipcode

    rating: int
        average rating for a given business, from Yelp

    price: string
        string showing price of business using $ symbols

    link: string
        a string with the link to the business website
    '''
    def __init__(self, name, zipcode, bus_type, phone, address, reviews, rating, price, link):
        '''
        Initalize instance of Yelp business according to class spec
        '''
        self.name = name
        self.zipcode = zipcode
        self.bus_type = bus_type
        self.phone = phone
        self.address = address
        self.reviews = reviews
        self.rating = rating
        self.price = price
        self.link = link

    def info(self):
        '''
        Return nicely formatted information about Yelp object.
        '''
        # From https://stackoverflow.com/questions/45965007/multiline-f-string-in-python
        # python strings will concatenate in return statements when not comma-separated.
        return (
            f"{self.name} ({self.bus_type}) is located at {self.address}. \n"
            f"It has a price rating of: {self.price}. There are {self.reviews} reviews and a rating of {self.rating}. \n"
            f"More information can be found at {self.link}"
        )

# Yelp Fusion API Functions

def yelp_make_request(baseurl, params):
    '''Make a request to the Web API using the baseurl and params
    
    Parameters
    ----------
    baseurl: string
        The URL for the API endpoint
    params: dictionary
        A dictionary of param:value pairs
    
    Returns
    -------
    dict
        the data returned from making the request in the form of 
        a dictionary
    '''

    # Replace params dict with lowercase hashtags (or any other string params)
    for key, values in params.items():
        if type(values) == str:
            params[key] = values.lower()


    # Make request using params & oauth
    response = requests.get(url=baseurl,
                            params=params,
                            headers={'Authorization': 'Bearer {}'.format(yelp_key)})
    results = response.json()
    return results

def yelp_make_request_with_cache(baseurl, zipcode, term=None):
    '''Check the cache for a saved result for this baseurl+params:values
    combo. If the result is found, return it. Otherwise send a new
    request, save it, then return it.

    Parameters
    ----------
    baseurl: string
        The URL for the API endpoint
    zipcode: integer
        The zipcode to search for businesses nearby
    term: string
        search term to accompany location search, if supplied.
    limit: integer
        The number of results to request from Yelp Fusion API

    Returns
    -------
    dict
        the results of the query as a dictionary loaded from cache
        JSON
    '''
    #TODO Implement function
    CACHE_DICT = open_cache()
    # Saving parameters of location and limit into
    # dictionary for get request, if necessary.
    params = {'limit': 10}

    if zipcode is not None:
        params['location'] = zipcode

    if term is not None:
        params['term'] = term


    # Using our unique key function to save and search keys in our cache
    query_url = construct_unique_key(baseurl, params)

    # See if this query has already been done (and is saved in cache)
    if query_url in CACHE_DICT.keys():
        print('fetching cached data')
        return CACHE_DICT[query_url]

    # If query is not in cache, make new get request,
    # save in cache & return data from cache
    else:
        print('making new request')
        CACHE_DICT[query_url] = yelp_make_request(baseurl, params)
        save_cache(CACHE_DICT)
        return CACHE_DICT[query_url]

def yelp_database_insert(json_results):
    '''Parse Yelp API results and print nearby businesses.
    
    Parameters
    ----------
    json_results: dict
        dictionary containing response from Yelp API
    '''
    # verify that this key is valid
    conn = sqlite3.connect('Si507Proj.sqlite')
    cur = conn.cursor()

    if 'businesses' in json_results.keys():
        list_dict_nearby = json_results['businesses']
    else:
        return "No valid results."

    # Iterate through list of dictionaries containing nearby places & get fields
    for i in range(len(list_dict_nearby)):

        if 'name' in list_dict_nearby[i].keys():
            name = list_dict_nearby[i]['name']
        else:
            name = 'No Name'

        if 'location' in list_dict_nearby[i].keys():
            if 'zip_code' in list_dict_nearby[i]['location'].keys():
                zipcode = list_dict_nearby[i]['location']['zip_code']
            else:
                zipcode = 'No Zip'
            if 'address1' in list_dict_nearby[i]['location'].keys(): 
                address = list_dict_nearby[i]['location']['address1']
            else:
                address = 'No Address'
        else:
            zipcode = 'No Zip'
            address = 'No Address'


        if 'categories' in list_dict_nearby[i].keys():
            if len(list_dict_nearby[i]['categories']) > 0:
                if 'title' in list_dict_nearby[i]['categories'][0].keys():
                    bus_type = list_dict_nearby[i]['categories'][0]['title']
                else:
                    bus_type = 'No Type'
            else:
                bus_type = 'No Type'
        else:
            bus_type = 'No Type'

        if 'phone' in list_dict_nearby[i].keys():
            phone = list_dict_nearby[i]['phone']
        else:
            phone = 'No Phone'

        if 'review_count' in list_dict_nearby[i].keys():
            reviews = list_dict_nearby[i]['review_count']
        else:
            reviews = 'No Reviews'

        if 'rating' in list_dict_nearby[i].keys():
            rating = list_dict_nearby[i]['rating']
        else:
            rating = 'No Rating'

        if 'price' in list_dict_nearby[i].keys():
            price = list_dict_nearby[i]['price']
        else:
            price = 'No Price'

        if 'url' in list_dict_nearby[i].keys():
            link = list_dict_nearby[i]['url']
        else:
            link = 'No Link'

        obj = Yelp(name, zipcode, bus_type, phone, address, reviews, rating, price, link)
        cur.execute(insert_yelp, [obj.name, obj.zipcode, obj.bus_type, obj.phone, obj.address, obj.reviews, obj.rating, obj.price, obj.link])
    conn.commit()
    conn.close()

# Flask App Functionalities

def get_zip_results(zipcode):
    conn = sqlite3.connect('Si507Proj.sqlite')
    cur = conn.cursor()
    
    resp = zip_make_request_with_cache(zip_base, zipcode)
    obj = get_zip_instance(resp)
    if obj is None:
        return None
    conn.execute(insert_zip, [obj.zipcode, obj.latitude, obj.longitude, obj.city, obj.state, obj.timezone])
    conn.commit()

    q = f'''
        SELECT Zipcode, City, State, Timezone, Latitude, Longitude
        FROM zipcodes
        WHERE Zipcode == {zipcode}
    '''
    results = cur.execute(q).fetchall()
    conn.close()
    return results

def get_yelp_results(zipcode):
    conn = sqlite3.connect('Si507Proj.sqlite')
    cur = conn.cursor()

    response = yelp_make_request_with_cache(yelp_base, zipcode)
    yelp_database_insert(response)
    q = f'''
        SELECT Name, Business_Type, Phone, Address, Reviews, Rating, Price, Link
        FROM yelp
        WHERE Zipcode == {zipcode}'''

    results = cur.execute(q).fetchall()
    conn.close()
    return results

@app.route('/')
def index():
    # set up connection with database and establish cursor
    conn = sqlite3.connect('Si507Proj.sqlite')
    # cur = conn.cursor()

    conn.execute(create_zip)
    conn.execute(create_yelp)
    conn.commit()
    conn.close()
    return render_template('index.html')

@app.route('/zipresults', methods=['POST'])
def zipresults():
    zipcode = request.form['zipc']
    results = get_zip_results(zipcode)
    if results is None:
        return render_template('errorpage.html', results=results)
    return render_template('zipresults.html', results=results)

@app.route('/yelpresults', methods=['POST'])
def yelpresults():
    zipcode = request.form['zipc']
    results = get_yelp_results(zipcode)
    return render_template('yelpresults.html', results=results)



if __name__ == "__main__":
    app.run(debug=True)