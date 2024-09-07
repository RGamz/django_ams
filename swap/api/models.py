from django.db import models
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from datetime import datetime
from typing import Optional

from api.managers import TicketManager

EXCLUDED_LOG_TYPES = [1, 2, 5, 6, 8, 9, 12, 15, 20, 21, 22, 23, 24, 25, 26, 27,
                      28, 29, 32, 36, 41, 42, 43, 45, 48, 49, 50, 51, 52, 53,
                      54, 55, 56, 57, 59, 64, 65, 66, 67, 68, 70, 71, 72, 73,
                      74, 75, 77, 81, 82, 83, 84, 85, 87, 88, 89, 90, 91, 92,
                      93, 94, 95, 96, 97, 101, 102, 103, 104, 107, 110, 113,
                      118, 119]


class Contrat(models.Model):
    id = models.IntegerField(primary_key=True)
    nom = models.CharField(max_length=50)

    class Meta:
        db_table = 'contrats'
        managed = False  # No migrations for this model


class TicketStatus(models.Model):
    id = models.IntegerField(primary_key=True)
    tr_nom = models.OneToOneField('Translate', db_column='tr_nom',on_delete=models.CASCADE,)

    class Meta:
        db_table = 'support_tickets_statuts'
        managed = False  # No migrations for this model


