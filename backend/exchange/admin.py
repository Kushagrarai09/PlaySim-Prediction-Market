from django.contrib import admin
from .models import Market,Wallet,Order,Trade,Position,LedgerAccount,LedgerTransaction,LedgerEntry,Settlement,MarketChallenge,AuditLog
@admin.register(Market)
class MarketAdmin(admin.ModelAdmin):
    list_display=("id","question","status","closes_at","resolves_at","outcome"); list_filter=("status",); search_fields=("question","resolution_rules")
for model in [Wallet,Order,Trade,Position,LedgerAccount,LedgerTransaction,LedgerEntry,Settlement,MarketChallenge,AuditLog]: admin.site.register(model)
