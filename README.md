## Open Source EEG Framework

### 1. Hardware- und Geräteverwaltung (Device Management)

Das Framework bietet eine Abstraktionsebene für die verwendete Hardware.

* **Standardisierte EEG-Kanäle:** Verwaltung einer zentralen Bibliothek von Standardkanälen (z. B. Fp1, Cz).
* **Gerätemodelle & Hersteller:** Registrierung von jeglicher Hardware und deren Kategorisierung (z. B. Smartwatch, EEG, Lautsprecher).
* **Hardware-Fähigkeiten (Capabilities):** Definition, welche spezifischen Kanäle ein bestimmtes Gerätemodell überhaupt aufzeichnen kann.
* **Physische Instanzen:** Repräsentiert das tatsächliche Gerät im Labor und mappt, in welcher Spalte des eingehenden Datenstroms oder der Datei die Werte für einen bestimmten Kanal zu finden sind (also auch welche Kanäle verwendet wurden).

### 2. Ereignismarkierung (Trigger System)

Ein robustes System zur zeitgenauen Markierung von Ereignissen.

* **Trigger-Definitionen & Gruppen:** Anlage einzelner Marker und deren Bündelung für spezifische Experimente. Jegliche Datenerfassungs-Files haben, wenn Trigger verwendet wurden, die verwendete Trigger-Gruppe gespeichert.
* **Live-Annotation (Hotkeys):** Flexible Zuweisung von Tastatur-Kürzeln zu Triggern, um in Live-Sitzungen manuell Marker zu setzen.
* **Trigger-Paare als Workflow-Hilfe:** Die logische Verknüpfung von Start- und End-Triggern dient als komfortables "Extra" für die Benutzeroberfläche. Es ermöglicht Nutzern, zusammengehörige Marker schneller und fehlerfrei einer Trigger-Gruppe zuzuweisen, anstatt sie einzeln suchen zu müssen.

### 3. Experiment-Design (Stimulus Management)

Verwaltung der Inhalte, die den Probanden präsentiert werden.

* **Stimuli & Playlisten:** Erstellung von einzelnen Reizen (inklusive optionaler Dauer bei auditiven) und deren Anordnung in sequenziellen Abfolgen, um den exakten Ablauf einer Untersuchung zu choreografieren.

### 4. Dynamische "Entity-Metadata-Registry" Architektur

Das System nutzt eine hochflexible Entity-Metadata-Registry, um das Datenmodell im laufenden Betrieb zu erweitern und für jegliche Art von Studie oder Experiment alle Daten speichern zu können.

* **Funktionsweise für UI und Questionnaires:** Forscher können im System abstrakte Definitionsfelder anlegen (z. B. eine Skala für "Müdigkeit" oder Textfelder für "Koffein-Konsum"). Diese Felder werden in logischen Gruppen gebündelt und über die Registry an bestimmte Tabellen (wie eine Sitzung oder ein Probandenprofil) geknüpft. Dazu kann man dann eine Komponente im Frontend erstellen, welche diese Registry ausliest und daraus vollautomatisch dynamische Eingabemasken (Questionnaires) auf der Seite generiert. Diese gespeicherten Daten können dann später problemlos für Berechnungen oder Auswertungen verwendet werden.
* **Hardware-Einstellungen:** Auf dem gleichen Weg lassen sich gerätespezifische Konfigurationen abbilden. Wird eine bestimmte Hardware in einer Session genutzt, kann das Metadaten-System automatisch die passenden Eingabefelder für beispielsweise Impedanz-Werte, Filter-Settings oder Verstärkereinstellungen generieren. All diese Daten werden flexibel strukturiert gespeichert, völlig ohne dass dafür Programmcode geschrieben werden muss.
* **Allgemein:** Es ist vorallem, bei stark variierenden experimentellen Rahmenbedingungen und zusätzlichen Hilfsmitteln nützlich. Ein praktisches Beispiel ist die Verwendung von Schlafmasken während einer EEG-Aufnahme: Kommt eine Schlafmaske nur bei spezifischen Einzelsitzungen zum Einsatz, kann das entsprechende Metadatenfeld (z. B. "Schlafmaske verwendet") flexibel nur an diese konkreten Sessions geknüpft werden. Ist die Schlafmaske hingegen ein fester, zwingender Bestandteil des gesamten experimentellen Designs, lässt sich das Feld direkt auf der übergeordneten Event-Ebene hinterlegen, sodass es für alle zugehörigen Aufnahmen als Standard gespeichert wird.

