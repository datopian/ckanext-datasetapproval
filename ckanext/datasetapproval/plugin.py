import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan.lib.plugins import DefaultPermissionLabels

from ckanext.datasetapproval import actions, blueprints, helpers, validation

import json
import logging as log
from ckan.common import _, c

log = log.getLogger(__name__)

import six
from six import text_type
def unicode_please(value):
    if isinstance(value, six.binary_type):
        try:
            return six.ensure_text(value)
        except UnicodeDecodeError:
            return value.decode(u'cp1252')
    return text_type(value)

class DatasetapprovalPlugin(plugins.SingletonPlugin, 
        DefaultPermissionLabels, toolkit.DefaultDatasetForm):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IValidators)
    plugins.implements(plugins.IActions)
    plugins.implements(plugins.IBlueprint)
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IPackageController, inherit=True)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IDatasetForm)
    plugins.implements(plugins.IPermissionLabels, inherit=True)



    # IConfigurer
    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic',
            'datasetapproval')

   # IActions
    def get_actions(self):
        return {
            'package_create': actions.package_create,
            'package_show': actions.package_show,
            'package_update': actions.package_update
        }

    #IDatasetForm
    def create_package_schema(self):
        schema = super(DatasetapprovalPlugin, self).create_package_schema()
        schema.update({
            'approval_state': [toolkit.get_validator('state_validator'), toolkit.get_converter('convert_to_extras')]
        })
        return schema
    def update_package_schema(self):
        schema = super(DatasetapprovalPlugin, self).update_package_schema()
        # our custom field
        schema.update({
            'approval_state': [toolkit.get_validator('state_validator'), toolkit.get_converter('convert_to_extras')]
        })
        return schema

    def show_package_schema(self):
        schema = super(DatasetapprovalPlugin, self).show_package_schema()
        schema.update({
            'approval_state': [toolkit.get_converter('convert_from_extras')]
        })
        return schema

    def is_fallback(self):
        # Return True to register this plugin as the default handler for
        return True

    def package_types(self):
        # registers itself as the default (above).
        return []

    # ITemplateHelpers
    def get_helpers(self):
        return {
            'is_admin': helpers.is_admin,
        }

    # IValidators
    def get_validators(self):
        return {
            'state_validator': validation.state_validator,
        }

    # IPackageController
    def before_search(self, search_params):
        if toolkit.c.userobj:
            user_is_syadmin = toolkit.c.userobj.sysadmin
        else:
            user_is_syadmin = False

        include_approval_pending = search_params.get('include_approval_pending', False)
        include_drafts = search_params.get('include_drafts', False)

        if include_drafts:
            # show pending dataset in user dashboard.
            search_params.update({
                'fq': "+creator_user_id:{0} ".format(c.userobj.id) + search_params.get('fq', '')
            })
        elif include_approval_pending or user_is_syadmin: 
            search_params.pop('include_approval_pending', None)

            # Order dataset by approval state for sysadmin user.
            if search_params.get('sort', '').startswith('approval_state'):
                search_params.update({
                    'fq': '!(approval_state:(active OR approved))' + search_params.get('fq', '')
                 })
            return search_params
        else:
            search_params.update({
                'fq': '!(approval_state:(pending OR rejected))' + search_params.get('fq', '')
            })
        return search_params

    # IPermissionLabels
    def get_user_dataset_labels(self, user_obj):
        labels = super(DatasetapprovalPlugin, self
                       ).get_user_dataset_labels(user_obj)

        dataset_approve_permission = False
        if user_obj and user_obj.plugin_extras:
            dataset_approve_permission = user_obj.plugin_extras.get('dataset_approve_permission', False)

        if dataset_approve_permission:
            labels = [x for x in labels if not x.startswith('member')]
            orgs = toolkit.get_action(u'organization_list_for_user')(
                {u'user': user_obj.id}, {u'permission': u'admin'})
            labels.extend(u'member-%s' % o['id'] for o in orgs)
            
        return labels


    # IBlueprint
    def get_blueprint(self):
        return blueprints.approveBlueprint


