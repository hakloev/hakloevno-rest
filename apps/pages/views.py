from collections import defaultdict

from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.http import require_safe

import json
import requests
import requests_cache
import xml.etree.ElementTree as ET

# Create your views here.
BASE_YR_API_URL = 'http://api.yr.no/weatherapi/'
LOCATION_FORECAST_ENDPOINT = 'locationforecast/1.9/'  # ?lat=60.10;lon=9.58
LOCATION_TEXT_ENDPOINT = 'textlocation/1.0/'  # ?latitude=60.10;longitude=9.58;language=nb

requests_cache.install_cache('yr_api_cache', expire_after=1800)  # Cache for 30 minutes


def validate_weather_api_query_parameters(lat, lon):
    if not lat or not lon:
        # TODO: Check if on correct format, i.e., x.xx
        return False
    return True


@require_safe
def weather_text(request):
    """
    GET-route that proxies requests to api.yr.no/../textlocation/ and translates the returning XML into JSON
    Required: ?lat=x.xx&lon=y.yy
    :param request:
    :return: JsonResponse
    """
    lat, lon = request.GET.get('lat', None), request.GET.get('lon', None)

    if not validate_weather_api_query_parameters(lat, lon):
        return JsonResponse({
            "error": "Invalid query parameters."
        }, status=400)

    r = requests.get(BASE_YR_API_URL + LOCATION_TEXT_ENDPOINT, params={
        'latitude': lat,
        'longitude': lon,
        'language': 'nb'
    })

    if r.status_code is not requests.codes.ok:
        return JsonResponse({
            "originUrl": r.url,
            "status": r.status_code,
            "error": r.reason,
        }, status=r.status_code)

    tree = ET.ElementTree(ET.fromstring(r.text))
    text_forecasts = []

    for forecast in tree.findall('./time'):  # Find all <time>-nodes
        temp_forecast = forecast.attrib

        location = forecast.find('./location')  # Find the <location>-node
        if location is not None:
            temp_forecast.update(location.attrib)
            forecast_text = location.find('./forecast')  # Find the <forecast>-node
            if forecast_text is not None:
                temp_forecast['forecast'] = forecast_text.text

        text_forecasts.append(temp_forecast)

    return JsonResponse({
        'originUrl': r.url,
        'forecasts': text_forecasts,
    })


@require_safe
def weather_forecast(request):
    """
    GET-route that proxies requests to api.yr.no/../locationforecast/ and translates the returning XML into JSON
    Required: ?lat=x.xx&lon=y.yy
    :param request:
    :return: JsonResponse
    """
    lat, lon = request.GET['lat'], request.GET['lon']

    if not validate_weather_api_query_parameters(lat, lon):
        return JsonResponse({
            "error": "Invalid query parameters."
        }, status=400)

    r = requests.get(BASE_YR_API_URL + LOCATION_FORECAST_ENDPOINT, params={'lat': lat, 'lon': lon})

    if r.status_code is not requests.codes.ok:
        return JsonResponse({
            "originUrl": r.url,
            "status": r.status_code,
            "error": r.reason,
        }, status=r.status_code)

    tree = ET.ElementTree(ET.fromstring(r.text))
    forecasts = defaultdict(dict)

    for forecast in tree.findall('./product/time'):  # Find every <time>-node
        identifier = forecast.attrib.get('to')  # Sort/identify by to-attribute
        temp_forecast = forecasts[identifier]

        temp_forecast.update(forecast.attrib)  # Update attributes

        location = forecast.find('./location')  # Find <location>-node in <time>-node

        if location.find('./symbol') is None:  # Check if it is not a <location>-node with symbol data
            for child in location:
                child.attrib.pop('id', None)
                temp_forecast[child.tag] = child.attrib  # Add all child data to child tag in temp_forecast
        else:
            #  <location>-node with symbol data, update accordingly
            temp_forecast['icon'] = location.find('./symbol').attrib
            temp_forecast['precipitation'] = location.find('./precipitation').attrib
            #  Check if the node has temperature data and update accordingly
            if location.find('./minTemperature') is not None and location.find('./maxTemperature') is not None:
                location[1].attrib.pop('id', None)
                location[2].attrib.pop('id', None)
                temp_forecast['minTemperature'] = location[1].attrib
                temp_forecast['maxTemperature'] = location[2].attrib

        temp_forecast.update(location.attrib)

        forecasts[identifier].update(temp_forecast)

    return JsonResponse({
        "originUrl": r.url,
        "forecasts": list(forecasts.values()),
    })
