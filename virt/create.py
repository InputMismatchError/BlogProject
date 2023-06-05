import mysql.connector

mydb = mysql.connector.connect(
    host = "localhost" ,
    user = "root" ,
    passwd = "1234" )

my_cursor = mydb.cursor()

# IF YOU OPEN THE SERVER FOR THE FİRST TİME, UNCOMMENT THE COMMENTED LİNE BELOW AND RUN THE CODE ONE TİME, 
# THEN YOU DONT NEED THİS FİLE ANYMORE !  
#my_cursor.execute("CREATE DATABASE users")

my_cursor.execute("SHOW DATABASES")
for db in my_cursor:
    print(db)