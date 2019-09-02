from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Optional
from wtforms.fields.html5 import DateField


class filter(FlaskForm):
    #host_name = StringField("Host name", validators=[DataRequired()])
    host_name = StringField("Host name")
    key = StringField("Item key", validators=[DataRequired()])

    date_from = DateField("Date from", format='%m/%d/%Y')
    date_till = DateField("Date till", format='%m/%d/%Y', validators=[Optional()])
    srch = SubmitField("Find")
