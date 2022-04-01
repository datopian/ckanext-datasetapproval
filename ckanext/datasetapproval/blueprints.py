import logging

from flask import Blueprint

from ckan import model
from ckan.lib import base
from ckan.plugins import toolkit


log = logging.getLogger()


approveBlueprint = Blueprint('approval', __name__,)


def approve(id):
    return _make_action(id, 'approve')

def reject(id):
    return _make_action(id, 'reject')


def _raise_not_authz_or_not_pending(id):
    toolkit.check_access(
        'package_delete', {'model': model, 'user': toolkit.c.user}, {'id': id})
    # check approval_state is pending
    data_dict = toolkit.get_action('package_show')({}, {'id': id})
    if data_dict.get('approval_state') != 'pending':
        raise toolkit.ObjectNotFound('Dataset "{}" not found'.format(id))


def _make_action(package_id, action='reject'):
    states = {
        'reject': 'rejected',
        'approve': 'approved'
    }
    # check access and state
    _raise_not_authz_or_not_pending(package_id)
    data_dict = toolkit.get_action('package_patch')(
        {'model': model, 'user': toolkit.c.user},
        {'id': package_id, 'approval_state': states[action]}
    )
    msg = 'Dataset "{0}" {1}'.format(data_dict['title'], states[action])
    if action == 'approve':
        toolkit.h.flash_success(msg)
    else:
        toolkit.h.flash_error(msg)
    return toolkit.redirect_to(controller='dataset', action='read', id=data_dict['name'])


approveBlueprint.add_url_rule('/dataset-publish/<id>/approve', view_func=approve)
approveBlueprint.add_url_rule('/dataset-publish/<id>/reject', view_func=reject)
