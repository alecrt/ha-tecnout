# TecnoAlarm TecnoOut - Home Assistant Integration

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]][license]
[![hacs][hacsbadge]][hacs]
[![Community Forum][forum-shield]][forum]

Integrazione Home Assistant per centrali TecnoAlarm tramite protocollo TecnoOut.

[releases-shield]: https://img.shields.io/github/release/alecrt/ha-tecnout.svg?style=for-the-badge
[releases]: https://github.com/alecrt/ha-tecnout/releases
[commits-shield]: https://img.shields.io/github/commit-activity/y/alecrt/ha-tecnout.svg?style=for-the-badge
[commits]: https://github.com/alecrt/ha-tecnout/commits/main
[license-shield]: https://img.shields.io/github/license/alecrt/ha-tecnout.svg?style=for-the-badge
[license]: https://github.com/alecrt/ha-tecnout/blob/main/LICENSE
[hacs]: https://github.com/hacs/integration
[hacsbadge]: https://img.shields.io/badge/HACS-Default-orange.svg?style=for-the-badge
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=for-the-badge
[forum]: https://community.home-assistant.io/

## 🚀 Caratteristiche

- ✅ **Configurazione tramite UI** - Setup semplice dall'interfaccia di Home Assistant
- ✅ **Sensori Binari per Zone** - Monitora tutte le zone dell'allarme
- ✅ **Switch per Programmi** - Attiva/disattiva i programmi di allarme
- ✅ **Protezione con PIN** - 🔐 Servizi protetti da PIN per armare/disarmare
- ✅ **Aggiornamento Automatico** - Polling automatico dello stato ogni 5 secondi
- ✅ **Watchdog Connection** - Keep-alive automatico per evitare disconnessioni
- ✅ **Device Info Completo** - Informazioni dettagliate sulla centrale

## 📋 Requisiti

- Home Assistant 2024.1.0 o superiore
- Centrale TecnoAlarm con modulo TecnoOut
- Connettività di rete alla centrale (TCP/IP)
- Codice utente e passphrase configurati sulla centrale

## 📦 Installazione

### Tramite HACS (Consigliato)

1. Apri HACS nel tuo Home Assistant
2. Vai su "Integrations"
3. Clicca sul menu in alto a destra (⋮) e seleziona "Custom repositories"
4. Aggiungi l'URL: `https://github.com/alecrt/ha-tecnout`
5. Seleziona categoria: "Integration"
6. Cerca "TecnoAlarm TecnoOut" e clicca "Download"
7. Riavvia Home Assistant

**Nota**: L'integrazione verrà aggiunta all'elenco default di HACS dopo l'approvazione del team HACS.

### Manuale

1. Copia la cartella `custom_components/ha_tecnout` nella cartella `custom_components` della tua installazione Home Assistant
2. Riavvia Home Assistant

## ⚙️ Configurazione

1. Vai su **Impostazioni** → **Dispositivi e Servizi**
2. Clicca su **Aggiungi Integrazione**
3. Cerca **TecnoAlarm TecnoOut**
4. Inserisci i dati richiesti:
   - **Indirizzo IP**: L'IP della centrale TecnoAlarm
   - **Porta**: La porta TCP (default: 10001)
   - **Codice Utente**: Il codice utente (0-999999)
   - **Passphrase**: La passphrase per la crittografia AES
   - **Modalità Legacy**: Abilita solo per hardware vecchio
   - **Intervallo Watchdog**: Intervallo keep-alive in secondi (default: 30)
   - **PIN di Controllo** (opzionale): 🔐 PIN per proteggere armare/disarmare

## 🎯 Entità Create

### Binary Sensors (Sensori Binari)

Per ogni **zona attiva** viene creato un sensore binario:

