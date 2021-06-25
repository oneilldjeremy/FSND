import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
Initialize the datbase
'''
db_drop_and_create_all()

# ROUTES
'''
GET /drinks
Open to public
Returns the drink.short() data representation
Returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
or appropriate status code indicating reason for failure
'''
@app.route('/drinks')
def retrieve_drinks():
    drinks = Drink.query.all()
    formatted_drinks = [drink.short() for drink in drinks]

    if len(drinks) == 0:
        abort(404)

    return jsonify({
    'success': True,
    'drinks': formatted_drinks
    })


'''
GET /drinks-detail
Requires the 'get:drinks-detail' permission
Returns the drink.long() data representation
Returns status code 200 and json {"success": True, "drinks": drinks}
where drinks is the list of drinks
or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def retrieve_drinks_details(jwt):
    drinks = Drink.query.all()
    formatted_drinks = [drink.long() for drink in drinks]

    if len(drinks) == 0:
        abort(404)

    return jsonify({
    'success': True,
    'drinks': formatted_drinks
    })


'''
POST /drinks
Creates a new drink
Requirse the 'post:drinks' permission
Returns the drink.long() data representation
Returns status code 200 and json {"success": True, "drinks": drink}
where drink an array containing only the newly created drink
or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(jwt):
    body = request.get_json()

    title = body.get('title', None)
    recipe = body.get('recipe', None)

    if not title or not recipe:
        abort(400) 
    
    if not isinstance(recipe, list):
        abort(400)
    
    try:
        new_drink = Drink(title=title,recipe=json.dumps(recipe))
        new_drink.insert();
    except:
        abort(422)

    return jsonify({
        'success': True,
        'drinks': [new_drink.long()]
    })


'''
PATCH /drinks/<id> where <id> is the existing model id
Respond with a 404 error if <id> is not found
Otherwise, updates the corresponding row for <id>
Requirse the 'patch:drinks' permission
Returns the drink.long() data representation
Returns status code 200 and json {"success": True, "drinks": drink}
where drink an array containing only the updated drink
or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(jwt, drink_id):
    body = request.get_json()

    title = body.get('title', None)
    recipe = body.get('recipe', None)

    if not title and not recipe:
        abort(400) 
    
    if recipe and not isinstance(recipe, list):
        abort(400)
    
    try:
        current_drink = Drink.query.get(drink_id)

        if current_drink is None:
            abort(404)
        
        if title:
            current_drink.title = title
        if recipe:
            current_drink.recipe = json.dumps(recipe)
        current_drink.update();
    except:
        abort(422)

    return jsonify({
        'success': True,
        'drinks': [current_drink.long()]
    })


'''
DELETE /drinks/<id> where <id> is the existing model id
Responds with a 404 error if <id> is not found
Deletes the corresponding row for <id>
Requires the 'delete:drinks' permission
Returns status code 200 and json {"success": True, "delete": id} 
where id is the id of the deleted record
or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(jwt, drink_id):
    try:
        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()

        if drink is None:
            abort(404)

        drink.delete()
    
    except:
        abort(422)

    return jsonify({
    'success': True,
    'deleted': drink_id,
    
    })


# Error Handling
@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False, 
        "error": 400,
        "message": "bad request"
        }), 400


@app.errorhandler(404)
def not_found():
    return jsonify({
        "success": False, 
        "error": 404,
        "message": "resource not found"
        }), 404

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        "success": False, 
        "error": error.status_code,
        "message": error.error['description']
        }), error.status_code
