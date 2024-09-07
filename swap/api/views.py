from django.db import connection
from rest_framework import viewsets
from api.models import Ticket
from api.serializers import TicketSerializer
from django.db.models import Q, Count, Case, When, IntegerField
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from api.forms import LoginForm
from django.contrib.auth.decorators import login_required

# these are related to simple ticket types like technical question or asking for product notice etc
SIMPLE_TICKETS_TYPE_IDS = [1, 4, 22, 51, 71]

# out of warranty ticket type
OUT_OF_WARRANTY_TYPE_ID = 63

KINGFISHER_CONTRACTS_IDS = [104, 85]
SUNTEK_CONTRACT_ID = 99
REUSED_CONTRACT = 84
TERACT_CONTRACTS = [100, 101, 103]
BUILDER_CONTRACTS_IDS = [30, 106]

# contract names : ['BCM Better Choice', 'BCM BURGAIN', 'BCM JIWEI', 'BCM Le Fun', 'Carrefour Barbecues', 'FOXTER ASPIRATEUR -LECLERC', 'JHS CLIM -LECLERC', 'LECLERC - MONO Batterie', 'NHP FOXTER - LECLERC']
BRONZE_CONTRACTS_IDS = [52, 74, 89, 82, 75, 35, 65, 81, 48]

# contract names : ['MTD - assist. dom.', 'MTD - standard']
MTD_CONTRACTS_IDS = [69, 70]

# ['LEROY MERLIN FR - STERWINS', 'BUILDER / TCK']
LEROY_CONTRACTS_IDS = [30, 60]

# mobilier de jardin : Bcm better choice, Bcm le fun, Bcm jiwai, Teract mobilier de jardin
MOBILIER_JARDIN_CONTRACTS_IDS = [52, 82, 89, 103]

# russian contracts
CONTRACTS_EXCLUDED_IDS = [3, 46, 64, 71]


def log_in(request):

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(
                request,
                username=cd['username'],
                password=cd['password']
            )
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('/')  # Redirect to the home page
                else:
                    return HttpResponse('Disabled account')
            else:
                return HttpResponse('Invalid login')
    else:
        form = LoginForm()
    return render(request, 'api/login.html', {'form': form})


class BaseViewSet(viewsets.ModelViewSet):
    serializer_class = TicketSerializer

    def get_read_filter(self):
        return Q(read=0)

    def get_queryset_base(self):
        return Ticket.objects.with_last_action_dates() \
            .select_related('produit', 'admin', 'reserved_by', 'type', 'distributeur', 'station') \
            .prefetch_related('ticketcontrat__contrat',
                              'produit__marque',
                              'ticket_status',
                              'ticket_status__tr_nom',
                              'type',
                              ) \
            .filter(is_removed=0).filter(self.get_read_filter()) \
            .order_by('last_action_date') \
            .annotate(admin_ticket_count=Count('admin'))


class AllUnclosedTickets(BaseViewSet):
    def get_read_filter(self):
        return Q(read=0) | Q(read=1)

    def get_queryset(self):
        base_queryset = self.get_queryset_base()
        return base_queryset.filter(~Q(statut=2)).all()


@login_required
def index(request):

    open_tickets = AllUnclosedTickets().get_queryset().exclude(admin__pseudo__in=['Kirill', 'Abdurakhman', 'Igor', 'Nikita'])

    tickets_per_admin = open_tickets.values('admin__pseudo').annotate(
        open_tickets=Count(Case(When(~Q(statut=2), then=1), output_field=IntegerField())),
        read_tickets=Count(Case(When(read=1, then=1), output_field=IntegerField())),
        unread_tickets=Count(Case(When(read=0, then=1), output_field=IntegerField()))
    ).order_by('-open_tickets')

    total_read_tickets = open_tickets.filter(read=1).count()
    total_unread_tickets = open_tickets.filter(read=0).count()

    with connection.cursor() as cursor:
        cursor.execute(
            '''
                SELECT
                    admin,
                    SUM(message_qty) AS messages,
                    SUM(logs_qty) AS logs,
                    SUM(message_qty + logs_qty) AS total_actions
                FROM (
                    SELECT
                        a.pseudo AS admin,
                        COUNT(l.id_ticket) AS logs_qty,
                        0 AS message_qty
                    FROM
                        support_tickets_logs l
                    LEFT JOIN
                        support_tickets_logs_types lt ON lt.id = l.id_type
                    LEFT JOIN
                        translate tr ON tr.id = lt.tr_nom
                    LEFT JOIN
                        admins a ON a.id_entite = l.id_entite
                    WHERE
                        a.pseudo NOT IN ('', 'Nikita', 'Igor', 'Angélique')
                        AND DATE(FROM_UNIXTIME(l.ts)) = CURRENT_DATE
                        AND l.id_type NOT IN (1, 2, 5, 6, 8, 9, 12, 15, 20, 21,
                            22, 23, 24, 25, 26, 27, 28, 29, 32, 36, 41, 42, 43,
                            45, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 59, 64,
                            65, 66, 67, 68, 70, 71, 72, 73, 74, 75, 77, 81, 82,
                            83, 84, 85, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96,
                            97, 101, 102, 103, 104, 107, 110, 113, 118, 119)
                    GROUP BY
                        a.pseudo

                    UNION ALL

                    SELECT
                        a.pseudo AS admin,
                        0 AS logs_qty,
                        COUNT(mes.message) AS message_qty
                    FROM
                        discussions_messages mes
                    LEFT JOIN
                        admins a ON a.id_entite = mes.id_entite
					LEFT JOIN
						support_tickets t ON mes.id_discussion = t.id_discussion
                    WHERE
                        a.id_entite != ''
                        AND DATE(FROM_UNIXTIME(mes.ts_creation)) = CURRENT_DATE
                        AND a.pseudo NOT IN ('', 'Nikita', 'Igor')
                        AND t.id IS NOT NULL
                    GROUP BY
                        a.pseudo
                ) AS temp_table
                GROUP BY
                    admin
                ORDER BY
                    total_actions DESC;
               ''')
        rows = cursor.fetchall()

    # Create a list of dictionaries with days_since_creation
    openTicketList2 = []
    messages_sum = 0
    logs_sum = 0
    total_actions = 0

    for row in rows:
        messages_sum += row[1]
        logs_sum += row[2]
        total_actions += row[3]
        tickets_dict = {'admin': row[0], 'messages': row[1], 'logs': row[2], 'total_actions': row[3]}
        openTicketList2.append(tickets_dict)

    context = {
        'openTicketList': open_tickets,
        'openTicketCounter': open_tickets.count(),
        'ticketsPerAdmin': tickets_per_admin,
        'totalRead': total_read_tickets,
        'totalUnread': total_unread_tickets,
        'messages_sum': messages_sum,
        'logs_sum': logs_sum,
        'total_actions': total_actions,
        'LogsAndMessagesPerAdmin': openTicketList2
    }

    return render(request, 'api/index.html', context)

