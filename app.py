import streamlit as st

# --- 1. DEFINIZIONE DATI MANTRA 2025/2026 (DA IMMAGINE) ---

# Mappatura esatta basata sull'immagine fornita.
# Ogni sottolista rappresenta uno slot in campo e i ruoli accettati.
# L'ordine nella lista non conta per la verifica, conta che ci siano gli slot giusti.

SCHEMI_MANTRA = {
    "3-4-3": [
        ["Por"], 
        ["Dc"], ["Dc"], ["Dc", "B"],          # DIFESA: 2 Dc puri, 1 Dc o B (Max 1 Braccetto)
        ["E"], ["M", "C"], ["C"], ["E"],      # CENTROCAMPO
        ["W", "A"], ["Pc", "A"], ["W", "A"]   # ATTACCO (Punta centrale A o Pc)
    ],
    "3-4-1-2": [
        ["Por"],
        ["Dc"], ["Dc"], ["Dc", "B"],
        ["E"], ["M", "C"], ["C"], ["E"],
        ["T"],
        ["Pc", "A"], ["Pc", "A"]
    ],
    "3-4-2-1": [
        ["Por"],
        ["Dc"], ["Dc"], ["Dc", "B"],
        ["E", "W"], ["M"], ["M", "C"], ["E"], # Nota: Un esterno è E/W, l'altro E
        ["T"], ["T", "A"],
        ["Pc", "A"]
    ],
    "3-5-2": [
        ["Por"],
        ["Dc"], ["Dc"], ["Dc", "B"],
        ["E", "W"], ["M", "C"], ["M"], ["C"], ["E"], # 5 a centrocampo specifici
        ["Pc", "A"], ["Pc", "A"]
    ],
    "3-5-1-1": [
        ["Por"],
        ["Dc"], ["Dc"], ["Dc", "B"],
        ["E", "W"], ["M"], ["C"], ["M"], ["E", "W"],
        ["T", "A"],
        ["Pc", "A"]
    ],
    "4-3-3": [
        ["Por"],
        ["Dd"], ["Dc"], ["Dc"], ["Ds"],
        ["M", "C"], ["M"], ["C"],
        ["W", "A"], ["Pc", "A"], ["W", "A"]
    ],
    "4-3-1-2": [
        ["Por"],
        ["Dd"], ["Dc"], ["Dc"], ["Ds"],
        ["M", "C"], ["M"], ["C"],
        ["T"],
        ["T", "A", "Pc"], ["Pc", "A"]        # Nota: Una punta può essere anche T
    ],
    "4-4-2": [
        ["Por"],
        ["Dd"], ["Dc"], ["Dc"], ["Ds"],
        ["E", "W"], ["M", "C"], ["C"], ["E"],
        ["Pc", "A"], ["Pc", "A"]
    ],
    "4-1-4-1": [
         ["Por"],
         ["Dd"], ["Dc"], ["Dc"], ["Ds"],
         ["M"],                               
         ["E", "W"], ["C", "T"], ["T"], ["W"], # Linea trequarti specifica da immagine
         ["Pc", "A"]
    ],
    "4-4-1-1": [
        ["Por"],
        ["Dd"], ["Dc"], ["Dc"], ["Ds"],
        ["E", "W"], ["M"], ["C"], ["E", "W"],
        ["T", "A"],
        ["Pc", "A"]
    ],
    "4-2-3-1": [
        ["Por"],
        ["Dd"], ["Dc"], ["Dc"], ["Ds"],
        ["M"], ["M", "C"],
        ["W", "T"], ["T"], ["W", "A"],
        ["Pc", "A"]
    ]
}

# --- 2. FUNZIONI LOGICHE (BACKTRACKING) ---

def verifica_formazione(giocatori_selezionati, schema_nome, slot_schema):
    """
    Algoritmo ricorsivo per verificare se i giocatori entrano negli slot.
    """
    # Caso base: se non ci sono più giocatori da piazzare, abbiamo successo!
    if not giocatori_selezionati:
        return True

    # Strategia di ottimizzazione: 
    # Proviamo a piazzare prima i giocatori con MENO ruoli (più difficili da collocare).
    # Esempio: Se ho un "B" puro e un "Dc/B", meglio piazzare prima il "B" puro.
    giocatori_ordinati = sorted(giocatori_selezionati, key=lambda x: len(x['ruoli']))
    
    giocatore_corrente = giocatori_ordinati[0]
    ruoli_giocatore = set(giocatore_corrente['ruoli'])
    
    # Resto dei giocatori da piazzare
    altri_giocatori = giocatori_ordinati[1:]

    # Iteriamo su tutti gli slot disponibili nello schema
    for i, slot in enumerate(slot_schema):
        # 'slot' è una lista di ruoli accettati per quella posizione (es. ["Dc", "B"])
        # Verifichiamo se il giocatore ha almeno un ruolo valido per questo slot
        if any(r in slot for r in ruoli_giocatore):
            
            # Creiamo una nuova lista di slot rimuovendo quello appena occupato
            nuovi_slot = slot_schema[:i] + slot_schema[i+1:]
            
            # Chiamata ricorsiva: proviamo a piazzare gli altri giocatori negli slot rimasti
            if verifica_formazione(altri_giocatori, schema_nome, nuovi_slot):
                return True

    return False

