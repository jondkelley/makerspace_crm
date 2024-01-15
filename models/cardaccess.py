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
            VolunteerAccessLog,
            PersonDoorControllerProfiles,
            DoorAccessLog,
            KeyCard,
            KeyCode,
        ], safe=True)
