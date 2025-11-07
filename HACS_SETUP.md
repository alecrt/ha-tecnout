# Guida alla Pubblicazione su HACS

Questa guida descrive i passi necessari per pubblicare l'integrazione TecnoAlarm TecnoOut su HACS (Home Assistant Community Store).

## ✅ Requisiti Completati

Il progetto è già stato configurato per essere compatibile con HACS:

- ✅ Struttura directory corretta (`custom_components/ha_tecnout/`)
- ✅ File `hacs.json` presente nella root
- ✅ File `info.md` per la descrizione in HACS
- ✅ File `manifest.json` correttamente configurato
- ✅ README.md completo
- ✅ LICENSE file (MIT)
- ✅ GitHub workflows per CI/CD
- ✅ Repository GitHub: https://github.com/alecrt/ha-tecnout

## 📦 Passi per la Pubblicazione

### 1. Preparazione Repository GitHub

Prima di pubblicare, assicurati di:

```bash
# Aggiungi tutti i file al repository
git add .

# Crea il primo commit
git commit -m "Initial release v1.1.0"

# Aggiungi il repository remoto (se non già fatto)
git remote add origin https://github.com/alecrt/ha-tecnout.git

# Pusha il codice
git push -u origin main
```

### 2. Crea il Primo Tag/Release

HACS richiede almeno una release GitHub:

```bash
# Crea un tag per la versione 1.1.0
git tag -a v1.1.0 -m "Release v1.1.0"

# Pusha il tag
git push origin v1.1.0
```

Oppure crea una release direttamente da GitHub:
1. Vai su https://github.com/alecrt/ha-tecnout/releases/new
2. Tag version: `v1.1.0`
3. Release title: `v1.1.0 - Initial Release`
4. Descrizione: Copia il contenuto da `CHANGELOG_PIN.md` o scrivi le funzionalità principali
5. Clicca "Publish release"

### 3. Aggiungi il Repository a HACS

Gli utenti possono aggiungere l'integrazione come **repository custom**:

1. Apri HACS in Home Assistant
2. Vai su "Integrations"
3. Clicca sui tre puntini in alto a destra
4. Seleziona "Custom repositories"
5. Inserisci l'URL: `https://github.com/alecrt/ha-tecnout`
6. Categoria: `Integration`
7. Clicca "Add"

### 4. (Opzionale) Richiesta Inclusione in HACS Default

Per far apparire l'integrazione nell'elenco di default di HACS, devi fare richiesta al team HACS:

1. Vai su: https://github.com/hacs/default/issues/new/choose
2. Scegli "Add to default" template
3. Compila il form con:
   - Repository: `https://github.com/alecrt/ha-tecnout`
   - Categoria: Integration
   - Descrizione dell'integrazione
   - Perché dovrebbe essere aggiunta

**Nota**: Per essere accettata in HACS default, l'integrazione deve rispettare criteri di qualità più stringenti. La tua integrazione è già ben strutturata e dovrebbe avere buone possibilità.

## 🔄 Rilascio di Nuove Versioni

Quando rilasci una nuova versione:

1. Aggiorna il campo `version` in `custom_components/ha_tecnout/manifest.json`
2. Aggiorna il `CHANGELOG_PIN.md` con le novità
3. Commit e push:
   ```bash
   git add .
   git commit -m "Release v1.2.0"
   git push
   ```
4. Crea un nuovo tag:
   ```bash
   git tag -a v1.2.0 -m "Release v1.2.0"
   git push origin v1.2.0
   ```
5. Crea la release su GitHub (questo triggerera il workflow automatico)

Il workflow `.github/workflows/release.yaml` creerà automaticamente lo zip per la release.

## 📋 Checklist Pre-Release

Prima di ogni release, verifica:

- [ ] Versione aggiornata in `manifest.json`
- [ ] CHANGELOG aggiornato
- [ ] README aggiornato (se necessario)
- [ ] Codice testato localmente
- [ ] Nessun errore di linting (esegui `ruff check`)
- [ ] Codice formattato (esegui `black` e `isort`)
- [ ] GitHub workflows passano (dopo il push)

## 🛠️ Test Locale dell'Integrazione

Prima di pubblicare, testa l'integrazione localmente:

1. Copia la cartella `custom_components/ha_tecnout` in:
   - `/config/custom_components/ha_tecnout` (Home Assistant)
   
2. Riavvia Home Assistant

3. Configura l'integrazione dall'interfaccia UI

4. Verifica tutte le funzionalità:
   - Configurazione via UI
   - Sensori zone
   - Switch programmi
   - Servizi con PIN

## 📊 Monitoraggio

Dopo la pubblicazione:

- Monitora le Issues su GitHub: https://github.com/alecrt/ha-tecnout/issues
- Controlla i workflow GitHub Actions per errori
- Verifica che gli utenti riescano a installare correttamente l'integrazione

## 🎯 Obiettivi Futuri

Per migliorare ulteriormente l'integrazione:

- [ ] Aggiungere unit tests (per coverage 90%+)
- [ ] Implementare diagnostics support
- [ ] Aggiungere reauthentication flow
- [ ] Creare traduzioni aggiuntive
- [ ] Documentazione più dettagliata
- [ ] Raggiungere Quality Scale Silver/Gold

## 🔗 Link Utili

- **HACS Documentation**: https://hacs.xyz/
- **HACS Default Repositories**: https://github.com/hacs/default
- **Home Assistant Developer Docs**: https://developers.home-assistant.io/
- **GitHub Actions**: https://docs.github.com/en/actions

## ❓ Domande Frequenti

### Come aggiorno l'integrazione su HACS?

Quando crei una nuova release su GitHub, HACS rileverà automaticamente l'aggiornamento. Gli utenti vedranno l'aggiornamento disponibile in HACS.

### Posso cambiare il nome dell'integrazione?

Sì, ma dovrai aggiornare:
- `manifest.json` (campo `name`)
- `hacs.json` (campo `name`)
- `README.md`
- `info.md`

### Come funziona il workflow di release?

Il workflow `.github/workflows/release.yaml` si attiva automaticamente quando crei una release su GitHub. Verifica che la versione nel manifest corrisponda al tag e crea uno zip dell'integrazione.

### Devo caricare lo zip manualmente?

No, il workflow lo fa automaticamente. Assicurati solo che il tag della release corrisponda alla versione nel `manifest.json` (es. tag `v1.1.0` = versione `1.1.0`).

---

**Buona fortuna con la pubblicazione! 🚀**

Se hai domande o problemi, apri una issue su GitHub.

