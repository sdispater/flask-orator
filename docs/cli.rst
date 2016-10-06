.. _CLI:

CLI
###

The following examples assume that a file named ``db.py`` has been created with the following content:

.. code-block:: python

    from your_application import db

    if __name__ == '__main__':
        db.cli.run()


Migrations
==========


Creating Migrations
-------------------

To create a migration, you can use the ``make:migration`` command on the CLI:

.. code-block:: bash

    python db.py make:migration create_users_table

This will create a migration file that looks like this:

.. code-block:: python

    from orator.migrations import Migration


    class CreateTableUsers(Migration):

        def up(self):
            """
            Run the migrations.
            """
            pass

        def down(self):
            """
            Revert the migrations.
            """
            pass


By default, the migration will be placed in a ``migrations`` folder relative to where the command has been executed,
and will contain a timestamp which allows the framework to determine the order of the migrations.

If you want the migrations to be stored in another folder, use the ``--path/-p`` option:

.. code-block:: bash

    python db.py make:migration create_users_table -p my/path/to/migrations

The ``--table`` and ``--create`` options can also be used to indicate the name of the table,
and whether the migration will be creating a new table:

.. code-block:: bash

    python db.py make:migration add_votes_to_users_table --table=users

    python db.py make:migration create_users_table --table=users --create

These commands would respectively create the following migrations:

.. code-block:: python

    from orator.migrations import Migration


    class AddVotesToUsersTable(Migration):

        def up(self):
            """
            Run the migrations.
            """
            with self.schema.table('users') as table:
                pass

        def down(self):
            """
            Revert the migrations.
            """
            with self.schema.table('users') as table:
                pass

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


Running Migrations
------------------

To run all outstanding migrations, just use the ``migrate`` command:

.. code-block:: bash

    python db.py migrate


Rolling back migrations
-----------------------

Rollback the last migration operation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    python db.py migrate:rollback

Rollback all migrations
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    python db.py migrate:reset


Getting migrations status
-------------------------

To see the status of the migrations, just use the ``migrations:status`` command:

.. code-block:: bash

    python db.py migrate:status

This would output something like this:

.. code-block:: bash

    +----------------------------------------------------+------+
    | Migration                                          | Ran? |
    +----------------------------------------------------+------+
    | 2015_05_02_04371430559457_create_users_table       | Yes  |
    | 2015_05_04_02361430725012_add_votes_to_users_table | No   |
    +----------------------------------------------------+------+
