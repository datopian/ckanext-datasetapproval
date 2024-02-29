import logging
from functools import partial

from flask import Blueprint, redirect, url_for

from ckan import model
from ckan.lib import base
from ckan.plugins import toolkit
import ckan.lib.base as base
from ckan.views.user import _extra_template_variables
import ckan.lib.helpers as h
from ckan.authz import users_role_for_group_or_org
from ckan.lib.mailer import MailerException
from ckanext.datasetapproval.mailer import mail_package_approve_reject_notification_to_editors
from ckan.views.dataset import url_with_params
import ckan.logic as logic
import ckan.lib.navl.dictization_functions as dict_fns


log = logging.getLogger()

tuplize_dict = logic.tuplize_dict
clean_dict = logic.clean_dict
parse_params = logic.parse_params
flatten_to_string_key = logic.flatten_to_string_key

approveBlueprint = Blueprint('approval', __name__,)


def _pager_url(params_nopage, package_type, q=None, page=None):
    params = list(params_nopage)
    params.append((u'page', page))
    return search_url(params, package_type)


def search_url(params, package_type=None):
    url = h.url_for('approval.dataset_review', id=toolkit.c.user)
    return url_with_params(url, params)


def approve(id):
    return _make_action(id, 'approve')

def reject(id):
    return _make_action(id, 'reject')

def dataset_review(id):
    if toolkit.c.user != id:
        return toolkit.abort(404)

    # Pass extra params to user_object
    if toolkit.c.userobj.plugin_extras:
        toolkit.c.userobj.plugin_extras = toolkit.c.userobj.plugin_extras \
                                    .update({'has_approval_permission': True})
    else :
        toolkit.c.userobj.plugin_extras = {'has_approval_permission': True}

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

    params_nopage = [(k, v) for k, v in toolkit.request.args.items(multi=True)
                     if k != u'page']
    limit = 20
    page = h.get_page_number(toolkit.request.args)
    pager_url = partial(_pager_url, params_nopage, 'dataset')
    
    search_dict = {
        'rows': limit,
        'start': limit * (page - 1),
        'fq': 'publishing_status:in_review',
        'include_in_review': True,
        'include_private': True,
        'include_drafts': True
        }

    in_review_datasets = toolkit.get_action('package_search')(context,
                                               data_dict=search_dict)
    
    print(search_dict)

    extra_vars['user_dict'].update({
        'datasets' : in_review_datasets['results'],
        'total_count': in_review_datasets['count']
        })
    
    extra_vars[u'page'] = h.Page(
        collection = in_review_datasets['results'],
        page = page,
        url = pager_url,
        item_count = in_review_datasets['count'],
        items_per_page = limit
    )
    extra_vars[u'page'].items = in_review_datasets['results']

    return base.render(u'user/dashboard_review.html', extra_vars)


def _raise_not_authz_or_not_pending(id):
    dataset_dict = toolkit.get_action('package_show') \
                    ({u'ignore_auth': True}, {'id': id})
    permission = users_role_for_group_or_org(dataset_dict.get('owner_org'), toolkit.c.userobj.name)
    is_pending = dataset_dict.get('publishing_status') == 'in_review'

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
    toolkit.get_action('package_patch')(
        {'model': model, 'user': toolkit.c.user},
        {'id': package_id, 'publishing_status': states[action], 'private': False}
    )
    # Notify editors via email that dataset has been approved/rejected.
    try:
        mail_package_approve_reject_notification_to_editors(package_id, states[action])
    except MailerException:
        message = '[email] Failed to sent notification to the editor: {}'
        log.critical(message.format(package_id))
    
    return toolkit.redirect_to(controller='dataset', action='read', id=package_id)


def terms_and_conditions():
    data_dict = {}
    if toolkit.request.method == 'POST':
        data_dict['terms_agreed'] = True
        if 'agree' in toolkit.request.form:
            # Redirect to the "Add Metadata" step if agreed
            return toolkit.redirect_to(url_for('dataset.new'))
        else:
            # Handle the case where terms are not agreed upon
            pass
    # Render the terms and conditions page if GET request or terms not agreed
    return base.render('package/snippets/terms_and_conditions.html', extra_vars={'pkg_dict': data_dict})


def request_review(id):
    # Retrieve the context for CKAN's logic functions
    context = {'model': model, 'session': model.Session,
               'user': toolkit.c.user or toolkit.c.author}

    try:
        package_dict = toolkit.get_action('package_show')(context, {'id': id})
    except toolkit.ObjectNotFound:
        toolkit.abort(404, toolkit._('Dataset not found'))
    except toolkit.NotAuthorized:
        toolkit.abort(401, toolkit._('Unauthorized to read dataset'))

    return base.render('package/snippets/review_request.html', extra_vars={'pkg_dict': package_dict, 'data': package_dict}) 

@approveBlueprint.route('/submit_review', methods=['POST'])
def submit_review():
    context = {'model': model, 'session': model.Session,
               'user': toolkit.c.user or toolkit.c.author}
    if toolkit.request.method == 'POST':
        dataset_name = toolkit.request.form['dataset_name']
        data_dict = toolkit.get_action(u'package_show')(context, {u'id': dataset_name})
        data_dict['publishing_status'] = u'in_review'
        toolkit.get_action(u'package_update')(
            context,
            data_dict
        )

        id=data_dict['id']
        return h.redirect_to(u'{}.read'.format('dataset'), id=id)


approveBlueprint.add_url_rule(u'/dataset-publish/<id>/approve', view_func=approve)
approveBlueprint.add_url_rule(u'/dataset-publish/<id>/reject', view_func=reject)
approveBlueprint.add_url_rule(u'/user/<id>/dataset_review', view_func=dataset_review)
approveBlueprint.add_url_rule(u'/dataset/terms', view_func=terms_and_conditions)
approveBlueprint.add_url_rule(u'/dataset/<id>/review', view_func=request_review)
# approveBlueprint.add_url_rule(u'/dataset/submit_review', view_func=submit_review, methods=['POST'])