# AGENT VERIFICATION


class AgentVerificationBaseViewSet(BaseViewSet):
    def get_queryset_base(self):
        return super().get_queryset_base() \
            .filter(admin__pseudo='03 - Agent Vérification SWAP')


class AgentVerificationOpenTicketsViewSet(AgentVerificationBaseViewSet):
    def get_queryset(self):
        return self.get_queryset_base() \
            .filter(~Q(statut=2)).all()


class AgentVerificationClosedAndUnreadViewSet(AgentVerificationBaseViewSet):
    def get_queryset(self):
        return self.get_queryset_base() \
            .filter(statut=2).all()


class AgentVerificationSuntekViewSet(AgentVerificationBaseViewSet):
    def get_queryset(self):
        return self.get_queryset_base() \
            .filter(~Q(statut=2), ticketcontrat__contrat__id=SUNTEK_CONTRACT_ID).all()


class AgentVerificationTeractViewSet(AgentVerificationBaseViewSet):
    def get_queryset(self):
        return self.get_queryset_base() \
            .filter(~Q(statut=2), ticketcontrat__contrat__id__in=TERACT_CONTRACTS).all()


@login_required
def agent_verification(request):
    open_tickets = AgentVerificationOpenTicketsViewSet().get_queryset()

    closed_unread = AgentVerificationClosedAndUnreadViewSet().get_queryset()

    suntek_tickets = AgentVerificationSuntekViewSet().get_queryset()

    teract_tickets = AgentVerificationTeractViewSet().get_queryset()

    context = {
        'openTicketList': open_tickets,
        'openTicketCounter': open_tickets.count(),

        'closedUnread': closed_unread,
        'closedUnreadCounter': closed_unread.count(),

        'suntekTickets': suntek_tickets,
        'suntekTicketsCounter': suntek_tickets.count(),

        'teractTickets': teract_tickets,
        'teractTicketsCounter': teract_tickets.count(),
    }

    return render(request, 'api/agent_verification.html', context)


# AGENT ADMINISTRATIF

class AgentAdministratifBaseViewSet(BaseViewSet):
    def get_queryset_base(self):
        return super().get_queryset_base() \
            .filter(admin__pseudo='02 - Agent Administratif SWAP')


class AgentAdministratifOpenTicketsViewSet(AgentAdministratifBaseViewSet):
    def get_queryset(self):
        return self.get_queryset_base() \
            .filter(~Q(statut=2)).all()


class AgentAdministratifClosNonLus(AgentAdministratifBaseViewSet):
    # all closed but unread tickets
    def get_queryset(self):
        return self.get_queryset_base() \
            .filter(Q(statut=2)).all()


class AgentAdministratifSimpleUnclosed(AgentAdministratifBaseViewSet):
    # simple tickets non lus
    def get_queryset(self):
        return self.get_queryset_base() \
            .filter(Q(type__id__in=SIMPLE_TICKETS_TYPE_IDS), ~Q(statut=2)).all()


class AgentAdministratifSuntek(AgentAdministratifBaseViewSet):
    # Suntek tickets
    def get_queryset(self):
        return self.get_queryset_base() \
            .filter(~Q(statut=2), ticketcontrat__contrat__id=SUNTEK_CONTRACT_ID).all()


class AgentAdministratifModerateReparation(AgentAdministratifBaseViewSet):
    # Tickets with statut 'La station a fait une demande de réparation qui doit être modérée par un admin'
    def get_queryset(self):
        return self.get_queryset_base() \
            .filter(~Q(statut=2), ticket_status=2).all()


class AgentAdministratifDemandeGarantie(AgentAdministratifBaseViewSet):
    # Tickets with statut 'Une demande de garantie a été effectuée. La demande est en cours de modération par SWAP'
    def get_queryset(self):
        return self.get_queryset_base() \
            .filter(~Q(statut=2), ticket_status=3).all()


class AgentAdministratifModerateDDG(AgentAdministratifBaseViewSet):
    # Tickets with statut ''Attente moderation DDG''
    def get_queryset(self):
        return self.get_queryset_base() \
            .filter(~Q(statut=2), ticket_status=4).all()


class AgentAdministratifPiecesLivraison(AgentAdministratifBaseViewSet):
    # Tickets with statut 'Un admin a validé la demande de réparation, les pièces sont en cours de transport.'
    def get_queryset(self):
        return self.get_queryset_base() \
            .filter(~Q(statut=2), ticket_status=5).all()


class AgentAdministratifReparationReussie(AgentAdministratifBaseViewSet):
    # Tickets with statut 'La réparation s'est bien passée. Un certificat de diagnostic est disponible en pièce jointe à gauche.'
    def get_queryset(self):
        return self.get_queryset_base() \
            .filter(~Q(statut=2), ticket_status=14).all()


class AgentAdministratifAnr(AgentAdministratifBaseViewSet):
    # Tickets with statut 'Une attestation de non réparation (ANR) a été validée.'
    def get_queryset(self):
        return self.get_queryset_base() \
            .filter(~Q(statut=2), ticket_status=7).all()


class AgentAdministratifTeract(AgentAdministratifBaseViewSet):
    def get_queryset(self):
        return self.get_queryset_base() \
            .filter(~Q(statut=2), ticketcontrat__contrat__id__in=TERACT_CONTRACTS).all()


class AgentAdministratifMobilierJardin(AgentAdministratifBaseViewSet):
    def get_queryset(self):
        return self.get_queryset_base() \
            .filter(~Q(statut=2), ticketcontrat__contrat__id__in=MOBILIER_JARDIN_CONTRACTS_IDS).all()


