# -*- coding: utf-8 -*-

from flask import current_app, request, jsonify as base_jsonify, make_response
from orator import DatabaseManager, Model as BaseModel
from orator.pagination import Paginator
from orator.commands.application import application as orator_application
from orator.commands.command import Command
from orator.exceptions.orm import ModelNotFound
from cleo import Application


try:
    import simplejson as json
except ImportError:
    import json


class Orator(object):

    def __init__(self, app=None, manager_class=DatabaseManager):
        self.Model = BaseModel
        self.cli = None
        self._db = None
        self._manager_class = manager_class

        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        if 'ORATOR_DATABASES' not in app.config:
            raise RuntimeError('Missing "ORATOR_DATABASES" configuration')

        # Register request hooks
        self.register_handlers(app)

        # Getting config databases
        self._config = app.config['ORATOR_DATABASES']

        # Initializing database manager
        self._db = self._manager_class(self._config)

        self.Model.set_connection_resolver(self._db)

        # Setting current page resolver
        Paginator.current_page_resolver(self._current_page_resolver)

        # Setting commands
        self.init_commands()

    def _current_page_resolver(self):
        return int(request.args.get('page', 1))

    def init_commands(self):
        self.cli = Application(
            orator_application.get_name(),
            orator_application.get_version(),
            complete=True
        )

        for command in orator_application.all().values():
            if isinstance(command, Command):
                self.cli.add(command.__class__(self._db))
            else:
                self.cli.add(command)

    def register_handlers(self, app):
        self._register_error_handlers(app)

        teardown = app.teardown_appcontext

        @teardown
        def disconnect(_):
            return self._db.disconnect()

    def _register_error_handlers(self, app):
        @app.errorhandler(ModelNotFound)
        def model_not_found(error):
            response = make_response(error.message, 404)

            return response

    def __getattr__(self, item):
        return getattr(self._db, item)


def jsonify(obj, **kwargs):
    indent = None
    if current_app.config['JSONIFY_PRETTYPRINT_REGULAR'] \
            and not request.is_xhr:
        indent = 2

    if hasattr(obj, 'to_json'):
        response = current_app.response_class(
            obj.to_json(indent=indent),
            mimetype='application/json'
        )
    else:
        response = base_jsonify(obj, **kwargs)

    return response
