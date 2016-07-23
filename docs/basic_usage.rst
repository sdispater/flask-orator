.. _BasicUsage:

Basic Usage
###########


A Minimal Application
=====================

.. note::

    This example application will not go into details as to how the ORM works.
    You can refer to the `Orator documentation <http://orator-orm.com/docs>`_ for more information.


Setting up Flask-Orator for a single Flask application is quite simple.
Create your application, load its configuration and then create an ``Orator``
object.

The ``Orator`` object behaves like a ``DatabaseManager`` instance set up
to work flawlessly with Flask.


.. code-block:: python

    from flask import Flask
    from flask_orator import Orator

    app = Flask(__name__)
    app.config['ORATOR_DATABASES'] = {
        'development': {
            'driver': 'sqlite',
            'database': '/tmp/test.db'
        }
    }

    db = Orator(app)


    class User(db.Model):

        __fillable__ = ['name', 'email']

        def __repr__(self):
            return '<User %r>' % self.name


Now, you need to create the database and the ``users`` table using the embedded CLI application.
Let's create a file named ``db.py`` which has the following content:

.. code-block:: python

    from your_application import db

    if __name__ == '__main__':
        db.cli.run()

This file, when executed, gives you access to useful commands to manage you databases.

.. note::

    For the exhaustive list of commands see the :ref:`CLI` section.

You first need to make a migration file to create the table:

.. code-block:: text

    python db.py make:migration create_users_table --table users --create

This will add a file in the ``migrations`` folder named ``create_users_table``
and prefixed by a timestamp:

.. code-block:: python

    from orator.migrations import Migration


    class CreateTableUsers(Migration):

        def up(self):
            """
            Run the migrations.
            """
            with self.schema.create('users') as table:
                table.increments('id')
                table.timestamps()

        def down(self):
            """
            Revert the migrations.
            """
            self.schema.drop('users')

You need to modify this file to add the ``name`` and ``email`` columns:

.. code-block:: python

    with self.schema.create('users') as table:
        table.increments('id')
        table.string('name').unique()
        table.string('email').unique()
        table.timestamps()

Then, you can run the migration:

.. code-block:: text

    python db.py migrate

Confirm and you database and table will be created.

Once your database set up, you can create some users:

.. code-block:: python

    from your_application import User

    admin = User.create(name='admin', email='admin@example.com')
    guest = Guest.create(name='guest', email='guest@example.com')

The ``create()`` method will create the users instantly. But you can also
initiate them and save them later:

.. code-block:: python

    admin = User(name='admin', email='admin@example.com')
    # Do something else...
    admin.save()

You can now retrieve them easily from the database:

.. code-block:: python

    users = User.all()

    admin = User.where('name', 'admin').first()


Relationships
=============

Setting up relationships between tables is a breeze.
Let's create a ``Post`` model with the ``User`` model as a parent:


.. code-block:: python


    class Post(db.Model):

        __fillable__ = ['title', 'content']

        @property
        def user(self):
            return self.belongs_to('users')


And we add the ``posts`` relationship to the ``User`` model:

.. code-block:: python

    class User(db.Model):

        @property
        def posts(self):
            return self.has_many('posts')

Before we can play with these models we need to create the ``posts`` table
and set up the relationship at database level:

.. code-block:: text

    python db.py make:migration create_posts_table --table posts --create

And we modify the generated file to look like this:

.. code-block:: python

    from orator.migrations import Migration


    class CreatePostsTable(Migration):

        def up(self):
            """
            Run the migrations.
            """
            with self.schema.create('posts') as table:
                table.increments('id')
                table.string('title')
                table.text('content')
                table.integer('user_id', unsigned=True)
                table.timestamps()

                table.foreign('user_id').references('id').on('users')

        def down(self):
            """
            Revert the migrations.
            """
            self.schema.drop('posts')

Finally we run it:

.. code-block:: text

    python db.py migrate

We can now instantiate some posts:

.. code-block:: python

    admin_post = Post(title='Admin Post',
                      description='This is a restricted post')

    guest_post = Post(title='Guest Post',
                      description='This is a guest post')

and associate them with users:

.. code-block:: python

    # Associate from user.posts relation
    admin.posts().save(admin_post)

    # Associate from post.user relation
    guest_post.user().associate(guest)

Relationships properties are `dynamic properties <http://orator-orm.com/docs/orm.html#dynamic-properties>`_
meaning that ``user.posts`` is the underlying collection of posts so we can do things like:

.. code-block:: python

    user.posts.first()
    user.posts[2:7]
    user.posts.is_empty()

But, if we need to retrieve a more fine-grained portion of posts we can actually to so:

.. code-block:: python

    user.posts().where('title', 'like', '%admin%').get()
    user.posts().first()


Pagination
==========

Flask-Orator supports pagination:

.. code-block:: python

    users = User.paginate(15)

This will retrieve ``15`` users. The current page is determined by default by the ``?page`` query string
parameter of the request.

This behavior can be modified if needed, either by explicitely specifying the current page:

.. code-block:: python

    users = User.paginate(15, request.args['index'])

or by changing the default ``Paginator`` current page resolver:

.. code-block:: python

    from flask import request
    from orator import Paginator

    def current_page_resolver():
        return request.args.get('index', 1)

    Paginator.current_page_resolver(current_page_resolver)


What's more?
============

Like said in introduction Flask-Orator is a wrapper around `Orator <http://orator-orm.com>`_ to integrate it
more easily with Flask applications. So, basically, everything you can do with Orator
is also possible with Flask-Orator.

Referer to the `Orator documentation <http://orator-orm/docs/>`_ to see the features available.