### 5. Wissenschaftliches Studien- und Event-Management

* **Übergeordnete Events:** Einzelne Aufzeichnungs-Sitzungen (Sessions) werden unter einem großen "Event" (z. B. einer bestimmten klinischen Studie oder Versuchsreihe) gruppiert.
* **Event-spezifische Seiten/Komponenten:** Für diese Events können Seiten für die Datenaufnahme, Analyse oder Auswertung selber erstellt werden, mit bereitgestellten Komponenten und der zusätzlichen Option, selber Komponenten hierfür zu erstellen, zu erweitern oder anzupassen.

### 6. Multi-Modale Sitzungen & Synchronisation

* **Synchronisierte Bio-Signale:** Das Framework ist in der Lage, parallel zum EEG weitere Sensordaten (wie eine Pulsmessung) aufzuzeichnen. Diese parallelen Datenströme erhalten in Echtzeit exakt dieselben Trigger-Marker wie das EEG-File, was eine zeitliche Synchronisation bei der späteren Analyse garantiert. Zudem kann es selber auditive Stimuli abspielen, sodass die Trigger-Sitzung so exakt wie nur möglich ist, um beispielsweise einzelne Stimuli-Abschnitte später richtig segmentieren zu können.

### 7. Selbsterweiterndes Framework durch Custom Scripts und externe Bibliotheken

* **Integrierte Python-Pipelines:** Um auf extrem individuelle Anforderungen von Studien und Analyse reagieren zu können, bietet das Framework eine "Self-Expanding"-Funktion. Forscher mit entsprechenden Programmierkenntnissen können direkt über das Frontend eigene Python-Skripte schreiben und speichern, um Daten abseits der vorgefertigten Standardkomponenten völlig frei zu analysieren und nach eigenen Wünschen zu visualisieren.
* **Automatisches Mitwachsen durch Bibliothek-Updates:** Für diese eigens geschriebenen Skripte stellt das System (in einer isolierten, sicheren Container-Umgebung)Datenwissenschafts-Bibliotheken wie pandas (zur Datenverarbeitung) und matplotlib (zur Visualisierung) bereit. Das macht das Framework selbsterweiternd: Sobald sich diese externen Bibliotheken weiterentwickeln und neue Features bieten, erweitert sich der potenzielle Funktions- und Visualisierungsumfang des EEG-Frameworks vollautomatisch mit, ohne dass der Kerncode der Plattform dafür jemals angepasst werden muss.

### 8. Maximale Anpassungsfähigkeit durch dynamische Stammdaten- und Kategorienverwaltung

* **Zentrale Stammdatenpflege:** Das Framework verzichtet auf starr einprogrammierte Dropdown-Listen oder fest kodierte Zuordnungen. Stattdessen können Forscher und Administratoren sämtliche Stammdaten, wie neue Hardware-Hersteller, spezifische EEG-Kanäle, Frequenzbänder oder Trigger-Definitionen, jederzeit eigenständig über die Benutzeroberfläche verwalten, anpassen und erweitern.
* **Generisches Kategorien-System:** Ein zentrales Architekturkonzept ist die generische, dynamische Verwaltung aller Systemkategorien. Ob es um die Kategorisierung von Gerätemodellen, Stimuli, selbsterstellten Datenverarbeitungs-Skripten oder Metadaten-Gruppen geht, Nutzer können das System völlig frei strukturieren. Das System adaptiert sich dadurch an die spezifische Nomenklatur und die Organisationsrichtlinien der jeweiligen Labors/Nutzergruppe. Diese tiefe Flexibilität auf administrativer Ebene sorgt dafür, dass das Framework mit neuen Forschungsansätzen und organisatorischen Veränderungen organisch mitwachsen kann, ohne dass dafür Software-Updates oder Code-Anpassungen nötig sind. Zudem ermöglicht es auch überall die Nutzung von Filtern nach Kategorie um die Suche nach spezifischen Elementen zu vereinfachen.

### 9. Mehrsprachigkeit und Internationalisierung (i18n)

* **Zweisprachiges Frontend:** Die gesamte Benutzeroberfläche des Frameworks ist vollständig zweisprachig (Deutsch und Englisch) konzipiert und übersetzt.
* **Originalgetreue Datenspeicherung:** Während sich die Menüs, Warnungen und Systemmeldungen dynamisch der gewählten Sprachessprache anpassen, bleibt das Datenmodell begrenzt: Nutzergenerierte Inhalte (wie Namen von Geräten, Trigger-Beschreibungen oder Antworten in Questionnaires) werden exakt in der Sprache in der Datenbank gespeichert, in der sie vom Nutzer eingegeben wurden.

