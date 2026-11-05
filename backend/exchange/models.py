import uuid
from django.conf import settings
from django.db import models
class Market(models.Model):
    class Status(models.TextChoices):
        DRAFT="DRAFT"; OPEN="OPEN"; CLOSED="CLOSED"; DISPUTED="DISPUTED"; RESOLVED="RESOLVED"; VOID="VOID"; SUSPENDED="SUSPENDED"
    question=models.CharField(max_length=240); description=models.TextField(blank=True); resolution_rules=models.TextField(); resolution_source_url=models.URLField()
    closes_at=models.DateTimeField(); resolves_at=models.DateTimeField(); dispute_window_minutes=models.PositiveIntegerField(default=30)
    status=models.CharField(max_length=12,choices=Status.choices,default="DRAFT"); outcome=models.CharField(max_length=4,blank=True)
    created_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name="created_markets"); created_at=models.DateTimeField(auto_now_add=True); sequence=models.PositiveBigIntegerField(default=0)
    def __str__(self): return self.question
class Wallet(models.Model):
    user=models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="wallet"); available_cents=models.BigIntegerField(default=0); reserved_cents=models.BigIntegerField(default=0); updated_at=models.DateTimeField(auto_now=True)
class LedgerAccount(models.Model):
    code=models.CharField(max_length=100,unique=True); owner=models.ForeignKey(settings.AUTH_USER_MODEL,null=True,blank=True,on_delete=models.PROTECT); kind=models.CharField(max_length=20,default="SYSTEM")
class LedgerTransaction(models.Model):
    idempotency_key=models.CharField(max_length=180,unique=True); kind=models.CharField(max_length=40); reference=models.CharField(max_length=160,blank=True); created_at=models.DateTimeField(auto_now_add=True)
class LedgerEntry(models.Model):
    transaction=models.ForeignKey(LedgerTransaction,on_delete=models.PROTECT,related_name="entries"); account=models.ForeignKey(LedgerAccount,on_delete=models.PROTECT,related_name="entries"); amount_cents=models.BigIntegerField(); created_at=models.DateTimeField(auto_now_add=True)
class Order(models.Model):
    class Side(models.TextChoices): BUY="BUY"; SELL="SELL"
    class Outcome(models.TextChoices): YES="YES"; NO="NO"
    class Kind(models.TextChoices): LIMIT="LIMIT"; MARKET="MARKET"
    class Status(models.TextChoices): OPEN="OPEN"; PARTIAL="PARTIAL"; FILLED="FILLED"; CANCELLED="CANCELLED"
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False); market=models.ForeignKey(Market,on_delete=models.PROTECT,related_name="orders"); user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name="orders")
    side=models.CharField(max_length=4,choices=Side.choices); outcome=models.CharField(max_length=3,choices=Outcome.choices); kind=models.CharField(max_length=6,choices=Kind.choices,default="LIMIT")
    price_ticks=models.PositiveSmallIntegerField(); quantity=models.PositiveIntegerField(); filled_quantity=models.PositiveIntegerField(default=0); reserved_cash_cents=models.BigIntegerField(default=0); reserved_shares=models.PositiveIntegerField(default=0)
    status=models.CharField(max_length=10,choices=Status.choices,default="OPEN"); idempotency_key=models.CharField(max_length=160); request_hash=models.CharField(max_length=64,default=""); sequence=models.PositiveBigIntegerField(); created_at=models.DateTimeField(auto_now_add=True)
    class Meta:
        constraints=[models.UniqueConstraint(fields=["user","idempotency_key"],name="unique_user_order_idem"),models.CheckConstraint(condition=models.Q(price_ticks__gte=1,price_ticks__lte=99),name="order_price_range"),models.CheckConstraint(condition=models.Q(quantity__gte=1),name="order_qty_positive")]
        indexes=[models.Index(fields=["market","outcome","side","status","price_ticks","sequence"])]
    @property
    def remaining(self): return self.quantity-self.filled_quantity
class Trade(models.Model):
    market=models.ForeignKey(Market,on_delete=models.PROTECT,related_name="trades"); buy_order=models.ForeignKey(Order,on_delete=models.PROTECT,related_name="buy_trades"); sell_order=models.ForeignKey(Order,on_delete=models.PROTECT,related_name="sell_trades"); outcome=models.CharField(max_length=3); price_ticks=models.PositiveSmallIntegerField(); quantity=models.PositiveIntegerField(); sequence=models.PositiveBigIntegerField(); created_at=models.DateTimeField(auto_now_add=True)
    class Meta: ordering=["sequence"]
class Position(models.Model):
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE); market=models.ForeignKey(Market,on_delete=models.PROTECT); outcome=models.CharField(max_length=3); quantity=models.BigIntegerField(default=0); cost_basis_cents=models.BigIntegerField(default=0); realized_pnl_cents=models.BigIntegerField(default=0)
    class Meta: constraints=[models.UniqueConstraint(fields=["user","market","outcome"],name="unique_position")]
class Settlement(models.Model):
    market=models.ForeignKey(Market,on_delete=models.PROTECT); user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT); idempotency_key=models.CharField(max_length=180,unique=True); amount_cents=models.BigIntegerField(default=0); created_at=models.DateTimeField(auto_now_add=True)
class MarketChallenge(models.Model):
    market=models.ForeignKey(Market,on_delete=models.PROTECT,related_name="challenges"); created_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT); reason=models.TextField(); evidence_url=models.URLField(blank=True); status=models.CharField(max_length=12,default="PENDING"); decision_note=models.TextField(blank=True); created_at=models.DateTimeField(auto_now_add=True)
class AuditLog(models.Model):
    actor=models.ForeignKey(settings.AUTH_USER_MODEL,null=True,blank=True,on_delete=models.SET_NULL); market=models.ForeignKey(Market,null=True,blank=True,on_delete=models.SET_NULL); action=models.CharField(max_length=60); entity_type=models.CharField(max_length=60); entity_id=models.CharField(max_length=160); details=models.JSONField(default=dict); created_at=models.DateTimeField(auto_now_add=True)
