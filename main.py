#per compilare
#pyinstaller --onefile --noconsole main.py
import tkinter as tk
from tkinter import ttk  # Importa ttk per utilizzare Combobox
from tkinter import messagebox  # Importa messagebox per la finestra di conferma
import os
import webbrowser
import subprocess
import time
import datetime

values=[]

# Funzione per filtrare i valori nella combobox in base al testo inserito
def filter_combobox(event):
    global values # Dichiarazione di utilizzo della variabile globale
    # Ottieni il testo corrente inserito nella Combobox
    typed_text = event.widget.get()
    print("Valori stampati dal filtro:", values)  # Stampa i valori caricati

    # Filtra i valori che iniziano con il testo digitato
    filtered_values = [value for value in values if value.lower().startswith(typed_text.lower())]

    # Aggiorna i valori della Combobox con i valori filtrati
    event.widget['values'] = filtered_values

    # Mostra la lista aggiornata dei valori
    event.widget.event_generate('<Down>')

# Funzione per creare righe dinamiche e memorizzare gli Entry in una lista
def create_dynamic_rows(frame, num_rows):

    global values # Dichiarazione di utilizzo della variabile globale
    combos = []  # Lista per memorizzare le combobox

    for i in range(num_rows):
        # Creazione della label
        label = tk.Label(frame, text=f"Choreo {i + 1}", bg=colore_sfondo_label, fg=colore_testo_label, font=font)
        label.grid(row=i, column=0, padx=5, pady=2)

        # Creazione di uno stile personalizzato
        style = ttk.Style()

        # Configurazione del colore di sfondo e del testo per il combobox
        style.configure("TCombobox", fieldbackground=colore_sfondo_entry, background=colore_sfondo_entry, foreground=colore_testo_entry)

        # Crea una Combobox
        combobox = ttk.Combobox(frame,font=font, width=25, style="TCombobox")
        # Imposta i valori nella Combobox
        combobox['values'] = values

        # Imposta una scritta predefinita
        combobox.set("Choose a choreo")

        combobox.grid(row=i, column=1, padx=5, pady=2)

        if (i==0):
            button_show = tk.Button(frame_left, text="Up", bg=colore_sfondo_button, fg=colore_testo_button, font=font, command=move_up)
            button_show.grid(row=i, column=2, pady=2)

            # Bind degli eventi per il cambiamento di colore
            button_show.bind("<Enter>", on_enter)  # Quando il mouse entra nel pulsante
            button_show.bind("<Leave>", on_leave)  # Quando il mouse esce dal pulsante

        # Aggiungi il binding per filtrare i valori mentre si digita
        combobox.bind('<KeyRelease>', filter_combobox)

        # Aggiungi la combobox alla lista
        combos.append(combobox)

    return combos

#carica le choreo dal file choreolist.dt
def load_values_from_file():
    global values # Dichiarazione di utilizzo della variabile globale
    try:
        with open("choreolist.dat", "r") as file:
            # Leggi ogni linea e rimuovi spazi bianchi come newline
            values = [line.strip() for line in file.readlines()]
            values.sort()  # Ordina i valori in ordine alfabetico
        return values
    except FileNotFoundError:
        print(f"File choreolist.dat' non trovato.")
        return []

# Funzione per aggiornare tutte le combobox
def update_combobox():
    global values # Dichiarazione di utilizzo della variabile globale
    values = load_values_from_file()
    values.sort()  # Ordina i valori in ordine alfabetico
    print("Valori stampati da funz aggiornamento:", values)
    print("modifica")
    for combobox in combos:
        combobox['values'] = values
        # Aggiungi il binding per filtrare i valori mentre si digita
        combobox.bind('<KeyRelease>', filter_combobox)
