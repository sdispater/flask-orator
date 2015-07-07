# -*- coding: utf-8 -*-

import json
import traceback
from unittest import TestCase
from flask import Flask, jsonify, request
from flask_orator import Orator, jsonify


class FlaskOratorTestCase(TestCase):

    def setUp(self):
        app = Flask(__name__)
        app.config['ORATOR_DATABASES'] = {
            'test': {
                'driver': 'sqlite',
                'database': ':memory:'
            }
        }

        db = Orator(app)

        self.app = app
        self.db = db

        self.User = self.make_user_model()

        @app.route('/')
        def index():
            try:
                return jsonify(self.User.order_by('id').paginate(5))
            except Exception as e:
                print(e)
                print(traceback.format_exc())
                raise

        @app.route('/users', methods=['POST'])
        def create():
            data = request.json
            user = self.User.create(**data)

            return jsonify(user)

        self.init_tables()

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
