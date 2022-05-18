import logging

from ckan import model
from ckan.common import config
from ckan.plugins import toolkit
from ckan.lib.mailer import mail_user
from ckan.lib.base import render_jinja2
from ckan.logic.action.get import member_list as core_member_list

log = logging.getLogger(__name__)


def mail_package_review_request_to_admins(context, data_dict, _type='new'):
    members = core_member_list(
        context=context,
        data_dict={'id': data_dict.get('owner_org')}
    )
    admin_ids = [i[0] for i in members if i[2] == 'Admin']

    for admin_id in admin_ids:
        user = model.User.get(admin_id)
        if user.email:
            subj = _compose_email_subj(_type)
            body = _compose_email_body(context, data_dict, user, _type)
            mail_user(user, subj, body)
            log.debug('[email] Dataset review request email sent to {0}'.format(user.name))


def _compose_email_subj(_type):
    return ' A {0} dataset is requested for review.'.format(_type)

def _get_publisher_name(context, id):
    try:
        user_dict = toolkit.get_action('user_show')(context, {'id': id})
        return user_dict.get('display_name')
    except toolkit.ObjectNotFound as e:
        return 'None'

def _compose_email_body(context, data_dict, user, _type):
    pkg_link = toolkit.url_for('dataset_read', id=data_dict['name'], qualified=True)
    admin_name = user.fullname or user.name
    site_title = config.get('ckan.site_title')
    site_url = config.get('ckan.site_url')
    package_title = data_dict.get('title')
    package_description = data_dict.get('notes', '')
    package_url = pkg_link
    publisher_name = _get_publisher_name(context, data_dict.get('creator_user_id'))

    email_body = f'''
        Dear {admin_name},

        {'An'if _type == 'updated' else 'A'} {_type} dataset has been requested for review by {publisher_name}:

            {package_title}

            {package_description}

        To approve or reject the request, please visit the following page (logged in as an admin):

            {package_url}

        Have a nice day.


        --
        Message sent by {site_title} ({site_url})
        This is an automated message, please don't respond to this address.
        '''
    log.error(email_body)
    return email_body
