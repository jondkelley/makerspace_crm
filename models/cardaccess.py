from peewee import *
from . import get_database, BaseModel, database_file
from .makerspace import Person
from playhouse.sqlite_ext import JSONField

class DoorProfiles(BaseModel):
    """
    store which door controller, door and time profile people have access to
    """
    controller = CharField(max_length=24) # controller ID or ALL
    profile_id = IntegerField()
    start_date = CharField(max_length=11) # yyyy-MM-dd
    end_date = CharField(max_length=11) # yyyy-MM-dd
    time_segment_1_start = CharField(max_length=5) # 16:00
    time_segment_1_end = CharField(max_length=5) # 22:00
    time_segment_2_start = CharField(max_length=5)
    time_segment_2_end = CharField(max_length=5)
    time_segment_3_start = CharField(max_length=5)
    time_segment_3_end = CharField(max_length=5)
    person = ForeignKeyField(Person)

class PersonDoorControllerProfiles(BaseModel):
    """
    store which door controller, door and time profile people have access to
    """
    controller = CharField(max_length=24) # which controller to write to
    door_time_profiles = JSONField() # {"1": 1, "2": 1, "3": 1, "4": 1}
    start_date = CharField(max_length=11) # yyyy-MM-dd
    end_date = CharField(max_length=11) # yyyy-MM-dd
    person = ForeignKeyField(Person)

class VolunteerAccessLog(BaseModel):
    """
    volunteer access log
    """
    log_sha1 = CharField(max_length=40) # sha1 hash to prevent duplicate entries written between polling
    event_dt = DateTimeField(constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')])
    card_number = IntegerField()
    event_type = CharField(max_length=32)
    event_type_id = IntegerField() # door id
    event_reason = CharField(max_length=64)
    door = IntegerField() # door id
    controller = IntegerField() # controller id
    access_granted = BooleanField()
    person = ForeignKeyField(Person, backref='dooraccess_log')

class DoorAccessLog(BaseModel):
    """
    build door access log for reporting functions, scraped off the controller logs
    """
    log_sha1 = CharField(max_length=40) # sha1 hash to prevent duplicate entries written between polling
    event_dt = DateTimeField(constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')])
    card_number = IntegerField()
    event_type = CharField(max_length=32)
    event_type_id = IntegerField() # door id
    event_reason = CharField(max_length=64)
    door = IntegerField() # door id
    controller = IntegerField() # controller id
    access_granted = BooleanField()
    person = ForeignKeyField(Person, backref='dooraccess_log')

class KeyCard(BaseModel):
    card_number = IntegerField(unique=True)
    card_type = CharField(max_length=64)
    person = ForeignKeyField(Person, unique=True, backref='key_card')

class KeyCode(BaseModel):
    passcode = IntegerField(unique=True)
    person = ForeignKeyField(Person, unique=True, backref='key_code')

# Create tables and apply database settings
def create_tables():
    with get_database(database_file) as db:
        db.create_tables([
            DoorProfiles,
            PersonDoorControllerProfiles,
            DoorAccessLog,
            KeyCard,
            KeyCode,
        ], safe=True)
