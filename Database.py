import pymysql 
  
# Create a connection object 
  
conn  = pymysql.connect('w01b9024.kasserver.com', 'd0355a21', 'uYpeZEAqWz2xkod2', 'd0355a21') 
  
# Create a cursor object 
cur  = conn.cursor() 
  
  
query = "SELECT moves.SEQ, moves.UNITNR, moves.UNITTYPE, moves.COMPOUNDPOS_TO, moves.MOVEDATE, moves.ADDRESS_CLIENT FROM (SELECT SEQ, MAX(Q) as mQ FROM internalMovesSQL GROUP BY SEQ) as maxQ, `internalMovesSQL` as moves WHERE moves.SEQ = maxQ.SEQ AND moves.Q = maxQ.mQ ORDER BY moves.SEQ""
"
  
cur.execute(query) 
  
rows = cur.fetchall() 
conn.close() 
  
for row in rows : 
    print(row)
