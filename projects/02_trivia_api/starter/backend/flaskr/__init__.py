import os
from flask import Flask, request, abort, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import func
from flask_cors import CORS
import random
import math

from models import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
  page = request.args.get('page', 1, type=int)
  start = (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE

  questions = [question.format() for question in selection]
  current_questions = questions[start:end]

  return current_questions

def create_app(test_config=None):
    # Create the app
    app = Flask(__name__)
    setup_db(app)

    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response

    # Endpoint to return all categories
    @app.route('/categories')
    def retrieve_categories():
      categories = Category.query.order_by(Category.id).all()
      formatted_categories = {category.id: category.type for category in categories}

      if len(categories) == 0:
        abort(404)

      return jsonify({
        'success': True,
        'categories': formatted_categories
      })

    # Endpoint to return all questions
    @app.route('/questions')
    def retrieve_questions():
      selection = Question.query.order_by(Question.id).all()
      current_questions = paginate_questions(request, selection)
      total_questions = len(Question.query.all())
      categories = Category.query.order_by(Category.id).all()
      formatted_categories = {category.id: category.type for category in categories}
      current_category = Category.query.order_by(Category.id).first()

      if len(current_questions) == 0:
        abort(404)

      return jsonify({
        'success': True,
        'questions': current_questions,
        'total_questions': total_questions,
        'categories': formatted_categories,
        'current_category': {current_category.id: current_category.type}
      })

    # Endpoint to delete a question from the database
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_questions(question_id):
      try:
        question = Question.query.filter(Question.id == question_id).one_or_none()

        if question is None:
          abort(404)

        db.session.delete(question)
        db.session.commit()
        
      except:
        db.session.rollback()
        abort(422)
      finally:
        db.session.close()

      return jsonify({
        'success': True,
        'deleted': question_id,
        
      })


    # Endpoint that will will create a new question in the database, or complete a search in the text 
    # of the questions based on a search term entered by the user.
    @app.route('/questions', methods=['POST'])
    def create_question():
      body = request.get_json()

      search_term = body.get('searchTerm')

      if search_term:
        search_matches = Question.query.order_by(Question.id).filter(Question.question.ilike('%{}%'.format(search_term)))
        current_questions = paginate_questions(request, search_matches)
        total_questions = len(search_matches.all())
        current_category = Category.query.order_by(Category.id).first()

        return jsonify({
          'success': True,
          'questions': current_questions,
          'total_questions': total_questions,
          'current_category': {current_category.id: current_category.type}
        })
      else:
        try:
          question = body.get('question', None)
          answer = body.get('answer', None)
          difficulty = body.get('difficulty', None)
          category = body.get('category', None)

          new_question = Question(question=question,answer=answer,category=category,difficulty=difficulty)
          db.session.add(new_question)
          db.session.commit()
        except:
          db.session.rollback()
          abort(422)
        finally:
          new_question_id = new_question.id
          db.session.close()

        return jsonify({
          'success': True,
          'question_id': new_question_id
        })
    
    # Endpoint to return questions in a specified category
    @app.route('/categories/<int:category_id>/questions')
    def retrieve_questions_by_category(category_id):
      selection = Question.query.order_by(Question.id).filter(Question.category == category_id)
      total_questions = len(selection.all())
      current_questions = paginate_questions(request, selection)
      current_category = Category.query.get(category_id)

      if total_questions == 0:
        abort(404)

      return jsonify({
        'success': True,
        'questions': current_questions,
        'total_questions': total_questions,
        'current_category': {current_category.id: current_category.type}
      })


    # Endpoint that will provide the next question to a quiz. The query will get a random question from the database 
    # (by category if specified), not including previous questions. 
    @app.route('/quizzes', methods=['POST'])
    def create_quiz():
      body = request.get_json()

      previous_questions = body.get('previous_questions', None)
      quiz_category = body.get('quiz_category', None)

      current_question = Question.query.filter(Question.category == quiz_category['id']).filter(Question.id.notin_(previous_questions)).order_by(func.random()).first()

      if current_question:
        current_question = current_question.format()

      return jsonify({
        'success': True,
        'question': current_question
      })  

    @app.errorhandler(400)
    def bad_request(error):
      return jsonify({
        "success": False, 
        "error": 400,
        "message": "bad request"
        }), 400 

    @app.errorhandler(404)
    def not_found(error):
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

    return app

    