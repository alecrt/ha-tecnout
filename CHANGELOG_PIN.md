# 🔐 Changelog - Protezione PIN

## Nuova Funzionalità: Protezione con PIN

**Data**: 07/11/2025  
**Versione**: 1.1.0

### ✨ Cosa è Stato Aggiunto

#### 1. Campo PIN nella Configurazione

- Nuovo campo opzionale **"PIN di Controllo"** nel config flow
- Se lasciato vuoto, nessuna protezione viene applicata
- Se configurato, protegge i servizi custom

#### 2. Servizi Custom Protetti

**Nuovo**: `ha_tecnout.arm_program`
- Inserisce un programma di allarme
- Parametri:
  - `program_id` (required): Numero programma (1-N)
  - `pin` (optional): PIN di controllo

**Nuovo**: `ha_tecnout.disarm_program`
- Disinserisce un programma di allarme
- Parametri:
  - `program_id` (required): Numero programma (1-N)
  - `pin` (optional): PIN di controllo

#### 3. Verifiche di Sicurezza

- Verifica PIN lato server (sicuro)
- Errore `HomeAssistantError` se PIN errato o mancante
- Log dettagliati delle operazioni
- Nessun PIN nei log (sicurezza)

#### 4. Documentazione

**Nuovi File**:
- `PIN_PROTECTION.md` - Guida completa all'uso del PIN
- `services.yaml` - Definizione servizi per UI
- `CHANGELOG_PIN.md` - Questo file

**File Aggiornati**:
- `README.md` - Aggiunta sezione servizi PIN
- `strings.json` - Traduzioni italiane
- `translations/en.json` - Traduzioni inglesi
- `const.py` - Nuove costanti
- `config_flow.py` - Campo PIN
- `__init__.py` - Registrazione servizi

### 📝 File Modificati

```
custom_components/ha_tecnout/
├── __init__.py              ✏️ Registrazione servizi
├── const.py                 ✏️ Costanti PIN e servizi
├── config_flow.py           ✏️ Campo PIN opzionale
├── strings.json             ✏️ Traduzioni servizi IT
├── translations/en.json     ✏️ Traduzioni servizi EN
└── services.yaml            🆕 Definizione servizi

Documentazione:
├── README.md                ✏️ Sezione servizi PIN
├── PIN_PROTECTION.md        🆕 Guida completa
└── CHANGELOG_PIN.md         🆕 Questo file
```

### 🎯 Comportamento

#### Con PIN Configurato

```
┌─────────────────────┐
│ Configurazione PIN  │
│    PIN: "1234"      │
└─────────────────────┘
         │
         ├─→ Switch UI: Funzionano normalmente (no PIN)
         │
         └─→ Servizi:
              ├─ Con PIN corretto → ✅ Esegue comando
              ├─ Con PIN errato   → ❌ HomeAssistantError
              └─ Senza PIN        → ❌ HomeAssistantError
```

#### Senza PIN Configurato

```
┌─────────────────────┐
│ Configurazione      │
│    PIN: (vuoto)     │
└─────────────────────┘
         │
         ├─→ Switch UI: Funzionano normalmente
         │
         └─→ Servizi: Funzionano senza richiedere PIN
```

### 📊 Esempi d'Uso

#### Automazione con PIN

```yaml
automation:
  - alias: "Inserisci allarme quando esco"
    trigger:
      - platform: state
        entity_id: person.mario_rossi
        to: "not_home"
    action:
      - service: ha_tecnout.arm_program
        data:
          program_id: 1
          pin: "1234"
```

#### Script Protetto

```yaml
script:
  inserisci_allarme:
    sequence:
      - service: ha_tecnout.arm_program
        data:
          program_id: 1
          pin: "{{ states('input_text.alarm_pin') }}"
```

#### Dashboard Button

```yaml
type: button
name: Inserisci Allarme
icon: mdi:shield-lock
tap_action:
  action: call-service
  service: ha_tecnout.arm_program
  service_data:
    program_id: 1
    pin: "1234"
```

### 🔒 Sicurezza

**Implementata**:
- ✅ Verifica PIN lato server
- ✅ PIN non in chiaro nei log
- ✅ PIN memorizzato criptato da HA
- ✅ Errori specifici per PIN errato

**Limitazioni**:
- ⚠️ Switch UI non protetti (per usabilità)
- ⚠️ PIN visibile nelle automazioni YAML
- ⚠️ Un solo PIN per tutta l'integrazione

### 🚀 Migration Guide

Se aggiorni da versione precedente:

1. **Non è richiesta nessuna azione** - Tutto continua a funzionare
2. **Per abilitare PIN**:
   - Rimuovi l'integrazione
   - Riaggiungila con il PIN configurato
3. **Aggiorna le automazioni** per usare i nuovi servizi (opzionale)

### 📚 Documentazione

Leggi la guida completa: [PIN_PROTECTION.md](PIN_PROTECTION.md)

Include:
- Setup passo-passo
- Esempi completi
- Best practice sicurezza
- FAQ
- Troubleshooting

### 🎓 Compatibilità

- ✅ Home Assistant 2024.1.0+
- ✅ Python 3.11+
- ✅ Retrocompatibile (PIN opzionale)

### 🐛 Known Issues

Nessuno al momento.

### 📬 Feedback

Hai suggerimenti o problemi? Apri una issue su GitHub!

---

**Versione 1.1.0** - Feature completa e testata ✅

