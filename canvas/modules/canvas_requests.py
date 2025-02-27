import requests
import json
import os


API_KEY=os.getenv("CANVAS_API_TOKEN")
ENV=os.getenv("CANVAS_ENV")
PER_PAGE="?per_page="+os.getenv("PAGE_SIZE")
API_URL=os.getenv("API_URL")

def get(endpoint,params={},per_page=100):
    """wrapper of the requests.get function
    
    :param endpoint: an endpoint without the base url, for example, courses/83/assignments/23
    :param params: params to be passed to the api
    """
    
    return requests.get(url=API_URL+endpoint+PER_PAGE+str(per_page),params=params,headers={"Authorization": "Bearer "+API_KEY})

def get_raw_url(url,params={}):
    """wrapper of the requests.get function with a raw url
    
    :param url: a full url, for example, https://www.instructure.com/api/v1/courses/83/assignments/23
    :param params: params to be passed to the api
    """
    return requests.get(url=url,params=params,headers={"Authorization": "Bearer "+API_KEY})

def delete(endpoint,params={}):
    """wrapper of the requests.delete function
    
    :param endpoint: an endpoint without the base url, for example, courses/83/assignments/23
    :param params: params to be passed to the api
    """
    return requests.delete(url=API_URL+endpoint,params=params,headers={"Authorization": "Bearer "+API_KEY})

def put(endpoint,json={},params={},data={}):
    """wrapper of the requests.put function
    
    :param endpoint: an endpoint without the base url, for example, courses/83/assignments/23
    :param json: data for the api, the data needs to be updated
    :param params: params to be passed to the api
    """
    #print(json)
    #print(params)
    return requests.put(url=API_URL+endpoint,json=json,data=data,params=params,headers={"Authorization": "Bearer "+API_KEY})

def post(endpoint,json={},params={}):
    """wrapper of the requests.post function
    
    :param endpoint: an endpoint without the base url, for example, courses/83/assignments/23
    :param json: data for the api 
    :param params: params to be passed to the api
    """
    return requests.post(url=API_URL+endpoint,json=json,params=params,headers={"Authorization": "Bearer "+API_KEY})

def post_raw_url(url,json={},params={}):
    """wrapper of the requests.post function with a raw url
    
    :param url: a full url, for example, https://www.instructure.com/api/v1/courses/83/assignments/23
    :param json: data for the api 
    :param params: params to be passed to the api
    """
    return requests.post(url=url,json=json,params=params,headers={"Authorization": "Bearer "+API_KEY})