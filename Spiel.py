# importieren von Libraries (d.h. Baukästen)
import pygame
import pygame_gui
from pygame import mixer # für Musik
import math # für Aufrunden
from types import SimpleNamespace # für die Variable döner
import random # für die Bestellungen

# Spielkonstanten zum Rumexperimentieren (lateinische Großbuchstaben, Ä/ß gehen nicht)
STARTKAPITAL = 4600

LADEN1_MIETE = 150
LADEN1_BEWERTUNGSFAKTOR = 1 # Wie stark sich Bewertungen auf die Nachfrage (d.h. Kunden pro Tag) auswirken
LADEN1_NACHFRAGEFAKTOR = 5 # entspricht Kunden pro Tag
LADEN1_FALAFELFAKTOR = 0.1 # wie wahrscheinlich ein Kunde Falafel statt Fleisch will 

LADEN2_MIETE = 450
LADEN2_BEWERTUNGSFAKTOR = 2
LADEN2_NACHFRAGEFAKTOR = 12
LADEN2_FALAFELFAKTOR = 0.2

LADEN3_MIETE = 1200
LADEN3_BEWERTUNGSFAKTOR = 4
LADEN3_NACHFRAGEFAKTOR = 32
LADEN3_FALAFELFAKTOR = 0.35

BROTGRILL1_KOSTEN = 800
BROTGRILL2_KOSTEN = 2300
BROTGRILL3_KOSTEN = 3200

SPIESS_PRO_DOENER = 0.15 # kg
KALB_KOSTEN = 12 # pro kg
HUHN_KOSTEN = 5 # pro kg
HACK_KOSTEN = 2 # pro kg
FALAFEL_KOSTEN = 0.08 # pro St.
FALAFEL_PRO_DOENER = 4 # St.
SALAT_KOSTEN = 0.005 # pro g
SALAT_PRO_DOENER = 10 # g
TOMATE_KOSTEN = 0.1 # pro St.
TOMATE_PRO_DOENER = 0.5 # St.
ZWIEBEL_KOSTEN = 0.02 # pro St.
ZWIEBEL_PRO_DOENER = 0.5 # St.
GURKE_KOSTEN = 0.1 # pro St.
GURKE_PRO_DOENER = 0.1 # St.
WEISSKOHL_KOSTEN = 0.001 # pro g 
WEISSKOHL_PRO_DOENER = 20 # g
ROTKOHL_KOSTEN = 0.003 # pro g
ROTKOHL_PRO_DOENER = 10 # g
FETA_KOSTEN = 0.01 # pro g
FETA_PRO_DOENER = 20 # g
JOGHURTSOSSE_KOSTEN = 0.001 # pro g
JOGHURTSOSSE_PRO_DOENER = 30 # g
KNOBLAUCHSOSSE_KOSTEN = 0.001 # pro g
KNOBLAUCHSOSSE_PRO_DOENER = 30 # g
SCHARFESOSSE_KOSTEN = 0.001 # pro g
SCHARFESOSSE_PRO_DOENER = 30 # g
BROT_KOSTEN = 0.25 # pro St.
BROT_PRO_DOENER = 1 # St.

SPIESS_ZEIT_VERKOKELT = 30 # Sekunden bis der Spieß verkokelt ist
SPIESS_ZEIT_GEGART = 9

BROTGRILL1_BROT_ZEIT_VERKOKELT = 7 # Sekunden bis das Brot verkokelt ist
BROTGRILL1_BROT_ZEIT_GEGART = 4
BROTGRILL2_BROT_ZEIT_VERKOKELT = 5
BROTGRILL2_BROT_ZEIT_GEGART = 2
BROTGRILL3_BROT_ZEIT_VERKOKELT = 3
BROTGRILL3_BROT_ZEIT_GEGART = 1

ZEIT_BIS_NEUER_KUNDE = 7 # Mittelwert (Gaussche Verteilung)

GEDULD = 20

