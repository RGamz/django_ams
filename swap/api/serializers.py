from rest_framework import serializers
from api.models import Ticket, Produit, Admin, Contrat, Marque, TicketStatus, Translate, Discussion, Log


class MarqueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marque
        fields = ['id', 'nom']


class ProduitSerializer(serializers.ModelSerializer):
    marque = MarqueSerializer()

    class Meta:
        model = Produit
        fields = ['ref', 'marque']


class AdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Admin
        fields = ['pseudo']


class ContratSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contrat
        fields = ['id', 'nom']


class StatusSerializer(serializers.ModelSerializer):
    nom_fr = serializers.CharField(source='tr_nom.fr')

    class Meta:
        model = TicketStatus
        fields = ['id', 'nom_fr']


class TranslateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Translate
        fields = ['fr', 'en', 'ru']


class DiscussionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discussion
        fields = ['id', 'id_discussion', 'id_entite', 'message', 'for_particulier', 'for_station', 'for_distributeur', 'ts_creation']


class LogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Log
        fields = ['id', 'id_ticket', 'log_type', 'ts']


class TicketSerializer(serializers.ModelSerializer):
    produit = ProduitSerializer()
    admin = AdminSerializer()
    reserved_by = AdminSerializer()
    contrat = serializers.SerializerMethodField()
    station = serializers.SerializerMethodField()
    distributor = serializers.CharField(source='distributeur.societe', read_only=True)
    ticket_status = StatusSerializer()

    def get_contrat(self, obj):
        # Use the pre-fetched related objects
        if hasattr(obj, 'ticketcontrat') and obj.ticketcontrat and hasattr(obj.ticketcontrat, 'contrat'):
            contrat = obj.ticketcontrat.contrat
            return ContratSerializer(contrat).data if contrat else None
        return None

    def get_station(self, obj):
        if hasattr(obj, 'station') and obj.station:
            return obj.station.societe
        return None

    class Meta:
        model = Ticket
        fields = ['id', 'read', 'date_claim', 'ts_creation', 'produit', 'admin', 'reserved_by', 'contrat', 'distributor', 'station', 'ticket_status', 'type']
