import streamlit as st
import pandas as pd

# --- 1. DATI MANTRA 2025/2026 ---
SCHEMI_MANTRA = {
    "3-4-3": [["Por"], ["Dc"], ["Dc"], ["Dc", "B"], ["E"], ["M", "C"], ["C"], ["E"], ["W", "A"], ["Pc", "A"], ["W", "A"]],
    "3-4-1-2": [["Por"], ["Dc"], ["Dc"], ["Dc", "B"], ["E"], ["M", "C"], ["C"], ["E"], ["T"], ["Pc", "A"], ["Pc", "A"]],
    "3-4-2-1": [["Por"], ["Dc"], ["Dc"], ["Dc", "B"], ["E", "W"], ["M"], ["M", "C"], ["E"], ["T"], ["T", "A"], ["Pc", "A"]],
    "3-5-2": [["Por"], ["Dc"], ["Dc"], ["Dc", "B"], ["E", "W"], ["M", "C"], ["M"], ["C"], ["E"], ["Pc", "A"], ["Pc", "A"]],
    "3-5-1-1": [["Por"], ["Dc"], ["Dc"], ["Dc", "B"], ["E", "W"], ["M"], ["C"], ["M"], ["E", "W"], ["T", "A"], ["Pc", "A"]],
    "4-3-3": [["Por"], ["Dd"], ["Dc"], ["Dc"], ["Ds"], ["M", "C"], ["M"], ["C"], ["W", "A"], ["Pc", "A"], ["W", "A"]],
    "4-3-1-2": [["Por"], ["Dd"], ["Dc"], ["Dc"], ["Ds"], ["M", "C"], ["M"], ["C"], ["T"], ["T", "A", "Pc"], ["Pc", "A"]],
    "4-4-2": [["Por"], ["Dd"], ["Dc"], ["Dc"], ["Ds"], ["E", "W"], ["M", "C"], ["C"], ["E"], ["Pc", "A"], ["Pc", "A"]],
    "4-1-4-1": [["Por"], ["Dd"], ["Dc"], ["Dc"], ["Ds"], ["M"], ["E", "W"], ["C", "T"], ["T"], ["W"], ["Pc", "A"]],
    "4-4-1-1": [["Por"], ["Dd"], ["Dc"], ["Dc"], ["Ds"], ["E", "W"], ["M"], ["C"], ["E", "W"], ["T", "A"], ["Pc", "A"]],
    "4-2-3-1": [["Por"], ["Dd"], ["Dc"], ["Dc"], ["Ds"], ["M"], ["M", "C"], ["W", "T"], ["T"], ["W", "A"], ["Pc", "A"]]
}

# --- 2. LOGICA DIAGNOSTICA AVANZATA ---
def verifica_formazione(giocatori_selezionati, schema_nome, slot_schema):
    if not giocatori_selezionati: return True
    giocatori_ordinati = sorted(giocatori_selezionati, key=lambda x: len(x['ruoli']))
    giocatore_corrente = giocatori_ordinati[0]
    ruoli_giocatore = set(giocatore_corrente['ruoli'])
    altri_giocatori = giocatori_ordinati[1:]
    
    for i, slot in enumerate(slot_schema):
        if any(r in slot for r in ruoli_giocatore):
            if verifica_formazione(altri_giocatori, schema_nome, slot_schema[:i] + slot_schema[i+1:]):
                return True
    return False

