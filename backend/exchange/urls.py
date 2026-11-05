from django.urls import path
from .views import *
urlpatterns=[
 path("markets/",MarketListView.as_view()),path("markets/<int:pk>/",MarketDetailView.as_view()),
 path("markets/<int:market_id>/book/",BookView.as_view()),path("markets/<int:market_id>/trades/",TradesView.as_view()),
 path("markets/<int:market_id>/resolve/",ResolveView.as_view()),path("markets/<int:market_id>/challenge/",ChallengeView.as_view()),
 path("challenges/<int:challenge_id>/decision/",ChallengeDecisionView.as_view()),path("orders/",OrderCreateView.as_view()),
 path("orders/my/",MyOrdersView.as_view()),path("orders/<uuid:order_id>/",CancelOrderView.as_view()),
 path("wallet/",WalletView.as_view()),path("portfolio/",PortfolioView.as_view()),path("admin/faucet/",FaucetView.as_view()),
 path("admin/close-markets/",CloseSweepView.as_view()),path("market-maker/<int:market_id>/tick/",MarketMakerView.as_view()),
]