#rimuove la choreo se richiesto e memorizza l'ora in cui è stata suonata nel file del blocco
def remove_values(text):
    global values # Dichiarazione di utilizzo della variabile globale
    if text in values:
        values.remove(text)
    for combobox in combos:
        combobox['values'] = values
    # Ottenere la data e l'ora attuali
    now = datetime.datetime.now()

    # Formattare la data e l'ora come stringa
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")  # Esempio: '2024-09-05 15:30:45'

    with open("playlistblock.dat", "a") as file:
        file.write(text + "\n" + timestamp + "\n")


def add_values(valori_da_aggiungere):
    for combobox in combos:
        # Ottieni i valori attuali della combobox come una lista
        valori_attuali = list(combobox['values'])

        # Combina i valori attuali con i nuovi, evitando duplicati
        nuovi_valori = valori_attuali + [valore for valore in valori_da_aggiungere if valore not in valori_attuali]

        # Se necessario, converti tuple in stringhe
        nuovi_valori = [str(valore) if isinstance(valore, tuple) else valore for valore in nuovi_valori]

        # Ordina i valori come stringhe per evitare errori
        nuovi_valori_ordinati = sorted(nuovi_valori, key=lambda x: str(x))

        # Imposta i nuovi valori ordinati nella combobox
        combobox['values'] = nuovi_valori_ordinati

#inserisce il nome della nuova choreo nel file Choreolist.dat
def append_to_file():
    text = nome_choreo.get().strip()  # Prendi il testo dall'Entry e rimuovi eventuali spazi iniziali e finali
    if text:  # Se il testo non è vuoto
        text=text.upper()
        with open("choreolist.dat", "a") as file:  # Apri il file in modalità append, crea il file se non esiste
            file.write(text + "\n")  # Scrivi il testo con un ritorno a capo
        nome_choreo.delete(0, tk.END)  # Pulisci il campo Entry dopo aver inserito il testo
        update_combobox()  # Aggiorna i valori della Combobox
    else:
        # Se il testo è vuoto
        nome_choreo.insert(0, "Insert choreo")  # Inserisce il testo all'inizio

# Funzione per filtrare le righe in base all'ora e restituirle in una lista
def filtra_righe_per_ora():
    righe_valide = []
    righe_da_tenere= []

    #ore da aggiungere
    ore_da_aggiungere= int(blocco.get())

    with open("playlistblock.dat", 'r') as file:
        righe = file.readlines()

    # Ottieni il tempo attuale e somma le ore fornite
    ora_corrente = datetime.datetime.now()

    #stampa orari
    print("Ore da aggiungere "+ str(ore_da_aggiungere))
    print(f"Ora corrente {ora_corrente.strftime('%H:%M:%S')}")

    print("inizio controllo")
    for i in range(1, len(righe), 2):  # Legge solo le righe con i timestamp
        # Converte la stringa del timestamp in un oggetto datetime
        ora_riga = datetime.datetime.strptime(righe[i].strip(), "%Y-%m-%d %H:%M:%S")
        print("Choreo" + righe[i - 1])
        print(f"Ora della riga {ora_riga.strftime('%H:%M:%S')}")
        # Se la riga soddisfa la condizione, la aggiunge alla lista da ricaricare nella combo
        ora_da_controllare = ora_riga + datetime.timedelta(hours=ore_da_aggiungere)
        print(f"Ora da controllare {ora_da_controllare.strftime('%H:%M:%S')}")
        if  ora_corrente > ora_da_controllare:
            print("Choreo da ricaricare nella combobox" + righe[i - 1])
            righe_valide.append((righe[i - 1].strip()))
        else:
            # Se la riga non soddisfa la condizione, la aggiunge alla lista da ricaricare nel file
            print("Choreo da ricaricare nel file" + righe[i - 1])
            righe_da_tenere.append(righe[i-1]) #mantiene il contenuto
            righe_da_tenere.append(righe[i])  # mantiene il timestamp

    #sovrascrivi il file con le righe che vuoi mantenere
    with open("playlistblock.dat", 'w') as file:
        print(f"Righe da riscrivere nel file: {righe_da_tenere}")
        file.writelines(righe_da_tenere)

    return righe_valide

