import os
import streamlit as st
import pandas as pd
import graphviz

RESULT = {}
TRIANGULAR_TABLE = {}
PARSE_TREE = None
PREV_NODE = None

def is_accepted(input_string):
  global TRIANGULAR_TABLE
  TRIANGULAR_TABLE.clear()
  prodRules = get_set_of_production()
  input_string = input_string.lower().split(' ')
  # Inisialisasi triangular table
  for i in range(1, len(input_string)+1):
    for j in range(i, len(input_string)+1):
      TRIANGULAR_TABLE[(i,j)] = []

  for i in reversed(range(1, len(input_string)+1)):
    for j in range(1, i+1):
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

  f = open(os.path.join(dirpath, '../rules-of-cnf.txt'), "r", encoding="utf-8")
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
  
  # print(RESULT)

  return RESULT

def get_raw_set_of_production():
    global RESULT
    RESULT.clear()

    dirpath = os.path.dirname(os.path.abspath(__file__))
    f = open(os.path.join(dirpath, '../rules-of-cfg.txt'), "r", encoding="utf-8")
    for lines in f:
        line = lines.splitlines()
        line = line[0].split(" -> ")
        lhs = line[0]
        rhs = line[1].split(" | ")
        if lhs in RESULT.keys():
            RESULT[lhs].extend(rhs)
        else:
            RESULT[lhs] = rhs
    f.close()
    for key, value in RESULT.items():
        if key == "PropNoun":
            tempList = []
            for val in value:
                if val not in tempList:
                    tempList.append(val.lower())
            RESULT[key] = tempList
    tempList = []
    tempDict = {}
    counter = 1
    for key, value in RESULT.items():
        if key == "K":
            for val in value:
                if len(val.split(" ")) > 2:
                    temp = val.split(" ")
                    while len(temp) > 2:
                        checkStr = temp[0] + " " + temp[1]
                        isFound = False
                        for k, v in tempDict.items():
                            if checkStr == v:
                                isFound = True
                                temp.pop(0)
                                temp.pop(0)
                                temp.insert(0, k)
                                break
                        if not isFound:
                            tempDict["K" + str(counter)] = checkStr
                            temp.pop(0)
                            temp.pop(0)
                            temp.insert(0, "K" + str(counter))
                            counter += 1
                    tempList.append(" ".join(temp))
                else:
                    tempList.append(val)
            RESULT[key] = tempList
    for key, value in tempDict.items():
        RESULT[key] = [value]
    
    print(RESULT)
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

def is_parent(posX, posY, limit, check, prodRules):
  global TRIANGULAR_TABLE
  x = posX
  y = posY
  while posX > 1 and posY <= limit:
    posX -= 1
    if TRIANGULAR_TABLE[(posX, posY)] != []:
      backVar = TRIANGULAR_TABLE[(posX, posY)][-1]
      for i in prodRules[backVar]:
        if check in i.split(" "):
          return [True, posX, posY]
      return [False, None, None]
  posX = x
  posY = y
  while posX >= 1 and posY < limit:
    posY += 1
    if TRIANGULAR_TABLE[(posX, posY)] != []:
      backVar = TRIANGULAR_TABLE[(posX, posY)][-1]
      for i in prodRules[backVar]:
        if check in i.split(" "):
          return [True, posX, posY]
      return [False, None, None]
  return [False, None, None]

