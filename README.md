# ThingsBoard Integration für Home Assistant

Eine vollständige Home Assistant Custom Component Integration für [ThingsBoard](https://thingsboard.io/), die die HTTP API verwendet.

## Features

- ✅ **Automatische Entity-Discovery**: Erkennt alle Attribute automatisch
- ✅ **Stündliche Aktualisierung**: Daten werden jede Stunde automatisch aktualisiert
- ✅ **HTTP API**: Nutzt die ThingsBoard HTTP API (Device API)
- ✅ **UI-Konfiguration**: Einfache Einrichtung über die Home Assistant UI
- ✅ **Mehrsprachig**: Unterstützt Deutsch und Englisch
- ✅ **Sensor-Entities**: Erstellt automatisch Sensoren für alle entdeckten Attribute
- ✅ **Gerätesteuerung**: Setzen von SharedAttributes über Services und Number-Entities
- ✅ **Number-Entities**: Numerische SharedAttributes werden automatisch als steuerbare Number-Entities erstellt

## Installation

### HACS (empfohlen)

1. Öffnen Sie HACS in Home Assistant
2. Gehen Sie zu "Integrations"
3. Klicken Sie auf das Menü (⋮) und wählen Sie "Custom repositories"
4. Fügen Sie diese Repository-URL hinzu: `https://github.com/lemming1337/homeassistant-thingsboard`
5. Kategorie: `Integration`
6. Klicken Sie auf "Add"
7. Suchen Sie nach "ThingsBoard" und installieren Sie es
8. Starten Sie Home Assistant neu

### Manuelle Installation

1. Kopieren Sie den Ordner `custom_components/thingsboard` in Ihr Home Assistant `custom_components` Verzeichnis
2. Starten Sie Home Assistant neu

## Konfiguration

### ThingsBoard vorbereiten

1. Melden Sie sich in Ihrem ThingsBoard-Dashboard an
2. Erstellen Sie ein neues Gerät oder wählen Sie ein bestehendes aus
3. Gehen Sie zu **Devices** → Ihr Gerät → **Details**
4. Kopieren Sie das **Access Token** (unter "Device credentials")

### Home Assistant einrichten

1. Gehen Sie zu **Einstellungen** → **Geräte & Dienste**
2. Klicken Sie auf **+ Integration hinzufügen**
3. Suchen Sie nach **ThingsBoard**
4. Geben Sie Ihre ThingsBoard-Verbindungsdaten ein:
   - **ThingsBoard Host URL**: z.B. `https://demo.thingsboard.io` oder Ihre eigene Instanz
   - **Device Access Token**: Das Access Token Ihres Geräts

### Beispiel-Konfiguration

```yaml
# Beispiel: Keine YAML-Konfiguration erforderlich
# Die Integration wird vollständig über die UI konfiguriert
```

## Verwendung

Nach der Konfiguration:

1. Die Integration verbindet sich mit ThingsBoard
2. Alle Attribute (client und shared) werden automatisch erkannt
3. Für jedes Attribut wird ein Sensor erstellt
4. Die Sensoren werden stündlich aktualisiert
5. Neue Attribute werden bei der nächsten Aktualisierung automatisch hinzugefügt

### Sensor-Naming

Sensoren werden automatisch benannt als:
- `sensor.thingsboard_client_<attributname>`
- `sensor.thingsboard_shared_<attributname>`

### Beispiel-Attribute in ThingsBoard

Wenn Ihr ThingsBoard-Gerät folgende Attribute hat:

**Client Attributes:**
```json
{
  "temperature": 23.5,
  "humidity": 65,
  "battery": 87
}
```

**Shared Attributes:**
```json
{
  "targetTemperature": 22.0,
  "mode": "auto"
}
```

Dann werden folgende Sensoren erstellt:
- `sensor.thingsboard_client_temperature`
- `sensor.thingsboard_client_humidity`
- `sensor.thingsboard_client_battery`
- `sensor.thingsboard_shared_targettemperature`
- `sensor.thingsboard_shared_mode`

Zusätzlich wird für numerische SharedAttributes eine Number-Entity erstellt:
- `number.thingsboard_targettemperature` (steuerbar!)

## Gerätesteuerung

Die Integration ermöglicht die Steuerung von ThingsBoard-Geräten durch Setzen von SharedAttributes.

### Number-Entities (UI-Steuerung)

Numerische SharedAttributes werden automatisch als **Number-Entities** erstellt, die direkt in der Home Assistant UI gesteuert werden können:

1. Gehen Sie zu **Einstellungen** → **Geräte & Dienste** → **ThingsBoard**
2. Klicken Sie auf Ihr Gerät
3. Sie sehen alle Number-Entities mit Eingabefeldern
4. Ändern Sie den Wert direkt in der UI

**Beispiel:**
- SharedAttribute `targetTemperature: 22.0` → `number.thingsboard_targettemperature`
- Wert ändern → Wird sofort an ThingsBoard gesendet

### Services für erweiterte Steuerung

Für komplexere Szenarien oder Automatisierungen stehen zwei Services zur Verfügung:

#### 1. `thingsboard.set_attribute` - Einzelnes Attribut setzen

```yaml
service: thingsboard.set_attribute
data:
  config_entry_id: "01234567890abcdef"
  attribute_key: "targetTemperature"
  value: 22.5
```

#### 2. `thingsboard.set_attributes` - Mehrere Attribute gleichzeitig

```yaml
service: thingsboard.set_attributes
data:
  config_entry_id: "01234567890abcdef"
  attributes:
    targetTemperature: 22.5
    mode: "auto"
    enabled: true
```

### Config Entry ID finden

Um die `config_entry_id` zu finden:

1. Gehen Sie zu **Einstellungen** → **Geräte & Dienste**
2. Klicken Sie auf **ThingsBoard**
3. Klicken Sie auf die drei Punkte (⋮) bei Ihrer Integration
4. Die ID ist in der URL sichtbar: `.../config/config_entries/entry/[CONFIG_ENTRY_ID]`

### Beispiel-Automatisierung

```yaml
automation:
  - alias: "Temperatur bei Sonnenuntergang erhöhen"
    trigger:
      - platform: sun
        event: sunset
    action:
      - service: thingsboard.set_attribute
        data:
          config_entry_id: "YOUR_CONFIG_ENTRY_ID"
          attribute_key: "targetTemperature"
          value: 23.0
```

## Technische Details

### API-Endpunkte

Die Integration verwendet folgende ThingsBoard HTTP API Endpunkte:

- **GET** `/api/v1/{token}/attributes` - Abrufen aller Attribute (client & shared)
- **POST** `/api/v1/{token}/attributes` - Setzen von Attributen (für Gerätesteuerung)

### Update-Intervall

- Standard: **1 Stunde**
- Kann durch Ändern der `DEFAULT_SCAN_INTERVAL` Konstante in `const.py` angepasst werden

### Unterstützte Datentypen

- Strings
- Zahlen (Integer und Float)
- Boolean
- Verschachtelte Objekte (werden als JSON dargestellt)

## Fehlerbehebung

### Verbindung fehlgeschlagen

- Überprüfen Sie die ThingsBoard Host-URL (muss mit `http://` oder `https://` beginnen)
- Prüfen Sie Ihre Netzwerkverbindung
- Stellen Sie sicher, dass ThingsBoard von Home Assistant aus erreichbar ist

### Ungültiges Token

- Kopieren Sie das Access Token erneut aus ThingsBoard
- Stellen Sie sicher, dass das Gerät in ThingsBoard aktiviert ist
- Überprüfen Sie, ob das Token nicht abgelaufen ist

### Keine Sensoren sichtbar

- Stellen Sie sicher, dass Ihr Gerät in ThingsBoard Attribute hat
- Warten Sie bis zur nächsten Aktualisierung (max. 1 Stunde)
- Überprüfen Sie die Home Assistant Logs für Fehlermeldungen

### Logs anzeigen

```bash
# Home Assistant Logs prüfen
tail -f /config/home-assistant.log | grep thingsboard
```

Oder in der Home Assistant UI:
**Einstellungen** → **System** → **Logs**

## Entwicklung

### Struktur

```
custom_components/thingsboard/
├── __init__.py          # Integration Setup
├── config_flow.py       # UI Konfiguration
├── const.py             # Konstanten
├── coordinator.py       # Daten-Update-Coordinator
├── manifest.json        # Integration Metadata
├── sensor.py            # Sensor Platform
├── strings.json         # UI Strings
└── translations/        # Übersetzungen
    ├── de.json          # Deutsch
    └── en.json          # Englisch
```

### Abhängigkeiten

- `aiohttp>=3.8.0` - Für asynchrone HTTP-Anfragen
- Home Assistant Core >= 2024.1.0

## Lizenz

MIT License

## Support

Bei Problemen oder Fragen:
- Erstellen Sie ein [Issue auf GitHub](https://github.com/lemming1337/homeassistant-thingsboard/issues)

## Credits

Entwickelt für die Integration von ThingsBoard IoT-Plattform mit Home Assistant.

---

**Hinweis**: Dies ist eine Community-Integration und wird nicht offiziell von ThingsBoard oder Home Assistant unterstützt.
