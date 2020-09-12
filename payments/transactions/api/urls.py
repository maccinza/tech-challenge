from django.urls import path

from transactions.api.views import (
    RecordTransactionView,
    TransactionsReportView,
)
from transactions.apps import TransactionsConfig

app_name = TransactionsConfig.name

urlpatterns = [
    path("transacao", RecordTransactionView.as_view()),
    path("transacoes/estabelecimento", TransactionsReportView.as_view()),
]
