# 🔧 Hotfix v1.1.1 - Risoluzione Problema Connessione

**Data**: 07/11/2025  
**Versione**: 1.1.0 → **1.1.1**  
**Tipo**: Bug Fix Critico

## 🐛 Problema Rilevato

### Sintomo
Durante la configurazione dell'integrazione, se la connessione falliva:
- Errore "Failed to connect to the control panel"
- **Watchdog thread continuava a girare** in background ogni 30 secondi
- Log ripetuti: "Watchdog detected error 'Connection closed by remote host', attempting reconnect"

### Log Osservati
```
2025-11-07 16:44:01.667 WARNING (Thread-3 (_watchdog_loop)) 
[custom_components.ha_tecnout.tecnout.tecnout_client] 
Watchdog detected error 'Connection closed by remote host', attempting reconnect

2025-11-07 16:44:31.669 WARNING (Thread-3 (_watchdog_loop)) 
[custom_components.ha_tecnout.tecnout.tecnout_client] 
Watchdog detected error 'Connection closed by remote host', attempting reconnect

[...continua ogni 30 secondi...]
```

### Causa Root
1. **Config flow** creava client con watchdog attivo
2. **Watchdog partiva** durante il test di connessione
3. Se connessione **falliva**, `client.close()` non veniva eseguito
4. **Thread watchdog** continuava a girare indefinitamente

### Codice Problematico

**Prima** (`config_flow.py`):
```python
client = TecnoOutClient(
    host=data[CONF_HOST],
    port=data[CONF_PORT],
    user_code=data[CONF_USER_CODE],
    passphrase=data[CONF_PASSPHRASE],
    legacy=data.get(CONF_LEGACY, DEFAULT_LEGACY),
    watchdog_interval=data.get(CONF_WATCHDOG_INTERVAL),  # ← Watchdog attivo!
)

try:
    await hass.async_add_executor_job(client.connect)
    info = await hass.async_add_executor_job(client.get_info)
    await hass.async_add_executor_job(client.close)
except ConnectionError as err:
    raise CannotConnect from err  # ← client.close() mai chiamato!
```

## ✅ Soluzione Implementata

### Fix 1: Disabilitare Watchdog nel Config Flow

**Dopo** (`config_flow.py`):
```python
# Create client WITHOUT watchdog for connection test
# Watchdog will be enabled only when integration is fully set up
client = TecnoOutClient(
    host=data[CONF_HOST],
    port=data[CONF_PORT],
    user_code=data[CONF_USER_CODE],
    passphrase=data[CONF_PASSPHRASE],
    legacy=data.get(CONF_LEGACY, DEFAULT_LEGACY),
    watchdog_interval=None,  # ← Disable watchdog durante test!
)

try:
    await hass.async_add_executor_job(client.connect)
    info = await hass.async_add_executor_job(client.get_info)
except ConnectionError as err:
    raise CannotConnect from err
except Exception as err:
    _LOGGER.exception("Unexpected exception")
    raise InvalidAuth from err
finally:
    # Always close the client, even if there's an error
    try:
        await hass.async_add_executor_job(client.close)
    except Exception:
        pass  # Ignore errors during cleanup
```

**Cambimenti**:
- ✅ `watchdog_interval=None` → Watchdog NON parte durante config flow
- ✅ `finally` block → `client.close()` SEMPRE eseguito
- ✅ Watchdog si attiva solo quando l'integrazione è configurata correttamente

### Fix 2: Aumentato Timeout Connessione

**Prima** (`tecnout_client.py`):
```python
self._sock = socket.create_connection((self.host, self.port), timeout=0.5)
```

**Dopo**:
```python
self._sock = socket.create_connection((self.host, self.port), timeout=10.0)
```

**Motivazione**:
- 0.5 secondi troppo breve per reti lente o connessioni remote
- 10 secondi permette anche connessioni più lente

## 📝 File Modificati

| File | Modifica | Riga |
|------|----------|------|
| `config_flow.py` | Watchdog disabilitato + finally block | 46-81 |
| `tecnout_client.py` | Timeout aumentato da 0.5s a 10s | 181 |
| `manifest.json` | Versione 1.1.0 → 1.1.1 | 9 |

