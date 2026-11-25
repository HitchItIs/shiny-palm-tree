# IHK AP1 Trainer für FIAE

Ein interaktiver Kommandozeilen-Trainer zur Vorbereitung auf die IHK-Abschlussprüfung Teil 1 (AP1) für Fachinformatikerinnen und Fachinformatiker der Anwendungsentwicklung (FIAE). Der Trainer erzeugt praxisnahe Aufgaben, wertet Antworten direkt aus und erklärt die Rechenwege.

## Themen

| Modul | Thema | Das wird trainiert |
| --- | --- | --- |
| `subnet` | IPv4-Subnetting | Subnetzmaske, Netz- und Broadcast-Adresse, Hostbereich und Hostanzahl |
| `transfer` | Datenübertragung | Übertragungsrate sowie Transferzeiten mit dezimalen und binären Einheiten |
| `raid` | RAID-Kalkulator | Brutto- und Nettokapazität, Ausfallsicherheit und Effizienz |
| `numerals` | Zahlensysteme (Dez/Bin/Hex) | Umrechnung zwischen Dezimal-, Binär- und Hexadezimalsystem |
| `pricing` | Bezugskalkulation | Zieleinkaufspreis, Bareinkaufspreis und Bezugspreis |
| `sla` | SLA & Verfügbarkeit | Verfügbarkeit und maximal zulässige Ausfallzeit pro Jahr |

## Funktionen

- Einzelthemen, eine zufällige Aufgabe oder eine Prüfungs-Simulation mit fünf gemischten Aufgaben
- Kompakte Prüfungsauswertung mit Gesamtzeit, IHK-Notenschlüssel und Bestanden-Status ab 50 %
- Fortschritt pro Thema: erreichte Punkte werden lokal in `stats.json` gespeichert
- Schrittweise Lösungswege zu jeder Aufgabe
- Toleranz bei Rundungen und Eingabe von Dezimalzahlen mit deutschem Komma
- Rich-basierte Oberfläche mit Themenübersicht, Fortschrittsbalken und Serienanzeige für perfekte Aufgaben

## Installation und Start

Voraussetzung ist Python 3.10 oder neuer. Im Projektverzeichnis unter Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

Falls die PowerShell-Skriptausführung die Aktivierung blockiert, kann Python auch direkt aus der virtuellen Umgebung aufgerufen werden:

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe main.py
```

## Tests

Führe die Tests aus dem Projektverzeichnis aus:

```powershell
python -m unittest discover -s tests -v
```

## Eigenes Modul hinzufügen

Erstelle in `generators/` eine Klasse, die von `BaseGenerator` erbt. Implementiere die Eigenschaften `category_id` und `name` sowie `generate()`, das eine `Task` mit `InputField`-Feldern und deutschen `solution_steps` zurückgibt. Importiere den Generator anschließend in `main.py` und füge eine Instanz zur Liste `GENERATORS` hinzu. Ergänze passende Unit-Tests in `tests/`.

## Projektstruktur

```text
.
├── core/
│   ├── evaluator.py
│   ├── models.py
│   └── stats.py
├── generators/
│   ├── base.py
│   ├── numerals.py
│   ├── pricing.py
│   ├── raid.py
│   ├── sla.py
│   ├── subnet.py
│   └── transfer.py
├── tests/
│   ├── test_evaluator.py
│   ├── test_numerals.py
│   ├── test_pricing.py
│   ├── test_raid.py
│   ├── test_sla.py
│   ├── test_stats.py
│   ├── test_subnet.py
│   └── test_transfer.py
├── .gitignore
├── main.py
├── README.md
└── requirements.txt
```
