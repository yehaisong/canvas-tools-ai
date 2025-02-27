import json
import canvas_requests as cr
def get_discussions(courseid):
    response = cr.get("courses/"+str(courseid)+"/discussion_topics?&per_page=100",{})
    return json.loads(response.content)

def update_discussion(courseid,discussionid,payload):
    response = cr.put("courses/"+str(courseid)+"/discussion_topics/"+str(discussionid),payload)
    print(response)
    return json.loads(response.content)