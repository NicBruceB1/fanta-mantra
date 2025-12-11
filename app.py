import streamlit as st
import pandas as pd

# --- 1. DATI MANTRA 2025/2026 ---
# Nota: Rispecchiano le asimmetrie (es. 4-4-2 ha un lato E/W e l'altro solo E)
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

# --- 2. LOGICA DIAGNOSTICA ESPERTA ---
def verifica_formazione(giocatori_selezionati, schema_nome, slot_schema):
    if not giocatori_selezionati: return True
    # Ordiniamo per numero ruoli (euristica base)
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
    
    # -- Conteggi Intelligenti --
    count_por = sum(1 for p in giocatori if 'Por' in p['ruoli'])
    
    # Punte e Attaccanti
    pc_puri = sum(1 for p in giocatori if p['ruoli'] == ['Pc'])
    pc_totali = sum(1 for p in giocatori if 'Pc' in p['ruoli'])
    
    # Esterni
    # W_no_E: Giocatori che sono W (o W/A) ma NON possono fare la E
    w_no_e = sum(1 for p in giocatori if 'W' in p['ruoli'] and 'E' not in p['ruoli'])
    
    # 1. Check Portieri
    if count_por > 1: problemi.append(f"⛔ **Troppi Portieri**: {count_por} selezionati. Ne serve 1.")
    
    # 2. Check Punte (Pc)
    if pc_puri > 2: problemi.append(f"⛔ **Troppi Pc puri**: Hai {pc_puri} giocatori solo Pc. Massimo 2.")
    
    # 3. Check CONFLITTO W vs E (Il tuo caso specifico)
    # Se hai 2 o più Pc, devi usare moduli a 2 punte (4-4-2, 3-5-2, ecc).
    # Questi moduli richiedono almeno una E. Se tu hai 2 W che non sono E, non possono giocare.
    if pc_totali >= 2 and w_no_e >= 2:
        problemi.append("⛔ **Conflitto Fasce**: Hai selezionato 2 Punte (Pc) e 2 Ali (W) che non hanno il ruolo E. I moduli a due punte (es. 4-4-2) supportano una W da un lato, ma richiedono obbligatoriamente una **E** dall'altro. Non puoi mettere due W pure.")

    # 4. Check Generico Esterni
    esterni_tot = sum(1 for p in giocatori if any(r in ['W','A','E'] for r in p['ruoli']))
    if esterni_tot > 4:
        problemi.append("⚠️ **Troppi Esterni**: Hai troppi giocatori di fascia.")

    # 5. Check Difesa (solo se rosa quasi completa)
    difensori = sum(1 for p in giocatori if any(r in ['Dd','Ds','Dc','B'] for r in p['ruoli']))
    if tot >= 9 and difensori < 3:
        problemi.append("⛔ **Mancano Difensori**: Hai selezionato quasi una squadra intera ma meno di 3 difensori.")
    
    # 6. Fallback
    if not problemi:
        problemi.append("❓ **Incastro impossibile**: Combinazione di ruoli non valida per nessuno schema. Controlla di non aver sovrapposto troppi giocatori nello stesso ruolo specifico.")

    return problemi

# --- 3. INTERFACCIA ---
st.set_page_config(page_title="Mantra Helper", layout="centered")
st.title("⚽ Mantra Helper")

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
        if st.button("🗑️ Cancella Rosa"):
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
                st.markdown("#### 🕵️ Analisi del problema:")
                for msg in analizza_problemi(target): st.write(msg)

elif not uploaded_file:
    st.info("👆 Carica il file Excel sopra per iniziare.")
