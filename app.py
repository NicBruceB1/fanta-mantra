import streamlit as st
import pandas as pd

# --- 1. DEFINIZIONE DATI MANTRA 2025/2026 ---
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

# --- 2. LOGICA DIAGNOSTICA (Errore Parlante) ---
def verifica_formazione(giocatori_selezionati, schema_nome, slot_schema):
    if not giocatori_selezionati: return True
    # Ordina per chi ha meno ruoli (più rigidi)
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
    
    # Check 1: Portieri
    count_por = sum(1 for p in giocatori if 'Por' in p['ruoli'])
    if count_por > 1: problemi.append(f"⛔ **Troppi Portieri**: Ne hai messi {count_por}. Ne serve 1.")
    elif count_por == 0 and len(giocatori) > 10: problemi.append("⛔ **Manca il Portiere**.")

    # Check 2: Difensori totali
    difensori = sum(1 for p in giocatori if any(r in ['Dd', 'Ds', 'Dc', 'B'] for r in p['ruoli']))
    if len(giocatori) >= 10 and difensori < 3:
        problemi.append(f"⛔ **Pochi Difensori**: Hai solo {difensori} difensori. Minimo 3.")

    # Check 3: Braccetti puri
    solo_b = sum(1 for p in giocatori if 'B' in p['ruoli'] and 'Dc' not in p['ruoli'])
    if solo_b > 1:
        problemi.append(f"⚠️ **Troppi 'B' puri**: Hai {solo_b} giocatori solo 'B'. Massimo 1 nelle difese a 3.")

    # Check 4: Punte
    solo_pc = sum(1 for p in giocatori if p['ruoli'] == ['Pc'])
    if solo_pc > 2:
        problemi.append(f"⚠️ **Troppe Punte (Pc)**: Hai {solo_pc} giocatori solo Pc. Massimo 2.")

    if not problemi and len(giocatori) == 11:
        problemi.append("❓ **Conflitto generico**: Probabilmente hai troppi giocatori per lo stesso ruolo (es. troppi terzini o troppi mediani).")
    
    return problemi

# --- 3. INTERFACCIA ---
st.set_page_config(page_title="Mantra Mobile", layout="centered")
st.title("⚽ Mantra Helper")

if 'rosa' not in st.session_state: st.session_state.rosa = []

# --- CARICAMENTO FILE ---
with st.expander("📂 Carica Excel", expanded=not st.session_state.rosa):
    uploaded_file = st.file_uploader("Seleziona file", type=["xlsx", "xls"])
    if uploaded_file:
        try:
            df = pd.read_excel(uploaded_file)
            df.columns = [str(c).strip().capitalize() for c in df.columns]
            if "Ruolo" in df.columns and "Calciatore" in df.columns:
                nuova_rosa = []
                for _, row in df.iterrows():
                    nome = str(row['Calciatore']).strip()
                    ruoli_raw = str(row['Ruolo'])
                    for sep in [';', ',', '/']:
                        if sep in ruoli_raw:
                            ruoli_raw = ruoli_raw.replace(sep, ',')
                    ruoli = [r.strip() for r in ruoli_raw.split(',')]
                    nuova_rosa.append({"nome": nome, "ruoli": ruoli})
                st.session_state.rosa = nuova_rosa
                st.success(f"✅ Caricati {len(nuova_rosa)} giocatori!")
                st.rerun()
            else:
                st.error("Il file deve avere colonne: Ruolo, Calciatore")
        except Exception as e:
            st.error(f"Errore: {e}")

if st.session_state.rosa:
    if st.button("🔄 Cambia File Excel"):
        st.session_state.rosa = []
        st.rerun()
    
    st.divider()
    nomi = sorted([p['nome'] for p in st.session_state.rosa])
    scelte = st.multiselect("Chi schieri? (Max 11)", nomi)

    if st.button("🚀 Verifica", type="primary"):
        if not scelte: st.warning("Seleziona qualcuno")
        elif len(scelte) > 11: st.error("Max 11 giocatori")
        else:
            target = [p for p in st.session_state.rosa if p['nome'] in scelte]
            validi = []
            for n, s in SCHEMI_MANTRA.items():
                if verifica_formazione(target, n, s.copy()): validi.append(n)
            
            if validi:
                st.success(f"Trovati {len(validi)} moduli:")
                for m in validi: st.write(f"🛡️ **{m}**")
            else:
                st.error("❌ Nessuna formazione valida.")
                for msg in analizza_problemi(target): st.write(msg)
