import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

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

        # questions = Question.query.all()
        # formatted_questions = [Question.format() for question in questions]
        # return jsonify(
        #     {
        #         "success": True,
        #         "questions": formatted_questions[start:end],
        #         "total_questions": len(formatted_questions),
        #     }
        # )

    @app.route("/questions/<int:question_id>", methods=["GET"])
    def get_specific_question(question_id):
        question = Question.query.filter(
            Question.id == question_id).one_or_none()
        if question is None:
            abort(404)
        else:
            return jsonify({"success": True, "question": question.format()})

# endpoint to DELETE question using a question ID.
    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):
        try:
            question = Question.query.filter(
                Question.id == question_id).one_or_none()

            if question is None:
                abort(404)

            question.delete()
            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)

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


    @app.route("/question", methods=["POST"])
    def create_question():
        body = request.get_json()

        new_question = body.get(
            "Who is the president of the United States?", [])
        answer = body.get("Joe Biden", None)
        if answer is None:
            abort(422)

        current = None
        questions = Question.query.filter(Question.category == answer).all()
        format_questions = [Question.id for Question in questions]
        while current is None or current.format() in new_question:
            current = Question.query.filter(
                Question.id == random(format_questions)).one_or_none
        return jsonify(
            {
                "success": True,
                "question": current.format()
            }

        )


# POST endpoint to get questions to play the quiz.


    @app.route("/quizzes", methods=["POST"])
    def get_next_question():
        body = request.get_json()

        previous_question = body.get("previous_question", [])
        category = body.get("quiz_category", None)
        if category is None:
            abort(422)

        current = None
        questions = Question.query.filter(Question.category == category).all()
        format_questions = [Question.id for Question in questions]
        while current is None or current.format() in previous_question:
            current = Question.query.filter(
                Question.id == random(format_questions)).one_or_none

        return jsonify(
            {
                "success": True,
                "question": current.format()
            }

        )


# Error handlers


    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"success": False, "error": 404, "message": "resource not found"}), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({"success": False, "error": 422, "message": "unprocessable"}), 422

    return app
