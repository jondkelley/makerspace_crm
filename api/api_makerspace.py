from flask_restful import Resource, reqparse
from models.crm.makerspace import (BillingCadenceTypeMap, MembershipTypeMap, ContractTypeMap, Zone, Location, Equipment,
    Person, PersonEmergencyContact, PersonContact, PersonTrainedEquipment, PersonContract, PersonMembership, PersonRbac,
    PersonPhoto, PersonAvatarPic, PersonContract, EquipmentPhoto, EquipmentHistoryRecord, Equipment, Form, PersonForm)
from models.crm.cardaccess import (DoorProfiles, PersonDoorCredentialProfile, DoorAccessLog, KeyCard, KeyCode)
import base64
from flask import jsonify, request
from peewee import IntegrityError

class FormResource(Resource):
    def post(self):
        data = request.get_json()
        try:
            new_form = Form.create(
                name=data['name'],
                description=data.get('description', ''),
                form_url=data['form_url']
            )
            return {'message': 'Form created successfully', 'id': new_form.id}, 201
        except KeyError as e:
            return {'error': f'Missing key {e}'}, 400
        except IntegrityError as e:
            return {'error': str(e)}, 400

    def get(self, form_id):
        try:
            form = Form.get(Form.id == form_id)
            return {
                'id': form.id,
                'name': form.name,
                'description': form.description,
                'form_url': form.form_url
            }
        except DoesNotExist:
            return {'error': 'Form not found'}, 404

    def delete(self, form_id):
        try:
            form = Form.get(Form.id == form_id)
            form.delete_instance()
            return {'message': f'Form with ID {form_id} has been deleted'}, 200
        except DoesNotExist:
            return {'error': 'Form not found'}, 404

    def put(self, form_id):
        try:
            form = Form.get(Form.id == form_id)
            data = request.get_json()
            form.name = data.get('name', form.name)
            form.description = data.get('description', form.description)
            form.form_url = data.get('form_url', form.form_url)
            form.save()
            return {'message': f'Form with ID {form_id} has been updated'}, 200
        except DoesNotExist:
            return {'error': 'Form not found'}, 404

class PersonFormResource(Resource):
    def post(self):
        data = request.get_json()
        try:
            new_person_form = PersonForm.create(
                person=data['person'],
                form=data['form']
            )
            return {'message': 'Person form association created successfully', 'id': new_person_form.id}, 201
        except KeyError as e:
            return {'error': f'Missing key {e}'}, 400
        except IntegrityError as e:
            return {'error': str(e)}, 400

    def get(self, person_form_id):
        try:
            person_form = PersonForm.get(PersonForm.id == person_form_id)
            return {
                'id': person_form.id,
                'person_id': person_form.person.id,
                'form_id': person_form.form.id
            }
        except DoesNotExist:
            return {'error': 'PersonForm not found'}, 404

    def delete(self, person_form_id):
        try:
            person_form = PersonForm.get(PersonForm.id == person_form_id)
            person_form.delete_instance()
            return {'message': f'PersonForm with ID {person_form_id} has been deleted'}, 200
        except DoesNotExist:
            return {'error': 'PersonForm not found'}, 404

    def put(self, person_form_id):
        data = request.get_json()
        try:
            person_form = PersonForm.get(PersonForm.id == person_form_id)
            if 'person' in data:
                person_form.person = data['person']
            if 'form' in data:
                person_form.form = data['form']
            person_form.save()
            return {'message': f'PersonForm with ID {person_form_id} has been updated'}, 200
        except DoesNotExist:
            return {'error': 'PersonForm not found'}, 404

