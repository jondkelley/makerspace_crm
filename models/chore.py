from peewee import *
from playhouse.postgres_ext import JSONField  # Assuming you are using PostgreSQL
from . import get_database, BaseModel, database_file
import datetime
from .makerspace import Person
from peewee import Check

class ChoreFrequency:
    """
    expected chore frequency
    """
    DAILY = 'daily'
    WEEKLY = 'monthly'
    MONTHLY = 'monthly'
    QUARTERLY = 'quarterly'
    YEARLY = 'yearly'
    CHOICES = (DAILY, WEEKLY, MONTHLY, QUARTERLY, YEARLY)

class ChoreClass:
    """
    chore class types
    """
    CHOICES = ('maintenence', 'cleanup', 'organization', 'administrative')

class Chore(BaseModel):
    """
    chores that need to be done
    """
    name = CharField(max_length=40, unique=True)
    description = CharField(max_length=200)
    classification = CharField(max_length=32, constraints=[Check(f"classification IN {str(ChoreClass.CHOICES)}")])
    creator = ForeignKeyField(Person, backref='created_chores', null=True)
    last_completed = DateTimeField(default=datetime.datetime.now)
    frequency = CharField(max_length=32, constraints=[Check(f"frequency IN {str(ChoreFrequency.CHOICES)}")])
    def __str__(self):
        return self.name

class ChoreVolunteer(BaseModel):
    """
    chores assigned to volunteers, so we can notify them if a chore is due
    """
    person = ForeignKeyField(Person, backref='volunteered_chores')
    chore = ForeignKeyField(Chore, backref='volunteers')

class ChoreHistory(BaseModel):
    """
    chore history log
    """
    chore = ForeignKeyField(Chore, backref='history')
    person = ForeignKeyField(Person, null=True)
    notes = CharField(max_length=200)
    class_type = CharField(max_length=40)
    status = CharField(max_length=10)  # 'started', 'done'

    class Meta:
        order_by = ('-created_dt',)

# Create tables and apply database settings
def create_tables():
    with get_database(database_file) as db:
        db.create_tables([
            Chore,
            ChoreVolunteer,
            ChoreHistory
        ], safe=True)

