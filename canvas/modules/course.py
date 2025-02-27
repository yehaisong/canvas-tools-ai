import requests
import json
import os
import canvas_requests as cr

class Course:
    def __init__(self,id,code,name,syllabus):
        self.name = name
        self.id=id
        self.code=code
        self.syllabus=syllabus
    
    def serialize(self):
        _course={}
        _course["id"]=self.id
        _course["code"]=self.code
        _course["name"]=self.name
        _course["syllabus"]=self.syllabus
        return _course
    
def create_course(course:object):
    endpoint = f"accounts/{course['account_id']}/courses"
    response = cr.post(endpoint=endpoint,json=course,params={})
    if(response.status_code == 200):
        course = json.loads(response.content)
        return course["id"]
    else:
        return 0
    
def get_courses(account_id:int,search_term:str="",blueprint:bool=False,enrollment_term_id:int=0):
    endpoint = f"accounts/{account_id}/courses"
    params = {"blueprint":blueprint}
    if(search_term!=""):
        params["search_term"] = search_term
    if(enrollment_term_id!=0):
        params["enrollment_term_id"] = enrollment_term_id
    response = cr.get(endpoint=endpoint,params=params)
    courses = []
    if response.status_code == 200:
        while True:
            paged_courses = response.json()
            for s in paged_courses:
               courses.append(s)
            if ("last" in response.links and response.links["current"]["url"]!=response.links["last"]["url"]) or ("next" in response.links and response.links["current"]["url"]!=response.links["next"]["url"]):
                response=cr.get_raw_url(response.links["next"]["url"])
            else:
                break
    return courses

    

def enroll_users(courseid:int,emails:list,type:str):
    endpoint_user=f"accounts/1/users"
    for email in emails:
        #obtain user id by user's email
        users_response = cr.get(endpoint=endpoint_user,params={"search_term":f"{email}"})
        if(users_response.status_code == 200):
            users = json.loads(users_response.content)
            if(len(users)==0): #no user was found
                print (f"User not found: {email}")
            elif(len(users)==1): #one user  was found
                enroll_user(courseid,users[0]["id"],type)
            else: #multiple users were found
                i=0
                print(f"Multiple users were found: Enter the number to confirm the user.")
                while i<len(users):
                    print(str(i)+": "+ users[i]["name"])#+", "+users[i]["email"])
                    i+=1

                selected = input("Enter the number to confirm the user:")
                while (not selected.isdigit()) or (int(selected) < 0 or int(selected) >= len(users)):
                    selected = input("Enter the number to confirm the user:")
                #add selected user
                enroll_user(courseid,users[int(selected)]["id"],"TeacherEnrollment")
        else:
            print (f"User not found: {email}")

def enroll_user(courseid,userid,type):
    endpoint_enrollment = f"courses/{courseid}/enrollments"
    data = {
        "enrollment":{
            "user_id":userid,
            "type":type,
            "enrollment_state":"active"
        }
    }
    return cr.post(endpoint=endpoint_enrollment,json=data,params={})

def enroll_user_section(sectionid,userid,type,limit_privileges=True):
    endpoint_enrollment = f"sections/{sectionid}/enrollments"
    data = {
        "enrollment":{
            "user_id":userid,
            "type":type,
            "enrollment_state":"active",
            "limit_privileges_to_course_section":limit_privileges,
            "notify":False
        }
    }
    return cr.post(endpoint=endpoint_enrollment,json=data,params={})

def delete_course(id):
    endpoint = f"courses/{id}"
    return cr.delete(endpoint=endpoint,json={},params={"event":"delete"})

def update_course(id, course):
    endpoint = f"courses/{id}"
    return cr.put(endpoint=endpoint, params=course)

def push_blueprint_changes (course_id:int):
    endpoint = f"courses/{course_id}/blueprint_templates/default/migrations"
    payload = {
        "send_notification": False,
        "copy_settings": False
    }
    return cr.post(endpoint=endpoint,json=payload,params={})