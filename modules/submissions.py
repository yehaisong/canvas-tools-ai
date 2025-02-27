import json
import canvas_requests as cr

def get_submissions(course_id, assignment_id,include:list=[]):
    endpoint = f"courses/{course_id}/assignments/{assignment_id}/submissions"
    response = cr.get(endpoint=endpoint,params={"include[]":include})
    submissions = []
    if response.status_code == 200:
        while True:
            paged_submissions = response.json()
            for s in paged_submissions:
               submissions.append(s)
            if ("last" in response.links and response.links["current"]["url"]!=response.links["last"]["url"]) or ("next" in response.links and response.links["current"]["url"]!=response.links["next"]["url"]):
                response=cr.get_raw_url(response.links["next"]["url"])
            else:
                break
    return submissions

def get_submission(course_id, assignment_id, user_id, include:list=[]):
    endpoint = f"courses/{course_id}/assignments/{assignment_id}/submissions/{user_id}"
    response = cr.get(endpoint=endpoint,params={"include[]":include})
    return response.json()

def delete_submission_comment(course_id, assignment_id, user_id, comment_id):
    endpoint = f"courses/{course_id}/assignments/{assignment_id}/submissions/{user_id}/comments/{comment_id}"
    response = cr.delete(endpoint=endpoint)
    return response
                           
def grade_submission(courseid,assignmentid,userid,grade_results):
    endpoint = f"courses/{courseid}/assignments/{assignmentid}/submissions/{userid}"
    response = cr.put(endpoint=endpoint, json=grade_results)
    return response

def update_grade(courseid,assignmentid,userid,new_grade):
    endpoint = f"courses/{courseid}/assignments/{assignmentid}/submissions/{userid}"
    grade_results = {"submission":
        {
            "posted_grade":new_grade
            }
        }
    response = cr.put(endpoint=endpoint, json=grade_results)
    return response  