# Funzione per spostare i valori delle combobox verso l'alto
def move_up():
    if not combos:
        return

    if varCheck.get() == 1:  # Se la checkbox è selezionata
        if not blocco.get().isdigit():  # Controlla che ci sia un numero nell'Entry
            messagebox.showwarning("Error", "You must enter a number in REPEAT AFTER HOURS!")
            #blocco.config(bg="yellow")  # Colora l'Entry in rosso
            return

    # Prendi il contenuto della prima combobox
    first_value = combos[0].get()
    # Pulisci il contenuto della prima combobox
    combos[0].set('')

    # Sposta i contenuti delle combobox
    for i in range(1, len(combos)):
        previous_value = combos[i].get()
        combos[i - 1].set(previous_value)

    # Pulisci l'ultima combobox
    combos[-1].set('Choose a choreo')

    # Scrivi il valore della prima combobox nel file storico
    if first_value:
        # Ottenere la data e l'ora attuali
        now = datetime.datetime.now()

        # Formattare la data e l'ora come stringa
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S")  # Esempio: '2024-09-05 15:30:45'

        with open("playliststore.dat", "a") as file:
            file.write(first_value + "\n" + timestamp + "\n")

    #se richiesta la gestione del blocco per un certo numero di ore
        if varCheck.get() == 1:
            righe_da_tenere= []
            #elimino la choreo dalla lista dei valori
            remove_values(first_value)
            #aggiungo la choreo per cui è passato il tempo di blocco
            righe_da_aggiungere=filtra_righe_per_ora()
            add_values(righe_da_aggiungere)

