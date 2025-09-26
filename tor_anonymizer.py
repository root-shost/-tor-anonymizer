#!/usr/bin/env python3
"""
Tor Anonymizer Tool - Versione Sicura e Migliorata
Author: root-shost
Version: 2.0
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import requests
import subprocess
import time
import threading
import sys
import os
import logging
import re
from urllib.parse import urlparse
from stem import Signal
from stem.control import Controller

# Configurazione logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('tor_anonymizer.log'),
        logging.StreamHandler()
    ]
)

class TorSecurityManager:
    """Gestione sicura delle operazioni Tor"""
    
    @staticmethod
    def validate_url(url):
        """Validazione sicurezza URL avanzata"""
        if not url or len(url) > 2048:
            raise ValueError("URL troppo lungo o vuoto")
        
        parsed = urlparse(url)
        
        # Whitelist protocolli permessi
        if parsed.scheme not in ['http', 'https']:
            url = 'https://' + url
            parsed = urlparse(url)
        
        # Previeni SSRF attacks
        ssrf_blacklist = ['localhost', '127.0.0.1', '169.254.169.254', '0.0.0.0']
        if any(domain in parsed.netloc for domain in ssrf_blacklist):
            raise ValueError("Domain non permesso per motivi di sicurezza")
        
        # Validazione caratteri base
        if not re.match(r'^[a-zA-Z0-9:/._?&=%-]+$', url):
            raise ValueError("Caratteri non validi nell'URL")
        
        return url
    
    @staticmethod
    def check_tor_installed():
        """Controlla se Tor è installato sul sistema"""
        try:
            result = subprocess.run(
                ["which", "tor"], 
                capture_output=True, 
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, Exception):
            return False

class TorServiceManager:
    """Gestione sicura del servizio Tor"""
    
    def __init__(self):
        self.tor_process = None
        self.is_running = False
    
    def start_tor_safe(self):
        """Avvia Tor in modo sicuro senza privilegi sudo"""
        try:
            # Controlla se Tor è già in esecuzione
            if self.check_tor_connection():
                logging.info("✅ Tor è già in esecuzione")
                self.is_running = True
                return True
            
            logging.info("🔄 Avvio di Tor in modalità sicura...")
            
            # Crea directory dati se non esiste
            if not os.path.exists("tor_data"):
                os.makedirs("tor_data", mode=0o700)
            
            # Usa la configurazione torrc.example se presente
            torrc_file = "torrc.example" if os.path.exists("torrc.example") else None
            
            tor_cmd = ["tor"]
            if torrc_file:
                tor_cmd.extend(["-f", torrc_file])
            else:
                tor_cmd.extend([
                    "--SocksPort", "9050",
                    "--ControlPort", "9051", 
                    "--DataDirectory", "tor_data",
                    "--CookieAuthentication", "1"
                ])
            
            self.tor_process = subprocess.Popen(
                tor_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Attesa con verifica attiva
            if self.wait_for_tor_start():
                logging.info("✅ Tor avviato correttamente")
                self.is_running = True
                return True
            else:
                logging.error("❌ Timeout avvio Tor")
                return False
                
        except Exception as e:
            logging.error(f"❌ Errore avvio Tor: {e}")
            return False
    
    def check_tor_connection(self, timeout=5):
        """Verifica connessione Tor funzionante"""
        try:
            response = requests.get(
                'http://check.torproject.org',
                proxies={'http': 'socks5://127.0.0.1:9050'},
                timeout=timeout
            )
            return "Congratulations" in response.text
        except:
            return False
    
    def wait_for_tor_start(self, max_wait=30):
        """Attende avvio Tor con verifica attiva"""
        for attempt in range(max_wait):
            if self.check_tor_connection(timeout=2):
                return True
            
            # Controlla se il processo è ancora attivo
            if self.tor_process and self.tor_process.poll() is not None:
                logging.error("❌ Processo Tor terminato prematuramente")
                return False
            
            time.sleep(1)
        
        return False
    
    def renew_identity(self):
        """Rinnova identità Tor in modo sicuro"""
        try:
            with Controller.from_port(port=9051) as controller:
                controller.authenticate()
                controller.signal(Signal.NEWNYM)
                
                # Attendi ricostruzione circuito
                time.sleep(3)
                
                # Verifica nuovo IP
                return self.verify_tor_ip()
                
        except Exception as e:
            logging.error(f"❌ Errore rinnovo identità: {e}")
            return False
    
    def verify_tor_ip(self):
        """Verifica e mostra l'IP corrente attraverso Tor"""
        try:
            response = requests.get(
                'http://check.torproject.org',
                proxies={'http': 'socks5://127.0.0.1:9050'},
                timeout=10
            )
            
            if "Congratulations" in response.text:
                # Estrai IP dalla risposta
                ip_match = re.search(r'(\d+\.\d+\.\d+\.\d+)', response.text)
                ip = ip_match.group(1) if ip_match else "Sconosciuto"
                
                logging.info(f"🌐 IP Tor corrente: {ip}")
                return ip
            else:
                logging.warning("⚠️ Connessione non anonima")
                return None
                
        except Exception as e:
            logging.error(f"❌ Errore verifica IP: {e}")
            return None
    
    def stop_tor(self):
        """Ferma il processo Tor in modo sicuro"""
        if self.tor_process:
            try:
                self.tor_process.terminate()
                self.tor_process.wait(timeout=10)
                logging.info("✅ Tor fermato correttamente")
            except subprocess.TimeoutExpired:
                self.tor_process.kill()
                logging.warning("⚠️ Tor terminato forzatamente")
            self.is_running = False

