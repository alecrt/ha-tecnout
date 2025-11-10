# Changelog

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