@login_required
def agent_administratif(request):

    open_tickets = AgentAdministratifOpenTicketsViewSet().get_queryset()
    closed_unread = AgentAdministratifClosNonLus().get_queryset()
    simple_tickets = AgentAdministratifSimpleUnclosed().get_queryset()
    suntek_tickets = AgentAdministratifSuntek().get_queryset()
    teract_tickets = AgentAdministratifTeract().get_queryset()
    moderation_reparation = AgentAdministratifModerateReparation().get_queryset()
    demande_garantie = AgentAdministratifDemandeGarantie().get_queryset()
    moderation_ddg = AgentAdministratifModerateDDG().get_queryset()
    pieces_livraison = AgentAdministratifPiecesLivraison().get_queryset()
    reparation_reussie = AgentAdministratifReparationReussie().get_queryset()
    anr = AgentAdministratifAnr().get_queryset()
    mobilier_jardin = AgentAdministratifMobilierJardin().get_queryset()

    # moving some HG tickets to agent admin
    attente_devis_tickets = AgentHorsGarantieAttenteDevisStation().get_queryset()
    attente_devis_acceptation_client_tickets = AgentHorsGarantieAttenteAcceptationClient().get_queryset()
    devis_accepted_client_tickets = AgentHorsGarantieDevisAccepteParClient().get_queryset()
    attente_payement_devis_client_tickets = AgentHorsGarantieAttentePaiementPanier().get_queryset()
    moderation_transport_retour_tickets = AgentHorsGarantieTransportRetourModeration().get_queryset()
    hg_closed_unread = AgentHorsGarantieTicketsClosedUnread().get_queryset()

    context = {
        'openTicketList': open_tickets,
        'openTicketCounter': open_tickets.count(),

        'closedUnread': closed_unread,
        'closedUnreadCounter': closed_unread.count(),

        'simpleTickets': simple_tickets,
        'simpleTicketsCounter': simple_tickets.count(),

        'suntekTickets': suntek_tickets,
        'suntekTicketsCounter': suntek_tickets.count(),

        'moderationReparation': moderation_reparation,
        'moderationReparationCounter': moderation_reparation.count(),

        'demandeGarantieTickets': demande_garantie,
        'demandeGarantieTicketsCounter': demande_garantie.count(),

        'moderationDDG': moderation_ddg,
        'moderationDDGCounter': moderation_ddg.count(),

        'piecesLivraisonTickets': pieces_livraison,
        'piecesLivraisonTicketsCounter': pieces_livraison.count(),

        'reparationReussieTickets': reparation_reussie,
        'reparationReussieTicketsCounter': reparation_reussie.count(),

        'anrTickets': anr,
        'anrTicketsCounter': anr.count(),

        'teractTickets': teract_tickets,
        'teractTicketsCounter': teract_tickets.count(),

        'mobilierJardin': mobilier_jardin,
        'mobilierJardinCounter': mobilier_jardin.count(),

        # below are HG tickets
        'HGclosedUnread': hg_closed_unread,
        'HGclosedUnreadCounter': hg_closed_unread.count(),

        'attenteDevis': attente_devis_tickets,
        'attenteDevisCounter': attente_devis_tickets.count(),

        'attenteDevisAcceptationClient': attente_devis_acceptation_client_tickets,
        'attenteDevisAcceptationClientCounter': attente_devis_acceptation_client_tickets.count(),

        'devisAcceptedClient': devis_accepted_client_tickets,
        'devisAcceptedClientCounter': devis_accepted_client_tickets.count(),

        'attentePaymentDevisClient': attente_payement_devis_client_tickets,
        'attentePaymentDevisClientCounter': attente_payement_devis_client_tickets.count(),

        'moderationTransportRetour': moderation_transport_retour_tickets,
        'moderationTransportRetourCounter': moderation_transport_retour_tickets.count(),

    }

    return render(request, 'api/agent_administratif.html', context)


# AGENT TECHNIQUE

class AgentTechniqueBaseViewSet(BaseViewSet):
    def get_queryset_base(self):
        return super().get_queryset_base() \
            .filter(admin__pseudo='01 - Agent Technique SWAP')


class AgentTechniqueOpenTickets(AgentTechniqueBaseViewSet):
    def get_queryset(self):
        return self.get_queryset_base() \
            .filter(~Q(statut=2)).all()


class AgentTechniqueRiders(AgentTechniqueBaseViewSet):
    # contrats.nom NOT IN ('MTD - standard', 'MTD - assist. dom.')
    # filter only by riders (id_arbo = 1251, 217)
    def get_queryset(self):
        return self.get_queryset_base() \
            .filter(~Q(statut=2), produit__arbolink__id_arborescence__in=[1251, 217]) \
            .exclude(Q(ticketcontrat__contrat__id__in=[70])) \
            .all()


class AgentTechniqueDaye(AgentTechniqueBaseViewSet):
    def get_queryset(self):
        DAYE_REFS = [
            '1638ES',
            '1636ECLi',
            'PM4650S',
            'PM5660SHW',
            'PM5160SEHW',
            'PM5160SETrike',
            'PM5690SHW',
            'PM5170SHW-H'
            ]
        return self.get_queryset_base() \
            .filter(~Q(statut=2), produit__ref__in=DAYE_REFS) \
            .all()


class AgentTechniqueFeider(AgentTechniqueBaseViewSet):
    # Feider marque id = 3
    def get_queryset(self):
        return self.get_queryset_base() \
            .filter(~Q(statut=2), produit__marque__id=3) \
            .all()


class AgentTechniqueGenerators(AgentTechniqueBaseViewSet):
    def get_queryset(self):
        GENERATORS_ARBO_IDS = [102, 106, 107, 108, 1165, 110, 111, 152, 1175, 155, 1026, 1334]
        return self.get_queryset_base() \
            .filter(~Q(statut=2), produit__arbolink__id_arborescence__in=GENERATORS_ARBO_IDS) \
            .all()


class AgentTechniqueBronzeContracts(AgentTechniqueBaseViewSet):
    def get_queryset(self):
        return self.get_queryset_base() \
            .filter(~Q(statut=2), ticketcontrat__contrat__id__in=BRONZE_CONTRACTS_IDS) \
            .all()


class AgentTechniqueModerateDDG(AgentTechniqueBaseViewSet):
    # Tickets with statut 'Attente moderation DDG'
    def get_queryset(self):
        return self.get_queryset_base() \
            .filter(~Q(statut=2), ticket_status=4).all()


class AgentTechniqueReused(AgentTechniqueBaseViewSet):
    def get_queryset(self):
        return self.get_queryset_base() \
            .filter(~Q(statut=2), ticketcontrat__contrat__id=REUSED_CONTRACT) \
            .all()


class AgentTechniqueMTD(AgentTechniqueBaseViewSet):
    def get_queryset(self):
        return self.get_queryset_base() \
            .filter(~Q(statut=2), ticketcontrat__contrat__id__in=MTD_CONTRACTS_IDS) \
            .all()


class AgentTechniqueKingfisher(AgentTechniqueBaseViewSet):
    def get_queryset(self):
        return self.get_queryset_base() \
            .filter(~Q(statut=2), ticketcontrat__contrat__id__in=KINGFISHER_CONTRACTS_IDS) \
            .all()


