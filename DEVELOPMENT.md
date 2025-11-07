# Guida allo Sviluppo - TecnoAlarm TecnoOut Integration

## ✅ Stato Attuale

### Completato

- ✅ Struttura directory `custom_components/ha_tecnout/`
- ✅ File `manifest.json` con metadati corretti
- ✅ File `const.py` con tutte le costanti
- ✅ File `coordinator.py` con DataUpdateCoordinator
- ✅ File `config_flow.py` per configurazione UI
- ✅ File `__init__.py` entry point dell'integrazione
- ✅ File `binary_sensor.py` per le zone dell'allarme
- ✅ File `switch.py` per i programmi dell'allarme
- ✅ File `strings.json` per traduzioni italiane
- ✅ File `translations/en.json` per traduzioni inglesi
- ✅ File `README.md` con documentazione completa
- ✅ File `hacs.json` per compatibilità HACS

### Struttura File

```
TecnoOUTHa/
├── .cursorrules                    # Regole per Cursor
├── README.md                       # Documentazione principale
├── DEVELOPMENT.md                  # Questa guida
├── hacs.json                       # Configurazione HACS
├── tecnout/                        # Libreria client Python
│   ├── __init__.py
│   ├── tecnout_client.py          # Client TecnoOut
│   └── entities.py                # Entità Pydantic
└── custom_components/
    └── ha_tecnout/                 # Integrazione Home Assistant
        ├── __init__.py             # Entry point
        ├── manifest.json           # Metadata
        ├── const.py                # Costanti
        ├── coordinator.py          # DataUpdateCoordinator
        ├── config_flow.py          # Configurazione UI
        ├── binary_sensor.py        # Piattaforma sensori zone
        ├── switch.py               # Piattaforma switch programmi
        ├── strings.json            # Traduzioni IT
        └── translations/
            └── en.json             # Traduzioni EN
```

## 🎯 Prossimi Passi

### 1. Testing Locale

**Obiettivo**: Testare l'integrazione in un ambiente Home Assistant reale

**Passi**:

1. **Copiare l'integrazione in Home Assistant**:
   ```bash
   # Copia nella directory custom_components di Home Assistant
   cp -r custom_components/ha_tecnout /path/to/homeassistant/custom_components/
   ```

2. **Copiare anche la libreria tecnout**:
   ```bash
   # La libreria deve essere accessibile all'integrazione
   # Opzione A: Copiala dentro custom_components/ha_tecnout/
   cp -r tecnout custom_components/ha_tecnout/
   
   # Opzione B: Installala come pacchetto (se pubblicata su PyPI)
   pip install tecnout
   ```

3. **Riavviare Home Assistant**:
   - Riavvia completamente Home Assistant
   - Controlla i log per errori

4. **Aggiungere l'integrazione**:
   - Vai su Impostazioni → Dispositivi e Servizi
   - Clicca "Aggiungi Integrazione"
   - Cerca "TecnoAlarm TecnoOut"
   - Inserisci le credenziali della tua centrale

5. **Verificare le entità**:
   - Controlla che vengano create le zone (binary_sensor)
   - Controlla che vengano creati i programmi (switch)
   - Verifica che gli aggiornamenti funzionino

### 2. Pubblicazione Libreria Python (Opzionale ma Consigliato)

**Obiettivo**: Pubblicare la libreria `tecnout` su PyPI

**Perché**: Le best practice di Home Assistant richiedono che la logica API sia in una libreria separata pubblicata su PyPI.

**Passi**:

1. **Preparare la libreria**:
   ```bash
   cd tecnout
   # Creare setup.py o pyproject.toml
   # Aggiungere README, LICENSE
   ```

2. **Pubblicare su PyPI**:
   ```bash
   python -m build
   python -m twine upload dist/*
   ```

3. **Aggiornare manifest.json**:
   ```json
   "requirements": ["tecnout==1.0.0"]
   ```

### 3. Testing Avanzato

**Test da implementare**:

1. **Test Config Flow**:
   - Test connessione riuscita
   - Test credenziali errate
   - Test host non raggiungibile
   - Test integrazione già configurata

2. **Test Coordinator**:
   - Test fetch dati
   - Test errori di rete
   - Test riconnessione automatica

3. **Test Entità**:
   - Test creazione sensori zone
   - Test creazione switch programmi
   - Test aggiornamenti stato

**Creare file di test**:
```
tests/
├── __init__.py
├── conftest.py
├── test_config_flow.py
├── test_coordinator.py
├── test_binary_sensor.py
└── test_switch.py
```

### 4. Miglioramenti Futuri

**Feature aggiuntive**:

- [ ] **Sensor Platform**: Aggiungere sensori per stato generale (batteria, tamper, ecc.)
- [ ] **Services**: Creare servizi per azioni avanzate (esclusione zone, ecc.)
- [ ] **Diagnostics**: Implementare diagnostics support per debugging
- [ ] **Reauthentication Flow**: Gestire cambio credenziali
- [ ] **Options Flow**: Permettere modifica opzioni dopo configurazione
- [ ] **Repair Flows**: Gestire problemi noti con repair flows
- [ ] **Notifications**: Notifiche per eventi importanti (allarmi, tamper)
- [ ] **Eventi**: Emettere eventi Home Assistant per allarmi

