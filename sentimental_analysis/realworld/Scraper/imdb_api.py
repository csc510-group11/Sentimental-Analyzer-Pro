#nah not good
api_key = '<YOUR API KEY HERE>'

import requests

url = "https://imdb236.p.rapidapi.com/imdb/search"

querystring = {"primaryTitle":"Black Panther","type":"movie"}

headers = {
	"x-rapidapi-key": api_key,
	"x-rapidapi-host": "imdb236.p.rapidapi.com"
}

response = requests.get(url, headers=headers, params=querystring)

print(response.json())