from flask_restful import Api
#from .api_views import AllComputersResource, ComputerResource, AssignComputerResource
from .api_makerspace import (AllLocationResource, AllZonesResource, ZoneResource,
	LocationResource, PersonMembershipResource, ContractTypeMapResource,
	PersonTrainedEquipmentResource, MembershipTypeMapResource, PersonResource, PersonRbacResource,
	EquipmentPhotoResource, PersonContractResource, PersonAvatarPicResource, PersonPhotoResource)
from .api_chore import (ChoreHistoryResource, ChoreOwnershipResource, ChoreResource)
from .api_cardaccess import (DoorAccessLogResource, KeyCardResource, KeyCodeResource)

api = Api()

prefix = '/v1/api'
api.add_resource(AllZonesResource, f'{prefix}/zone/all')
api.add_resource(ZoneResource, f'{prefix}/zone', f'{prefix}/zone/<int:zone_id>')
api.add_resource(AllLocationResource, f'{prefix}/location/all')
api.add_resource(LocationResource, f'{prefix}/location', f'{prefix}/location/<int:structure_id>')
#api.add_resource(PersonBillingCadenceResource, f'{prefix}/person_billing_cadence', f'{prefix}/person_billing_cadence/<int:person_id>/<int:billing_cadence_type_id>')
api.add_resource(PersonMembershipResource, f'{prefix}/person_membership', f'{prefix}/person_membership/<int:person_id>/<int:membership_type_id>')
api.add_resource(ContractTypeMapResource, f'{prefix}/contract_type_map', f'{prefix}/contract_type_map/<int:type_id>')
api.add_resource(PersonTrainedEquipmentResource, f'{prefix}/person_allowed_equipment', f'{prefix}/person_allowed_equipment/<int:person_id>/<int:equipment_id>')
api.add_resource(MembershipTypeMapResource, f'{prefix}/membership_type_map', f'{prefix}/membership_type_map/<int:type_id>')
api.add_resource(PersonResource, f'{prefix}/person', f'{prefix}/person/<int:person_id>')
api.add_resource(PersonRbacResource, f'{prefix}/person_rbac', f'{prefix}/person_rbac/<int:person_id>')
api.add_resource(ChoreResource, f'{prefix}/chore', f'{prefix}/chore/<int:chore_id>')
api.add_resource(ChoreOwnershipResource, f'{prefix}/chore_ownership', f'{prefix}/chore_ownership/<int:chore_id>')
api.add_resource(ChoreHistoryResource, f'{prefix}/chore_history', f'{prefix}/chore_history/<int:history_id>')
api.add_resource(DoorAccessLogResource, f'{prefix}/access/door_access_log', f'{prefix}/access/door_access_log/<int:log_id>')
api.add_resource(KeyCardResource, f'{prefix}/access/cardid', f'{prefix}/access/cardid/<int:card_id>')
api.add_resource(KeyCodeResource, f'{prefix}/access/keycode', f'{prefix}/access/keycode/<int:code_id>')
api.add_resource(EquipmentPhotoResource, f'{prefix}/equipment_photo', f'{prefix}/equipment_photo/<int:photo_id>')
api.add_resource(PersonContractResource, f'{prefix}/person_contract', f'{prefix}/person_contract/<int:contract_id>')
api.add_resource(PersonAvatarPicResource, f'{prefix}/person_avatar', f'{prefix}/person_avatar/<int:avatar_id>')
api.add_resource(PersonPhotoResource, f'{prefix}/person_photo', f'{prefix}/person_photo/<int:photo_id>')
api.add_resource(EquipmentHistoryRecordResource, f'{prefix}/equipment_history', f'{prefix}/equipment_history/<int:record_id>')
api.add_resource(EquipmentResource, f'{prefix}/equipment', f'{prefix}/equipment/<int:equipment_id>')


# Examples
# api.add_resource(AllPersonsResource, '/persons/all')
# api.add_resource(PersonResource, '/persons', '/persons/<int:person_id>')
# api.add_resource(AllComputersResource, '/computers/all')
# api.add_resource(ComputerResource, '/computers', '/computers/<int:computer_id>')
# api.add_resource(AssignComputerResource, '/computers/<int:computer_id>/assign/<int:person_id>')

