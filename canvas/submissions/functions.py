import sys
import json
import csv
import time
from urllib.request import urlretrieve
sys.path.append("../modules")
import helper
import canvas_requests as cr
import submissions as cs
import assignments as ca
import course as cc
from datetime import date,datetime
import ctlassistant as at
import os
from gradingpolicy import setAssignmentPostPolicy


DEFAULT_CHAT_MODEL = at.CHAT_MODEL[3]


def get_current_term_id()->str:
    """Get the current term id.

    Returns:
        int: the current term id
    """
    endpoint = "accounts/1/terms"
    params = {
        "term_name":"Spring Semester 2025"
    }
    return 274
    

def get_courses(search_term:str="",term_id:int=0)->list:
    """Get all the courses that the user is enrolled in.

    Returns:
        list: a list of courses
    """
    return cc.get_courses(1,search_term,False,term_id)

def get_assignments(courseid:int)->list:
    """Get all the assignments in a course.

    Args:
        courseid (int): course id

    Returns:
        list: a list of assignments
    """
    return ca.get_assignments(courseid)

def find_rating(criterion, rating_id:str):
    """Find a rating item by the rating_id.

    Args:
        criterion (any): a criterion object
        rating_id (str): the target rating_id

    Returns:
        any: the rating item
    """
    for rating in criterion["ratings"]:
        if rating["id"] == rating_id:
            return rating
    return None