class EquipmentHistoryRecordResource(Resource):
    def post(self):
        try:
            data = request.get_json()
            person_id = data.get('person_id')
            notes = data['notes']
            class_type = data['class_type']

            new_record = EquipmentHistoryRecord.create(person=person_id, notes=notes, class_type=class_type)
            return {'message': 'Record created successfully', 'id': new_record.id}, 201
        except KeyError as e:
            return {'error': f'Missing key {e}'}, 400

    def get(self, record_id):
        try:
            record = EquipmentHistoryRecord.get(EquipmentHistoryRecord.id == record_id)
            return {
                'id': record.id,
                'person_id': record.person.id if record.person else None,
                'notes': record.notes,
                'class_type': record.class_type
            }
        except EquipmentHistoryRecord.DoesNotExist:
            return {'error': 'Record not found'}, 404

    def delete(self, record_id):
        try:
            record = EquipmentHistoryRecord.get(EquipmentHistoryRecord.id == record_id)
            record.delete_instance()
            return {'message': f'Record with ID {record_id} has been deleted'}, 200
        except EquipmentHistoryRecord.DoesNotExist:
            return {'error': 'Record not found'}, 404

    def put(self, record_id):
        try:
            record = EquipmentHistoryRecord.get(EquipmentHistoryRecord.id == record_id)
            data = request.get_json()
            record.notes = data.get('notes', record.notes)
            record.class_type = data.get('class_type', record.class_type)
            record.save()
            return {'message': f'Record with ID {record_id} has been updated'}, 200
        except EquipmentHistoryRecord.DoesNotExist:
            return {'error': 'Record not found'}, 404

class EquipmentResource(Resource):
    def post(self):
        try:
            data = request.get_json()
            new_equipment = Equipment.create(
                name=data['name'],
                equipment_type=data['equipment_type'],
                manufacturer=data.get('manufacturer'),
                model=data.get('model'),
                serial_number=data.get('serial_number'),
                out_of_order=data.get('out_of_order', False),
                asset_id=data.get('asset_id'),
                description=data['description'],
                instruction_manual_url=data.get('instruction_manual_url'),
                training_course_url=data.get('training_course_url'),
                required_form=data.get('required_form'),
                procurement_date=data.get('procurement_date'),
                donor=data.get('donor'),
                donor_document=data.get('donor_document'),
                donor_already_taxed=data.get('donor_already_taxed', False),
                is_loaned=data.get('is_loaned', False),
                requires_training=data.get('requires_training', False),
                value_market=data.get('value_market'),
                value_tax=data.get('value_tax'),
                assigned_zone=data['assigned_zone']
            )
            return {'message': 'Equipment created successfully', 'id': new_equipment.id}, 201
        except KeyError as e:
            return {'error': f'Missing key {e}'}, 400

    def get(self, equipment_id):
        try:
            equipment = Equipment.get(Equipment.id == equipment_id)
            return {
                # Assuming serialization of fields is done properly here.
                # Implement serialization logic as needed to convert model instances to JSON-friendly format.
            }
        except DoesNotExist:
            return {'error': 'Equipment not found'}, 404

    def delete(self, equipment_id):
        try:
            equipment = Equipment.get(Equipment.id == equipment_id)
            equipment.delete_instance()
            return {'message': f'Equipment with ID {equipment_id} has been deleted'}, 200
        except DoesNotExist:
            return {'error': 'Equipment not found'}, 404

    def put(self, equipment_id):
        try:
            equipment = Equipment.get(Equipment.id == equipment_id)
            data = request.get_json()
            # Update the equipment instance with new data
            # Ensure proper handling of fields and updating only those provided
            equipment.save()
            return {'message': f'Equipment with ID {equipment_id} has been updated'}, 200
        except DoesNotExist:
            return {'error': 'Equipment not found'}, 404

