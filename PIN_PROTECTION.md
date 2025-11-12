# 🔐 Protezione con PIN - TecnoAlarm TecnoOut

## Panoramica

L'integrazione TecnoAlarm TecnoOut supporta la **protezione con PIN** per armare e disarmare i programmi di allarme, aggiungendo un ulteriore livello di sicurezza.

## 🎯 Come Funziona

### 1. Configurazione del PIN

Durante la configurazione dell'integrazione, puoi specificare un **PIN di Controllo** opzionale:

- **Impostazioni** → **Dispositivi e Servizi** → **Aggiungi Integrazione** → **TecnoAlarm TecnoOut**
- Nel campo **"PIN di Controllo (opzionale)"** inserisci un PIN numerico (es: `1234`)
- Se lasci vuoto il campo, i servizi e i pannelli allarme funzioneranno senza richiedere PIN

### 2. Comportamento

#### Con PIN Configurato

Quando un PIN è configurato:

- ✅ I **pannelli di controllo allarme** richiedono il PIN per armare/disarmare
- ✅ I **servizi custom** richiedono il PIN per funzionare
- ✅ Gli **switch** nella UI continuano a funzionare normalmente (senza PIN)
- ✅ Il PIN è verificato lato server (sicuro)
- ❌ Azioni su pannelli allarme e servizi senza PIN o con PIN errato vengono rifiutate

#### Senza PIN Configurato

Se non configuri un PIN:

- ✅ Tutto funziona normalmente senza restrizioni
- ✅ Pannelli allarme, switch e servizi funzionano liberamente

## 🔧 Utilizzo dei Servizi

### Servizio: `ha_tecnout.arm_program`

Inserisce (arma) un programma di allarme.

**Parametri**:
- `program_id` (required): Numero del programma (1-N)
- `pin` (optional): PIN di controllo

**Esempio YAML**:
```yaml
service: ha_tecnout.arm_program
data:
  program_id: 1
  pin: "1234"
```

**Esempio Automazione**:
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
          program_id: 1  # Programma "Totale"
          pin: "1234"
```

### Servizio: `ha_tecnout.disarm_program`

Disinserisce (disarma) un programma di allarme.

**Parametri**:
- `program_id` (required): Numero del programma (1-N)
- `pin` (optional): PIN di controllo

**Esempio YAML**:
```yaml
service: ha_tecnout.disarm_program
data:
  program_id: 1
  pin: "1234"
```

**Esempio Automazione**:
```yaml
automation:
  - alias: "Disinserisci allarme quando arrivo"
    trigger:
      - platform: state
        entity_id: person.mario_rossi
        to: "home"
    action:
      - service: ha_tecnout.disarm_program
        data:
          program_id: 1  # Programma "Totale"
          pin: "1234"
```

## 🎛️ Pannelli di Controllo Allarme (Consigliato)

L'integrazione crea automaticamente **Pannelli di Controllo Allarme** (Alarm Control Panel) per ogni programma configurato. Questi pannelli offrono un'interfaccia nativa di Home Assistant per gestire l'allarme con supporto PIN integrato.

### Caratteristiche Principali

- 🔐 **Richiesta PIN nativa**: Quando configuri un PIN, l'interfaccia mostrerà automaticamente un tastierino per inserirlo
- 🎨 **Design standard HA**: Interfaccia nativa ben integrata con il resto di Home Assistant
- 📱 **Compatibilità totale**: Funziona perfettamente con app mobili, dashboard, Google Home, Alexa
- 🔔 **Stati chiari**: Mostra gli stati "Disinserito", "Inserito Totale", "Inserito Parziale", "Allarme Attivo", ecc.

### Utilizzo nei Dashboard

#### Card Alarm Panel Standard

La card più semplice e consigliata:

```yaml
type: alarm-panel
entity: alarm_control_panel.totale
```

Questa card mostrerà automaticamente:
- Stato attuale del programma
- Tastierino numerico per inserire il PIN (se configurato)
- Pulsanti per armare/disarmare

#### Card Personalizzata

Puoi personalizzare l'aspetto:

```yaml
type: alarm-panel
entity: alarm_control_panel.totale
states:
  - arm_away
name: Allarme Casa
```

### Automazioni con Pannelli Allarme

Puoi usare i pannelli allarme nelle automazioni:

```yaml
automation:
  - alias: "Notifica quando allarme inserito"
    trigger:
      - platform: state
        entity_id: alarm_control_panel.totale
        to: "armed_away"
    action:
      - service: notify.notify
        data:
          message: "Allarme inserito correttamente!"

  - alias: "Notifica allarme attivo"
    trigger:
      - platform: state
        entity_id: alarm_control_panel.totale
        to: "triggered"
    action:
      - service: notify.mobile_app
        data:
          message: "⚠️ ALLARME ATTIVO!"
          title: "Intrusione Rilevata"
```

### Inserimento/Disinserimento Programmatico

Puoi inserire/disinserire via servizi:

```yaml
# Inserimento
service: alarm_control_panel.alarm_arm_away
target:
  entity_id: alarm_control_panel.totale
data:
  code: "1234"  # Solo se configurato

# Disinserimento
service: alarm_control_panel.alarm_disarm
target:
  entity_id: alarm_control_panel.totale
data:
  code: "1234"  # Solo se configurato
