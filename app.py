import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Set page config
st.set_page_config(page_title="Drikke Planner", page_icon="🍹")

# Create a connection object
conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data
def load_data():
    return conn.read(worksheet="Sheet1")

# Load Google Sheet data
df = load_data()

# Initialize session state
if "df_edit" not in st.session_state:
    st.session_state.df_edit = df.copy()
if "page" not in st.session_state:
    st.session_state.page = "login"
if "changes_made" not in st.session_state:
    st.session_state.changes_made = False

# Login Page
if st.session_state.page == "login":
    st.title("Aslak and Hedda's Drink Planner")
    st.subheader("Log in, my friend!")

    with st.form(key="login_form"):
        fornavn = st.text_input("Enter your first name:", key="Fornavn", placeholder="First name")
        etternavn = st.text_input("Enter your last name:", key="Etternavn", placeholder="Last name")
        submitted = st.form_submit_button("Log in")

        if submitted and fornavn and etternavn:
            st.session_state.fornavn = fornavn.strip()
            st.session_state.etternavn = etternavn.strip()
            st.session_state.page = "dashboard"
            st.rerun()


# Dashboard Page
elif st.session_state.page == "dashboard":
    st.title("Bienvenido to the drink planner!")
    st.subheader(f"Heisann, {st.session_state.fornavn} 🍹")

    name = f"{st.session_state.fornavn} {st.session_state.etternavn}"

    for i, row in st.session_state.df_edit.iterrows():
        col1, col2, col3 = st.columns([2, 4, 4])

        with col1:
            bringer_raw = str(row["Bringer"]) if pd.notna(row["Bringer"]) else ""
            bringers = [n.strip() for n in bringer_raw.split(",") if n.strip()]
            count = len(bringers)
            st.write(f"{row['Drikke']} 🍹 ({count}/{int(row['Antall'])})")

        with col2:
            bringer_raw = row["Bringer"]
            bringers = [n.strip() for n in bringer_raw.split(",")] if pd.notna(bringer_raw) and bringer_raw.strip() else []
            can_add = name not in bringers and len(bringers) < int(row["Antall"])
            can_remove = name in bringers and len(bringers) > 0

            add_col, remove_col = st.columns([0.5, 0.5])
            with add_col:
                if st.button("➕", key=f"add_{i}", disabled=not can_add):
                    bringers.append(name)
                    #st.session_state.df_edit.at[i, "Bringer"] = ", ".join(bringers)
                    st.session_state.df_edit.at[i, "Bringer"] = str(", ".join(bringers))
                    st.session_state.changes_made = True
                    st.rerun()

            with remove_col:
                if st.button("➖", key=f"remove_{i}", disabled=not can_remove):
                    bringers.remove(name)
                    st.session_state.df_edit.at[i, "Bringer"] = ", ".join(bringers)
                    st.session_state.changes_made = True
                    st.rerun()

        with col3:
            if bringers:
                st.write("Bringing a bottle: " + ", ".join(bringers))
            else:
                st.write("No one has signed up yet. \U0001F641")

    st.markdown("---")

    # Confirm updates to sheet
    if st.session_state.changes_made:
        if st.button("💾 Comfirm your choice"):
            conn.update(worksheet="Sheet1", data=st.session_state.df_edit)
            st.cache_data.clear()
            st.session_state.df_edit = load_data()
            st.session_state.changes_made = False
            st.success("Google Sheet is updated!")

    # Optional logout
    if st.button("🔙 Log out"):
        st.session_state.clear()
        st.rerun()
