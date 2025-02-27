import json
import canvas_requests as cr

def create_rubric(course_id, rubric):
    endpoint = "courses/" + str(course_id) + "/rubrics"
    response = cr.post(endpoint=endpoint,json=rubric)
    return response.json()