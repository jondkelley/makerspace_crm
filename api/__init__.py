from flask_restful import Api
#from .api_views import AllComputersResource, ComputerResource, AssignComputerResource
from .api_makerspace import (AllLocationResource, AllZonesResource, ZoneResource,
	LocationResource, PersonBillingCadenceResource, PersonMembershipResource, ContractTypeMapResource,
	PersonAllowedEquipmentResource, MembershipTypeMapResource, PersonResource, PersonRbacResource)


api = Api()

prefix = '/api'
api.add_resource(AllZonesResource, f'{prefix}/zone/all')
api.add_resource(AllLocationResource, f'{prefix}/location/all')
api.add_resource(ZoneResource, f'{prefix}/zone', f'{prefix}/zone/<int:zone_id>')
api.add_resource(LocationResource, f'{prefix}/location', f'{prefix}/location/<int:structure_id>')
api.add_resource(PersonBillingCadenceResource, f'{prefix}/person_billing_cadence', f'{prefix}/person_billing_cadence/<int:person_id>/<int:billing_cadence_type_id>')
api.add_resource(PersonMembershipResource, f'{prefix}/person_membership', f'{prefix}/person_membership/<int:person_id>/<int:membership_type_id>')
api.add_resource(ContractTypeMapResource, f'{prefix}/contract_type_map', f'{prefix}/contract_type_map/<int:type_id>')
api.add_resource(PersonAllowedEquipmentResource, f'{prefix}/person_allowed_equipment', f'{prefix}/person_allowed_equipment/<int:person_id>/<int:equipment_id>')
api.add_resource(MembershipTypeMapResource, f'{prefix}/membership_type_map', f'{prefix}/membership_type_map/<int:type_id>')
api.add_resource(PersonResource, f'{prefix}/person', f'{prefix}/person/<int:person_id>')
api.add_resource(PersonRbacResource, f'{prefix}/person_rbac', f'{prefix}/person_rbac/<int:person_id>')



# Examples
# api.add_resource(AllPersonsResource, '/persons/all')
# api.add_resource(PersonResource, '/persons', '/persons/<int:person_id>')
# api.add_resource(AllComputersResource, '/computers/all')
# api.add_resource(ComputerResource, '/computers', '/computers/<int:computer_id>')
# api.add_resource(AssignComputerResource, '/computers/<int:computer_id>/assign/<int:person_id>')

