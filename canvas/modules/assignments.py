import json
import canvas_requests as cr

def get_assignment(course_id, assignment_id):
    endpoint =  f"courses/{course_id}/assignments/{assignment_id}"
    response = cr.get(endpoint=endpoint)
    return response.json() 

def list_assignments(course_id,search_term=None):
    endpoint = f"courses/{course_id}/assignments"
    if search_term:
        response = cr.get(endpoint=endpoint, params={"search_term": search_term})
    else:
        response = cr.get(endpoint=endpoint)
    return response.json()

def get_assignments(courseid:int):
    assignments = []
    response = cr.get("courses/"+str(courseid)+"/assignments?&per_page=100",{})
    #check all pages
    while True:
        rawobjects = json.loads(response.content)
        #check each page for body
        for object in rawobjects:           
            assignments.append(object)
        if ("last" in response.links and response.links["current"]["url"]!=response.links["last"]["url"]) or ("next" in response.links and response.links["current"]["url"]!=response.links["next"]["url"]):
            response=cr.get_raw_url(response.links["next"]["url"],{})
        else:
            break       
        
    return assignments

def get_single_assignment(courseid:int,assignmentid:int):
    return json.loads(cr.get(f"courses/{courseid}/assignments/{assignmentid}",{}).content)

def update_assignment(courseid:int,assignmentid:int,assignment:any):
    return cr.put(f"courses/{courseid}/assignments/{assignmentid}",json=assignment)

def create_assignment(courseid:int,assignment:any):
    return cr.post(f"courses/{courseid}/assignments",json=assignment)

def delete_assignment(courseid:int,assignmentid:int):
    return cr.delete(f"courses/{courseid}/assignments/{assignmentid}")

def create_assignment_override(courseid:int,assignmentid:int,assignmentoverride:any):
    return cr.post(f"courses/{courseid}/assignments/{assignmentid}/overrides",json=assignmentoverride)

def get_assignment_groups(courseid:int):
    return json.loads(cr.get(f"courses/{courseid}/assignment_groups",{}).content)

def get_assignments_in_group(courseid:int,groupid:int):
    return json.loads(cr.get(f"courses/{courseid}/assignment_groups/{groupid}/assignments",{}).content)

def edit_assignment(course_id, assignment_id, data):
    endpoint =  f"courses/{course_id}/assignments/{assignment_id}"
    response = cr.put(endpoint=endpoint, json=data)
    return response.json()