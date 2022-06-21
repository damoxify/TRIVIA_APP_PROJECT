import os
from tkinter import N
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
import sys

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    app = Flask(__name__)
    setup_db(app)
    CORS(app)
# create and configure the app

    @app.after_request
    def after_request(response):
        response.headers.add("Access-Control-Allow-Headers",
                             "Content-Type,Authorization,true")
        response.headers.add("Access-Control-Allow-Methods",
                             "GET,PUT,POST,DELETE,OPTIONS")
        return response

 # endpoint to handle GET requests for questions

    @app.route("api/v1/questions", methods=["GET"])
    def get_question(question_id):
        questions = Question.query.all()
        categories = Category.query.all()
        page = request.args.get("page", 1, type=int)
        formatted_categories = formatted_categories(categories)
        every_questions = [question.format() for question in questions]
        current_questions = paginate_questions(request, questions)
        if(len(current_questions) == 0 and page != 1):
            abort(404)
        return jsonify({
            "success": True,
            "total_questions": len(every_questions),
            "questions": current_questions,
            "categories": formatted_categories,
            "current_category": None
        })

        # question = Question.query.filter(
        #     Question.id == question_id).one_or_none()
        # if question is None:
        #     abort(404)
        # else:
        #     return jsonify({"success": True, "question": question.format()})


# endpoint to handle GET requests for questions including pagination

    @app.route("/questions", methods=["GET"])
    # @cross_origin
    def paginate_questions(request, selection):
        # Implement pagniation
        page = request.args.get("page", 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE

        questions = [question.format() for question in selection]
        current_questions = questions[start:end]
        return current_questions


# endpoint to DELETE question using a question ID.

    @app.route("api/v1/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):
        try:
            question = Question.query.filter(
                Question.id == question_id).one_or_none()

            if question is None:
                abort(404)

            question.delete()
            selection = Question.query.order_by(Question.id).all()

            return jsonify(
                {
                    "success": True,
                    "deleted": question_id,
                    "total_questions": len(Question.query.all()),
                }
            )

        except:
            abort(422)


# endpoint to POST a new question

    @app.route("api/v1/questions", methods=["POST"])
    def create_question():
        body = request.get_json()
        page = request.args.get("page", 1, type=int)

        question = body.get("question", None)
        answer = body.get("answer", None)
        category = body.get("category", None)
        difficulty = body.get("difficulty", None)
        search = body.get("searchTerm", None)
        try:
            if search:
                questions = Question.query.filter(
                    Question.question.ilike('%{}%'.format(search))).all()
                formatted_questions = paginate_questions(request, questions)

                if(len(formatted_questions) == 0 and page != 1):
                    abort(404)
                return jsonify({
                    "success": True,
                    "questions": formatted_questions,
                    "every_questions": len(questions),
                    "current_category": None
                })
            else:
                if (question == "") or (answer == "") or (category == None) or (difficulty == None):
                    abort(400)

# create new question
                new_question = Question(
                    question=question, answer=answer, category=category, difficulty=difficulty)

# commit new question to the database
                new_question.insert()

                return jsonify({
                    "success": True,
                })

        except Exception as e:
            code = sys.exc_info()[1].code
            if code == 400:
                abort(400)
            else:
                abort(422)


# POST endpoint to get questions to play the quiz.

    @app.route("api/v1/quizzes", methods=["POST"])
    def get_quizzes():
        try:
            body = request.get_json()
            previous_question = body.get("previous_question", [])
            category = body.get("quiz_category", None)
# if quiz category is not specified, get all other questions in category
            if (category is None):
                questions = Question.query.all()
            elif category["id"] == 0:
                questions = Question.query.all()
            else:
                questions = Question.query.filter(
                    Question.catgory == category["id"]).all()
            question_pool = []

            for quest in questions:
                if quest.id not in previous_question:
                    question_pool.append(quest)

            if (len(question_pool) == 0):
                random_question = None
            else:
                rand_index = random.randint(0, len(question_pool)-1)
                random_question = question_pool[rand_index].format()
            return jsonify({
                "success": True,
                "question": random_question,
            })
        except:
            print(sys.exc_info())
            abort(422)
        # current = None
        # questions = Question.query.filter(Question.category == category).all()
        # format_questions = [Question.id for Question in questions]
        # while current is None or current.format() in previous_question:
        #     current = Question.query.filter(
        #         Question.id == random(format_questions)).one_or_none

        # return jsonify(
        #     {
        #         "success": True,
        #         "question": current.format()
        #     }

        # )


# Error handlers

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"success": False, "error": 404, "message": "resource not found"}), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({"success": False, "error": 422, "message": "unprocessable"}), 422

    @app.errorhandler(405)
    def method_not_allowed(error):
        return (
            jsonify({"success": False, "error": 405,
                    "message": "method not allowed"}), 405,
        )

    @app.errorhandler(400)
    def bad_request(error):
        return (
            jsonify({"success": False, "error": 400,
                    "message": "bad request"}), 400,
        )

    @app.errorhandler(500)
    def internal_server_error(error):
        return (
            jsonify({"success": False, "error": 500,
                    "message": "internal server error"}), 500,
        )

    return app
