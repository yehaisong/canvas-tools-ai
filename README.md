# canvas-tools

## vscode extentions

- python (microsoft)
- python environments (microsoft)


## Install required packages

1. Install pipenv.  
   Mac/Linux
   ```
   python3 -m pip install --user pipenv
   ```
   Windows  
   ```
   py -m pip install --user pipenv
   ```
2. In the project folder, sync all packages
   ```
   pipenv sync
   ``` 
3. Activate the venv
   ```
   pipenv shell
   ``` 

for help useing pipenv, type `pipenv -h`


## create requirement.txt
 pipenv requirements > requirements.txt

## server

basic flask server

## client

svelte client


### build the client

```
npm install
npm run build
```
### test the client
```
npm run dev
```