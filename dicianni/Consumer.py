# consumer.py
#!/usr/bin/env python3

from os import system
from time import sleep
from Redis_News_Client import RedisNewsClient

def main():
    client = RedisNewsClient()
    
    print("Consumatore Notifiche")
    
    # Login
    EMAIL = login_user(client)
    if not EMAIL:
        return
    
    try:
        # Menu principale
        while True:
            system("clear || cls")
            
            canali_sottoscritti = client.get_user_channels(EMAIL)
            
            print(f"""
Consumer Notifiche - {EMAIL}:
  - (1) I miei canali ({len(canali_sottoscritti)})
  - (2) Sottoscrivi a canale
  - (3) Rimuovi sottoscrizione
  - (4) Notizie recenti (Lists)
  - (5) Notizie recenti (Streams) BONUS
  - (6) Ascolta real-time
  - (7) Ricerca per tempo (Streams) BONUS
  - (Q) Logout
            """)
            
            azione = input("Che azione vuoi fare? ").lower()
            
            if azione == "1":
                mostra_miei_canali(client, EMAIL)
            elif azione == "2":
                sottoscrivi_canale(client, EMAIL)
            elif azione == "3":
                rimuovi_sottoscrizione(client, EMAIL)
            elif azione == "4":
                mostra_notizie_lists(client, EMAIL)
            elif azione == "5":
                mostra_notizie_streams(client, EMAIL)
            elif azione == "6":
                ascolta_real_time(client, EMAIL)
            elif azione == "7":
                ricerca_per_tempo(client, EMAIL)
            elif azione == "q":
                break
            else:
                print("Comando invalido, riprova")
                sleep(1)
    
    finally:
        print("Logout completato!")

def login_user(client):
    """Login/registrazione"""
    EMAIL = input("Inserisci la tua email: ")
    
    if not EMAIL:
        print("Email obbligatoria!")
        return None
    
    if client.is_registered(EMAIL):
        print("Utente trovato, bentornato")
        
        password = input("Inserisci la tua password: ")
        if not client.authenticate_user(EMAIL, password):
            return None
    else:
        print("Devi registrarti")
        nome = input("Come ti chiami? ")
        password = input("Inserisci una password: ")
        
        if not client.register_user(EMAIL, password, nome):
            return None
    
    return EMAIL

def mostra_miei_canali(client, email):
    """Mostra canali sottoscritti"""
    canali = client.get_user_channels(email)
    
    if not canali:
        print("Non sei sottoscritto a nessun canale")
    else:
        print("I tuoi canali:")
        for canale in canali:
            stream_info = client.get_stream_info(canale)
            print(f"  - {canale} (Stream: {stream_info['length']} messaggi)")
    
    input("Premi ENTER per continuare...")

def sottoscrivi_canale(client, email):
    """Sottoscrizione a canale"""
    canali_disponibili = ["sport", "crypto", "cucina", "meteo", "cronaca", "tecnologia"]
    canali_attuali = client.get_user_channels(email)
    
    print("Canali disponibili:")
    for i, canale in enumerate(canali_disponibili, 1):
        status = "OK" if canale in canali_attuali else "NO"
        print(f"  {i}. [{status}] {canale}")
    
    try:
        scelta = int(input("Scegli canale (numero): ")) - 1
        canale = canali_disponibili[scelta]
        
        if client.subscribe_to_channel(email, canale):
            # Mostra preview ultime notizie
            notizie = client.get_notifiche_recenti(canale, 3)
            if notizie:
                print(f"\nUltime notizie da {canale}:")
                for notifica in notizie:
                    print(f"  - {notifica.get('titolo', 'N/A')}")
    except:
        print("Scelta non valida")
    
    sleep(2)

def rimuovi_sottoscrizione(client, email):
    """Rimuovi sottoscrizione"""
    canali = client.get_user_channels(email)
    
    if not canali:
        print("Non sei sottoscritto a nessun canale")
        sleep(2)
        return
    
    print("I tuoi canali:")
    for i, canale in enumerate(canali, 1):
        print(f"  {i}. {canale}")
    
    try:
        scelta = int(input("Canale da rimuovere (numero): ")) - 1
        canale = canali[scelta]
        
        if client.unsubscribe_from_channel(email, canale):
            print(f"Sottoscrizione rimossa da {canale}")
    except:
        print("Scelta non valida")
    
    sleep(2)

