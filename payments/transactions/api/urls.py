from django.urls import path

from transactions.api.views import RecordTransactionView
from transactions.apps import TransactionsConfig

app_name = TransactionsConfig.name

urlpatterns = [
    path("transacao/", RecordTransactionView.as_view()),
]
