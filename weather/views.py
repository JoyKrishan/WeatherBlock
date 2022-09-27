from datetime import date, timedelta
from glob import glob
import json
from django.shortcuts import render
from .forms import DateForm
from urllib.parse import urlencode
import requests
import asyncio
from ethairballoons.ethairballoons import ethairBalloons
import ast



BASE_API_URL ="https://api.worldweatheronline.com/premium/v1/past-weather.ashx?"
LOCATION = "Dhaka"
API_KEY = "ab021207000e4e7286d143115222509"
FORMAT = "json"
DATA_RETREIVED = False
MYSCHEMA = None

def createSchema():
    global MYSCHEMA
    provider = ethairBalloons('127.0.0.1', '../')
    mySchema = provider.createSchema(modelDefinition ={
        'name': "Weather",
        'contractName': "weatherContract",
        'properties': [{
            'name': "date",
            'type': "bytes32",
            'primaryKey': True
        },
        {
            'name': "maxTempC",
            'type': "bytes32"
        },
        {
            'name': "maxTempF",
            'type': "bytes32"
        }]
    })
    MYSCHEMA = mySchema
    mySchema.deploy()

def buildSchema(data):
    global MYSCHEMA
    for info in data:
        date, max_temp_C, max_temp_F = info
        save_receipt = MYSCHEMA.save({
            'date': date,
            'maxTempC':max_temp_C,
            'maxTempF':max_temp_F
        })
        print(save_receipt)



def get_full_url_with_enddate():
    today_date = date.today()
    date_thirty_days_ago = (today_date - timedelta(days=30))
    # print(today_date.strftime("%Y-%m-%d"))
    # print(date_thirty_days_ago.strftime("%Y-%m-%d"))

    params = {"q":LOCATION, "key":API_KEY, "date":date_thirty_days_ago.strftime("%Y-%m-%d"), "enddate":today_date.strftime("%Y-%m-%d"), "format":FORMAT}
    full_url = BASE_API_URL + urlencode(params)
    print(full_url)
    return full_url

def get_full_url(picked_date):
    """
        Generates the full_url required to make an API call
        params -> str:date, 
        return -> str:full_url 
    """
    params = {"q":LOCATION, "key":API_KEY, "date":picked_date, "format":FORMAT}
    full_url = BASE_API_URL + urlencode(params)
    return full_url

async def get_json_data_custom(full_url):
    response = requests.get(full_url)
    thirty_days_weather_data = []
    if response.status_code == 200: # success
        data_dump= json.loads(response.text)
        #print(data_dump)
        weather_data = data_dump['data']['weather']
        for info in weather_data:
            retreived_date = info['date']
            max_temp_C = info['maxtempC']
            max_temp_F = info['maxtempF']
            thirty_days_weather_data.append([retreived_date,max_temp_C, max_temp_F])
    return thirty_days_weather_data

def get_json_data(full_url):
    response = requests.get(full_url)
    if response.status_code == 200: # success
        data_dump= json.loads(response.text)
        max_temp_C = data_dump['data']['weather'][0]['maxtempC']
        max_temp_F = data_dump['data']['weather'][0]['maxtempF']

        return max_temp_C,max_temp_F


async def index(request):
    if request.method == "POST":
        form = DateForm(request.POST)
        if form.is_valid():
            print(form.cleaned_data)
            picked_date = form.cleaned_data['date_field']
            picked_date_str = picked_date.strftime("%Y-%m-%d")
            record = ast.literal_eval(MYSCHEMA.findById(picked_date_str))
            # full_url = get_full_url(picked_date_str)
            # max_temp_C, max_temp_F = get_json_data(full_url)
            user_message = f"The max tempature for {record['date']} is {record['maxTempC']} Celcius and {record['maxTempF']} Farhenheit."
            new_form = DateForm()
            return render(request, 'weather/index.html', {'form': new_form, 'user_message':record})

    else: # Get Request
        url = get_full_url_with_enddate()
        thirty_days_data = await get_json_data_custom(url)
        print(thirty_days_data)
        createSchema()
        buildSchema(thirty_days_data)
        form = DateForm()
    return render(request, 'weather/index.html', {'form':form})

