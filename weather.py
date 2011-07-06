#!/usr/bin/env python
#
# CDYNE Weather Python Module
# By Brandon Smith (brandon.smith@studiobebop.net)
#
import socket, httplib, urllib, urllib2
import xml.etree.ElementTree as etree
import time

class session:
    # Private Utility Functions
    def __init__(self):
        self.__action_url = "http://wsf.cdyne.com/WeatherWS/Weather.asmx"
        self.__max_retries = 5

    def __process_sub_elements(self, element):
        dictionary = {}
        for sub_element in element.getchildren():
            sub_element_name = sub_element.tag.split("}")[1]
            if sub_element.getchildren():
                values = []
                for sub_sub_element in sub_element.getchildren():
                    values.append(self.__process_sub_elements(sub_element))
                new_values = []
                for value in values:
                    if value not in new_values:
                        new_values.append(value)
                sub_element_value = new_values
            else:
                sub_element_value = sub_element.text
            dictionary[sub_element_name] = sub_element_value
        return dictionary

    def __xml_to_dictionary(self, xml):
        if type(xml) != etree.Element:
            root = etree.XML(xml)
        else:
            root = xml
        dictionary = {}
        if root is not None:
            for element in root.getchildren():
                element_name = element.tag.split("}")[1]
                if element.getchildren():
                    values = []
                    for sub_element in element.getchildren():
                        values.append(self.__process_sub_elements(sub_element))
                    element_value = values
                else:
                    element_value = element.text
                dictionary[element_name] = element_value
        return dictionary

    def __get_request(self, request):
        """
        Return contents of a given request
        """
        for i in range(0, self.__max_retries):
            try:
                return urllib2.urlopen(request).read()
            except urllib2.URLError:
                time.sleep(3)
            except httplib.BadStatusLine or httplib.InvalidURL:
                time.sleep(3)
            except socket.error or socket.timeout:
                time.sleep(3)
            except:
                import traceback
                traceback.print_exc()
        raise NameError("Failed to grab URL: %s", request)

    def __send_request(self, data, function):
        request_url = self.__action_url + "/%s" % function
        request_url += "?%s" % urllib.urlencode(data)
        response = self.__get_request(request_url)
        return self.__xml_to_dictionary(response)

    # Data retrieval functions
    def get_city_weather_by_zip(self, zip):
        """Gets current weather for a city based on zip code."""
        data = {"ZIP": zip}
        return self.__send_request(data, "GetCityWeatherByZIP")

    def get_city_forecast_by_zip(self, zip):
        data = {"ZIP": zip}
        return self.__send_request(data, "GetCityForecastByZIP")