class PersonRbacResource(Resource):
    def get(self, person_id):
        try:
            person_rbac = PersonRbac.select().where(PersonRbac.person_id == person_id)
            return [{'role': rbac.role, 'permission': rbac.permission} for rbac in person_rbac]
        except DoesNotExist:
            return {'error': 'PersonRbac not found'}, 404

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('role', type=str, required=True)
        parser.add_argument('permission', type=bool, required=True)
        parser.add_argument('person_id', type=int, required=True)
        args = parser.parse_args()

        try:
            person = Person.get_by_id(args['person_id'])
            person_rbac = PersonRbac.create(role=args['role'], permission=args['permission'], person=person)
            return {'message': 'PersonRbac created successfully', 'person_rbac_id': person_rbac.id}, 201
        except Person.DoesNotExist:
            return {'error': 'Person not found'}, 404

    def delete(self, person_rbac_id):
        try:
            person_rbac = PersonRbac.get_by_id(person_rbac_id)
            person_rbac.delete_instance()
            return {'message': f'PersonRbac with ID {person_rbac_id} has been deleted'}
        except PersonRbac.DoesNotExist:
            return {'error': 'PersonRbac not found'}, 404

    def put(self, person_rbac_id):
        parser = reqparse.RequestParser()
        parser.add_argument('role', type=str)
        parser.add_argument('permission', type=bool)
        args = parser.parse_args()

        try:
            person_rbac = PersonRbac.get_by_id(person_rbac_id)
            if 'role' in args:
                person_rbac.role = args['role']
            if 'permission' in args:
                person_rbac.permission = args['permission']
            person_rbac.save()
            return {'message': f'PersonRbac with ID {person_rbac_id} has been updated'}
        except PersonRbac.DoesNotExist:
            return {'error': 'PersonRbac not found'}, 404

class PersonResource(Resource):
    def get(self, person_id):
        try:
            person = Person.get(Person.id == person_id)
            if person.is_deleted:
                return {'error': 'Person has been soft deleted'}, 404
            return {
                'id': person.id,
                'first': person.first,
                'last': person.last,
                'email': person.email,
            }
        except Person.DoesNotExist:
            return {'error': 'Person not found'}, 404

    def delete(self, person_id):
        try:
            person = Person.get(Person.id == person_id)
            person.is_deleted = True
            person.save()
            return {'message': f'Person with ID {person_id} has been soft deleted'}
        except Person.DoesNotExist:
            return {'error': 'Person not found'}, 404

    def put(self, person_id):
        parser = reqparse.RequestParser()
        parser.add_argument('first', type=str, required=True)
        parser.add_argument('last', type=str, required=True)
        args = parser.parse_args()

        try:
            person = Person.get(Person.id == person_id)
            if person.is_deleted:
                return {'error': 'Person has been soft deleted'}, 404
            person.first = args['first']
            person.last = args['last']
            person.email = args['email']
            person.save()
            return {'message': f'Person with ID {person_id} has been updated'}
        except Person.DoesNotExist:
            return {'error': 'Person not found'}, 404

    def patch(self, person_id):
        # curl -X PATCH -H "Content-Type: application/json" -d '{"undelete": true}' http://localhost:5000/person/<person_id>
        # curl -X PATCH -H "Content-Type: application/json" -d '{"restore_softdelete": true}' http://localhost:5000/person/<person_id>
        parser = reqparse.RequestParser()
        parser.add_argument('restore_softdelete', type=bool, default=False)
        parser.add_argument('hard_delete', type=bool, default=False)
        args = parser.parse_args()
        try:
            person = Person.get(Person.id == person_id)
            undelete_flag = args.get('undelete')  # Check if "undelete" is in the JSON data
            hard_delete_flag = args.get('hard_delete')  # Check if "hard_delete" is in the JSON data

            if hard_delete_flag:
                # Perform hard deletion (remove from the database)
                person.delete_instance()
                return {'message': f'Person with ID {person_id} has been hard deleted'}
            elif undelete_flag and person.is_deleted:
                person.is_deleted = False
                person.save()
                return {'message': f'Person with ID {person_id} has been undeleted'}
            elif not undelete_flag:
                return {'message': 'No action specified in the request body'}, 200
            else:
                return {'message': 'Person is not soft-deleted or undelete action not allowed'}, 400
        except Person.DoesNotExist:
            return {'error': 'Person not found'}, 404

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('first', type=str, required=True)
        parser.add_argument('last', type=str, required=True)
        parser.add_argument('email', type=str, required=True)
        args = parser.parse_args()

        new_person = Person.create(
            first=args['first'],
            last=args['last'],
            email=args['email']
        )

        return {'message': 'Person created successfully', 'person_id': new_person.id}, 201

