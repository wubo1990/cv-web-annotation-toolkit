from django.forms import ModelForm
from mturk.models import Payment
import readonly_forms

# Create the form class.
class PaymentForm(ModelForm):
     class Meta:
         model = Payment


class SimplePaymentForm(readonly_forms.ReadonlyModelForm):
    class Meta:
        model = Payment
        exclude = ('ref', 'created_by','state','worker','work_product')


