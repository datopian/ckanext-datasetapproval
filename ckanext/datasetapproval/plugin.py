import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan.lib.plugins import DefaultPermissionLabels
from ckan.authz import users_role_for_group_or_org

from ckanext.datasetapproval import auth, actions, blueprints, helpers, validation

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


def editor_publishing_dataset(owner_org, user_obj):
    '''
    Check if user is editor of the organization
    '''
    user_capacity = users_role_for_group_or_org(owner_org, user_obj.name)
    if user_obj.sysadmin:
        return False
    return user_capacity != 'admin'

class DatasetapprovalPlugin(plugins.SingletonPlugin, 
        DefaultPermissionLabels, toolkit.DefaultDatasetForm):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IValidators)
    plugins.implements(plugins.IAuthFunctions)
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
        toolkit.add_resource('assets',
            'datasetapproval')

   # IActions
    def get_actions(self):
        return {
            'package_create': actions.package_create,
            'package_show': actions.package_show,
            'package_update': actions.package_update,
            'resource_create': actions.resource_create,
            'resource_update': actions.resource_update,
        }
    # IAuthFunctions
    def get_auth_functions(self):
        return {
            'package_show_with_approval': auth.package_show_with_approval
        }

    #IDatasetForm
    def create_package_schema(self):
        schema = super(DatasetapprovalPlugin, self).create_package_schema()
        schema.update({
            'publishing_status': [toolkit.get_validator('publishing_status_validator'),
                                        toolkit.get_converter('convert_to_extras')]
        })
        return schema
    def update_package_schema(self):
        schema = super(DatasetapprovalPlugin, self).update_package_schema()
        schema.update({
            'publishing_status': [toolkit.get_validator('publishing_status_validator'), 
                                        toolkit.get_converter('convert_to_extras')]
        })
        return schema

    def show_package_schema(self):
        schema = super(DatasetapprovalPlugin, self).show_package_schema()
        schema.update({
            'publishing_status': [toolkit.get_converter('convert_from_extras')]
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
            'publishing_status_validator': validation.publishing_status_validator,
        }

    # IPackageController
    def create(self, entity):
        # if editor published the dataset it will be awalys private
        if editor_publishing_dataset(entity.owner_org, toolkit.c.userobj):
            entity.private = True
        return entity

    def edit(self, entity):
        # if editor published the dataset it will be awalys private
        if editor_publishing_dataset(entity.owner_org, toolkit.c.userobj):
            entity.private = True
        return entity


    def before_search(self, search_params):
        include_in_review = search_params.get('include_in_review', False)

        if include_in_review:
            search_params.pop('include_in_review', None)

        include_drafts = search_params.get('include_drafts', False)

        if toolkit.c.userobj:
            user_is_syadmin = toolkit.c.userobj.sysadmin
        else:
            user_is_syadmin = False
            
        if user_is_syadmin:
            return search_params
        elif include_in_review:
            return search_params
        elif include_drafts:
            return search_params
        else:   
            search_params.update({
                'fq': '!(publishing_status:(draft OR in_review OR rejected))' + search_params.get('fq', '')
            })
        return search_params

    # IPermissionLabels
    def get_user_dataset_labels(self, user_obj):
        labels = super(DatasetapprovalPlugin, self
                       ).get_user_dataset_labels(user_obj)

        if user_obj and user_obj.plugin_extras:
            if user_obj.plugin_extras.get('has_approval_permission', False):
                labels = [x for x in labels if not x.startswith('member')]
                orgs = toolkit.get_action(u'organization_list_for_user')(
                    {u'user': user_obj.id}, {u'permission': u'admin'})
                labels.extend(u'member-%s' % o['id'] for o in orgs)
        return labels


    # IBlueprint
    def get_blueprint(self):
        return blueprints.approveBlueprint


