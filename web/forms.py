from flask_wtf import Form
from wtforms.fields import *
from wtforms.validators import Required, Email
import os


class SignupForm(Form):
    name = TextField(u'Your name', validators=[Required()])
    password = TextField(u'Your favorite password', validators=[Required()])
    email = TextField(u'Your email address', validators=[Email()])
    birthday = DateField(u'Your birthday')

    a_float = FloatField(u'A floating point number')
    a_decimal = DecimalField(u'Another floating point number')
    a_integer = IntegerField(u'An integer')

    now = DateTimeField(u'Current time',
                        description='...for no particular reason')
    sample_file = FileField(u'Your favorite file')
    eula = BooleanField(u'I did not read the terms and conditions',
                        validators=[Required('You must agree to not agree!')])

    submit = SubmitField(u'Signup')


# class FileUpload():

#     def allowed_files(self, file_name):
#         allowed_extensions = ['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif']
#         return '.' in file_name and file_name.rsplit('.', 1)[1].lower() in allowed_extensions

#     def upload(self, file):
#         file_name = file.filename
#         if file_name == '':
#             return 'NULL'

#         elif file_name and self.allowed_files(file_name):
#             secure_file_name = secure_filename(file_name)
#             file.save(os.path.join(
#                 app.config['UPLOAD_FOLDER'], 'Normal Changes Docs\\' + secure_file_name))

#         return str(os.path.join(app.config['UPLOAD_FOLDER'], 'Normal Changes Docs\\' + secure_file_name))