## ✅ Risultato Atteso

### Comportamento Corretto

**Durante Config Flow (test connessione)**:
- ✅ Watchdog **NON parte**
- ✅ Client si connette con timeout 10s
- ✅ Se fallisce → `client.close()` viene chiamato
- ✅ Nessun thread in background
- ✅ Nessun log ripetuto

**Dopo Configurazione (uso normale)**:
- ✅ Coordinator crea client **con watchdog attivo**
- ✅ Watchdog mantiene connessione
- ✅ Se problemi → watchdog tenta riconnessione
- ✅ Log solo se necessari

## 🧪 Test Scenari

### Scenario 1: Connessione Fallita
**Prima**:
- ❌ Config flow fallisce
- ❌ Watchdog continua a girare
- ❌ Log ogni 30 secondi infinitamente

**Dopo**:
- ✅ Config flow fallisce
- ✅ Client chiuso correttamente
- ✅ Nessun thread in background
- ✅ Nessun log ripetuto

### Scenario 2: Connessione Riuscita
**Prima**:
- ✅ Config flow OK
- ✅ Watchdog parte durante test (non necessario)
- ⚠️ Doppia istanza watchdog (test + coordinator)

**Dopo**:
- ✅ Config flow OK
- ✅ Watchdog NON parte durante test
- ✅ Watchdog parte solo nel coordinator
- ✅ Una sola istanza watchdog

### Scenario 3: Timeout Connessione
**Prima**:
- ❌ Timeout dopo 0.5 secondi
- ❌ Fallisce anche con rete OK ma lenta

**Dopo**:
- ✅ Timeout dopo 10 secondi
- ✅ Reti lente funzionano
- ✅ Connessioni remote funzionano

## 🚀 Come Aggiornare

### Rimuovi Configurazione Vecchia
1. Home Assistant → Impostazioni → Dispositivi e Servizi
2. Trova "TecnoAlarm TecnoOut"
3. Clicca sui tre puntini → "Elimina"

### Aggiorna File
1. Copia nuovi file `config_flow.py` e `tecnout_client.py`
2. Riavvia Home Assistant

### Riconfigura
1. Aggiungi integrazione "TecnoAlarm TecnoOut"
2. Inserisci credenziali
3. ✅ Dovrebbe connettersi senza watchdog in background

## 📊 Impatto

| Aspetto | Prima | Dopo |
|---------|-------|------|
| Thread watchdog durante test | ❌ Sì (bug) | ✅ No |
| Cleanup client su errore | ❌ No | ✅ Sì (finally) |
| Timeout connessione | 0.5s | 10s |
| Log ripetuti su fallimento | ❌ Sì | ✅ No |
| Gestione errori | Parziale | Completa |

## 🔍 Debug Suggerito

Se continui ad avere problemi di connessione:

### 1. Verifica Rete
```bash
ping [IP_CENTRALE]
telnet [IP_CENTRALE] 10001
```

### 2. Verifica Credenziali
- User Code: numerico 0-999999
- Passphrase: max 16 caratteri
- Porta: default 10001

### 3. Log Dettagliati
Aggiungi in `configuration.yaml`:
```yaml
logger:
  default: info
  logs:
    custom_components.ha_tecnout: debug
    custom_components.ha_tecnout.tecnout.tecnout_client: debug
```

### 4. Errori Comuni

**"Connection closed by remote host"**:
- Credenziali errate
- Crittografia fallita
- Protocollo non corretto

**"Connection timeout"**:
- IP irraggiungibile
- Porta bloccata da firewall
- Rete lenta (ora dovrebbe funzionare con 10s timeout)

**"Invalid auth"**:
- User code errato
- Passphrase errata
- Legacy mode necessario

## ✅ Conclusione

**Bug Risolto**: ✅ Watchdog non parte più durante config flow  
**Timeout Migliorato**: ✅ Aumentato da 0.5s a 10s  
**Gestione Errori**: ✅ Finally block assicura cleanup  
**Versione**: 1.1.1  

L'integrazione ora gestisce correttamente i fallimenti di connessione senza lasciare thread in background.

---

**Per problemi persistenti**, controlla i log con debug abilitato e verifica connettività di rete.

