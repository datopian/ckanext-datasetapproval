this.ckan.module('form-save', function (jQuery) {
    return {
      /* An object of module options */
      options: {
        type:''
      },
      /* Sets up the event listeners for the object. Called internally by
       * module.createInstance().
       *
       * Returns nothing.
       */
      initialize: function () {
        jQuery.proxyAll(this, /_on/);
        this.el.on('click', this._onClick);
      },
  
      /* Event handler that displays the confirm dialog */
      _onClick: function (event) {
      
        if(this.options.type === 'draft'){
          event.preventDefault();
          var form = $('#dataset-edit')
          console.log($('#field-publishing_status'))
          $('#field-publishing_status').val('draft')
          form.find('button[name=save]').click()
        }
        if(this.options.type === 'published'){
          event.preventDefault();
          var form = $('#dataset-edit')
          
          if ($('#field-publishing_status').val() != 'in_review'){
            $('#field-publishing_status').val('published')
          }

          form.find('button[name=save]').click()
        }
        if(this.options.type === 'resource-draft'){
          event.preventDefault();
          var form = $('#resource-edit')
          $('#field-pkg_publishing_status').val('draft')
          form.find('button[value=go-metadata]').click()
        }
      },
    };
  });