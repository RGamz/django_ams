from django.urls import include, path
from rest_framework import routers
from api.views import (
    AgentVerificationOpenTicketsViewSet,
    AgentVerificationClosedAndUnreadViewSet,
    AgentVerificationSuntekViewSet,
    AgentVerificationTeractViewSet,
    AgentAdministratifOpenTicketsViewSet,
    AgentAdministratifClosNonLus,
    AgentAdministratifSimpleUnclosed,
    AgentAdministratifSuntek,
    AgentAdministratifTeract,
    AgentAdministratifModerateReparation,
    AgentAdministratifDemandeGarantie,
    AgentAdministratifModerateDDG,
    AgentAdministratifPiecesLivraison,
    AgentAdministratifReparationReussie,
    AgentAdministratifAnr,
    AgentAdministratifMobilierJardin,
    AgentTechniqueOpenTickets,
    AgentTechniqueRiders,
    AgentTechniqueDaye,
    AgentTechniqueFeider,
    AgentTechniqueGenerators,
    AgentTechniqueBronzeContracts,
    AgentTechniqueModerateDDG,
    AgentTechniqueReused,
    AgentTechniqueMTD,
    AgentTechniqueKingfisher,
    AgentTechniqueSuntek,
    AgentTechniqueLeroy,
    AgentTechniqueKaufland,
    AgentTechniqueClosNonLus,
    AgentTechniqueSimpleUnclosed,
    AgentTechniqueProOpenTickets,
    AgentTechniqueProRiders,
    AgentTechniqueProDaye,
    AgentTechniqueProFeider,
    AgentTechniqueProGenerators,
    AgentTechniqueProBronzeContracts,
    AgentTechniqueProModerateDDG,
    AgentTechniqueProReused,
    AgentTechniqueProMTD,
    AgentTechniqueProKingfisher,
    AgentTechniqueProSuntek,
    AgentTechniqueProLeroy,
    AgentTechniqueProKaufland,
    AgentTechniqueProClosNonLus,
    AgentTechniqueProSimpleUnclosed,
    AgentHorsGarantieOpenViewSet,
    AgentHorsGarantieModerationDDG,
    AgentHorsGarantieAttenteDevisStation,
    AgentHorsGarantieModerationDevisStation,
    AgentHorsGarantieAttenteDevisClient,
    AgentHorsGarantieAttenteAcceptationClient,
    AgentHorsGarantieDevisAccepteParClient,
    AgentHorsGarantieAttentePaiementPanier,
    AgentHorsGarantiePrestationNonAboutie,
    AgentHorsGarantieReparationEffectuee,
    AgentHorsGarantieTransportRetourModeration,
    AgentHorsGarantieTicketsClosedUnread,
    AgentHorsGarantieTicketsWithoutSwapAcademy,
    AgentMotorOpenTickets,
    AgentMotorClosedUnread,
    AgentCreationPiecesOpenTickets, AgentCreationPiecesClosedAndUnread,
    AgentEntrepotSwapOpenTickets, AgentEntrepotSwapClosedAndUnread,
    AgentStationOpenTickets, AgentStationClosedAndUnread,
    AllTicketsNotForAgents, AllTicketsNotForAgentsClosedUnread,
    DemandeDeNoticeUniquementViewSet, RenseignementTechniqueViewSet,
    DemandeInfosSurMachineViewSet, ModerationEnregistrementMachineViewSet,
    ModerationEnregistrementMachineClientsBCMViewSet,
    TicketHivernageStationClientConvenirDate, TicketHivernageDateRendezVousConvenue,
    TicketHivernageStationDiagnosticMachine, TicketHivernageStationChoisirKitPieces,
    TicketHivernageEntretienMachineEnCours, TicketHivernageEntretienPasse,
    ShowerCabinOpenTickets
)

router = routers.DefaultRouter()

# AGENT VERIFICATION
router.register(r'agent_verification/open',
                AgentVerificationOpenTicketsViewSet,
                basename='agentverificationopen')