class AgentTechniqueSuntek(AgentTechniqueBaseViewSet):
    def get_queryset(self):
        return self.get_queryset_base() \
            .filter(~Q(statut=2), ticketcontrat__contrat__id=SUNTEK_CONTRACT_ID) \
            .all()


class AgentTechniqueLeroy(AgentTechniqueBaseViewSet):
    def get_queryset(self):
        return self.get_queryset_base() \
            .filter(~Q(statut=2), ticketcontrat__contrat__id__in=LEROY_CONTRACTS_IDS, distributeur__societe__contains='LEROY MERLIN') \
            .all()


class AgentTechniqueKaufland(AgentTechniqueBaseViewSet):
    def get_queryset(self):
        # kaufland contract id = 63
        CONTRACTS = [63]
        return self.get_queryset_base() \
            .filter(~Q(statut=2), ticketcontrat__contrat__id__in=CONTRACTS) \
            .all()


class AgentTechniqueClosNonLus(AgentTechniqueBaseViewSet):
    def get_queryset(self):
        return self.get_queryset_base() \
            .filter(Q(statut=2)).all()


class AgentTechniqueSimpleUnclosed(AgentTechniqueBaseViewSet):
    def get_queryset(self):
        return self.get_queryset_base() \
            .filter(Q(type__id__in=SIMPLE_TICKETS_TYPE_IDS), ~Q(statut=2)).all()


class AgentTechniqueMobilierJardin(AgentTechniqueBaseViewSet):
    def get_queryset(self):
        return self.get_queryset_base() \
            .filter(~Q(statut=2), ticketcontrat__contrat__id__in=MOBILIER_JARDIN_CONTRACTS_IDS).all()


class AgentTechniqueTeract(AgentTechniqueBaseViewSet):
    def get_queryset(self):
        return self.get_queryset_base() \
            .filter(~Q(statut=2), ticketcontrat__contrat__id__in=TERACT_CONTRACTS).all()


@login_required
def agent_technique(request):

    open_tickets = AgentTechniqueOpenTickets().get_queryset()
    closed_unread = AgentTechniqueClosNonLus().get_queryset()
    simple_tickets = AgentTechniqueSimpleUnclosed().get_queryset()
    kingfisher_tickets = AgentTechniqueKingfisher().get_queryset()
    suntek_tickets = AgentTechniqueSuntek().get_queryset()
    rider_tickets = AgentTechniqueRiders().get_queryset()
    daye_tickets = AgentTechniqueDaye().get_queryset()
    teract_tickets = AgentTechniqueTeract().get_queryset()
    feider_tickets = AgentTechniqueFeider().get_queryset()
    generator_tickets = AgentTechniqueGenerators().get_queryset()
    bronze_tickets = AgentTechniqueBronzeContracts().get_queryset()
    moderate_DDG = AgentTechniqueModerateDDG().get_queryset()
    reused_tickets = AgentTechniqueReused().get_queryset()
    mtd_tickets = AgentTechniqueMTD().get_queryset()
    leroy_tickets = AgentTechniqueLeroy().get_queryset()
    kaufland_tickets = AgentTechniqueKaufland().get_queryset()
    mobilier_jardin_tickets = AgentTechniqueMobilierJardin().get_queryset()

    context = {
        'openTicketList': open_tickets,
        'openTicketCounter': open_tickets.count(),

        'closedUnread': closed_unread,
        'closedUnreadCounter': closed_unread.count(),

        'simpleTickets': simple_tickets,
        'simpleTicketsCounter': simple_tickets.count(),

        'kingfisherTickets': kingfisher_tickets,
        'kingfisherTicketsCounter': kingfisher_tickets.count(),

        'suntekTickets': suntek_tickets,
        'suntekTicketsCounter': suntek_tickets.count(),

        'riderTickets': rider_tickets,
        'riderTicketsCounter': rider_tickets.count(),

        'dayeTickets': daye_tickets,
        'dayeTicketsCounter': daye_tickets.count(),

        'feiderTickets': feider_tickets,
        'feiderTicketsCounter': feider_tickets.count(),

        'generatorTickets': generator_tickets,
        'generatorTicketsCounter': generator_tickets.count(),

        'bronzeTickets': bronze_tickets,
        'bronzeTicketsCounter': bronze_tickets.count(),

        'moderateDDG': moderate_DDG,
        'moderateDDGCounter': moderate_DDG.count(),

        'reusedTickets': reused_tickets,
        'reusedTicketsCounter': reused_tickets.count(),

        'mtdTickets': mtd_tickets,
        'mtdTicketsCounter': mtd_tickets.count(),

        'leroyTickets': leroy_tickets,
        'leroyTicketsCounter': leroy_tickets.count(),

        'kauflandTickets': kaufland_tickets,
        'kauflandTicketsCounter': kaufland_tickets.count(),

        'mobilierJardinTickets': mobilier_jardin_tickets,
        'mobilierJardinTicketsCounter': mobilier_jardin_tickets.count(),

        'teractTickets': teract_tickets,
        'teractTicketsCounter': teract_tickets.count(),
    }

    return render(request, 'api/agent_technique.html', context)


# AGENT TECHNIQUE PRO

class AgentTechniqueProBaseViewSet(BaseViewSet):
    def get_queryset_base(self):
        return super().get_queryset_base() \
            .filter(admin__pseudo='09 - Agent Technique Pro')


class AgentTechniqueProOpenTickets(AgentTechniqueProBaseViewSet):
    def get_queryset(self):
        return self.get_queryset_base() \
            .filter(~Q(statut=2)).all()


class AgentTechniqueProRiders(AgentTechniqueProBaseViewSet):
    # contrats.nom NOT IN ('MTD - standard', 'MTD - assist. dom.')
    # filter only by riders (id_arbo = 1251, 217)
    def get_queryset(self):
        return self.get_queryset_base() \
            .filter(~Q(statut=2), produit__arbolink__id_arborescence__in=[1251, 217]) \
            .exclude(Q(ticketcontrat__contrat__id__in=[70])) \
            .all()


class AgentTechniqueProDaye(AgentTechniqueProBaseViewSet):
    def get_queryset(self):
        DAYE_REFS = [
            '1638ES',
            '1636ECLi',
            'PM4650S',
            'PM5660SHW',
            'PM5160SEHW',
            'PM5160SETrike',
            'PM5690SHW',
            'PM5170SHW-H'
            ]
        return self.get_queryset_base() \
            .filter(~Q(statut=2), produit__ref__in=DAYE_REFS) \
            .all()


class AgentTechniqueProFeider(AgentTechniqueProBaseViewSet):
    # Feider marque id = 3
    def get_queryset(self):
        return self.get_queryset_base() \
            .filter(~Q(statut=2), produit__marque__id=3) \
            .all()


