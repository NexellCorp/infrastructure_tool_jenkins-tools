from settings import *

MEDIA_URL = '/static/'
USE_OWN_COMBO = True

DATABASES['default']['NAME'] = '/var/lib/linaro-abs-frontend/session.db'

FRONTEND_JENKINS_USER = 'linaro-android-build-frontend@linaro.org'
FRONTEND_JENKINS_PASSWORD = open('/var/lib/linaro-abs-frontend/jenkins-password').read().strip()

{% if frontend_auth == "openid" %}
LOGIN_URL = '/openid/login/'
{% elif frontend_auth == "crowd" %}
AUTH_CROWD_APPLICATION_USER = '{{crowd_user}}'
AUTH_CROWD_APPLICATION_PASSWORD = '{{crowd_passwd}}'
{% endif %}

SECRET_KEY = "{{ lookup('password', cred_store + '/frontend/django_secret_key') }}"
