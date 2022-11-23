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


## Approval Flow for Dataset
1. All publisher users can save datasets as drafts for later editing, while creating/updating datasets without publishing it to the public.
2. Users with editor role in organization can create a dataset and submit it for approval.
3. Organization admin receives the email notification when dataset is submitted for approval.
4. Users with admin role in organization can reivew with approving or rejecting the dataset.
5. If dataset is approved by admin, it will be published and visible to all users.
6. If dataset is rejected, it will be visible to only editor and syasadmin users.
5. If dataset is rejected, editor can edit the dataset and submit it for approval again.

## License

[AGPL](https://www.gnu.org/licenses/agpl-3.0.en.html)