class AgentTechniqueProGenerators(AgentTechniqueProBaseViewSet):
    def get_queryset(self):
        GENERATORS_ARBO_IDS = [102, 106, 107, 108, 1165, 110, 111, 152, 1175, 155, 1026, 1334]
        return self.get_queryset_base() \
            .filter(~Q(statut=2), produit__arbolink__id_arborescence__in=GENERATORS_ARBO_IDS) \
            .all()


class AgentTechniqueProBronzeContracts(AgentTechniqueProBaseViewSet):
    def get_queryset(self):
        return self.get_queryset_base() \
            .filter(~Q(statut=2), ticketcontrat__contrat__id__in=BRONZE_CONTRACTS_IDS) \
            .all()


class AgentTechniqueProModerateDDG(AgentTechniqueProBaseViewSet):
    # Tickets with statut 'Attente moderation DDG'
    def get_queryset(self):
        return self.get_queryset_base() \
            .filter(~Q(statut=2), ticket_status=4).all()


class AgentTechniqueProReused(AgentTechniqueProBaseViewSet):
    def get_queryset(self):
        return self.get_queryset_base() \
            .filter(~Q(statut=2), ticketcontrat__contrat__id=REUSED_CONTRACT) \
            .all()


class AgentTechniqueProMTD(AgentTechniqueProBaseViewSet):
    def get_queryset(self):
        return self.get_queryset_base() \
            .filter(~Q(statut=2), ticketcontrat__contrat__id__in=MTD_CONTRACTS_IDS) \
            .all()


class AgentTechniqueProKingfisher(AgentTechniqueProBaseViewSet):
    def get_queryset(self):
        return self.get_queryset_base() \
            .filter(~Q(statut=2), ticketcontrat__contrat__id__in=KINGFISHER_CONTRACTS_IDS) \
            .all()


class AgentTechniqueProSuntek(AgentTechniqueProBaseViewSet):
    def get_queryset(self):
        return self.get_queryset_base() \
            .filter(~Q(statut=2), ticketcontrat__contrat__id=SUNTEK_CONTRACT_ID) \
            .all()


class AgentTechniqueProLeroy(AgentTechniqueProBaseViewSet):
    def get_queryset(self):
        return self.get_queryset_base() \
            .filter(~Q(statut=2), ticketcontrat__contrat__id__in=LEROY_CONTRACTS_IDS, distributeur__societe__contains='LEROY MERLIN') \
            .all()


class AgentTechniqueProKaufland(AgentTechniqueProBaseViewSet):
    def get_queryset(self):
        # kaufland contract id = 63
        CONTRACTS = [63]
        return self.get_queryset_base() \
            .filter(~Q(statut=2), ticketcontrat__contrat__id__in=CONTRACTS) \
            .all()


class AgentTechniqueProClosNonLus(AgentTechniqueProBaseViewSet):
    def get_queryset(self):
        return self.get_queryset_base() \
            .filter(Q(statut=2)).all()


class AgentTechniqueProSimpleUnclosed(AgentTechniqueProBaseViewSet):
    def get_queryset(self):
        return self.get_queryset_base() \
            .filter(Q(type__id__in=SIMPLE_TICKETS_TYPE_IDS), ~Q(statut=2)).all()


class AgentTechniqueProMobilierJardin(AgentTechniqueProBaseViewSet):
    def get_queryset(self):
        return self.get_queryset_base() \
            .filter(~Q(statut=2), ticketcontrat__contrat__id__in=MOBILIER_JARDIN_CONTRACTS_IDS).all()

class AgentTechniqueProTeract(AgentTechniqueProBaseViewSet):
    def get_queryset(self):
        return self.get_queryset_base() \
            .filter(~Q(statut=2), ticketcontrat__contrat__id__in=TERACT_CONTRACTS).all()


@login_required
def agent_technique_pro(request):

    open_tickets = AgentTechniqueProOpenTickets().get_queryset()
    closed_unread = AgentTechniqueProClosNonLus().get_queryset()
    simple_tickets = AgentTechniqueProSimpleUnclosed().get_queryset()
    kingfisher_tickets = AgentTechniqueProKingfisher().get_queryset()
    suntek_tickets = AgentTechniqueProSuntek().get_queryset()
    rider_tickets = AgentTechniqueProRiders().get_queryset()
    daye_tickets = AgentTechniqueProDaye().get_queryset()
    teract_tickets = AgentTechniqueProTeract().get_queryset()
    feider_tickets = AgentTechniqueProFeider().get_queryset()
    generator_tickets = AgentTechniqueProGenerators().get_queryset()
    bronze_tickets = AgentTechniqueProBronzeContracts().get_queryset()
    moderate_DDG = AgentTechniqueProModerateDDG().get_queryset()
    reused_tickets = AgentTechniqueProReused().get_queryset()
    mtd_tickets = AgentTechniqueProMTD().get_queryset()
    leroy_tickets = AgentTechniqueProLeroy().get_queryset()
    kaufland_tickets = AgentTechniqueProKaufland().get_queryset()
    mobilier_jardin_tickets = AgentTechniqueProMobilierJardin().get_queryset()

    context = {
        'openTicketList': open_tickets,
        'openTicketCounter': open_tickets.count(),

        'closedUnread': closed_unread,
        'closedUnreadCounter': closed_unread.count(),

        'simpleTickets': simple_tickets,
        'simpleTicketsCounter': simple_tickets.count(),

        'kingfisherTickets': kingfisher_tickets,
        'kingfisherTicketsCounter': kingfisher_tickets.count(),

        'suntekTickets': suntek_tickets,
        'suntekTicketsCounter': suntek_tickets.count(),

        'riderTickets': rider_tickets,
        'riderTicketsCounter': rider_tickets.count(),

        'dayeTickets': daye_tickets,
        'dayeTicketsCounter': daye_tickets.count(),

        'feiderTickets': feider_tickets,
        'feiderTicketsCounter': feider_tickets.count(),

        'generatorTickets': generator_tickets,
        'generatorTicketsCounter': generator_tickets.count(),

        'bronzeTickets': bronze_tickets,
        'bronzeTicketsCounter': bronze_tickets.count(),

        'moderateDDG': moderate_DDG,
        'moderateDDGCounter': moderate_DDG.count(),

        'reusedTickets': reused_tickets,
        'reusedTicketsCounter': reused_tickets.count(),

        'mtdTickets': mtd_tickets,
        'mtdTicketsCounter': mtd_tickets.count(),

        'leroyTickets': leroy_tickets,
        'leroyTicketsCounter': leroy_tickets.count(),

        'kauflandTickets': kaufland_tickets,
        'kauflandTicketsCounter': kaufland_tickets.count(),

        'mobilierJardinTickets': mobilier_jardin_tickets,
        'mobilierJardinTicketsCounter': mobilier_jardin_tickets.count(),

        'teractTickets': teract_tickets,
        'teractTicketsCounter': teract_tickets.count(),
    }

    return render(request, 'api/agent_technique_pro.html', context)


