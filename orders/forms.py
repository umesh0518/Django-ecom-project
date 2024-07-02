


from django import forms

from .models import Order


class OrderForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        placeholders = {
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'phone': 'Phone Number',
            'email': 'Email Address',
            'address': 'Address',
            'country': 'Country',
            'state': 'State',
            'city': 'City',
        }
        for field_name in self.fields:
            self.fields[field_name].widget.attrs['placeholder'] = placeholders.get(field_name, '')
    
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'phone', 'email', 'address', 'country', 'state', 'city']
