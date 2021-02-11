from sqlalchemy import create_engine
import pymysql
import pandas as pd
import model.Container
#Database credentials
user="d0355a21"
password="uYpeZEAqWz2xkod2"
host="w01b9024.kasserver.com"
database="d0355a21"

#Creating a database connection
db_connection_str = 'mysql+pymysql://d0355a21:uYpeZEAqWz2xkod2@w01b9024.kasserver.com/d0355a21'
db_connection = create_engine(db_connection_str)

#Database output of given query to Pandas dataframe
df = pd.read_sql('SELECT moves.SEQ, moves.UNITNR, moves.UNITTYPE, moves.COMPOUNDPOS_TO, moves.MOVEDATE, moves.ADDRESS_CLIENT FROM (SELECT SEQ, MAX(Q) as mQ FROM internalMovesSQL GROUP BY SEQ) as maxQ, `internalMovesSQL` as moves WHERE moves.SEQ = maxQ.SEQ AND moves.Q = maxQ.mQ AND moves.COMPOUNDPOS_TO LIKE "%.%.%" ORDER BY moves.SEQ;', con=db_connection)    

    
containerlist = []
for index, row in df.iterrows():
    position = row['COMPOUNDPOS_TO']
    containter_obj = Container(position)
    containerlist.append(containter_obj)



print(len(containerlist))
print(containerlist[0].get_position())

#print(df)
#print(df['SEQ'][0])