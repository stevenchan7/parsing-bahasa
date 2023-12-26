import os
import streamlit as st
import pandas as pd

TRIANGULAR_TABLE = {}
RESULT = {}

def onCekButtonClick(input_string_raw):
  input_string = input_string_raw.lower().split(" ")

  is_string_accepted = is_accepted(input_string)

  if (is_string_accepted):
    result = get_table_element(input_string_raw)

    df = pd.DataFrame(result)
    df = df.style.highlight_null(props="color: transparent;")  # Hide NaNs

    # Display the table in Streamlit
    st.write('Kalimat diterima')
    st.table(df)
  else:
    st.write('Input tidak diterima')

def is_accepted(input_string):
  prodRules = get_set_of_production()

  # Inisialisasi triangular table
  for i in range(1, len(input_string)+1):
    for j in range(i, len(input_string)+1):
      TRIANGULAR_TABLE[(i,j)] = []

  for i in reversed(range(1, len(input_string)+1)):
    for j in range(1, i+1):
      print(i, j)
      # Paling dasar  
      if (j == j + len(input_string) - i):
        tempList = []
        for key, value in prodRules.items():
          for val in value:
            if (val == input_string[j-1] and key not in tempList):
              tempList.append(key)
        TRIANGULAR_TABLE[(j, j + len(input_string) - i)] = tempList
      
      # Gabungin
      else:
        tempList = []
        resultList = []
        # Gabungin di sini
        for k in range(len(input_string) - i):
            first = TRIANGULAR_TABLE[(j,j+k)]
            second = TRIANGULAR_TABLE[(j+k+1,j+len(input_string) - i)]
            for fi in first:
                for se in second:
                    if (fi + " " + se not in tempList):
                        tempList.append(fi + " " + se)
        # Masukin key gabungan di sini, misal gabungannya NP Noun, nanti keynya adalah NP
        for key, value in prodRules.items():
            for val in value:
                if (val in tempList and key not in resultList):
                    resultList.append(key)
        TRIANGULAR_TABLE[(j,j+len(input_string) - i)] = resultList

  if "K" in TRIANGULAR_TABLE[(1, len(input_string))]:
    return True
  else:
    return False


def get_set_of_production():
  global RESULT
  RESULT.clear()

  dirpath = os.path.dirname(os.path.abspath(__file__))

  f = open(os.path.join(dirpath, '../rules-of-cfg.txt'), "r", encoding="utf-8")
  for line in f:
    # Remove space after line
    line = line.splitlines()
    line = line[0]

    # Seperate left and right
    line = line.split(" -> ")
    lhs = line[0]
    rhs = line[1].split(" | ")

    # Push to result
    if lhs in RESULT.keys():
        RESULT[lhs].extend(rhs) # Extend items if key exist
    else:
        RESULT[lhs] = rhs # Add new
  f.close()

  # Replace Propnoun value with lowercase
  for key, value in RESULT.items():
    if key == "Propnoun":
      tempList = []
      for val in value:
        if val not in tempList:
          tempList.append(val.lower())
      RESULT[key] = tempList

  return RESULT


def get_table_element(input_string):
  global TRIANGULAR_TABLE
  result = []
  n = len(input_string.split(" "))
  for i in range(1, n+1):
    temp = []
    for j in range(i):
      res = TRIANGULAR_TABLE[(j+1, n-i+j+1)]
      if len(res) == 0:
        temp.append("\u2205")
      else:
        temp.append("{" + ", ".join(res) + "}")
    result.append(temp)
  result.append(input_string.split(" "))
  return result
