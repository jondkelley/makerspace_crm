from peewee import Model, DateTimeField, BooleanField, SQL
from playhouse.sqlite_ext import SqliteExtDatabase

database_file = 'crm.sqlite'

def get_database(filename):
    db = SqliteExtDatabase(filename, pragmas=(
        ('cache_size', -1024 * 512),  # 512MB page-cache.
        ('journal_mode', 'wal'),  # Use WAL-mode (you should always use this!) allows reads to happen while writes occur
        ('foreign_keys', 1)))  # Enforce foreign-key constraint in sqlite (disabled by default)
    return db

class BaseModel(Model):
    """
    these attributes apply to every table automatically
    """
    created_dt = DateTimeField(constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')]) # object creation
    updated_dt = DateTimeField(null=True) # object last updated
    is_deleted = BooleanField(default=False) # support soft deletes
    is_hidden = BooleanField(default=False) # support hiding things from view
    class Meta:
        database = get_database(database_file)