```

## 📱 Utilizzo nell'Interfaccia

### 1. Via Developer Tools

1. Vai su **Developer Tools** → **Services**
2. Cerca `ha_tecnout.arm_program` o `ha_tecnout.disarm_program`
3. Compila i campi:
   - Program ID: `1`
   - PIN: `1234`
4. Clicca **Call Service**

### 2. Via Scripts

Crea uno script per inserire/disinserire facilmente:

```yaml
script:
  inserisci_allarme_totale:
    alias: "Inserisci Allarme Totale"
    sequence:
      - service: ha_tecnout.arm_program
        data:
          program_id: 1
          pin: "1234"
      - service: notify.notify
        data:
          message: "Allarme inserito!"

  disinserisci_allarme:
    alias: "Disinserisci Allarme"
    sequence:
      - service: ha_tecnout.disarm_program
        data:
          program_id: 1
          pin: "1234"
      - service: notify.notify
        data:
          message: "Allarme disinserito!"
```

### 3. Via Lovelace Dashboard

Aggiungi pulsanti alla dashboard:

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

## 🛡️ Sicurezza

### Best Practice

1. **Usa un PIN Forte**: Almeno 4-6 cifre
2. **Non Condividere il PIN**: Mantienilo segreto
3. **Cambia il PIN Periodicamente**: Rimuovi e riconfigura l'integrazione
4. **Non Loggare il PIN**: Il PIN non appare nei log
5. **Usa HTTPS**: Se accedi a HA da remoto, usa sempre HTTPS

### Limitazioni

- ⚠️ Gli **switch** nella UI non richiedono PIN (per usabilità)
- ⚠️ I **pannelli allarme** richiedono PIN per disarmare se configurato
- ⚠️ Se vuoi protezione totale su tutte le entità, usa **SOLO i pannelli allarme e i servizi** nelle automazioni
- ⚠️ Il PIN è memorizzato nel database di HA (criptato)

## 🔄 Protezione Nativa Home Assistant (Opzionale)

Per proteggere anche gli switch con conferma nativa di HA:

1. Vai su **Impostazioni** → **Dispositivi e Servizi**
2. Trova il dispositivo TecnoAlarm
3. Clicca su uno switch programma
4. Clicca sull'icona ingranaggio ⚙️
5. Abilita **"Richiedi conferma"**

Questo aggiungerà una conferma visuale prima di attivare/disattivare lo switch.

## ❓ Domande Frequenti

### Come cambio il PIN?

1. Rimuovi l'integrazione
2. Riaggiungila con il nuovo PIN

### Cosa succede se dimentico il PIN?

1. Rimuovi l'integrazione (i dispositivi smetteranno di funzionare)
2. Riaggiungila senza PIN o con nuovo PIN
3. Le entità verranno ricreate

### Posso usare PIN diversi per programmi diversi?

No, c'è un solo PIN per tutta l'integrazione. Per PIN differenti, dovresti:
- Modificare il codice dell'integrazione
- Oppure usare automazioni con controllo logico in Home Assistant

### Il PIN è sicuro?

Sì, ma con limitazioni:
- ✅ Il PIN è verificato lato server
- ✅ Non appare in chiaro nei log
- ✅ È memorizzato nel database HA (criptato)
- ⚠️ Chiunque abbia accesso all'interfaccia HA può usare gli switch
- ⚠️ Chiunque abbia accesso alle automazioni può vedere il PIN nel YAML

## 📊 Esempi Avanzati

### Notifica se PIN Errato

```yaml
automation:
  - alias: "Notifica tentativo PIN errato"
    trigger:
      - platform: event
        event_type: system_log_event
    condition:
      - condition: template
        value_template: "{{ 'Invalid or missing PIN' in trigger.event.data.message }}"
    action:
      - service: notify.notify
        data:
          message: "⚠️ Tentativo di inserimento allarme con PIN errato!"
```

### Inserimento con Conferma Vocale

```yaml
automation:
  - alias: "Inserisci allarme con conferma vocale"
    trigger:
      - platform: state
        entity_id: person.mario_rossi
        to: "not_home"
    action:
      - service: tts.google_translate_say
        data:
          message: "Inserimento allarme in corso"
      - service: ha_tecnout.arm_program
        data:
          program_id: 1
          pin: "1234"
      - delay:
          seconds: 2
      - service: tts.google_translate_say
        data:
          message: "Allarme inserito correttamente"
```

### Inserimento Programmato

```yaml
automation:
  - alias: "Inserisci allarme di notte"
    trigger:
      - platform: time
        at: "23:00:00"
    condition:
      - condition: state
        entity_id: switch.program_1_totale
        state: "off"
    action:
      - service: ha_tecnout.arm_program
        data:
          program_id: 2  # Programma "Parziale Notte"
          pin: "1234"
```

## 🎯 Riepilogo

| Feature | Switch UI | Pannello Allarme | Servizi con PIN |
|---------|-----------|------------------|-----------------|
| Facile da usare | ✅ | ✅ | ⚙️ |
| Richiede PIN | ❌ | ✅ | ✅ |
| Protezione avanzata | ❌ | ✅ | ✅ |
| Interfaccia nativa | ✅ | ✅ | ❌ |
| Tastierino PIN | ❌ | ✅ | ❌ |
| Automazioni | ✅ | ✅ | ✅ |
| Dashboard | ✅ | ✅ | ✅ |
| Scripts | ✅ | ✅ | ✅ |
| Google/Alexa | ⚙️ | ✅ | ❌ |
| Notifiche errori | ❌ | ✅ | ✅ |

**Raccomandazione**: Usa **Pannelli Allarme** per l'interfaccia utente (migliore esperienza con PIN), **servizi con PIN** per automazioni critiche, e **switch** solo per uso interno senza necessità di protezione.

---

**Hai domande?** Consulta la documentazione principale o apri una issue su GitHub.

