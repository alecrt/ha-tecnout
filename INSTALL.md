# Guida all'Installazione - TecnoAlarm TecnoOut

## 🎯 Installazione Rapida per Test Locale

### Prerequisiti

- Home Assistant installato e funzionante
- Accesso alla cartella `config` di Home Assistant
- Centrale TecnoAlarm raggiungibile via rete

### Step 1: Copia l'Integrazione

Copia l'intera cartella `custom_components/ha_tecnout` nella directory `custom_components` della tua installazione Home Assistant:

**Windows**:
```powershell
# Da PowerShell nella directory del progetto
xcopy /E /I custom_components\ha_tecnout C:\Path\To\HomeAssistant\config\custom_components\ha_tecnout
```

**Linux/macOS**:
```bash
# Da terminal nella directory del progetto
cp -r custom_components/ha_tecnout /path/to/homeassistant/config/custom_components/
```

**Home Assistant OS / Supervised**:
```bash
# Usa Samba, SSH, o File Editor per copiare la cartella
# Percorso: /config/custom_components/ha_tecnout
```

### Step 2: Riavvia Home Assistant

Riavvia completamente Home Assistant per caricare la nuova integrazione:

- **Via UI**: Impostazioni → Sistema → Riavvia
- **Via CLI**: `ha core restart`

### Step 3: Controlla i Log

Controlla che non ci siano errori all'avvio:

1. Vai su **Impostazioni** → **Sistema** → **Log**
2. Cerca eventuali errori relativi a `ha_tecnout`
3. Se ci sono errori, segnalali

### Step 4: Configura l'Integrazione

1. Vai su **Impostazioni** → **Dispositivi e Servizi**
2. Clicca su **+ Aggiungi Integrazione**
3. Cerca **TecnoAlarm TecnoOut**
4. Compila il form con i dati della tua centrale:

#### Dati Richiesti

| Campo | Descrizione | Esempio |
|-------|-------------|---------|
| **Indirizzo IP** | IP della centrale TecnoAlarm | `192.168.1.100` |
| **Porta** | Porta TCP (default 10001) | `10001` |
| **Codice Utente** | Codice utente 6 cifre | `123456` |
| **Passphrase** | Passphrase per crittografia AES | `mypassphrase` |
| **Modalità Legacy** | Abilita solo per hardware vecchio | `false` |
| **Intervallo Watchdog** | Secondi per keep-alive | `30.0` |

5. Clicca **Invia**

### Step 5: Verifica le Entità

Se la configurazione ha successo:

1. Dovresti vedere il dispositivo **TecnoAlarm [Modello]**
2. Clicca sul dispositivo per vedere le entità:
   - **Binary Sensors**: Una per ogni zona attiva
   - **Switches**: Uno per ogni programma

#### Esempio Entità

```
binary_sensor.zone_1_porta_ingresso    → OFF (Chiusa)
binary_sensor.zone_2_finestra_soggiorno → OFF (Chiusa)
switch.program_1_totale                → OFF (Disinserito)
switch.program_2_parziale_notte        → OFF (Disinserito)
```

### Step 6: Testa le Funzionalità

1. **Test Lettura Zone**:
   - Apri una porta/finestra con sensore
   - Verifica che il binary_sensor diventi `ON`
   - Chiudi la porta/finestra
   - Verifica che torni `OFF`

2. **Test Inserimento Programma**:
   - Clicca su uno switch per attivarlo
   - Attendi l'inserimento (exit time)
   - Verifica che lo switch diventi `ON`
   - Verifica che lo stato mostri "Armed"

3. **Test Disinserimento Programma**:
   - Clicca sullo switch per disattivarlo
   - Verifica che torni `OFF`
   - Verifica che lo stato mostri "Standby"

## 🐛 Troubleshooting

### Errore: "Impossibile connettersi alla centrale"

**Possibili cause**:
- IP o porta errati
- Centrale non raggiungibile via rete
- Firewall blocca la connessione

**Soluzioni**:
```bash
# Test connettività da Home Assistant
ping 192.168.1.100
telnet 192.168.1.100 10001
```

