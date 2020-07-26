NextCloud Registration interface
===

Django project to register new users into a nextcloud instance with invite codes.

Usage
---
First copy and modify ./nextcloud_register/local.py.default to ./nextcloud_register/local.py.
```bash
cp ./nextcloud_register/local.py.default ./nextcloud_register/local.py
```
Install the necessary requirements
```bash
./install_requirements.sh
```
Then run the script.
```bash
python manage.py runserver
```
Or run it on a proper server or whatever idk.
