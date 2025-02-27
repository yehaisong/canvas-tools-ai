import json
import canvas_requests as cr

def create_module_item(course_id, module_id, module_item):
    endpoint = "courses/" + str(course_id) + "/modules/" + str(module_id) + "/items"
    payload = module_item
    response = cr.post(endpoint=endpoint,json=payload)
    return response.json()

def delete_module_item(course_id, module_id, module_item_id):
    endpoint = "courses/" + str(course_id) + "/modules/" + str(module_id) + "/items/" + str(module_item_id)
    response = cr.delete(endpoint=endpoint)
    return response

def get_module_items(course_id, module_id):
    endpoint = "courses/" + str(course_id) + "/modules/" + str(module_id) + "/items"
    response = cr.get(endpoint=endpoint)
    return response.json()