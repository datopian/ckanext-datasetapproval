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
        permission = users_role_for_group_or_org(pkg_organizaiton, toolkit.c.userobj.name)
        if permission == 'admin' or toolkit.c.userobj.sysadmin:
            dataset_with_approval_access.append(dataset)

    extra_vars['user_dict'].update({
        'datasets' : dataset_with_approval_access,
        })

    return base.render(u'user/dashboard_review.html', extra_vars)

def _raise_not_authz_or_not_pending(id):
    dataset_dict = toolkit.get_action('package_show') \
                    ({u"ignore_auth": True}, {'id': id})
    permission = users_role_for_group_or_org(dataset_dict.get('owner_org'), toolkit.c.userobj.name)
    is_pending = dataset_dict.get('approval_state') == 'pending'

    if is_pending and (toolkit.c.userobj.sysadmin or permission == 'admin'):
        return 
    else :
        raise toolkit.abort(404, 'Dataset "{}" not found'.format(id))

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
    
    if action == 'approve':
        issues_list = toolkit.get_action('issue_search')(
            {'model': model, 'user': toolkit.c.user}, 
            {'dataset_id': package_id })
        for issue in issues_list['results']:
            issue_dict = {
                'issue_number': str(issue.get('number', '')),
                'dataset_id': package_id,
                'status': 'closed'
                }
            toolkit.get_action('issue_update')({'ignore_auth': True}, issue_dict)
        msg = 'Dataset "{0}" {1}.'.format(data_dict['title'], states[action])
        toolkit.h.flash_success(msg)
        return toolkit.redirect_to(controller='dataset', action='read', id=data_dict['name'])
    else:
        msg = 'Dataset "{0}" {1}. Please provide your feedback comment below.' \
                .format(data_dict['title'], states[action]) 
        toolkit.h.flash_error(msg)
        return toolkit.redirect_to(controller='issues', action='new', dataset_id=package_id)


approveBlueprint.add_url_rule('/dataset-publish/<id>/approve', view_func=approve)
approveBlueprint.add_url_rule('/dataset-publish/<id>/reject', view_func=reject)
approveBlueprint.add_url_rule(u'/user/<id>/dataset_review', view_func=dataset_review)

