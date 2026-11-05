from django.db import transaction
from django.core.exceptions import ValidationError
from .models import LedgerAccount,LedgerTransaction,LedgerEntry,Wallet
def user_account(user): return LedgerAccount.objects.get_or_create(code=f"USER:{user.pk}:CASH",defaults={"owner":user,"kind":"USER"})[0]
def treasury(): return LedgerAccount.objects.get_or_create(code="SYSTEM:VIRTUAL_TREASURY",defaults={"kind":"SYSTEM"})[0]
def ensure_wallet(user):
    wallet,_=Wallet.objects.get_or_create(user=user); user_account(user); treasury(); return wallet
@transaction.atomic
def journal(key,kind,reference,entries):
    if sum(v for _,v in entries)!=0: raise ValidationError("Ledger transaction must balance to zero.")
    tx,created=LedgerTransaction.objects.get_or_create(idempotency_key=key,defaults={"kind":kind,"reference":str(reference)})
    if created: LedgerEntry.objects.bulk_create([LedgerEntry(transaction=tx,account=a,amount_cents=v) for a,v in entries if v])
    return tx
@transaction.atomic
def issue_demo_cash(user,amount,key):
    if not 1<=amount<=100000: raise ValidationError("amount_cents must be 1..100000")
    wallet=Wallet.objects.select_for_update().get(user=user)
    if LedgerTransaction.objects.filter(idempotency_key=key).exists(): return wallet
    journal(key,"FAUCET",user.pk,[(treasury(),-amount),(user_account(user),amount)])
    wallet.available_cents+=amount; wallet.save(update_fields=["available_cents","updated_at"]); return wallet