class TorAnonymizerGUI:
    """Interfaccia grafica migliorata"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Tor Anonymizer Tool v2.0 - Sicuro")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        
        # Manager Tor
        self.tor_manager = TorServiceManager()
        self.security = TorSecurityManager()
        
        # Variabili UI
        self.status_var = tk.StringVar(value="Stato: Inizializzazione...")
        self.ip_var = tk.StringVar(value="IP: Non verificato")
        
        self.setup_ui()
        self.initialize_tor()
    
    def initialize_tor(self):
        """Inizializzazione asincrona di Tor"""
        def init_task():
            # Controlla installazione Tor
            if not self.security.check_tor_installed():
                self.show_error(
                    "Tor non installato",
                    "Installa Tor prima di procedere:\n\n"
                    "Ubuntu/Debian: sudo apt install tor\n"
                    "Windows: Scarica da torproject.org\n"
                    "macOS: brew install tor"
                )
                return
            
            # Avvia Tor
            if self.tor_manager.start_tor_safe():
                ip = self.tor_manager.verify_tor_ip()
                if ip:
                    self.update_status(f"✅ Tor attivo - IP: {ip}", "green")
                else:
                    self.update_status("⚠️ Tor attivo - Verifica IP fallita", "orange")
            else:
                self.show_error("Errore", "Impossibile avviare Tor")
        
        threading.Thread(target=init_task, daemon=True).start()
    
    def setup_ui(self):
        """Configurazione interfaccia utente"""
        # Style configuration
        style = ttk.Style()
        style.configure("Green.TLabel", foreground="green")
        style.configure("Red.TLabel", foreground="red")
        style.configure("Orange.TLabel", foreground="orange")
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # Status bar
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(status_frame, textvariable=self.status_var, 
                 style="Green.TLabel").pack(side=tk.LEFT)
        ttk.Label(status_frame, textvariable=self.ip_var, 
                 style="Orange.TLabel").pack(side=tk.RIGHT)
        
        # URL input section
        url_frame = ttk.LabelFrame(main_frame, text="Navigazione Anonima", padding="10")
        url_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        url_frame.columnconfigure(1, weight=1)
        
        ttk.Label(url_frame, text="URL:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.url_entry = ttk.Entry(url_frame, width=60, font=('Arial', 10))
        self.url_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        self.url_entry.bind('<Return>', lambda e: self.browse_anonymously())
        
        self.browse_btn = ttk.Button(url_frame, text="Browse Anonymously", 
                                   command=self.browse_anonymously)
        self.browse_btn.grid(row=0, column=2, pady=5, padx=5)
        
        # Control buttons
        control_frame = ttk.LabelFrame(main_frame, text="Controlli Tor", padding="10")
        control_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        self.new_identity_btn = ttk.Button(control_frame, text="🔄 New Identity", 
                                         command=self.renew_identity_thread,
                                         width=15)
        self.new_identity_btn.pack(side=tk.LEFT, padx=5)
        
        self.check_ip_btn = ttk.Button(control_frame, text="🌐 Check Current IP", 
                                     command=self.check_ip_thread,
                                     width=15)
        self.check_ip_btn.pack(side=tk.LEFT, padx=5)
        
        # Output area
        output_frame = ttk.LabelFrame(main_frame, text="Risultati", padding="10")
        output_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)
        
        self.output_area = scrolledtext.ScrolledText(output_frame, width=85, height=20,
                                                   font=('Consolas', 9))
        self.output_area.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
    
    def update_status(self, message, color="black"):
        """Aggiorna lo status della UI"""
        self.status_var.set(f"Stato: {message}")
        self.root.update_idletasks()
    
    def log_output(self, message, tag=None):
        """Aggiunge messaggio all'output area"""
        self.output_area.insert(tk.END, f"{message}\n", tag)
        self.output_area.see(tk.END)
        self.root.update_idletasks()
    
    def show_error(self, title, message):
        """Mostra messaggio di errore"""
        messagebox.showerror(title, message)
        self.log_output(f"❌ ERRORE: {title} - {message}", "error")
    
    def show_info(self, title, message):
        """Mostra messaggio informativo"""
        messagebox.showinfo(title, message)
        self.log_output(f"ℹ️ INFO: {title} - {message}", "info")
    
    def browse_anonymously(self):
        """Navigazione anonima con validazione sicurezza"""
        url = self.url_entry.get().strip()
        
        if not url:
            self.show_error("Input vuoto", "Inserisci un URL valido")
            return
        
        def browse_task():
            try:
                self.progress.start()
                self.browse_btn.config(state='disabled')
                
                # Validazione sicurezza URL
                safe_url = self.security.validate_url(url)
                self.log_output(f"🔍 Accesso a: {safe_url}")
                
                # Richiesta attraverso Tor
                response = requests.get(
                    safe_url,
                    proxies={
                        'http': 'socks5://127.0.0.1:9050',
                        'https': 'socks5://127.0.0.1:9050'
                    },
                    timeout=30,
                    headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0'
                    }
                )
                
                # Analizza response
                content_type = response.headers.get('content-type', '').lower()
                
                if 'text/html' in content_type:
                    # Estrai titolo dalla pagina HTML
                    title_match = re.search(r'<title>(.*?)</title>', response.text, re.IGNORECASE)
                    title = title_match.group(1) if title_match else "Nessun titolo"
                    
                    self.log_output(f"✅ Pagina caricata: {title}")
                    self.log_output(f"📊 Dimensione: {len(response.text)} caratteri")
                    self.log_output(f"🔢 Status Code: {response.status_code}")
                    
                    # Mostra anteprima contenuto
                    preview = response.text[:500] + "..." if len(response.text) > 500 else response.text
                    self.log_output(f"📄 Anteprima:\n{preview}\n")
                    
                else:
                    self.log_output(f"✅ File scaricato: {content_type}")
                    self.log_output(f"📊 Dimensione: {len(response.content)} bytes")
                
                self.update_status("Navigazione completata", "green")
                
            except ValueError as e:
                self.show_error("URL non valido", str(e))
            except requests.exceptions.Timeout:
                self.show_error("Timeout", "La richiesta ha impiegato troppo tempo")
            except requests.exceptions.RequestException as e:
                self.show_error("Errore di rete", str(e))
            except Exception as e:
                self.show_error("Errore imprevisto", str(e))
            finally:
                self.progress.stop()
                self.browse_btn.config(state='normal')
        
        threading.Thread(target=browse_task, daemon=True).start()
    
    def renew_identity_thread(self):
        """Rinnova identità in thread separato"""
        def renew_task():
            self.progress.start()
            self.new_identity_btn.config(state='disabled')
            
            self.log_output("🔄 Rinnovo identità Tor in corso...")
            
            if self.tor_manager.renew_identity():
                ip = self.tor_manager.verify_tor_ip()
                if ip:
                    self.log_output(f"✅ Nuova identità - IP: {ip}")
                    self.update_status(f"Identità rinnovata - IP: {ip}", "green")
                else:
                    self.log_output("⚠️ Identità rinnovata ma verifica IP fallita")
                    self.update_status("Identità rinnovata", "orange")
            else:
                self.show_error("Errore", "Impossibile rinnovare l'identità")
            
            self.progress.stop()
            self.new_identity_btn.config(state='normal')
        
        threading.Thread(target=renew_task, daemon=True).start()
    
    def check_ip_thread(self):
        """Verifica IP corrente in thread separato"""
        def check_task():
            self.progress.start()
            self.check_ip_btn.config(state='disabled')
            
            self.log_output("🌐 Verifica IP corrente attraverso Tor...")
            
            ip = self.tor_manager.verify_tor_ip()
            if ip:
                self.log_output(f"✅ IP attuale: {ip}")
                self.update_status(f"IP verificato: {ip}", "green")
            else:
                self.log_output("❌ Impossibile verificare l'IP")
                self.update_status("Verifica IP fallita", "red")
            
            self.progress.stop()
            self.check_ip_btn.config(state='normal')
        
        threading.Thread(target=check_task, daemon=True).start()
    
    def on_closing(self):
        """Pulizia alla chiusura dell'applicazione"""
        self.tor_manager.stop_tor()
        self.root.destroy()

def main():
    """Funzione principale"""
    # Verifica dipendenze
    try:
        import requests
        import stem
    except ImportError as e:
        print(f"❌ Dipendenze mancanti: {e}")
        print("📦 Installa con: pip install -r requirements.txt")
        sys.exit(1)
    
    # Avvia applicazione
    root = tk.Tk()
    app = TorAnonymizerGUI(root)
    
    # Gestione chiusura finestra
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        app.on_closing()

if __name__ == "__main__":
    main()
