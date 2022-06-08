import logging

from ckan.lib.mailer import MailerException
from ckan.plugins import toolkit
import ckan.plugins as p
import ckan.logic as logic

from ckanext.datasetapproval.mailer import mail_package_review_request_to_admins

log = logging.getLogger()


@p.toolkit.chained_action
@logic.side_effect_free
def package_show(up_func, context, data_dict):
    package = up_func(context, data_dict)
    # User with less perms then creator should not be able to access pending dataset
    pending = package.get('approval_state') == 'pending'
    # Same With rejected
    rejected = package.get('approval_state') == 'rejected'
    try:
        toolkit.check_access('package_update', context, data_dict)
        can_edit = True
    except toolkit.NotAuthorized:
        can_edit = False
    if not can_edit and pending:
        raise toolkit.ObjectNotFound
    if not can_edit and rejected:
        raise toolkit.ObjectNotFound
    return package


@p.toolkit.chained_action
def package_create(up_func, context, data_dict):
    dataset_dict = up_func(context, data_dict)
    if dataset_dict.get('approval_state') == 'pending':
        try:
            mail_package_review_request_to_admins(context, dataset_dict, 'new')
        except MailerException:
            message = '[email] Package review request is not sent: {0}'
            log.critical(message.format(data_dict.get('title')))
    return dataset_dict


@p.toolkit.chained_action
def package_update(up_func, context, data_dict):
    dataset_dict = up_func(context, data_dict)
    if dataset_dict.get('approval_state') == 'pending':
        try:
            mail_package_review_request_to_admins(context, dataset_dict, 'updated')
        except MailerException:
            message = '[email] Package review request is not sent: {0}'
            log.critical(message.format(data_dict.get('title')))
    return dataset_dict
