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
<img width="1100" alt="Screenshot 2022-11-23 at 8 43 38 AM" src="https://user-images.githubusercontent.com/87696933/203462820-9b5053cc-cad2-4353-afc0-f93fd144f9c4.png">


2. Users with editor role in organization can create a dataset and submit it for approval
**Editors user get this message**
<img width="1017" alt="Screenshot 2022-11-23 at 9 02 22 AM" src="https://user-images.githubusercontent.com/87696933/203462885-de0da117-98f3-4dae-b8e9-423acc4aa0e2.png">

**Submit for approval by clicking finish button.**
<img width="999" alt="Screenshot 2022-11-23 at 9 02 32 AM" src="https://user-images.githubusercontent.com/87696933/203462940-2aaffcc8-537d-43d6-863d-07cc0f73f481.png">

3. Organization admin receives the email notification when dataset is submitted for approval.
**Example:**
<img width="839" alt="Screenshot 2022-11-23 at 9 04 30 AM" src="https://user-images.githubusercontent.com/87696933/203463066-5edbd734-35d2-4a55-a2c2-ad80af26b68c.png">
4. Users with admin role in organization can reivew with approving or rejecting the dataset.
<img width="883" alt="Screenshot 2022-11-23 at 9 06 14 AM" src="https://user-images.githubusercontent.com/87696933/203463236-c372451e-f8a3-415e-b12b-d881d5651c8f.png">
5. If dataset is approved by admin, it will be published and visible to all users.
<img width="1496" alt="Screenshot 2022-11-23 at 9 08 13 AM" src="https://user-images.githubusercontent.com/87696933/203463433-305c0478-2ada-4320-9f85-e72182a3802c.png">
6. If dataset is rejected, it will be visible to only editor and syasadmin users.
<img width="1051" alt="Screenshot 2022-11-23 at 9 06 56 AM" src="https://user-images.githubusercontent.com/87696933/203463317-a1926f40-31c0-44b6-b4e7-00b6f7a9110d.png">
5. If dataset is rejected, editor can edit the dataset and submit it for approval again.

## License

[AGPL](https://www.gnu.org/licenses/agpl-3.0.en.html)