### 10. Ausführliches Fehler-Handling und Warnlogik

* **Proaktive Datenvalidierung:** Das Framework verfügt über eine tiefe, durchgängige Logik für Fehlermeldungen und Warnungen. Um die Datenintegrität zu wahren, prüft das System Eingaben bereits im Frontend auf logische Fehler (z. B. doppelt vergebene Hotkeys in einer Gruppe oder redundante Gerätenamen), bevor sie überhaupt das Backend erreichen.
* **Geführte Nutzererfahrung (UX):** Anstatt Nutzer durch abrupte Systemabstürze zu frustrieren, werden sie durch  bilinguale Warn-Dialoge (Custom Modals) auf potenziell fehlerhafte oder unvollständige Aktionen hingewiesen (z. B. der Versuch, TriggerGruppe ohne zugewiesene Tasten zu speichern). Dies sorgt für eine flüssige und fehlerresistente Bedienung.

### 11. Post-Session Trigger-Analyse und -Korrektur

* **Effiziente Navigation in massiven Rohdaten:** EEG-Rohdaten liegen typischerweise als gigantische CSV-Dateien mit unzähligen Zeilen (Datenpunkten) vor. Die manuelle Suche nach spezifischen Markern (Trigger) ist in solchen Dateien praktisch unmöglich oder extrem zeitaufwendig. Das Framework bietet hierfür ein dediziertes Analyse-Werkzeug.
* **Sequenz-Visualisierung und Zeilenangabe:** Durch die Kombination aus einer aufgezeichneten EEG-Datei und der zugehörigen Trigger-Gruppe analysiert das System den Datenstrom automatisch. Es visualisiert die gesamte Trigger-Sequenz übersichtlich in der Oberfläche und gibt präzise an, in exakt welcher Zeile der CSV-Datei ein bestimmter Trigger gesetzt wurde.
* **Nachträgliche Fehlerkorrektur:** Wenn während der Live-Aufnahme Fehler passieren (z. B. ein Trigger wurde zu spät, falsch oder versehentlich gar nicht gedrückt), ermöglicht diese Ansicht das einfache Entfernen, Hinzufügen oder Ändern von Triggern im Nachhinein.

### 12. Integration eines freien BCI-Gerüsts

* **Erweiterte Kanalabdeckung:** Durch die Einbindung eines Selbsterstellten EEG-Gerüsts für das von der Hochschule bereitgestellten, freie Brain-Computer Interfaces (BCI), wird die Nutzung und präzisere Erfassung von EEG-Kanälen, die mit den jetzigen EEGs der Hochschule nicht abgedeckt werden konnten, ermöglicht.
* **Optimierte Signalqualität bei unterschiedlichen Frisuren:** Das BCI Gerüst ist strukturell so aufgebaut, dass es den schlechteren Kontakt der Elektroden zur Kopfhaut, bedingt durch unterschiedliche Haartypen, Haardichten oder komplexe Frisuren, reduziert.

### 13. Authentifizierung, objektbasierte Rechteverwaltung und Systemgrenzen

