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

def verifica_formazione(giocatori_selezionati, schema_nome, slot_schema):
    if not giocatori_selezionati: return True
    # Ordina per chi ha meno ruoli (più difficile da piazzare)
    giocatori_ordinati = sorted(giocatori_selezionati, key=lambda x: len(x['ruoli']))
    giocatore_corrente = giocatori_ordinati[0]
    ruoli_giocatore = set(giocatore_corrente['ruoli'])
    altri_giocatori = giocatori_ordinati[1:]
    
    for i, slot in enumerate(slot_schema):
        if any(r in slot for r in ruoli_giocatore):
            # Ricorsione
            if verifica_formazione(altri_giocatori, schema_nome, slot_schema[:i] + slot_schema[i+1:]):
                return True
    return False

# --- INTERFACCIA ---
st.set_page_config(page_title="Mantra Excel Pro", layout="centered")
st.title("⚽ Mantra Pro: Carica Rosa")

if 'rosa' not in st.session_state:
    st.session_state.rosa = []

# --- UPLOAD EXCEL ---
with st.expander("📂 Carica file Excel (Ruolo - Calciatore)", expanded=True):
    uploaded_file = st.file_uploader("Trascina qui il file Excel", type=["xlsx", "xls"])
    
    if uploaded_file is not None:
        try:
            df = pd.read_excel(uploaded_file)
            # Pulisce i nomi delle colonne
            df.columns = [str(c).strip().capitalize() for c in df.columns]
            
            if "Ruolo" in df.columns and "Calciatore" in df.columns:
                nuova_rosa = []
                for index, row in df.iterrows():
                    nome = str(row['Calciatore']).strip()
                    ruoli_raw = str(row['Ruolo'])
                    # Gestione separatori (; o , o /)
                    if ";" in ruoli_raw: ruoli = [r.strip() for r in ruoli_raw.split(';')]
                    elif "," in ruoli_raw: ruoli = [r.strip() for r in ruoli_raw.split(',')]
                    elif "/" in ruoli_raw: ruoli = [r.strip() for r in ruoli_raw.split('/')]
                    else: ruoli = [ruoli_raw.strip()]
                    
                    nuova_rosa.append({"nome": nome, "ruoli": ruoli})
                
                st.session_state.rosa = nuova_rosa
                st.success(f"✅ Caricati {len(nuova_rosa)} giocatori!")
            else:
                st.error("⚠️ Il file Excel deve avere le colonne: 'Ruolo' e 'Calciatore'.")
        except Exception as e:
            st.error(f"Errore lettura file: {e}")

# --- VISUALIZZAZIONE ---
if st.session_state.rosa:
    st.divider()
    # Tabella semplice
    st.dataframe(
        pd.DataFrame([{"Calciatore": p['nome'], "Ruoli": ", ".join(p['ruoli'])} for p in st.session_state.rosa]),
        hide_index=True, use_container_width=True
    )

# --- CALCOLO ---
st.divider()
st.subheader("Chi gioca titolare?")

if st.session_state.rosa:
    nomi_rosa = sorted([p['nome'] for p in st.session_state.rosa])
    scelte = st.multiselect("Seleziona i giocatori (Max 11):", nomi_rosa)

    if st.button("🚀 Verifica Moduli", type="primary"):
        if not scelte: st.warning("Seleziona qualcuno.")
        elif len(scelte) > 11: st.error("Max 11 giocatori.")
        else:
            target = [p for p in st.session_state.rosa if p['nome'] in scelte]
            validi = []
            
            for nome, slot in SCHEMI_MANTRA.items():
                if verifica_formazione(target, nome, slot.copy()):
                    validi.append(nome)
            
            if validi:
                st.success(f"Trovati {len(validi)} moduli!")
                cols = st.columns(3)
                for i, m in enumerate(validi):
                    with cols[i%3]: st.markdown(f"#### 🛡️ {m}")
            else:
                st.error("Nessun modulo compatibile.")
                # Check errori comuni
                n_b_only = sum(1 for p in target if 'B' in p['ruoli'] and 'Dc' not in p['ruoli'])
                if n_b_only > 1: st.write("⚠️ Hai messo troppi 'B' puri (Max 1 nelle difese a 3).")
