"""
Module for the db connection. Now the connection is with a Arango db.

Find more info about pyArango in:
https://www.arangodb.com/tutorials/tutorial-python/
"""

from pymongo import MongoClient
from pymongo.database import Database
from pymongo import collection
import pymongo
from bson.objectid import ObjectId

# TODO: Set Logger


class dbConnector:
    """Connects with ONLY ONE db and perform operation on it."""

    def __init__(self, db_name, password='.', user='root', mongoURL='http://127.0.0.1:8529'):
        """Init the database conection and set atributes db atribute."""
        """
        if password is not '.':
            self.conn = Connection(username=user, password=password,
                                   arangoURL=arangoURL)
        else:
            self.conn = Connection(username=user,
                                   arangoURL=arangoURL)

        if self.conn.hasDatabase(db_name):
            # conectartla
            self.db = pyArango.database.Database(self.conn, db_name)
            pass
        else:
            self.db = self.conn.createDatabase(name=db_name)
            # Crearla
        """
        client = MongoClient(mongoURL, 27017) # TODO: conectar con username y password
        self.db = Database(client, db_name)
        collection.Collection(self.db, 'results')
        collection.Collection(self.db, 'queue')



#    def create_collection(self, coll_name): # Hay que probar si sirve como retrieve tambien
        """Create and return the collection."""
        #return collection.Collection(self.db, coll_name)


#    def retrieve_collection(self, coll_name):  # doc, bd, coll?
        # Posiblemente innecesario
        """Return the collection in a list form."""
        """
        self.db.reload()
        coll = self.db.collections[coll_name]
        document_list = []
        for document in coll.fetchAll():
            document_list.append(document._store)
        return document_list
        """
#        pass


    def save_document(self, doc, coll_name):  # doc, bd, coll?
        """
        Save the document in the database.

        It is saved in the collection with the name specified.
        Doc, is in a python dic form.
        """
        """
        self.db.reload()
        if self.db.hasCollection(coll_name):
            coll = self.db.collections[coll_name]
            document = coll.createDocument()
            document._store = doc
            document.save()
        else:
            print('There is no collection with that name')
        """
        self.db.coll_name.insert_one(doc)


    def get_document(self, coll_name, doc_id):  # doc, bd, coll?
        """Return the document in a python dic form."""
        """
        self.db.reload()
        # FIXME: Modo cutre de encontrar documentos sin clave
        # Usar AQL quizas
        document_list = self.retrieve_collection(coll_name)
        for doc in document_list:
            if doc[doc_name]:
                return doc
        # doc._store
        pass
        """
        return self.db.coll_name.find_one({"_id": ObjectId(doc_id)})


    def delete_documents_param(self, coll_name, param, value):
        # Elimina todos los documentos con un parametro=valor determinado
        self.db.coll_name.delete_many({param: value})


    def delete_all_documents(self, coll_name):
        # Elimina todos los documentos de la colección
        self.db.coll_name.delete_many({})