class Spiel:
    def __init__(self): # Konstruktor
        pygame.init() # initiiert alle pygame Module
        self.fenster = pygame.display.set_mode((1920, 1080), pygame.FULLSCREEN) # Fenstergröße (abhängig von self.fenster_größe) + Vollbild
        pygame.display.set_caption("Döner Simulator") # Fenstername
        self.fps = pygame.time.Clock() # Uhr für FPS
        self.spiel_läuft = True # Spiel-läuft-Status (braucht man fürs Beenden)

        self.gui = pygame_gui.UIManager( # "GUI-Manager" (GUI initiieren)
            (1920,1080), # Fenstergröße
            theme_path="Python/Döner Simulator/Layout.json" # Theme (Farben, Aussehen, etc.)
        )
        
        self.gui.preload_fonts([ # Fehlermeldungen sagen iwie immer, dass man das braucht (ka wieso, ist einfach aus den Fehlermeldungen kopiert)
            {
                'name': 'Inter', 
                'point_size': 30, 
                'style': 'regular', 
                'antialiased': '1',
                'path': 'Python/Döner Simulator/Schriftarten/Inter.ttf'
            },
            {
                'name': 'Inter', 
                'point_size': 20, 
                'style': 'regular', 
                'antialiased': '1',
                'path': 'Python/Döner Simulator/Schriftarten/Inter.ttf'
            },
            {
                'name': 'Ramadhan Mubarok Regular',
                'point_size': 50,
                'style': 'regular',
                'antialiased': '1',
                'path': 'Python/Döner Simulator/Schriftarten/Ramadhan Mubarok.otf'
            },
            {
                'name': 'Ramadhan Mubarok Regular',
                'point_size': 100,
                'style': 'regular',
                'antialiased': '1',
                'path': 'Python/Döner Simulator/Schriftarten/Ramadhan Mubarok.otf'
            }
        ])
        
        # Mauszeiger
        self.bild_mauszeiger_drücken = pygame.image.load("Python/Döner Simulator/Bilder/mauszeiger.png").convert_alpha()
        self.mauszeiger = pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_ARROW)
        self.mauszeiger_drücken = pygame.cursors.Cursor((0, 0), self.bild_mauszeiger_drücken)

        # Variablen
        self.kapital = STARTKAPITAL
        self.nachfragefaktor = 0
        self.nachfragefaktor_initial = 0 # Initial heißt immer am Anfang der Runde / des Tages
        self.kunden_für_den_tag = 0
        self.tag = 1 # für Miete

        self.laden1 = False
        self.laden2 = False
        self.laden3 = False

        self.brotgrill1_gekauft = False
        self.brotgrill2_gekauft = False
        self.brotgrill3_gekauft = False

        self.spießgewicht_gewicht = 0
        self.spieß_kalb_anteil = 70
        self.spieß_huhn_anteil = 0
        self.spieß_hack_anteil = 30
        self.falafel_anzahl = 0
        self.salat_anzahl = 0
        self.tomate_anzahl = 0
        self.zwiebel_anzahl = 0
        self.gurke_anzahl = 0
        self.weißkohl_anzahl = 0
        self.rotkohl_anzahl = 0
        self.feta_anzahl = 0
        self.joghurtsoße_anzahl = 0
        self.knoblauchsoße_anzahl = 0
        self.scharfesoße_anzahl = 0
        self.brot_anzahl = 0

        self.spießgewicht_gewicht_initial = 0
        self.falafel_anzahl_initial = 0
        self.salat_anzahl_initial = 0
        self.tomate_anzahl_initial = 0
        self.zwiebel_anzahl_initial = 0
        self.gurke_anzahl_initial = 0
        self.weißkohl_anzahl_initial = 0
        self.rotkohl_anzahl_initial = 0
        self.feta_anzahl_initial = 0
        self.joghurtsoße_anzahl_initial = 0
        self.knoblauchsoße_anzahl_initial = 0
        self.scharfesoße_anzahl_initial = 0

        self.dönerpreis = 0
        self.kosten_pro_döner = 0
        self.zutaten_einkauf_kosten = 0

        self.spieß_gargrad = "roh"
        self.fleischteller = "" # leer / Gargrad
        self.in_der_hand = [0, "", ""] # Stückzahl, Name, optional Gargrad
        self.brot_in_der_hand = False
        self.brot_im_brotgrill = 0
        self.brot_gargrad = "roh"
        self.brotgrill_zeit_verkokelt = 0
        self.brotgrill_zeit_gegart = 0

        self.döner_modus = False # soll in_der_hand überschreiben
        self.döner = SimpleNamespace(
            brot = "", # Gargrad ("" heißt False)
            fleisch = "", # Gargrad ("" heißt False)
            falafel = False,
            salat = False,
            tomate = False,
            zwiebel = False,
            gurke = False,
            rotkohl = False,
            weißkohl = False,
            feta = False,
            joghurtsoße = False,
            knoblauchsoße = False,
            scharfesoße = False
        )

        self.kunde_anwesend = False
        self.ladenmenü_kunde_dialog_erstellt = False
        self.aktueller_kunde = None
        self.bewertungen_summe = 0
        self.bewertungen_anzahl = 0 
        self.bewertung = 0 # Durchschnitt

        self.zeit_läuft = False
        self.ingame_stunde = 8
        self.ingame_minute = 0
        self.spieß_zeit = 0
        self.brotgrill_zeit = 0
        self.kunde_zeit = 0
        self.geduld_zeit = 0
        self.gui_starten = None # siehe button_kill_probieren()
        self.gui_pausieren = None
        self.gui_weiter = None

        self.sekunden_tick = pygame.USEREVENT + 1 # fügt ein neues, benutzerdefiniertes (-> USER) Event zu Pygame hinzu
        pygame.time.set_timer(self.sekunden_tick, 1000) # timed alle 1000 Millisekunden

        # Bilder vorladen
        self.start_bild = pygame.image.load("Python/Döner Simulator/Bilder/icon.png").convert_alpha() 
        pygame.display.set_icon(self.start_bild) # Fenstericon
        self.bild_laden1 = pygame.image.load("Python/Döner Simulator/Bilder/laden1.png").convert() # convert optimiert das bild -> kürzere Ladezeit
        self.bild_laden2 = pygame.image.load("Python/Döner Simulator/Bilder/laden2.png").convert()
        self.bild_laden3 = pygame.image.load("Python/Döner Simulator/Bilder/laden3.png").convert()

        self.bild_theke = pygame.image.load("Python/Döner Simulator/Bilder/theke.png")
        self.bild_laden1_hintergrund = pygame.image.load("Python/Döner Simulator/Bilder/laden1_hintergrund.png").convert_alpha() # convert_alpha berücksichtigt halbtransparente Pixel
        self.bild_laden2_hintergrund = pygame.image.load("Python/Döner Simulator/Bilder/laden2_hintergrund.png").convert_alpha()
        self.bild_laden3_hintergrund = pygame.image.load("Python/Döner Simulator/Bilder/laden3_hintergrund.png").convert_alpha()

        self.bild_spieß_gegart = pygame.image.load("Python/Döner Simulator/Bilder/spieß_gegart.png").convert_alpha()
        self.bitmap_spieß_gegart = pygame.mask.from_surface(self.bild_spieß_gegart)  # Erstellt eine Bitmap (0: transparent/1: nicht transparent), fürs Hovern
        self.element_spieß_gegart = self.element_zuschneiden(self.bild_spieß_gegart, self.bitmap_spieß_gegart) # returned einen SimpleNamespace
        self.element_spieß_gegart_rechteck = self.element_spieß_gegart.cropped.get_rect(topleft=self.element_spieß_gegart.absatz) # baut das neue Rechteck (element_zuschneiden()) an die richtige Stelle (es ist ja jetzt kleiner geworden)

        self.bild_spieß_gegart_halb = pygame.image.load("Python/Döner Simulator/Bilder/spieß_gegart_halb.png").convert_alpha()
        self.bitmap_spieß_gegart_halb = pygame.mask.from_surface(self.bild_spieß_gegart_halb)
        self.element_spieß_gegart_halb = self.element_zuschneiden(self.bild_spieß_gegart_halb, self.bitmap_spieß_gegart_halb)
        self.element_spieß_gegart_halb_rechteck = self.element_spieß_gegart_halb.cropped.get_rect(topleft=self.element_spieß_gegart_halb.absatz)

        self.bild_spieß_roh = pygame.image.load("Python/Döner Simulator/Bilder/spieß_roh.png").convert_alpha()
        self.bitmap_spieß_roh = pygame.mask.from_surface(self.bild_spieß_roh)
        self.element_spieß_roh = self.element_zuschneiden(self.bild_spieß_roh, self.bitmap_spieß_roh)
        self.element_spieß_roh_rechteck = self.element_spieß_roh.cropped.get_rect(topleft=self.element_spieß_roh.absatz)

        self.bild_spieß_roh_halb = pygame.image.load("Python/Döner Simulator/Bilder/spieß_roh_halb.png").convert_alpha()
        self.bitmap_spieß_roh_halb = pygame.mask.from_surface(self.bild_spieß_roh_halb)
        self.element_spieß_roh_halb = self.element_zuschneiden(self.bild_spieß_roh_halb, self.bitmap_spieß_roh_halb)
        self.element_spieß_roh_halb_rechteck = self.element_spieß_roh_halb.cropped.get_rect(topleft=self.element_spieß_roh_halb.absatz)

        self.bild_spieß_verkokelt = pygame.image.load("Python/Döner Simulator/Bilder/spieß_verkokelt.png").convert_alpha()
        self.bitmap_spieß_verkokelt = pygame.mask.from_surface(self.bild_spieß_verkokelt)
        self.element_spieß_verkokelt = self.element_zuschneiden(self.bild_spieß_verkokelt, self.bitmap_spieß_verkokelt)
        self.element_spieß_verkokelt_rechteck = self.element_spieß_verkokelt.cropped.get_rect(topleft=self.element_spieß_verkokelt.absatz)
        
        self.bild_spieß_verkokelt_halb = pygame.image.load("Python/Döner Simulator/Bilder/spieß_verkokelt_halb.png").convert_alpha()
        self.bitmap_spieß_verkokelt_halb = pygame.mask.from_surface(self.bild_spieß_verkokelt_halb)
        self.element_spieß_verkokelt_halb = self.element_zuschneiden(self.bild_spieß_verkokelt_halb, self.bitmap_spieß_verkokelt_halb)
        self.element_spieß_verkokelt_halb_rechteck = self.element_spieß_verkokelt_halb.cropped.get_rect(topleft=self.element_spieß_verkokelt_halb.absatz)

        self.bild_fleischteller_leer = pygame.image.load("Python/Döner Simulator/Bilder/fleischteller_leer.png").convert_alpha()
        self.bitmap_fleischteller_leer = pygame.mask.from_surface(self.bild_fleischteller_leer)
        self.element_fleischteller_leer = self.element_zuschneiden(self.bild_fleischteller_leer, self.bitmap_fleischteller_leer)
        self.element_fleischteller_leer_rechteck = self.element_fleischteller_leer.cropped.get_rect(topleft=self.element_fleischteller_leer.absatz)

        self.bild_fleischteller_roh = pygame.image.load("Python/Döner Simulator/Bilder/fleischteller_roh.png").convert_alpha()
        self.bitmap_fleischteller_roh = pygame.mask.from_surface(self.bild_fleischteller_roh)
        self.element_fleischteller_roh = self.element_zuschneiden(self.bild_fleischteller_roh, self.bitmap_fleischteller_roh)
        self.element_fleischteller_roh_rechteck = self.element_fleischteller_roh.cropped.get_rect(topleft=self.element_fleischteller_roh.absatz)

        self.bild_fleischteller_gegart = pygame.image.load("Python/Döner Simulator/Bilder/fleischteller_gegart.png").convert_alpha()
        self.bitmap_fleischteller_gegart = pygame.mask.from_surface(self.bild_fleischteller_gegart)
        self.element_fleischteller_gegart = self.element_zuschneiden(self.bild_fleischteller_gegart, self.bitmap_fleischteller_gegart)
        self.element_fleischteller_gegart_rechteck = self.element_fleischteller_gegart.cropped.get_rect(topleft=self.element_fleischteller_gegart.absatz)

        self.bild_fleischteller_verkokelt = pygame.image.load("Python/Döner Simulator/Bilder/fleischteller_verkokelt.png").convert_alpha()
        self.bitmap_fleischteller_verkokelt = pygame.mask.from_surface(self.bild_fleischteller_verkokelt)
        self.element_fleischteller_verkokelt = self.element_zuschneiden(self.bild_fleischteller_verkokelt, self.bitmap_fleischteller_verkokelt)
        self.element_fleischteller_verkokelt_rechteck = self.element_fleischteller_verkokelt.cropped.get_rect(topleft=self.element_fleischteller_verkokelt.absatz)

        self.bild_falafel_voll = pygame.image.load("Python/Döner Simulator/Bilder/falafel_voll.png").convert_alpha()
        self.bitmap_falafel_voll = pygame.mask.from_surface(self.bild_falafel_voll)
        self.element_falafel = self.element_zuschneiden(self.bild_falafel_voll, self.bitmap_falafel_voll)
        self.element_falafel_rechteck = self.element_falafel.cropped.get_rect(topleft=self.element_falafel.absatz)

        self.bild_salat_voll = pygame.image.load("Python/Döner Simulator/Bilder/salat_voll.png").convert_alpha()
        self.bitmap_salat_voll = pygame.mask.from_surface(self.bild_salat_voll)
        self.element_salat = self.element_zuschneiden(self.bild_salat_voll, self.bitmap_salat_voll)
        self.element_salat_rechteck = self.element_salat.cropped.get_rect(topleft=self.element_salat.absatz)

        self.bild_tomate_voll = pygame.image.load("Python/Döner Simulator/Bilder/tomate_voll.png").convert_alpha()
        self.bitmap_tomate_voll = pygame.mask.from_surface(self.bild_tomate_voll)
        self.element_tomate = self.element_zuschneiden(self.bild_tomate_voll, self.bitmap_tomate_voll)
        self.element_tomate_rechteck = self.element_tomate.cropped.get_rect(topleft=self.element_tomate.absatz)

        self.bild_zwiebel_voll = pygame.image.load("Python/Döner Simulator/Bilder/zwiebel_voll.png").convert_alpha()
        self.bitmap_zwiebel_voll = pygame.mask.from_surface(self.bild_zwiebel_voll)
        self.element_zwiebel = self.element_zuschneiden(self.bild_zwiebel_voll, self.bitmap_zwiebel_voll)
        self.element_zwiebel_rechteck = self.element_zwiebel.cropped.get_rect(topleft=self.element_zwiebel.absatz)

        self.bild_gurke_voll = pygame.image.load("Python/Döner Simulator/Bilder/gurke_voll.png").convert_alpha()
        self.bitmap_gurke_voll = pygame.mask.from_surface(self.bild_gurke_voll)
        self.element_gurke = self.element_zuschneiden(self.bild_gurke_voll, self.bitmap_gurke_voll)
        self.element_gurke_rechteck = self.element_gurke.cropped.get_rect(topleft=self.element_gurke.absatz)

        self.bild_rotkohl_voll = pygame.image.load("Python/Döner Simulator/Bilder/rotkohl_voll.png").convert_alpha()
        self.bitmap_rotkohl_voll = pygame.mask.from_surface(self.bild_rotkohl_voll)
        self.element_rotkohl = self.element_zuschneiden(self.bild_rotkohl_voll, self.bitmap_rotkohl_voll)
        self.element_rotkohl_rechteck = self.element_rotkohl.cropped.get_rect(topleft=self.element_rotkohl.absatz)

        self.bild_weißkohl_voll = pygame.image.load("Python/Döner Simulator/Bilder/weißkohl_voll.png").convert_alpha()
        self.bitmap_weißkohl_voll = pygame.mask.from_surface(self.bild_weißkohl_voll)
        self.element_weißkohl = self.element_zuschneiden(self.bild_weißkohl_voll, self.bitmap_weißkohl_voll)
        self.element_weißkohl_rechteck = self.element_weißkohl.cropped.get_rect(topleft=self.element_weißkohl.absatz)

        self.bild_feta_voll = pygame.image.load("Python/Döner Simulator/Bilder/feta_voll.png").convert_alpha()
        self.bitmap_feta_voll = pygame.mask.from_surface(self.bild_feta_voll)
        self.element_feta = self.element_zuschneiden(self.bild_feta_voll, self.bitmap_feta_voll)
        self.element_feta_rechteck = self.element_feta.cropped.get_rect(topleft=self.element_feta.absatz)

        self.bild_joghurtsoße_voll = pygame.image.load("Python/Döner Simulator/Bilder/joghurtsoße_voll.png").convert_alpha()
        self.bitmap_joghurtsoße_voll = pygame.mask.from_surface(self.bild_joghurtsoße_voll)
        self.element_joghurtsoße = self.element_zuschneiden(self.bild_joghurtsoße_voll, self.bitmap_joghurtsoße_voll)
        self.element_joghurtsoße_rechteck = self.element_joghurtsoße.cropped.get_rect(topleft=self.element_joghurtsoße.absatz)

        self.bild_knoblauchsoße_voll = pygame.image.load("Python/Döner Simulator/Bilder/knoblauchsoße_voll.png").convert_alpha()
        self.bitmap_knoblauchsoße_voll = pygame.mask.from_surface(self.bild_knoblauchsoße_voll)
        self.element_knoblauchsoße = self.element_zuschneiden(self.bild_knoblauchsoße_voll, self.bitmap_knoblauchsoße_voll)
        self.element_knoblauchsoße_rechteck = self.element_knoblauchsoße.cropped.get_rect(topleft=self.element_knoblauchsoße.absatz)

        self.bild_scharfesoße_voll = pygame.image.load("Python/Döner Simulator/Bilder/scharfesoße_voll.png").convert_alpha()
        self.bitmap_scharfesoße_voll = pygame.mask.from_surface(self.bild_scharfesoße_voll)
        self.element_scharfesoße = self.element_zuschneiden(self.bild_scharfesoße_voll, self.bitmap_scharfesoße_voll)
        self.element_scharfesoße_rechteck = self.element_scharfesoße.cropped.get_rect(topleft=self.element_scharfesoße.absatz)

        self.bild_brot_voll = pygame.image.load("Python/Döner Simulator/Bilder/brot_voll.png").convert_alpha()
        self.bitmap_brot_voll = pygame.mask.from_surface(self.bild_brot_voll)
        self.element_brot_voll = self.element_zuschneiden(self.bild_brot_voll, self.bitmap_brot_voll)
        self.element_brot_voll_rechteck = self.element_brot_voll.cropped.get_rect(topleft=self.element_brot_voll.absatz)

        self.bild_brot_halb = pygame.image.load("Python/Döner Simulator/Bilder/brot_halb.png").convert_alpha()
        self.bitmap_brot_halb = pygame.mask.from_surface(self.bild_brot_halb)
        self.element_brot_halb = self.element_zuschneiden(self.bild_brot_halb, self.bitmap_brot_halb)
        self.element_brot_halb_rechteck = self.element_brot_halb.cropped.get_rect(topleft=self.element_brot_halb.absatz)

        self.bild_toaster = pygame.image.load("Python/Döner Simulator/Bilder/toaster.png").convert_alpha()
        self.bitmap_toaster = pygame.mask.from_surface(self.bild_toaster)
        self.element_toaster = self.element_zuschneiden(self.bild_toaster, self.bitmap_toaster)
        self.element_toaster_rechteck = self.element_toaster.cropped.get_rect(topleft=self.element_toaster.absatz)

        self.bild_optigrill = pygame.image.load("Python/Döner Simulator/Bilder/optigrill.png").convert_alpha()
        self.bitmap_optigrill = pygame.mask.from_surface(self.bild_optigrill)
        self.element_optigrill = self.element_zuschneiden(self.bild_optigrill, self.bitmap_optigrill)
        self.element_optigrill_rechteck = self.element_optigrill.cropped.get_rect(topleft=self.element_optigrill.absatz)

        self.bild_optigrill_groß = pygame.image.load("Python/Döner Simulator/Bilder/optigrill_groß.png").convert_alpha()
        self.bitmap_optigrill_groß = pygame.mask.from_surface(self.bild_optigrill_groß)
        self.element_optigrill_groß = self.element_zuschneiden(self.bild_optigrill_groß, self.bitmap_optigrill_groß)
        self.element_optigrill_groß_rechteck = self.element_optigrill_groß.cropped.get_rect(topleft=self.element_optigrill_groß.absatz)

        self.bild_döner_fleisch = pygame.image.load("Python/Döner Simulator/Bilder/döner_fleisch.png").convert_alpha()
        self.bild_döner_falafel = pygame.image.load("Python/Döner Simulator/Bilder/döner_falafel.png").convert_alpha()
        self.bild_döner_leer = pygame.image.load("Python/Döner Simulator/Bilder/döner_leer.png").convert_alpha()

        self.bild_kunde_1 = pygame.image.load("Python/Döner Simulator/Bilder/kunde_1.png").convert_alpha()
        self.bild_kunde_2 = pygame.image.load("Python/Döner Simulator/Bilder/kunde_2.png").convert_alpha()
        self.bild_kunde_3 = pygame.image.load("Python/Döner Simulator/Bilder/kunde_3.png").convert_alpha()
        self.bild_kunde_4 = pygame.image.load("Python/Döner Simulator/Bilder/kunde_4.png").convert_alpha()
        self.bild_kunde_5 = pygame.image.load("Python/Döner Simulator/Bilder/kunde_5.png").convert_alpha()
        self.bild_kunde_6 = pygame.image.load("Python/Döner Simulator/Bilder/kunde_6.png").convert_alpha()
        self.bild_kunde_7 = pygame.image.load("Python/Döner Simulator/Bilder/kunde_7.png").convert_alpha()
        self.bild_kunde_8 = pygame.image.load("Python/Döner Simulator/Bilder/kunde_8.png").convert_alpha()
        self.bild_kunde_9 = pygame.image.load("Python/Döner Simulator/Bilder/kunde_9.png").convert_alpha()
        self.bild_kunde_10 = pygame.image.load("Python/Döner Simulator/Bilder/kunde_10.png").convert_alpha()
        self.bild_kunde_11 = pygame.image.load("Python/Döner Simulator/Bilder/kunde_11.png").convert_alpha()
        self.bild_kunde_12 = pygame.image.load("Python/Döner Simulator/Bilder/kunde_12.png").convert_alpha()
        self.bild_kunde_13 = pygame.image.load("Python/Döner Simulator/Bilder/kunde_13.png").convert_alpha()
        self.bild_kunde_14 = pygame.image.load("Python/Döner Simulator/Bilder/kunde_14.png").convert_alpha()
        self.bild_kunde_15 = pygame.image.load("Python/Döner Simulator/Bilder/kunde_15.png").convert_alpha()
        self.bild_kunde_16 = pygame.image.load("Python/Döner Simulator/Bilder/kunde_16.png").convert_alpha()
        self.bild_kunde_17 = pygame.image.load("Python/Döner Simulator/Bilder/kunde_17.png").convert_alpha()
        self.bild_kunde_18 = pygame.image.load("Python/Döner Simulator/Bilder/kunde_18.png").convert_alpha()
        self.bild_kunde_19 = pygame.image.load("Python/Döner Simulator/Bilder/kunde_19.png").convert_alpha()
        self.bild_kunde_20 = pygame.image.load("Python/Döner Simulator/Bilder/kunde_20.png").convert_alpha()

        self.menü = "startmenü" # Menü ist am Anfang das Startmenü
        self.startmenü_bauen() # GUI des Startmenüs bauen

        # Musik
        mixer.init() # Musik Library initiieren
        mixer.music.load('Python/Döner Simulator/Soundeffekte/Musik1.wav') # Musik vorladen
        mixer.music.play(-1) # spielt die musik x mal ab, -1 heißt unendlich (laut stackoverflow)
        mixer.music.set_volume(0.4) # Lautstärke (obviously)
    
    def element_zuschneiden(self, bild, bitmap: pygame.Mask):
        # Alle nicht-transparenten Bereiche finden
        rechtecke = bitmap.get_bounding_rects()

        # Fallback: Bild ist komplett transparent → 1x1 Pixel erzeugen
        if len(rechtecke) == 0:
            cropped = pygame.Surface((1, 1), pygame.SRCALPHA)
            bitmap = pygame.mask.from_surface(cropped)
            return SimpleNamespace(cropped=cropped, bitmap=bitmap, absatz=(0, 0))

        # Normale Verarbeitung
        inhalt = rechtecke[0].unionall(rechtecke[1:])
        cropped = bild.subsurface(inhalt).copy()
        bitmap = pygame.mask.from_surface(cropped)

        return SimpleNamespace(
            cropped=cropped,
            bitmap=bitmap,
            absatz=(inhalt.x, inhalt.y)
        )

    def hover_bedingung(self, element, element_rechteck):
        maus_position_bzgl_btn = (self.maus_position[0] - element_rechteck.x, self.maus_position[1] - element_rechteck.y) # negativ = zu weit links, positiv = zu weit rechts
        return (
            0 <= maus_position_bzgl_btn[0] < element.cropped.get_width()
            and 0 <= maus_position_bzgl_btn[1] < element.cropped.get_height()
            and element.bitmap.get_at(maus_position_bzgl_btn) # !!!!!! Prüft, ob dieser Pixel bei der Bitmap True ist (also nicht transparent)
        ) # so eine return-Schleife mit 'and' gibt dann quasi True aus, wenn alle Bedingungen erfüllt sind
        
    def spiel_starten(self):
        while self.spiel_läuft: # Spiel-Schleife

            self.zeit_verstrichen_seit_letztem_frame = self.fps.tick(165) / 1000.0 # 165 mal pro Sekunde den Bildschirm aktualisieren (165 FPS)
            self.maus_position = pygame.mouse.get_pos() # für self.mauszeiger
        
            self.hover_spieß_gegart = self.hover_bedingung(self.element_spieß_gegart, self.element_spieß_gegart_rechteck)
            self.hover_spieß_gegart_halb = self.hover_bedingung(self.element_spieß_gegart_halb, self.element_spieß_gegart_halb_rechteck)
            self.hover_spieß_roh = self.hover_bedingung(self.element_spieß_roh, self.element_spieß_roh_rechteck)
            self.hover_spieß_roh_halb = self.hover_bedingung(self.element_spieß_roh_halb, self.element_spieß_roh_halb_rechteck)
            self.hover_spieß_verkokelt = self.hover_bedingung(self.element_spieß_verkokelt, self.element_spieß_verkokelt_rechteck)
            self.hover_spieß_verkokelt_halb = self.hover_bedingung(self.element_spieß_verkokelt_halb, self.element_spieß_verkokelt_halb_rechteck)
            self.hover_fleischteller_leer = self.hover_bedingung(self.element_fleischteller_leer, self.element_fleischteller_leer_rechteck)
            self.hover_fleischteller_roh = self.hover_bedingung(self.element_fleischteller_roh, self.element_fleischteller_roh_rechteck)
            self.hover_fleischteller_gegart = self.hover_bedingung(self.element_fleischteller_gegart, self.element_fleischteller_gegart_rechteck)
            self.hover_fleischteller_verkokelt = self.hover_bedingung(self.element_fleischteller_verkokelt, self.element_fleischteller_verkokelt_rechteck)
            self.hover_falafel = self.hover_bedingung(self.element_falafel, self.element_falafel_rechteck)
            self.hover_salat = self.hover_bedingung(self.element_salat, self.element_salat_rechteck)
            self.hover_tomate = self.hover_bedingung(self.element_tomate, self.element_tomate_rechteck)
            self.hover_zwiebel = self.hover_bedingung(self.element_zwiebel, self.element_zwiebel_rechteck)
            self.hover_gurke = self.hover_bedingung(self.element_gurke, self.element_gurke_rechteck)
            self.hover_rotkohl = self.hover_bedingung(self.element_rotkohl, self.element_rotkohl_rechteck)
            self.hover_weißkohl = self.hover_bedingung(self.element_weißkohl, self.element_weißkohl_rechteck)
            self.hover_feta = self.hover_bedingung(self.element_feta, self.element_feta_rechteck)
            self.hover_joghurtsoße = self.hover_bedingung(self.element_joghurtsoße, self.element_joghurtsoße_rechteck)
            self.hover_knoblauchsoße = self.hover_bedingung(self.element_knoblauchsoße, self.element_knoblauchsoße_rechteck)
            self.hover_scharfesoße = self.hover_bedingung(self.element_scharfesoße, self.element_scharfesoße_rechteck)
            self.hover_brot_voll = self.hover_bedingung(self.element_brot_voll, self.element_brot_voll_rechteck)
            self.hover_brot_halb = self.hover_bedingung(self.element_brot_halb, self.element_brot_halb_rechteck)
            self.hover_toaster = self.hover_bedingung(self.element_toaster, self.element_toaster_rechteck)
            self.hover_optigrill = self.hover_bedingung(self.element_optigrill, self.element_optigrill_rechteck)
            self.hover_optigrill_groß = self.hover_bedingung(self.element_optigrill_groß, self.element_optigrill_groß_rechteck)
        
            for ereignis in pygame.event.get():
                self.gui.process_events(ereignis) 

                if ereignis.type == pygame.QUIT: # Fenster schließen
                    self.spiel_läuft = False

                # Zeit-Funktion (im Ladenmenü)
                if self.zeit_läuft == True:
                    if ereignis.type == self.sekunden_tick: # ohne diese Zeile rattert das schneller als eine Sekunde
                        self.ingame_minute += 1
                        if self.ingame_minute >= 60:
                            self.ingame_minute = 0
                            self.ingame_stunde += 1
                            if self.ingame_stunde >= 24:
                                self.ingame_stunde = 0

                        self.kunde_zeit += 1
                        if self.kunde_anwesend:
                            self.geduld_zeit += 1
                        if self.kunde_anwesend == False:
                            self.geduld_zeit = 0

                        # neuer Kunde nach bestimmter, zufälliger Zeit
                        if self.kunde_anwesend == False and self.kunde_zeit >= round(random.gauss(ZEIT_BIS_NEUER_KUNDE, 3)) and self.kunden_für_den_tag > 0: # Gaussche Verteilung wird in class Kunde erklärt :)
                            self.aktueller_kunde = Kunde()
                            spiel.ladenmenü_kunde_dialog_bauen()
                            self.ladenmenü_kunde_dialog_erstellt = True # braucht man, weil es nicht immer initialisiert ist :(
                            self.kunde_zeit = 0
                            self.kunden_für_den_tag -= 1

                    # Spieß-Zeit
                    if self.menü == "ladenmenü":
                        if ereignis.type == self.sekunden_tick:
                            self.spieß_zeit += 1

                            if self.spieß_zeit <= SPIESS_ZEIT_VERKOKELT: 
                                self.spieß_fortschritt = self.spieß_zeit/SPIESS_ZEIT_VERKOKELT*100
                            else:
                                self.spieß_fortschritt = 100
                            self.gui_laden_spieß_zustand.set_current_progress(self.spieß_fortschritt)

                            if self.brot_im_brotgrill != 0:
                                self.brotgrill_zeit += 1

                                if self.brotgrill_zeit <= self.brotgrill_zeit_verkokelt: 
                                    self.brotgrill_fortschritt = self.brotgrill_zeit/self.brotgrill_zeit_verkokelt*100
                                else:
                                    self.brotgrill_fortschritt = 100
                                self.gui_laden_brotgrill_zustand.set_current_progress(self.brotgrill_fortschritt)


                # außerhalb von der zeit_läuft Schleife, da sonst ohne Pause die Bilder nicht aktualisiert werden (eigene Erfahrung)
                if self.menü == "ladenmenü":
                    if self.spieß_zeit >= SPIESS_ZEIT_VERKOKELT:
                        self.spieß_gargrad = "verkokelt"
                    elif self.spieß_zeit >= SPIESS_ZEIT_GEGART:
                        self.spieß_gargrad = "gegart"
                    else:
                        self.spieß_gargrad = "roh"
                    if self.brotgrill_zeit >= self.brotgrill_zeit_verkokelt:
                        self.brot_gargrad = "verkokelt"
                    elif self.brotgrill_zeit >= self.brotgrill_zeit_gegart:
                        self.brot_gargrad = "gegart"
                    else:
                        self.brot_gargrad = "roh"

                    # :02d ist fürs Format (0 davor falls einstellige Zahl, Grenze davon: zweistellige Zahl, d = es handelt sich um eine Ganzzahl)
                    uhrzeit_text = f"Zeit: {self.ingame_stunde:02d}:{self.ingame_minute:02d} Uhr" 
                    self.gui_zeit_anzeige.set_text(uhrzeit_text)

                # Button Funktionen & Menüwechsel
                if ereignis.type == pygame_gui.UI_BUTTON_PRESSED and hasattr(ereignis, 'ui_element'):

                    if self.menü == "startmenü": # Diese if-Schleifen braucht man, da die UI Elemente nur in den Menüs existieren, sonst kennt Python die nicht und Fehlermeldung -_-
                        if ereignis.ui_element == self.gui_startmenü_starten:
                            self.startmenü_abbauen()
                            self.menü = "akquisitionsmenü"
                            self.akquisitionsmenü_bauen()
                        if ereignis.ui_element == self.gui_startmenü_verlassen: 
                            self.spiel_läuft = False

                    if self.menü == "akquisitionsmenü": 
                        if ereignis.ui_element == self.gui_laden1_button:
                            self.akquisitionsmenü_abbauen()
                            self.kapital = self.kapital - 3*LADEN1_MIETE
                            self.nachfragefaktor_initial = LADEN1_NACHFRAGEFAKTOR
                            self.nachfragefaktor = LADEN1_NACHFRAGEFAKTOR
                            self.bewertungsfaktor = LADEN1_BEWERTUNGSFAKTOR
                            self.laden1 = True
                            self.menü = "gerätekaufmenü"
                            self.gerätekaufmenü_bauen()
                            
                        if ereignis.ui_element == self.gui_laden2_button:
                            self.akquisitionsmenü_abbauen()
                            self.kapital = self.kapital - 3*LADEN2_MIETE
                            self.nachfragefaktor_initial = LADEN2_NACHFRAGEFAKTOR
                            self.nachfragefaktor = LADEN2_NACHFRAGEFAKTOR
                            self.bewertungsfaktor = LADEN2_BEWERTUNGSFAKTOR
                            self.laden2 = True
                            self.menü = "gerätekaufmenü"
                            self.gerätekaufmenü_bauen()
                            
                        if ereignis.ui_element == self.gui_laden3_button:
                            self.akquisitionsmenü_abbauen()
                            self.kapital = self.kapital - 3*LADEN3_MIETE
                            self.nachfragefaktor_initial = LADEN3_NACHFRAGEFAKTOR
                            self.nachfragefaktor = LADEN3_NACHFRAGEFAKTOR
                            self.bewertungsfaktor = LADEN3_BEWERTUNGSFAKTOR
                            self.laden3 = True
                            self.menü = "gerätekaufmenü"
                            self.gerätekaufmenü_bauen()
                    
                    if self.menü == "gerätekaufmenü":
                        if ereignis.ui_element == self.gui_brotgrill1_kaufen:
                            if self.brotgrill1_gekauft == False and self.kapital >= BROTGRILL1_KOSTEN:
                                self.brotgrill1_gekauft = True
                                self.brotgrill2_gekauft = False
                                self.brotgrill3_gekauft = False
                                self.brotgrill_zeit_gegart = BROTGRILL1_BROT_ZEIT_GEGART
                                self.brotgrill_zeit_verkokelt = BROTGRILL1_BROT_ZEIT_VERKOKELT
                                self.kapital = self.kapital - BROTGRILL1_KOSTEN
                                self.gui_gerätemenü_kapital.set_text(f"Kapital: {self.kapital} €")
                        if ereignis.ui_element == self.gui_brotgrill2_kaufen:
                            if self.brotgrill2_gekauft == False and self.kapital >= BROTGRILL2_KOSTEN:
                                self.brotgrill1_gekauft = False
                                self.brotgrill2_gekauft = True
                                self.brotgrill3_gekauft = False
                                self.brotgrill_zeit_gegart = BROTGRILL2_BROT_ZEIT_GEGART
                                self.brotgrill_zeit_verkokelt = BROTGRILL2_BROT_ZEIT_VERKOKELT
                                self.kapital = self.kapital - BROTGRILL2_KOSTEN
                                self.gui_gerätemenü_kapital.set_text(f"Kapital: {self.kapital} €")
                        if ereignis.ui_element == self.gui_brotgrill3_kaufen:
                            if self.brotgrill3_gekauft == False and self.kapital >= BROTGRILL3_KOSTEN:
                                self.brotgrill1_gekauft = False
                                self.brotgrill2_gekauft = False
                                self.brotgrill3_gekauft = True
                                self.brotgrill_zeit_gegart = BROTGRILL3_BROT_ZEIT_GEGART
                                self.brotgrill_zeit_verkokelt = BROTGRILL3_BROT_ZEIT_VERKOKELT
                                self.kapital = self.kapital - BROTGRILL3_KOSTEN
                                self.gui_gerätemenü_kapital.set_text(f"Kapital: {self.kapital} €")
                                
                        
                        if ereignis.ui_element == self.gui_geräte_weiter:
                            self.gerätekaufmenü_abbauen()
                            self.menü = "zutatenmenü"
                            self.zutatenmenü_bauen()
                            self.zutaten_kosten_aktualisieren()
                            self.zutaten_anteile_automatisch_ausfüllen()
       
                    if self.menü == "zutatenmenü":
                        if ereignis.ui_element == self.gui_zutaten_automatisch_ausfüllen:
                            self.zutaten_anteile_automatisch_ausfüllen()
                        if ereignis.ui_element == self.gui_zutaten_geräte:
                            self.zutatenmenü_abbauen()
                            self.menü = "gerätekaufmenü"
                            self.gerätekaufmenü_bauen()
                        if ereignis.ui_element == self.gui_zutaten_weiter:
                            self.kapital = round((self.kapital - self.zutaten_kosten_ermitteln()), 2)
                            self.zutaten_mengen_übernehmen()
                            self.zutatenmenü_abbauen()
                            self.menü = "ladenmenü"
                            self.ladenmenü_bauen()
                            self.ladenmenü_anzeigen_bauen()  # GUI-Elemente: einmalig
                            # ladenmenü_elemente_bauen & spieß_bauen: nicht hier, kommen jeden Frame

                    if self.menü == "ladenmenü":
                        try: # try, da die Elemente manchmal gar nicht erstellt sind
                            if ereignis.ui_element == self.gui_starten:
                                self.zeit_läuft = True
                                button_kill_probieren(self.gui_starten)
                                self.ladenmenü_zeitbefehle_umschalten("pausieren")
                        except:
                            pass
                        try:
                            if ereignis.ui_element == self.gui_pausieren:
                                self.zeit_läuft = False
                                self.ladenmenü_zeitbefehle_umschalten("weiter")
                        except:
                            pass
                        try:       
                            if ereignis.ui_element == self.gui_weiter:
                                self.zeit_läuft = True
                                self.ladenmenü_zeitbefehle_umschalten("pausieren")
                        except:
                            pass
                        if ereignis.ui_element == self.gui_ladenmenü_verlassen:
                            self.spiel_läuft = False
                        if ereignis.ui_element == self.gui_ladenmenü_müll:
                            self.in_der_hand = [0, "", ""]
                            self.döner_abbauen()
                        if ereignis.ui_element == self.gui_ladenmenü_tag_beenden:
                            self.neuer_tag()

                        if self.ladenmenü_kunde_dialog_erstellt == True:
                            if ereignis.ui_element == self.gui_ladenmenü_geben:
                                self.kunde_zeit = 0
                                self.bewertung_aktualisieren()
                                self.döner_abbauen()
                                self.ladenmenü_kunde_dialog_abbauen()
                                self.kunde_anwesend = False
                                self.aktueller_kunde = None
                                self.ladenmenü_kunde_dialog_erstellt = False
                                self.kapital += self.dönerpreis
                            if ereignis.ui_element == self.gui_ladenmenü_ablehnen:
                                self.kunde_zeit = 0
                                self.bewertung_aktualisieren_abgelehnt()
                                self.kunde_anwesend = False        
                                self.ladenmenü_kunde_dialog_abbauen()
                                self.aktueller_kunde = None
                                self.ladenmenü_kunde_dialog_erstellt = False

                        if self.menü == "ladenmenü": # es ist so verdammt dumm, dass man das doppelt machen muss (trial and error)
                        # Laden-Bilder
                            self.fenster.blit(self.bild_theke, (0, 0))
                            if self.laden1:
                                self.fenster.blit(self.bild_laden1_hintergrund, (0, 0))
                            if self.laden2:
                                self.fenster.blit(self.bild_laden2_hintergrund, (0, 0))
                            if self.laden3:
                                self.fenster.blit(self.bild_laden3_hintergrund, (0, 0))
                            self.ladenmenü_elemente_bauen()
                        

                # Über Hintergrund
                if self.menü == "ladenmenü":
                    self.ladenmenü_spieß_bauen()
                    self.ladenmenü_döner_bauen()
                    if self.kunde_anwesend:
                        self.fenster.blit(self.aktueller_kunde.bild_ausgewählt, (0, 0))   

                # Text-Eingabe Funktionen
                if ereignis.type == pygame_gui.UI_TEXT_ENTRY_CHANGED:
                    if self.menü == "zutatenmenü":
                        self.zutaten_kosten_aktualisieren() 
                        self.nachfragefaktor_aktualisieren()

                # Ladenmenü-Elemente-gedrückt-Funktionen
                if ereignis.type == pygame.MOUSEBUTTONDOWN:
                    if self.menü == "ladenmenü":
                        if self.hover_brot_halb or self.hover_brot_voll:
                            # Brot in die Hand nehmen
                            if self.in_der_hand == [0, "", ""] and self.brot_anzahl > 0:
                                self.in_der_hand = [1, "brot", "roh"]
                                self.brot_anzahl -= 1
                                self.gui_laden_brot_menge.set_text(str(self.brot_anzahl))
                                self.döner_modus = True
                                self.döner.brot = "roh"
                            # Zurücklegen
                            elif self.in_der_hand[1] == "brot" and self.in_der_hand[2] == "roh":
                                self.brot_anzahl += self.in_der_hand[0]
                                self.gui_laden_brot_menge.set_text(str(self.brot_anzahl))
                                self.in_der_hand = [0, "", ""]
                                self.döner_modus = False
                                self.döner.brot = ""

                        if (self.brotgrill1_gekauft and self.hover_toaster) or (self.brotgrill2_gekauft and self.hover_optigrill) or (self.brotgrill3_gekauft and self.hover_optigrill_groß):
                            # Brot auf Brotgrill legen
                            if self.in_der_hand[1] == "brot" and self.brot_im_brotgrill == 0:
                                self.brot_im_brotgrill = self.in_der_hand[0]
                                if self.in_der_hand[2] == "roh" or self.in_der_hand[2] == "":
                                    self.brotgrill_fortschritt = 0
                                elif self.in_der_hand[2] == "gegart":
                                    self.brotgrill_fortschritt = (self.brotgrill_zeit_gegart/self.brotgrill_zeit_verkokelt)*100
                                    self.brotgrill_zeit = self.brotgrill_zeit_gegart
                                elif self.in_der_hand[2] == "verkokelt":
                                    self.brotgrill_fortschritt = 100
                                    self.brotgrill_zeit = self.brotgrill_zeit_verkokelt
                                self.gui_laden_brotgrill_zustand.set_current_progress(self.brotgrill_fortschritt)
                                self.in_der_hand = [0, "", ""]
                                self.gui_laden_brotgrill_menge.set_text(str(self.brot_im_brotgrill))
                                self.döner_modus = False
                                self.döner.brot = ""
                            # Brot rausnehmen
                            elif self.in_der_hand == [0, "", ""] and self.brot_im_brotgrill == 1:
                                self.in_der_hand = [self.brot_im_brotgrill, "brot", self.brot_gargrad]
                                self.brot_im_brotgrill = 0
                                self.gui_laden_brotgrill_menge.set_text(str(self.brot_im_brotgrill))
                                self.brotgrill_zeit = 0
                                self.gui_laden_brotgrill_zustand.set_current_progress(0)
                                self.döner_modus = True
                                self.döner.brot = self.brot_gargrad
                                self.brot_gargrad = ""

                        if (self.hover_spieß_roh or self.hover_spieß_roh_halb or self.hover_spieß_gegart or self.hover_spieß_gegart_halb or self.hover_spieß_verkokelt or self.hover_spieß_verkokelt_halb) and self.spießgewicht_gewicht >= SPIESS_PRO_DOENER and self.fleischteller == "":
                            self.fleischteller = self.spieß_gargrad
                            self.spießgewicht_gewicht -= SPIESS_PRO_DOENER
                            self.gui_laden_spieß_menge.set_current_progress((self.spießgewicht_gewicht/self.spießgewicht_gewicht_initial) * 100)
                            self.spieß_zeit = 0
                            self.spieß_gargrad = "roh"

                        if self.hover_fleischteller_roh or self.hover_fleischteller_gegart or self.hover_fleischteller_verkokelt:
                            # In die Hand nehmen
                            if self.in_der_hand == [0, "", ""] and self.döner_modus == False:
                                self.in_der_hand = [SPIESS_PRO_DOENER, "fleisch", self.fleischteller]
                                self.fleischteller = ""
                            # In den Döner legen
                            elif self.döner_modus == True and self.döner.fleisch == "" and self.döner.falafel == False:
                                self.döner.fleisch = self.fleischteller
                                self.fleischteller = ""
                                self.gui_ladenmenü_döner.set_text(f"{self.döner}")
                            # Zurücklegen
                            elif self.in_der_hand[1] == "fleisch" and self.döner_modus == False and self.fleischteller == "":
                                self.fleischteller = self.in_der_hand[2]
                                self.in_der_hand = [0, "", ""]

                        self.elemente_in_hand_döner_nehmen(self.hover_falafel, self.falafel_anzahl, FALAFEL_PRO_DOENER, "falafel", self.gui_laden_falafel_menge, self.falafel_anzahl_initial)
                        self.elemente_in_hand_döner_nehmen(self.hover_salat, self.salat_anzahl, SALAT_PRO_DOENER, "salat", self.gui_laden_salat_menge, self.salat_anzahl_initial)
                        self.elemente_in_hand_döner_nehmen(self.hover_tomate, self.tomate_anzahl, TOMATE_PRO_DOENER, "tomate", self.gui_laden_tomate_menge, self.tomate_anzahl_initial)
                        self.elemente_in_hand_döner_nehmen(self.hover_zwiebel, self.zwiebel_anzahl, ZWIEBEL_PRO_DOENER, "zwiebel", self.gui_laden_zwiebel_menge, self.zwiebel_anzahl_initial)
                        self.elemente_in_hand_döner_nehmen(self.hover_gurke, self.gurke_anzahl, GURKE_PRO_DOENER, "gurke", self.gui_laden_gurke_menge, self.gurke_anzahl_initial)
                        self.elemente_in_hand_döner_nehmen(self.hover_rotkohl, self.rotkohl_anzahl, ROTKOHL_PRO_DOENER, "rotkohl", self.gui_laden_rotkohl_menge, self.rotkohl_anzahl_initial)
                        self.elemente_in_hand_döner_nehmen(self.hover_weißkohl, self.weißkohl_anzahl, WEISSKOHL_PRO_DOENER, "weißkohl", self.gui_laden_weißkohl_menge, self.weißkohl_anzahl_initial)
                        self.elemente_in_hand_döner_nehmen(self.hover_feta, self.feta_anzahl, FETA_PRO_DOENER, "feta", self.gui_laden_feta_menge, self.feta_anzahl_initial)
                        self.elemente_in_hand_döner_nehmen(self.hover_joghurtsoße, self.joghurtsoße_anzahl, JOGHURTSOSSE_PRO_DOENER, "joghurtsoße", self.gui_laden_joghurtsoße_menge, self.joghurtsoße_anzahl_initial)
                        self.elemente_in_hand_döner_nehmen(self.hover_knoblauchsoße, self.knoblauchsoße_anzahl, KNOBLAUCHSOSSE_PRO_DOENER, "knoblauchsoße", self.gui_laden_knoblauchsoße_menge, self.knoblauchsoße_anzahl_initial)
                        self.elemente_in_hand_döner_nehmen(self.hover_scharfesoße, self.scharfesoße_anzahl, SCHARFESOSSE_PRO_DOENER, "scharfesoße", self.gui_laden_scharfesoße_menge, self.scharfesoße_anzahl_initial)
                                

            self.gui.update(self.zeit_verstrichen_seit_letztem_frame) # GUI aktualisieren
            self.gui.draw_ui(self.fenster) # Bilder sollen *über* den GUI Elementen sein (Bilder kommen erst unten)

            self.hover_irgendeiner = ( 
                self.hover_spieß_gegart or self.hover_spieß_gegart_halb or self.hover_spieß_roh
                or self.hover_spieß_roh_halb or self.hover_spieß_verkokelt or self.hover_spieß_verkokelt_halb
                or self.hover_fleischteller_leer or self.hover_fleischteller_roh
                or self.hover_fleischteller_gegart or self.hover_fleischteller_verkokelt
                or self.hover_falafel or self.hover_salat or self.hover_tomate or self.hover_zwiebel 
                or self.hover_gurke or self.hover_rotkohl or self.hover_weißkohl or self.hover_feta 
                or self.hover_joghurtsoße or self.hover_knoblauchsoße or self.hover_scharfesoße
                or self.hover_brot_voll or self.hover_brot_halb
                or self.hover_toaster or self.hover_optigrill or self.hover_optigrill_groß
                )
            pygame.mouse.set_cursor(self.mauszeiger_drücken if self.hover_irgendeiner and self.menü == "ladenmenü" else self.mauszeiger) # muss nach der GUI-Aktualisierung kommen

            # Bilder anzeigen (📌 zu Images in pygame_gui konnte ich online nichts finden)
            if self.menü == "startmenü":
                self.fenster.blit(self.start_bild, (560,150)) # Start Bild anzeigen
            if self.menü == "akquisitionsmenü":
                self.fenster.blit(self.bild_laden1, (300,220))
                self.fenster.blit(self.bild_laden2, (850,220))
                self.fenster.blit(self.bild_laden3, (1400,220))
                
            pygame.display.update() # Bildschirm aktualisieren

        pygame.quit() # Wenn nichts in der Hauptschleife ist, beende das Spiel und pygame

    def startmenü_bauen(self):
        self.fenster.fill((40,40,40))
        self.gui_startmenü_titel = pygame_gui.elements.UILabel (
            relative_rect=(690,175,800,150), # Größe (x-Position von oben links, y, Breite, Höhe)
            text="Döner Simulator",
            manager=self.gui, # GUI-Manager verbinden
            object_id="#start_text" # welches Layout in der theme.json ausgewählt werden soll
        )
        self.gui_startmenü_starten = pygame_gui.elements.UIButton (
            relative_rect=(560,450,800,100),
            text="Starten",
            manager=self.gui,
            object_id="#start_button"
        )
        self.gui_startmenü_verlassen = pygame_gui.elements.UIButton (
            relative_rect=(560,600,800,100),
            text="Zurück zum Desktop",
            manager=self.gui,
            object_id="#quit_button"
        )
        self.gui_startmenü_hinweis = pygame_gui.elements.UILabel (
            relative_rect=(0,1020,1920,21),
            text="© Jason Ziegler, Selim Kantarci, Leon Nguyen, Sadettin Erdem, Valerio Sibenik | Bilder: Blogger Canon Gaillon (Icon, CC BY), Gemini (Kundenbilder), ChatGPT (Sonstiges) | Musik: Pixabay | Schriftarten: Google Fonts, Dafont",
            manager=self.gui,
            object_id="#normal_klein_zentriert"
        )
    
    def startmenü_abbauen(self):
        self.gui_startmenü_titel.kill()
        self.gui_startmenü_starten.kill()
        self.gui_startmenü_verlassen.kill()
        self.gui_startmenü_hinweis.kill()

    def akquisitionsmenü_bauen(self):
        self.fenster.fill((40,40,40))
        self.gui_akquisitions_text = pygame_gui.elements.UILabel (
            relative_rect=(50,50,500,150),
            text="Laden auswählen",
            manager=self.gui,
            object_id="#titel"
        )
        self.gui_drei_monate_info = pygame_gui.elements.UILabel (
            relative_rect=(700,50,700,150),
            text="Sie müssen die Miete für 3 Monate vorbezahlen.",
            manager=self.gui,
            object_id="#normal"
        )
        self.gui_akquisitionsmenü_startkapital = pygame_gui.elements.UILabel (
            relative_rect=(1600,50,500,150),
            text=f"Startkapital: {STARTKAPITAL} €",
            manager=self.gui,
            object_id="#normal"
        )

        self.gui_laden1_titel = pygame_gui.elements.UILabel (
            relative_rect=(300,510,400,100),
            text="Foodtruck auf dem Dorf",
            manager=self.gui,
            object_id="#kleine_überschrift"
        )
        self.gui_laden2_titel = pygame_gui.elements.UILabel (
            relative_rect=(850,510,400,100),
            text="Laden in einer Kleinstadt",
            manager=self.gui,
            object_id="#kleine_überschrift"
        )
        self.gui_laden3_titel = pygame_gui.elements.UILabel (
            relative_rect=(1400,510,400,100),
            text="Grossstadtimbiss",
            manager=self.gui,
            object_id="#kleine_überschrift"
        )

        self.gui_laden0_schwierigkeit = pygame_gui.elements.UILabel (
            relative_rect=(30,620,300,50),
            text="Schwierigkeit",
            manager=self.gui,
            object_id="#normal"
        )
        self.gui_laden0_nachfrage = pygame_gui.elements.UILabel (
            relative_rect=(30,680,300,50),
            text="Nachfrage",
            manager=self.gui,
            object_id="#normal"
        )
        self.gui_laden0_konkurrenz = pygame_gui.elements.UILabel (
            relative_rect=(30,740,300,50),
            text="Konkurrenz",
            manager=self.gui,
            object_id="#normal"
        )
        self.gui_laden0_bewertung = pygame_gui.elements.UILabel (
            relative_rect=(30,800,300,50),
            text="Bewertungen",
            manager=self.gui,
            object_id="#normal"
        )
        self.gui_laden0_miete = pygame_gui.elements.UILabel (
            relative_rect=(30,860,300,50),
            text="monatliche Miete",
            manager=self.gui,
            object_id="#normal"
        )

        self.gui_laden1_schwierigkeit = pygame_gui.elements.UILabel (
            relative_rect=(350,620,300,50),
            text="Einfach",
            manager=self.gui,
            object_id="#normal"
        )
        self.gui_laden1_nachfrage = pygame_gui.elements.UILabel (
            relative_rect=(350,680,300,50),
            text="mäßig",
            manager=self.gui,
            object_id="#normal"
        )
        self.gui_laden1_konkurrenz = pygame_gui.elements.UILabel (
            relative_rect=(350,740,300,50),
            text="keine",
            manager=self.gui,
            object_id="#normal"
        )
        self.gui_laden1_bewertung = pygame_gui.elements.UILabel (
            relative_rect=(350,800,300,50),
            text="wenig Einfluss",
            manager=self.gui,
            object_id="#normal"
        )
        self.gui_laden1_miete = pygame_gui.elements.UILabel (
            relative_rect=(350,860,300,50),
            text=f"{LADEN1_MIETE} €",
            manager=self.gui,
            object_id="#normal"
        )

        self.gui_laden2_schwierigkeit = pygame_gui.elements.UILabel (
            relative_rect=(900,620,300,50),
            text="Normal",
            manager=self.gui,
            object_id="#normal"
        )
        self.gui_laden2_nachfrage = pygame_gui.elements.UILabel (
            relative_rect=(900,680,300,50),
            text="hoch",
            manager=self.gui,
            object_id="#normal"
        )
        self.gui_laden2_konkurrenz = pygame_gui.elements.UILabel (
            relative_rect=(900,740,300,50),
            text="etwas",
            manager=self.gui,
            object_id="#normal"
        )
        self.gui_laden2_bewertung = pygame_gui.elements.UILabel (
            relative_rect=(900,800,300,50),
            text="mäßig streng",
            manager=self.gui,
            object_id="#normal"
        )
        self.gui_laden2_miete = pygame_gui.elements.UILabel (
            relative_rect=(900,860,300,50),
            text=f"{LADEN2_MIETE} €",
            manager=self.gui,
            object_id="#normal"
        )

        self.gui_laden3_schwierigkeit = pygame_gui.elements.UILabel (
            relative_rect=(1450,620,300,50),
            text="Schwer",
            manager=self.gui,
            object_id="#normal"
        )
        self.gui_laden3_nachfrage = pygame_gui.elements.UILabel (
            relative_rect=(1450,680,300,50),
            text="sehr hoch",
            manager=self.gui,
            object_id="#normal"
        )
        self.gui_laden3_konkurrenz = pygame_gui.elements.UILabel (
            relative_rect=(1450,740,300,50),
            text="stark",
            manager=self.gui,
            object_id="#normal"
        )
        self.gui_laden3_bewertung = pygame_gui.elements.UILabel (
            relative_rect=(1450,800,300,50),
            text="streng",
            manager=self.gui,
            object_id="#normal"
        )
        self.gui_laden3_miete = pygame_gui.elements.UILabel (
            relative_rect=(1450,860,300,50),
            text=f"{LADEN3_MIETE} €",
            manager=self.gui,
            object_id="#normal"
        )

        self.gui_laden1_button = pygame_gui.elements.UIButton (
            relative_rect=(300,940,420,90),
            text="Auswählen",
            manager=self.gui,
            object_id="#kleiner_button"
        )
        self.gui_laden2_button = pygame_gui.elements.UIButton (
            relative_rect=(850,940,420,90),
            text="Auswählen",
            manager=self.gui,
            object_id="#kleiner_button"
        )
        self.gui_laden3_button = pygame_gui.elements.UIButton (
            relative_rect=(1400,940,420,90),
            text="Auswählen",
            manager=self.gui,
            object_id="#kleiner_button"
        )

    def akquisitionsmenü_abbauen(self):
        self.gui_akquisitions_text.kill()
        self.gui_akquisitionsmenü_startkapital.kill()
        self.gui_drei_monate_info.kill()
        self.gui_laden1_titel.kill()
        self.gui_laden2_titel.kill()
        self.gui_laden3_titel.kill()
        self.gui_laden0_bewertung.kill()
        self.gui_laden1_bewertung.kill()
        self.gui_laden2_bewertung.kill()
        self.gui_laden3_bewertung.kill()
        self.gui_laden0_konkurrenz.kill()
        self.gui_laden1_konkurrenz.kill()
        self.gui_laden2_konkurrenz.kill()
        self.gui_laden3_konkurrenz.kill()
        self.gui_laden0_miete.kill()
        self.gui_laden1_miete.kill()
        self.gui_laden2_miete.kill()
        self.gui_laden3_miete.kill()
        self.gui_laden0_nachfrage.kill()
        self.gui_laden1_nachfrage.kill()
        self.gui_laden2_nachfrage.kill()
        self.gui_laden3_nachfrage.kill()
        self.gui_laden0_schwierigkeit.kill()
        self.gui_laden1_schwierigkeit.kill()
        self.gui_laden2_schwierigkeit.kill() 
        self.gui_laden3_schwierigkeit.kill()
        self.gui_laden1_button.kill()
        self.gui_laden2_button.kill()
        self.gui_laden3_button.kill()

    def gerätekaufmenü_bauen(self):
        self.fenster.fill((40,40,40))
        self.gui_gerätekauf_text = pygame_gui.elements.UILabel (
            relative_rect=(50,50,500,150),
            text="Geräte kaufen",
            manager=self.gui,
            object_id="#titel"
        )
        self.gui_geld_einplanen_info = pygame_gui.elements.UILabel (
            relative_rect=(700,50,850,150),
            text="Planen Sie noch etwa 100 € für die Zutaten ein.",
            manager=self.gui,
            object_id="#normal"
        )
        self.gui_gerätemenü_kapital = pygame_gui.elements.UILabel (
            relative_rect=(1600,50,500,150),
            text=f"Kapital: {self.kapital} €",
            manager=self.gui,
            object_id="#normal"
        )

        self.gui_geräte_brotgrill = pygame_gui.elements.UILabel (
            relative_rect=(100,250,200,60),
            text="Brot Grill",
            manager=self.gui,
            object_id="#kleine_überschrift"
        )
        self.gui_brotgrill1 = pygame_gui.elements.UITextBox (
            relative_rect=(400,250,450,150),
            html_text="Toaster<br>wärmt langsam",
            manager=self.gui,
            object_id="#normal"
        )
        self.gui_brotgrill1_kaufen = pygame_gui.elements.UIButton (
            relative_rect=(400,370,200,60),
            text=f"{BROTGRILL1_KOSTEN} €",
            manager=self.gui,
            object_id="#kauf_button"
        )
        self.gui_brotgrill2 = pygame_gui.elements.UITextBox (
            relative_rect=(900,250,450,150),
            html_text="Optigrill<br>wärmt schnell",
            manager=self.gui,
            object_id="#normal"
        )
        self.gui_brotgrill2_kaufen = pygame_gui.elements.UIButton (
            relative_rect=(900,370,200,60),
            text=f"{BROTGRILL2_KOSTEN} €",
            manager=self.gui,
            object_id="#kauf_button"
        )
        self.gui_brotgrill3 = pygame_gui.elements.UITextBox (
            relative_rect=(1400,250,450,150),
            html_text="Optigrill+<br>wärmt sehr schnell",
            manager=self.gui,
            object_id="#normal"
        )
        self.gui_brotgrill3_kaufen = pygame_gui.elements.UIButton (
            relative_rect=(1400,370,200,60),
            text=f"{BROTGRILL3_KOSTEN} €",
            manager=self.gui,
            object_id="#kauf_button"
        )

        self.gui_geräte_weiter = pygame_gui.elements.UIButton (
            relative_rect=(1600,970,300,90),
            text="Weiter",
            manager=self.gui,
            object_id="#kleiner_button"
        )

    def gerätekaufmenü_abbauen(self):
        self.gui_gerätekauf_text.kill()
        self.gui_geld_einplanen_info.kill()
        self.gui_gerätemenü_kapital.kill()
        self.gui_geräte_brotgrill.kill()
        self.gui_brotgrill1.kill()
        self.gui_brotgrill1_kaufen.kill()
        self.gui_brotgrill2.kill()
        self.gui_brotgrill2_kaufen.kill()
        self.gui_brotgrill3.kill()
        self.gui_brotgrill3_kaufen.kill()
        self.gui_geräte_weiter.kill()

    def zutatenmenü_bauen(self):
        self.falafel_anzahl_initial = self.falafel_anzahl
        self.salat_anzahl_initial = self.salat_anzahl
        self.tomate_anzahl_initial = self.tomate_anzahl
        self.zwiebel_anzahl_initial = self.zwiebel_anzahl
        self.gurke_anzahl_initial = self.gurke_anzahl
        self.rotkohl_anzahl_initial = self.rotkohl_anzahl
        self.weißkohl_anzahl_initial = self.weißkohl_anzahl
        self.feta_anzahl_initial = self.feta_anzahl
        self.joghurtsoße_anzahl_initial = self.joghurtsoße_anzahl
        self.knoblauchsoße_anzahl_initial = self.knoblauchsoße_anzahl
        self.scharfesoße_anzahl_initial = self.scharfesoße_anzahl

        self.fenster.fill((40,40,40)) 
        self.gui_zutaten_text = pygame_gui.elements.UILabel (
            relative_rect=(50,50,500,150),
            text="Zutaten",
            manager=self.gui,
            object_id="#titel"
        )
        self.gui_zutaten_info = pygame_gui.elements.UILabel (
            relative_rect=(400,50,1100,150),
            text="Der Preis bestimmt die Nachfrage.",
            manager=self.gui,
            object_id="#normal"
        )
        self.gui_zutaten_kapital = pygame_gui.elements.UILabel (
            relative_rect=(1600,50,500,150),
            text=f"Kapital: {self.kapital} €",
            manager=self.gui,
            object_id="#normal"
        ) 
        self.gui_spießgewicht_info = pygame_gui.elements.UILabel (
            relative_rect=(20,250,370,60),
            text=f"kg Gewicht ({SPIESS_PRO_DOENER}kg/Döner):",
            manager=self.gui,
            object_id="#normal"
        )
        self.gui_spießgewicht = pygame_gui.elements.UITextEntryLine (
            relative_rect=(400,250,100,60),
            initial_text=f"{self.spießgewicht_gewicht}",
            manager=self.gui,
            object_id="#eingabe"
        )
        self.gui_spießgewicht.set_allowed_characters(["0","1","2","3","4","5","6","7","8","9","."]) # nur Zahlen + Kommazahlen
        self.gui_kalb = pygame_gui.elements.UILabel (
            relative_rect=(530,250,230,60),
            text=f"% Kalb ({KALB_KOSTEN}€/kg):",
            manager=self.gui,
            object_id="#normal"
        )
        self.gui_kalb_anteil = pygame_gui.elements.UITextEntryLine (
            relative_rect=(760,250,100,60),
            initial_text=f"{self.spieß_kalb_anteil}",
            manager=self.gui,
            object_id="#eingabe"
        )
        self.gui_kalb_anteil.set_allowed_characters(["0","1","2","3","4","5","6","7","8","9","."])
        self.gui_huhn = pygame_gui.elements.UILabel (
            relative_rect=(890,250,230,60),
            text=f"% Huhn ({HUHN_KOSTEN}€/kg):",
            manager=self.gui,
            object_id="#normal"
        )
        self.gui_huhn_anteil = pygame_gui.elements.UITextEntryLine (
            relative_rect=(1130,250,100,60),
            initial_text=f"{self.spieß_huhn_anteil}",
            manager=self.gui,
            object_id="#eingabe"
        )
        self.gui_huhn_anteil.set_allowed_characters(["0","1","2","3","4","5","6","7","8","9","."])
        self.gui_hack = pygame_gui.elements.UILabel (
            relative_rect=(1260,250,230,60),
            text=f"% Hack ({HACK_KOSTEN}€/kg):",
            manager=self.gui,
            object_id="#normal"
        )
        self.gui_hack_anteil = pygame_gui.elements.UITextEntryLine (
            relative_rect=(1500,250,100,60),
            initial_text=f"{self.spieß_hack_anteil}",
            manager=self.gui,
            object_id="#eingabe"
        )
        self.gui_hack_anteil.set_allowed_characters(["0","1","2","3","4","5","6","7","8","9","."])
        self.gui_falafel = pygame_gui.elements.UILabel (
            relative_rect=(20,360,370,60),
            text=f"St. Falafel ({FALAFEL_PRO_DOENER}/D., {FALAFEL_KOSTEN}€/St.):",
            manager=self.gui,
            object_id="#normal"
        )
        self.gui_falafel_anteil = pygame_gui.elements.UITextEntryLine (
            relative_rect=(390,360,100,60),
            initial_text=f"{self.falafel_anzahl}",
            manager=self.gui,
            object_id="#eingabe"
        )
        self.gui_falafel_anteil.set_allowed_characters(["0","1","2","3","4","5","6","7","8","9","."])
        self.gui_salat = pygame_gui.elements.UILabel (
            relative_rect=(500,360,360,60),
            text=f"g Salat ({SALAT_PRO_DOENER}g/D.,{SALAT_KOSTEN}/g):",
            manager=self.gui,
            object_id="#normal"
        )
        self.gui_salat_anteil = pygame_gui.elements.UITextEntryLine (
            relative_rect=(840,360,100,60),
            initial_text=f"{self.salat_anzahl}",
            manager=self.gui,
            object_id="#eingabe"
        )
        self.gui_salat_anteil.set_allowed_characters(["0","1","2","3","4","5","6","7","8","9","."])
        self.gui_salat_anteil.set_text_length_limit(3)
        self.gui_tomate = pygame_gui.elements.UILabel (
            relative_rect=(950,360,340,60),
            text=f"Tomate ({TOMATE_PRO_DOENER}/D., {TOMATE_KOSTEN}€/St.):",
            manager=self.gui,
            object_id="#normal"
        )
        self.gui_tomate_anteil = pygame_gui.elements.UITextEntryLine (
            relative_rect=(1300,360,100,60),
            initial_text=f"{self.tomate_anzahl}",
            manager=self.gui,
            object_id="#eingabe"
        )
        self.gui_tomate_anteil.set_allowed_characters(["0","1","2","3","4","5","6","7","8","9","."])
        self.gui_tomate_anteil.set_text_length_limit(3)
        self.gui_zwiebel = pygame_gui.elements.UILabel (
            relative_rect=(1420,360,370,60),
            text=f"Zwiebel ({ZWIEBEL_PRO_DOENER}/D., {ZWIEBEL_KOSTEN}€/St.):",
            manager=self.gui,
            object_id="#normal"
        )
        self.gui_zwiebel_anteil = pygame_gui.elements.UITextEntryLine (
            relative_rect=(1800,360,100,60),
            initial_text=f"{self.zwiebel_anzahl}",
            manager=self.gui,
            object_id="#eingabe"
        )
        self.gui_zwiebel_anteil.set_allowed_characters(["0","1","2","3","4","5","6","7","8","9","."])
        self.gui_gurke = pygame_gui.elements.UILabel (
            relative_rect=(20,430,310,60),
            text=f"Gurke ({GURKE_PRO_DOENER}/D., {GURKE_KOSTEN}€/St.):",
            manager=self.gui,
            object_id="#normal"
        )
        self.gui_gurke_anteil = pygame_gui.elements.UITextEntryLine (
            relative_rect=(320,430,100,60),
            initial_text=f"{self.gurke_anzahl}",
            manager=self.gui,
            object_id="#eingabe"
        )
        self.gui_gurke_anteil.set_allowed_characters(["0","1","2","3","4","5","6","7","8","9","."])
        self.gui_weißkohl = pygame_gui.elements.UILabel (
            relative_rect=(430,430,410,60),
            text=f"g Weißkohl ({WEISSKOHL_PRO_DOENER}g/D., {WEISSKOHL_KOSTEN}€/g):",
            manager=self.gui,
            object_id="#normal"
        )
        self.gui_weißkohl_anteil = pygame_gui.elements.UITextEntryLine (
            relative_rect=(850,430,100,60),
            initial_text=f"{self.weißkohl_anzahl}",
            manager=self.gui,
            object_id="#eingabe"
        )
        self.gui_weißkohl_anteil.set_allowed_characters(["0","1","2","3","4","5","6","7","8","9","."])
        self.gui_weißkohl_anteil.set_text_length_limit(3)
        self.gui_rotkohl = pygame_gui.elements.UILabel (
            relative_rect=(970,430,400,60),
            text=f"g Rotkohl ({ROTKOHL_PRO_DOENER}g/D., {ROTKOHL_KOSTEN}€/g):",
            manager=self.gui,
            object_id="#normal"
        )
        self.gui_rotkohl_anteil = pygame_gui.elements.UITextEntryLine (
            relative_rect=(1370,430,100,60),
            initial_text=f"{self.rotkohl_anzahl}",
            manager=self.gui,
            object_id="#eingabe"
        )
        self.gui_rotkohl_anteil.set_allowed_characters(["0","1","2","3","4","5","6","7","8","9","."])
        self.gui_rotkohl_anteil.set_text_length_limit(3)
        self.gui_feta = pygame_gui.elements.UILabel (
            relative_rect=(1480,430,400,60),
            text=f"g Feta ({FETA_PRO_DOENER}g/D., {FETA_KOSTEN}€/g):",
            manager=self.gui,
            object_id="#normal"
        )
        self.gui_feta_anteil = pygame_gui.elements.UITextEntryLine (
            relative_rect=(1810,430,100,60),
            initial_text=f"{self.feta_anzahl}",
            manager=self.gui,
            object_id="#eingabe"
        )
        self.gui_feta_anteil.set_allowed_characters(["0","1","2","3","4","5","6","7","8","9","."])
        self.gui_feta_anteil.set_text_length_limit(3)
        self.gui_joghurtsoße = pygame_gui.elements.UILabel (
            relative_rect=(20,540,470,60),
            text=f"g Joghurtsoße ({JOGHURTSOSSE_PRO_DOENER}g/D., {JOGHURTSOSSE_KOSTEN}€/g):",
            manager=self.gui,
            object_id="#normal"
        )
        self.gui_joghurtsoße_anteil = pygame_gui.elements.UITextEntryLine (
            relative_rect=(490,540,100,60),
            initial_text=f"{self.joghurtsoße_anzahl}",
            manager=self.gui,
            object_id="#eingabe"
        )
        self.gui_joghurtsoße_anteil.set_allowed_characters(["0","1","2","3","4","5","6","7","8","9","."])
        self.gui_knoblauchsoße = pygame_gui.elements.UILabel (
            relative_rect=(600,540,500,60),
            text=f"g Knoblauchsoße ({KNOBLAUCHSOSSE_PRO_DOENER}g/D., {KNOBLAUCHSOSSE_KOSTEN}€/g):",
            manager=self.gui,
            object_id="#normal"
        )
        self.gui_knoblauchsoße_anteil = pygame_gui.elements.UITextEntryLine (
            relative_rect=(1110,540,100,60),
            initial_text=f"{self.knoblauchsoße_anzahl}",
            manager=self.gui,
            object_id="#eingabe"
        )
        self.gui_knoblauchsoße_anteil.set_allowed_characters(["0","1","2","3","4","5","6","7","8","9","."])
        self.gui_knoblauchsoße_anteil.set_text_length_limit(4)
        self.gui_scharfesoße = pygame_gui.elements.UILabel (
            relative_rect=(1220,540,530,60),
            text=f"g Scharfe Soße ({SCHARFESOSSE_PRO_DOENER}g/D., {SCHARFESOSSE_KOSTEN}€/g):",
            manager=self.gui,
            object_id="#normal"
        )
        self.gui_scharfesoße_anteil = pygame_gui.elements.UITextEntryLine (
            relative_rect=(1740,540,100,60),
            initial_text=f"{self.scharfesoße_anzahl}",
            manager=self.gui,
            object_id="#eingabe"
        )
        self.gui_scharfesoße_anteil.set_allowed_characters(["0","1","2","3","4","5","6","7","8","9","."])
        self.gui_brot = pygame_gui.elements.UILabel (
            relative_rect=(20,650,370,60),
            text=f"Fladenbrot ({BROT_PRO_DOENER}/D., {BROT_KOSTEN}€/St.):",
            manager=self.gui,
            object_id="#normal"
        )
        self.gui_brot_anteil = pygame_gui.elements.UITextEntryLine (
            relative_rect=(400,650,100,60),
            initial_text=f"{self.brot_anzahl}",
            manager=self.gui,
            object_id="#eingabe"
        )
        self.gui_brot_anteil.set_allowed_characters(["0","1","2","3","4","5","6","7","8","9","."])
        self.gui_dönerpreis_festlegen_info = pygame_gui.elements.UILabel (
            relative_rect=(0,880,1920,60),
            text=f"Ein Döner mit allem würde Sie {self.kosten_pro_döner} € kosten. Sie erwarten {self.nachfragefaktor} Kunden. Ihr Einkauf kostet {self.zutaten_einkauf_kosten} €.",
            manager=self.gui,
            object_id="#normal_zentriert"
        )
        self.gui_dönerpreis_festlegen_info2 = pygame_gui.elements.UILabel (
            relative_rect=(580,970,270,60),
            text="Ihr Preis in €:",
            manager=self.gui,
            object_id="#normal"
        )
        self.gui_dönerpreis_festlegen = pygame_gui.elements.UITextEntryLine (
            relative_rect=(800,950,400,100),
            initial_text=f"{self.dönerpreis}",
            manager=self.gui,
            object_id="#große_eingabe"
        )
        self.gui_dönerpreis_festlegen.set_allowed_characters(["0","1","2","3","4","5","6","7","8","9","."])
        self.gui_zutaten_geräte = pygame_gui.elements.UIButton (
            relative_rect=(20,970,300,90),
            text="Geräte kaufen",
            manager=self.gui,
            object_id="#kleiner_button"
        )
        self.gui_zutaten_automatisch_ausfüllen = pygame_gui.elements.UIButton (
            relative_rect=(1500,750,400,90),
            text="Automatisch ausfüllen",
            manager=self.gui,
            object_id="#kleiner_button"
        )
        self.gui_zutaten_weiter = pygame_gui.elements.UIButton (
            relative_rect=(1600,970,300,90),
            text="Weiter",
            manager=self.gui,
            object_id="#kleiner_button"
        )
        # initial_text wird bei element.text, was man für z.B. kosten_pro_döner_ermitteln() braucht, nicht ausgegeben (argh!),
        # deswegen muss man für jedes element noch element.set_text (eben mit der methode unten) machen
        self.zutaten_anteile_automatisch_ausfüllen()
        self.nachfragefaktor_aktualisieren() # <- nicht, weil sonst der Dönerpreis astronomisch wird (irgendwas mit nachfragefaktor_initial oder so läuft da schief :/)

    def zutatenmenü_abbauen(self):
        self.gui_zutaten_text.kill()
        self.gui_zutaten_info.kill()
        self.gui_zutaten_kapital.kill()
        self.gui_spießgewicht_info.kill()
        self.gui_spießgewicht.kill()
        self.gui_kalb.kill()
        self.gui_kalb_anteil.kill()
        self.gui_huhn.kill()
        self.gui_huhn_anteil.kill()
        self.gui_hack.kill()
        self.gui_hack_anteil.kill()
        self.gui_falafel.kill()
        self.gui_falafel_anteil.kill()
        self.gui_salat.kill()
        self.gui_salat_anteil.kill()
        self.gui_tomate.kill()
        self.gui_tomate_anteil.kill()
        self.gui_zwiebel.kill()
        self.gui_zwiebel_anteil.kill()
        self.gui_gurke.kill()
        self.gui_gurke_anteil.kill()
        self.gui_weißkohl.kill()
        self.gui_weißkohl_anteil.kill()
        self.gui_rotkohl.kill()
        self.gui_rotkohl_anteil.kill()
        self.gui_feta.kill()
        self.gui_feta_anteil.kill()
        self.gui_joghurtsoße.kill()
        self.gui_joghurtsoße_anteil.kill()
        self.gui_knoblauchsoße.kill()
        self.gui_knoblauchsoße_anteil.kill()
        self.gui_scharfesoße.kill()
        self.gui_scharfesoße_anteil.kill()
        self.gui_brot.kill()
        self.gui_brot_anteil.kill()
        self.gui_dönerpreis_festlegen_info.kill()
        self.gui_dönerpreis_festlegen_info2.kill()
        self.gui_dönerpreis_festlegen.kill()
        self.gui_zutaten_automatisch_ausfüllen.kill()
        self.gui_zutaten_geräte.kill()
        self.gui_zutaten_weiter.kill()
        self.fenster.fill((40,40,40))

    def kosten_pro_döner_ermitteln(self):
        if self.laden1:
                self.falafel_faktor = LADEN1_FALAFELFAKTOR
        if self.laden2:
            self.falafel_faktor = LADEN2_FALAFELFAKTOR
        if self.laden3:
            self.falafel_faktor = LADEN3_FALAFELFAKTOR
        gesamt = (
            (1 - self.falafel_faktor) * (
                probieren(lambda: (float(self.gui_kalb_anteil.text)/100) * SPIESS_PRO_DOENER * KALB_KOSTEN) + # float() wandelt den Text in der Eingabe in eine Dezimalzahl um, damit gerechnet werden kann (double gibt es laut Reddit in Python nicht)
                probieren(lambda: (float(self.gui_huhn_anteil.text)/100) * SPIESS_PRO_DOENER * HUHN_KOSTEN) + 
                probieren(lambda: (float(self.gui_hack_anteil.text)/100) * SPIESS_PRO_DOENER * HACK_KOSTEN) ) +
            self.falafel_faktor * (FALAFEL_PRO_DOENER * FALAFEL_KOSTEN) +
            (SALAT_PRO_DOENER * SALAT_KOSTEN)  + 
            (TOMATE_PRO_DOENER * TOMATE_KOSTEN) + 
            (ZWIEBEL_PRO_DOENER * ZWIEBEL_KOSTEN) + 
            (GURKE_PRO_DOENER * GURKE_KOSTEN) + 
            (WEISSKOHL_PRO_DOENER * WEISSKOHL_KOSTEN) + 
            (ROTKOHL_PRO_DOENER * ROTKOHL_KOSTEN) + 
            (FETA_PRO_DOENER * FETA_KOSTEN) +
            (JOGHURTSOSSE_PRO_DOENER * JOGHURTSOSSE_KOSTEN) + 
            (KNOBLAUCHSOSSE_PRO_DOENER * KNOBLAUCHSOSSE_KOSTEN) + 
            (SCHARFESOSSE_PRO_DOENER * SCHARFESOSSE_KOSTEN) +
            BROT_KOSTEN # Veraltet: probieren(lambda: float(self.brot_anteil.text) / (float(self.brot_anteil.text) * BROT_PRO_DOENER) * BROT_KOSTEN)
        )
        return round(gesamt, 2) # rundet auf 2 Nachkommastellen

    def zutaten_kosten_ermitteln(self):
        gesamt = (
            probieren(lambda: float(self.gui_kalb_anteil.text)/100 * (float(self.gui_spießgewicht.text) - self.spießgewicht_gewicht) * KALB_KOSTEN) +
            probieren(lambda: float(self.gui_huhn_anteil.text)/100 * (float(self.gui_spießgewicht.text) - self.spießgewicht_gewicht) * HUHN_KOSTEN) + 
            probieren(lambda: float(self.gui_hack_anteil.text)/100 * (float(self.gui_spießgewicht.text) - self.spießgewicht_gewicht) * HACK_KOSTEN) +
            probieren(lambda: (float(self.gui_falafel_anteil.text) - self.falafel_anzahl) * FALAFEL_KOSTEN) +
            probieren(lambda: (float(self.gui_salat_anteil.text) - self.salat_anzahl) * SALAT_KOSTEN) + 
            probieren(lambda: (float(self.gui_tomate_anteil.text) - self.tomate_anzahl) * TOMATE_KOSTEN) +
            probieren(lambda: (float(self.gui_zwiebel_anteil.text) - self.zwiebel_anzahl) * ZWIEBEL_KOSTEN) + 
            probieren(lambda: (float(self.gui_gurke_anteil.text) - self.gurke_anzahl) * GURKE_KOSTEN) + 
            probieren(lambda: (float(self.gui_weißkohl_anteil.text) - self.weißkohl_anzahl) * WEISSKOHL_KOSTEN) + 
            probieren(lambda: (float(self.gui_rotkohl_anteil.text) - self.rotkohl_anzahl) * ROTKOHL_KOSTEN) + 
            probieren(lambda: (float(self.gui_feta_anteil.text) - self.feta_anzahl) * FETA_KOSTEN) +
            probieren(lambda: (float(self.gui_joghurtsoße_anteil.text) - self.joghurtsoße_anzahl) * JOGHURTSOSSE_KOSTEN) +
            probieren(lambda: (float(self.gui_knoblauchsoße_anteil.text) - self.knoblauchsoße_anzahl) * KNOBLAUCHSOSSE_KOSTEN) +
            probieren(lambda: (float(self.gui_scharfesoße_anteil.text) - self.scharfesoße_anzahl) * SCHARFESOSSE_KOSTEN) +
            probieren(lambda: (float(self.gui_brot_anteil.text) - self.brot_anzahl) * BROT_KOSTEN)
        )
        return round(gesamt, 2)

    def zutaten_kosten_aktualisieren(self):
        # es können Fehler passieren, z.B. durch 0 teilen oder so, 
        # dieses try (versuche) & except (wenn voriges einen Fehler ergeben hat, tu das) ist ne Absicherung, damit das Spiel nicht abstürzt
        try: 
            self.kosten_pro_döner = self.kosten_pro_döner_ermitteln()
            self.zutaten_einkauf_kosten = self.zutaten_kosten_ermitteln()
        except:
            self.kosten_pro_döner = 0
            self.zutaten_einkauf_kosten = 0
        self.gui_dönerpreis_festlegen_info.set_text(f"Ein Döner mit allem würde Sie {self.kosten_pro_döner} € kosten. Sie erwarten {self.nachfragefaktor} Kunden. Ihr Einkauf kostet {self.zutaten_einkauf_kosten} €.")

    def zutaten_anteile_automatisch_ausfüllen(self):
        self.nachfragefaktor = int(round(self.nachfragefaktor)) # Absicherung, gab mehrere Probleme mit nicht-ints
        if self.laden1:
            self.falafel_faktor = LADEN1_FALAFELFAKTOR
        if self.laden2:
            self.falafel_faktor = LADEN2_FALAFELFAKTOR
        if self.laden3:
            self.falafel_faktor = LADEN3_FALAFELFAKTOR

        self.gui_spießgewicht.set_text(f"{max((math.ceil(self.nachfragefaktor * SPIESS_PRO_DOENER)), SPIESS_PRO_DOENER)}") # math.ceil heißt aufrunden
        self.gui_kalb_anteil.set_text(f"{self.spieß_kalb_anteil}")
        self.gui_huhn_anteil.set_text(f"{self.spieß_huhn_anteil}")
        self.gui_hack_anteil.set_text(f"{self.spieß_hack_anteil}")
        self.gui_falafel_anteil.set_text(f"{max((math.ceil(self.nachfragefaktor * self.falafel_faktor * FALAFEL_PRO_DOENER)), FALAFEL_PRO_DOENER)}") # man kann nicht weniger Falafel kaufen, als man für einen Döner braucht
        self.gui_salat_anteil.set_text(f"{self.nachfragefaktor * SALAT_PRO_DOENER}")
        self.gui_tomate_anteil.set_text(f"{max((math.ceil(self.nachfragefaktor * TOMATE_PRO_DOENER)), TOMATE_PRO_DOENER)}")
        self.gui_zwiebel_anteil.set_text(f"{max((math.ceil(self.nachfragefaktor * ZWIEBEL_PRO_DOENER)), ZWIEBEL_PRO_DOENER)}")
        self.gui_gurke_anteil.set_text(f"{max((math.ceil(self.nachfragefaktor * GURKE_PRO_DOENER)), GURKE_PRO_DOENER)}")
        self.gui_weißkohl_anteil.set_text(f"{max((self.nachfragefaktor * WEISSKOHL_PRO_DOENER), WEISSKOHL_PRO_DOENER)}")
        self.gui_rotkohl_anteil.set_text(f"{max((self.nachfragefaktor * ROTKOHL_PRO_DOENER), ROTKOHL_PRO_DOENER)}")
        self.gui_feta_anteil.set_text(f"{max((self.nachfragefaktor * FETA_PRO_DOENER), FETA_PRO_DOENER)}")
        self.gui_joghurtsoße_anteil.set_text(f"{max((self.nachfragefaktor * JOGHURTSOSSE_PRO_DOENER), JOGHURTSOSSE_PRO_DOENER)}")
        self.gui_knoblauchsoße_anteil.set_text(f"{max((self.nachfragefaktor * KNOBLAUCHSOSSE_PRO_DOENER), KNOBLAUCHSOSSE_PRO_DOENER)}")
        self.gui_scharfesoße_anteil.set_text(f"{max((self.nachfragefaktor * SCHARFESOSSE_PRO_DOENER), SCHARFESOSSE_PRO_DOENER)}")
        self.gui_brot_anteil.set_text(f"{self.nachfragefaktor * BROT_PRO_DOENER}")
        self.gui_dönerpreis_festlegen_info.set_text(f"Ein Döner mit allem würde Sie {self.kosten_pro_döner} € kosten. Sie erwarten {self.nachfragefaktor} Kunden. Ihr Einkauf kostet {self.zutaten_einkauf_kosten} €.")

    def zutaten_mengen_übernehmen(self): # setzt die Variablen zu dem, was in den Eingaben steht
        self.spießgewicht_gewicht = round(float(self.gui_spießgewicht.text))
        self.spieß_hack_anteil = round(float(self.gui_hack_anteil.text))
        self.spieß_huhn_anteil = round(float(self.gui_huhn_anteil.text))
        self.spieß_kalb_anteil = round(float(self.gui_kalb_anteil.text))
        self.falafel_anzahl = round(float(self.gui_falafel_anteil.text))
        self.salat_anzahl = round(float(self.gui_salat_anteil.text))
        self.tomate_anzahl = round(float(self.gui_tomate_anteil.text))
        self.zwiebel_anzahl = round(float(self.gui_zwiebel_anteil.text))
        self.gurke_anzahl = round(float(self.gui_gurke_anteil.text))
        self.rotkohl_anzahl = round(float(self.gui_rotkohl_anteil.text))
        self.weißkohl_anzahl = round(float(self.gui_weißkohl_anteil.text))
        self.feta_anzahl = round(float(self.gui_feta_anteil.text))
        self.joghurtsoße_anzahl = round(float(self.gui_joghurtsoße_anteil.text))
        self.knoblauchsoße_anzahl = round(float(self.gui_knoblauchsoße_anteil.text))
        self.scharfesoße_anzahl = round(float(self.gui_scharfesoße_anteil.text))
        self.brot_anzahl = round(float(self.gui_brot_anteil.text))

        self.spießgewicht_gewicht_initial = round(float(self.gui_spießgewicht.text))
        self.falafel_anzahl_initial = round(float(self.gui_falafel_anteil.text))
        self.salat_anzahl_initial = round(float(self.gui_salat_anteil.text))
        self.tomate_anzahl_initial = round(float(self.gui_tomate_anteil.text))
        self.zwiebel_anzahl_initial = round(float(self.gui_zwiebel_anteil.text))
        self.gurke_anzahl_initial = round(float(self.gui_gurke_anteil.text))
        self.rotkohl_anzahl_initial = round(float(self.gui_rotkohl_anteil.text))
        self.weißkohl_anzahl_initial = round(float(self.gui_weißkohl_anteil.text))
        self.feta_anzahl_initial = round(float(self.gui_feta_anteil.text))
        self.joghurtsoße_anzahl_initial = round(float(self.gui_joghurtsoße_anteil.text))
        self.knoblauchsoße_anzahl_initial = round(float(self.gui_knoblauchsoße_anteil.text))
        self.scharfesoße_anzahl_initial = round(float(self.gui_scharfesoße_anteil.text))

    def nachfragefaktor_aktualisieren(self):
        self.kosten_pro_döner = self.kosten_pro_döner_ermitteln()
        self.dönerpreis = round(float(wenn_keine_zahl_0(self.gui_dönerpreis_festlegen.text)), 2)
        self.profit = self.dönerpreis - self.kosten_pro_döner
        self.nachfragefaktor = max((int(round((self.nachfragefaktor_initial - 0.25*(round(self.profit * self.bewertungsfaktor))), 2))), 0)
        self.kunden_für_den_tag = self.nachfragefaktor
        self.gui_dönerpreis_festlegen_info.set_text(f"Ein Döner mit allem würde Sie {self.kosten_pro_döner} € kosten. Sie erwarten {self.nachfragefaktor} Kunden. Ihr Einkauf kostet {self.zutaten_einkauf_kosten} €.")

    def ladenmenü_bauen(self):
        #self.fenster.fill((40,40,40))
        self.gui_bewertung_info = pygame_gui.elements.UILabel (
            relative_rect=(30,30,120,30),
            text="Bewertung: ",
            manager=self.gui,
            object_id="#normal_klein"
        )
        self.gui_bewertung = pygame_gui.elements.UIProgressBar (
            relative_rect=(150,30,350,30),
            manager=self.gui,
            object_id="#bewertung",
        )
        self.gui_bewertungen_anzahl = pygame_gui.elements.UILabel (
            relative_rect=(510,30,100,30),
            text=f"({self.bewertungen_anzahl})",
            manager=self.gui,
            object_id="#normal_klein"
        )
        self.ladenmenü_zeitbefehle_umschalten("starten")
        self.gui_zeit_anzeige = pygame_gui.elements.UILabel (
            relative_rect=(850,30,220,30),
            text=f"Zeit: {self.ingame_stunde:02d}:{self.ingame_minute:02d} Uhr",
            manager=self.gui,
            object_id="#normal_klein"
        )
        self.gui_ladenmenü_kapital = pygame_gui.elements.UILabel (
            relative_rect=(1100,30,300,30),
            text=f"Kapital: {self.kapital} €",
            manager=self.gui,
            object_id="#normal_klein"
        )
        self.gui_ladenmenü_müll = pygame_gui.elements.UIButton (
            relative_rect=(1330,25,100,40),
            text="Müll",
            manager=self.gui,
            object_id="#kleiner_roter_button"
        )
        self.gui_ladenmenü_tag_beenden = pygame_gui.elements.UIButton (
            relative_rect=(1460,25,170,40),
            text="Tag beenden",
            manager=self.gui,
            object_id="#kleiner_roter_button"
        )
        self.gui_ladenmenü_verlassen = pygame_gui.elements.UIButton (
            relative_rect=(1660,25,230,40),
            text="Zurück zum Desktop",
            manager=self.gui,
            object_id="#kleiner_roter_button"
        )
        self.gui_ladenmenü_döner = pygame_gui.elements.UILabel (
            relative_rect=(5,0,1910,13),
            text=f"{self.döner}",
            manager=self.gui,
            object_id="#normal_mini_zentriert"
        )

    def ladenmenü_zeitbefehle_umschalten(self, befehl):
        if befehl == "starten": # Button am Anfang
             self.gui_starten = pygame_gui.elements.UIButton (
                relative_rect=(700,30,120,30),
                text="Starten",
                manager=self.gui,
                object_id="#mini_button"
            )
        if befehl == "weiter": # Button nach Pause (Weiter)
            self.gui_weiter = pygame_gui.elements.UIButton (
                relative_rect=(700,30,120,30),
                text="Weiter",
                manager=self.gui,
                object_id="#mini_button"
            )
            button_kill_probieren(self.gui_starten)
            button_kill_probieren(self.gui_pausieren)
        if befehl == "pausieren": # Button nach Weiter (Pausieren)
            self.gui_pausieren = pygame_gui.elements.UIButton (
                relative_rect=(700,30,120,30),
                text="Pausieren",
                manager=self.gui,
                object_id="#mini_button"
            )
            button_kill_probieren(self.gui_weiter)

    def ladenmenü_abbauen(self):
        self.gui_bewertung_info.kill()
        self.gui_bewertung.kill()
        self.gui_bewertungen_anzahl.kill()
        button_kill_probieren(self.gui_starten)
        button_kill_probieren(self.gui_pausieren)
        button_kill_probieren(self.gui_weiter)
        self.gui_zeit_anzeige.kill()
        self.gui_ladenmenü_kapital.kill()
        self.gui_ladenmenü_verlassen.kill()
        self.gui_ladenmenü_müll.kill()
        self.gui_ladenmenü_tag_beenden.kill()
        self.gui_ladenmenü_döner.kill()

    def ladenmenü_spieß_bauen(self):
        if self.spieß_gargrad == "roh":
            self.fenster.blit(self.bild_spieß_roh, (0, 0))
        elif self.spieß_gargrad == "gegart":
            self.fenster.blit(self.bild_spieß_gegart, (0, 0))
        elif self.spieß_gargrad == "verkokelt":
            self.fenster.blit(self.bild_spieß_verkokelt, (0, 0))

        if self.fleischteller == "":
            self.fenster.blit(self.bild_fleischteller_leer, (0, 0))
        elif self.fleischteller == "roh":
            self.fenster.blit(self.bild_fleischteller_roh, (0, 0))
        elif self.fleischteller == "gegart":
            self.fenster.blit(self.bild_fleischteller_gegart, (0, 0))
        elif self.fleischteller == "verkokelt":
            self.fenster.blit(self.bild_fleischteller_verkokelt, (0, 0))

    def ladenmenü_elemente_bauen(self):
        self.fenster.blit(self.bild_falafel_voll, (0, 0))
        self.fenster.blit(self.bild_salat_voll, (0, 0))
        self.fenster.blit(self.bild_tomate_voll, (0, 0))
        self.fenster.blit(self.bild_zwiebel_voll, (0, 0))
        self.fenster.blit(self.bild_gurke_voll, (0, 0))
        self.fenster.blit(self.bild_rotkohl_voll, (0, 0))
        self.fenster.blit(self.bild_weißkohl_voll, (0, 0))
        self.fenster.blit(self.bild_feta_voll, (0, 0))
        self.fenster.blit(self.bild_joghurtsoße_voll, (0, 0))
        self.fenster.blit(self.bild_knoblauchsoße_voll, (0, 0))
        self.fenster.blit(self.bild_scharfesoße_voll, (0, 0))
        self.fenster.blit(self.bild_brot_voll, (0, 0))
        if self.brotgrill1_gekauft:
            self.fenster.blit(self.bild_toaster, (0, 0))
        elif self.brotgrill2_gekauft:
            self.fenster.blit(self.bild_optigrill, (0, 0))
        elif self.brotgrill3_gekauft:
            self.fenster.blit(self.bild_optigrill_groß, (0, 0)) 

    def ladenmenü_anzeigen_bauen(self):
        self.gui_laden_spieß_zustand = pygame_gui.elements.UIProgressBar (
            relative_rect=(200,340,120,30),
            manager=self.gui,
            object_id="#bewertung",
        )
        self.gui_laden_spieß_menge = pygame_gui.elements.UIProgressBar (
            relative_rect=(200,380,120,30),
            manager=self.gui,
            object_id="#bewertung",
        )
        anzeige_100_setzen(self.spießgewicht_gewicht, self.gui_laden_spieß_menge)
        self.gui_laden_falafel_menge = pygame_gui.elements.UIProgressBar (
            relative_rect=(375,775,125,30),
            manager=self.gui,
            object_id="#bewertung",
        )
        anzeige_100_setzen(self.falafel_anzahl, self.gui_laden_falafel_menge)
        self.gui_laden_salat_menge = pygame_gui.elements.UIProgressBar (
            relative_rect=(500,775,110,30),
            manager=self.gui,
            object_id="#bewertung",
        )
        anzeige_100_setzen(self.salat_anzahl, self.gui_laden_salat_menge)
        self.gui_laden_tomate_menge = pygame_gui.elements.UIProgressBar (
            relative_rect=(610,775,100,30),
            manager=self.gui,
            object_id="#bewertung",
        )
        anzeige_100_setzen(self.tomate_anzahl, self.gui_laden_tomate_menge)
        self.gui_laden_zwiebel_menge = pygame_gui.elements.UIProgressBar (
            relative_rect=(710,775,100,30),
            manager=self.gui,
            object_id="#bewertung",
        )
        anzeige_100_setzen(self.zwiebel_anzahl, self.gui_laden_zwiebel_menge)
        self.gui_laden_gurke_menge = pygame_gui.elements.UIProgressBar (
            relative_rect=(810,775,90,30),
            manager=self.gui,
            object_id="#bewertung",
        )
        anzeige_100_setzen(self.gurke_anzahl, self.gui_laden_gurke_menge)
        self.gui_laden_rotkohl_menge = pygame_gui.elements.UIProgressBar (
            relative_rect=(900,775,90,30),
            manager=self.gui,
            object_id="#bewertung",
        )
        anzeige_100_setzen(self.rotkohl_anzahl, self.gui_laden_rotkohl_menge)
        self.gui_laden_weißkohl_menge = pygame_gui.elements.UIProgressBar (
            relative_rect=(990,775,100,30),
            manager=self.gui,
            object_id="#bewertung",
        )
        anzeige_100_setzen(self.weißkohl_anzahl, self.gui_laden_weißkohl_menge)
        self.gui_laden_feta_menge = pygame_gui.elements.UIProgressBar (
            relative_rect=(1090,775,90,30),
            manager=self.gui,
            object_id="#bewertung",
        )
        anzeige_100_setzen(self.feta_anzahl, self.gui_laden_feta_menge)
        self.gui_laden_joghurtsoße_menge = pygame_gui.elements.UIProgressBar (
            relative_rect=(1180,775,100,30),
            manager=self.gui,
            object_id="#bewertung",
        )
        anzeige_100_setzen(self.joghurtsoße_anzahl, self.gui_laden_joghurtsoße_menge)
        self.gui_laden_knoblauchsoße_menge = pygame_gui.elements.UIProgressBar (
            relative_rect=(1280,775,90,30),
            manager=self.gui,
            object_id="#bewertung",
        )
        anzeige_100_setzen(self.knoblauchsoße_anzahl, self.gui_laden_knoblauchsoße_menge)
        self.gui_laden_scharfesoße_menge = pygame_gui.elements.UIProgressBar (
            relative_rect=(1370,775,110,30),
            manager=self.gui,
            object_id="#bewertung",
        )
        anzeige_100_setzen(self.scharfesoße_anzahl, self.gui_laden_scharfesoße_menge)
        self.gui_laden_brot_menge = pygame_gui.elements.UILabel (
            relative_rect=(1350,600,120,30),
            text=str(self.brot_anzahl),
            manager=self.gui,
            object_id="#mini_button",
        )
        self.gui_laden_brotgrill_menge = pygame_gui.elements.UILabel (
            relative_rect=(1745,700,30,30),
            text=str(self.brot_im_brotgrill),
            manager=self.gui,
            object_id="#mini_button",
        )
        self.gui_laden_brotgrill_zustand = pygame_gui.elements.UIProgressBar (
            relative_rect=(1700,740,120,30),
            manager=self.gui,
            object_id="#bewertung",
        )
        
    def ladenmenü_anzeigen_abbauen(self):
        self.gui_laden_spieß_zustand.kill()
        self.gui_laden_spieß_menge.kill()
        self.gui_laden_falafel_menge.kill()
        self.gui_laden_salat_menge.kill()
        self.gui_laden_tomate_menge.kill()
        self.gui_laden_zwiebel_menge.kill()
        self.gui_laden_gurke_menge.kill()
        self.gui_laden_rotkohl_menge.kill()
        self.gui_laden_weißkohl_menge.kill()
        self.gui_laden_feta_menge.kill()
        self.gui_laden_joghurtsoße_menge.kill()
        self.gui_laden_knoblauchsoße_menge.kill()
        self.gui_laden_scharfesoße_menge.kill()
        self.gui_laden_brot_menge.kill()
        self.gui_laden_brotgrill_menge.kill()
        self.gui_laden_brotgrill_zustand.kill()

    def ladenmenü_döner_bauen(self):
        if self.in_der_hand == [0, "", ""] and self.döner_modus == False:
            return None # skippt den Rest des Codes

        if self.döner.brot == "":
            self.fenster.blit(self.bild_döner_leer, (0, 0))
        if self.döner.falafel:
            self.fenster.blit(self.bild_döner_falafel, (0, 0))
        if self.döner.fleisch != "":
            self.fenster.blit(self.bild_döner_fleisch, (0, 0))

    def döner_abbauen(self):
        setattr(self.döner, "brot", "")
        setattr(self.döner, "fleisch", "")
        setattr(self.döner, "falafel", False)
        setattr(self.döner, "salat", False)
        setattr(self.döner, "tomate", False)
        setattr(self.döner, "zwiebel", False)
        setattr(self.döner, "gurke", False)
        setattr(self.döner, "rotkohl", False)
        setattr(self.döner, "weißkohl", False)
        setattr(self.döner, "feta", False)
        setattr(self.döner, "joghurtsoße", False)
        setattr(self.döner, "knoblauchsoße", False)
        setattr(self.döner, "scharfesoße", False)
        self.gui_ladenmenü_döner.set_text(str(self.döner))
        self.döner_modus = False
        self.in_der_hand = [0, "", ""]

    def ladenmenü_kunde_dialog_bauen(self):
        self.gui_kunde_sprechblase = pygame_gui.elements.UITextBox (
                relative_rect=(660,500,600,100),
                html_text=str(self.aktueller_kunde.bestellungstext()),
                manager=self.gui,
                object_id="#mini_button"
            )
        self.gui_ladenmenü_geben = pygame_gui.elements.UIButton (
            relative_rect=(660,610,290,40),
            text="Döner geben",
            manager=self.gui,
            object_id="#kunde_grüner_button"
        )
        self.gui_ladenmenü_ablehnen = pygame_gui.elements.UIButton (
            relative_rect=(970,610,290,40),
            text="Bestellung ablehnen",
            manager=self.gui,
            object_id="#kunde_roter_button"
        )

    def ladenmenü_kunde_dialog_abbauen(self):
        self.gui_kunde_sprechblase.kill()
        self.gui_ladenmenü_geben.kill()
        self.gui_ladenmenü_ablehnen.kill()

    def elemente_in_hand_döner_nehmen(self, hover, anzahl, pro_döner, name, gui_menge: pygame_gui.elements.UIProgressBar, anzahl_initial):
        if hover:
            # In die Hand nehmen
            if self.in_der_hand == [0, "", ""] and anzahl >= pro_döner and self.döner_modus == False:
                self.in_der_hand = [pro_döner, name, ""]
                setattr(self, f"{name}_anzahl", getattr(self, f"{name}_anzahl") - pro_döner) # setattr braucht man, wenn bei Namespace.x das x eine Variable ist
                gui_menge.set_current_progress(getattr(self, f"{name}_anzahl") / anzahl_initial * 100)
            # In den Döner legen
            elif self.döner_modus == True:
                if name == "falafel" and self.döner.falafel == False:
                    self.döner.falafel = True
                    setattr(self, f"{name}_anzahl", getattr(self, f"{name}_anzahl") - pro_döner)
                    gui_menge.set_current_progress(getattr(self, f"{name}_anzahl") / anzahl_initial * 100)
                    self.gui_ladenmenü_döner.set_text(f"{self.döner}")
                elif name != "falafel" and getattr(self.döner, name) == False:
                    setattr(self.döner, name, True)
                    setattr(self, f"{name}_anzahl", getattr(self, f"{name}_anzahl") - pro_döner)
                    gui_menge.set_current_progress(getattr(self, f"{name}_anzahl") / anzahl_initial * 100)
                    self.gui_ladenmenü_döner.set_text(f"{self.döner}")
            # Zurücklegen
            elif self.in_der_hand[1] == name and self.döner_modus == False:
                setattr(self, f"{name}_anzahl", getattr(self, f"{name}_anzahl") + self.in_der_hand[0])
                gui_menge.set_current_progress(getattr(self, f"{name}_anzahl") / anzahl_initial * 100)
                self.in_der_hand = [0, "", ""]

    def bewertung_aktualisieren(self):
        self.bewertungen_summe += self.aktueller_kunde.bewerten()
        self.bewertungen_anzahl += 1
        if self.bewertungen_anzahl > 0: # sonst Teilung durch 0 ^^, einfach nicht riskieren
            self.bewertung = ((self.bewertungen_summe / 100) / self.bewertungen_anzahl) * 100
        else:
            self.bewertung = 0
        self.gui_bewertung.set_current_progress(self.bewertung)
        self.gui_bewertungen_anzahl.set_text(f"({self.bewertungen_anzahl})")

    def bewertung_aktualisieren_abgelehnt(self):
        # bewertungen_summe bleibt gleich
        self.bewertungen_anzahl += 1
        if self.bewertungen_anzahl > 0:
            self.bewertung = ((self.bewertungen_summe / 100) / self.bewertungen_anzahl) * 100
        else:
            self.bewertung = 0
        self.gui_bewertung.set_current_progress(self.bewertung)
        self.gui_bewertungen_anzahl.set_text(f"({self.bewertungen_anzahl})")

    def neuer_tag(self):
        self.zeit_läuft = False
        self.ingame_minute = 0
        self.ingame_stunde = 0
        self.zeit = 0
        self.kunde_zeit = 0
        self.brotgrill_zeit = 0

        self.in_der_hand = [0, "", ""]
        self.döner_abbauen()
        self.brot_im_brotgrill = 0
        self.fleischteller = ""
        self.spieß_gargrad = "roh"
        self.brot_in_der_hand = False

        self.nachfragefaktor = int(round(self.nachfragefaktor * (self.bewertung/100)*float(f"1.{self.bewertungsfaktor}"))) # letztes: Gute Bewertungen erhöhen Nachfrage (urban: großer Effekt)
        self.nachfragefaktor_initial = self.nachfragefaktor

        self.tag += 1
        if spiel.laden1:
            self.miete = LADEN1_MIETE
        if spiel.laden2:
            self.miete = LADEN2_MIETE
        if spiel.laden3:
            self.miete = LADEN3_MIETE
        self.kapital -= round((self.miete / 30), 2)

        self.ladenmenü_abbauen()
        self.ladenmenü_anzeigen_abbauen()
        if self.kunde_anwesend:
            if self.ladenmenü_kunde_dialog_erstellt:
                self.ladenmenü_kunde_dialog_abbauen()
                self.ladenmenü_kunde_dialog_erstellt = False
        self.kunde_anwesend = False
        self.aktueller_kunde = None
        self.fenster.fill((40,40,40))

        self.menü = "zutatenmenü"
        self.zutatenmenü_bauen()
        