### 5. Documentazione Aggiuntiva

**Da creare**:

- [ ] **CHANGELOG.md**: Registro delle modifiche
- [ ] **CONTRIBUTING.md**: Guida per contribuire
- [ ] **LICENSE**: Licenza del progetto
- [ ] **Screenshots**: Screenshot dell'interfaccia UI
- [ ] **Examples**: Esempi di automazioni con l'integrazione

### 6. Quality Scale - Livello Silver

**Requisiti da soddisfare**:

- ✅ Config flow implementato
- ✅ Coordinator pattern
- ✅ Traduzioni multiple
- ✅ Type hints
- ⬜ Test coverage ≥90%
- ⬜ Reauthentication flow
- ⬜ Diagnostics support
- ⬜ Repair flows

### 7. Pubblicazione HACS

**Quando pronto**:

1. Creare repository GitHub pubblico
2. Aggiungere tag version (es. v1.0.0)
3. Sottomettere a HACS default repository
4. O distribuire come custom repository

## 🐛 Problemi Noti da Risolvere

### Import della Libreria tecnout

**Problema**: La libreria `tecnout` deve essere accessibile all'integrazione.

**Soluzioni possibili**:

1. **Soluzione Temporanea**: Copiare `tecnout` dentro `custom_components/ha_tecnout/tecnout/`
   - Modificare gli import da `from tecnout.` a `from .tecnout.`

2. **Soluzione Corretta**: Pubblicare `tecnout` su PyPI e usare `requirements` nel manifest

### Dipendenze

**Problema**: La libreria usa `pycryptodome` che deve essere dichiarato.

**Soluzione**: È già nel manifest.json come `pycryptodome==3.20.0`

### Watchdog Thread

**Nota**: Il watchdog thread è implementato per mantenere la connessione attiva. Potrebbe necessitare tuning in base al comportamento reale della centrale.

## 📝 Checklist Pre-Rilascio

Prima di pubblicare la versione 1.0.0:

- [ ] Test manuale completo su Home Assistant reale
- [ ] Tutti gli import funzionano correttamente
- [ ] Nessun errore nei log durante operazioni normali
- [ ] Config flow funziona correttamente
- [ ] Entità vengono create e aggiornate
- [ ] Switch attiva/disattiva programmi correttamente
- [ ] Device info è corretto
- [ ] Traduzioni sono corrette (IT e EN)
- [ ] README è completo e accurato
- [ ] Codice segue le best practice Home Assistant
- [ ] Type hints sono completi
- [ ] Docstrings sono presenti

## 🔧 Comandi Utili

### Validare manifest.json
```bash
# Home Assistant ha un validator per manifest
# Da eseguire da dentro ambiente Home Assistant
python -m script.hassfest
```

### Controllare Type Hints
```bash
mypy custom_components/ha_tecnout/
```

### Formattare codice
```bash
black custom_components/ha_tecnout/
isort custom_components/ha_tecnout/
```

### Lint
```bash
pylint custom_components/ha_tecnout/
```

## 📚 Risorse

- [Home Assistant Developer Docs](https://developers.home-assistant.io/)
- [Config Flow](https://developers.home-assistant.io/docs/config_entries_config_flow_handler)
- [DataUpdateCoordinator](https://developers.home-assistant.io/docs/integration_fetching_data)
- [Testing](https://developers.home-assistant.io/docs/development_testing)

## 💡 Note Importanti

1. **Libreria Separata**: Home Assistant richiede che la logica API sia in una libreria separata, non nell'integrazione stessa. La libreria `tecnout` è corretta in questo senso.

2. **Async Operations**: Tutte le operazioni I/O devono essere async. Usiamo `hass.async_add_executor_job()` per il client sincrono.

3. **Coordinator Pattern**: Il coordinator gestisce tutti gli update, le entità si limitano a leggere i dati.

4. **Unique ID**: Ogni entità deve avere un unique_id basato su `entry.entry_id` + identificativo univoco.

5. **Device Info**: Tutte le entità appartengono allo stesso device (la centrale).

## 🎓 Best Practice Seguite

- ✅ Type hints completi con `from __future__ import annotations`
- ✅ Logging appropriato con livelli corretti
- ✅ Gestione errori con eccezioni specifiche
- ✅ Docstrings per classi e metodi pubblici
- ✅ Naming conventions Python (snake_case, PascalCase)
- ✅ Config flow per configurazione UI
- ✅ Coordinator per fetch dati centralizzato
- ✅ CoordinatorEntity per entità sincronizzate
- ✅ Device info completo
- ✅ Traduzioni multiple (IT, EN)
- ✅ Manifest.json completo con tutti i campi
- ✅ Async/await per operazioni non bloccanti
- ✅ Gestione corretta di setup/unload

Buono sviluppo! 🚀