router.register(r'agent_verification/closed_and_unread', 
                AgentVerificationClosedAndUnreadViewSet, 
                basename='agentverificationclosedandunread')

router.register(r'agent_verification/suntek',
                AgentVerificationSuntekViewSet,
                basename='agentverificationsuntek')

router.register(r'agent_verification/teract',
                AgentVerificationTeractViewSet,
                basename='agentverificationteract')

# ---------ADMIN-------------

router.register(r'agent_administratif/open',
                AgentAdministratifOpenTicketsViewSet,
                basename='agentadministratifopen')

router.register(r'agent_administratif/closed_non_lu',
                AgentAdministratifClosNonLus,
                basename='agentadministratifclosnonlus')

router.register(r'agent_administratif/simple_unclosed',
                AgentAdministratifSimpleUnclosed,
                basename='agentadministratifsimpleunclosed')

router.register(r'agent_administratif/suntek',
                AgentAdministratifSuntek,
                basename='agentadministratifsuntek')

router.register(r'agent_administratif/teract',
                AgentAdministratifTeract,
                basename='agentadministratifteract')

router.register(r'agent_administratif/moderate_reparation',
                AgentAdministratifModerateReparation,
                basename='agentadministratifmoderatereparation')

router.register(r'agent_administratif/demande_garantie',
                AgentAdministratifDemandeGarantie,
                basename='agentadministratifdemandegarantie')

router.register(r'agent_administratif/ddg',
                AgentAdministratifModerateDDG,
                basename='agentadministratifmoderateddg')

router.register(r'agent_administratif/pieces_livraison',
                AgentAdministratifPiecesLivraison,
                basename='agentadministratifpieceslivraison')

router.register(r'agent_administratif/reparation_reussie',
                AgentAdministratifReparationReussie,
                basename='agentadministratifreparationreussie')

router.register(r'agent_administratif/anr',
                AgentAdministratifAnr,
                basename='agentadministratifanr')

router.register(r'agent_administratif/mobilier_jardin',
                AgentAdministratifMobilierJardin,
                basename='agentadministratifmobilierjardin')

# ---------TECH-------------

router.register(r'agent_technique/open',
                AgentTechniqueOpenTickets,
                basename='agenttechniqueopentickets')

router.register(r'agent_technique/riders',
                AgentTechniqueRiders,
                basename='agenttechniqueriders')

router.register(r'agent_technique/daye',
                AgentTechniqueDaye,
                basename='agenttechniquedaye')

router.register(r'agent_technique/feider',
                AgentTechniqueFeider,
                basename='agenttechniquefeider')

router.register(r'agent_technique/generators',
                AgentTechniqueGenerators,
                basename='agenttechniquegenerators')

router.register(r'agent_technique/bronze',
                AgentTechniqueBronzeContracts,
                basename='agenttechniquebronze')

router.register(r'agent_technique/ddg',
                AgentTechniqueModerateDDG,
                basename='agenttechniquemoderateddg')

router.register(r'agent_technique/reused',
                AgentTechniqueReused,
                basename='agenttechniquereused')

router.register(r'agent_technique/mtd',
                AgentTechniqueMTD,
                basename='agenttechniquemtd')

router.register(r'agent_technique/kingfisher',
                AgentTechniqueKingfisher,
                basename='agenttechniquekingfisher')

router.register(r'agent_technique/suntek',
                AgentTechniqueSuntek,
                basename='agenttechniquesuntek')

router.register(r'agent_technique/leroy',
                AgentTechniqueLeroy,
                basename='agenttechniqueleroy')

router.register(r'agent_technique/kaufland',
                AgentTechniqueKaufland,
                basename='agenttechniquekaufland')

router.register(r'agent_technique/clos_non_lu',
                AgentTechniqueClosNonLus,
                basename='agenttechniqueclosnonlus')

router.register(r'agent_technique/simple',
                AgentTechniqueSimpleUnclosed,
                basename='agenttechniquesimple')


# ---------TECH PRO-------------

router.register(r'agent_technique_pro/open',
                AgentTechniqueProOpenTickets,
                basename='agenttechniqueproopentickets')

