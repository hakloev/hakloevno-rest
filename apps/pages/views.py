from collections import defaultdict
from django.http import JsonResponse
from django.views.decorators.http import require_safe

import requests
import requests_cache
import xml.etree.ElementTree as ET

# Create your views here.
BASE_YR_API_URL = 'http://api.yr.no/weatherapi/'
LOCATION_FORECAST_ENDPOINT = 'locationforecast/1.9/'  # ?lat=60.10;lon=9.58

requests_cache.install_cache('yr_api_cache', expire_after=1800)  # Cache for 30 minutes


@require_safe
def weather_api(request):
    """
    GET-route that proxies requests to api.yr.no and translates the returning XML into JSON
    Required: ?lat=x.xx&lon=y.yy
    :param request:
    :return: JsonResponse
    """
    lat, lon = request.GET['lat'], request.GET['lon']

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
