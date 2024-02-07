from flask_restful import Resource, reqparse
from flask import jsonify, request

class BaseResource(Resource):
    @staticmethod
    def model_to_dict(instance, exclude_fields=None):
        """
        Converts a model instance into a dictionary, excluding specified fields.
        
        :param instance: The model instance to serialize.
        :param exclude_fields: A list of field names to exclude from the resulting dictionary.
        :return: A dictionary representation of the model instance.
        """
        if exclude_fields is None:
            exclude_fields = ['is_deleted']

        data = {}
        for field_name in instance._meta.fields.keys():
            if field_name not in exclude_fields:
                value = getattr(instance, field_name)
                # Convert complex types to their string representation or use custom formatting
                if isinstance(value, Model):
                    # This handles foreign keys by inserting the ID, but you might customize it
                    data[field_name] = value.id
                else:
                    data[field_name] = value
        return data

    def parse_data(self, model=None):
        """
        Parses and validates JSON request data against a specified Peewee model's schema.

        This method is intended to ensure that the incoming request data contains only valid fields
        that exist in the specified model's schema. It filters out any invalid fields (i.e., fields
        not present in the model) and returns the validated data. If no model is specified, the method
        attempts to use a default model associated with the resource class.

        Parameters:
        - model (Model, optional): The Peewee model class to validate the incoming data against.
          If None, the default model associated with the resource class is used.

        Returns:
        - tuple: A tuple containing three elements:
            1. dict or None: The validated data as a dictionary if validation succeeds, or None if it fails.
            2. dict or None: An error message as a dictionary if validation fails, or None if it succeeds.
            3. int or None: An HTTP status code (400 for Bad Request) if validation fails, or None if it succeeds.

        The method performs the following steps:
        1. Extracts data from the incoming HTTP request's body, assuming JSON format.
        2. Validates each key in the request data against the model's fields, filtering out any
           fields not defined in the model.
        3. Returns the filtered data along with any error information and HTTP status code as appropriate.

        This approach helps in maintaining data integrity and ensures that only relevant and
        valid data is processed by the resource methods.
        """
        data = request.get_json()
        if model is None:
            model = self.model
        invalid_columns = find_invalid_columns_in_table(model, data)
        if invalid_columns:
            return None, {'error': f'Invalid columns: {invalid_columns}'}, 400
        return {k: v for k, v in data.items() if k not in invalid_columns}, None, None

    @staticmethod
    def handle_does_not_exist(e):
        """
        return 404 document
        """
        return {'error': 'Resource not found'}, 404

    def get(self, object_id):
        try:
            obj = self.model.get(self.model.id == object_id)
            if obj.is_deleted:
                return {'error': f'{self.model.__name__} has been deleted'}, 404
            if obj.is_hidden:
                return {'error': f'{self.model.__name__} is hidden'}, 403  # Using 403 Forbidden for hidden objects
            return obj.to_dict(), 200
        except self.model.DoesNotExist as e:
            return self.handle_does_not_exist(e)

    def post(self):
        valid_data, error, status_code = self.parse_data()
        if error:
            return error, status_code
        obj = self.model.create(**valid_data)
        return {'message': f'{self.model.__name__} created successfully', 'id': obj.id}, 201

    def delete(self, object_id):
        try:
            obj = self.model.get(self.model.id == object_id)
            # Soft delete the object by setting is_deleted to True
            obj.is_deleted = True
            obj.save()
            return {'message': f'{self.model.__name__} with ID {object_id} has been soft deleted'}, 200
        except self.model.DoesNotExist:
            return {'error': f'{self.model.__name__} not found'}, 404

    def put(self, object_id):
        valid_data, error, status_code = self.parse_data()
        if error:
            return error, status_code

        try:
            obj = self.model.get(self.model.id == object_id)
            if obj.is_deleted or obj.is_hidden:
                return {'error': f'{self.model.__name__} is not accessible'}, 403

            for key, value in valid_data.items():
                setattr(obj, key, value)

            obj.save()
            return {'message': f'{self.model.__name__} with ID {object_id} has been updated'}, 200
        except self.model.DoesNotExist:
            return {'error': f'{self.model.__name__} not found'}, 404

    def patch(self, object_id):
        parser = reqparse.RequestParser()
        parser.add_argument('restore_softdelete', type=bool, store_missing=False)
        parser.add_argument('hard_delete', type=bool, store_missing=False)
        parser.add_argument('hide', type=bool, store_missing=False)
        parser.add_argument('unhide', type=bool, store_missing=False)
        args = parser.parse_args()

        try:
            obj = self.model.get(self.model.id == object_id)
            if 'hard_delete' in args and args['hard_delete']:
                obj.delete_instance()
                return {'message': f'{self.model.__name__} with ID {object_id} has been hard deleted'}, 200
            if 'hide' in args and args['hide']:
                obj.is_hidden = True
                obj.save()
                return {'message': f'{self.model.__name__} with ID {object_id} has been hidden'}, 200
            if 'unhide' in args and args['unhide'] and obj.is_hidden:
                obj.is_hidden = False
                obj.save()
                return {'message': f'{self.model.__name__} with ID {object_id} has been unhidden'}, 200

            return {'error': 'Invalid request or no action specified'}, 400
        except DoesNotExist:
            return {'error': f'{self.model.__name__} not found'}, 404
