# redis_news_client.py
import redis
import json
import hashlib
import os
from datetime import datetime, timedelta
from time import sleep

class RedisNewsClient:
    def __init__(self):
        # Usa variabili ambiente per Docker
        redis_host = os.getenv('REDIS_HOST', 'localhost')
        redis_port = int(os.getenv('REDIS_PORT', 6379))
        
        self.r = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
        
        if not self.r.ping():
            raise Exception("Redis non funzionante")
        
        # Configurazione persistenza notifiche
        self.notification_expiry_hours = 24
    
    # ==================== UTENTI (Hash + Sets) ====================
    
    def is_registered(self, email: str) -> bool:
        """Check se utente è registrato"""
        return self.r.sismember("utenti_registrati", email)
    
    def register_user(self, email: str, password: str, nome: str) -> bool:
        """Registra utente"""
        if self.is_registered(email):
            print("Utente già registrato")
            return False
        
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        with self.r.pipeline() as pipe:
            pipe.sadd("utenti_registrati", email)
            pipe.hset(f"utenti:{email}", mapping={
                "nome": nome,
                "password": password_hash,
                "canali_sottoscritti": json.dumps([]),
                "created_at": datetime.now().isoformat()
            })
            pipe.execute()
        
        print("Registrazione completata!")
        return True
    
    def authenticate_user(self, email: str, password: str) -> bool:
        """Autentica utente"""
        if not self.is_registered(email):
            return False
        
        user_dict = self.r.hgetall(f"utenti:{email}")
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        if password_hash != user_dict["password"]:
            print("Password errata")
            return False
        
        print(f"Sei autenticato, benvenuto {user_dict['nome']}")
        return True
    
    def get_user_channels(self, email: str) -> list:
        """Ottiene canali sottoscritti"""
        if not self.is_registered(email):
            return []
        
        user_dict = self.r.hgetall(f"utenti:{email}")
        return json.loads(user_dict.get("canali_sottoscritti", "[]"))
    
    def subscribe_to_channel(self, email: str, canale: str) -> bool:
        """Sottoscrivi a canale"""
        canali = self.get_user_channels(email)
        
        if canale not in canali:
            canali.append(canale)
            self.r.hset(f"utenti:{email}", "canali_sottoscritti", json.dumps(canali))
            print(f"Sottoscritto a {canale}")
            return True
        
        print(f"Già sottoscritto a {canale}")
        return False
    
    def unsubscribe_from_channel(self, email: str, canale: str) -> bool:
        """Rimuovi sottoscrizione"""
        canali = self.get_user_channels(email)
        
        if canale in canali:
            canali.remove(canale)
            self.r.hset(f"utenti:{email}", "canali_sottoscritti", json.dumps(canali))
            return True
        
        return False
    
    # ==================== NOTIFICHE - SISTEMA IBRIDO ====================
    
    def pubblica_notifica(self, canale: str, titolo: str, messaggio: str, priorita: str = "normale"):
        """
        Pubblica notifica con sistema ibrido:
        1. Lists + Hash per persistenza base
        2. Redis Streams per persistenza avanzata (BONUS)
        3. Pub/Sub per real-time
        """
        timestamp = datetime.now()
        
        # ID incrementale
        notifica_id = self.r.incr(f"n_notifiche:{canale}")
        
        notifica_data = {
            "id": notifica_id,
            "titolo": titolo,
            "messaggio": messaggio,
            "canale": canale,
            "priorita": priorita,
            "timestamp": timestamp.isoformat(),
            "timestamp_unix": int(timestamp.timestamp())
        }
        
        with self.r.pipeline() as pipe:
            # 1. SISTEMA BASE - Lists + Hash
            # Hash per dettagli notifica
            pipe.hset(f"notifica_dettagli:{canale}:{notifica_id}", mapping=notifica_data)
            
            # List per cronologia
            pipe.lpush(f"notifiche_recenti:{canale}", str(notifica_id))
            
            # Mantieni solo ultime N notifiche per canale (requisito persistenza)
            pipe.ltrim(f"notifiche_recenti:{canale}", 0, 99)
            
            # 2. SISTEMA BONUS - Redis Streams
            stream_key = f"stream_notifiche:{canale}"
            pipe.xadd(stream_key, notifica_data)
            
            # TTL per streams (persistenza N ore come richiesto)
            expire_seconds = self.notification_expiry_hours * 3600
            pipe.expire(stream_key, expire_seconds)
            
            pipe.execute()
        
        # 3. PUB/SUB per real-time
        self.r.publish(f"canale_live:{canale}", json.dumps(notifica_data))
        
        return notifica_id
    
    # ==================== RECUPERO NOTIFICHE ====================
    
    def get_notifiche_recenti_lists(self, canale: str, limite: int = 10) -> list:
        """Recupera notifiche da Lists"""
        ids = self.r.lrange(f"notifiche_recenti:{canale}", 0, limite - 1)
        return [self.r.hgetall(f"notifica_dettagli:{canale}:{id}") for id in ids]
    
    def get_notifiche_recenti_streams(self, canale: str, limite: int = 10) -> list:
        """Recupera notifiche da Streams (BONUS)"""
        try:
            stream_key = f"stream_notifiche:{canale}"
            messages = self.r.xrevrange(stream_key, count=limite)
            
            notifiche = []
            for message_id, fields in messages:
                notifica = dict(fields)
                notifica['stream_id'] = message_id
                notifiche.append(notifica)
            
            return notifiche
        except Exception as e:
            print(f"Errore Streams: {e}")
            return []
    
    def get_notifiche_recenti(self, canale: str, limite: int = 10) -> list:
        """Recupera notifiche recenti (con fallback automatico)"""
        # Prova prima con Streams, poi fallback a Lists
        notifiche = self.get_notifiche_recenti_streams(canale, limite)
        if notifiche:
            return notifiche
        
        return self.get_notifiche_recenti_lists(canale, limite)
    
    # ==================== STREAMS FEATURES (BONUS) ====================
    
    def get_stream_info(self, canale: str) -> dict:
        """Info stream (BONUS)"""
        try:
            stream_key = f"stream_notifiche:{canale}"
            info = self.r.xinfo_stream(stream_key)
            return {
                'length': info.get('length', 0),
                'first_entry': info.get('first-entry'),
                'last_entry': info.get('last-entry')
            }
        except:
            return {'length': 0}
    
    def get_notifiche_by_time_range(self, canale: str, ore_fa: int = 24) -> list:
        """Ricerca notifiche per range temporale (BONUS Streams)"""
        try:
            stream_key = f"stream_notifiche:{canale}"
            
            # Calcola timestamp di inizio
            start_time = int((datetime.now() - timedelta(hours=ore_fa)).timestamp() * 1000)
            start_id = f"{start_time}-0"
            
            # XRANGE con range temporale
            messages = self.r.xrange(stream_key, min=start_id, max='+')
            
            notifiche = []
            for message_id, fields in messages:
                notifica = dict(fields)
                notifica['stream_id'] = message_id
                notifiche.append(notifica)
            
            return notifiche
        except Exception as e:
            print(f"Errore range temporale: {e}")
            return []
    
    # ==================== PUB/SUB REAL-TIME ====================
    
    def ascolta_notifiche_realtime(self, canali: list, handler_function):
        """Ascolta notifiche real-time con Pub/Sub"""
        p = self.r.pubsub()
        
        # Subscribe a tutti i canali
        for canale in canali:
            p.subscribe(f"canale_live:{canale}")
        
        print(f"In ascolto real-time di {len(canali)} canali...")
        
        # Loop ascolto
        while True:
            msg = p.get_message()
            
            if msg and msg["type"] == "message":
                try:
                    canale = msg["channel"].replace("canale_live:", "")
                    notifica = json.loads(msg["data"])
                    handler_function(notifica)
                except json.JSONDecodeError:
                    continue
            
            sleep(0.01)
    
    def ascolta_con_thread(self, canali: list, handler_function):
        """Versione con thread per real-time"""
        p = self.r.pubsub()
        
        # Crea wrapper handler che deserializza JSON
        def wrapped_handler(message):
            try:
                # Deserializza JSON string in dizionario Python
                notifica = json.loads(message['data'])
                # Chiama l'handler originale con dati deserializzati
                handler_function(notifica)
            except (json.JSONDecodeError, KeyError, TypeError) as e:
                print(f"Errore parsing notifica: {e}")
                print(f"Dati ricevuti: {message}")
    
        # Subscribe con handler wrapped
        channel_handlers = {}
        for canale in canali:
            channel_handlers[f"canale_live:{canale}"] = wrapped_handler
        
        p.subscribe(**channel_handlers)
        
        # Run in thread
        t = p.run_in_thread(0.01)
        
        input("Premi ENTER per interrompere..\n")
        t.stop()
        
        return t