def search_left(listVar, checkPos, curPost, posX, posY, limit, prodRules):
    global PARSE_TREE
    global PREV_NODE

    structureTier = ["S", "P", "O", "Pel", "Ket"]

    if len(listVar) == 1:
        if (listVar[0] == "K"):
            PARSE_TREE.edge("K", PREV_NODE)
            return
        else:
            res, x, y = is_parent(posX, posY, limit, listVar[curPost], prodRules)
            if res == True:
                temp = TRIANGULAR_TABLE[(x, y)][-1]
                parentNode = str(temp + " (" + str(x) + "," + str(y) + ")")
                PARSE_TREE.edge(parentNode, PREV_NODE)
                PREV_NODE = parentNode
                search_left(TRIANGULAR_TABLE[(x, y)], len(TRIANGULAR_TABLE[(x, y)])-2, len(TRIANGULAR_TABLE[(x, y)])-1, x, y, limit, prodRules)
            else:
                return
    else:
        if listVar[checkPos] in structureTier and checkPos == 0:
            res, x, y = is_parent(posX, posY, limit, listVar[checkPos], prodRules)
            if res == True:
                parentNode = str(listVar[checkPos] + " (" + str(posX) + "," + str(posY) + ")")
                PARSE_TREE.edge(parentNode, PREV_NODE)
                PREV_NODE = parentNode
                PARSE_TREE.edge("K", parentNode)
                return
            else:
                res2, x2, y2 = is_parent(posX, posY, limit, listVar[curPost], prodRules)
                if res2 == True:
                    temp = TRIANGULAR_TABLE[(x2, y2)][-1]
                    parentNode = str(temp + " (" + str(x2) + "," + str(y2) + ")")
                    PARSE_TREE.edge(parentNode, PREV_NODE)
                    PREV_NODE = parentNode
                    search_left(TRIANGULAR_TABLE[(x2, y2)], len(TRIANGULAR_TABLE[(x2, y2)])-2, len(TRIANGULAR_TABLE[(x2, y2)])-1, x2, y2, limit, prodRules)
                else:
                    return
        elif listVar[checkPos] in structureTier and checkPos > 0:
            res, x, y = is_parent(posX, posY, limit, listVar[checkPos], prodRules)
            if res == True:
                parentNode = str(listVar[checkPos] + " (" + str(posX) + "," + str(posY) + ")")
                PARSE_TREE.edge(parentNode, PREV_NODE)
                PREV_NODE = parentNode
                search_left(TRIANGULAR_TABLE[(x, y)], len(TRIANGULAR_TABLE[(x, y)])-2, len(TRIANGULAR_TABLE[(x, y)])-1, x, y, limit, prodRules)
            else:
                search_left(listVar, checkPos-1, curPost, posX, posY, limit, prodRules)
        elif listVar[checkPos] not in structureTier and checkPos == 0:
            parentNode = str(listVar[checkPos] + " (" + str(posX) + "," + str(posY) + ")")
            PARSE_TREE.edge(parentNode, PREV_NODE)
            PREV_NODE = parentNode
            res, x, y = is_parent(posX, posY, limit, listVar[checkPos], prodRules)
            if res:
                temp = TRIANGULAR_TABLE[(x, y)][-1]
                parentNode = str(temp + " (" + str(x) + "," + str(y) + ")")
                PARSE_TREE.edge(parentNode, PREV_NODE)
                PREV_NODE = parentNode
                search_left(TRIANGULAR_TABLE[(x, y)], len(TRIANGULAR_TABLE[(x, y)])-2, len(TRIANGULAR_TABLE[(x, y)])-1, x, y, limit, prodRules)
        elif listVar[checkPos] not in structureTier and checkPos > 0:
            isFound = False
            for i in prodRules[listVar[checkPos]]:
                if listVar[curPost] in i.split(" "):
                    parentNode = str(listVar[checkPos] + " (" + str(posX) + "," + str(posY) + ")")
                    PARSE_TREE.edge(parentNode, PREV_NODE)
                    PREV_NODE = parentNode
                    isFound = True
                    break
            if isFound:
                search_left(listVar, checkPos-1, checkPos, posX, posY, limit, prodRules)

def get_parse_tree(inputString):
  if is_accepted(inputString):
    global TRIANGULAR_TABLE
    global PARSE_TREE
    global PREV_NODE

    PARSE_TREE = graphviz.Graph("G", strict=True)
    PARSE_TREE.attr("node", shape="circle")
    PARSE_TREE.node("K")

    prodRules = get_raw_set_of_production()
    inputString = inputString.lower().split(" ")

    for i in range(1, len(inputString)+1):
      baseList = TRIANGULAR_TABLE[(i, i)]
      childNode = str(inputString[i-1] + " (" + str(i) + "," + str(i) + ")")
      parentNode = str(baseList[-1] + " (" + str(i) + "," + str(i) + ")")
      PARSE_TREE.edge(parentNode, childNode)
      PREV_NODE = parentNode
      if (len(baseList) == 1):
        search_left(baseList, len(baseList)-1, len(baseList)-1, i, i, len(inputString), prodRules)
      else:
        search_left(baseList, len(baseList)-2, len(baseList)-1, i, i, len(inputString), prodRules)
    return PARSE_TREE
  else:
    return None
