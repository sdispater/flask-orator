# -*- coding: utf-8 -*-

from flask import current_app, request, jsonify as base_jsonify, Response
from orator import DatabaseManager, Model as BaseModel
from orator.pagination import Paginator
from orator.commands.migrations import (
    InstallCommand, MigrateCommand,
    MigrateMakeCommand, RollbackCommand,
    StatusCommand, ResetCommand
)
from orator.commands.application import application as orator_application
from cleo import Application


try:
    import simplejson as json
except ImportError:
    import json


class Orator(object):

    def __init__(self, app=None):
        self.Model = BaseModel
        self.cli = None
        self._db = None

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
        self._db = DatabaseManager(self._config)

        self.Model.set_connection_resolver(self._db)

        # Setting current page resolver
        def current_page_resolver():
            return int(request.args.get('page', 1))

        Paginator.current_page_resolver(current_page_resolver)

        # Setting commands
        self.init_commands()

    def init_commands(self):
        self.cli = Application(orator_application.get_name(),
                               orator_application.get_version())
        
        self.cli.add(InstallCommand(self))
        self.cli.add(MigrateCommand(self))
        self.cli.add(MigrateMakeCommand(self))
        self.cli.add(RollbackCommand(self))
        self.cli.add(StatusCommand(self))
        self.cli.add(ResetCommand(self))

    def register_handlers(self, app):
        teardown = app.teardown_appcontext

        @teardown
        def disconnect(_):
            return self._db.disconnect()

    def __getattr__(self, item):
        return getattr(self._db, item)


def jsonify(obj, **kwargs):
    indent = None
    if current_app.config['JSONIFY_PRETTYPRINT_REGULAR'] \
            and not request.is_xhr:
        indent = 2

    if hasattr(obj, 'to_json'):
        response = Response(obj.to_json(indent=indent),
                            mimetype='application/json',
                            **kwargs)
    elif isinstance(obj, list):
        response = Response(json.dumps(obj, indent=indent),
                            mimetype='application/json',
                            **kwargs)
    else:
        response = base_jsonify(obj, **kwargs)

    return response
