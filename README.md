# Hunter WiFi for Home Assistant

Local Home Assistant integration for Hunter irrigation controllers that expose the
Hunter WiFi HTTP API.

## Features

- Config flow fields:
  - controller IP address
  - enabled zones (1-8)
  - enabled programs (1-3)
- Per-zone duration number entities (minutes), default `5`
- Stateless action buttons:
  - start zone
  - stop zone
  - start program
  - stop program

## HTTP API mapping

- Start zone:
  - `GET /api/start/zone/{zone}?time={minutes}`
- Stop zone:
  - `GET /api/stop/zone/{zone}`
- Start program:
  - `GET /api/start/program/{program}`
- Stop program:
  - `GET /api/stop/program/{program}`

## Example

See `examples/dashboard.yml` for a simple Lovelace view example.

## Reference

- Hunter WiFi API docs:
  - https://ecodina.github.io/hunter-wifi/#!pages/api.md
