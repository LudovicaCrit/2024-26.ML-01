# demo.py
#!/usr/bin/env python3

from Redis_News_Client import RedisNewsClient
import time

def crea_dati_demo():
    """Crea dati demo per testare il sistema"""
    client = RedisNewsClient()
    
    # Drop all existing data in Redis
    client.r.flushdb()
    print("Database Redis eliminato e ricreato.")

    # Proceed with demo data creation
    print("CREAZIONE DATI DEMO")
    print("Sistema: Lists + Hash + Sets + Pub/Sub")
    print("Bonus: Redis Streams per persistenza avanzata")
    print("=" * 50)
    
    # 1. UTENTI DEMO
    print("\n1. CREAZIONE UTENTI DEMO")
    print("-" * 30)
    
    utenti_demo = [
        ("mario@test.it", "123", "Mario", ["sport", "cronaca"]),
        ("laura@test.it", "321", "Laura", ["cucina", "crypto"]),
        ("giuseppe@test.it", "password789", "Giuseppe", ["meteo", "sport"]),
        ("anna@test.it", "passwordabc", "Anna", ["tecnologia"])
    ]
    
    for email, password, nome, canali in utenti_demo:
        if client.register_user(email, password, nome):
            print(f"Utente {nome} creato")
            
            # Sottoscrivi ai canali
            for canale in canali:
                client.subscribe_to_channel(email, canale)
    
    # 2. NOTIZIE DEMO
    print("\n2. PUBBLICAZIONE NOTIZIE DEMO")
    print("-" * 30)
    
    notizie_demo = [
        # Sport
        ("sport", "Juventus batte Milan 3-1", "Partita spettacolare allo Stadium", "alta"),
        ("sport", "Federer si ritira", "Il campione svizzero annuncia il ritiro", "normale"),
        
        # Crypto
        ("crypto", "Bitcoin supera $60K", "Nuovo record storico per la criptovaluta", "alta"),
        ("crypto", "Ethereum 2.0 completo", "L'upgrade della blockchain è realtà", "normale"),
        
        # Cucina
        ("cucina", "Carbonara autentica", "I veri segreti della ricetta romana", "normale"),
        ("cucina", "Ristorante stellato", "Apre il nuovo locale di Cracco", "bassa"),
        
        # Meteo
        ("meteo", "Allerta temporali", "Weekend di piogge intense al Nord", "urgente"),
        ("meteo", "Prima neve", "Imbiancate le Alpi sopra i 2000m", "normale"),
        
        # Cronaca
        ("cronaca", "Elezioni comunali", "Ballottaggio decisivo in 25 città", "normale"),
        ("cronaca", "Scoperta Pompei", "Nuova villa romana perfettamente conservata", "bassa"),
        
        # Tecnologia
        ("tecnologia", "iPhone 16 presentato", "Apple svela le innovazioni del futuro", "normale"),
        ("tecnologia", "ChatGPT-5 rivoluzionario", "AI supera tutti i test di Turing", "alta")
    ]
    
    published_count = 0
    for canale, titolo, messaggio, priorita in notizie_demo:
        notizia_id = client.pubblica_notifica(canale, titolo, messaggio, priorita)
        published_count += 1
        
        priorita_sigla = {'bassa': 'BASSA', 'normale': 'NORMALE', 'alta': 'ALTA', 'urgente': 'URGENTE'}
        sigla = priorita_sigla.get(priorita, 'NORMALE')
        
        print(f"#{notizia_id} {canale.upper()}: {titolo} [{sigla}]")
        
        # Piccolo delay per timestamp diversi
        time.sleep(0.1)
    
    print(f"\n{published_count} notizie pubblicate!")
    print("Ogni notifica salvata in:")
    print("   - Lists + Hash")
    print("   - Streams (bonus)")
    print("   - Pub/Sub (real-time)")
    
    print(f"\nDEMO COMPLETATA!")
    print("=" * 50)
    print("Sistema pronto per il test!")
    print()
    print("Per testare:")
    print("1. python producer.py  # Invia notizie")
    print("2. python consumer.py  # Ricevi notizie")
    print()
    print("Credenziali demo:")
    print("   - mario@test.it / password123 (sport, cronaca)")
    print("   - laura@test.it / password456 (cucina, crypto)")
    print("   - giuseppe@test.it / password789 (meteo, sport)")
    print("   - anna@test.it / passwordabc (tecnologia)")
    print()
    print("BONUS FEATURES:")
    print("   - Producer opzione T: Test Streams avanzato")
    print("   - Consumer opzione 5: Notizie da Streams")
    print("   - Consumer opzione 7: Ricerca temporale")

if __name__ == "__main__":
    crea_dati_demo()