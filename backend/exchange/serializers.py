from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Market,Order,Trade,Wallet,Position,MarketChallenge
User=get_user_model()
class RegisterSerializer(serializers.ModelSerializer):
    password=serializers.CharField(write_only=True,min_length=10)
    class Meta: model=User; fields=("id","username","password")
    def create(self,validated_data):
        user=User.objects.create_user(**validated_data)
        from .ledger import ensure_wallet
        ensure_wallet(user); return user
class MarketSerializer(serializers.ModelSerializer):
    class Meta:
        model=Market; fields=("id","question","description","resolution_rules","resolution_source_url","closes_at","resolves_at","dispute_window_minutes","status","outcome","created_at","sequence"); read_only_fields=("status","outcome","created_at","sequence")
class OrderSerializer(serializers.ModelSerializer):
    remaining=serializers.IntegerField(read_only=True)
    class Meta:
        model=Order; fields=("id","market","side","outcome","kind","price_ticks","quantity","filled_quantity","remaining","reserved_cash_cents","reserved_shares","status","created_at"); read_only_fields=("id","filled_quantity","remaining","reserved_cash_cents","reserved_shares","status","created_at")
class TradeSerializer(serializers.ModelSerializer):
    class Meta: model=Trade; fields=("id","outcome","price_ticks","quantity","sequence","created_at")
class WalletSerializer(serializers.ModelSerializer):
    class Meta: model=Wallet; fields=("available_cents","reserved_cents")
class PositionSerializer(serializers.ModelSerializer):
    market_question=serializers.CharField(source="market.question",read_only=True)
    class Meta: model=Position; fields=("id","market","market_question","outcome","quantity","cost_basis_cents","realized_pnl_cents")
class ChallengeSerializer(serializers.ModelSerializer):
    class Meta: model=MarketChallenge; fields=("id","market","reason","evidence_url","status","decision_note","created_at"); read_only_fields=("id","status","decision_note","created_at")