- **Nome**: Nome della zona (es. "Porta Ingresso", "Finestra Soggiorno")
- **Stato**: `ON` se zona in allarme o pre-allarme, `OFF` altrimenti
- **Attributi**:
  - `zone_number`: Numero della zona
  - `isolation_active`: Zona esclusa
  - `zone_status`: Stato zona
  - `battery_low`: Batteria scarica
  - `supervision_alarm`: Allarme supervisione
  - `pre_alarm`: Pre-allarme attivo
  - `alarm`: Allarme attivo
  - E altri...

### Switches (Interruttori)

Per ogni **programma** viene creato uno switch:

- **Nome**: Nome del programma (es. "Totale", "Parziale Notte")
- **Stato**: `ON` se programma inserito, `OFF` se disinserito
- **Attributi**:
  - `program_number`: Numero del programma
  - `status`: Stato corrente ("Armed", "Standby", ecc.)
  - `prealarm`: Pre-allarme attivo
  - `alarm`: Allarme attivo
  - `alarm_memory`: Memoria allarme

### Azioni

- **Turn On Switch**: Inserisce il programma con esclusione automatica zone aperte
- **Turn Off Switch**: Disinserisce il programma

## 🔐 Servizi con Protezione PIN

L'integrazione fornisce servizi protetti da PIN per un controllo più sicuro:

### `ha_tecnout.arm_program`
Inserisce un programma con verifica PIN opzionale.

```yaml
service: ha_tecnout.arm_program
data:
  program_id: 1
  pin: "1234"  # Richiesto se configurato
```

### `ha_tecnout.disarm_program`
Disinserisce un programma con verifica PIN opzionale.

```yaml
service: ha_tecnout.disarm_program
data:
  program_id: 1
  pin: "1234"  # Richiesto se configurato
```

**Documentazione completa**: Vedi [PIN_PROTECTION.md](PIN_PROTECTION.md)

## 🔧 Struttura del Progetto

```
custom_components/ha_tecnout/
├── __init__.py              # Entry point dell'integrazione
├── manifest.json            # Metadata dell'integrazione
├── config_flow.py           # Configurazione tramite UI
├── const.py                 # Costanti
├── coordinator.py           # Data Update Coordinator
├── binary_sensor.py         # Piattaforma sensori binari (zone)
├── switch.py                # Piattaforma switch (programmi)
├── strings.json             # Traduzioni italiane
└── translations/
    └── en.json              # Traduzioni inglesi
```

## 🏗️ Architettura

L'integrazione segue le best practice di Home Assistant:

- **Config Flow**: Configurazione completa tramite UI
- **DataUpdateCoordinator**: Gestione centralizzata degli aggiornamenti
- **CoordinatorEntity**: Entità sincronizzate automaticamente
- **Type Hints**: Codice completamente tipizzato
- **Async/Await**: Operazioni non bloccanti

## 📚 Libreria Python

L'integrazione utilizza la libreria `tecnout` (inclusa nella cartella `tecnout/`) che implementa il protocollo proprietario TecnoOut con:

- Comunicazione TCP/IP con crittografia AES
- Gestione automatica del watchdog per keep-alive
- Supporto per comandi di lettura e scrittura
- Entità Pydantic per validazione dati

## 🐛 Debug

Per abilitare i log dettagliati, aggiungi in `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.ha_tecnout: debug
    tecnout: debug
```

## 🤝 Contribuire

Contributi, issues e feature requests sono benvenuti!

## 📝 Licenza

Questo progetto segue le linee guida di Home Assistant per le integrazioni custom.

## 🔗 Link Utili

- [Home Assistant Developer Docs](https://developers.home-assistant.io/)
- [Home Assistant Integration Quality Scale](https://developers.home-assistant.io/docs/core/integration-quality-scale)

## 🎖️ Quality Scale

Questa integrazione mira al livello **Silver** della Integration Quality Scale:

- ✅ Config flow implementato
- ✅ Coordinator pattern
- ✅ Device info
- ✅ Traduzioni multiple
- ✅ Type hints completi
- ✅ Async operations