class TicketContrat(models.Model):
    ticket = models.OneToOneField('Ticket', related_name='ticketcontrat', db_column='id_ticket', on_delete=models.CASCADE, blank=True, null=True)
    contrat = models.ForeignKey('Contrat', related_name='ticketcontrat', db_column='id_contrat', on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        db_table = 'support_tickets_contrat'
        managed = False  # No migrations for this model


class Admin(models.Model):
    id = models.IntegerField(primary_key=True)
    pseudo = models.CharField(max_length=100)
    id_entite = models.IntegerField(null=False, unique=True)

    class Meta:
        db_table = 'admins'
        managed = False  # No migrations for this model


class Produit(models.Model):
    id = models.IntegerField(primary_key=True)
    marque = models.ForeignKey('Marque', db_column='id_marque', on_delete=models.CASCADE)
    ref = models.CharField(max_length=50)
    poids = models.FloatField()
    code_barres = models.CharField(max_length=13)
    tr_nom = models.IntegerField()
    dpr = models.FloatField()

    class Meta:
        db_table = 'produits'
        managed = False  # No migrations for this model


class Ticket(models.Model):
    id = models.IntegerField(primary_key=True)
    id_discussion = models.IntegerField()
    id_particulier = models.IntegerField()
    read = models.BooleanField()
    ts_message = models.IntegerField()
    is_removed = models.BooleanField()
    is_admin_closure = models.BooleanField()
    ts_creation = models.IntegerField()
    statut = models.IntegerField()

    date_claim = models.DateTimeField()

    station = models.ForeignKey('Entity', db_column='id_station', on_delete=models.CASCADE, related_name='ticket_station', blank=True, null=True)
    distributeur = models.ForeignKey('Entity', db_column='id_distributeur', on_delete=models.CASCADE, related_name='ticket_distributor', blank=True, null=True)
    type = models.ForeignKey('TicketType', db_column='id_type', on_delete=models.CASCADE)
    admin = models.ForeignKey('Admin', db_column='id_admin', to_field='id_entite', related_name='support_ticket_for_admin', on_delete=models.CASCADE)
    reserved_by = models.ForeignKey('Admin', db_column='id_admin_claim', to_field='id_entite', related_name='support_ticket_for_reserved_by', on_delete=models.CASCADE, blank=True, null=True)
    produit = models.ForeignKey('Produit', db_column='id_machine', on_delete=models.CASCADE)
    objects = TicketManager()
    ticket_status = models.ForeignKey('TicketStatus', db_column='id_statut', on_delete=models.CASCADE)

    def get_contrat(self):
        try:
            return self.ticketcontrat.contrat if self.ticketcontrat.contrat else None
        except ObjectDoesNotExist:
            return ""

    def days_since_creation(self) -> int:
        try:
            if self.ts_creation is None:
                raise ValueError("No value passed for ts_creation")

            if not isinstance(self.ts_creation, int):
                raise TypeError("ts_creation is of the wrong type, expected int")

            ts_creation_date = datetime.fromtimestamp(self.ts_creation)
            return (datetime.now() - ts_creation_date).days

        except TypeError as e:
            print(f"Type error: {e}")
            return None
        except ValueError as e:
            print(f"Value error: {e}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None

    def days_since_reservation(self) -> Optional[int]:
        try:
            if self.date_claim is None:
                return None

            if not isinstance(self.date_claim, datetime):
                raise TypeError("ts_creation is of the wrong type, expected datetime")

            reservation_date = timezone.localtime(self.date_claim)  # date_claim is timezone-aware
            return (timezone.now() - reservation_date).days

        except TypeError as e:
            print(f"Type error: {e}")
            return None
        except ValueError as e:
            print(f"Value error: {e}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None

    def get_last_action_date(self) -> int:
        return datetime.fromtimestamp(max(self.last_log_timestamp, self.last_message_timestamp))

    def days_since_last_action(self) -> int:
        try:
            last_action_date = self.get_last_action_date()
            return (datetime.now() - last_action_date).days

        except TypeError as e:
            print(f"Type error: {e}")
            return None
        except ValueError as e:
            print(f"Value error: {e}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None

    def creation_date(self) -> datetime:
        return datetime.strftime(datetime.fromtimestamp(self.ts_creation), '%d.%m.%Y')

    class Meta:
        db_table = 'support_tickets'
        ordering = ['id']
        managed = False  # No migrations for this model


class TicketType(models.Model):
    id = models.IntegerField(primary_key=True)
    tr_title = models.IntegerField()

    class Meta:
        db_table = 'support_tickets_types'
        managed = False  # No migrations for this model


class Translate(models.Model):
    id = models.IntegerField(primary_key=True)
    fr = models.TextField()
    en = models.TextField()
    ru = models.TextField()

    class Meta:
        db_table = 'translate'
        managed = False  # No migrations for this model


class Entity(models.Model):
    id = models.IntegerField(primary_key=True)
    id_fournisseur = models.IntegerField()
    id_admin = models.IntegerField()
    id_depot = models.IntegerField()
    id_station = models.IntegerField()
    id_etablissement = models.IntegerField()
    id_distributeur = models.IntegerField()
    id_societe = models.IntegerField()
    societe = models.CharField(max_length=100)

    class Meta:
        db_table = 'entites'
        managed = False  # No migrations for this model


class Log(models.Model):
    id = models.IntegerField(primary_key=True)
    id_ticket = models.IntegerField()
    log_type = models.ForeignKey('LogType', db_column='id_type', on_delete=models.CASCADE)
    ts = models.IntegerField()

    class Meta:
        db_table = 'support_tickets_logs'
        managed = False  # No migrations for this model


class LogType(models.Model):
    id = models.IntegerField(primary_key=True)
    tr_nom = models.IntegerField()

    class Meta:
        db_table = 'support_tickets_logs_types'
        managed = False  # No migrations for this model


class ArboLink(models.Model):
    id = models.IntegerField(primary_key=True)
    produit = models.ForeignKey('Produit', db_column='id_produit', on_delete=models.CASCADE)
    id_arborescence = models.IntegerField()

    class Meta:
        db_table = 'f_produits_machine'
        managed = False  # No migrations for this model


class Marque(models.Model):
    id = models.IntegerField(primary_key=True)
    nom = models.CharField(max_length=100)

    class Meta:
        db_table = 'marques'
        managed = False  # No migrations for this model


class SwapEntity(models.Model):
    id = models.IntegerField(primary_key=True)
    id_entite = models.IntegerField()

    class Meta:
        db_table = 'f_entites_swap'
        managed = False  # No migrations for this model


class Discussion(models.Model):
    id = models.IntegerField(primary_key=True)
    id_discussion = models.ForeignKey('Ticket', db_column='id_discussion', on_delete=models.CASCADE)
    id_entite = models.IntegerField()
    message = models.TextField()
    for_particulier = models.BooleanField()
    for_station = models.BooleanField()
    for_distributeur = models.BooleanField()
    ts_creation = models.IntegerField()

    class Meta:
        db_table = 'discussions_messages'
        managed = False  # No migrations for this model
