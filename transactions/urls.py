from django.urls import path
from . import views


urlpatterns = [
    path("get_wallet_details", views.GetWalletDetails.as_view(), name="get_wallet_details"),
    path("fund_wallet", views.FundWallet.as_view(), name="fund_wallet"),
    path("send_money", views.SendMoney.as_view(), name="send_money"),
]
