import streamlit as st

st.set_page_config(layout="wide")

# Custom styles
st.markdown("""
    <style>
    .center {
        display: flex;
        justify-content: center;
        align-items: center;
        flex-direction: column;
        font-size: 22px;
    }
    .button-row {
        display: flex;
        justify-content: center;
        gap: 40px;
        margin-top: 40px;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.markdown("""
<div class="center">
    <h1>📊 WDRR Calculator</h1>
    <p>Choose your market:</p>
</div>
""", unsafe_allow_html=True)

# Navigation buttons
col1, col2, col3 = st.columns([2, 1, 2])
with col2:
    st.markdown("""
    <div class="button-row">
        <a href="/CL" target="_self">
            <button style="font-size:18px;padding:10px 25px;">CL</button>
        </a>
        <a href="/ES" target="_self">
            <button style="font-size:18px;padding:10px 25px;">ES</button>
        </a>
    </div>
    """, unsafe_allow_html=True)
