# Guida al Contributo

Grazie per il tuo interesse nel contribuire a TecnoAlarm TecnoOut! 🎉

## 🚀 Come Contribuire

### Segnalare Bug

1. Controlla se il bug è già stato segnalato nelle [Issues](https://github.com/alecrt/ha-tecnout/issues)
2. Se non esiste, crea una nuova issue usando il template "Bug Report"
3. Fornisci quanti più dettagli possibili:
   - Versione Home Assistant
   - Versione integrazione
   - Log di errore
   - Passi per riprodurre

### Proporre Nuove Funzionalità

1. Apri una issue usando il template "Feature Request"
2. Descrivi chiaramente la funzionalità e il problema che risolve
3. Discuti con i maintainer prima di iniziare l'implementazione

### Inviare Pull Request

1. **Fork** il repository
2. **Crea un branch** per la tua feature (`git checkout -b feature/amazing-feature`)
3. **Configura l'ambiente di sviluppo** (vedi sotto)
4. **Fai le tue modifiche** seguendo le linee guida di codice
5. **Testa** le modifiche
6. **Commit** le modifiche (`git commit -m 'Add amazing feature'`)
7. **Push** al branch (`git push origin feature/amazing-feature`)
8. **Apri una Pull Request**

## 🛠️ Setup Ambiente di Sviluppo

### Prerequisiti

- Python 3.11 o superiore
- Home Assistant (per test)
- Git

### Installazione

```bash
# Clone del repository
git clone https://github.com/alecrt/ha-tecnout.git
cd ha-tecnout

# Crea ambiente virtuale
python -m venv venv

# Attiva ambiente virtuale
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# Installa dipendenze di sviluppo
pip install -r requirements-dev.txt
```

## 📝 Linee Guida di Codice

### Stile del Codice

Questo progetto segue le [linee guida di Home Assistant](https://developers.home-assistant.io/docs/development_index):

- **PEP 8** per lo stile Python
- **Black** per formattazione automatica
- **isort** per ordinamento import
- **Ruff** per linting
- **Type hints** obbligatori

### Esegui i Tool di Qualità

Prima di fare commit, esegui:

```bash
# Formattazione automatica
black custom_components/ha_tecnout
isort custom_components/ha_tecnout

# Linting
ruff check custom_components/ha_tecnout

# Type checking
mypy custom_components/ha_tecnout
```

### Struttura del Codice

- `__init__.py`: Entry point, setup/unload
- `config_flow.py`: Configurazione UI
- `coordinator.py`: Data Update Coordinator
- `const.py`: Costanti
- `binary_sensor.py`: Piattaforma sensori zone
- `switch.py`: Piattaforma switch programmi
- `services.yaml`: Definizione servizi
- `strings.json`: Traduzioni (italiano)
- `translations/en.json`: Traduzioni (inglese)

## 🧪 Testing

### Test Manuali

1. Copia `custom_components/ha_tecnout` nella tua installazione Home Assistant
2. Riavvia Home Assistant
3. Configura l'integrazione dall'UI
4. Testa tutte le funzionalità

### Test Automatici (TODO)

Il progetto non ha ancora unit test, ma è un obiettivo futuro:

```bash
# Quando disponibili
pytest tests/
```

## 📋 Checklist Pull Request

Prima di aprire una PR, assicurati che:

- [ ] Il codice segue le linee guida di stile
- [ ] Hai eseguito Black, isort, e Ruff senza errori
- [ ] Hai testato le modifiche localmente
- [ ] Hai aggiornato la documentazione se necessario
- [ ] Hai aggiunto/aggiornato le traduzioni se necessario
- [ ] Il commit message è chiaro e descrittivo

## 📖 Documentazione

Quando apporti modifiche, aggiorna anche:

- `README.md` - se cambi funzionalità principali
- `info.md` - per descrizione HACS
- `CHANGELOG_PIN.md` - per la cronologia delle modifiche
- Docstrings nel codice - per nuove classi/metodi

## 🔄 Processo di Review

1. Un maintainer revisionerà la tua PR
2. Potrebbero essere richieste modifiche
3. Una volta approvata, la PR verrà merged
4. Le modifiche saranno incluse nella prossima release

## 🌍 Traduzioni

Per aggiungere una nuova lingua:

1. Crea `custom_components/ha_tecnout/translations/[LANG_CODE].json`
2. Traduci tutte le stringhe da `strings.json`
3. Testa la traduzione in Home Assistant

Lingue supportate:
- 🇮🇹 Italiano (strings.json)
- 🇬🇧 Inglese (translations/en.json)

## 💡 Best Practice

### Commit Messages

Usa commit message descrittivi:

```bash
# Buoni esempi
git commit -m "Fix: Corretto errore nella gestione PIN vuoto"
git commit -m "Feature: Aggiunto supporto per programmi multipli"
git commit -m "Docs: Aggiornata documentazione servizi"

# Evita
git commit -m "fix"
git commit -m "changes"
git commit -m "update"
```

### Branch Names

Usa nomi descrittivi:

```bash
feature/nome-funzionalita
bugfix/nome-bug
docs/descrizione-doc
refactor/cosa-refactori
```

## 🎯 Aree di Contributo

Cerchiamo aiuto in queste aree:

### Alta Priorità
- [ ] Unit tests e test di integrazione
- [ ] Supporto per discovery automatico
- [ ] Diagnostics support
- [ ] Reauthentication flow

### Media Priorità
- [ ] Traduzioni aggiuntive (francese, tedesco, spagnolo)
- [ ] Miglioramenti UI/UX
- [ ] Ottimizzazioni performance
- [ ] Documentazione avanzata

### Bassa Priorità
- [ ] Esempi di automazioni
- [ ] Blueprint per automazioni comuni
- [ ] Video tutorial
- [ ] FAQ espansa

## 📞 Supporto

Se hai domande:

1. Controlla la [documentazione](README.md)
2. Cerca nelle [Issues esistenti](https://github.com/alecrt/ha-tecnout/issues)
3. Apri una nuova issue con tag "question"

## 📜 Licenza

Contribuendo a questo progetto, accetti che i tuoi contributi saranno rilasciati sotto la [Licenza MIT](LICENSE).

## 🙏 Riconoscimenti

Grazie a tutti i contributori che aiutano a migliorare questa integrazione!

---

**Happy coding! 🚀**