def append_to_csv(file_path, rows):
    """Append rows to a csv file. If the file does not exist, create a new file and write the header.

    Args:
        file_path (str): file path
        rows (list[dict[str, Any]]): row to append. the first row should be the header.
    """
    file_exists = os.path.isfile(file_path)
    with open(file_path, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(rows[0].keys())  # Write header if file is newly created
        for row in rows:
            writer.writerow(row.values())

def parse_feedback_with_rubric(courseid, assignmentid, username, studentid, rubric, feedback, cost:str):
    """Parse feedback with rubric and generate the following:
    - markdown string
    - feedback json object
    - csv rows

    Args:
        courseid (int): course id
        assignmentid (int): addignment id
        username (str): username
        studentid (int): student id
        rubric (any): grading rubric
        feedback (any): feedback from the AI model
        cost (str): comma separated cost string, format: "prompt_tokens,completion_tokens,total_tokens,cost,processtime"

    Returns:
         - markdown string
         - feedback json object
        - csv rows
    """
    date_time_string=f'{datetime.now().strftime("%m/%d/%Y %H:%M:%S")} GMT'
    md_string = "## Assessment\n\n"
    show_username = ""
    if(username!=""):
        show_username = f"Student Name: {username}; "
    md_string += f"Course ID: {courseid}; Assignment ID: {assignmentid}; {show_username}Student ID: {studentid}\n\n"
    md_string += f"Generated: {date_time_string}\n\n"
    # write overall comment
    md_string += f"\n## Overall Comments\n\n{feedback['comment']['text_comment']}\n\n"
    # csv row
    csv_row =[courseid,assignmentid,studentid]
    # go through rubric assessments
    if(rubric!=None):
        md_string += f"|Critetion|Rating|Points|Comments|\n|---|---|---|---|\n"
        rubric_assessments = feedback["rubric_assessment"]
        total_points = 0
        for criterion in rubric:
            rubric_assessment = rubric_assessments[criterion["id"]]
            # create an empty rating item
            rating = {"description":"","long_description":""}
            # get rating_id if supplied
            if("rating_id" in rubric_assessment):
                rating = find_rating(criterion, rubric_assessment["rating_id"])
                rating["description"] = rating["description"].replace("\n"," ")
                rating["long_description"] = rating["long_description"].replace("\n"," ")
            # write a rubric assessment
            md_string += f"|{criterion['description']}|**{rating['description']}**<br>{rating['long_description']}|{rubric_assessment['points']}/{criterion['points']}|{rubric_assessment['comments']}|\n"
            total_points += float(rubric_assessment["points"])
            csv_row.append (float(rubric_assessment["points"]))
        md_string += f"\n## Total Points\n\n{total_points}"  
        csv_row.append(total_points)
    else:
        md_string += f'\n## Total Points\n\n{feedback["submission"]["posted_grade"]}'  
    # write cost
    tokens=cost.split(",")
    md_string += f"\n## Cost\n\nmodel: {DEFAULT_CHAT_MODEL['model']}; prompt token: {tokens[0]}; completion token: {tokens[1]}; total token: {tokens[2]}; cost: ${tokens[3]}; time: {tokens[4]}s"
    #append tokens to feedback
    feedback["tokens"]={}
    feedback["tokens"]["prompt_tokens"]=tokens[0]
    feedback["tokens"]["completion_tokens"]=tokens[1]
    feedback["tokens"]["total_tokens"]=tokens[2]
    feedback["cost"]=tokens[3]
    feedback["processtime"]=tokens[4]
    feedback["timestamp"]=date_time_string
    feedback["model"]=DEFAULT_CHAT_MODEL["model"]
    #prepare for csv
    csv_row.append(tokens[3])
    csv_row.append(tokens[4])
    csv_row.append(date_time_string)
    columns = ["course_id","assignment_id","student_id"]
    n = len(csv_row)-7 # minus 3 for course_id, assignment_id, student_id, minus 3 for total_points, cost,  processtime, and timestamp
    for i in range(n):
        columns.append(f"criterion_{i+1}")
    columns.append("total_points")
    columns.append("cost")
    columns.append("processtime")
    columns.append("timestamp")
    csv_rows = [dict(zip(columns, csv_row))] #header and row
    return md_string,feedback,csv_rows
    
        
def json_to_file(courseid, assignmentid, username, studentid, rubric, feedback, cost:str,timestamp:int):
    report_md_output_path=helper.check_path(f"temp/{courseid}/{assignmentid}/reports_md")
    report_json_output_path=helper.check_path(f"temp/{courseid}/{assignmentid}/reports_json")
    output_file = f'{report_md_output_path}/{username.replace(",","")}_{studentid}_{courseid}_{assignmentid}_{timestamp}.md'
    output_file_json = f'{report_json_output_path}/{username.replace(",","")}_{studentid}_{courseid}_{assignmentid}_{timestamp}.json'
    # dump md the output file
    md_string,json_feedback,rows = parse_feedback_with_rubric(courseid, assignmentid, username, studentid, rubric, feedback, cost)
    with open(output_file, "w", encoding="utf-8") as md_file:
        md_file.write(md_string)
    print(f"Results saved to {output_file}.")
    #dump json to the output file
    with open(output_file_json, mode="w", encoding="utf-8") as json_file:
        json.dump(json_feedback,json_file)
    # append to csv
    append_to_csv(f"temp/{courseid}/{assignmentid}/{courseid}_{assignmentid}_grades.csv", rows)
        
def grade_assignment(courseid:int, assignmentid:int, grading_guidelines:str="",grading_instructions_end:str="",userids:list=[],custom_rubric=None,show_username_in_report:bool=False,submit_grades:bool=False,override_grade:bool=False,save_to_file:bool=True, temperature:float=0.5,skip_graded:bool=True,top_n:int=-1):
    """Grade an assignment.

    Args:
        courseid (int): Canvas course id
        assignmentid (int): Canvas assignment id
        grading_guidelines (str, optional): Additional grading guidelines besides rubric. Defaults to "".
        grading_instructions_end (str, optional): Last words that you want to add onto the grading guidelines. Defaults to "".
        userids (list, optional): A list of users' submissions for grading. If the list empty, grade all users. Defaults to [].
        custom_rubric (dict, optional): A custom rubric for grading. You can use this to test rubric drafts. Or set a rubric other than the system one. Defaults to None.
        show_username_in_report (bool, optional): Show username in the report. Defaults to False.
        submit_grades (bool, optional): Submit grades and comments to Canvas. Defaults to False. If true, the assignment post policy will be set to manual post.
        override_grade (bool, optional): Only works when submit_grades is True. Override grades and comments if submissions have existing grades. Defaults to False.
        save_to_file (bool, optional): Save results to a file. Defaults to True.
        temperature (float, optional): The temperature of the AI model, 0-2. Defaults to 0.5.
        skip_graded (bool, optional): Skip graded submissions. Defaults to True.
        top_n (int, optional): Grade the top n submissions. Defaults to -1. If -1, grade all submissions.
    """
    if(submit_grades):
        setAssignmentPostPolicy(assignmentid,True)
        print(f"Assignment {assignmentid} post policy is set to mannual post.")
    skip_grading = False # turn on or off AI grading for testing purposes
    openai_call_delay_in_seconds = 10
    grading_system_instructions = f"You are an objective grader and can grade assignments in many subject areas. You will grade students' works based on the context, rubric, and additional guidelines provided by the instructor. Use a JSON object to provide your grading and feedback. If there is a rubric presented in the prompt, please grade based on each criterion first and then provide overall constructive feedback.  "
    grading_instructions_end += "Do not include feedback on rubric items in the overall comments."
    rubric_assessment_instructions = ""
    output_path=helper.check_path(f"temp/{courseid}/{assignmentid}")
    submission_files_path=helper.check_path(f"{output_path}/submissions")   
    # retrive the assignemnt from Canvas
    assignment = ca.get_assignment(courseid, assignmentid)
    #print (assignment["rubric"]
    # get the rubric
    rubric = None
    if("rubric" in assignment):
        rubric = assignment["rubric"]
    #print(rubric)
    # get the content of the assignment
    content:str = ""
    if("description" in assignment):
        content = assignment["description"]
    #print(content)
    ## get assignment settings
    use_rubric_for_grading:bool = False
    if("use_rubric_for_grading" in assignment):
        use_rubric_for_grading = assignment["use_rubric_for_grading"]
    free_form_criterion_comments:bool = True
    if("free_form_criterion_comments" in assignment):
        free_form_criterion_comments = assignment["free_form_criterion_comments"]
    if (rubric != None or custom_rubric != None): # and (use_rubric_for_grading)):
        # if there is a custom_rubric, always use it for grading.
        if custom_rubric != None:
            rubric = custom_rubric
            use_rubric_for_grading = True
        grading_instructions = f"## Rubric \n {rubric} \n ### Guidelines \n {grading_guidelines}\n Please use the guidelines above to grade students work. Make sure to use the grading guidelines, provide concise and constructive feedback for each criterion or question as instructed in the grading guidelines, and then provide a summary of the assessment. \n  "
        include_posted_grade_json_text = "" # for adjust json format if not use rubric for grading
        include_posted_grade_text = "" 
        if(not use_rubric_for_grading):
            include_posted_grade_json_text = ",\"submission\":{\"posted_grade\":\"[points]\"}"
            include_posted_grade_text = "and a posted_grade under the key 'submission'."
        if (not free_form_criterion_comments):
            # if free_form_criterion_comments is true, rating_id is not needed. use default rubric_assessment_instructions.
            # if free_form_criterion_comments is false, add rating_id to the json format.
            # specify the rating_id for each criterion in the rubric.
            rubric_assessment_instructions = f"The JSON object has the following keys: rubric_assessment and comment{include_posted_grade_text}. The rubric_assessment is an object based on the criteria in the grading guidelines. Each criterion in the rubric_assessment has a key using the rubric_criterion_id from the rubric, and inside of the key, it has points, rating_id, and comments. Each criterion has several rating categories. Pick the most appropriate rating and use the points for each criterion. If it has a range, pick the closest one. If you give a student the full grade for a criterion, put an empty string as the comments for the criterion. The total points are the points you are giving the student, and the comment is the overall feedback you are providing to the student. The JSON object should be in the following format: {{\"comment\":{{\"text_comment\":\"[overall feedback]\"}},\"rubric_assessment\":{{\"[rubric_criterion_id]\":{{\"points\":\"[points from the chosen rating category]\",\"rating_id\":\"[the id of the chosen rating category]\",\"comments\":\"[criterion comments]\"}}}}{include_posted_grade_json_text}}}. In the comments, replace line breaks with the html tag '<br>'."
        else:
            rubric_assessment_instructions = f"The JSON object has the following keys: rubric_assessment and comment{include_posted_grade_text}. The rubric_assessment is an object based on all the criteria in the grading guidelines. Each criterion in the rubric_assessment has a key using the rubric_criterion_id from the grading guideline, and inside of the key, it has points and comments. If you give a student the full grade for a criterion, put an empty string as the comments for the criterion. The total points are the points you are giving the student, and the comment is the overall feedback you are providing to the student. The JSON object should be in the following format: {{\"comment\":{{\"text_comment\":\"[overall feedback]\"}},\"rubric_assessment\":{{\"[rubric_criterion_id]\":{{\"points\":\"[10]\",\"comments\":\"[criterion comments]\"}}}}{include_posted_grade_json_text}}}. In the comments, replace line breaks with the html tag '<br>'."
    else:
        # if there is no rubric or use_rubric_for_grading is false, provide a general guideline
        grading_instructions = f"## Rubric \n {grading_guidelines} \n There is no rubric for this assignment. Please provide a overall grade with rationale and contructive feedback. \n"
        # specify the json format for grading without rubric.
        rubric_assessment_instructions = "The JSON object have the following keys: comment and submission. The submission key has a sub key posted_grade for the total points you are giving the student, and the comments is the overall feedback you are providing to the student. The JSON object should be in the following format: {\"comment\":{\"text_comment\":\"[overall feedback]\"},\"submission\":{\"posted_grade\":\"[points]\"}}"

    # get all submissions of the assignment
    submissions = cs.get_submissions(courseid, assignmentid,["user"])
    # numbering the graded submissions
    # {n}/{index}/{total_n}, n is the number of submissions should be graded, index is the index of the number of the current submission, total_n is the total number of submissions
    n = 0 # count the number of submissions should be graded
    index = 0 # the index of the number of the current submission
    total_n = len(submissions)
    timestamp = time.time_ns()
    print("(graded/scanned/total)")
    for submission in submissions:
       #get the user id
        index=index+1
        userid = submission["user_id"]
        username = ""
        if(show_username_in_report):
            username = f'{submission["user"]["sortable_name"]}'
        #Check submission status. If graded and SkipGraded is true or no submission, skip grading
        grade_state = submission["workflow_state"] #Possible values: “submitted”, “unsubmitted”, “graded”, “pending_review”
        #print(f"Grade state: {grade_state}")
        if (grade_state=="unsubmitted"):
            print(f"Skip {userid} ({n}/{index}/{total_n}). Unsubmitted.")
            continue
        
        n+=1
        if(top_n>0 and n>top_n):
            break
        
        elif (grade_state=="graded" and skip_graded):
            print(f"Skip {userid} ({n}/{index}/{total_n}). Skip graded.")
            continue
        #get the submission id
        #submissionid = submission["id"]
        # set conditions for grading. 
        # by user id
        # by grade_state, Possible values: “submitted”, “unsubmitted”, “graded”, “pending_review”
        if ((userid in userids) or (len(userids)==0)): #grade specified users or all users if not specified.
            starttime = time.time()
            print(f"Grading {userid} ({n}/{index}/{total_n}) ...")
            time.sleep(openai_call_delay_in_seconds)
            #TODO: check the type of the assignment submission. It could be a file or online text. Assumed it is online_upload
            temp_file = ""
            filename = ""
            temp_filename = ""
            #submisstion_type
            submission_type = submission["submission_type"]
            if(submission_type=="online_upload"):
                # save file
                if("attachments" in submission and len(submission["attachments"])>0):
                    file_url=submission["attachments"][0]["url"]
                    filename = submission["attachments"][0]["filename"]
                    temp_filename = f'{username.replace(",","")}_{userid}_{filename}'
                    temp_file = f'{submission_files_path}/{temp_filename}'
                    urlretrieve(file_url, temp_file)
            elif(submission_type=="discussion_topic"):
                #discussion topic
                temp_file = f'{submission_files_path}/{username.replace(",","")}_{userid}_discussion_topic.md'
                with open(temp_file, "w") as file:
                    for entry in submission["discussion_entries"]:
                        file.write(f'{entry["message"]}\n\n')
            elif(submission_type=="online_text_entry"):
                #online text entry
                temp_file = f'{submission_files_path}/{username.replace(",","")}_{userid}_online_text_entry.md'
                with open(temp_file, "w") as file:
                    file.write(f'{submission["body"]}\n\n')
            else:
                print(f"Skip {userid} ({n}/{total_n}). Unsupported submission type.{submission_type}")
            #TODO: get the file type and convert it to markdown. not just docs file.
            if (temp_file.endswith(".docx") or temp_file.endswith(".pdf") or temp_file.endswith(".md")):
            # extract content from file
                if(temp_file.endswith(".docx")):    
                    output = temp_file.replace(".docx",".md")
                    helper.convert_docx_to_md(temp_file,output)
                elif(temp_file.endswith(".pdf")):
                    output = temp_file.replace(".pdf",".md")
                    helper.convert_pdf_to_md(temp_file,output)
                else:
                    output = temp_file
                # compose prompt
                with open(output, "r") as file:
                    student_work = file.read()
                # grade
                messages = [
                    {
                        "role":"system",
                        "content":f"{grading_system_instructions} {rubric_assessment_instructions}. Remember, use a JSON object to provide your grading and feedback."
                    },
                    {
                        "role":"user",
                        "content":f"Please provide your grading and feedback for the following assignment from the student {username}. ## Assignment Content \n\n {content}.\n\n {grading_instructions}\n\n## Student Submission\n\n`{student_work}`\n{grading_instructions_end}"
                    }
                ]
                if(skip_grading):
                    continue
                feedback,tokens = at.chat(messages,response_format="json_object",temperature=temperature)
                #print(feedback)
                try:
                    feedback_json = json.loads(feedback)
                    endtime = time.time()
                    cost = f"{tokens},{round(endtime-starttime)}"
                    costs = cost.split(",")
                    print(f"prompt token: {costs[0]}; completion token: {costs[1]}; total token: {costs[2]}; cost: ${costs[3]}; time: {costs[4]}s")
                    if (save_to_file):
                        json_to_file(courseid, assignmentid, username, userid, rubric, feedback_json, f"{cost}",timestamp)
                    if (submit_grades and (grade_state!="graded" or override_grade)):
                        response = cs.grade_submission(courseid,assignmentid,userid,feedback_json)
                        print(response)
                    else:
                        print(f"Skip {userid} ({n}/{total_n}). override grade is false.")
                except Exception as e:
                    print(f"Error during grade {userid} ({n}/{total_n}). {e}")
            else:
                print(f"Skip {userid} ({n}/{total_n}). No attachement or unsupported file format.")
        else:
            print(f"Skip {userid} ({n}/{total_n}). Not in the list of users to grade.")

def get_submissions_grades(courseid:int, assignmentid:int)->str:
    """_summary_

    Args:
        courseid (int): course_id
        assignmentid (int): assignment_id

    Returns:
        str: csv file name with relative path
    """
    output_path=helper.check_path(f"temp/{courseid}/{assignmentid}")
    output_file = f"{output_path}/{courseid}_{assignmentid}_canvas_grades.csv"
    # clear the csv file
    if os.path.exists(output_file):
        os.remove(output_file)
    # retrive the assignemnt from Canvas
    submissions = cs.get_submissions(courseid, assignmentid,['rubric_assessment'])
    # clear the csv file
    total_points = 0
    for submission in submissions:
        if(submission["workflow_state"]=="graded"):
            #get the user id
            userid = submission["user_id"]
            #get the submission id
            #submissionid = submission["id"]
            points =[courseid,assignmentid,userid]
            columns = ["course_id","assignment_id","student_id"]
            if("rubric_assessment" in submission):
                rubric_assessments = submission["rubric_assessment"]
                #entered_score = submission["entered_score"]
                # go through rubric assessments   
                total_points = 0
                for key in rubric_assessments.keys():
                    rubric_assessment = rubric_assessments[key]
                    total_points += float(rubric_assessment["points"])
                    points.append (float(rubric_assessment["points"]))
                points.append(total_points)
                #prepare for csv
                n = len(points)-4
                for i in range(n):
                    columns.append(f"criterion_{i+1}")
                columns.append("total_points")
            else:
                points.append(submission["entered_score"])
                columns.append("total_points")
            rows = [dict(zip(columns, points))]
            append_to_csv(output_file, rows)
    return f"{courseid}_{assignmentid}_canvas_grades.csv"

def remove_all_submissions_grades(courseid:int, assignmentid:int):
    """_summary_

    Args:
        courseid (int): course_id
        assignmentid (int): assignment_id

    Returns:
        response
    """
    # retrive the assignemnt from Canvas
    submissions = cs.get_submissions(courseid, assignmentid,['rubric_assessment','submission_comments'])
    # clear the csv file
    total_points = 0
    for submission in submissions:
        remove_submission_grade(courseid,submission)


def remove_single_student_submission_grade(courseid:int, assignmentid:int, userid:int)->any:
    """_summary_

    Args:
        courseid (int): course_id
        assignmentid (int): assignment_id
        userid (int): user_id

    Returns:
        response
    """
    # retrive the assignemnt from Canvas
    submission = cs.get_submission(courseid, assignmentid,userid,['rubric_assessment','submission_comments'])
    return remove_submission_grade(courseid,submission)

def remove_submission_grade(courseid:int,submission:any):
    """_summary_

    Args:
        submission (any): submission object

    Returns:
        response
    """
    if(submission["workflow_state"]=="graded"):
        #get the user id
        userid = submission["user_id"]
        assignmentid = submission["assignment_id"]
        submission["posted_grade"]=None
        if("submission_comments" in submission):
            for comment in submission["submission_comments"]:
                commentid = comment["id"]
                #print (f'comment id: {commentid}')
                cs.delete_submission_comment(courseid,assignmentid,userid,commentid)
                #remove overall comments
        #get the submission id
        #submissionid = submission["id"]
        #reset rubric assessments
        if("rubric_assessment" in submission):
            rubric_assessments = submission["rubric_assessment"]
            #entered_score = submission["entered_score"]
            # go through rubric assessments   
            total_points = 0
            for key in rubric_assessments.keys():
                rubric_assessments[key]["rating_id"]=None
                rubric_assessments[key]["comments"]=""
                rubric_assessments[key]["points"]=None
            #print(rubric_assessments)
            print(f'delete {userid}-{cs.grade_submission(courseid,assignmentid,userid,{"rubric_assessment":rubric_assessments})}')