class EquipmentPhotoResource(Resource):
    """
     curl -d @path/to/data.json -X POST
    """
    def post(self, equipment_id):
        if 'photo' in request.files:
            photo = request.files['photo']
            filename = photo.filename
            photo_data = photo.read()
            encoded_data = base64.b64encode(photo_data).decode('utf-8')

            new_photo = EquipmentPhoto.create(equipment=equipment_id, filename=filename, data=encoded_data)
            return {'message': 'Photo uploaded successfully'}, 201
        return {'error': 'No photo uploaded'}, 400

    def get(self, photo_id):
        try:
            photo = EquipmentPhoto.get(EquipmentPhoto.id == photo_id)
            return {
                'id': photo.id,
                'equipment_id': photo.equipment.id,
                'filename': photo.filename,
                'data': photo.data
            }
        except EquipmentPhoto.DoesNotExist:
            return {'error': 'Photo not found'}, 404

    def delete(self, photo_id):
        try:
            photo = EquipmentPhoto.get(EquipmentPhoto.id == photo_id)
            photo.delete_instance()
            return {'message': f'Photo with ID {photo_id} has been deleted'}, 200
        except EquipmentPhoto.DoesNotExist:
            return {'error': 'Photo not found'}, 404

    def put(self, photo_id):
        parser = reqparse.RequestParser()
        parser.add_argument('photo', type=werkzeug.datastructures.FileStorage, location='files')
        args = parser.parse_args()

        try:
            photo = EquipmentPhoto.get(EquipmentPhoto.id == photo_id)
            if args['photo'] is not None:
                file_data = args['photo'].read()
                encoded_data = base64.b64encode(file_data).decode('utf-8')
                photo.data = encoded_data
                photo.filename = args['photo'].filename
                photo.save()
                return {'message': f'Photo with ID {photo_id} has been updated'}, 200
            return {'error': 'No new photo provided'}, 400
        except EquipmentPhoto.DoesNotExist:
            return {'error': 'Photo not found'}, 404

#### UNTESTED

class MembershipTypeMapResource(Resource):
    def get(self, type_id):
        try:
            membership_type = MembershipTypeMap.get(MembershipTypeMap.id == type_id)
            return {
                'id': membership_type.id,
                'name': membership_type.name,
                'description': membership_type.description
            }
        except MembershipTypeMap.DoesNotExist:
            return {'error': 'Membership Type not found'}, 404

    def delete(self, type_id):
        try:
            membership_type = MembershipTypeMap.get(MembershipTypeMap.id == type_id)
            membership_type.delete_instance()
            return {'message': f'Membership Type with ID {type_id} has been deleted'}
        except MembershipTypeMap.DoesNotExist:
            return {'error': 'Membership Type not found'}, 404

    def put(self, type_id):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True)
        parser.add_argument('description', type=str, required=True)
        args = parser.parse_args()

        try:
            membership_type = MembershipTypeMap.get(MembershipTypeMap.id == type_id)
            membership_type.name = args['name']
            membership_type.description = args['description']
            membership_type.save()
            return {'message': f'Membership Type with ID {type_id} has been updated'}
        except MembershipTypeMap.DoesNotExist:
            return {'error': 'Membership Type not found'}, 404

class PersonTrainedEquipmentResource(Resource):
    # CRUD operations for PersonTrainedEquipment (many-to-many relationship)
    # Example: Create a new association between equipment and a person
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('equipment_id', type=int, required=True)
        parser.add_argument('person_id', type=int, required=True)
        args = parser.parse_args()

        try:
            equipment = Equipment.get(Equipment.id == args['equipment_id'])
            person = Person.get(Person.id == args['person_id'])

            association, created = PersonTrainedEquipment.get_or_create(equipment=equipment, person=person)

            if created:
                return {'message': 'Association created successfully'}, 201
            else:
                return {'message': 'Association already exists'}, 200
        except (Equipment.DoesNotExist, Person.DoesNotExist):
            return {'error': 'Equipment or Person not found'}, 404