# Funzione per salvare il contenuto delle combobox in un file HTML
def save_to_html():
    with open("template.html", "r") as template_file:
        html_content = template_file.read()

        # Recupera il testo dall'Entry "nome_evento"
        evento_nome = nome_evento.get().strip()  # Usa .strip() per rimuovere eventuali spazi bianchi

        if evento_nome:  # Verifica che il nome dell'evento non sia vuoto
            # Inserisci il nome dell'evento nell'HTML
            html_content = html_content.replace("<!-- Nome -->", evento_nome)
        else:
            evento_nome="Insert event name"
            html_content = html_content.replace("<!-- Nome -->", evento_nome)
            nome_evento.insert(0, "Insert event name")  # Inserisce il testo all'inizio

    # Costruzione delle righe della tabella
    table_rows = ""
    for i, combobox in enumerate(combos):
        value = combobox.get()
        if value and value != "Choose a choreo":  # Solo se la combobox non è vuota
            if i==0:
                table_rows += f"<tr><td>Play</td><td>{value}</td></tr>\n"
            else:
                table_rows += f"<tr><td> </td><td>{value}</td></tr>\n"

    # Inserisci le righe della tabella nell'HTML
    html_content = html_content.replace(
        '<!-- I dati delle combobox saranno inseriti qui -->', table_rows)

    # Salva il file HTML aggiornato
    with open("playlist.html", "w") as html_file:
        html_file.write(html_content)
    #ATTENZIONE
    #Vai nelle Impostazioni di Chrome.
    # Scorri fino alla sezione All'avvio.
    # Seleziona l'opzione Apri la pagina Nuova scheda o Apri una pagina specifica o un insieme di pagine
    # invece di Riprendi da dove eri rimasto.

    # Carico la pagina html in Chrome
    # Percorso relativo al file
    relative_path = './playlist.html'
    # Ottenere il percorso assoluto
    abs_path = os.path.abspath(relative_path)
    #print("Il percorso assoluto del file è:", abs_path)

    #Chiudi tutte le istanze di Chrome senza mostrare l'elenco dei PID
    subprocess.call(["taskkill", "/F", "/IM", "chrome.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Aspetta qualche secondo per assicurarti che tutte le istanze siano chiuse
    time.sleep(1)

    # Apri una nuova scheda con un file HTML specifico in modalità incognito
    chrome_path = 'C:/Program Files/Google/Chrome/Application/chrome.exe'

    # Avvia Chrome in modalità incognito
    subprocess.Popen([chrome_path, '--incognito', f'file:///{abs_path}'])

def save_to_html_for_load():
    with open("templatericarica.html", "r") as template_file:
        html_content = template_file.read()

        # Recupera il testo dall'Entry "nome_evento"
        evento_nome = nome_evento.get().strip()  # Usa .strip() per rimuovere eventuali spazi bianchi

        if evento_nome:  # Verifica che il nome dell'evento non sia vuoto
            # Inserisci il nome dell'evento nell'HTML
            html_content = html_content.replace("<!-- Nome -->", evento_nome)
        else:
            evento_nome="Insert event name"
            html_content = html_content.replace("<!-- Nome -->", evento_nome)
            nome_evento.insert(0, "Insert event name")  # Inserisce il testo all'inizio

    # Costruzione delle righe della tabella
    table_rows = ""
    for i, combobox in enumerate(combos):
        value = combobox.get()
        if value and value != "Choose a choreo":  # Solo se la combobox non è vuota
            if i==0:
                table_rows += f"<tr><td>Play</td><td>{value}</td></tr>\n"
            else:
                table_rows += f"<tr><td> </td><td>{value}</td></tr>\n"

    # Inserisci le righe della tabella nell'HTML
    html_content = html_content.replace(
        '<!-- I dati delle combobox saranno inseriti qui -->', table_rows)

    # Salva il file HTML aggiornato
    with open("playlist.html", "w") as html_file:
        html_file.write(html_content)

#svuot il file dello storico delle choreo ballate
def clear_file(text):
    # Svuotare il contenuto di un file
    print("Cancellazione del file "+text)
    with open(text, "w") as file:
        pass  # Non scrivendo nulla, il file viene svuotato

    #ricarico tutte le coreo nei values delle combobox
    if text=="playlistblock.dat":
#        print("Riattivo le coreo per file " + text)
        values = load_values_from_file()
        for combobox in combos:
            combobox['values'] = values

# Funzione di validazione: accetta solo numeri
def only_numbers(char):
    return char.isdigit()  # Ritorna True solo se il carattere è un numero

# Funzione di conferma per uscire dall'applicazione
def exit_app():
    if messagebox.askokcancel("Exit", "Are you sure you want to exit?"):
        root.quit()

# Funzione per cambiare il colore del pulsante quando il mouse entra
def on_enter(e):
    e.widget['background'] = colore_sfondo_button_on
    e.widget['foreground'] = colore_testo_button_on

# Funzione per ripristinare il colore del pulsante quando il mouse esce
def on_leave(e):
    e.widget['background'] = colore_sfondo_button
    e.widget['foreground'] = colore_testo_button

# Funzione per aggiungere una riga orizzontale sottile
def add_horizontal_line(frame, row_index):
    canvas = tk.Canvas(frame, height=1, bg=colore_sfondo_line, bd=0, highlightthickness=0)
    canvas.grid(row=row_index, column=0, columnspan=40, pady=5, sticky="ew")
    canvas.create_line(0, 0, 800, 0, fill=colore_sfondo_line)

def avvio_programma():
    with open("templatericarica.html", "r") as template_file:
        html_content = template_file.read()
    # Salva il file HTML vuoto
    with open("playlist.html", "w") as html_file:
        html_file.write(html_content)

def open_email():
    webbrowser.open("buscherinis@gmail.com")

def show_tooltip(event):
    tooltip = tk.Toplevel(root)
    tooltip.wm_overrideredirect(True)
    tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
    label_msg = tk.Label(tooltip, text="Click to send an email", background="yellow", relief="solid", padx=5, pady=5)
    label_msg.pack()

def hide_tooltip(event):
    for widget in root.winfo_children():
        if isinstance(widget, tk.Toplevel):
                widget.destroy()

def center_window(root, width, height):
    #ottieni la dimensione dello schermo
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    #calcola le coordinate per centrare la finestra
    x = (screen_width//2) - (width//2)
    y = (screen_height // 2) - (height // 2)

    #imposta le dimensioni e la posizione della finestra
    root.geometry(f"{width}x{height}+{x}+{y}")

# Inizio programma principale

#Svuota il file html
avvio_programma()

# Impostazioni della fnestra
# Imposta il font
font_titolo = ("Georgia", 18)  # Font Arial, dimensione 16
font = ("Georgia", 16)  # Font Arial, dimensione 16
font_developed = ("Arial", 10)  # Font Arial, dimensione 16
# Numero di righe da generare
num_rows = 6

# Definire il colore comune
colore_sfondo_root = "#AAC2FB"

colore_sfondo_line = "white"

colore_sfondo_titolo = "#5F70E7"
colore_testo_titolo = "white"

colore_sfondo_label = "white"
colore_testo_label = "black"

colore_sfondo_button = "white"
colore_testo_button = "black"

colore_sfondo_button_on = "#FF3E3E"
colore_testo_button_on = "white"

colore_sfondo_entry = "white"
colore_testo_entry = "black"

# Crea la finestra principale
root = tk.Tk()
root.title("Country playlist manager")

# Imposta le dimensioni della finestra
#center_window(root,800,600)
center_window(root,1024,600)
root.configure(bg=colore_sfondo_root)

# Sovrascrivi il comportamento del pulsante di chiusura
root.protocol("WM_DELETE_WINDOW", exit_app)

# Crea la prima label e posizionala al centro in alto
label_top = tk.Label(root, text="Country playlist manager", bg=colore_sfondo_titolo, fg=colore_testo_titolo, font=font_titolo)
label_top.pack(side="top", pady=20, anchor="n")

# Crea un frame per la prima riga, centrata
frame_center = tk.Frame(root, bg=colore_sfondo_root)
frame_center.pack(anchor="n")

# Prima riga: label e campo di input centrato
label_1 = tk.Label(frame_center, text="Event name:", bg=colore_sfondo_label, fg=colore_testo_label, font=font)
label_1.grid(row=0, column=0, padx=5, pady=2)

nome_evento = tk.Entry(frame_center, bg=colore_sfondo_entry, fg=colore_testo_entry, font=font)
nome_evento.grid(row=0, column=1, padx=5, pady=2)

# Crea un secondo frame per le righe indentate a sinistra
frame_left = tk.Frame(root, bg=colore_sfondo_root)
frame_left.pack(pady=10, anchor="w")

values = load_values_from_file()

# Chiama la funzione per creare le righe e ottenere la lista degli Entry
combos = create_dynamic_rows(frame_left, num_rows)

button_show = tk.Button(frame_left, text="Show", bg=colore_sfondo_button, fg=colore_testo_button, font=font, command=save_to_html)
button_show.grid(row=num_rows-1, column=2, pady=2)

# Bind degli eventi per il cambiamento di colore
button_show.bind("<Enter>", on_enter)  # Quando il mouse entra nel pulsante
button_show.bind("<Leave>", on_leave)  # Quando il mouse esce dal pulsante

button_load = tk.Button(frame_left, text="Load", bg=colore_sfondo_button, fg=colore_testo_button, font=font, command=save_to_html_for_load)
button_load.grid(row=num_rows-1, column=3, padx=10, pady=2)

# Bind degli eventi per il cambiamento di colore
button_load.bind("<Enter>", on_enter)  # Quando il mouse entra nel pulsante
button_load.bind("<Leave>", on_leave)  # Quando il mouse esce dal pulsante

# Aggiungi una linea orizzontale sottile dopo il pulsante
add_horizontal_line(frame_left, num_rows)  # Posiziona la linea dopo il pulsante

label_bottom= tk.Label(frame_left, text="New choreo",bg=colore_sfondo_label, fg=colore_testo_label, font=font)
label_bottom.grid(row=num_rows+1, column=0, padx=5, pady=2)

# Creazione del campo di input
nome_choreo = tk.Entry(frame_left, bg=colore_sfondo_entry, fg=colore_testo_entry, font=font)
nome_choreo.grid(row=num_rows+1, column=1, padx=5, pady=2)

button_insert = tk.Button(frame_left, text="Insert",  bg=colore_sfondo_button, fg=colore_testo_button, font=font, command=append_to_file)
button_insert.grid(row=num_rows+1, column=2, pady=2)

# Bind degli eventi per il cambiamento di colore
button_insert.bind("<Enter>", on_enter)  # Quando il mouse entra nel pulsante
button_insert.bind("<Leave>", on_leave)  # Quando il mouse esce dal pulsante

# Aggiungi una linea orizzontale sottile dopo il pulsante
add_horizontal_line(frame_left, num_rows+2)  # Posiziona la linea dopo il pulsante

#gestione del blocco choreo per un certo numero di ore
varCheck = tk.IntVar()
# Creazione della checkbox
checkbox = tk.Checkbutton(frame_left, text="Repeat after hours",bg=colore_sfondo_label, fg=colore_testo_label, font=font, variable=varCheck)
# Posizionamento della checkbox nella griglia
checkbox.grid(row=num_rows+3, column=0, padx=5, pady=2)

# Creazione dell'Entry con validazione
# Registra la funzione di validazione
validation = root.register(only_numbers)

blocco = tk.Entry(frame_left, validate="key", validatecommand=(validation, '%S'), width=2, font=font)  # %S rappresenta il carattere inserito
blocco.grid(row=num_rows+3, column=1, sticky="w", padx=5, pady=2)

button_storico = tk.Button(frame_left, text="Clear store playlist",  bg=colore_sfondo_button, fg=colore_testo_button, font=font, command=lambda:clear_file("playliststore.dat"))
button_storico.grid(row=num_rows+4, column=0, pady=2)

# Bind degli eventi per il cambiamento di colore
button_storico.bind("<Enter>", on_enter)  # Quando il mouse entra nel pulsante
button_storico.bind("<Leave>", on_leave)  # Quando il mouse esce dal pulsante

button_block = tk.Button(frame_left, text="Clear block file",  bg=colore_sfondo_button, fg=colore_testo_button, font=font, command=lambda:clear_file("playlistblock.dat"))
button_block.grid(row=num_rows+4, column=1, pady=2)

# Bind degli eventi per il cambiamento di colore
button_block.bind("<Enter>", on_enter)  # Quando il mouse entra nel pulsante
button_block.bind("<Leave>", on_leave)  # Quando il mouse esce dal pulsante

button_exit = tk.Button(frame_left, text="Exit",  bg=colore_sfondo_button, fg=colore_testo_button, font=font, command=exit_app)

button_exit.grid(row=num_rows+5, column=10, pady=2)
# Bind degli eventi per il cambiamento di colore
button_exit.bind("<Enter>", on_enter)  # Quando il mouse entra nel pulsante
button_exit.bind("<Leave>", on_leave)  # Quando il mouse esce dal pulsante

email_label = tk.Label(frame_left, text="Developed by Stefano Buscherini",bg=colore_sfondo_label, fg=colore_testo_label, font=font_developed)
email_label.bind("<Button-1>", lambda e: open_email())
email_label.grid(row=num_rows+6, column=0, padx=5, pady=2)

email_label.bind("<Enter>", show_tooltip)
email_label.bind("<Leave>", hide_tooltip)

# Avvia il loop principale della finestra
root.mainloop()