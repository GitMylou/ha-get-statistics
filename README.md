# ha-get-statistics
Get long term statistics from home assistant database

## Installation

Install the folder long_term_stats in the custom_components directory of your home assistant installation.

Add this to configuration.yaml:
```yaml
long_term_stats:
```
Restart Home Assistant.

## Usage

### API Endpoint

```sh
GET /api/long_term_stats
```

###  Authentication
You must use a long-lived access token:

Go to Profile → Long-Lived Access Tokens → Create Token

###  Query Parameters

| Parameter   | Required | Description                                           |
| ----------- | -------- | ----------------------------------------------------- |
| `entity_id` | ✅        | Entity ID (e.g., `sensor.energy_total`)               |
| `datetime`  | ✅        | ISO8601 datetime string (e.g., `2025-07-13 14:42:00`) |

###  Example

```sh
GET /api/long_term_stats?entity_id=sensor.energy_total&datetime=2025-07-13T14:42:00
Authorization: Bearer YOUR_LONG_LIVED_TOKEN
```