router.register(r'agent_technique_pro/riders',
                AgentTechniqueProRiders,
                basename='agenttechniqueproriders')

router.register(r'agent_technique_pro/daye',
                AgentTechniqueProDaye,
                basename='agenttechniqueprodaye')

router.register(r'agent_technique_pro/feider',
                AgentTechniqueProFeider,
                basename='agenttechniqueprofeider')

router.register(r'agent_technique_pro/generators',
                AgentTechniqueProGenerators,
                basename='agenttechniqueprogenerators')

router.register(r'agent_technique_pro/bronze',
                AgentTechniqueProBronzeContracts,
                basename='agenttechniqueprobronze')

router.register(r'agent_technique_pro/ddg',
                AgentTechniqueProModerateDDG,
                basename='agenttechniquepromoderateddg')

router.register(r'agent_technique_pro/reused',
                AgentTechniqueProReused,
                basename='agenttechniqueproreused')

router.register(r'agent_technique_pro/mtd',
                AgentTechniqueProMTD,
                basename='agenttechniquepromtd')

router.register(r'agent_technique_pro/kingfisher',
                AgentTechniqueProKingfisher,
                basename='agenttechniqueprokingfisher')

router.register(r'agent_technique_pro/suntek',
                AgentTechniqueProSuntek,
                basename='agenttechniqueprosuntek')

router.register(r'agent_technique_pro/leroy',
                AgentTechniqueProLeroy,
                basename='agenttechniqueproleroy')

router.register(r'agent_technique_pro/kaufland',
                AgentTechniqueProKaufland,
                basename='agenttechniqueprokaufland')

router.register(r'agent_technique_pro/clos_non_lu',
                AgentTechniqueProClosNonLus,
                basename='agenttechniqueproclosnonlus')

router.register(r'agent_technique_pro/simple',
                AgentTechniqueProSimpleUnclosed,
                basename='agenttechniqueprosimple')

#  -----------OUT OF WARRANTY-------------

router.register(r'agent_hors_garantie/open',
                AgentHorsGarantieOpenViewSet,
                basename='agenthorsgarantieopenviewset')

router.register(r'agent_hors_garantie/ddg',
                AgentHorsGarantieModerationDDG,
                basename='agenthorsgarantieddg')

router.register(r'agent_hors_garantie/attente_devis',
                AgentHorsGarantieAttenteDevisStation,
                basename='agenthorsgarantieattentedevis')

router.register(r'agent_hors_garantie/moderation_devis_station',
                AgentHorsGarantieModerationDevisStation,
                basename='agenthorsgarantiemoderationdevisstation')

router.register(r'agent_hors_garantie/attente_devis_client',
                AgentHorsGarantieAttenteDevisClient,
                basename='agenthorsgarantieattentedevisclient')

router.register(r'agent_hors_garantie/attente_acceptation_client',
                AgentHorsGarantieAttenteAcceptationClient,
                basename='agenthorsgarantieattenteacceptationclient')

router.register(r'agent_hors_garantie/devis_accepte_client',
                AgentHorsGarantieDevisAccepteParClient,
                basename='agenthorsgarantiedevisaccepteclient')

router.register(r'agent_hors_garantie/attente_paiement_panier',
                AgentHorsGarantieAttentePaiementPanier,
                basename='agenthorsgarantieattentepaiementpanier')

router.register(r'agent_hors_garantie/prestation_non_aboutie',
                AgentHorsGarantiePrestationNonAboutie,
                basename='agenthorsgarantieprestationnonaboutie')

router.register(r'agent_hors_garantie/reparation_effectuee',
                AgentHorsGarantieReparationEffectuee,
                basename='agenthorsgarantiereparationeffectuee')

router.register(r'agent_hors_garantie/transport_retour_moderation',
                AgentHorsGarantieTransportRetourModeration,
                basename='agenthorsgarantietransportretourmoderation')

router.register(r'agent_hors_garantie/closed_unread',
                AgentHorsGarantieTicketsClosedUnread,
                basename='agenthorsgarantieticketsclosedunread')

