import ckan.plugins.toolkit as toolkit

import logging as log

log = log.getLogger(__name__)

def publishing_status_validator(key, data, errors, context):
    user_orgs = toolkit.get_action('organization_list_for_user')(
        context, {'id': context['user']})
    
    state = data.pop(key, 'draft')

    owner_org_id = data.get(('owner_org',))

    # Published means user finished updating the dataset and ready to publish. 
    if state == 'published':
        for org in user_orgs:
            if org.get('id') == owner_org_id:
                # IF the user is not an admin, force the publishing status to be in_review
                # Otherwise, leave aways approved.
                    if org.get('capacity') == 'admin' :
                        state =  'approved'
                    else: 
                        state = 'in_review'
    data[key] = state
    return