def analizza_problemi(giocatori):
    problemi = []
    tot = len(giocatori)
    
    # 1. Check Portieri (Severo)
    count_por = sum(1 for p in giocatori if 'Por' in p['ruoli'])
    if count_por > 1: problemi.append(f"⛔ **Troppi Portieri**: {count_por} selezionati. Ne serve 1.")
    elif tot >= 11 and count_por == 0: problemi.append("⛔ **Manca il Portiere**: Hai 11 giocatori ma nessun Por.")

    # 2. Check Punte Pc (Severo)
    # Contiamo chi è SOLO Pc (molto vincolante)
    solo_pc = sum(1 for p in giocatori if p['ruoli'] == ['Pc'])
    # Contiamo chi HA il ruolo Pc (anche se ne ha altri)
    tutti_pc = sum(1 for p in giocatori if 'Pc' in p['ruoli'])
    
    if solo_pc > 2: problemi.append(f"⛔ **Troppi Pc puri**: Hai {solo_pc} giocatori che sono solo Pc. Massimo 2.")
    if tutti_pc > 3: problemi.append(f"⚠️ **Affollamento Attacco**: Hai {tutti_pc} punte (Pc). È difficile farle coesistere tutte.")

    # 3. Check Braccetti / Difesa
    solo_b = sum(1 for p in giocatori if 'B' in p['ruoli'] and 'Dc' not in p['ruoli'])
    if solo_b > 1: problemi.append(f"⛔ **Troppi 'B' puri**: {solo_b} selezionati. Nelle difese a 3 ne puoi schierare max 1.")
    
    difensori_totali = sum(1 for p in giocatori if any(r in ['Dd','Ds','Dc','B'] for r in p['ruoli']))
    if tot > 5 and difensori_totali == 0:
        problemi.append("⚠️ **Mancano Difensori**: Hai selezionato molti giocatori ma 0 difensori.")

    # 4. Check Esterni/Ali (W/A/E)
    esterni = sum(1 for p in giocatori if any(r in ['W','A','E'] for r in p['ruoli']))
    if esterni > 4:
        problemi.append("⚠️ **Troppi Esterni/Ali**: Molti moduli supportano max 2 o 4 esterni. Tu ne hai scelti tanti.")

    # 5. ERRORE GENERICO (Ora scatta SEMPRE se non ci sono altri errori specifici)
    if not problemi:
        problemi.append("❓ **Conflitto di Ruoli**: I giocatori selezionati non si incastrano insieme. Probabilmente hai troppi giocatori per lo stesso ruolo specifico (es. 2 Pc + troppe Ali) che si contendono gli stessi posti.")

    return problemi

# --- 3. INTERFACCIA ---
st.set_page_config(page_title="Mantra Helper", layout="centered")
st.title("⚽ Mantra Helper")

# Inizializza stato
if 'rosa' not in st.session_state: st.session_state.rosa = []

# BOX CARICAMENTO
with st.expander("📂 Gestione File Excel", expanded=not bool(st.session_state.rosa)):
    uploaded_file = st.file_uploader("Carica file Excel", type=["xlsx", "xls"])
    if uploaded_file:
        try:
            df = pd.read_excel(uploaded_file)
            df.columns = [str(c).strip().capitalize() for c in df.columns]
            if "Ruolo" in df.columns and "Calciatore" in df.columns:
                nuova_rosa = []
                for _, row in df.iterrows():
                    nome = str(row['Calciatore']).strip()
                    ruoli_raw = str(row['Ruolo'])
                    for sep in [';', ',', '/']: ruoli_raw = ruoli_raw.replace(sep, ',')
                    ruoli = [r.strip() for r in ruoli_raw.split(',')]
                    nuova_rosa.append({"nome": nome, "ruoli": ruoli})
                
                st.session_state.rosa = nuova_rosa
                st.success(f"✅ Caricati {len(nuova_rosa)} giocatori!")
            else:
                st.error("Colonne richieste: Ruolo, Calciatore")
        except Exception as e:
            st.error(f"Errore: {e}")
            
    if st.session_state.rosa:
        if st.button("🗑️ Cancella Rosa attuale"):
            st.session_state.rosa = []
            st.rerun()

# SEZIONE OPERATIVA
if st.session_state.rosa:
    st.divider()
    st.subheader("Schiera la formazione")
    
    nomi = sorted([p['nome'] for p in st.session_state.rosa])
    scelte = st.multiselect("Seleziona i giocatori (Max 11):", nomi)

    if st.button("🚀 Verifica Moduli", type="primary"):
        if not scelte: st.warning("Seleziona almeno un giocatore")
        elif len(scelte) > 11: st.error("Massimo 11 giocatori!")
        else:
            target = [p for p in st.session_state.rosa if p['nome'] in scelte]
            validi = []
            
            prog = st.progress(0)
            tot = len(SCHEMI_MANTRA)
            for i, (n, s) in enumerate(SCHEMI_MANTRA.items()):
                if verifica_formazione(target, n, s.copy()): validi.append(n)
                prog.progress((i+1)/tot)
            prog.empty()
            
            if validi:
                st.success(f"Trovati {len(validi)} moduli compatibili:")
                cols = st.columns(3)
                for i, m in enumerate(validi):
                    with cols[i%3]: st.markdown(f"### 🛡️ {m}")
            else:
                st.error("❌ Nessuna formazione valida.")
                # Mostra sempre l'analisi, anche se parziale
                st.markdown("#### 🕵️ Analisi:")
                for msg in analizza_problemi(target): st.write(msg)

elif not uploaded_file:
    st.info("👆 Carica il file Excel sopra per iniziare.")
