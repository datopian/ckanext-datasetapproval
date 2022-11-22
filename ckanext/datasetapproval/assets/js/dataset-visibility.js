/* Dataset visibility toggler
 * When no organization is selected in the org dropdown then set visibility to
 * public always and disable dropdown
 */
delete this.ckan.module.registry['dataset-visibility']
this.ckan.module('dataset-visibility', function ($) {
    return {
      currentValue: false,
      options: {
        organizations: $('#field-organizations'),
        visibility: $('#field-private'),
        currentValue: null,
        authorizedOrg: []
      },
  
      initialize: function() {
        $.proxyAll(this, /_on/);
        this.options.currentValue = this.options.visibility.val();
        this.options.organizations.on('change', this._onOrganizationChange);
        this._onOrganizationChange();
        var self = this;
        this.sandbox.client.call(
          'GET', 'organization_list_for_user', '', function(data) {
            self.options.authorizedOrg = data.result
              var capacity = data.result.find(
                (org) => org.id === self.options.organizations.val()).capacity
              var value = self.options.organizations.val();
              if (value && capacity === 'admin' ) {
                self.options.visibility
                  .prop('disabled', false)
                  .val(self.options.currentValue);
              } else {
                self.options.visibility
                  .prop('disabled', true)
                  .val('True');
              }
          },
        )
      },
  
      _onOrganizationChange: function() {
        var capacity = false
        if (this.options.authorizedOrg.length != 0) {
          capacity = this.options.authorizedOrg.find(
            (org) => org.id === this.options.organizations.val()).capacity
        }       
        var value = this.options.organizations.val();
        if (value && capacity === 'admin') {
          this.options.visibility
            .prop('disabled', false)
            .val(this.options.currentValue);
        } else {
          this.options.visibility
            .prop('disabled', true)
            .val('True');
        }
      }
    };
  });
  