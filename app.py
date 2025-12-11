# app.py
import streamlit as st
import pandas as pd
from solver import solve_equilibrium
from reactions import reactions

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="🧪 Chemical Reaction Equilibrium Solver",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');
body {
    background: linear-gradient(135deg, #0D1B2A, #1B263B);
    color: #E0E0E0;
    font-family: 'Poppins', sans-serif;
}
h1, h2, h3, h4 { color: #00FFA3; font-family: 'Poppins', sans-serif; }
h1 { font-size: 48px; }
h2 { font-size: 36px; }
h3 { font-size: 28px; }
.stButton>button {
    background-color: #0077B6;
    color: #FFFFFF;
    font-weight: bold;
    border-radius: 8px;
    padding: 10px 18px;
    transition: 0.3s;
}
.stButton>button:hover {
    background-color: #00B4D8;
}
.dataframe, .stDataFrame {
    background-color: #0A1D2F !important;
    color: #CAF0F8 !important;
    border-radius: 6px;
    font-family: 'Poppins', sans-serif;
}
.indent { margin-left: 25px; }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
st.sidebar.title("🧭 Navigation")
page = st.sidebar.radio("Go to", ["🏠 Home", "🧪 Solver", "📚 Theory", "📖 Reaction Database", "ℹ️ About"])


# -----------------------------------------------------------------------------------
# --- HOME PAGE ---
if page == "🏠 Home":
    st.title("🧪 Chemical Reaction Equilibrium Solver Using Gibbs Free Energy Minimization")
    st.markdown("""
### Welcome! 🚀

This web-based solver analyzes the equilibrium behavior of chemical reactions under specified temperature and pressure conditions. It uses thermodynamic principles to determine **equilibrium compositions** and **reaction properties**.

**Features include:**  
<div class="indent">• 🔬 Select industrially relevant reactions</div>
<div class="indent">• 🌡️ Input initial moles and operating conditions</div>
<div class="indent">• ⚡ Compute thermodynamic properties and equilibrium composition</div>


**Main Capabilities:**  
<div class="indent">• 📉 Gibbs Free Energy minimization</div>
<div class="indent">• 🧮 Thermodynamic property evaluation</div>
<div class="indent">• 🔁 Numerical solution of reaction extent</div>


**The Solver Computes:**  
<div class="indent">• 🔥 Standard Enthalpy Change (ΔH°)</div>
<div class="indent">• ❄️ Standard Entropy Change (ΔS°)</div>
<div class="indent">• ⚡ Standard Gibbs Free Energy Change (ΔG°)</div>
<div class="indent">• 📊 Equilibrium Constant (K)</div>
<div class="indent">• ↔️ Extent of Reaction (ξ)</div>
<div class="indent">• ⚛️ Equilibrium Mole Fractions</div>


All reactions are based on real industrial chemical processes.
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------------
# SOLVER PAGE
# -----------------------------------------------------------------------------------
elif page == "🧪 Solver":

    st.title("🧪 Solver 🧮")

    # Reaction selection
    st.markdown("### Step 1: Select a Reaction 🧪")
    reaction_names = [r["name"] for r in reactions]
    selected_name = st.selectbox("Choose a reaction", reaction_names)
    reaction = next(r for r in reactions if r["name"] == selected_name)

    st.markdown(f"**Balanced Equation:** ⚖️ {reaction['equation']}")
    st.markdown(f"**Description:** 💡 {reaction['description']}")

    # Conditions
    st.markdown("### Step 2: Enter Reaction Conditions 🌡️")
    col1, col2 = st.columns(2)
    with col1:
        T = st.number_input("Temperature (K)", min_value=200.0, max_value=2000.0, value=298.15)
    with col2:
        P = st.number_input("Pressure (atm)", min_value=0.1, max_value=1000.0, value=1.0)

    # Initial moles
    st.markdown("### Step 3: Enter Initial Moles of Species ⚛️")
    n0 = {}
    for species in reaction["stoichiometry"]:
        n0[species] = st.number_input(f"{species} (mol)", min_value=0.0, value=1.0)

    # Button
    if st.button("Compute Equilibrium 🚀"):
        with st.spinner("Calculating equilibrium..."):
            try:
                results = solve_equilibrium(reaction, n0, T, P)
                species = list(reaction["stoichiometry"].keys())

                st.markdown("### ✅ Equilibrium Results")

                # Results table
                results_table = pd.DataFrame({
                    "Property": [
                        "Extent of Reaction (ξ)",
                        "ΔH° (kJ/mol)",
                        "ΔS° (kJ/mol·K)",
                        "ΔG° (kJ/mol)",
                        "K (Equilibrium Constant)"
                    ],
                    "Value": [
                        f"{results['ξ_eq']:.4f}",
                        f"{results['ΔH']:.4f}",
                        f"{results['ΔS']:.4f}",
                        f"{results['ΔG']:.4f}",
                        f"{results['K']:.4e}"
                    ]
                })

                st.dataframe(results_table)

               
                species = list(reaction["stoichiometry"].keys())
                # Composition Table
                st.markdown("### ⚛️ Equilibrium Composition")
                composition_table = pd.DataFrame({
                    "Species": species + ["Total Moles (N)"],
                    "Moles (ξ)": list(results["n_eq_xi"].values()) + [results["N_expr"]],
                    "Moles (mol)": [f"{val:.4f}" for val in results["n_eq"].values()] + [f"{results['N']:.4f}"],
                    "Mole Fraction (ξ)": list(results["y_eq_xi"].values()) + [""],
                    "Mole Fraction": [f"{val:.4f}" for val in results["y_eq"].values()] + [""]
                })

                st.dataframe(composition_table)

            except Exception as e:
                st.error(f"Error in calculation: {e}")


# -----------------------------------------------------------------------------------
# --- THEORY PAGE ---
elif page == "📚 Theory":
    st.title("📚 Thermodynamic Theory")
    st.markdown("""
## Gibbs Free Energy Minimization Condition ⚖️

At equilibrium, the Gibbs free energy of the system is minimized. The equilibrium condition is:

ΔG = ΔG° + RT ln(Q) = 0

This leads to:

Q = K

The solver numerically adjusts the extent of reaction (ξ) until this condition is satisfied, which is mathematically equivalent to **minimizing the total Gibbs free energy** at constant T and P.

---

### Formulas Used 🔬

**1. Standard Enthalpy Change of Reaction (ΔH°):**  
ΔH° = Σ(νᵢ ΔHᵢ°)

**2. Standard Entropy Change of Reaction (ΔS°):**  
ΔS° = Σ(νᵢ Sᵢ°)

**3. Standard Gibbs Free Energy Change (ΔG°):**  
ΔG° = ΔH° − TΔS°  

**4. Equilibrium Constant (K):**  
K = exp(−ΔG° / RT)  

**5. Extent of Reaction (ξ):**  
nᵢ = nᵢ₀ + νᵢ ξ  

**6. Equilibrium Mole Fraction:**  
yᵢ = nᵢ / Σ nᵢ
""")


# -----------------------------------------------------------------------------------
# REACTION DATABASE
# -----------------------------------------------------------------------------------
elif page == "📖 Reaction Database":
    st.title("📖 Reaction Database")

    df = pd.DataFrame(
        [[r["name"], r["equation"], r["description"]] for r in reactions],
        columns=["Reaction Name", "Balanced Equation", "Industrial Description"]
    )

    st.dataframe(df, use_container_width=True)


# -----------------------------------------------------------------------------------
# ABOUT PAGE
# -----------------------------------------------------------------------------------
elif page == "ℹ️ About":
    st.title("ℹ️ About This Project")
    st.markdown("""
**Developed by:** GROUP 3 — CHE 3105  
**Course:** ChE 408 – Solution Thermodynamics  
**University:** Batangas State University – TNEU  

### Data Source
• Lange’s Handbook of Chemistry, 12th Edition  
• Perry’s Chemical Engineers’ Handbook, 9th Edition

### Software Used
• Python  
• NumPy  
• Streamlit  

### Computational Method
• Gibbs Free Energy Minimization  
""")

