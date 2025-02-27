# canvas.json file
The canvas.json file have the access token.
```
{
    "api_key":"123456",
    "env":"prod",
    "apiurl":"https://cedarville.instructure.com/api/v1/",
    "page_size": "100"
}
```
## Prepare the env file for openai
```
ORG_ID = <value>
OPENAI_API_KEY = <value>
```
# Search and replace media.cedarville.edu with Kaltura code
1. start pipenv shell in python-workshop folder  
```
pipenv shell
```
2. Use search_media_bulk.py to search in multiple courses. You may edit the search_template.json file to define more search templates.  
```
python replace_media_bulk.py
```
3. python search_media.py to search in one course. It will ask for a course id and then ask if you want to run in a test mode. If you enter Y, it will run in a test mode so no actural update will be made.  
```
python replace_media.py
```

# Search and replace any string

1. Use check_course() function in searchcontent.py to search target string. It will return a list of elements that contains the target string.
2. Replace old string with new string and assign to new_content of each element.
3. Call element.Update() to update each element in Canvas.