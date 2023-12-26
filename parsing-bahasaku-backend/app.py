from modules.cnf import get_table_element, is_accepted
import streamlit as st
import pandas as pd

st.title('Parsing Bahasa Kelompok D2')
st.divider()
input_string_raw = st.text_input('Masukkan kalimat', 'Saya sangat lama', placeholder='Kalimatmu')
# st.button('Cek', type='primary', on_click=lambda: onCekButtonClick(input_string_raw))

input_string = input_string_raw.lower().split(" ")

is_string_accepted = is_accepted(input_string)

df = None

result = get_table_element(input_string_raw)

df = pd.DataFrame(result)
df = df.style.highlight_null(props="color: transparent;")  # Hide NaNs

if (is_string_accepted):
  # Display the table in Streamlit
  st.write('Kalimat diterima')
else:
  st.write('Input tidak diterima')

if(df):
  st.table(df)