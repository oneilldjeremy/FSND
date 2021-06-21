# Backend - Full Stack Trivia API 

### Installing Dependencies for the Backend

1. **Python 3.7** - Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)


2. **Virtual Enviornment** - We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organaized. Instructions for setting up a virual enviornment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)


3. **PIP Dependencies** - Once you have your virtual environment setup and running, install dependencies by naviging to the `/backend` directory and running:
```bash
pip install -r requirements.txt
```
This will install all of the required packages we selected within the `requirements.txt` file.


4. **Key Dependencies**
 - [Flask](http://flask.pocoo.org/)  is a lightweight backend microservices framework. Flask is required to handle requests and responses.

 - [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM we'll use handle the lightweight sqlite database. You'll primarily work in app.py and can reference models.py. 

 - [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/#) is the extension we'll use to handle cross origin requests from our frontend server. 

### Database Setup
With Postgres running, restore a database using the trivia.psql file provided. From the backend folder in terminal run:
```bash
psql trivia < trivia.psql
```

### Running the server

From within the `./src` directory first ensure you are working using your created virtual environment.

To run the server, execute:

```bash
flask run --reload
```

The `--reload` flag will detect file changes and restart the server automatically.

### Error Handling
Errors are returned as JSON objects in the following format:
```
{
    "success": False, 
    "error": 400,
    "message": "bad request"
}
```
The API will return three error types when requests fail:
- 400: Bad Request
- 404: Resource Not Found
- 422: Not Processable 

Endpoints
GET '/api/v1.0/categories'
GET ...
POST ...
DELETE ...

GET '/api/v1.0/categories'
- Fetches a dictionary of categories in which the keys are the ids and the value is the corresponding string of the category, and a success value
- Request Arguments: None
- Returns: An object with a single key, categories, that contains an object of id: category_string key:value pairs. 
{
    {'1' : "Science",
    '2' : "Art",
    '3' : "Geography",
    '4' : "History",
    '5' : "Entertainment",
    '6' : "Sports"},
    'success': true
}

GET 'api/v1.0/questions?page=${integer}'
- Fetches a paginated list of question objects, a total number of questions, all categories and current category string. 
- Request Arguments: page - integer
- Returns: An object with 10 paginated questions, total questions, object including all categories, current category object, and a success value
{
    'questions': [
        {
            'id': 1,
            'question': 'Question',
            'answer': 'Answer', 
            'difficulty': 5,
            'category': 2
        },
    ],
    'totalQuestions': 24,
    'categories': { '1' : "Science",
    '2' : "Art",
    '3' : "Geography",
    '4' : "History",
    '5' : "Entertainment",
    '6' : "Sports" },
    'currentCategory': { '1' : 'Science'},
    'success': true

}

GET 'api/v1.0/categories/${id}/questions'
- Fetches questions for a cateogry specified by id request argument 
- Request Arguments: id - integer
- Returns: An object with questions for the specified category, total questions, current category object, and a success value
{
    'questions': [
        {
            'id': 1,
            'question': 'Question',
            'answer': 'Answer', 
            'difficulty': 2,
            'category': 6
        },
    ],
    'totalQuestions': 24,
    'currentCategory': { '1' : 'Science'},
    'success': true
}

DELETE '/questions/${id}'
- Deletes a specified question using the id of the question
- Request Arguments: id - integer
- Returns: An object with a success value and the deleted question id
{
    'success': true,
    'deleted': 3
}

POST '/quizzes'
- Sends a post request in order to get the next question 
- Request Body: 
{'previous_questions':  an array of question id's such as [1, 4, 20, 15]
'quiz_category': a current category object }
- Returns: a single new question object and a success message
{
    'question': {
        'id': 1,
        'question': 'Question',
        'answer': 'Answer', 
        'difficulty': 5,
        'category': 4
    },
    'success': true
}

POST '/questions'
- Sends a post request in order to add a new question
- Request Body: 
{
    'question':  'A new question',
    'answer':  'A new answer',
    'difficulty': 1,
    'category': 3,
}
- Returns: An object with a success value and the new question id
{
    'success': true,
    'question_id': 24
}

POST '/questions'
- Sends a post request in order to search for a specific question by search term 
- Request Body: 
{
    'searchTerm': 'Search Term'
}
- Returns: any array of questions, a number of totalQuestions that met the search term, a current category object, and a success value 
{
    'questions': [
        {
            'id': 1,
            'question': 'Question',
            'answer': 'Answer', 
            'difficulty': 5,
            'category': 5
        },
    ],
    'totalQuestions': 24,
    'currentCategory': { '1' : 'Science'},
    'success': true
}

## Testing
To run the tests, run
```
dropdb trivia_test
createdb trivia_test
psql trivia_test < trivia.psql
python test_flaskr.py
```
