# Worx Vision for Home Assistant

![Worx Vision Banner](https://raw.githubusercontent.com/allroggen/landroid/main/images/worx-vision-banner.svg)

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://hacs.xyz/)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2024.3%2B-41BDF5.svg)](https://www.home-assistant.io/)
[![Release](https://img.shields.io/github/v/release/allroggen/landroid)](https://github.com/allroggen/landroid/releases)

Custom Home Assistant integration for Worx Vision / Landroid robotic mowers powered by `pyworxcloud`.

**Version:** `0.2.2`

## Features

- Login with Worx account (email/password)
- Supports multiple mowers (select by serial number)
- Lawn mower control entity (start, pause, dock)
- Sensors for battery, state, errors, runtime, last update and GPS
- Binary sensors for mowing, rain delay, error and charging
- Schedule switch
- Additional services:
  - `worx_vision.start_zone`
  - `worx_vision.set_schedule`
  - `worx_vision.ots`

## Requirements

- Home Assistant `2024.3+`
- Worx/Landroid cloud account
- HACS (recommended)

## Installation

### HACS (recommended)

1. Open HACS and add this repository as a **Custom repository** (`Integration`).
2. Install **Worx Vision**.
3. Restart Home Assistant.
4. Go to **Settings → Devices & Services → Add Integration**.
5. Select **Worx Vision** and enter your credentials.

### Manual

1. Copy `custom_components/worx_vision` into your Home Assistant configuration directory.
2. Restart Home Assistant.
3. Add the integration via the UI.

## Configuration

- Enter Worx cloud email and password.
- If you have multiple mowers, choose the target mower.

## Dashboard card (Lovelace)

This integration now provides a built-in custom Lovelace card that appears in the card picker.

### Add predefined card from Dashboard UI

1. Open your dashboard and click **Add card**.
2. Search for **Worx Vision Card**.
3. Select your `lawn_mower.*` entity in the card editor.

Card type (manual YAML):

```yaml
type: custom:worx-vision-card
entity: lawn_mower.my_mower
name: Worx Vision
```

You can still build custom layouts with the entities provided by this integration:

### 1) Quick start card

Use one compact stack for status and actions (`start`, `pause`, `dock`):

```yaml
type: vertical-stack
cards:
  - type: entities
    title: Worx Vision
    entities:
      - entity: lawn_mower.my_mower
        name: Mower
      - entity: sensor.my_mower_battery
      - entity: sensor.my_mower_status
      - entity: binary_sensor.my_mower_error
      - entity: switch.my_mower_schedule
  - type: horizontal-stack
    cards:
      - type: button
        name: Start
        icon: mdi:play
        tap_action:
          action: perform-action
          perform_action: lawn_mower.start_mowing
          target:
            entity_id: lawn_mower.my_mower
      - type: button
        name: Pause
        icon: mdi:pause
        tap_action:
          action: perform-action
          perform_action: lawn_mower.pause
          target:
            entity_id: lawn_mower.my_mower
      - type: button
        name: Dock
        icon: mdi:home-import-outline
        tap_action:
          action: perform-action
          perform_action: lawn_mower.dock
          target:
            entity_id: lawn_mower.my_mower
```

> Replace `my_mower` with your real entity names from Home Assistant.

### 2) Enhanced compact layout

Add a compact overview with live states and location values:

```yaml
type: vertical-stack
cards:
  - type: entities
    title: Worx Vision Overview
    entities:
      - entity: lawn_mower.my_mower
      - entity: sensor.my_mower_status
      - entity: sensor.my_mower_last_update
      - entity: sensor.my_mower_battery
      - entity: binary_sensor.my_mower_is_mowing
      - entity: binary_sensor.my_mower_charging
      - entity: binary_sensor.my_mower_rain_delay_active
      - entity: binary_sensor.my_mower_error
      - entity: switch.my_mower_schedule
  - type: entities
    title: Position
    entities:
      - entity: sensor.my_mower_latitude
      - entity: sensor.my_mower_longitude
```

### 3) Future option: dedicated custom card

If you want a product-style UX, a dedicated custom Lovelace card can be built later (specialized mower visuals, state icons, and highlighted error handling).

## Services

| Service | Description | Fields |
|---|---|---|
| `worx_vision.start_zone` | Start mowing in a zone | `serial_number` (optional), `zone` (required) |
| `worx_vision.set_schedule` | Update mower schedule | `serial_number` (optional), `enabled` (optional), `time_extension` (optional), `entries` (optional) |
| `worx_vision.ots` | One-time schedule run | `serial_number` (optional), `boundary` (optional, default `false`), `runtime` (required, minutes) |

### Service field details

- `worx_vision.start_zone`
  - `serial_number` (optional)
  - `zone` (required)
- `worx_vision.set_schedule`
  - `serial_number` (optional)
  - `enabled` (optional)
  - `time_extension` (optional)
  - `entries` (optional list of schedule objects)
- `worx_vision.ots`
  - `serial_number` (optional)
  - `boundary` (optional, default `false`)
  - `runtime` (required, minutes)

## Support

- Issues / bug reports: <https://github.com/allroggen/landroid/issues>
- Feature requests are welcome via GitHub issues

## HACS logo / branding

- The banner on the HACS detail page is rendered from this README (`hacs.json` has `render_readme: true`).
- The integration icon/logo in HACS/Home Assistant does **not** come from `hacs.json`.
- For the real integration icon, add branding for domain `worx_vision` in `home-assistant/brands` under `core_integrations/worx_vision`.

## Hinweis (DE)

Diese Integration nutzt die inoffizielle Cloud-Kommunikation über `pyworxcloud`. Änderungen an der Hersteller-API können Funktionen beeinflussen.
