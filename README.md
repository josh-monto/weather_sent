# CS 410 Final Project

This project was created to analyze local sentiment about weather in selected cities,
using both the Twitter API and National Weather Service API. This project can be run using
the Flask framework.

IMPORTANT NOTE: To access the Twitter API, a file named 'bearer_token.txt' must be added to the root
project folder and must contain only a bearer token from Twitter, which can be easily generated on
developer.twitter.com. This application is not a heavy user of data, it only generates one request to the Twitter API for every submission from the app, but be aware of rate limits regardless.

Project was created using:

Python 3.10.5
Node 19.2.0
NPM 8.9.13

For information on installing Node and NPM you can find information here:

https://docs.npmjs.com/downloading-and-installing-node-js-and-npm

To clone repository run the following from command line:
```
git clone https://github.com/josh-monto/weather_sent.git
```

As mentioned above, you need to generate a bearer token for accessing the Twitter API (instructions can be found at https://developer.twitter.com/en/docs/authentication/oauth-2-0/bearer-tokens). A file named `bearer_token.txt` must be added to project's root folder and contain only the generated bearer token.

It is recommended to run in a virtual environment (https://docs.python.org/3.10/library/venv.html)

Now, with Node and NPM installed, repository cloned, `bearer_token.txt` added, and virtual environment activated, navigate to project root folder in command line and run the following commands to set up d3, install all packages, and download stopwords folder:

```
npm init
npm install --save d3
pip install Flask, nltk, tweepy, noaa_sdk, vaderSentiment, pandas, rank_bm25
Python -m nltk.downloader stopwords
```

Now run the project:
I haven’t started FMECA stuff yet as I’m still working on the reliability, so you’ll be the first on this, though Sona White from Product Line will be joining tomorrow.
```
Python -m flask run
```

Navigate to http://127.0.0.1:5000 in browser window. The page may take up to 20 seconds to open.

Once the page opens, you can select a city from the dropdown menu and click Submit once (the Submit button does not currently deactivate while code runs). Wait up to 20 seconds for page to update with information for selected city.