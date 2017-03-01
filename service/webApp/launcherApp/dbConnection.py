"""
Module for the db connection. Now the connection is with a MongoDB.

Find more info about pyArango in:
https://docs.mongodb.com/getting-started/python/
http://api.mongodb.com/python/current/index.html
"""
from pymongo import MongoClient
from pymongo.database import Database
from pymongo import collection
from bson.objectid import ObjectId

# TODO: Set Logger


class dbConnector:
    """Connects with ONLY ONE db and perform operation on it."""

    def __init__(self, db_name, password='.', user='root', url='mongodb://localhost:27017/'):
        """Init the database conection and set atributes db atribute."""
        # TODO: conectar con username y password
        client = MongoClient(url, 27017)
        self.db = Database(client, db_name)
        collection.Collection(self.db, 'experiments')
        collection.Collection(self.db, 'queue')

    def save_document(self, doc, coll_name):  # doc, bd, coll?
        """
        Save the document in the database.

        It is saved in the collection with the name specified.
        Doc, is in a python dic form. Return the id as a ObjectID.
        """
        # FIXME: Ojo con devolver ObjectId
        return self.db[coll_name].insert_one(doc)

    def get_document(self, coll_name, doc_id):  # doc, bd, coll?
        """Return the document in a python dic form."""
        return self.db[coll_name].find_one({"_id": ObjectId(doc_id)})

    def delete_documents_param(self, coll_name, param, value):
        """Elimina todos los documentos con un parametro=valor determinado."""
        self.db[coll_name].delete_many({param: value})

    def delete_all_documents(self, coll_name):
        """Elimina todos los documentos de la coleccion."""
        self.db[coll_name].delete_many({})

    def update_document(self, doc_query, doc_update, coll_name):
        """Update the first document (or all documments?) matched with the query."""
        self.db[coll_name].update_one(
            doc_query,
            {'$set': doc_update})

    def push_document(self):
        """."""
        pass

    def pop_document(self):
        """."""
        pass

    def pull_document(self, coll_name, doc_param, doc_value):
        """."""
        self.db[coll_name].update_one(
            {doc_param:doc_value},
            {'$pull': doc_update})

    # Seguramente sobren las dos funciones de abajo
    def create_collection(self, coll_name):
        # Hay que probar si sirve como retrieve tambien
        """Create and return the collection."""
        # return collection.Collection(self.db, coll_name)
        pass

    def retrieve_collection(self, coll_name):  # doc, bd, coll?
        # Posiblemente innecesario
        """Return the collection in a list form."""
        pass
