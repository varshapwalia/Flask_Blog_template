""" Database model base class """

from flask_mongoengine import MongoEngine
from datetime import datetime, timedelta

db = MongoEngine()

class BaseDocument(db.Document):
    """A base document defining certain critical fields
    
    :param datetime created_at: The timestamp when the document was created
    :param datetime updated_at: The timestamp when the document was last updated
   
    """

    meta = {
        'abstract': True
    }
    created_at = db.DateTimeField()
    updated_at = db.DateTimeField()

    def save(self, *args, **kwargs):
        """Triggered when the document is saved, updates the fields"""
        if not self.created_at:
            self.created_at = datetime.now() + timedelta(minutes=336,seconds=18)
        self.updated_at = datetime.now() + timedelta(minutes=336,seconds=18)
        return super(BaseDocument, self).save(*args, **kwargs)