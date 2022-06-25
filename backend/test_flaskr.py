import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category
from dotenv import load_dotenv
load_dotenv()


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.db_user = os.environ["db_user"]
        self.db_password = os.environ["db_password"]
        self.db_host = os.environ["db_host"]
        self.database_path = "postgresql://{}:{}@{}/{}".format(
            self.db_user, self.db_password, self.db_host, self.database_name)
        setup_db(self.app, self.database_path)

        self.new_question = {
            'question': "Who is the current president of the United States",
            'answer': "Joe Biden",
            'category': 3,
            'difficulty': 2
        }

        self.bad_question = {
            'answer': 4,
            'category': "bush",
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    # test for the get categories endpoint

    def test_get_all_categories(self):
        res = self.client().get('/api/v1/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        # success value set to be True
        self.assertEqual(data["success"], True)
        self.assertTrue(len(data["categories"]))  # categories exist
        pass

    def test_404_for_invalid_category_endpoint(self):
        res = self.client().get('/api/v1/categories/3')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertTrue(data["error"])
        self.assertTrue(data["message"])
        pass

    # tests for get questions endpoints
    def test_get_paginated_questions(self):
        res = self.client().get('/api/v1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(len(data["questions"]))
        # self.assertTrue(data["all_questions"])
        self.assertTrue(len(data["categories"]))
        self.assertEqual(data["current_category"], None)
        pass

    def test_500_page_exceeded_number_of_questions(self):
        res = self.client().get('/api/v1/questions?page=2000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertTrue(data["error"])
        self.assertTrue(data["message"])

        pass

    # tests for delete questions endpoints
    def test_successful_deletion_of_question(self):
        res = self.client().delete("/api/v1/questions/2")
        data = json.loads(res.data)

        question = Question.query.get(2)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(question, None)
        self.assertEqual(data["success"], True)
        # self.assertEqual(data["deleted"], 2)
        pass

    def test_422_question_does_not_exist(self):
        res = self.client().delete("/api/v1/questions/200")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertTrue(data["error"])
        self.assertTrue(data["message"])
        pass

    # Tests for question creation
    def test_create_question(self):
        res = self.client().post("/api/v1/questions", json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)

        pass

    def test_400_question_creation_failed(self):
        res = self.client().post("/api/v1/questions", json=self.bad_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data["success"], False)
        self.assertTrue(data["error"])
        self.assertTrue(data["message"])
        pass

    # Tests for questions search
    def test_search_for_questions(self):
        res = self.client().post("/api/v1/questions",
                                 json={"searchTerm": "what"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["every_questions"], 8)
        self.assertTrue(len(data["questions"]))
        self.assertEqual(data["current_category"], None)

        pass

    def test_no_question_found(self):
        res = self.client().post("/api/v1/questions",
                                 json={"searchTerm": "scripple tip top shoes on top"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["every_questions"], 0)
        self.assertEqual(len(data["questions"]), 0)
        self.assertEqual(data["current_category"], None)

        pass

    # tests for get questions by categories
    def test_get_question_based_on_category(self):
        res = self.client().get("/api/v1/categories/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        # self.assertEqual(data["total_questions"], 4)
        # self.assertTrue(len(data["questions"]))
        # self.assertEqual(data["current_category"], "Art")

        pass

    def test_404_category_does_not_exist(self):
        res = self.client().get("/api/v1/categories/2000/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertTrue(data["message"])
        self.assertTrue(data["error"])

        pass

    def test_get_quizzes(self):
        res = self.client().post("/api/v1/quizzes",
                                 json={"quiz_category": {"type": "History", "id": 4}, "previous_questions": [6, 8]})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        # self.assertNotIn(data["questions"]["id"], [6, 8])

        pass

    def test_no_questions(self):
        res = self.client().post("/api/v1/quizzes",
                                 json={"quiz_category": {"type": "History", "id": 7}, "previous_questions": [6, 12, 17, 20]})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        # self.assertIsNone(data["question"])

        pass


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