class ContractTypeMapResource(Resource):
    def get(self, type_id):
        try:
            contract_type = ContractTypeMap.get(ContractTypeMap.id == type_id)
            return {
                'id': contract_type.id,
                'name': contract_type.name,
                'description': contract_type.description
            }
        except ContractTypeMap.DoesNotExist:
            return {'error': 'Contract Type not found'}, 404

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True)
        parser.add_argument('description', type=str, required=True)
        args = parser.parse_args()

        try:
            contract_type = ContractTypeMap.create(name=args['name'], description=args['description'])
            return {'message': 'Contract Type created successfully', 'id': contract_type.id}, 201
        except IntegrityError:
            return {'error': 'Contract Type creation failed'}, 500

    def delete(self, type_id):
        try:
            contract_type = ContractTypeMap.get(ContractTypeMap.id == type_id)
            contract_type.delete_instance()
            return {'message': f'Contract Type with ID {type_id} has been deleted'}
        except ContractTypeMap.DoesNotExist:
            return {'error': 'Contract Type not found'}, 404

    def put(self, type_id):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True)
        parser.add_argument('description', type=str, required=True)
        args = parser.parse_args()

        try:
            contract_type = ContractTypeMap.get(ContractTypeMap.id == type_id)
            contract_type.name = args['name']
            contract_type.description = args['description']
            contract_type.save()
            return {'message': f'Contract Type with ID {type_id} has been updated'}
        except ContractTypeMap.DoesNotExist:
            return {'error': 'Contract Type not found'}, 404

class PersonMembershipResource(Resource):
    def get(self, person_id):
        try:
            person = Person.get(Person.id == person_id)
            memberships = person.personmembership_set.select().join(MembershipTypeMap)
            membership_list = [{'id': membership.membership_type.id, 'name': membership.membership_type.name, 'description': membership.membership_type.description} for membership in memberships]
            return {'person_id': person.id, 'memberships': membership_list}
        except Person.DoesNotExist:
            return {'error': 'Person not found'}, 404

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('person_id', type=int, required=True)
        parser.add_argument('membership_type_id', type=int, required=True)
        args = parser.parse_args()

        try:
            person = Person.get(Person.id == args['person_id'])
            membership_type = MembershipTypeMap.get(MembershipTypeMap.id == args['membership_type_id'])

            association, created = PersonMembership.get_or_create(person=person, membership_type=membership_type)

            if created:
                return {'message': 'Person-Membership association created successfully'}, 201
            else:
                return {'message': 'Person-Membership association already exists'}, 200
        except (Person.DoesNotExist, MembershipTypeMap.DoesNotExist):
            return {'error': 'Person or Membership Type not found'}, 404

    def put(self, person_id, membership_type_id):
        parser = reqparse.RequestParser()
        parser.add_argument('person_id', type=int, required=True)
        parser.add_argument('membership_type_id', type=int, required=True)
        args = parser.parse_args()

        try:
            person = Person.get(Person.id == args['person_id'])
            membership_type = MembershipTypeMap.get(MembershipTypeMap.id == args['membership_type_id'])

            association, created = PersonMembership.get_or_create(person=person, membership_type=membership_type)

            if created:
                return {'message': 'Person-Membership association created successfully'}, 201
            else:
                return {'message': 'Person-Membership association already exists'}, 200
        except (Person.DoesNotExist, MembershipTypeMap.DoesNotExist):
            return {'error': 'Person or Membership Type not found'}, 404

    def delete(self, person_id, membership_type_id):
        try:
            person = Person.get(Person.id == person_id)
            membership_type = MembershipTypeMap.get(MembershipTypeMap.id == membership_type_id)

            association = PersonMembership.get(person=person, membership_type=membership_type)
            association.delete_instance()
            return {'message': 'Person-Membership association deleted successfully'}
        except (Person.DoesNotExist, MembershipTypeMap.DoesNotExist, PersonMembership.DoesNotExist):
            return {'error': 'Person, Membership Type, or association not found'}, 404


