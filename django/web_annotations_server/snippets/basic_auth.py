#From http://www.djangosnippets.org/snippets/56/

from django.conf import settings
from django.http import HttpResponse

from django.contrib.auth import authenticate, login, logout

def basic_challenge(realm = None):
    if realm is None:
        realm = getattr(settings, 'WWW_AUTHENTICATION_REALM', _('Restricted Access'))

    # TODO: Make a nice template for a 401 message?
    response =  HttpResponse(_('Authorization Required'), mimetype="text/plain")
    response['WWW-Authenticate'] = 'Basic realm="%s"' % (realm)
    response.status_code = 401
    return response

def basic_authenticate(authentication):
    # Taken from paste.auth
    (authmeth, auth) = authentication.split(' ',1)
    if 'basic' != authmeth.lower():
        return None
    auth = auth.strip().decode('base64')
    username, password = auth.split(':',1)
    return authenticate(username = username, password = password)

class BasicAuthenticationMiddleware:
    def process_request(self, request):
        if not getattr(settings, 'BASIC_WWW_AUTHENTICATION', False):
            return None
        if not request.META.has_key('HTTP_AUTHORIZATION'):
            # If the user out of the session as well
            #logout(request)
            return None
        user =  basic_authenticate(request.META['HTTP_AUTHORIZATION'])
        if user is None:
            return None
        else:
            login(request, user)
