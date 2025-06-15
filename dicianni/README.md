# Sistema Notifiche Redis - Documentazione

## Cos'è
Sistema di notifiche real-time che combina **persistenza** e **messaggistica istantanea** usando Redis. Implementa un'architettura ibrida con Lists+Hash per la base e Streams per funzionalità avanzate.

## Architettura
```
Producer → Redis (Lists/Hash/Streams/Pub-Sub) → Consumer
```

- **Lists + Hash**: Persistenza base delle notifiche
- **Streams**: Log avanzato con timestamp (BONUS)
- **Pub/Sub**: Notifiche real-time istantanee
- **Sets**: Gestione utenti registrati

## Installazione e Avvio

### Con Docker (consigliato)
```bash
# 1. Avvia Redis e crea dati demo
docker-compose up redis demo

# 2. In un nuovo terminale - Consumer
docker-compose run --rm consumer

# 3. In un altro terminale - Producer  
docker-compose run --rm producer
```

### Locale
```bash
# Avvia Redis in locale
redis-server

# Crea dati demo
python demo.py

# Avvia applicazioni
python consumer.py  # terminale 1
python producer.py  # terminale 2
```

## Credenziali Demo
- `mario@test.it` / `123` → sport, cronaca
- `laura@test.it` / `321` → cucina, crypto  
- `giuseppe@test.it` / `password789` → meteo, sport
- `anna@test.it` / `passwordabc` → tecnologia

## Canali Disponibili
- **sport** → Calcio, tennis, olimpiadi
- **crypto** → Bitcoin, Ethereum, DeFi
- **cucina** → Ricette, ristoranti, chef
- **meteo** → Previsioni, allerte, clima
- **cronaca** → Politica, società, eventi
- **tecnologia** → AI, smartphone, innovazione

## Guida d'Uso

### Producer - Invia Notifiche
```
(A) Sport      → "Juventus batte Milan 3-1"
(B) Crypto     → "Bitcoin sopra $50K" 
(C) Cucina     → "Ricetta carbonara autentica"
(D) Custom     → Scegli canale/titolo/messaggio/priorità
(T) Test       → Funzionalità Streams avanzate
(Q) Esci
```

### Consumer - Ricevi Notifiche
```
(1) I miei canali        → Lista sottoscrizioni
(2) Sottoscrivi          → Aggiungi nuovo canale
(3) Rimuovi              → Cancella sottoscrizione  
(4) Notizie Lists        → Cronologia persistente
(5) Notizie Streams      → Log avanzato (BONUS)
(6) Ascolta real-time    → Notifiche istantanee
(7) Ricerca temporale    → Cerca per ore/giorni (BONUS)
(Q) Logout
```

## Test Real-time
1. **Consumer**: Opzione 6 "Ascolta real-time"
2. **Producer**: Invia notifica (A/B/C/D)
3. **Risultato**: Notifica appare istantaneamente nel Consumer

## Strutture Dati Redis

### Utenti
```redis
utenti_registrati: {"mario@test.it", "laura@test.it", ...}
utenti:mario@test.it: {nome: "Mario", password: "hash", canali_sottoscritti: "[\"sport\"]"}
```

### Notifiche Base (Lists + Hash)
```redis
notifiche_recenti:sport: [3, 2, 1]  # IDs cronologici
notifica_dettagli:sport:1: {titolo: "Juventus vince", messaggio: "...", priorita: "alta"}
n_notifiche:sport: 3  # Contatore incrementale
```

### Notifiche Streams (BONUS)
```redis
stream_notifiche:sport: [
  1704030300000-0: {titolo: "Juventus vince", messaggio: "...", timestamp: "..."},
  1704030250000-0: {titolo: "Milan pareggia", messaggio: "...", timestamp: "..."}
]
```

### Real-time (Pub/Sub)
```redis
canale_live:sport     # Channel per notifiche sport
canale_live:crypto    # Channel per notifiche crypto
```

## Comandi Redis Principali

### Gestione Utenti
```redis
SISMEMBER utenti_registrati mario@test.it    # Verifica registrazione
HGETALL utenti:mario@test.it                 # Dati utente completi
HSET utenti:mario@test.it canali_sottoscritti "[\"sport\"]"  # Aggiorna sottoscrizioni
```

### Notifiche Persistenti
```redis
LRANGE notifiche_recenti:sport 0 9           # Ultime 10 notifiche
HGETALL notifica_dettagli:sport:1            # Dettagli notifica specifica
INCR n_notifiche:sport                       # Nuovo ID notifica
```

### Streams (BONUS)
```redis
XADD stream_notifiche:sport * titolo "..." messaggio "..."     # Aggiungi notifica
XREVRANGE stream_notifiche:sport + - COUNT 10                  # Ultime 10
XRANGE stream_notifiche:sport 1704030000000-0 +                # Da timestamp
```

### Real-time
```redis
PUBLISH canale_live:sport '{"titolo":"Juventus vince"}'        # Invia notifica
SUBSCRIBE canale_live:sport                                    # Ascolta canale
```

## Priorità Notifiche
- **bassa** → Notizie generali
- **normale** → Notizie standard (default)
- **alta** → Notizie importanti  
- **urgente** → Allerte critiche

## Funzionalità BONUS (Streams)

### Ricerca Temporale
```python
# Cerca notifiche ultime 24 ore
client.get_notifiche_by_time_range("sport", 24)

# Info stream
client.get_stream_info("sport")  # Numero messaggi, primo/ultimo entry
```

### Persistenza Avanzata
- **Auto-cleanup**: Streams si eliminano dopo 24 ore
- **Timestamp automatico**: Ogni notifica ha timestamp preciso
- **Ricerca temporale**: Trova notifiche per range di ore/giorni

## Troubleshooting

### Container si chiude subito
```bash
# Invece di: docker-compose up -d
# Usa: docker-compose run --rm consumer
```

### Notifiche non arrivano in real-time
1. Verifica sottoscrizioni: Consumer opzione 1
2. Controlla canale giusto: Producer deve usare canale sottoscritto
3. Prova prima con Lists: Consumer opzione 4

### Redis non si connette
```bash
# Verifica Redis attivo
docker-compose ps
redis-cli ping  # Se locale

# Reset completo
docker-compose down
docker-compose up redis demo
```

### Database sporco
```bash
# Reset dati demo
docker-compose run --rm demo
```

## Performance
- **Lists**: ~10k notifiche/sec
- **Streams**: ~8k notifiche/sec  
- **Pub/Sub**: Latenza <1ms
- **Memoria**: ~1KB per notifica

## File Principali
- `Redis_News_Client.py` → Logica Redis core
- `producer.py` → Interfaccia invio notifiche
- `consumer.py` → Interfaccia ricezione notifiche  
- `demo.py` → Creazione dati di test
- `docker-compose.yml` → Configurazione Docker