def mostra_notizie_lists(client, email):
    """Notizie da Lists"""
    canali = client.get_user_channels(email)
    
    if not canali:
        print("Sottoscrivi a dei canali prima!")
        input("Premi ENTER...")
        return
    
    print("NOTIZIE RECENTI (Lists):")
    for canale in canali:
        notizie = client.get_notifiche_recenti_lists(canale, 3)
        print(f"\n{canale.upper()}:")
        
        for notifica in notizie:
            print(f"  - {notifica.get('titolo', 'N/A')} ({notifica.get('priorita', 'N/A')})")
    
    input("Premi ENTER per continuare...")

def mostra_notizie_streams(client, email):
    """Notizie da Streams (BONUS)"""
    canali = client.get_user_channels(email)
    
    if not canali:
        print("Sottoscrivi a dei canali prima!")
        input("Premi ENTER...")
        return
    
    print("NOTIZIE RECENTI (Redis Streams - BONUS):")
    for canale in canali:
        notizie = client.get_notifiche_recenti_streams(canale, 3)
        stream_info = client.get_stream_info(canale)
        
        print(f"\n{canale.upper()} (Stream: {stream_info['length']} messaggi totali):")
        
        for notifica in notizie:
            stream_id = notifica.get('stream_id', 'N/A')
            print(f"  {notifica.get('titolo', 'N/A')} (ID: {stream_id})")
            print(f"  {notifica.get('messaggio', 'N/A')}")
    
    input("Premi ENTER per continuare...")

def ricerca_per_tempo(client, email):
    """Ricerca per range temporale (BONUS Streams)"""
    canali = client.get_user_channels(email)
    
    if not canali:
        print("Sottoscrivi a dei canali prima!")
        sleep(2)
        return
    
    print("RICERCA PER TEMPO (Redis Streams - BONUS)")
    
    canale = input(f"Canale ({'/'.join(canali)}): ")
    if canale not in canali:
        print("Canale non sottoscritto!")
        sleep(2)
        return
    
    ore_fa = int(input("Ore fa (default 24): ") or "24")
    
    notizie = client.get_notifiche_by_time_range(canale, ore_fa)
    
    print(f"\nNotizie {canale} ultime {ore_fa} ore:")
    print(f"Trovate {len(notizie)} notifiche con Streams")
    
    for i, notifica in enumerate(notizie[:10], 1):  # Prime 10
        timestamp = notifica.get('timestamp', 'N/A')
        print(f"  {i}. {notifica.get('titolo', 'N/A')}")
        print(f"      {timestamp}")
    
    input("Premi ENTER per continuare...")

def ascolta_real_time(client, email):
    """Ascolto real-time"""
    canali = client.get_user_channels(email)
    
    if not canali:
        print("Sottoscrivi a dei canali prima!")
        sleep(2)
        return
    
    def handler_notifica(notifica):
        """Handler per nuove notifiche"""
        priorita_sigla = {'bassa': 'BASSA', 'normale': 'NORM', 'alta': 'ALTA', 'urgente': 'URG'}
        sigla = priorita_sigla.get(notifica.get('priorita', 'normale'), 'NORM')
        
        # Ensure proper handling of notification data
        print(f"\nNUOVA NOTIFICA da {notifica.get('canale', 'N/A')}:")
        print(f"{notifica.get('titolo', 'N/A')} [{sigla}]")
        print(f"{notifica.get('messaggio', 'N/A')}")
        print("=" * 50)
    
    print(f"Ascolto real-time di {len(canali)} canali...")
    print("Usa il Producer per inviare notifiche e vederle qui!")
    
    # Usa il metodo con thread
    client.ascolta_con_thread(canali, handler_notifica)

if __name__ == "__main__":
    main()
