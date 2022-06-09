import logging

from flask import Blueprint

from ckan import model
from ckan.lib import base
from ckan.plugins import toolkit
import ckan.lib.base as base
from ckan.views.user import _extra_template_variables
import ckan.lib.helpers as h
from ckan.authz import users_role_for_group_or_org
from ckan.lib.mailer import MailerException
from ckanext.datasetapproval.mailer import mail_package_approve_reject_notification_to_editors
log = logging.getLogger()


approveBlueprint = Blueprint('approval', __name__,)


def approve(id):
    return _make_action(id, 'approve')

def reject(id):
    return _make_action(id, 'reject')

def dataset_review(id):
    if toolkit.c.user != id:
        return toolkit.abort(404)

    context = {
        u'model': model,
        u'session': model.Session,
        u'user': toolkit.c.user,
        u'auth_user_obj': toolkit.c.userobj,
        u'for_view': True
    }
    data_dict = {
        u'id': id,
        u'user_obj': toolkit.c.userobj,
        u'include_num_followers': True
    }

    extra_vars = _extra_template_variables(context, data_dict)

    if extra_vars is None:
        return h.redirect_to(u'user.login')

    search_dict = {
        'rows': 50,
        'fq': 'approval_state:pending',
        'include_approval_pending': True,
        'include_private': True
        }

    review_pending_dataset = toolkit.get_action('package_search')(context=context,
                                               data_dict=search_dict).get('results')

    dataset_with_approval_access = []
    for dataset in review_pending_dataset: 
        pkg_organizaiton = dataset.get('owner_org')
        permisssion = users_role_for_group_or_org(pkg_organizaiton, toolkit.c.userobj.name)
        if permisssion == 'admin':
            dataset_with_approval_access.append(dataset)

    extra_vars['user_dict'].update({
        'datasets' : dataset_with_approval_access,
        })

    return base.render(u'user/dashboard_review.html', extra_vars)

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
    # Notify editors via email that dataset has been approved/rejected.
    try:
        mail_package_approve_reject_notification_to_editors(package_id, states[action])
    except MailerException:
        message = '[email] Failed to sent notification to the editor: {}'
        log.critical(message.format(package_id))
    
    msg = 'Dataset "{0}" {1}'.format(data_dict['title'], states[action])
    if action == 'approve':
        toolkit.h.flash_success(msg)
    else:
        toolkit.h.flash_error(msg)
    return toolkit.redirect_to(controller='dataset', action='read', id=data_dict['name'])


approveBlueprint.add_url_rule('/dataset-publish/<id>/approve', view_func=approve)
approveBlueprint.add_url_rule('/dataset-publish/<id>/reject', view_func=reject)
approveBlueprint.add_url_rule(u'/user/<id>/dataset_review', view_func=dataset_review)

