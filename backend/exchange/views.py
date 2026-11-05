from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from rest_framework import generics,permissions,status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from .models import Market,Order,Trade,Wallet,Position
from .serializers import RegisterSerializer,MarketSerializer,OrderSerializer,TradeSerializer,WalletSerializer,PositionSerializer,ChallengeSerializer
from .ledger import ensure_wallet,issue_demo_cash
from .services import submit_order,cancel_order,order_book,resolve_market,create_challenge,decide_challenge,market_maker_tick
User=get_user_model()
class RegisterView(generics.CreateAPIView):
    serializer_class=RegisterSerializer; permission_classes=[permissions.AllowAny]
class HealthView(APIView):
    permission_classes=[permissions.AllowAny]
    def get(self,request): return Response({"status":"ok","service":"playsim"})
class MarketListView(generics.ListAPIView):
    serializer_class=MarketSerializer; permission_classes=[permissions.AllowAny]
    def get_queryset(self): return Market.objects.exclude(status="DRAFT").order_by("-created_at")
class MarketDetailView(generics.RetrieveAPIView):
    queryset=Market.objects.all(); serializer_class=MarketSerializer; permission_classes=[permissions.AllowAny]
class OrderCreateView(APIView):
    def post(self,request):
        o,f=submit_order(request.user,request.data,request.headers.get("Idempotency-Key") or request.data.get("idempotency_key")); return Response({"order":OrderSerializer(o).data,"fills":f},status=201)
class MyOrdersView(generics.ListAPIView):
    serializer_class=OrderSerializer
    def get_queryset(self): return Order.objects.filter(user=self.request.user).order_by("-created_at")
class CancelOrderView(APIView):
    def delete(self,request,order_id): return Response(OrderSerializer(cancel_order(request.user,order_id)).data)
class BookView(APIView):
    permission_classes=[permissions.AllowAny]
    def get(self,request,market_id):
        m=Market.objects.get(pk=market_id); out=request.query_params.get("outcome","YES")
        if out not in ("YES","NO"): raise ValidationError("outcome must be YES or NO")
        return Response(order_book(m,out))
class TradesView(generics.ListAPIView):
    serializer_class=TradeSerializer; permission_classes=[permissions.AllowAny]
    def get_queryset(self): return Trade.objects.filter(market_id=self.kwargs["market_id"]).order_by("-sequence")[:100]
class WalletView(APIView):
    def get(self,request): return Response(WalletSerializer(Wallet.objects.get_or_create(user=request.user)[0]).data)
class PortfolioView(APIView):
    def get(self,request):
        p=Position.objects.filter(user=request.user).select_related("market")
        return Response({"positions":PositionSerializer(p,many=True).data,"open_orders":OrderSerializer(Order.objects.filter(user=request.user,status__in=["OPEN","PARTIAL"]),many=True).data})
class FaucetView(APIView):
    def post(self,request):
        if not request.user.is_staff: return Response({"detail":"Staff only"},status=403)
        target=User.objects.get(pk=request.data.get("user_id",request.user.pk)); ensure_wallet(target)
        with transaction.atomic():
            Wallet.objects.select_for_update().get(user=target)
            w=issue_demo_cash(target,int(request.data.get("amount_cents",10000)),f"faucet:{target.pk}:{request.data.get('key','demo')}")
        return Response(WalletSerializer(w).data)
class ResolveView(APIView):
    def post(self,request,market_id): return Response(MarketSerializer(resolve_market(market_id,request.user,request.data.get("outcome"))).data)
class ChallengeView(APIView):
    def post(self,request,market_id):
        s=ChallengeSerializer(data={**request.data,"market":market_id}); s.is_valid(raise_exception=True)
        c=create_challenge(market_id,request.user,s.validated_data["reason"],s.validated_data.get("evidence_url","")); return Response(ChallengeSerializer(c).data,status=201)
class ChallengeDecisionView(APIView):
    def post(self,request,challenge_id): return Response(ChallengeSerializer(decide_challenge(challenge_id,request.user,request.data.get("decision"),request.data.get("note",""))).data)
class MarketMakerView(APIView):
    def post(self,request,market_id): return Response(market_maker_tick(market_id,request.user,int(request.data.get("fair_price",50)),int(request.data.get("spread",4)),int(request.data.get("quantity",10))))
class CloseSweepView(APIView):
    def post(self,request):
        if not request.user.is_staff: return Response({"detail":"Staff only"},status=403)
        n=Market.objects.filter(status="OPEN",closes_at__lte=timezone.now()).update(status="CLOSED"); return Response({"closed_markets":n})
