import ckan.plugins.toolkit as toolkit

import logging as log

log = log.getLogger(__name__)


def state_validator(key, data, errors, context):
    user_orgs = toolkit.get_action('organization_list_for_user')(
        context, {'id': context['user']})
    office_id = data.get(('owner_org',))

    state = data.pop(key, None)
    is_ready_to_publish = data.get(('publishing_status',)) == 'published'
  
    # If the user is member of the organization but not an admin, force the
    # state to be pending
    for org in user_orgs:
        if org.get('id') == office_id:
            if org.get('capacity') == 'admin':
                # If no state provided and user is an admin, default to active
                state = state or 'active'
            elif is_ready_to_publish:
                # If not admin and not draft, dataset has to go through approval process. 
                state = 'pending'
            else: 
                state = False

    data[key] = state or 'active'
    return 'hello'
