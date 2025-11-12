# Changelog

## 1.4.0 – 2025-11-12
### ✨ Nuove Funzionalità
- **Aggiunta piattaforma Alarm Control Panel**: I programmi di allarme sono ora disponibili come entità `alarm_control_panel` native di Home Assistant
- **Supporto PIN integrato**: Richiesta PIN tramite tastierino numerico nativo nell'interfaccia utente (solo per disarmare)
- **Interfaccia migliorata**: Card `alarm-panel` standard con stati chiari (Disinserito, Inserito Totale, Inserito Parziale, Allarme Attivo)
- **Compatibilità assistenti vocali**: Supporto migliorato per Google Home e Alexa

### 🔄 Modifiche
- **Rimossi switch per programmi**: I programmi non sono più disponibili come switch, solo tramite `alarm_control_panel` (più appropriato per sistemi di allarme)
- **Switch solo per zone**: Gli switch ora controllano esclusivamente l'isolamento delle zone
- **PIN solo per disarmare**: L'inserimento dell'allarme NON richiede PIN (comportamento standard per maggiore praticità)

### 📚 Documentazione
- Aggiornata `PIN_PROTECTION.md` con guida completa ai pannelli di controllo allarme
- Aggiunti esempi di utilizzo con card `alarm-panel` e automazioni
- Tabella comparativa tra Switch, Pannelli Allarme e Servizi

## 1.3.0 – 2025-11-10
- Aggiunti switch per il controllo dell'isolamento delle zone
- I programmi con nome predefinito "Program X" (non configurati) vengono ora esclusi automaticamente dall'interfaccia
- Migliorata l'esperienza utente con entità più pulite e rilevanti

## 1.1.1 – 2025-11-07
- Disattivato il watchdog durante i test di connessione nel config flow e garantita la chiusura del client anche in caso di errore.
- Aumentato il timeout di connessione a 10 s per gestire reti lente o instabili.

## 1.1.0 – 2025-11-07
- Introdotta la protezione opzionale tramite PIN con i servizi `ha_tecnout.arm_program` e `ha_tecnout.disarm_program`.
- Validazione del PIN lato server, log sicuri e gestione degli errori dedicata.
- Aggiornata la documentazione, le traduzioni e definiti i servizi per l'interfaccia di Home Assistant.

