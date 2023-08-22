#  Copyright (c) 2023 Andrii Malchyk, All rights reserved.
from flask_wtf import FlaskForm
from wtforms import SubmitField, SearchField
from wtforms.validators import DataRequired


class SearchForm(FlaskForm):
    search = SearchField(label="Search", validators=[DataRequired()], description="Search")
    submit = SubmitField("Search")