# OUT OF WARRANTY TICKETS

class AgentHorsGarantieBaseViewSet(BaseViewSet):
    def get_read_filter(self):
        return Q(read=0) | Q(read=1)

    def get_queryset_base(self):
        return super().get_queryset_base() \
            .filter(type=63) \
            .exclude(ticketcontrat__contrat__id__in=CONTRACTS_EXCLUDED_IDS) \
            .all()


class AgentHorsGarantieOpenViewSet(AgentHorsGarantieBaseViewSet):
    def get_queryset(self):
        return self.get_queryset_base() \
            .filter(~Q(statut=2)).all()


# tous tickets HG en attente de moderation DDG
class AgentHorsGarantieModerationDDG(BaseViewSet):
    def get_queryset(self):
        DDG_STATUS_ID = [4]
        return self.get_queryset_base() \
            .filter(~Q(statut=2), ticket_status__id__in=DDG_STATUS_ID) \
            .exclude(ticketcontrat__contrat__id__in=CONTRACTS_EXCLUDED_IDS) \
            .all()


# tous tickets HG en attente de diagnostic ou devis station
class AgentHorsGarantieAttenteDevisStation(AgentHorsGarantieBaseViewSet):
    def get_queryset(self):
        ATTENTE_DEVIS_STATUS_ID = [1,16,34]
        return self.get_queryset_base() \
            .filter(~Q(statut=2), ticket_status__id__in=ATTENTE_DEVIS_STATUS_ID) \
            .all()


# tous tickets HG en attente de la modération par un administrateur du devis proposé par la station
class AgentHorsGarantieModerationDevisStation(AgentHorsGarantieBaseViewSet):
    def get_queryset(self):
        MODERATION_DEVIS_STATION_STATUS_ID = 35
        return self.get_queryset_base() \
            .filter(~Q(statut=2), ticket_status__id=MODERATION_DEVIS_STATION_STATUS_ID) \
            .all()


# tous tickets HG en attente de devis pour client
class AgentHorsGarantieAttenteDevisClient(AgentHorsGarantieBaseViewSet):
    def get_queryset(self):
        ATTENTE_DEVIS_CLIENT_STATUS_ID = 36
        return self.get_queryset_base() \
            .filter(~Q(statut=2), ticket_status__id=ATTENTE_DEVIS_CLIENT_STATUS_ID) \
            .all()


# attente acceptation devis par le client
class AgentHorsGarantieAttenteAcceptationClient(AgentHorsGarantieBaseViewSet):
    def get_queryset(self):
        ATTENTE_ACCEPTATION_CLIENT_STATUS_ID = 38
        return self.get_queryset_base() \
            .filter(~Q(statut=2), ticket_status__id=ATTENTE_ACCEPTATION_CLIENT_STATUS_ID) \
            .all()


# Le client a accepté le devis, la station peut commencer la réparation
class AgentHorsGarantieDevisAccepteParClient(AgentHorsGarantieBaseViewSet):
    def get_queryset(self):
        DEVIS_ACCEPTE_CLIENT_STATUS_ID = 39
        return self.get_queryset_base() \
            .filter(~Q(statut=2), ticket_status__id=DEVIS_ACCEPTE_CLIENT_STATUS_ID) \
            .all()


# En attente de paiement du panier par le client
class AgentHorsGarantieAttentePaiementPanier(AgentHorsGarantieBaseViewSet):
    def get_queryset(self):
        ATTENTE_PAIEMENT_PANIER_STATUS_ID = 62
        return self.get_queryset_base() \
            .filter(~Q(statut=2), ticket_status__id=ATTENTE_PAIEMENT_PANIER_STATUS_ID) \
            .all()


# La prestation n'a pas pu aboutir
class AgentHorsGarantiePrestationNonAboutie(AgentHorsGarantieBaseViewSet):
    def get_queryset(self):
        PRESTATION_NON_ABOUTIE_STATUS_ID = 37
        return self.get_queryset_base() \
            .filter(~Q(statut=2), ticket_status__id=PRESTATION_NON_ABOUTIE_STATUS_ID) \
            .all()


# La réparation a été effectuée avec succès
class AgentHorsGarantieReparationEffectuee(AgentHorsGarantieBaseViewSet):
    def get_queryset(self):
        REPARATION_EFFECTUEE_STATUS_IDS = [14, 40]
        return self.get_queryset_base() \
            .filter(~Q(statut=2), ticket_status__id__in=REPARATION_EFFECTUEE_STATUS_IDS) \
            .all()


# Le transport retour a besoin d'être modéré par un admin
class AgentHorsGarantieTransportRetourModeration(AgentHorsGarantieBaseViewSet):
    def get_queryset(self):
        TRANSPORT_RETOUR_MODERATION_STATUS_ID = 60
        return self.get_queryset_base() \
            .filter(~Q(statut=2), ticket_status__id=TRANSPORT_RETOUR_MODERATION_STATUS_ID) \
            .all()


# Tickets clos et non lus
class AgentHorsGarantieTicketsClosedUnread(AgentHorsGarantieBaseViewSet):
    def get_read_filter(self):
        return Q(read=0)

    def get_queryset(self):
        return self.get_queryset_base() \
            .filter(statut=2) \
            .all()


# All tickets out of warranty without swap academies
class AgentHorsGarantieTicketsWithoutSwapAcademy(AgentHorsGarantieBaseViewSet):
    def get_queryset(self):
        EXCLUDED_STATION_IDS = [12582, 27756, 666079, 670769, 3051]
        return self.get_queryset_base() \
            .filter(~Q(statut=2), ~Q(station__id__in=EXCLUDED_STATION_IDS)) \
            .all()


