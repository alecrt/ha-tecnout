# 🔐 Protezione con PIN - TecnoAlarm TecnoOut

## Panoramica

L'integrazione TecnoAlarm TecnoOut supporta la **protezione con PIN** per armare e disarmare i programmi di allarme, aggiungendo un ulteriore livello di sicurezza.

## 🎯 Come Funziona

### 1. Configurazione del PIN

Durante la configurazione dell'integrazione, puoi specificare un **PIN di Controllo** opzionale:

- **Impostazioni** → **Dispositivi e Servizi** → **Aggiungi Integrazione** → **TecnoAlarm TecnoOut**
- Nel campo **"PIN di Controllo (opzionale)"** inserisci un PIN numerico (es: `1234`)
- Se lasci vuoto il campo, i servizi funzioneranno senza richiedere PIN

### 2. Comportamento

#### Con PIN Configurato

Quando un PIN è configurato:

- ✅ I **servizi custom** richiedono il PIN per funzionare
- ✅ Gli **switch** nella UI continuano a funzionare normalmente
- ✅ Il PIN è verificato lato server (sicuro)
- ❌ Chiamate ai servizi senza PIN o con PIN errato vengono rifiutate

#### Senza PIN Configurato

Se non configuri un PIN:

- ✅ Tutto funziona normalmente senza restrizioni
- ✅ Switch e servizi funzionano liberamente

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
- ⚠️ Se vuoi protezione totale, usa **SOLO i servizi** nelle automazioni
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

| Feature | Switch UI | Servizi con PIN |
|---------|-----------|-----------------|
| Facile da usare | ✅ | ⚙️ |
| Richiede PIN | ❌ | ✅ |
| Protezione avanzata | ❌ | ✅ |
| Automazioni | ✅ | ✅ |
| Dashboard | ✅ | ✅ |
| Scripts | ✅ | ✅ |
| Notifiche errori | ❌ | ✅ |

**Raccomandazione**: Usa **servizi con PIN** per automazioni critiche e switch per uso manuale quotidiano.

---

**Hai domande?** Consulta la documentazione principale o apri una issue su GitHub.

