from django.contrib import admin
from . models import Ticket, Contrat, TicketStatus, TicketContrat, Admin
from . models import Produit, TicketType, Translate, Entity, Log, LogType
from . models import ArboLink, Marque, SwapEntity, Discussion

# Register your models here.
admin.site.register(Ticket)
admin.site.register(Contrat)
admin.site.register(TicketStatus)
admin.site.register(TicketContrat)
admin.site.register(Admin)
admin.site.register(Produit)
admin.site.register(TicketType)
admin.site.register(Translate)
admin.site.register(Entity)
admin.site.register(Log)
admin.site.register(LogType)
admin.site.register(ArboLink)
admin.site.register(Marque)
admin.site.register(SwapEntity)
admin.site.register(Discussion)
