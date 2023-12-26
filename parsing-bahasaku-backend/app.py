from modules.cnf import get_set_of_production, get_table_element, is_accepted, onCekButtonClick
import streamlit as st
import pandas as pd


input_string_raw = st.text_input('Masukkan kalimat', 'Saya sangat lama', placeholder='Kalimatmu')
st.button('Cek', type='primary', on_click=lambda: onCekButtonClick(input_string_raw))