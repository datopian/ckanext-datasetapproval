import logging
import ckan.authz as authz

from ckan.lib.mailer import MailerException
from ckan.plugins import toolkit
import ckan.plugins as p
import ckan.logic as logic

from ckanext.datasetapproval.mailer import mail_package_review_request_to_admins

log = logging.getLogger()


@p.toolkit.chained_action
@logic.side_effect_free
def package_show(up_func, context, data_dict):
    toolkit.check_access('package_show_with_approval', context, data_dict)
    return up_func(context, data_dict)

@p.toolkit.chained_action
def package_create(up_func, context, data_dict):
    dataset_dict = up_func(context, data_dict)
    # Sent email to admins to review the dataset
    if dataset_dict.get('publishing_status') == 'in_review':
        try:
            mail_package_review_request_to_admins(context, dataset_dict, 'new')
        except MailerException:
            message = '[email] Package review request is not sent: {0}'
            log.critical(message.format(data_dict.get('title')))
    return dataset_dict


@p.toolkit.chained_action
def package_update(up_func, context, data_dict):
    dataset_dict = up_func(context, data_dict)
    
    # Sent email to admins to review the dataset
    if dataset_dict.get('publishing_status') == 'in_review':
        try:
            mail_package_review_request_to_admins(context, dataset_dict, 'updated')
        except MailerException:
            message = '[email] Package review request is not sent: {0}'
            log.critical(message.format(data_dict.get('title')))
    return dataset_dict


@p.toolkit.chained_action   
def resource_create(up_func,context, data_dict):
    result = up_func(context, data_dict)
     # little hack here, update dataset publishing status 
    if data_dict.get('pkg_publishing_status', False):
        toolkit.get_action('package_patch')(context, {
            'id': data_dict.get('package_id', ''), 
            'publishing_status': data_dict.get('pkg_publishing_status')
            })
        data_dict.pop('pkg_publishing_status', None)
    return result


@p.toolkit.chained_action   
def resource_update(up_func,context, data_dict):
    result = up_func(context, data_dict)
    # little hack here, update dataset publishing status 
    if data_dict.get('pkg_publishing_status', False):
        toolkit.get_action('package_patch')(context, {
            'id': data_dict.get('package_id', ''), 
            'publishing_status': data_dict.get('pkg_publishing_status')
            })
        data_dict.pop('pkg_publishing_status', None)
    return result
