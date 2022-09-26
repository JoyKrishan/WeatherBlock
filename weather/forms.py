from django import forms
from datetime import date, timedelta
from django.core.exceptions import ValidationError

class DateInput(forms.DateInput):
    input_type= 'date'

def customDateValidation(value):
    today = date.today()
    date_thirty_days_ago = today - timedelta(days=30)
    if value > today:
        raise ValidationError('Date cannot be Future')
    elif value < date_thirty_days_ago:
        raise ValidationError('Date cannot be from 30 days ago')

class DateForm(forms.Form):
    date_field = forms.DateField(label='Date',widget=DateInput, validators=[customDateValidation],
                                error_messages= {
                                    'required': "Date is required"
                                })