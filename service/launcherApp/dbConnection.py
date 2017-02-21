"""Module for the db connection. Now the connection is with a Arango db."""

from pyArango.connection import *
import pyArango

# TODO: Set Logger


class dbConnector:
    """Connects with ONLY ONE db and perform operation on it."""
    def connect_db(self, db_name):
        """
        Connect with the database.

        If the db doesn't exist it is created.
        Return a db object?.
        """
        if self.conn.hasDatabase(db_name):
            # conectartla
            self.db = pyArango.database.Database(self.conn, db_name)
            pass
        else:
            self.db = self.conn.createDatabase(name=db_name)
            # Crearla

    def __init__(self, password, db_name, user='root',
                 arangoURL='http://127.0.0.1:8529'):
        """Init the database conection and set atributes db atribute."""
        self.conn = Connection(username=user, password=password,
                               arangoURL=arangoURL)
        self.db = connect_db(db_name)

    def save_document(self, doc, coll_name):  # doc, bd, coll?
        """
        Save the document in the database.

        It is saved in the collection with the name specified.
        Doc, is in a python dic form.
        """
        if self.db.hasCollection(coll_name):
            coll = self.db.collections[coll_name]
            document = coll.createDocument()
            document._store = doc
            document.save()
        else:
            print('There is no collection with that name')

        userColl = self.db.collections['Users']

    def retrieve_document(self, doc_name):  # doc, bd, coll?
        """Return the document in a python dic form."""
        # doc._store
        pass

    def create_collection(self, coll_name):  # doc, bd, coll?
        """Create and return the collection."""
        if self.db.hasCollection(coll_name):
            print('The database already has a collection with that name')
        else:
            self.db.createCollection(name=coll_name)

    def retrieve_collection(self, coll_name):  # doc, bd, coll?
        # Innecesario???
        # FIXME: Posiblemente innecesario
        """Return the collection in a list form."""
        pass

    # def connect_db(self, db_name):
    #     """
    #     Connect with the database.
    #
    #     If the db doesn't exist it is created.
    #     Return a db object?.
    #     """
    #     if self.conn.hasDatabase(db_name):
    #         # conectartla
    #         self.db = pyArango.database.Database(self.conn, db_name)
    #         pass
    #     else:
    #         self.db = self.conn.createDatabase(name="automodelingDB")
    #         # Crearla