* **Vollständige Login- und Rechteverwaltung:** Das Framework nutzt das Authentifizierungssystem von Django für Kernfunktionen wie Login und Logout. Ein Feature ist die "Object-Level Permission"-Architektur (Rechte auf Datensatz-Ebene). Diese ermöglicht es Administratoren, spezifischen Nutzern (z. B. einzelnen Probanden) gezielt Zugriffsrechte für individuelle, selbsterstellte Seiten zuzuweisen. Ein Proband sieht nach dem Login somit nur exakt die dynamischen Questionnaires oder Session-Ansichten, die ihm explizit freigegeben wurden, und kann diese selbstständig ausfüllen und speichern.
* **Flexible Multi-Device-Nutzung:** Das Rollenkonzept erlaubt somit künftig die Erstellung dedizierter Ansichten für Live-Sitzungen. So kann ein Proband während einer laufenden EEG-Aufnahme auf einem separaten Gerät (z. B. einem Tablet) eine spezifisch für ihn freigegebene Seite bedienen, während die Forscher auf ihrem Hauptbildschirm durch ihre administrativen Rechte die volle Kontrolle behalten. Allgemein entfällt die Notwendigkeit, dass der Proband das gleiche Gerät wie der Datenerfasser nutzen muss, um Eingaben zu tätigen. Der webbasierte Ansatz des EEG-Frameworks bietet zudem die problemlose Einbindung von Tablets oder die Nutzung persönlicher Geräte der Teilnehmenden (Bring Your Own Device).
* **Pragmatische, lokale Datenspeicherung:** Im Rahmen des Entwicklungszeitraums der Masterarbeit wurde bewusst auf ein hochkomplexes, verteiltes Datenspeichersystem (wie Cloud-Buckets oder spezialisierte Zeitreihen-Datenbanken) verzichtet. Die anfallenden Dateien, was neben den großen EEG-Rohdaten ausdrücklich auch sämtliche Stimuli-Dateien (z. B. Medien) sowie die synchronisierten Aufzeichnungen der Pulsmessung umfasst, werden stattdessen pragmatisch und effizient in einem einfachen lokalen Ordner (Local Folder im Root-Verzeichnis) gespeichert. Für den aktuellen Laborbetrieb und den Proof-of-Concept ist dieser Ansatz völlig ausreichend.
* **Fokus auf lokale Ausführungsumgebung:** Aus zeitlichen Aspekten beschränkt sich das Projekt in dieser Phase auf eine reine lokale Ausführungsumgebung (Localhost). Auf aufwändige DevOps-Prozesse wie Staging-Verfahren, automatisierte Release-Pipelines (CI/CD) oder das Hosting auf externen Servern wurde verzichtet. Die saubere architektonische Trennung von Backend (Django), Tool-Service (FastAPI) und Frontend (Vue 3) stellt jedoch sicher, dass das System strukturell jederzeit bereit ist, um in einer möglichen späteren Projektphase auf produktive Server- und Cloud-Infrastrukturen migriert zu werden.

### 14. Session Workflow und Event-Rollen

Das System trennt strikt zwischen der Definition einer Studie (Event-Builder) und deren Ausführung (Session Runner). Eine **Session** repräsentiert in diesem Datenmodell exakt einen Durchlauf: **1 Event + 1 Phase (Page Group) + 1 Proband (Subject)**.
Der Workflow ist in drei Kernbereiche unterteilt:

* **1. Event-Builder (Vorbereitung):** Hier wird die Struktur der Studie definiert (Bottom-Up).
  * **Bausteine (Components):** Die kleinsten Einheiten (z. B. Rich-Text-Blöcke oder Metadaten-Formulare).
  * **Seiten (Pages):** Fassen mehrere Bausteine in einer festen Reihenfolge zusammen.
  * **Phasen (Page Groups):** Bündeln Seiten zu logischen Abschnitten (z. B. "Pre-Session Fragebogen", "Main Task").
  * **Event Roles:** [WIP]

* **2. Session Launcher (Das Wartezimmer):**
  Der Einstiegspunkt für den Forscher. Hier werden Event, Phase und Proband ausgewählt. Wird eine bereits existierende Kombination aus Event, Phase und Proband erkannt, warnt das System und bietet zwei Optionen:
  * **Resume (Fortsetzen):** Lädt die bisherigen Antworten aus der Datenbank und springt in die Sitzung zurück.
  * **Reset (Neu starten):** Löscht alle bisher erfassten Metadaten dieser Sitzungs-Phase und setzt den Zeitstempel zurück.

* **3. Session Runner (Die Engine):**
  Die Ausführungsumgebung, die den Blueprint des Events rendert. 
  * Erlaubt fließendes Vor- und Zurück-Navigieren zwischen den Seiten, ohne dass Daten verloren gehen.
  * Eingaben in Metadaten-Formularen werden bei jedem Seitenwechsel automatisch als Upsert (`update_or_create`) im Backend gespeichert.

### 15. Session Historie und Reports

* **Session Historie (Overview):**
  Ein globales Dashboard, das alle jemals gestarteten Sitzungen auflistet. Die Tabelle bietet Metadaten wie Zeitstempel, zugehöriges Event, die jeweilige Phase und den Identifier des Probanden. Die Ansicht kann schnell nach bestimmten Probanden, Events (+Event Ersteller) und PageGroups gefiltert werden, um den Überblick in laufenden Studien zu behalten.
* **Session Report (Daten-Ansicht):**
  Aus der Historie oder direkt nach Abschluss einer Sitzung im Runner gelangt man in den detaillierten Session Report. Hier werden alle über Metadaten-Formulare erfassten Antworten der jeweiligen Sitzung (z. B. Pre- und Post-Fragebögen) tabellarisch und lesbar aufbereitet.

#### 16. Metadaten Ansicht mit ID
