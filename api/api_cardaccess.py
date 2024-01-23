from flask_restful import Resource, reqparse
from models.crm.makerspace import (Person)
from models.crm.cardaccess import (KEY_CARD_TYPES, DoorProfiles, PersonDoorCredentialProfile, DoorAccessLog, KeyCard, KeyCode)

from peewee import DoesNotExist
from flask import jsonify
from peewee import IntegrityError
import datetime

class DoorAccessLogResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('log_sha1', type=str, required=True)
    parser.add_argument('event_dt', type=str, required=True)  # Format as 'YYYY-MM-DD HH:MM:SS'
    parser.add_argument('card_number', type=int, required=True)
    parser.add_argument('event_type', type=str, required=True)
    parser.add_argument('event_type_id', type=int, required=True)
    parser.add_argument('event_reason', type=str, required=True)
    parser.add_argument('door', type=int, required=True)
    parser.add_argument('controller', type=int, required=True)
    parser.add_argument('access_granted', type=bool, required=True)
    parser.add_argument('person_id', type=int, required=True)
    

    def get(self, log_id):
        try:
            log = DoorAccessLog.get(DoorAccessLog.id == log_id)
            return {
                'id': log.id,
                'log_sha1': log.log_sha1,
                'event_dt': log.event_dt,
                'card_number': log.card_number,
                'event_type': log.event_type,
                'event_type_id': log.event_type_id,
                'event_reason': log.event_reason,
                'door': log.door,
                'controller': log.controller,
                'access_granted': log.access_granted,
                'person_id': log.person.id if log.person else None
            }
        except DoesNotExist:
            return {'error': 'Log not found'}, 404

    def post(self):
        args = self.parser.parse_args()
        try:
            person = Person.get_by_id(args['person_id'])
            log = DoorAccessLog.create(
                log_sha1=args['log_sha1'],
                card_number=args['card_number'],
                event_type=args['event_type'],
                event_type_id=args['event_type_id'],
                event_reason=args['event_reason'],
                door=args['door'],
                controller=args['controller'],
                access_granted=args['access_granted'],
                person=person
            )
            return {'message': 'Log created successfully', 'log_id': log.id}, 201

        except DoesNotExist:
            return {'error': 'Person not found'}, 404

    def put(self, log_id):
        args = self.parser.parse_args()
        try:
            log = DoorAccessLog.get_by_id(log_id)
            if 'person_id' in args:
                log.person = Person.get_by_id(args['person_id'])
            # Update other fields if they are in args
            log.save()
            return {'message': f'Log with ID {log_id} has been updated'}
        except DoesNotExist:
            return {'error': 'Log or related entity not found'}, 404

    def delete(self, log_id):
        try:
            log = DoorAccessLog.get_by_id(log_id)
            log.delete_instance()
            return {'message': f'Log with ID {log_id} has been deleted'}
        except DoesNotExist:
            return {'error': 'Log not found'}, 404

class KeyCardResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('card_number', type=int, required=True)
    parser.add_argument('card_type', type=str, required=True, choices=KEY_CARD_TYPES)
    parser.add_argument('person_id', type=int, required=True)
    

    def get(self, card_id):
        try:
            card = KeyCard.get(KeyCard.id == card_id)
            return {
                'id': card.id,
                'card_number': card.card_number,
                'card_type': card.card_type,
                'person_id': card.person.id
            }
        except DoesNotExist:
            return {'error': 'KeyCard not found'}, 404

    def post(self):
        args = self.parser.parse_args()
        try:
            person = Person.get_by_id(args['person_id'])
            card = KeyCard.create(
                card_number=args['card_number'],
                card_type=args['card_type'],
                person=person
            )
            return {'message': 'KeyCard created successfully', 'card_id': card.id}, 201

        except DoesNotExist:
            return {'error': 'Person not found'}, 404

    def put(self, card_id):
        args = self.parser.parse_args()
        try:
            card = KeyCard.get_by_id(card_id)
            if 'person_id' in args:
                card.person = Person.get_by_id(args['person_id'])
            # Update other fields if they are in args
            card.save()
            return {'message': f'KeyCard with ID {card_id} has been updated'}
        except DoesNotExist:
            return {'error': 'KeyCard or related entity not found'}, 404

    def delete(self, card_id):
        try:
            card = KeyCard.get_by_id(card_id)
            card.delete_instance()
            return {'message': f'KeyCard with ID {card_id} has been deleted'}
        except DoesNotExist:
            return {'error': 'KeyCard not found'}, 404

class KeyCodeResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('passcode', type=int, required=True)
    parser.add_argument('person_id', type=int, required=True)

    def get(self, code_id):
        try:
            code = KeyCode.get(KeyCode.id == code_id)
            return {
                'id': code.id,
                'passcode': code.passcode,
                'person_id': code.person.id
            }
        except DoesNotExist:
            return {'error': 'KeyCode not found'}, 404

    def post(self):
        args = self.parser.parse_args()
        try:
            person = Person.get_by_id(args['person_id'])
            code = KeyCode.create(
                passcode=args['passcode'],
                person=person
            )
            return {'message': 'KeyCode created successfully', 'code_id': code.id}, 201

        except DoesNotExist:
            return {'error': 'Person not found'}, 404

    def put(self, code_id):
        args = self.parser.parse_args()
        try:
            code = KeyCode.get_by_id(code_id)
            if 'person_id' in args:
                code.person = Person.get_by_id(args['person_id'])
            # Update other fields if they are in args
            code.save()
            return {'message': f'KeyCode with ID {code_id} has been updated'}
        except DoesNotExist:
            return {'error': 'KeyCode or related entity not found'}, 404

    def delete(self, code_id):
        try:
            code = KeyCode.get_by_id(code_id)
            code.delete_instance()
            return {'message': f'KeyCode with ID {code_id} has been deleted'}
        except DoesNotExist:
            return {'error': 'KeyCode not found'}, 404
