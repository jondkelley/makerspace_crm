from flask_restful import Resource, reqparse
from models.crm.makerspace import (Person)
from models.crm.chore import (ChoreHistory, ChoreOwnership, Chore)
from models.crm.cardaccess import (DoorProfiles, PersonDoorCredentialProfile, DoorAccessLog, KeyCard, KeyCode)

from flask import jsonify
from peewee import IntegrityError

class ChoreResource(Resource):
    def get(self, chore_id):
        try:
            chore = Chore.get(Chore.id == chore_id)
            return {
                'id': chore.id,
                'name': chore.name,
                'description': chore.description,
                'classification': chore.classification,
                'creator': chore.creator.id if chore.creator else None,
                'last_completed': chore.last_completed,
                'frequency': chore.frequency
            }
        except DoesNotExist:
            return {'error': 'Chore not found'}, 404

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True)
        parser.add_argument('description', type=str, required=True)
        parser.add_argument('classification', type=str, required=True)
        parser.add_argument('creator_id', type=int)
        parser.add_argument('frequency', type=str, required=True)
        args = parser.parse_args()

        try:
            creator = Person.get_by_id(args['creator_id']) if args['creator_id'] else None
            chore = Chore.create(
                name=args['name'],
                description=args['description'],
                classification=args['classification'],
                creator=creator,
                last_completed=datetime.datetime.now(),
                frequency=args['frequency']
            )
            return {'message': 'Chore created successfully', 'chore_id': chore.id}, 201
        except DoesNotExist:
            return {'error': 'Creator not found'}, 404

    def put(self, chore_id):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str)
        parser.add_argument('description', type=str)
        parser.add_argument('classification', type=str)
        parser.add_argument('creator_id', type=int)
        parser.add_argument('frequency', type=str)
        parser.add_argument('last_completed', type=str)  # Use a suitable date/time format
        args = parser.parse_args()

        try:
            chore = Chore.get_by_id(chore_id)
            if 'name' in args:
                chore.name = args['name']
            if 'description' in args:
                chore.description = args['description']
            if 'classification' in args:
                chore.classification = args['classification']
            if 'creator_id' in args:
                chore.creator = Person.get_by_id(args['creator_id']) if args['creator_id'] else None
            if 'frequency' in args:
                chore.frequency = args['frequency']
            if 'last_completed' in args:
                chore.last_completed = datetime.datetime.strptime(args['last_completed'], "%Y-%m-%d %H:%M:%S")

            chore.save()
            return {'message': f'Chore with ID {chore_id} has been updated'}
        except DoesNotExist:
            return {'error': 'Chore not found or invalid input'}, 404

    def delete(self, chore_id):
        try:
            chore = Chore.get_by_id(chore_id)
            chore.delete_instance()
            return {'message': f'Chore with ID {chore_id} has been deleted'}
        except DoesNotExist:
            return {'error': 'Chore not found'}, 404

class ChoreOwnershipResource(Resource):
    def get(self, ownership_id):
        try:
            ownership = ChoreOwnership.get(ChoreOwnership.id == ownership_id)
            return {
                'id': ownership.id,
                'person_id': ownership.person.id,
                'chore_id': ownership.chore.id,
                'completion_percentage': ownership.completion_percentage,
                'notes': ownership.notes
            }
        except DoesNotExist:
            return {'error': 'Chore ownership record not found'}, 404

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('person_id', type=int, required=True)
        parser.add_argument('chore_id', type=int, required=True)
        parser.add_argument('completion_percentage', type=float, default=0.0)
        parser.add_argument('notes', type=str)
        args = parser.parse_args()

        try:
            person = Person.get_by_id(args['person_id'])
            chore = Chore.get_by_id(args['chore_id'])
            ownership = ChoreOwnership.create(
                person=person,
                chore=chore,
                completion_percentage=args['completion_percentage'],
                notes=args['notes']
            )
            return {'message': 'Chore ownership created successfully', 'ownership_id': ownership.id}, 201
        except DoesNotExist:
            return {'error': 'Person or Chore not found'}, 404

    def put(self, ownership_id):
        parser = reqparse.RequestParser()
        parser.add_argument('person_id', type=int)
        parser.add_argument('chore_id', type=int)
        parser.add_argument('completion_percentage', type=float)
        parser.add_argument('notes', type=str)
        args = parser.parse_args()

        try:
            ownership = ChoreOwnership.get_by_id(ownership_id)
            if 'person_id' in args:
                ownership.person = Person.get_by_id(args['person_id'])
            if 'chore_id' in args:
                ownership.chore = Chore.get_by_id(args['chore_id'])
            if 'completion_percentage' in args:
                ownership.completion_percentage = args['completion_percentage']
            if 'notes' in args:
                ownership.notes = args['notes']

            ownership.save()
            return {'message': f'ChoreOwnership with ID {ownership_id} has been updated'}
        except DoesNotExist:
            return {'error': 'ChoreOwnership not found or invalid Person/Chore'}, 404

    def delete(self, ownership_id):
        try:
            ownership = ChoreOwnership.get_by_id(ownership_id)
            ownership.delete_instance()
            return {'message': f'ChoreOwnership with ID {ownership_id} has been deleted'}
        except DoesNotExist:
            return {'error': 'ChoreOwnership not found'}, 404

class ChoreHistoryResource(Resource):
    def get(self, history_id):
        try:
            history = ChoreHistory.get(ChoreHistory.id == history_id)
            return {
                'id': history.id,
                'chore_id': history.chore.id,
                'person_id': history.person.id if history.person else None,
                'notes': history.notes,
                'class_type': history.class_type,
                'status': history.status
            }
        except DoesNotExist:
            return {'error': 'Chore history record not found'}, 404

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('chore_id', type=int, required=True)
        parser.add_argument('person_id', type=int)
        parser.add_argument('notes', type=str)
        parser.add_argument('class_type', type=str, required=True)
        parser.add_argument('status', type=str, required=True)
        args = parser.parse_args()

        try:
            chore = Chore.get_by_id(args['chore_id'])
            person = Person.get_by_id(args['person_id']) if args['person_id'] else None
            history = ChoreHistory.create(
                chore=chore,
                person=person,
                notes=args['notes'],
                class_type=args['class_type'],
                status=args['status']
            )
            return {'message': 'Chore history created successfully', 'history_id': history.id}, 201
        except DoesNotExist:
            return {'error': 'Chore or Person not found'}, 404

    def put(self, history_id):
        parser = reqparse.RequestParser()
        parser.add_argument('chore_id', type=int)
        parser.add_argument('person_id', type=int)
        parser.add_argument('notes', type=str)
        parser.add_argument('class_type', type=str)
        parser.add_argument('status', type=str)
        args = parser.parse_args()

        try:
            history = ChoreHistory.get_by_id(history_id)
            if 'chore_id' in args:
                history.chore = Chore.get_by_id(args['chore_id'])
            if 'person_id' in args:
                history.person = Person.get_by_id(args['person_id']) if args['person_id'] else None
            if 'notes' in args:
                history.notes = args['notes']
            if 'class_type' in args:
                history.class_type = args['class_type']
            if 'status' in args:
                history.status = args['status']

            history.save()
            return {'message': f'ChoreHistory with ID {history_id} has been updated'}
        except DoesNotExist:
            return {'error': 'ChoreHistory not found or invalid Chore/Person'}, 404

    def delete(self, history_id):
        try:
            history = ChoreHistory.get_by_id(history_id)
            history.delete_instance()
            return {'message': f'ChoreHistory with ID {history_id} has been deleted'}
        except DoesNotExist:
            return {'error': 'ChoreHistory not found'}, 404
