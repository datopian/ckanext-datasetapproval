
import logging
from ckan.logic.auth import get_package_object
from ckan.plugins import toolkit as tk

log = logging.getLogger(__name__)

@tk.auth_allow_anonymous_access
def package_show_with_approval(context, data_dict):
    user = context.get('user')
    package = get_package_object(context, data_dict)

    if package.extras.get('publishing_status') in ['in_review', 'draft', 'rejected']:
        # Accessiable to within editors so that they can collabrate on the dataset

        try:
            tk.check_access('package_update', context, data_dict)
        except tk.ObjectNotFound:
            return {
                'success': False,
                'msg': tk._('Dataset not found')
                }
        except tk.NotAuthorized:
            return {
                'success': False,
                'msg': tk._('User %s not authorized to read package %s') % (user, package.id)
            }
    
    return {'success': True}
