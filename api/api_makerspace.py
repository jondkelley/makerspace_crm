from flask_restful import Resource, reqparse
from models.makerspace import (BillingCadenceTypeMap, MembershipTypeMap, ContractTypeMap, Zone, Location, Equipment,
    Person, PersonEmergencyContact, PersonContact, PersonTrainedEquipment, PersonContract, PersonMembership)
from models.cardaccess import (DoorProfiles, PersonDoorCredentialProfile, DoorAccessLog, KeyCard, KeyCode)

from flask import jsonify
from peewee import IntegrityError


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

class PersonAllowedEquipmentResource(Resource):
    # CRUD operations for PersonAllowedEquipment (many-to-many relationship)
    # Example: Create a new association between equipment and a person
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('equipment_id', type=int, required=True)
        parser.add_argument('person_id', type=int, required=True)
        args = parser.parse_args()

        try:
            equipment = Equipment.get(Equipment.id == args['equipment_id'])
            person = Person.get(Person.id == args['person_id'])

            association, created = PersonAllowedEquipment.get_or_create(equipment=equipment, person=person)

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


class PersonBillingCadenceResource(Resource):
    def get(self, person_id):
        try:
            person = Person.get(Person.id == person_id)
            billing_cadences = person.personbillingcadence_set.select().join(BillingCadenceTypeMap)
            billing_cadence_list = [{'id': billing_cadence.membership_type.id, 'name': billing_cadence.membership_type.name, 'description': billing_cadence.membership_type.description} for billing_cadence in billing_cadences]
            return {'person_id': person.id, 'billing_cadences': billing_cadence_list}
        except Person.DoesNotExist:
            return {'error': 'Person not found'}, 404

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('person_id', type=int, required=True)
        parser.add_argument('billing_cadence_type_id', type=int, required=True)
        args = parser.parse_args()

        try:
            person = Person.get(Person.id == args['person_id'])
            billing_cadence_type = BillingCadenceTypeMap.get(BillingCadenceTypeMap.id == args['billing_cadence_type_id'])

            association, created = PersonBillingCadence.get_or_create(person=person, membership_type=billing_cadence_type)

            if created:
                return {'message': 'Person-Billing Cadence association created successfully'}, 201
            else:
                return {'message': 'Person-Billing Cadence association already exists'}, 200
        except (Person.DoesNotExist, BillingCadenceTypeMap.DoesNotExist):
            return {'error': 'Person or Billing Cadence Type not found'}, 404

    def put(self, person_id, billing_cadence_type_id):
        parser = reqparse.RequestParser()
        parser.add_argument('person_id', type=int, required=True)
        parser.add_argument('billing_cadence_type_id', type=int, required=True)
        args = parser.parse_args()

        try:
            person = Person.get(Person.id == args['person_id'])
            billing_cadence_type = BillingCadenceTypeMap.get(BillingCadenceTypeMap.id == args['billing_cadence_type_id'])

            association, created = PersonBillingCadence.get_or_create(person=person, membership_type=billing_cadence_type)

            if created:
                return {'message': 'Person-Billing Cadence association created successfully'}, 201
            else:
                return {'message': 'Person-Billing Cadence association already exists'}, 200
        except (Person.DoesNotExist, BillingCadenceTypeMap.DoesNotExist):
            return {'error': 'Person or Billing Cadence Type not found'}, 404

    def delete(self, person_id, billing_cadence_type_id):
        try:
            person = Person.get(Person.id == person_id)
            billing_cadence_type = BillingCadenceTypeMap.get(BillingCadenceTypeMap.id == billing_cadence_type_id)

            association = PersonBillingCadence.get(person=person, membership_type=billing_cadence_type)
            association.delete_instance()
            return {'message': 'Person-Billing Cadence association deleted successfully'}
        except (Person.DoesNotExist, BillingCadenceTypeMap.DoesNotExist, PersonBillingCadence.DoesNotExist):
            return {'error': 'Person, Billing Cadence Type, or association not found'}, 404

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
