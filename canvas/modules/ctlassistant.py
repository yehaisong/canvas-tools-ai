from openai import OpenAI
import os
import time
import json
import math

API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI()
client.organization = os.getenv("ORG_ID")
client.api_key = API_KEY

MAX_HISTORY_MESSAGES = -10
CHAT_MODEL = [
    {
        "model": "gpt-4o",
        "input_cost":0.0025,
        "output_cost":0.010
    },
    {
        "model":"chatgpt-4o-latest",
        "input_cost":0.0025,
        "output_cost":0.010
    },
    {
        "model":"gpt-4o-mini",
        "input_cost":0.00015,
        "output_cost":0.0006
    },
    {
        "model":"o3-mini",
        "input_cost":0.0011,
        "output_cost":0.044
    }
]
IMAGE_MODEL = "dall-e-3"
VISION_MODEL = "gpt-4-vision-preview"

assistants = client.beta.assistants.list()
#for a in assistants:
#    print(f"{a.id},{a.name}")

def submit_message(assistantid:str,threadid:str,request_message:str,additional_instructions:str=None):
    message = client.beta.threads.messages.create(
        thread_id=threadid,
        role="user",
        content=request_message    
    )    
    #run the assistant
    run = client.beta.threads.runs.create(
        thread_id=threadid,
        assistant_id=assistantid,
        additional_instructions=additional_instructions        
    )
    run = wait_on_run(run,threadid)
    #return the response
    messages = client.beta.threads.messages.list(thread_id=threadid,order="asc",after=message.id)
    return get_messages(messages)    

def wait_on_run(run, threadid):
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(
            thread_id=threadid,
            run_id=run.id,
        )
        time.sleep(0.1)
    return run

def get_messages(messages):
    json_messages = []
    for m in messages:
        json_messages.append({"role":m.role,"content":m.content[0].text.value})
    return json_messages

def assistant(prompts,assistantid,additional_instructions=None):
    assistantid = assistantid #"asst_jvYLOj31VjH5ecI8l1AQbSum" #ctl id assistant
    
    #new thread if no threadid is provided
    thread = client.beta.threads.create()
    threadid = thread.id
    
    response = ""
     
    for prompt in prompts:
        #run the assistant
        json_messages = submit_message(assistantid,threadid,prompt["text"],additional_instructions)
        #save history
        for m in json_messages:        
            response += m["content"] + "\n"
            #print(m["content"]) 
        time.sleep(1)
    
    return response

def chat(messages:list,model:json=CHAT_MODEL[0],response_format:str="text", temperature:float=1.0):
    """chat with the model

    Args:
        messages (list): prompt messages
        model (json, optional): The model description. Defaults to CHAT_MODEL[0]. 
        response_format (str, optional): The format for the response. Defaults to "text", can be "text" or "json".
        temperature (float, optional): The temperature of the model, 0-2. Defaults to 1.0.

    Returns:
        any: AI response
        str: comma separated string with the following values: prompt_tokens,completion_tokens,total_tokens,estimated_cost
    """
    response = client.chat.completions.create(
        model=model["model"],
        messages=messages,
        response_format={ "type": response_format },
        temperature=temperature
    )
    
    prompt_tokens = response.usage.prompt_tokens
    completion_tokens = response.usage.completion_tokens
    total_tokens = response.usage.total_tokens
    estimated_cost =  round(math.ceil(prompt_tokens)/1000.0*model["input_cost"]+math.ceil(completion_tokens/1000.0)*model["output_cost"],2)
    
    return response.choices[0].message.content,f"{prompt_tokens},{completion_tokens},{total_tokens},{estimated_cost}"