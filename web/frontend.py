# This contains our frontend; since it is a bit messy to use the @app.route
# decorator style when using application factories, all of our routes are
# inside blueprints. This is the front-facing blueprint.
#
# You can find out more about blueprints at
# http://flask.pocoo.org/docs/blueprints/

from flask import Blueprint, render_template, flash, redirect, url_for
from flask_nav.elements import View
from markupsafe import escape
from apis.AzureBlobController import app_api
from .forms import SignupForm
from .nav import nav, ExtendedNavbar

frontend = Blueprint('frontend', __name__)
frontend.register_blueprint(app_api)

# We're adding a navbar as well through flask-navbar. In our example, the
# navbar has an usual amount of Link-Elements, more commonly you will have a
# lot more View instances.
nav.register_element('frontend_top', ExtendedNavbar(
    title=View('Azure Blob Upload', '.index'),
    root_class='navbar navbar-inverse',
    items=(
        View('Home', '.index'),
        View('Debug-Info', 'debug.debug_root'),
        # Below will create a Drop down
        # Subgroup(
        #     'Docs',
        #     Link('Flask-Bootstrap', 'http://pythonhosted.org/Flask-Bootstrap'),
        #     Link('Flask-AppConfig', 'https://github.com/mbr/flask-appconfig'),
        #     Link('Flask-Debug', 'https://github.com/mbr/flask-debug'),
        #     Separator(),
        #     Text('Bootstrap'),
        #     Link('Getting started', 'http://getbootstrap.com/getting-started/'),
        #     Link('CSS', 'http://getbootstrap.com/css/'),
        #     Link('Components', 'http://getbootstrap.com/components/'),
        #     Link('Javascript', 'http://getbootstrap.com/javascript/'),
        #     Link('Customize', 'http://getbootstrap.com/customize/'),
        # ),
    ),
    right_items=(
        # Text('Using Flask-Bootstrap {}'.format(FLASK_BOOTSTRAP_VERSION)),
        View('SignUp', '.example_form'),
    )
))


# Our index-page just shows a quick explanation. Check out the template
# "templates/index.html" documentation for more details.
@frontend.route('/')
def index():
    return render_template('index.html')


@frontend.route('/uploader')
def uploader_html():
    return render_template('upload.html')

# Shows a long signup form, demonstrating form rendering.


@frontend.route('/example-form/', methods=('GET', 'POST'))
def example_form():
    form = SignupForm()

    if form.validate_on_submit():
        flash('Hello, {}. You have successfully signed up'
              .format(escape(form.name.data)))
        # In a real application, you may wish to avoid this tedious redirect.
        return redirect(url_for('.index'))

    return render_template('signup.html', form=form)
