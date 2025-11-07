# TecnoAlarm TecnoOut Integration

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

[![hacs][hacsbadge]][hacs]

_Integrazione per Home Assistant che permette di controllare e monitorare centrali TecnoAlarm tramite protocollo TecnoOut._

## 🚀 Funzionalità

- **Configurazione tramite UI** - Setup semplice e intuitivo dall'interfaccia di Home Assistant
- **Sensori Binari per Zone** - Monitora automaticamente tutte le zone attive della centrale
- **Switch per Programmi** - Attiva e disattiva i programmi di inserimento (Totale, Parziale, ecc.)
- **Protezione con PIN** - Servizi protetti da PIN per operazioni di armare/disarmare
- **Aggiornamento Automatico** - Polling automatico dello stato ogni 5 secondi
- **Watchdog Connection** - Keep-alive automatico per mantenere la connessione stabile
- **Device Info Completo** - Tutte le entità raggruppate sotto il dispositivo centrale

## 📋 Requisiti

- Home Assistant 2024.1.0 o superiore
- Centrale TecnoAlarm con modulo TecnoOut abilitato
- Connettività TCP/IP alla centrale
- Codice utente e passphrase configurati sulla centrale

## ⚙️ Configurazione

Dopo l'installazione:

1. Vai su **Impostazioni** → **Dispositivi e Servizi**
2. Clicca su **Aggiungi Integrazione**
3. Cerca **TecnoAlarm TecnoOut**
4. Inserisci i dati richiesti:
   - Indirizzo IP della centrale
   - Porta TCP (default: 10001)
   - Codice Utente (0-999999)
   - Passphrase per crittografia AES
   - PIN di controllo (opzionale, per proteggere armare/disarmare)

## 🎯 Entità Create

### Binary Sensors (Sensori Zone)
- Uno per ogni zona attiva della centrale
- Stato ON se zona in allarme/pre-allarme
- Attributi dettagliati: stato batteria, supervisione, esclusione, ecc.

### Switches (Programmi)
- Uno per ogni programma configurato
- Permette di inserire/disinserire i programmi
- Stato e attributi del programma sempre aggiornati

## 🔐 Servizi

### `ha_tecnout.arm_program`
Inserisce un programma con verifica PIN opzionale.

### `ha_tecnout.disarm_program`
Disinserisce un programma con verifica PIN opzionale.

## 🐛 Debug

Per log dettagliati, aggiungi in `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.ha_tecnout: debug
```

## 📝 Note

Questa integrazione implementa il protocollo proprietario TecnoOut con:
- Comunicazione TCP/IP crittografata (AES)
- Gestione automatica del watchdog
- Supporto per hardware legacy
- Validazione dati con Pydantic

---

[releases-shield]: https://img.shields.io/github/release/alecrt/ha-tecnout.svg?style=for-the-badge
[releases]: https://github.com/alecrt/ha-tecnout/releases
[commits-shield]: https://img.shields.io/github/commit-activity/y/alecrt/ha-tecnout.svg?style=for-the-badge
[commits]: https://github.com/alecrt/ha-tecnout/commits/main
[license-shield]: https://img.shields.io/github/license/alecrt/ha-tecnout.svg?style=for-the-badge
[hacs]: https://github.com/hacs/integration
[hacsbadge]: https://img.shields.io/badge/HACS-Default-orange.svg?style=for-the-badge