class Kunde:
    def __init__(self):
        spiel.kunde_anwesend = True # für Bild anzeigen
        self.bild_auswahl = random.randint(1,20)
        self.bild_ausgewählt = getattr(spiel, f"bild_kunde_{self.bild_auswahl}")

        if spiel.laden1:
            self.falafel_faktor = LADEN1_FALAFELFAKTOR
        if spiel.laden2:
            self.falafel_faktor = LADEN2_FALAFELFAKTOR
        if spiel.laden3:
            self.falafel_faktor = LADEN3_FALAFELFAKTOR
        if random.random() > self.falafel_faktor: # Wahrscheinlichkeit (random.random gibt Kommazahl zwischen 0 und 1)
            self.will_fleisch = True
        else:
            self.will_fleisch = False

        self.gemüse = []
        self.gemüse_wahl = round(random.gauss(7,2)) # Zufällig, aber Gaussche Verteilung ◞◠◟ (Mittelpunkt, Standardabweichung)
        if self.gemüse_wahl > 7 or self.gemüse_wahl < 0 :
            self.gemüse_wahl = 7 # schneidet die Verteilung auf einer Seite ab ◞◜
        for i in range(self.gemüse_wahl): # wiederhole 7 mal (wie for(i=0,i<7,i++){})
            self.gemüse.append(True)
        if (7 - self.gemüse_wahl) != 0:
            for i in range(7 - self.gemüse_wahl):
                self.gemüse.append(False)
        random.shuffle(self.gemüse) # mischen

        self.soßen = []
        self.soßen_wahl = round(random.gauss(3,1)) 
        if self.soßen_wahl > 3 or self.soßen_wahl < 0:
            self.soßen_wahl = 3
        for i in range(self.soßen_wahl):
            self.soßen.append(True)
        if (3 - self.soßen_wahl) != 0:
            for i in range(3 - self.soßen_wahl):
                self.soßen.append(False)
        random.shuffle(self.soßen)

        self.bestellung = SimpleNamespace(
            fleisch = self.will_fleisch,
            falafel = not self.will_fleisch,
            salat = self.gemüse[0],
            tomate = self.gemüse[1],
            zwiebel = self.gemüse[2],
            gurke = self.gemüse[3],
            rotkohl = self.gemüse[4],
            weißkohl = self.gemüse[5],
            feta = self.gemüse[6],
            joghurtsoße = self.soßen[0],
            knoblauchsoße = self.soßen[1],
            scharfesoße = self.soßen[2]
        )

    def bestellungstext(self):
        text = (
            "Einmal Döner mit " \
            + ("Fleisch" if self.will_fleisch else "Falafel") \
            + (", ohne Salat" if not self.gemüse[0] else "") \
            + (", ohne Tomaten" if not self.gemüse[1] else "") \
            + (", ohne Zwiebeln" if not self.gemüse[2] else "") \
            + (", ohne Gurke" if not self.gemüse[3] else "") \
            + (", ohne Rotkohl" if not self.gemüse[4] else "") \
            + (", ohne Weißkohl" if not self.gemüse[5] else "") \
            + (", ohne Feta" if not self.gemüse[6] else "") \
            + (", ohne Joghurtsoße" if not self.soßen[0] else "") 
            + (", ohne Knoblauchsoße" if not self.soßen[1] else "") \
            + (", ohne Scharf" if not self.soßen[2] else "") \
            + "."
        )
        return text
    
    def bewerten(self):
        self.minuspunkte = 0
        
        self.faktor = 1
        if spiel.laden1:
            self.faktor = LADEN1_BEWERTUNGSFAKTOR
        elif spiel.laden2:
            self.faktor = LADEN2_BEWERTUNGSFAKTOR
        elif spiel.laden3:
            self.faktor = LADEN3_BEWERTUNGSFAKTOR

        def gargrad_abhängig(element):
            if getattr(spiel.döner, element) == "roh":
                self.minuspunkte += 12 * self.faktor
            if getattr(spiel.döner, element) == "verkokelt":
                self.minuspunkte += 12 * self.faktor
            if getattr(spiel.döner, element) == "":
                self.minuspunkte += 25 * self.faktor

        def normal(element):
            if getattr(self.bestellung, element) != getattr(spiel.döner, element):
                    self.minuspunkte += 8 * self.faktor

        gargrad_abhängig("brot")
        if getattr(self.bestellung, "fleisch") == True:
            gargrad_abhängig("fleisch")

        if getattr(self.bestellung, "falafel") != getattr(spiel.döner, "falafel"):
            self.minuspunkte += 22 * self.faktor
        normal("salat")
        normal("tomate")
        normal("zwiebel")
        normal("gurke")
        normal("rotkohl")
        normal("weißkohl")
        normal("feta")
        normal("joghurtsoße")
        normal("knoblauchsoße")
        normal("scharfesoße")

        self.geduld = GEDULD
        if spiel.laden1:
            self.geduld -= LADEN1_BEWERTUNGSFAKTOR
        if spiel.laden2:
            self.geduld -= LADEN2_BEWERTUNGSFAKTOR
        if spiel.laden3:
            self.geduld -= LADEN3_BEWERTUNGSFAKTOR
        if spiel.geduld_zeit > self.geduld:
            self.minuspunkte += spiel.geduld_zeit - self.geduld

        self.minuspunkte += round(int(spiel.gui_hack_anteil.text)/10)
        self.minuspunkte += round(int(spiel.gui_huhn_anteil.text)/20)

        return (100 - self.minuspunkte) if (self.minuspunkte < 100) else 0

# klassenunabhängige Methoden:
def probieren(x): # für kosten_pro_döner_ermitteln() & zutaten_kosten_ermitteln()
    try:
        return x() # x ist eine Methode
    except:
        return 0
    
def wenn_keine_zahl_0(x): # für nachfragefaktor_aktualisieren() (gui_dönerpreis_festlegen kann auch "" sein -> keine Zahl, Spiel würde abstürzen)
    try:
        float(x)
        return x
    except:
        return 0
    
def button_kill_probieren(button: pygame_gui.elements.UIButton): # braucht man, da nicht alle Buttons initialisiert sind (Spielabsturz vermeiden)
    if button != None:
        button.kill()

def anzeige_100_setzen(variable, anzeige: pygame_gui.elements.UIProgressBar):
    if variable == 0:
        anzeige.set_current_progress(0)
    else:
        anzeige.set_current_progress(100)

# START
spiel = Spiel()
spiel.spiel_starten()