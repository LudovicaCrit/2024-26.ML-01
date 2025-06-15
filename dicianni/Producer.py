# producer.py
#!/usr/bin/env python3

from os import system
from time import sleep
from Redis_News_Client import RedisNewsClient

def main():
    client = RedisNewsClient()
    
    print("Produttore Notifiche")
    print("Sistema: Lists + Hash + Pub/Sub")
    print("Bonus: Redis Streams per persistenza avanzata")
    
    while True:
        system("clear || cls")
        
        print(f"""
Produttore Notifiche:
  - (A) Pubblica notizia Sport
  - (B) Pubblica notizia Crypto  
  - (C) Pubblica notizia Cucina
  - (D) Notizia personalizzata
  - (T) Test sistema Streams (BONUS)
  - (Q) Esci
        """)
        
        azione = input("Che azione vuoi fare? ").lower()
        
        if azione == "a":
            pubblica_notizia_veloce(client, "sport")
        elif azione == "b":
            pubblica_notizia_veloce(client, "crypto")
        elif azione == "c":
            pubblica_notizia_veloce(client, "cucina")
        elif azione == "d":
            pubblica_notizia_custom(client)
        elif azione == "t":
            test_streams_features(client)
        elif azione == "q":
            break
        else:
            print("Comando invalido, riprova")
            sleep(1)

def pubblica_notizia_veloce(client, canale):
    """Pubblica notizia rapida"""
    esempi = {
        "sport": ("Juventus vince 2-1", "Grande partita allo Stadium", "alta"),
        "crypto": ("Bitcoin sopra $50K", "Nuovo record per la criptovaluta", "normale"),
        "cucina": ("Ricetta carbonara", "I segreti della pasta romana", "normale")
    }
    
    titolo, contenuto, priorita = esempi[canale]
    notizia_id = client.pubblica_notifica(canale, titolo, contenuto, priorita)
    
    print(f"Notifica #{notizia_id} pubblicata!")
    print(f"Salvata in Lists e Streams")
    print(f"Inviata via Pub/Sub")
    
    sleep(3)

def pubblica_notizia_custom(client):
    """Pubblica notizia personalizzata"""
    canale = input("Canale (sport/crypto/cucina/meteo/cronaca/tecnologia): ")
    titolo = input("Titolo: ")
    messaggio = input("Messaggio: ")
    priorita = input("Priorità (bassa/normale/alta/urgente): ") or "normale"
    
    notizia_id = client.pubblica_notifica(canale, titolo, messaggio, priorita)
    print(f"Notifica #{notizia_id} pubblicata!")
    sleep(2)

def test_streams_features(client):
    """Test funzionalità Streams (BONUS)"""
    print("\nTEST REDIS STREAMS (BONUS)")
    
    canale = input("Canale da testare: ") or "sport"
    
    # Info stream
    info = client.get_stream_info(canale)
    print(f"\nInfo Stream '{canale}':")
    print(f"   Messaggi: {info['length']}")
    
    # Test range temporale
    ore_fa = int(input("Notifiche ultime N ore (default 24): ") or "24")
    notifiche_range = client.get_notifiche_by_time_range(canale, ore_fa)
    
    print(f"\nNotifiche ultime {ore_fa} ore:")
    for i, notifica in enumerate(notifiche_range[:5], 1):
        print(f"   {i}. {notifica.get('titolo', 'N/A')} ({notifica.get('priorita', 'N/A')})")
    
    input("Premi ENTER per continuare...")

if __name__ == "__main__":
    main()