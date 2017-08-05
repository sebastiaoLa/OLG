import sqlite3

conn = sqlite3.connect("OLG.db")

cur = conn.cursor()

cur.execute(""" CREATE TABLE jogador (idjogador INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, senha TEXT, pontuacao INTEGER DEFAULT 0) """)
cur.execute(""" CREATE TABLE partidas (idpartidas INTEGER PRIMARY KEY AUTOINCREMENT, jogador1 INTEGER, jogador2 INTEGER, jogadordavez INTEGER, tabuleiro TEXT DEFAULT '  ,  ,  ,  ,  ,  ,  ,  ,  ') """)
cur.execute(""" CREATE TABLE historico (idhistorico INTEGER PRIMARY KEY AUTOINCREMENT, jogador1 TEXT, jogador2 TEXT, vencedor TEXT) """)

conn.commit()
cur.close()
