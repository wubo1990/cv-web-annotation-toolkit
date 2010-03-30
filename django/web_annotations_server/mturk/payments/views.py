from django.shortcuts import render_to_response,get_object_or_404 
from django.http import HttpResponse,Http404,HttpResponseRedirect
from django.contrib.auth.decorators import login_required,permission_required

from boto.mturk.price import Price

from forms import *
import mturk.views
from mturk.models import *

def main(request):
    return render_to_response('mturk/payments/main.html',{'user':request.user});

@permission_required('payment.pay_bonus')
def create_interactive(request):
    if request.method == 'POST':
        form = PaymentForm(request.POST, request.FILES)
        if form.is_valid():
            payment = form.save()
            return render_to_response('mturk/payments/create_done.html', {'form': form,'user':request.user,'payment':payment})
    else:
        form = PaymentForm()

    return render_to_response('mturk/payments/create.html', {'form': form,'user':request.user})


def make_payment(payment):
    conn = mturk.views.get_mt_connection(payment.work_product.session)
    grant_bonus_rs=conn.grant_bonus(payment.worker.worker,payment.work_product.assignment_id,Price(payment.amount),payment.note)
    if grant_bonus_rs.status == True:
        payment.state=4;
        success=True
    else:
        payment.state=5;
        payment.ref=str(rs);
        success=False
    payment.save()
    return success

@login_required
def make_payments(request,queryset):
    total=0;
    n_ok=0;
    n_failed=0;
    n_skipped=0;
    for payment in queryset:
        if payment.state==3:
            success=make_payment(payment)
            if success:
                total += payment.amount;
                n_ok+=1;
            else:
                n_failed+=1;
        else:
            n_skipped+=1
    return render_to_response('mturk/payments/payments_made.html', {'queryset': queryset,'total':total,'n_ok':n_ok,'n_failed':n_failed,'n_skipped':n_skipped})


@permission_required('payment.pay_bonus')
def create_simple(request,work_product_id):
    work_product = get_object_or_404(WorkProduct,id=work_product_id)

    if request.method == 'POST':
        form = SimplePaymentForm(request.POST, request.FILES)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.created_by = request.user;
            payment.work_product = work_product;
            payment.worker = Worker.objects.get(session=None,worker=work_product.worker);
            payment.ref = "";
            payment.state = 3;
            payment.save();
            return render_to_response('mturk/payments/create_done.html', {'form': form,'user':request.user,'payment':payment})
    else:
        form = SimplePaymentForm()

    return render_to_response('mturk/payments/create_minimal.html', {'form': form,'user':request.user})

@permission_required('payment.pay_bonus')
def create_simple2(request,worker,session_code):
    session=get_object_or_404(Session,code=session_code);
    work_product = WorkProduct.objects.filter(session=session,worker=worker)[0]

    if request.method == 'POST':
        form = SimplePaymentForm(request.POST, request.FILES)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.created_by = request.user;
            payment.work_product = work_product;
            payment.worker = Worker.objects.get(session=None,worker=work_product.worker);
            payment.ref = "";
            payment.state = 3;
            payment.save();
            return render_to_response('mturk/payments/create_done.html', {'form': form,'user':request.user,'payment':payment})
    else:
        form = SimplePaymentForm()

    return render_to_response('mturk/payments/create_minimal.html', {'form': form,'user':request.user})
