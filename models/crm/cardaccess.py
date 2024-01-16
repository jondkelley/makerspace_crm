from peewee import *
from . import get_database, BaseModel, RootModel, database_file
from .makerspace import Person
from playhouse.sqlite_ext import JSONField

class Controller(RootModel):
    """
    maps which direction a door is considered to be going and if its an exterior door
    """
    controller = IntegerField()
    name = CharField(max_length=32)

class DoorDirectionMap(RootModel):
    """
    maps which direction a door is considered to be going and if its an exterior door
    """
    controller = ForeignKeyField(Controller)
    door = IntegerField()
    direction = CharField(max_length=3, constraints=[Check("direction IN ('in', 'out')")])
    exterior_door = BooleanField()

class DoorProfiles(BaseModel):
    """
    store which door controller, door and time profile people have access to
    """
    controller = ForeignKeyField(Controller)
    profile_id = IntegerField() # profile ID to write to the controller
    start_date = CharField(max_length=11) # yyyy-MM-dd
    end_date = CharField(max_length=11) # yyyy-MM-dd
    time_segment_1_start = CharField(max_length=5) # 16:00
    time_segment_1_end = CharField(max_length=5) # 22:00
    time_segment_2_start = CharField(max_length=5)
    time_segment_2_end = CharField(max_length=5)
    time_segment_3_start = CharField(max_length=5)
    time_segment_3_end = CharField(max_length=5)
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
    person = ForeignKeyField(Person)

def calculate_volunteer_hours(person_id, start_date, end_date, checkin_controller=1, checkin_door=1, checkout_controller=2, checkout_door=2):
    # Fetch records for the specified person within the given date range
    # import datetime
    # person_id = 123  # Replace with the actual person ID
    # # Define the start and end dates for the calculation
    # start_date = datetime.datetime(2023, 1, 1)  # January 1, 2023
    # end_date = datetime.datetime(2023, 1, 31)   # January 31, 2023
    # # Calculate the volunteer hours
    # total_volunteer_hours = calculate_volunteer_hours(person_id, start_date, end_date)
    # # Convert total duration to a more readable format (e.g., hours)
    # hours = total_volunteer_hours.total_seconds() / 3600
    # print(f"Total volunteer hours for person {person_id} from {start_date} to {end_date}: {hours} hours")
    logs = (VolunteerAccessLog
            .select()
            .where(
                (VolunteerAccessLog.person == person_id) &
                (VolunteerAccessLog.event_dt >= start_date) &
                (VolunteerAccessLog.event_dt <= end_date)
            )
            .order_by(VolunteerAccessLog.event_dt))

    total_duration = datetime.timedelta(0)
    check_in_time = None

    for log in logs:
        if log.controller == checkin_controller and log.door == checkin_door:
            check_in_time = log.event_dt
        elif log.controller == checkout_controller and log.door == checkout_door and check_in_time:
            duration = log.event_dt - check_in_time
            total_duration += duration
            check_in_time = None

    return total_duration

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
    person = ForeignKeyField(Person)

KEY_CARD_TYPES = ('keyfob', 'card', 'bracelet', 'sticker', 'phone', 'other')

class KeyCard(BaseModel):
    card_number = IntegerField(unique=True)
    card_type = CharField(max_length=64, constraints=[Check(f"card_type IN {str(KEY_CARD_TYPES)}")])
    person = ForeignKeyField(Person, unique=True, backref='key_card')

class KeyCode(BaseModel):
    passcode = IntegerField(unique=True)
    person = ForeignKeyField(Person, unique=True, backref='key_code')

class PersonDoorCredentialProfile(BaseModel):
    """
    store which door controller, door and time profile people have access to
    """
    person = ForeignKeyField(Controller)
    card = ForeignKeyField(KeyCard)
    code = ForeignKeyField(KeyCode)
    door_1_profile = ForeignKeyField(DoorProfiles)
    door_2_profile = ForeignKeyField(DoorProfiles)
    door_3_profile = ForeignKeyField(DoorProfiles)
    door_4_profile = ForeignKeyField(DoorProfiles)
    access_start_date = CharField(max_length=11) # yyyy-MM-dd
    access_end_date = CharField(max_length=11) # yyyy-MM-dd

# Create tables and apply database settings
def create_tables():
    with get_database(database_file) as db:
        db.create_tables([
            Controller,
            DoorDirectionMap,
            DoorProfiles,
            VolunteerAccessLog,
            PersonDoorCredentialProfile,
            DoorAccessLog,
            KeyCard,
            KeyCode,
        ], safe=True)
