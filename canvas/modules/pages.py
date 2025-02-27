import json
import canvas_requests as cr

def create_page(course_id, wiki_page):
    endpoint = "courses/" + str(course_id) + "/pages"
    payload = {
        'wiki_page':{
            'title': wiki_page['title'],
            'body': wiki_page['body'],
            'editing_roles': wiki_page['editing_roles'],
            'published': wiki_page['published'],
            'front_page': wiki_page['front_page'],
            'notify_of_update': wiki_page['notify_of_update']
        }
        
    }
    print (wiki_page['title'])
    response = cr.post(endpoint=endpoint,json=payload)
    return response.json()

def list_pages(course_id,search_term=None):
    endpoint = "courses/" + str(course_id) + "/pages"
    params = {
        "search_term":search_term,
        "published":True
    }
    response = cr.get(endpoint=endpoint,params=params)
    return response.json()

def get_page(course_id,page_id):
    endpoint = "courses/" + str(course_id) + "/pages/" + str(page_id)
    response = cr.get(endpoint=endpoint)
    return response.json()

def delete_page(course_id,page_id):
    endpoint = "courses/" + str(course_id) + "/pages/" + str(page_id)
    response = cr.delete(endpoint=endpoint)
    return response.json()

def update_page_body(course_id,page_id,wiki_page_body):
    endpoint = "courses/" + str(course_id) + "/pages/" + str(page_id)
    payload = {
        'wiki_page':{
            'body': wiki_page_body
        }
        
    }
    response = cr.put(endpoint=endpoint,json=payload)
    return response.json()