@login_required
def agent_hors_garantie(request):

    open_tickets = AgentHorsGarantieOpenViewSet().get_queryset()
    moderation_DDG = AgentHorsGarantieModerationDDG().get_queryset()
    attente_devis_client_tickets = AgentHorsGarantieAttenteDevisClient().get_queryset()
    moderation_devis_station_tickets = AgentHorsGarantieModerationDevisStation().get_queryset()
    prestation_non_aboutie_tickets = AgentHorsGarantiePrestationNonAboutie().get_queryset()
    reparation_success_tickets = AgentHorsGarantieReparationEffectuee().get_queryset()
    no_swap_academy = AgentHorsGarantieTicketsWithoutSwapAcademy().get_queryset()

    context = {
        'openTicketList': open_tickets,
        'openTicketCounter': open_tickets.count(),

        'moderationDDG': moderation_DDG,
        'moderationDDGCounter': moderation_DDG.count(),

        'moderationDevisStation': moderation_devis_station_tickets,
        'moderationDevisStationCounter': moderation_devis_station_tickets.count(),

        'attenteDevisClient': attente_devis_client_tickets,
        'attenteDevisClientCounter': attente_devis_client_tickets.count(),

        'prestationNonAboutie': prestation_non_aboutie_tickets,
        'prestationNonAboutieCounter': prestation_non_aboutie_tickets.count(),

        'reparationSuccess': reparation_success_tickets,
        'reparationSuccessCounter': reparation_success_tickets.count(),

        'noSwapAcademy': no_swap_academy,
        'noSwapAcademyCounter': no_swap_academy.count(),

    }

    return render(request, 'api/agent_hors_garantie.html', context)


# AGENT BS AND HONDA MOTORS

class AgentMotorBaseViewSet(BaseViewSet):
    def get_queryset_base(self):
        return super().get_queryset_base() \
            .filter(admin__pseudo='05 - Agent Moteur BS/Honda')


# tous tickets agent BS et Honda
class AgentMotorOpenTickets(AgentMotorBaseViewSet):
    def get_queryset(self):
        return self.get_queryset_base() \
            .filter(~Q(statut=2)) \
            .all()


# tous tickets agent BS et Honda clos et non lu
class AgentMotorClosedUnread(AgentMotorBaseViewSet):
    def get_queryset(self):
        return self.get_queryset_base() \
            .filter(Q(statut=2)) \
            .all()


@login_required
def agent_moteur(request):

    open_tickets = AgentMotorOpenTickets().get_queryset()
    closed_unread = AgentMotorClosedUnread().get_queryset()

    context = {
        'openTicketList': open_tickets,
        'openTicketCounter': open_tickets.count(),

        'closedUnread': closed_unread,
        'closedUnreadCounter': closed_unread.count(),

    }

    return render(request, 'api/agent_moteur.html', context)


# -------------AGENT PIECES----------------

class AgentCreationPiecesBaseViewSet(BaseViewSet):
    def get_queryset_base(self):
        return super().get_queryset_base() \
            .filter(admin__pseudo='06 - Agent Création Pièces')


# tous tickets pieces
class AgentCreationPiecesOpenTickets(AgentCreationPiecesBaseViewSet):
    def get_queryset(self):
        return self.get_queryset_base() \
            .filter(~Q(statut=2)) \
            .all()


# tous tickets pieces closed et non lu
class AgentCreationPiecesClosedAndUnread(AgentCreationPiecesBaseViewSet):
    def get_queryset(self):
        return self.get_queryset_base() \
            .filter(Q(statut=2)) \
            .all()


@login_required
def agent_pieces(request):
    open_tickets = AgentCreationPiecesOpenTickets().get_queryset()

    closed_unread = AgentCreationPiecesClosedAndUnread().get_queryset()

    context = {
        'openTicketList': open_tickets,
        'openTicketCounter': open_tickets.count(),

        'closedUnread': closed_unread,
        'closedUnreadCounter': closed_unread.count(),
    }

    return render(request, 'api/agent_pieces.html', context)


# -------------AGENT ENTREPOT-------------

class AgentEntrepotSwapBaseViewSet(BaseViewSet):
    def get_queryset_base(self):
        return super().get_queryset_base() \
            .filter(admin__pseudo='04 - Agent Entrepôt SWAP')


class AgentEntrepotSwapOpenTickets(AgentEntrepotSwapBaseViewSet):
    def get_queryset(self):
        return self.get_queryset_base() \
            .filter(~Q(statut=2)) \
            .all()


class AgentEntrepotSwapClosedAndUnread(AgentEntrepotSwapBaseViewSet):
    def get_queryset(self):
        return self.get_queryset_base() \
            .filter(Q(statut=2)) \
            .all()


@login_required
def agent_entrepot(request):
    open_tickets = AgentEntrepotSwapOpenTickets().get_queryset()

    closed_unread = AgentEntrepotSwapClosedAndUnread().get_queryset()

    context = {
        'openTicketList': open_tickets,
        'openTicketCounter': open_tickets.count(),

        'closedUnread': closed_unread,
        'closedUnreadCounter': closed_unread.count(),
    }

    return render(request, 'api/agent_entrepot.html', context)


# AGENT STATION

class AgentStationBaseViewSet(BaseViewSet):
    def get_queryset_base(self):
        return super().get_queryset_base() \
            .filter(admin__pseudo='07 - Agent Station')


class AgentStationOpenTickets(AgentStationBaseViewSet):
    def get_queryset(self):
        return self.get_queryset_base() \
            .filter(~Q(statut=2)) \
            .all()


class AgentStationClosedAndUnread(AgentStationBaseViewSet):
    def get_queryset(self):
        return self.get_queryset_base() \
            .filter(Q(statut=2)) \
            .all()


@login_required
def agent_station(request):
    open_tickets = AgentStationOpenTickets().get_queryset()

    closed_unread = AgentStationClosedAndUnread().get_queryset()

    context = {
        'openTicketList': open_tickets,
        'openTicketCounter': open_tickets.count(),

        'closedUnread': closed_unread,
        'closedUnreadCounter': closed_unread.count(),
    }

    return render(request, 'api/agent_station.html', context)


# NOT AGENTS

class NonAgentTicketsBaseViewSet(BaseViewSet):
    AGENT_PSEUDOS_EXCLUDED = [
        '01 - Agent Technique SWAP',
        '02 - Agent Administratif SWAP',
        '03 - Agent Vérification SWAP',
        '04 - Agent Entrepôt SWAP',
        '05 - Agent Moteur BS/Honda',
        '06 - Agent Création Pièces',
        '07 - Agent Station',
        '09 - Agent Technique Pro',
        'Abdurakhman',
        'Kirill',
        'Igor',
        'Nikita',
        'Vyacheslav'
    ]


    def get_queryset_base(self):
        return super().get_queryset_base() \
            .filter(~Q(admin__pseudo__in=self.AGENT_PSEUDOS_EXCLUDED)) \
            .exclude(ticketcontrat__contrat__id__in=CONTRACTS_EXCLUDED_IDS)


class AllTicketsNotForAgents(NonAgentTicketsBaseViewSet):
    def get_queryset(self):
        return self.get_queryset_base() \
            .filter(~Q(statut=2)) \
            .all()


