import json
import canvas_requests as cr

def deleteQuizQuestion(courseid,quizid,questionid):
    target_endpoint="courses/"+str(courseid)+"/quizzes/"+str(quizid)+"/questions/"+str(questionid)
    target_response = cr.delete(endpoint=target_endpoint,params={})
    print(f'{target_endpoint} - {target_response}')

def createQuiz(courseid,quiz):
    target_endpoint="courses/"+str(courseid)+"/quizzes"
    target_response = cr.post(
        endpoint=target_endpoint,params={},
        json=quiz)
    print(f'{target_endpoint} - {target_response}')
    return json.loads(target_response.content)

def listQuestions(courseid,quizid):
    target_endpoint="courses/"+str(courseid)+"/quizzes/"+str(quizid)+"/questions/"
    target_response = cr.get(
        endpoint=target_endpoint,params={})
    return json.loads(target_response.content)

def addQuestion(courseid,quizid,question):
    target_endpoint="courses/"+str(courseid)+"/quizzes/"+str(quizid)+"/questions"
    target_response = cr.post(
        endpoint=target_endpoint,params={},
        json=question)
    print(f'{target_endpoint} - {target_response}')

def deleteQuiz(courseid,quizid):
    target_endpoint="courses/"+str(courseid)+"/quizzes/"+str(quizid)
    target_response = cr.delete(
        endpoint=target_endpoint,params={})
    print(f'{target_endpoint} - {target_response}')

def getQuizzes(courseid):
    target_endpoint="courses/"+str(courseid)+"/quizzes"
    target_response = cr.get(
        endpoint=target_endpoint,params={})
    return json.loads(target_response.content)

def getQuizReport(courseid,quizid):
    target_endpoint="courses/"+str(courseid)+"/quizzes/"+str(quizid)+"/reports"
    target_response = cr.get(
        endpoint=target_endpoint,params={})
    return json.loads(target_response.content)

def updateQuiz(courseid,quizid,quiz):
    target_endpoint="courses/"+str(courseid)+"/quizzes/"+str(quizid)
    target_response = cr.put(
        endpoint=target_endpoint,params={},
        json=quiz)
    print(f'{target_endpoint} - {target_response}')

def getExams(courseid,name):
    target_endpoint="courses/"+str(courseid)+"/quizzes"
    target_response = cr.get(
        endpoint=target_endpoint,params={})
    quizzes = json.loads(target_response.content)
    exams = []
    for q in quizzes:
        if(q["title"].lower().find(name.lower())!=-1):
            exams.append(q)            
    return exams
