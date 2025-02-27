import sys
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from urllib.request import urlretrieve
import helper
import canvas_requests as cr
from datetime import date
from course import get_courses, push_blueprint_changes
from assignments import get_assignments


print(cr.API_URL)
print(cr.API_KEY)

_transport = RequestsHTTPTransport(
    url='https://cedarville.instructure.com/api/graphql',
    use_json=True,
    headers={
        "Authorization":f"Bearer {cr.API_KEY}"
    }
)

client = Client(
    transport=_transport,
    fetch_schema_from_transport=True
)

def setCoursePostPolicy(course_id:str, post_manually:bool):
    """Set the post policy for a course

    Args:
        course_id (str): The course
        post_manually (bool): True if the course should be posted manually, False if it should be posted automatically
    """
    query = gql('''
    mutation MyMutation($course_id: ID!, $post_manually: Boolean!)
    {
        __typename  setCoursePostPolicy(input: {courseId: $course_id, postManually: $post_manually}) 
        {
            errors {
                attribute
                message
                __typename
            }    
            postPolicy {
                postManually
                __typename
            }
        }
    }'''  )
    variables = {
        "course_id": f"{course_id}",
        "post_manually": post_manually
    }
    return client.execute(query, variables)

def setAssignmentPostPolicy(assignment_id:str, post_manually:bool):
    """Set the post policy for an assignment

    Args:
        assignment_id (str): The assignment id
        post_manually (bool): True if the assignment should be posted manually, False if it should be posted automatically

    Returns:
        _type_: result of the mutation
    """
    
    query = gql('''
    mutation MyMutation($assignment_id: ID!, $post_manually: Boolean!)
    {
        __typename  setAssignmentPostPolicy(input: {assignmentId: $assignment_id, postManually: $post_manually}) 
        {
            errors {
                attribute
                message
                __typename
            }    
            postPolicy {
                postManually
                __typename
            }
        }
    }'''  )
    variables = {
        "assignment_id": f"{assignment_id}",
        "post_manually": post_manually
    }
    
    return client.execute(query, variables)