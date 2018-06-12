from .fields import FieldLogin
from .messages import MessageLogin
from .forms import LoginForm
from django.contrib.auth import login, logout

class LoginFormMiddleware(object):
    def process_request(self, request):
        if request.method == 'POST' and ( 'base-account' in request.POST)  and request.POST['base-account'] == 'Login':
            form = LoginForm(data=request.POST, prefix="login")
            form.fields['username'].label = FieldLogin.USERNAME
            form.fields['username'].widget.attrs['class'] = "login__form--input login__form--input-error"
            form.fields['password'].label = FieldLogin.PASSWORD
            form.fields['password'].widget.attrs['class'] = "login__form--input login__form--input-error"
            form.fields['message'].widget.attrs['class'] = "form-control"
            if form.errors:
                form.fields['message'].help_text = MessageLogin.INCORRECT_CREDENTIALS
            else: 
                form.fields['message'].help_text = ""
            
            if form.is_valid():
                login(request, form.get_user())
            request.method = 'GET' 
        else:
            form = LoginForm(request, prefix="login")
            form.fields['username'].label = FieldLogin.USERNAME
            form.fields['username'].widget.attrs['class'] = "login__form--input"
            form.fields['password'].label = FieldLogin.PASSWORD
            form.fields['password'].widget.attrs['class'] = "login__form--input"
            form.fields['message'].help_text = ""


        request.login_form = form


class LogoutFormMiddleware(object):
    def process_request(self, request):
        if request.method == 'POST' and ('base-account' in request.POST) and request.POST['base-account'] == 'Logout':
            logout(request)
            request.method = 'GET'