# class PersonBillingCadenceResource(Resource):
#     def get(self, person_id):
#         try:
#             person = Person.get(Person.id == person_id)
#             billing_cadences = person.personbillingcadence_set.select().join(BillingCadenceTypeMap)
#             billing_cadence_list = [{'id': billing_cadence.membership_type.id, 'name': billing_cadence.membership_type.name, 'description': billing_cadence.membership_type.description} for billing_cadence in billing_cadences]
#             return {'person_id': person.id, 'billing_cadences': billing_cadence_list}
#         except Person.DoesNotExist:
#             return {'error': 'Person not found'}, 404

#     def post(self):
#         parser = reqparse.RequestParser()
#         parser.add_argument('person_id', type=int, required=True)
#         parser.add_argument('billing_cadence_type_id', type=int, required=True)
#         args = parser.parse_args()

#         try:
#             person = Person.get(Person.id == args['person_id'])
#             billing_cadence_type = BillingCadenceTypeMap.get(BillingCadenceTypeMap.id == args['billing_cadence_type_id'])

#             association, created = PersonBillingCadence.get_or_create(person=person, membership_type=billing_cadence_type)

#             if created:
#                 return {'message': 'Person-Billing Cadence association created successfully'}, 201
#             else:
#                 return {'message': 'Person-Billing Cadence association already exists'}, 200
#         except (Person.DoesNotExist, BillingCadenceTypeMap.DoesNotExist):
#             return {'error': 'Person or Billing Cadence Type not found'}, 404

#     def put(self, person_id, billing_cadence_type_id):
#         parser = reqparse.RequestParser()
#         parser.add_argument('person_id', type=int, required=True)
#         parser.add_argument('billing_cadence_type_id', type=int, required=True)
#         args = parser.parse_args()

#         try:
#             person = Person.get(Person.id == args['person_id'])
#             billing_cadence_type = BillingCadenceTypeMap.get(BillingCadenceTypeMap.id == args['billing_cadence_type_id'])

#             association, created = PersonBillingCadence.get_or_create(person=person, membership_type=billing_cadence_type)

#             if created:
#                 return {'message': 'Person-Billing Cadence association created successfully'}, 201
#             else:
#                 return {'message': 'Person-Billing Cadence association already exists'}, 200
#         except (Person.DoesNotExist, BillingCadenceTypeMap.DoesNotExist):
#             return {'error': 'Person or Billing Cadence Type not found'}, 404

#     def delete(self, person_id, billing_cadence_type_id):
#         try:
#             person = Person.get(Person.id == person_id)
#             billing_cadence_type = BillingCadenceTypeMap.get(BillingCadenceTypeMap.id == billing_cadence_type_id)

#             association = PersonBillingCadence.get(person=person, membership_type=billing_cadence_type)
#             association.delete_instance()
#             return {'message': 'Person-Billing Cadence association deleted successfully'}
#         except (Person.DoesNotExist, BillingCadenceTypeMap.DoesNotExist, PersonBillingCadence.DoesNotExist):
#             return {'error': 'Person, Billing Cadence Type, or association not found'}, 404


