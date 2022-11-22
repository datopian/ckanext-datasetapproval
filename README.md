[![CKAN](https://img.shields.io/badge/ckan-2.9-orange.svg?style=flat-square)](https://github.com/ckan/ckan/tree/2.9)

# ckanext-datasetapproval
An extension which provides a feature to approve or reject a dataset before making it public.

## Installation
To install ckanext-datasetapproval:

Note: if you're using `ckanext_scheming` extension, add new field to the schema configuration YAML file.

   - field_name: publishing_status
     label: Publishing Status
     form_snippet: null
     display_snippet: null
     validators: ignore_missing publishing_status_validator

1. Activate your CKAN virtual environment, for example:

     . /usr/lib/ckan/default/bin/activate

2. Clone the source and install it on the virtualenv

    git clone https://github.com//ckanext-datasetapproval.git
    cd ckanext-datasetapproval
    pip install -e .
	pip install -r requirements.txt

3. Add `dataset_approval` to the `ckan.plugins` setting in your CKAN
   config file (by default the config file is located at
   `/etc/ckan/default/ckan.ini`).

4. Restart CKAN. For example if you've deployed CKAN with Apache on Ubuntu:

     sudo service apache2 reload




## License

[AGPL](https://www.gnu.org/licenses/agpl-3.0.en.html)
