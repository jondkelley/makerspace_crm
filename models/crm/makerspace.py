from peewee import *
from . import get_database, BaseModel, FileModel, database_file
from playhouse.sqlite_ext import JSONField
import datetime

class BillingEventType(BaseModel):
    """
    store billing event types
    # API
    """
    name = CharField(max_length=128) #overdue, paid, billing due, deliquent
    description = TextField()

class Location(BaseModel):
    # API
    name = CharField(max_length=128)

class Zone(BaseModel):
    # API
    name = CharField(max_length=128)
    location = ForeignKeyField(Location, backref='zones')

# Mapping tables to define defined typed categories to assign userr to
class BillingCadenceTypeMap(BaseModel):
    # API
    name = CharField(max_length=128)
    billing_plan_id = TextField(null=True) # maybe quickbooks reference
    description = TextField()

class MembershipTypeMap(BaseModel):
    # API
    name = CharField(max_length=128) # board/staff, volunteer, partial, full, full_extended, 24/7
    description = TextField()

class ContractTypeMap(BaseModel):
    # API
    name = CharField(max_length=128) # liability waver, table saw waiver, etc.
    description = TextField()

class Person(BaseModel):
    # API
    first = CharField(max_length=64)
    last = CharField(max_length=64)
    email = CharField(max_length=512)

class PersonBilling(BaseModel):
    """
    Records billing events
    # API
    """
    billing_entity_id = TextField(null=True) # maybe quickbooks reference
    last_invoice = DateTimeField(default=datetime.datetime.now)
    next_invoice = DateTimeField(default=datetime.datetime.now)
    last_paid = DateTimeField(default=datetime.datetime.now)
    billing_cadence = ForeignKeyField(BillingCadenceTypeMap)
    billing_ref = CharField(max_length=128, null=True) # used as external billing reference to quickbooks
    is_paid = BooleanField(default=False)
    is_overdue = BooleanField(default=False)
    is_deliquent = BooleanField(default=False)
    person = ForeignKeyField(Person, backref='billing')

class PersonCredentials(BaseModel):
    """
    Reference table person credentials
    """
    uid = CharField(unique=True, max_length=64, null=True) # could be used if we switch to a directory server for auth
    user_id = CharField(max_length=64)
    password_hash = CharField(max_length=128)
    person = ForeignKeyField(Person, backref='credentials')

    @classmethod
    def update_password(cls, user_id, new_password):
        hashed_password = generate_password_hash(new_password)
        query = cls.update(password_hash=hashed_password).where(cls.user_id == user_id)
        query.execute()

class PasswordResetToken(BaseModel):
    user = ForeignKeyField(PersonCredentials, backref='reset_tokens')
    token = CharField(max_length=128, unique=True)
    expires_at = DateTimeField()

    @classmethod
    def create_token_for_user(cls, user, token, expires_in=3600):
        expiration_time = datetime.datetime.now() + datetime.timedelta(seconds=expires_in)
        return cls.create(user=user, token=token, expires_at=expiration_time)

INTERCOM_STATUS_TYPES = ('available', 'volunteering', 'away')
INTERCOM_STATUS_TYPES_PREV = (None, 'available', 'volunteering', 'away')

class PersonIntercomStatus(BaseModel):
    """
    user availability in CRM
    """
    prev_status = CharField(max_length=40, constraints=[Check(f"class_type IN {str(INTERCOM_STATUS_TYPES_PREV)}")])
    status = CharField(max_length=40, constraints=[Check(f"class_type IN {str(INTERCOM_STATUS_TYPES)}")])
    person = ForeignKeyField(Person)

class PersonPreferences(BaseModel):
    """
    store user application preferences
    """
    setting_key = CharField(max_length=512)
    setting_value = JSONField()
    person = ForeignKeyField(Person)

class PersonAvatarPic(FileModel):
    """
    user avatar
    # API
    """
    person = ForeignKeyField(Person, backref='profile_pic')

class PersonPhoto(FileModel):
    """
    membership picture
    # API
    """
    person = ForeignKeyField(Person, backref='photo')

class PersonEmergencyContact(BaseModel):
    email = CharField(max_length=512)
    phone = CharField(max_length=64)
    first = CharField(max_length=64)
    last = CharField(max_length=64)
    person = ForeignKeyField(Person, backref='emergency_contact')

class PersonContact(BaseModel):
    phone = CharField(max_length=64)
    street = CharField(max_length=128)
    city = CharField(max_length=64)
    state = CharField(max_length=64)
    zip_code = CharField(max_length=10)
    person = ForeignKeyField(Person, backref='person_address')