class PersonContractResource(Resource):
    """
    curl -X POST http://<your-server-url>/path/to/person-contract \
         -F "contract_type_id=<contract_type_id>" \
         -F "person_id=<person_id>" \
         -F "revision=<revision>" \
         -F "contract=@/path/to/contract_file" 
    """
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('contract_type_id', type=int, required=True)
        parser.add_argument('person_id', type=int, required=True)
        parser.add_argument('revision', type=str)
        parser.add_argument('contract', type=werkzeug.datastructures.FileStorage, location='files')
        args = parser.parse_args()

        if 'contract' in request.files:
            contract_file = request.files['contract']
            filename = contract_file.filename
            file_data = contract_file.read()
            encoded_data = base64.b64encode(file_data).decode('utf-8')

            new_contract = PersonContract.create(
                contract_type=args['contract_type_id'],
                person=args['person_id'],
                revision=args.get('revision'),
                filename=filename,
                data=encoded_data
            )
            return {'message': 'Contract uploaded successfully'}, 201
        return {'error': 'No contract file uploaded'}, 400

    def get(self, contract_id):
        try:
            contract = PersonContract.get(PersonContract.id == contract_id)
            return {
                'id': contract.id,
                'contract_type_id': contract.contract_type.id,
                'person_id': contract.person.id,
                'revision': contract.revision,
                'filename': contract.filename,
                'data': contract.data
            }
        except PersonContract.DoesNotExist:
            return {'error': 'Contract not found'}, 404

    def delete(self, contract_id):
        try:
            contract = PersonContract.get(PersonContract.id == contract_id)
            contract.delete_instance()
            return {'message': f'Contract with ID {contract_id} has been deleted'}, 200
        except PersonContract.DoesNotExist:
            return {'error': 'Contract not found'}, 404

    def put(self, contract_id):
        parser = reqparse.RequestParser()
        parser.add_argument('contract', type=werkzeug.datastructures.FileStorage, location='files')
        parser.add_argument('revision', type=str)
        args = parser.parse_args()

        try:
            contract = PersonContract.get(PersonContract.id == contract_id)
            if 'contract' in request.files:
                contract_file = request.files['contract']
                contract.filename = contract_file.filename
                contract.data = base64.b64encode(contract_file.read()).decode('utf-8')
            if args.get('revision'):
                contract.revision = args['revision']
            contract.save()
            return {'message': f'Contract with ID {contract_id} has been updated'}, 200
        except PersonContract.DoesNotExist:
            return {'error': 'Contract not found'}, 404

class PersonAvatarPicResource(Resource):
    """
     curl -d @path/to/data.json -X POST
    """
    def post(self, person_id):
        if 'avatar' in request.files:
            avatar = request.files['avatar']
            filename = avatar.filename
            file_data = avatar.read()
            encoded_data = base64.b64encode(file_data).decode('utf-8')

            new_avatar = PersonAvatarPic.create(person=person_id, filename=filename, data=encoded_data)
            return {'message': 'Avatar uploaded successfully'}, 201
        return {'error': 'No avatar file uploaded'}, 400

    def get(self, avatar_id):
        try:
            avatar = PersonAvatarPic.get(PersonAvatarPic.id == avatar_id)
            return {
                'id': avatar.id,
                'person_id': avatar.person.id,
                'filename': avatar.filename,
                'data': avatar.data
            }
        except PersonAvatarPic.DoesNotExist:
            return {'error': 'Avatar not found'}, 404

    def delete(self, avatar_id):
        try:
            avatar = PersonAvatarPic.get(PersonAvatarPic.id == avatar_id)
            avatar.delete_instance()
            return {'message': f'Avatar with ID {avatar_id} has been deleted'}, 200
        except PersonAvatarPic.DoesNotExist:
            return {'error': 'Avatar not found'}, 404

    def put(self, avatar_id):
        if 'avatar' in request.files:
            try:
                avatar = PersonAvatarPic.get(PersonAvatarPic.id == avatar_id)
                file_data = request.files['avatar'].read()
                encoded_data = base64.b64encode(file_data).decode('utf-8')
                avatar.data = encoded_data
                avatar.filename = request.files['avatar'].filename
                avatar.save()
                return {'message': f'Avatar with ID {avatar_id} has been updated'}, 200
            except PersonAvatarPic.DoesNotExist:
                return {'error': 'Avatar not found'}, 404
        return {'error': 'No new avatar provided'}, 400