### Errore: "Autenticazione fallita"

**Possibili cause**:
- Codice utente errato
- Passphrase errata

**Soluzioni**:
- Verifica il codice utente (6 cifre, 0-999999)
- Verifica la passphrase (max 16 caratteri)
- Prova con modalità legacy abilitata

### Integrazione non compare nella lista

**Soluzioni**:
1. Verifica che la cartella sia copiata correttamente:
   ```
   config/custom_components/ha_tecnout/
   ```

2. Controlla che tutti i file siano presenti:
   ```
   __init__.py
   manifest.json
   config_flow.py
   coordinator.py
   const.py
   binary_sensor.py
   switch.py
   strings.json
   translations/
   tecnout/
   ```

3. Riavvia di nuovo Home Assistant

4. Controlla i log per errori di import

### Entità non vengono create

**Soluzioni**:
1. Controlla che la centrale abbia zone/programmi configurati
2. Verifica nei log eventuali errori durante il setup
3. Prova a rimuovere e riconfigurare l'integrazione

### Aggiornamenti non funzionano

**Soluzioni**:
1. Verifica la connessione alla centrale
2. Controlla i log per errori del coordinator
3. Verifica che il watchdog sia attivo (default 30s)

## 📊 Log di Debug

Per abilitare log dettagliati, aggiungi in `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.ha_tecnout: debug
    custom_components.ha_tecnout.coordinator: debug
    custom_components.ha_tecnout.tecnout: debug
```

Poi riavvia Home Assistant e riproduci il problema. I log dettagliati ti aiuteranno a capire cosa non funziona.

## 🔍 Verifiche Avanzate

### Verifica Import Python

Dalla Developer Tools → Template, testa:

```python
{{ states.binary_sensor }}
{{ states.switch }}
```

Dovresti vedere le entità create dall'integrazione.

### Verifica Device Info

Vai su **Impostazioni** → **Dispositivi e Servizi** → Clicca sul dispositivo TecnoAlarm

Dovresti vedere:
- **Produttore**: TecnoAlarm
- **Modello**: TP20-440 / TP8-88 PLUS / EV 10-50
- **Versione Firmware**: X.X
- **Identificatore**: Univoco per l'integrazione

### Test Automazioni

Crea un'automazione di test:

```yaml
automation:
  - alias: "Test TecnoAlarm - Allarme Zona"
    trigger:
      - platform: state
        entity_id: binary_sensor.zone_1_porta_ingresso
        to: "on"
    action:
      - service: notify.notify
        data:
          message: "ALLARME! Zona 1 attivata!"
```

## ✅ Checklist Funzionamento

- [ ] Integrazione visibile in "Aggiungi Integrazione"
- [ ] Configurazione completata con successo
- [ ] Dispositivo creato con nome corretto
- [ ] Binary sensors creati per tutte le zone attive
- [ ] Switches creati per tutti i programmi
- [ ] Zone si aggiornano quando cambiano stato
- [ ] Programmi si attivano/disattivano correttamente
- [ ] Attributi delle entità sono corretti
- [ ] Nessun errore nei log durante uso normale
- [ ] Watchdog mantiene la connessione attiva

## 🎓 Prossimi Passi

Dopo aver verificato che tutto funziona:

1. **Crea Automazioni**: Usa le entità nelle tue automazioni
2. **Dashboard**: Aggiungi le entità alla tua dashboard
3. **Notifiche**: Configura notifiche per allarmi
4. **Test Estesi**: Testa tutti gli scenari d'uso
5. **Feedback**: Segnala bug o richieste di funzionalità

## 📞 Supporto

Se hai problemi:

1. Controlla questa guida
2. Leggi `DEVELOPMENT.md` per dettagli tecnici
3. Controlla i log di debug
4. Crea una issue su GitHub con:
   - Versione Home Assistant
   - Modello centrale TecnoAlarm
   - Log completi dell'errore
   - Passi per riprodurre il problema

Buon test! 🚀