class PersonBillingLog(BaseModel):
    """
    store billing log data
    # API
    """
    description = CharField(max_length=64)
    billing_event_type_id = ForeignKeyField(BillingEventType, unique=True, backref='person_event_type')
    person = ForeignKeyField(Person, backref='billing_log')

class Form(BaseModel):
    """
    forms to be filled out by users
    # API
    """
    name = CharField(max_length=128, unique=True)
    description = TextField()
    form_url = CharField(unique=True)

class PersonForm(BaseModel):
    """
    forms filled out by user
    # API
    """
    person = ForeignKeyField(Person)
    form = ForeignKeyField(Form)

class DonorDocument(FileModel):
    """
    contract or document showing the donation of this equipment to the makerspace
    """
    description = TextField()

EQUIPMENT_RECORD_HISTORY_TYPES = ('maintenence', 'repair', 'accounting')
EQUIPMENT_TYPES = ('tool', 'machine')

class EquipmentHistoryRecord(BaseModel):
    """
    equipment history record
    # API
    """
    person = ForeignKeyField(Person, null=True)
    notes = CharField(max_length=200)
    class_type = CharField(max_length=40, constraints=[Check(f"class_type IN {str(EQUIPMENT_RECORD_HISTORY_TYPES)}")])

    class Meta:
        order_by = ('-created_dt',)

class Equipment(BaseModel):
    # API
    """ large equipment """
    name = CharField(max_length=128)
    equipment_type = CharField(max_length=40, constraints=[Check(f"equipment_type IN {str(EQUIPMENT_TYPES)}")])
    manufacturer = CharField(max_length=128, null=True)
    model = CharField(max_length=128, null=True)
    serial_number = CharField(null=True)
    out_of_order = BooleanField(default=False)
    asset_id = IntegerField(null=True)
    description = TextField()
    instruction_manual_url = TextField(unique=True, null=True)
    training_course_url = TextField(unique=True, null=True)
    required_form = ForeignKeyField(Form, backref='equipment', null=True)
    procurement_date = DateTimeField(constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')])
    donor = TextField(null=True)
    donor_document = ForeignKeyField(DonorDocument, backref='equipment', null=True)
    donor_already_taxed = BooleanField(default=False, null=True)
    is_loaned = BooleanField(default=False, null=True) # loaned but not donated
    requires_training = BooleanField(default=False, null=True) # loaned but not donated
    value_market = DecimalField(decimal_places=2, auto_round=True, max_digits=10, null=True)
    value_tax = DecimalField(decimal_places=2, auto_round=True, max_digits=10, null=True)
    assigned_zone = ForeignKeyField(Zone, backref='equipment')

class EquipmentPhoto(FileModel):
    """
    equipment picture
    # API
    """
    equipment = ForeignKeyField(Equipment, backref='photo')

class PersonTrainedEquipment(BaseModel):
    """
    many to many relation for who is trained on equipment
    # API
    """
    equipment = ForeignKeyField(Equipment)
    person = ForeignKeyField(Person)
    training_dt = DateTimeField(constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')])
    trainer = ForeignKeyField(Person, null=True)
    training_course_url = TextField(null=True)
    training_course_revision = CharField(max_length=10, null=True)

class PersonContract(FileModel):
    """
    many to many relation on who has signed a contract, with copy of contract file
    # API
    """
    contract_type = ForeignKeyField(ContractTypeMap)
    person = ForeignKeyField(Person)
    revision = CharField(max_length=10, null=True)

class PersonMembership(BaseModel):
    """
    many to many relation on type of club membership
    # API
    """
    membership_type = ForeignKeyField(MembershipTypeMap)
    person = ForeignKeyField(Person)

class PersonRbac(BaseModel):
    """
    many to many rbac relationships
    # API
    """
    role = TextField()
    permission = BooleanField(default=False)
    person = ForeignKeyField(Person)

# Create tables and apply database settings
def create_tables():
    with get_database(database_file) as db:
        db.create_tables([
            BillingCadenceTypeMap,
            MembershipTypeMap,
            ContractTypeMap,
            Zone,
            Location,
            Equipment,
            DonorDocument,
            Form,
            PersonBillingLog,
            Person,
            PersonCredentials,
            PersonPreferences,
            PersonAvatarPic,
            PersonPhoto,
            PersonEmergencyContact,
            PersonContact,
            PersonBilling,
            PersonTrainedEquipment,
            PersonContract,
            PersonMembership,
            PersonRbac,
        ], safe=True)
