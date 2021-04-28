# Final_Proj
This Project is for SI 507, Winter 2021. It is the Final Project. 
This Project accesses the Zipcode API (https://www.zipcodeapi.com/API) and the Yelp Fusion API (https://www.yelp.com/developers/documentation/v3/get_started)


When using this python program, please ensure that you have the packages below:
- json
- requests
- sqlite3
- flask (Flask, render_template, request)

Please supply API keys in a file named secrets.py
In secrets.py, label the Zipcode API key as zip_api_key

Also, label the Yelp Fusion API key as yelp_api_key

When running this program, the user will interact via Flask in an html page, which should open in a local browser. 
The user may enter a valid zip code (examples provided), and receive location information. 
Then, the user may search the same zipcode, or a new zipcode, and recieve information about businesses nearby that are on Yelp. 
The user may display sorted results by selecting the feature to sort and the direction of the sort.

Please hit Ctrl + C in the Python terminal to close the Flask program when done. 