# --- 3. INTERFACCIA STREAMLIT ---

st.set_page_config(page_title="Mantra Helper 25/26", layout="centered")

st.title("⚽ Mantra Helper 2025/26")
st.markdown("Verifica formazioni con regole ufficiali (es. **Max 1 B** nelle difese a 3).")

# --- GESTIONE ROSA ---
if 'rosa' not in st.session_state:
    st.session_state.rosa = []

with st.expander("📝 Gestione Rosa", expanded=True):
    col1, col2 = st.columns([2, 3])
    with col1:
        nuovo_nome = st.text_input("Nome", key="input_nome")
    with col2:
        # Lista ruoli completa
        ruoli_possibili = ["Por", "Dd", "Ds", "Dc", "B", "E", "M", "C", "T", "W", "A", "Pc"]
        nuovi_ruoli = st.multiselect("Ruoli", ruoli_possibili, key="input_ruoli")
    
    if st.button("Aggiungi"):
        if nuovo_nome and nuovi_ruoli:
            if any(p['nome'].lower() == nuovo_nome.lower() for p in st.session_state.rosa):
                st.warning("Giocatore già esistente.")
            else:
                st.session_state.rosa.append({"nome": nuovo_nome, "ruoli": nuovi_ruoli})
                st.success(f"Aggiunto: {nuovo_nome}")
        else:
            st.error("Inserisci Nome e Ruoli.")

    # Tabella riassuntiva
    if st.session_state.rosa:
        st.caption(f"Hai {len(st.session_state.rosa)} giocatori in rosa.")
        # Visualizzazione compatta
        text_rosa = ""
        for p in st.session_state.rosa:
            text_rosa += f"**{p['nome']}** ({','.join(p['ruoli'])})  •  "
        st.markdown(text_rosa)

# --- SCHIERAMENTO ---
st.divider()
st.subheader("Chi vuoi schierare?")

if not st.session_state.rosa:
    st.info("Inserisci i giocatori sopra per iniziare.")
else:
    nomi_rosa = [p['nome'] for p in st.session_state.rosa]
    nomi_rosa.sort()
    
    scelte_utente = st.multiselect(
        "Seleziona i titolari fissi (Max 11):", 
        nomi_rosa
    )

    if st.button("🔍 Verifica Moduli Disponibili", type="primary"):
        if not scelte_utente:
            st.warning("Seleziona almeno un giocatore.")
        elif len(scelte_utente) > 11:
            st.error("Non puoi selezionare più di 11 giocatori.")
        else:
            giocatori_target = [p for p in st.session_state.rosa if p['nome'] in scelte_utente]
            
            formazioni_valide = []
            
            # Barra di caricamento (scenografica, il calcolo è veloce)
            bar = st.progress(0)
            tot_schemi = len(SCHEMI_MANTRA)
            
            for idx, (nome_schema, slot_disponibili) in enumerate(SCHEMI_MANTRA.items()):
                # Passiamo una copia degli slot per non modificarli
                if verifica_formazione(giocatori_target, nome_schema, slot_disponibili.copy()):
                    formazioni_valide.append(nome_schema)
                bar.progress((idx + 1) / tot_schemi)
            
            bar.empty() # Rimuove la barra alla fine
            
            st.divider()
            
            if formazioni_valide:
                st.success(f"✅ PUOI SCHIERARLI! Trovati {len(formazioni_valide)} moduli compatibili.")
                
                cols = st.columns(3)
                for i, mod in enumerate(formazioni_valide):
                    with cols[i % 3]:
                        st.markdown(f"### 🛡️ {mod}")
            else:
                st.error("❌ NESSUN MODULO COMPATIBILE.")
                
                # --- LOGICA ERRORE PARLANTE ---
                st.markdown("#### Perché?")
                
                # Controllo specifico Braccetti
                cnt_B_only = sum(1 for p in giocatori_target if 'B' in p['ruoli'] and 'Dc' not in p['ruoli'])
                cnt_Dc_B = sum(1 for p in giocatori_target if 'B' in p['ruoli'] or 'Dc' in p['ruoli'])
                
                if cnt_B_only > 1:
                    st.write(f"⚠️ **Problema Braccetti:** Hai selezionato {cnt_B_only} giocatori che sono solo 'B' (o che stai usando come B). Nelle difese a 3 è ammesso **solo 1 Braccetto** (gli altri devono essere Dc).")
                
                elif len(scelte_utente) >= 3 and cnt_Dc_B == 0:
                     st.write("⚠️ **Mancano Difensori:** Non hai selezionato abbastanza Dc o B per fare una difesa.")
                
                else:
                    st.write("⚠️ Conflitto generico: Probabilmente hai troppi giocatori per lo stesso ruolo (es. troppe Punte Pc o troppi Esterni che non possono fare altro).")
