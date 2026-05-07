# Worx Vision Home Assistant Integration

DE/EN custom Home Assistant integration for Worx Vision robotic mowers using `pyworxcloud`.

## Features

- Cloud login via Worx account (email/password)
- Supports multiple mowers (choose by serial number)
- Lawn mower entity (start, pause, dock)
- Sensors for battery, status, errors, runtime, last update, GPS
- Binary sensors for mowing/rain delay/error/charging
- Switch for schedule on/off
- Custom services:
  - `worx_vision.start_zone`
  - `worx_vision.set_schedule`
  - `worx_vision.ots`

## Requirements

- Home Assistant `2024.3+`
- HACS (recommended)
- Worx/Landroid cloud account

---

## Installation (EN)

### Option A: HACS (recommended)

1. Add this repository as a custom repository in HACS (Integration type).
2. Install **Worx Vision**.
3. Restart Home Assistant.
4. Go to **Settings → Devices & Services → Add Integration**.
5. Select **Worx Vision** and enter credentials.

### Option B: Manual

1. Copy `custom_components/worx_vision` into your Home Assistant config folder.
2. Restart Home Assistant.
3. Add integration via UI.

## Configuration

- Enter Worx cloud email/password.
- If multiple mowers exist, select the device to add.

## Services

### `worx_vision.start_zone`

- `serial_number` (optional)
- `zone` (required)

### `worx_vision.set_schedule`

- `serial_number` (optional)
- `enabled` (optional)
- `time_extension` (optional)
- `entries` (optional list of schedule objects)

### `worx_vision.ots`

- `serial_number` (optional)
- `boundary` (optional, default `false`)
- `runtime` (required, minutes)

---

## Installation (DE)

### Option A: HACS (empfohlen)

1. Dieses Repository in HACS als benutzerdefiniertes Repository hinzufügen (Typ: Integration).
2. **Worx Vision** installieren.
3. Home Assistant neu starten.
4. Unter **Einstellungen → Geräte & Dienste → Integration hinzufügen** auswählen.
5. **Worx Vision** auswählen und Zugangsdaten eingeben.

### Option B: Manuell

1. `custom_components/worx_vision` in dein Home-Assistant-Konfigurationsverzeichnis kopieren.
2. Home Assistant neu starten.
3. Integration über die UI hinzufügen.

## Konfiguration

- Worx Cloud E-Mail/Passwort eintragen.
- Bei mehreren Mähern den gewünschten Mäher auswählen.

## Hinweise

- Die Integration nutzt die inoffizielle Cloud-Kommunikation über `pyworxcloud`.
- API-Änderungen auf Herstellerseite können Funktionen beeinflussen.