class AllTicketsNotForAgentsClosedUnread(NonAgentTicketsBaseViewSet):
    def get_queryset(self):
        return self.get_queryset_base() \
            .filter(Q(statut=2)) \
            .all()


@login_required
def other_admins(request):
    open_tickets = AllTicketsNotForAgents().get_queryset()

    closed_unread = AllTicketsNotForAgentsClosedUnread().get_queryset()

    context = {
        'openTicketList': open_tickets,
        'openTicketCounter': open_tickets.count(),

        'closedUnread': closed_unread,
        'closedUnreadCounter': closed_unread.count(),
    }

    return render(request, 'api/other_admins.html', context)


# SIMPLE TICKETS

class TicketTypeBaseViewSet(BaseViewSet):
    def get_queryset_base(self, ticket_type_id):
        return super().get_queryset_base() \
            .filter(~Q(statut=2), type__id=ticket_type_id) \
            .order_by('id')


class DemandeDeNoticeUniquementViewSet(TicketTypeBaseViewSet):
    def get_queryset(self):
        return self.get_queryset_base(1).all()


class RenseignementTechniqueViewSet(TicketTypeBaseViewSet):
    def get_queryset(self):
        return self.get_queryset_base(4).all()


class DemandeInfosSurMachineViewSet(TicketTypeBaseViewSet):
    def get_queryset(self):
        return self.get_queryset_base(22).all()


class ModerationEnregistrementMachineViewSet(TicketTypeBaseViewSet):
    def get_queryset(self):
        return self.get_queryset_base(51).all()


class ModerationEnregistrementMachineClientsBCMViewSet(TicketTypeBaseViewSet):
    def get_queryset(self):
        return self.get_queryset_base(71).all()


@login_required
def simple_tickets(request):
    demande_notice_tickets = DemandeDeNoticeUniquementViewSet().get_queryset()
    renseignement_technique_tickets = RenseignementTechniqueViewSet().get_queryset()
    demande_infos_machine_tickets = DemandeInfosSurMachineViewSet().get_queryset()
    moderation_enregistrement_tickets = ModerationEnregistrementMachineViewSet().get_queryset()
    moderation_enregistrement_BCM_tickets = ModerationEnregistrementMachineClientsBCMViewSet().get_queryset()

    context = {
        'demandeNotice': demande_notice_tickets,
        'demandeNoticeCounter': demande_notice_tickets.count(),

        'renseignementTechnique': renseignement_technique_tickets,
        'renseignementTechniqueCounter': renseignement_technique_tickets.count(),

        'demandeInfosMachine': demande_infos_machine_tickets,
        'demandeInfosMachineCounter': demande_infos_machine_tickets.count(),

        'moderationEnregistrement': moderation_enregistrement_tickets,
        'moderationEnregistrementCounter': moderation_enregistrement_tickets.count(),

        'moderationEnregistrementBCM': moderation_enregistrement_BCM_tickets,
        'moderationEnregistrementBCMCounter': moderation_enregistrement_BCM_tickets.count(),

    }

    return render(request, 'api/simple_tickets.html', context)


# TICKETS HIVERNAGE

class TicketHivernageBaseViewSet(BaseViewSet):
    def get_queryset_base(self, status_ids):
        return super().get_queryset_base() \
            .filter(~Q(statut=2), type_id=45) \
            .exclude(statut=2) \
            .filter(ticket_status__id__in=status_ids)


class TicketHivernageStationClientConvenirDate(TicketHivernageBaseViewSet):
    def get_queryset(self):
        return self.get_queryset_base([30]).all()


class TicketHivernageDateRendezVousConvenue(TicketHivernageBaseViewSet):
    def get_queryset(self):
        return self.get_queryset_base([22]).all()


class TicketHivernageStationDiagnosticMachine(TicketHivernageBaseViewSet):
    def get_queryset(self):
        return self.get_queryset_base([23]).all()


class TicketHivernageStationChoisirKitPieces(TicketHivernageBaseViewSet):
    def get_queryset(self):
        return self.get_queryset_base([25]).all()


class TicketHivernageEntretienMachineEnCours(TicketHivernageBaseViewSet):
    def get_queryset(self):
        return self.get_queryset_base([26]).all()


class TicketHivernageEntretienPasse(TicketHivernageBaseViewSet):
    def get_queryset(self):
        return self.get_queryset_base([26]).all()


@login_required
def tickets_hivernage(request):
    convenir_date_tickets = TicketHivernageStationClientConvenirDate().get_queryset()
    date_rdv_convenue_tickets = TicketHivernageDateRendezVousConvenue().get_queryset()
    station_diag_machine_tickets = TicketHivernageStationDiagnosticMachine().get_queryset()
    station_choisir_pieces_tickets = TicketHivernageStationChoisirKitPieces().get_queryset()
    entretien_encours_tickets = TicketHivernageEntretienMachineEnCours().get_queryset()
    entretien_passe_tickets = TicketHivernageEntretienPasse().get_queryset()

    context = {
        'convenirDate': convenir_date_tickets,
        'convenirDateCounter': convenir_date_tickets.count(),

        'dateRdvConvenue': date_rdv_convenue_tickets,
        'dateRdvConvenueCounter': date_rdv_convenue_tickets.count(),

        'stationDiagMachine': station_diag_machine_tickets,
        'stationDiagMachineCounter': station_diag_machine_tickets.count(),

        'stationChoisirPieces': station_choisir_pieces_tickets,
        'stationChoisirPiecesCounter': station_choisir_pieces_tickets.count(),

        'entretienEncours': entretien_encours_tickets,
        'entretienEncoursCounter': entretien_encours_tickets.count(),

        'entretienPasse': entretien_passe_tickets,
        'entretienPasseCounter': entretien_passe_tickets.count(),

    }

    return render(request, 'api/tickets_hivernage.html', context)


# RU SHOWER CABINS

class ShowerCabinBaseViewSet(BaseViewSet):
    def get_queryset_base(self):
        SHOWER_CONTRACT_IDS = [64, 71]
        return super().get_queryset_base() \
            .filter(ticketcontrat__contrat__id__in=SHOWER_CONTRACT_IDS) \
            .all()


class ShowerCabinOpenTickets(ShowerCabinBaseViewSet):
    def get_read_filter(self):
        return Q(read=0) | Q(read=1)

    def get_queryset(self):
        return self.get_queryset_base() \
            .filter(~Q(statut=2)) \
            .all()


@login_required
def ru_shower(request):
    open_tickets = ShowerCabinOpenTickets().get_queryset()

    context = {
        'openTicketList': open_tickets,
        'openTicketCounter': open_tickets.count(),
    }

    return render(request, 'api/ru_shower.html', context)
