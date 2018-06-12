![Biuletyn Polonistyczny](https://biuletynpolonistyczny.pl/static/bportal/images/logo.svg)

# Polish Studies Bulletin [ver. 2.0] 

Polish Studies Bulletin - an Internet portal containing up-to-date information on the life of the Polish studies community [https://biuletynpolonistyczny.pl]

The project of the [Institute of Literary Research of the Polish Academy of Sciences](http://ibl.waw.pl/) and the [Poznań Supercomputing and Networking Center](http://www.pcss.pl), carried out in cooperation with the [Committee of Literature Sciences of the Polish Academy of Sciences](http://knol.pan.pl/) and the Conference of University Polish Studies.

Code developed and owned by Poznań Supercomputing and Networking Center and available under the European Union Public License (EUPL) ver. 1.2. For full license text go to https://joinup.ec.europa.eu/collection/eupl/eupl-text-11-12.

---

# Configuration of a development environment

Requirements:

* Python 2.7.x and 3.5.x
* npm 3.5.x and gulp 3.9.x
* PostgreSQL 9.x (create bportal_db database)
* Solr 6.5.x (create bportal core)

Install:

	sudo apt-get install python3-psycopg2
	sudo apt-get install python3-dev python3-setuptools
	sudo apt-get install python3-pip 
	sudo pip3 install Django==1.9.13
	sudo pip3 install django-reversion==2.0.13
	sudo pip3 install django-autocomplete-light==3.2.10
	sudo pip3 install django-addanother==2.0.0
	sudo pip3 install django-ckeditor==5.3.0
	sudo pip3 install django-floppyforms==1.6.2
	sudo pip3 install django-bootstrap==0.2.4
	sudo pip3 install django-bootstrap-breadcrumbs==0.8.2
	sudo pip3 install django-mptt==0.8.3
	sudo pip3 install django-taggit==0.22.2
	sudo pip3 install django-polymorphic==0.9.1
	sudo pip3 install django-sitemessage==0.7.1
	sudo pip3 install django-extra-views==0.7.1
	sudo pip3 install django-imagekit==3.3
	sudo pip3 install webencodings==0.5.1
	sudo pip3 install django-wysiwyg==0.7.1
	sudo pip3 install django-simple-captcha==0.5.5
	sudo pip3 install django-filter==1.0.4
	sudo pip3 install django-phonenumber-field==0.7.2
	sudo pip3 install pysolr==3.4.0
	sudo pip3 install django-haystack==2.6.1
	sudo pip3 install django-cities-light==3.2.0
	sudo pip3 install six==1.10.0
	sudo pip3 uninstall Pillow
	sudo apt-get install libtiff5-dev libjpeg8-dev zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev tcl8.6-dev tk8.6-dev python-tk
	sudo pip3 install Pillow==3.0.0
	sudo apt-get install python-dev python-pip python-lxml libcairo2 libpango1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info
	sudo pip3 install weasyprint==0.24
	sudo pip3 install django-weasyprint==0.1
	sudo pip3 install html5lib==0.9999999
	sudo pip3 install tablib==0.12.1
	sudo pip3 install django-import-export==0.7.0
	sudo pip3 install python-dateutil==2.6.0
	sudo pip3 install django-meta==1.4
	sudo pip3 install social-auth-app-django==2.1.0

Copy bportal/settings.py.template to bportal/settings.py and adjust values. Next startup up a project:

	gulp
	python3 manage.py collectstatic
	python3 manage.py migrate
	python3 manage.py makemigrations bportal
	python3 manage.py migrate bportal
	python3 manage.py deleterevisions
	python3 manage.py createinitialrevisions
	sudo python3 manage.py cities_light --force-all
	python3 manage.py createsuperuser
	python3 manage.py runserver
	
Login as superuser and add:

* a site on `http://localhost:8000/admin/sites/site/`
* five flat pages on `http://localhost:8000/admin/flatpages/flatpage/` (/about/, /cookies/, /editors/, /faq/, /partners/)

Add system data:

	python3 manage.py loaddata bportal/fixtures/initial_data.json

Copy bportal/newsletter/newsletter.sh.template to newsletter.sh and adjust paths.

Configure the Solr core according to config/solr/* files.

# Configuration of a production environment

Requirements:

* Apache 2.4.x with mod_wsgi

Install:

	pip3 install python-memcached==1.59
	
Remove DEBUG options from bportal/settings.py and set the following:

```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': 'unix:/tmp/memcached.sock',
    }
}
```

Import people, projects and dissertations from files obtained from OPI:

* `http://localhost:8000/admin/bportal/person/import/`
* `http://localhost:8000/admin/bportal/project/import/`
* `http://localhost:8000/admin/bportal/dissertation/import/`

Rebuild the Solr index:

	python3 manage.py clear_index
	python3 manage.py update_index bportal

