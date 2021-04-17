#########################################
##### Name: Taylor Marlin           #####
##### Uniqname:    taylmarl         #####
#########################################

import json
import requests
import secrets as pysecrets # file with api keys

CACHE_FILENAME = "final_cache.json"
CACHE_DICT = {}

zip_key = pysecrets.zip_api_key
#zip_base = 
yelp_key = pysecrets.yelp_api_key
#yelp_base

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

def make_request(baseurl, params, api_key):
    '''Make a request to the Web API using the baseurl and params

    Parameters
    ----------
    baseurl: string
        The URL for the API endpoint
    params: dictionary
        A dictionary of param:value pairs
    api_label: string
        A string of either "yelp" or "zip", to
        differentiate which keys are needed

    Returns
    -------
    dict
        the data returned from making the request in the form of 
        a dictionary
    '''
    #TODO Implement function

    # Replace params dict with lowercase hashtags (or any other string params)
    for key, values in params.items():
        if type(values) == str:
            params[key] = values.lower()

    # Add key to params
    if api_key:
        params['key'] = api_key

    # Make request using params & oauth
    response = requests.get(url=baseurl,
                            params=params)
    results = response.json()
    return results

def make_request_with_cache(baseurl, hashtag, count, api_label):
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
    #TODO Implement function
    CACHE_DICT = open_cache()
    # Saving parameters of hashtag and count into
    # dictionary for get request, if necessary.
    params = {'q': hashtag.lower(), 'count': count}

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

        # Determine which api key we need
        if api_label.lower() == 'yelp':
            api_key = yelp_key
            baseurl = yelp_base
        elif api_label.lower() == 'zip':
            api_key = zip_key
            baseurl = zip_base
        else:
            api_key = None


        CACHE_DICT[query_url] = make_request(baseurl, params, api_key)
        save_cache(CACHE_DICT)
        return CACHE_DICT[query_url]