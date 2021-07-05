# Scinguistics Archive

The Scinguistics Archive is a WebApp developed to serve the [Scinguistics](https://cramdvoicelessons.blog/) community as a repository for audio recordings of voice lessons and related voice training material.

This WebApp is built using the [Django web framework](https://www.djangoproject.com/), and uses [PostgreSQL](https://www.postgresql.org/) as a database and [Backblaze B2](https://www.backblaze.com/b2/cloud-storage.html) as a storage solution for audio recordings. It utilizes [django-allauth](https://www.intenct.nl/projects/django-allauth/) for user authentication via the [Patreon API](https://docs.patreon.com/#introduction).

The WebApp available at https://archive.cramdvoicelessons.blog/, and it was developed by [Lílian](https://github.com/lily-mosquitoes) and [Emilia](https://github.com/EmiliaBlasten) for the [Scinguistics team](https://cramdvoicelessons.blog/) with support from [CRAMDVoiceLessons](https://www.patreon.com/CRAMDvoicelessons).

## specifications

This WebApp is hosted with [Heroku](https://www.heroku.com/about) provisioned with the [Heroku Postgres Add-on](https://elements.heroku.com/addons/heroku-postgresql) and [jonathanong's FFmpeg buildpack](https://elements.heroku.com/buildpacks/jonathanong/heroku-buildpack-ffmpeg-latest).

## configuration variables

Invoked in `scinguistics_archive/settings.py`, these should be exported as environment variables and values of IDs and Keys should be kept secret.
- `DJANGO_ALLOWED_HOSTS` (string of host names separated by comma, e.g. `"example.herokuapp.com,127.0.0.1"`)
- `DJANGO_DEBUG` (set "True" on test server, "False" on production)
- `DJANGO_SECRET_KEY` (a large random string, you can use [python's secrets.token_urlsafe](https://docs.python.org/3/library/secrets.html#secrets.token_urlsafe) to produce one)
- `DATABASE_URL` (parsed by [dj-database-url](https://github.com/kennethreitz/dj-database-url), [see schema](https://github.com/kennethreitz/dj-database-url#url-schema))
- `BACKBLAZE_KEY_ID` (from your B2 Application Key [non-master], [see Backblaze B2 docs](https://www.backblaze.com/b2/docs/application_keys.html))
- `BACKBLAZE_KEY` (from your B2 Application Key [non-master], [see Backblaze B2 docs](https://www.backblaze.com/b2/docs/application_keys.html))
- `BACKBLAZE_BUCKET` (your B2 Bucket Name, [see Backblaze B2 docs](https://www.backblaze.com/b2/docs/buckets.html))
- `PATREON_CLIENT_ID` (from your [Patreon API Client](https://www.patreon.com/portal/registration/register-clients))
- `PATREON_CLIENT_SECRET` (from your [Patreon API Client](https://www.patreon.com/portal/registration/register-clients))
- `SECURE_SSL_REDIRECT` (set "False" on test server, "True" on production)

## how to run locally

- clone the repo `git clone https://github.com/lily-mosquitoes/scinguistics_archive.git`
- start a new virtual env `python3 -m pip venv venv` then source it `source venv/bin/activate`
- move into the repo `cd scinguistics_archive`
- install requirements `python3 -m pip install -r requirements.txt`
- set all of the [config vars](#configuration-variables)
    - remember to start a database service (code uses [postgresql](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-postgresql-on-ubuntu-20-04), change that in `scinguistics_archive/settings.py` if using something else)
- in `catalog/models.py` **comment out** the Lesson recording variable:
...`# recording = models.FileField(blank=True, null=True, upload_to='uploads', storage=BackblazeB2Storage, help_text='Recording link from the CDN (autofilled from CRAIG/GIARC link)')`
- run `python3 manage.py createcachetable`
    - this will fail if the previously mentioned line is not **commented out**
- run `python3 manage.py makemigrations`
- run `python3 manage.py migrate`
- in `catalog/models.py` **uncomment** the Lesson recording variable:
    - `recording = models.FileField(blank=True, null=True, upload_to='uploads', storage=BackblazeB2Storage, help_text='Recording link from the CDN (autofilled from CRAIG/GIARC link)')`
- run `python3 manage.py makemigrations`
- run `python3 manage.py migrate`
- run `python3 manage.py collectstatic`
- run `python3 manage.py createsuperuser`
- run `python3 manage.py runserver`
Now your test server should be accessible from http://127.0.0.1:8000/.

## how to deploy with Heroku

- clone the repo `git clone https://github.com/lily-mosquitoes/scinguistics_archive.git`
- start a new virtual env `python3 -m pip venv venv` then source it `source venv/bin/activate`
- move into the repo `cd scinguistics_archive`
- install requirements `python3 -m pip install -r requirements.txt`
- install the [Heroku CLI](https://devcenter.heroku.com/articles/getting-started-with-python#set-up)
- run `heroku login`
- run `heroku apps:create NAME` where NAME is any name you wish to give the app
- check if postgresql is provisioned by running `heroku addons`
- if not, run `heroku addons:create heroku-postgresql:hobby-dev` (`hoby-dev` is the free tier, [see tiers here](https://elements.heroku.com/addons/heroku-postgresql) and substitute with the desired tier codename)
- `heroku buildpacks:add --index 1 https://github.com/jonathanong/heroku-buildpack-ffmpeg-latest.git`
- set the [config vars](#configuration-variables) with `heroku congif:set VAR_NAME="value"`
    - obs: Heroku automatically sets the `DATABASE_URL` variable
- in `catalog/models.py` **comment out** the Lesson recording variable:
    - `# recording = models.FileField(blank=True, null=True, upload_to='uploads', storage=BackblazeB2Storage, help_text='Recording link from the CDN (autofilled from CRAIG/GIARC link)')`
- run `python3 manage.py makemigrations`
- run `git push heroku main`
- run `heroku run python manage.py createcachetable`
    - this will fail if the previously mentioned line is not **commented out**
- run `heroku run python manage.py migrate`
- in `catalog/models.py` **uncomment** the Lesson recording variable:
    - `recording = models.FileField(blank=True, null=True, upload_to='uploads', storage=BackblazeB2Storage, help_text='Recording link from the CDN (autofilled from CRAIG/GIARC link)')`
- run `python3 manage.py makemigrations`
- run `git push heroku main`
- run `heroku run python manage.py migrate`
- run `heroku run python manage.py createsuperuser`
Now the deployed WebApp should be available at Heroku's provided url, as a shortcut you can run `heroku open`.
Remember to add and commit changes using git (`git add .`, `git commit -m "commit message"`), and re-deploy to Heroku with `git push heroku main`.
It is recommended to schedule [backups for the database](https://devcenter.heroku.com/articles/heroku-postgres-backups).
