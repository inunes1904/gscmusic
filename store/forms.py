from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms.models import ModelForm

from store.models import Evaluation



class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'password1', 'password2']
class EvaluationForm(ModelForm):
    class Meta:
        model = Evaluation
        fields = ['comment', 'product_evaluation']
        exclude = ['product','customer']
    
    def __init__(self, *args, **kwargs):
        super(EvaluationForm, self).__init__(*args, **kwargs)
        self.fields['comment'].widget.attrs.update({'style': 'width:800px; height:55px; ', 'placeholder':'Write your product review'})
        self.fields['product_evaluation'].widget.attrs.update({'class': 'inline-block'})