class PersonPhotoResource(Resource):
    """
     curl -d @path/to/data.json -X POST
    """
    def post(self, person_id):
        if 'photo' in request.files:
            photo = request.files['photo']
            filename = photo.filename
            file_data = photo.read()
            encoded_data = base64.b64encode(file_data).decode('utf-8')

            new_photo = PersonPhoto.create(person=person_id, filename=filename, data=encoded_data)
            return {'message': 'Photo uploaded successfully'}, 201
        return {'error': 'No photo file uploaded'}, 400

    def get(self, photo_id):
        try:
            photo = PersonPhoto.get(PersonPhoto.id == photo_id)
            return {
                'id': photo.id,
                'person_id': photo.person.id,
                'filename': photo.filename,
                'data': photo.data
            }
        except PersonPhoto.DoesNotExist:
            return {'error': 'Photo not found'}, 404

    def delete(self, photo_id):
        try:
            photo = PersonPhoto.get(PersonPhoto.id == photo_id)
            photo.delete_instance()
            return {'message': f'Photo with ID {photo_id} has been deleted'}, 200
        except PersonPhoto.DoesNotExist:
            return {'error': 'Photo not found'}, 404

    def put(self, photo_id):
        if 'photo' in request.files:
            try:
                photo = PersonPhoto.get(PersonPhoto.id == photo_id)
                file_data = request.files['photo'].read()
                encoded_data = base64.b64encode(file_data).decode('utf-8')
                photo.data = encoded_data
                photo.filename = request.files['photo'].filename
                photo.save()
                return {'message': f'Photo with ID {photo_id} has been updated'}, 200
            except PersonPhoto.DoesNotExist:
                return {'error': 'Photo not found'}, 404
        return {'error': 'No new photo provided'}, 400

### END UNTESTED



class AllLocationResource(Resource):
    def get(self):
        locations = Location.select()
        location_list = {'locations': [{'id': location.id, 'name': location.name} for location in locations]}
        return location_list

class AllZonesResource(Resource):
    def get(self):
        zones = Zone.select()
        zone_list = {'zones': [{'id': zone.id, 'name': zone.name, 'location': {'id': zone.location.id, 'name': zone.location.name}} for zone in zones]}
        return zone_list

class ZoneResource(Resource):
    def get(self, zone_id):
        try:
            zone = Zone.get(Zone.id == zone_id)
            return {'id': zone.id, 'name': zone.name, 'location': {'id': zone.location.id, 'name': zone.location.name}}
        except Zone.DoesNotExist:
            return {'error': 'Zone not found'}, 404

    def delete(self, zone_id):
        try:
            zone = Zone.get(Zone.id == zone_id)
            zone.delete_instance()
            return {'message': f'Zone with ID {zone_id} has been deleted'}
        except Zone.DoesNotExist:
            return {'error': 'Zone not found'}, 404

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True)
        parser.add_argument('location_id', type=int, required=True)
        args = parser.parse_args()

        location = Location.get(Location.id == args['location_id'])
        new_zone = Zone.create(name=args['name'], location=location)
        return {'message': 'Zone created successfully', 'zone_id': new_zone.id}, 201

class LocationResource(Resource):
    def get(self, location_id):
        try:
            location = Location.get(Location.id == location_id)
            return {'id': location.id, 'name': location.name}
        except Location.DoesNotExist:
            return {'error': 'Location not found'}, 404

    def delete(self, location_id):
        try:
            location = Location.get(Location.id == location_id)
            # Check if there are any zones associated with this location
            associated_zones = Zone.select().where(Zone.location == location)
            associated_zones_list = [{'id': zone.id, 'name': zone.name} for zone in associated_zones]
            if associated_zones:
                return {'error': 'Cannot delete the location as there are associated zones.', 'associations': associated_zones_list}, 400
            
            location.delete_instance()
            return {'message': f'Location with ID {location_id} has been deleted'}
        except Location.DoesNotExist:
            return {'error': 'Location not found'}, 404

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True)
        args = parser.parse_args()

        try:
            new_location = Location.create(name=args['name'])
            return {'message': 'Location created successfully', 'location_id': new_location.id}, 201
        except Zone.DoesNotExist:
            return {'error': 'Zone not found'}, 404
