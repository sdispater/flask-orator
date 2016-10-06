# -*- coding: utf-8 -*-

import sys
import os
import json
import tempfile
import uuid
from unittest import TestCase
from flask import Flask, jsonify, request
from flask_orator import Orator, jsonify
from sqlite3 import ProgrammingError
from orator.support.collection import Collection


PY2 = sys.version_info[0] == 2


class FlaskOratorTestCase(TestCase):

    def setUp(self):
        dbname = '%s.db' % str(uuid.uuid4())
        self.dbpath = os.path.join(tempfile.gettempdir(), dbname)

        app = Flask(__name__)
        app.config['ORATOR_DATABASES'] = {
            'test': {
                'driver': 'sqlite',
                'database': self.dbpath
            }
        }

        db = Orator(app)

        self.app = app
        self.db = db

        self.User = self.make_user_model()

        @app.route('/')
        def index():
            return jsonify(self.User.order_by('id').paginate(5))

        @app.route('/users', methods=['POST'])
        def create():
            data = request.json
            user = self.User.create(**data)

            return jsonify(user)

        @app.route('/users/<user_id>', methods=['GET'])
        def show(user_id):
            return self.User.find_or_fail(user_id)

        self.init_tables()

    def tearDown(self):
        os.remove(self.dbpath)

    def init_tables(self):
        with self.schema().create('users') as table:
            table.increments('id')
            table.string('name').unique()
            table.string('email').unique()
            table.timestamps()

    def make_user_model(self):
        class User(self.db.Model):

            __fillable__ = ['name', 'email']

        return User

    def post(self, client, endpoint, params_=None, **data):
        headers = [
            ('Content-Type', 'application/json')
        ]

        if params_ is None:
            params_ = {}

        return client.post(endpoint, headers=headers,
                           data=json.dumps(data))

    def get(self, client, endpoint, **data):
        return client.get(endpoint)

    def connection(self):
        return self.db.Model.get_connection_resolver().connection()

    def schema(self):
        return self.connection().get_schema_builder()

    def assertRaisesRegex(self, expected_exception, expected_regex,
                          callable_obj=None, *args, **kwargs):
        if PY2:
            return self.assertRaisesRegexp(
                expected_exception, expected_regex,
                callable_obj, *args, **kwargs)

        return super(FlaskOratorTestCase, self).assertRaisesRegex(
            expected_exception, expected_regex,
            callable_obj, *args, **kwargs
        )

    def assertRegex(self, *args, **kwargs):
        if PY2:
            return self.assertRegexpMatches(*args, **kwargs)
        else:
            return super(FlaskOratorTestCase, self).assertRegex(*args, **kwargs)


class BasicAppTestCase(FlaskOratorTestCase):

    def test_basic_insert(self):
        c = self.app.test_client()

        user_data = json.loads(
            self.post(c, '/users', name='foo', email='foo@bar.com').data.decode()
        )
        self.assertEqual(1, user_data['id'])
        self.assertEqual('foo', user_data['name'])
        self.assertEqual('foo@bar.com', user_data['email'])

        self.post(c, '/users', name='bar', email='bar@baz.com')

        users = json.loads(
            self.get(c, '/').data.decode()
        )
        self.assertEqual('foo', users[0]['name'])
        self.assertEqual('bar', users[1]['name'])

    def test_model_not_found_returns_404(self):
        c = self.app.test_client()

        response = self.get(c, '/users/9999')

        self.assertEqual(404, response.status_code)
        self.assertRegex(str(response.data), 'No query results found for model \[User\]')


class PaginatorTestCase(FlaskOratorTestCase):

    def test_default_page(self):
        c = self.app.test_client()

        for i in range(10):
            self.post(c, '/users',
                      name='user %s' % i,
                      email='foo%s@bar.com' % i)

        users = json.loads(
            self.get(c, '/').data.decode()
        )

        self.assertEqual(5, len(users))
        self.assertEqual(1, users[0]['id'])
        self.assertEqual(5, users[-1]['id'])

    def test_specific_page(self):
        c = self.app.test_client()

        for i in range(10):
            self.post(c, '/users',
                      name='user %s' % i,
                      email='foo%s@bar.com' % i)

        users = json.loads(
            self.get(c, '/?page=2').data.decode()
        )

        self.assertEqual(5, len(users))
        self.assertEqual(6, users[0]['id'])
        self.assertEqual(10, users[-1]['id'])

    def test_page_greater_than_max_page(self):
        c = self.app.test_client()

        for i in range(10):
            self.post(c, '/users',
                      name='user %s' % i,
                      email='foo%s@bar.com' % i)

        users = json.loads(
            self.get(c, '/?page=5').data.decode()
        )

        self.assertEqual(0, len(users))


class ConsistenceTestCase(FlaskOratorTestCase):

    def test_handlers(self):
        connection = self.db.connection().get_connection()

        c = self.app.test_client()

        self.get(c, '/')

        self.assertRaisesRegex(ProgrammingError, 'Cannot operate on a closed database.', connection.commit)

        self.assertIsNone(self.db.connection().get_connection())

    def test_behaves_like_manager(self):
        @self.app.route('/users')
        def users():
            try:
                users = jsonify(Collection(self.db.table('users').get()).map(lambda x: dict(x.items())))
            except Exception:
                raise

            return users

        c = self.app.test_client()

        for i in range(10):
            self.post(c, '/users',
                      name='user %s' % i,
                      email='foo%s@bar.com' % i)

        users = json.loads(self.get(c, '/users').data.decode())

        self.assertEqual(10, len(users))
