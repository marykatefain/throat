""" User-related forms """
from flask import request, redirect, url_for
from urllib.parse import urlparse, urljoin
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextField, TextAreaField
from wtforms import BooleanField, HiddenField, SelectField
from wtforms.validators import DataRequired, Length, Email, Required, EqualTo
from wtforms.validators import Optional, Regexp
from wtforms.fields.html5 import EmailField
from flask_babel import lazy_gettext as _l


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


def get_redirect_target():
    for target in request.args.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return target


class RedirectForm(FlaskForm):
    next = HiddenField()

    def __init__(self, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)
        if not self.next.data:
            self.next.data = get_redirect_target() or ''

    def redirect(self, endpoint='index', **values):
        if is_safe_url(self.next.data):
            return redirect(self.next.data)
        target = get_redirect_target()
        return redirect(target or url_for(endpoint, **values))


class LoginForm(RedirectForm):
    """ Login form. """
    username = StringField(_l('Username'),
                           validators=[DataRequired(), Length(max=32)])
    password = PasswordField(_l('Password'), validators=[DataRequired(),
                                                     Length(min=7, max=256)])
    remember = BooleanField(_l('Remember me'))


class OptionalIfFieldIsEmpty(Optional):
    """ A custom field validator. """
    def __init__(self, field_name, *args, **kwargs):
        self.field_name = field_name
        super(OptionalIfFieldIsEmpty, self).__init__(*args, **kwargs)

    def __call__(self, form, field):
        other_field = form._fields.get(self.field_name)
        if other_field is None:
            raise Exception('no field named "{0}" in form'
                            .format(self.field_name))
        if other_field.data == '':
            super(OptionalIfFieldIsEmpty, self).__call__(form, field)


class RegistrationForm(FlaskForm):
    """ Registration form. """
    username = TextField(_l('Username'), [Length(min=2, max=32), Regexp(r'[a-zA-Z0-9_-]+')])
    email = EmailField(_l('Email Address (optional)'), validators=[OptionalIfFieldIsEmpty('email'), Email(_l("Invalid email address."))])
    password = PasswordField(_l('Password'), [
        Required(),
        EqualTo('confirm', message=_l('Passwords must match')),
        Length(min=7, max=256)
    ])
    confirm = PasswordField(_l('Repeat Password'))
    invitecode = TextField(_l('Invite Code'))
    accept_tos = BooleanField(_l('I accept the TOS'), [Required()])
    captcha = TextField(_l('Captcha'))
    ctok = HiddenField()
    securityanswer = TextField(_l('Security question'))


class ChangePasswordForm(FlaskForm):
    password = PasswordField(_l('New password'), [
        Required(),
        EqualTo('confirm', message=_l('Passwords must match')),
        Length(min=7, max=256),
    ])
    confirm = PasswordField(_l('Repeat Password'), [Required()])

    oldpassword = PasswordField(_l('Your current password'), [
        Required(),
        Length(min=7, max=256)
    ])


class DeleteAccountForm(FlaskForm):
    password = PasswordField(_l('Your password'), [
        Required(),
        Length(min=7, max=256),
    ])
    consent = TextField(_l("Type 'YES' here"), [Required(), Length(max=10)])


class EditUserForm(FlaskForm):
    """ Edit User info form. """
    # username = TextField('Username', [Length(min=2, max=32)])
    email = EmailField(_l('Email Address (optional)'),
                       validators=[OptionalIfFieldIsEmpty('email'),
                                   Email(_l("Invalid email address."))])
    disable_sub_style = BooleanField(_l('Disable custom sub styles'))
    show_nsfw = BooleanField(_l('Show NSFW content'))

    experimental = BooleanField(_l('Enable experimental features'))
    noscroll = BooleanField(_l('Disable infinite scroll'))
    nochat = BooleanField(_l('Disable chat'))

    subtheme = TextField(_l("Global stylesheet (select a sub)"))

    language = SelectField(_l('Language'), validate_choice=False)


class CreateUserMessageForm(FlaskForm):
    """ CreateUserMessage form. """
    to = TextField(_l('to'), [Length(min=2, max=32), Regexp(r'[a-zA-Z0-9_-]+')])
    subject = StringField(_l('subject'),
                          validators=[DataRequired(), Length(min=1, max=400)])

    content = TextAreaField(_l('message'),
                            validators=[DataRequired(),
                                        Length(min=1, max=16384)])


class PasswordRecoveryForm(FlaskForm):
    """ the 'forgot your password?' form """
    email = EmailField(_l('Email Address'),
                       validators=[Email(_l("Invalid email address."))])
    captcha = TextField(_l('Captcha'))
    ctok = HiddenField()


class PasswordResetForm(FlaskForm):
    """ the 'forgot your password?' form """
    user = HiddenField()
    key = HiddenField()
    password = PasswordField(_l('Password'), [
        Required(),
        EqualTo('confirm', message=_l('Passwords must match')),
        Length(min=7, max=256)
    ])
    confirm = PasswordField(_l('Repeat Password'))

class LogOutForm(FlaskForm):
    """ Logout form. This form has no fields.
        We only use it for the CSRF stuff"""
    pass
