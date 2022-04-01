import ckan.plugins.toolkit as toolkit

import logging as log

log = log.getLogger(__name__)


def state_validator(key, data, errors, context):
    user_orgs = toolkit.get_action('organization_list_for_user')(
        context, {'id': context['user']})
    office_id = data.get(('owner_org',))

    state = data.pop(key, None)

    # If the user is member of the organization but not an admin, force the
    # state to be pending
    for org in user_orgs:
        if org.get('id') == office_id:
            if org.get('capacity') == 'admin':
                # If no state provided and user is an admin, default to active
                state = state or 'active'
            else:
                # If not admin, create as pending
                state = 'pending'

    data[key] = state or 'active'
    return 'hello'