router.register(r'agent_hors_garantie/tickets_without_swap',
                AgentHorsGarantieTicketsWithoutSwapAcademy,
                basename='agenthorsgarantieticketswithoutswap')


# --------AGENT MOTEUR-----------
router.register(r'agent_moteur/open_tickets',
                AgentMotorOpenTickets,
                basename='agentmoteuropentickets')

router.register(r'agent_moteur/clos_non_lus',
                AgentMotorClosedUnread,
                basename='agentmoteurclosedandunread')


# --------AGENT PIECES---------
router.register(r'agent_creation_pieces/open_tickets',
                AgentCreationPiecesOpenTickets,
                basename='agentcreationpiecesopentickets')

router.register(r'agent_creation_pieces/closed_and_unread',
                AgentCreationPiecesClosedAndUnread,
                basename='agentcreationpiecesclosedandunread')

# --------AGENT ENTREPOT -------------
router.register(r'agent_entrepot_swap/open_tickets',
                AgentEntrepotSwapOpenTickets,
                basename='agententrepotswapopentickets')

router.register(r'agent_entrepot_swap/closed_and_unread',
                AgentEntrepotSwapClosedAndUnread,
                basename='agententrepotswapclosedandunread')

# -------------AGENT STATION------------
router.register(r'agent_station/open_tickets',
                AgentStationOpenTickets,
                basename='agentstationopentickets')

router.register(r'agent_station/closed_and_unread',
                AgentStationClosedAndUnread,
                basename='agentstationclosedandunread')

# -------------OTHER ADMINS ----------------
router.register(r'tickets_not_for_agents/open_tickets',
                AllTicketsNotForAgents,
                basename='allticketsnotforagents')

router.register(r'tickets_not_for_agents/closed_unread',
                AllTicketsNotForAgentsClosedUnread,
                basename='allticketsnotforagentsclosedunread')

# -----------SIMPLE TICKETS-------------------
router.register(r'tickets_simples/demande_notice_uniquement',
                DemandeDeNoticeUniquementViewSet,
                basename='demandenoticeuniquement')

router.register(r'tickets_simples/renseignement_technique',
                RenseignementTechniqueViewSet,
                basename='renseignementtechnique')

router.register(r'tickets_simples/demande_infos_machine',
                DemandeInfosSurMachineViewSet,
                basename='demandeinfossurmachine')

router.register(r'tickets_simples/moderation_enregistrement_machine',
                ModerationEnregistrementMachineViewSet,
                basename='moderationenregistrementmachine')

router.register(r'tickets_simples/moderation_enregistrement_machine_clients_bcm',
                ModerationEnregistrementMachineClientsBCMViewSet,
                basename='moderationenregistrementmachineclientsbcm')

# --------------HIVERNAGE------------------
router.register(r'tickets_hivernage/station_client_convenir_date',
                TicketHivernageStationClientConvenirDate,
                basename='tickethivernagestationclientconvenirdat')

router.register(r'tickets_hivernage/date_rendez_vous_convenue',
                TicketHivernageDateRendezVousConvenue,
                basename='tickethivernagedaterendezvousconvenue')

router.register(r'tickets_hivernage/station_diagnostic_machine',
                TicketHivernageStationDiagnosticMachine,
                basename='tickethivernagestationdiagnosticmachine')

router.register(r'tickets_hivernage/station_choisir_kit_pieces',
                TicketHivernageStationChoisirKitPieces,
                basename='tickethivernagestationchoisirkitpieces')

router.register(r'tickets_hivernage/entretien_machine_en_cours',
                TicketHivernageEntretienMachineEnCours,
                basename='tickethivernageentretienmachineencours')

router.register(r'tickets_hivernage/entretien_machine_passe',
                TicketHivernageEntretienPasse,
                basename='tickethivernageentretienpasse')

# -------------RU SHOWER ---------------
router.register(r'ru_shower_cabins/open',
                ShowerCabinOpenTickets,
                basename='showercabinsopentickets')

urlpatterns = router.urls
