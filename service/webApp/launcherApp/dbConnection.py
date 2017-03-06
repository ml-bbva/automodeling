"""
Module for the db connection. Now the connection is with a MongoDB.

Find more info about pymongo in:
https://docs.mongodb.com/getting-started/python/
http://api.mongodb.com/python/current/index.html
"""
from pymongo import MongoClient
from pymongo.database import Database
from bson.objectid import ObjectId

# TODO: Set Logger


class dbConnector:
    """Connects with ONLY ONE db and perform operation on it."""

    def __init__(
            self, db_name, password='.',
            user='root', url='mongo-single.experiment1.svc.cluster.local'):
        """
        Init the database conection and set atributes db atribute.

        The collections needed for the app are created here.
        """
        # TODO: conectar con username y password
        # NOTE: La creacion de las colleciones necesarias va aqui. Deberia?
        client = MongoClient(url, 27017)
        self.db = Database(client, db_name)
        # Create needed collections
        self.create_collection('experiments')
        self.create_collection('queue')
        self.create_collection('running')
        # Create needed documents
        if self.db['queue'].find().count() is 0:
            self.save_document({'queue': []}, 'queue')
        if self.db['running'].find().count() is 0:
            self.save_document({'running': []}, 'running')

    def save_document(self, doc, coll_name):
        """
        Save the document in the database.

        It is saved in the collection with the name specified.
        Doc, is in a python dic form. Return the id as a ObjectID.
        """
        # FIXME: Ojo con devolver ObjectId
        return self.db[coll_name].insert_one(doc)

    def get_document(self, doc_query, coll_name):  # doc, bd, coll?
        """Return the document in a python dic form."""
        # TODO: hacer que devuelva false si la query no da result
        return self.db[coll_name].find_one(doc_query)

    def delete_document(self, doc_query, coll_name):
        """Elimina todos los documentos que coincida con la query."""
        self.db[coll_name].delete_one(doc_query)

    def delete_documents(self, doc_query, coll_name):
        """Elimina todos los documentos que coincida con la query."""
        self.db[coll_name].delete_many(doc_query)

    def delete_all_documents(self, coll_name):
        """Elimina todos los documentos de la coleccion."""
        self.db[coll_name].delete_many({})

    def update_document(self, doc_query, doc_update, coll_name):
        """Update the first document matched with the query."""
        self.db[coll_name].update_one(
            doc_query,
            {'$set': doc_update})

    def update_documents(self, doc_query, doc_update, coll_name):
        """Update all documents matched with the query."""
        self.db[coll_name].update_one(
            doc_query,
            {'$set': doc_update})

    def push_document(self, doc_query, key, element, coll_name):
        """."""
        self.db[coll_name].update_one(
            doc_query,
            {'$push': {
                key: element
            }})

    def pop_document(self, doc_query, key, coll_name):
        """Return and remove the first element in the database."""
        result = self.db[coll_name].find_one_and_update(
            doc_query,
            {'$pop': {
                key: -1
            }}
        )
        try:
            return result[key].pop(0)
        except IndexError:
            return False

    def pull_document(self, doc_query, key, element, coll_name):
        """."""
        self.db[coll_name].update_one(
            doc_query,
            {'$pull': {
                key: element
            }})

    def create_collection(self, coll_name):
        # Hay que probar si sirve como retrieve tambien
        """Create the collection. Return True if succed or False if fail."""
        # return collection.Collection(self.db, coll_name)
        coll_names = self.db.collection_names()
        if coll_name not in coll_names:
            self.db.create_collection(coll_name)
            return True
        else:
            return False

    def retrieve_collection(self, coll_name):  # doc, bd, coll?
        # Posiblemente innecesario
        """Return the collection in a list form."""
        pass
