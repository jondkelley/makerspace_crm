from flask_restful import Api
#from .api_views import AllComputersResource, ComputerResource, AssignComputerResource
from .api_makerspace import (AllLocationResource, AllZonesResource, ZoneResource,
	LocationResource, PersonBillingCadenceResource, PersonMembershipResource, ContractTypeMapResource,
	PersonAllowedEquipmentResource, MembershipTypeMapResource, PersonResource)


api = Api()

api.add_resource(AllZonesResource, '/zone/all')
api.add_resource(AllLocationResource, '/location/all')
api.add_resource(ZoneResource, '/zone', '/zone/<int:zone_id>')
api.add_resource(LocationResource, '/location', '/location/<int:structure_id>')
api.add_resource(PersonBillingCadenceResource, '/person_billing_cadence', '/person_billing_cadence/<int:person_id>/<int:billing_cadence_type_id>')
api.add_resource(PersonMembershipResource, '/person_membership', '/person_membership/<int:person_id>/<int:membership_type_id>')
api.add_resource(ContractTypeMapResource, '/contract_type_map', '/contract_type_map/<int:type_id>')
api.add_resource(PersonAllowedEquipmentResource, '/person_allowed_equipment', '/person_allowed_equipment/<int:person_id>/<int:equipment_id>')
api.add_resource(MembershipTypeMapResource, '/membership_type_map', '/membership_type_map/<int:type_id>')
api.add_resource(PersonResource, '/person', '/person/<int:person_id>')


# Examples
# api.add_resource(AllPersonsResource, '/persons/all')
# api.add_resource(PersonResource, '/persons', '/persons/<int:person_id>')
# api.add_resource(AllComputersResource, '/computers/all')
# api.add_resource(ComputerResource, '/computers', '/computers/<int:computer_id>')
# api.add_resource(AssignComputerResource, '/computers/<int:computer_id>/assign/<int:person_id>')

