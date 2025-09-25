from django.shortcuts import render
from django.views.generic import CreateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Transaction
from .forms import DepositForm, WithdrawForm, LoanRequestForm
from django.contrib import messages
from .constants import Deposite, Withdraw, Loan, Loan_Paid
from django.http import HttpResponse
from datetime import datetime
from django.db.models import Sum
from django.views import View
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template.loader import render_to_string

# Create your views here.

def send_transactions_email(sumject, user, amount, to_user, template):
  message = render_to_string(template, {
    'user' : user,
    'amount' : amount,
  })
  send_email = EmailMultiAlternatives(sumject, '', to=[to_user])
  send_email.attach_alternative(message, "text/html")
  send_email.send()

class TransactionCreateMixin(LoginRequiredMixin, CreateView):
  template_name = 'transactions/transaction_form.html'
  model = Transaction
  title = ''
  success_url = reverse_lazy('transaction_report')

  def get_form_kwargs(self):
    kwargs = super().get_form_kwargs()
    kwargs.update({
      'account' : self.request.user.account,
    })
    return kwargs

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context.update({
      'title' : self.title
    })
    return context


class DepositMoneyView(TransactionCreateMixin):
  form_class = DepositForm
  title = 'Deposit'

  def get_initial(self):
    initial = {'transaction_type': Deposite}
    return initial
  
  def form_valid(self, form):
    amount = form.cleaned_data.get('amount')
    account = self.request.user.account
    account.balance += amount
    account.save(
      update_fields = ['balance']
    )

    messages.success(self.request, f'{amount}$ was deposited to account successfully')

    send_transactions_email("Deposite Message", self.request.user, amount, self.request.user.email, 'transactions/deposite_email.html')

    return super().form_valid(form)
  

class WithdrawMoneyView(TransactionCreateMixin):
  form_class = WithdrawForm
  title = 'Withdrow Money'

  def get_initial(self):
    initial = {'transaction_type': Withdraw}
    return initial
  
  def form_valid(self, form):
    amount = form.cleaned_data.get('amount')
    account = self.request.user.account
    account.balance -= amount
    account.save(
      update_fields = ['balance']
    )

    messages.success(self.request, f'{amount}$ was Withdrawed successfully')

    send_transactions_email("Withdraw Message", self.request.user, amount, self.request.user.email, 'transactions/withdraw_email.html')

    return super().form_valid(form)
  

class LoanRequestMoneyView(TransactionCreateMixin):
  form_class = LoanRequestForm
  title = 'Loan for request'

  def get_initial(self):
    initial = {'transaction_type': Loan}
    return initial
  
  def form_valid(self, form):
    amount = form.cleaned_data.get('amount')
    current_loan_count = Transaction.objects.filter(account = self.request.user.account, transaction_type=3, loan_approve=True).count()

    if current_loan_count > 3:
      return HttpResponse('you have cross your limit')

    messages.success(self.request, f'loan request has been successfully sent to admin')

    send_transactions_email("Loan Request", self.request.user, amount, self.request.user.email, 'transactions/loan_request_email.html')

    return super().form_valid(form)
  


class TransactionReportView(LoginRequiredMixin, ListView):
  template_name = 'transactions/transaction_report.html'
  model = Transaction
  balance = 0

  def get_queryset(self):
    queryset = super().get_queryset().filter(
      account = self.request.user.account
    )

    start_date_str = self.request.GET.get('start_date')
    end_date_str = self.request.GET.get('end_date')

    if start_date_str and end_date_str:
      start_date = datetime.strptime(start_date_str, "%y-%m-%d").date()
      end_date = datetime.strptime(end_date_str, "%y-%m-%d").date()
      queryset = queryset.filter(timestamp__gte=start_date, timestamp__lte=end_date)

      self.balance = Transaction.objects.filter(timestamp__gte=start_date, timestamp__lte=end_date).aggregate(Sum('amount'))['amount__sum']
    else:
      self.balance = self.request.user.account.balance

    return queryset.distinct()
    
  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context.update({
      'account' : self.request.user.account
    })
    return context
  

class PayloanView(LoginRequiredMixin, View):
  def get(self, request, loan_id):
    loan = get_object_or_404(Transaction, id=loan_id)

    if loan.loan_approve:
      user_account = loan.account
      if loan.amount < user_account.balance:
        user_account.balance -= loan.amount
        loan.balance_after_transaction = user_account.balance
        user_account.save()
        loan.transaction_type = Loan_Paid
        loan.save()
        return redirect()
      else:
        messages.error(self.request, f'your loan is Greater than available balance')
        return redirect()
      

class LoanListView(LoginRequiredMixin, ListView):
  model = Transaction
  template_name = 'transactions/loan_request.html'
  context_object_name = 'loans'

  def get_queryset(self):
    user_account = self.request.user.account
    queryset = Transaction.objects.filter(account = user_account, transaction_type = Loan)
    return queryset