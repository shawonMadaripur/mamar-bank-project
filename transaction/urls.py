from django.urls import path
from .views import DepositMoneyView, WithdrawMoneyView, LoanRequestMoneyView, TransactionReportView, PayloanView, LoanListView

urlpatterns = [
    path('deposit/', DepositMoneyView.as_view(), name = 'deposite_money'),
    path('withdraw/', WithdrawMoneyView.as_view(), name = 'withdraw_money'),
    path('report/', TransactionReportView.as_view(), name = 'transaction_report'),
    path('loan_request/', LoanRequestMoneyView.as_view(), name = 'loan_request'),
    path('loans/', LoanListView.as_view(), name = 'loan_list'),
    path('pay_loan/<int:loan_id>/', PayloanView.as_view(), name = 'pay_loan'),
]
