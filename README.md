# Coding Challenge App

A skeleton flask app to use for a coding challenge.
## Prerequisites

- [Python3](https://www.python.org/downloads/)
- [flask-restful](https://flask-restful.readthedocs.io/en/0.3.3/installation.html)
- [Git](https://git-scm.com/)


## Install:

You can use a virtual environment (conda, venv, etc):
```
conda env create -f environment.yml
source activate user-profiles
```

Or just pip install from the requirements file
``` 
pip install -r requirements.txt
```

## Running the code

### Spin up the service

```
# start up local server
python -m run 
```

### Making Requests

#### Goal: Health check
```
curl -i "http://127.0.0.1:5000/health-check"
```

#### Goal: Get Merged User profile data from Github and Bitbucket
For API design documentation, please visit the design_document.docx in root folder


Curl request without token header.

```
curl -i "http://127.0.0.1:5000/users/{organization}/profile"
```

Note: In case we need to access more than 60 requests per hour, then only Token should be provided, otherwise there is no need to
provide any token in the header

- [Generate your own Token ](https://github.com/settings/tokens)

 
Curl request with token header.
```
curl -i -H "x-github-auth-token: {token}" "http://127.0.0.1:5000/users/{organization}/profile"
```

## Testing

Run `python -m unittest tests/test_app.py` from project root.
