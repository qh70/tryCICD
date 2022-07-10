from cgitb import text
import json
from sre_constants import CATEGORY
from unicodedata import category

with open("taipei-attractions.json",mode="r",encoding="utf-8") as response:
    data=json.load(response)

import mysql.connector
mydb=mysql.connector.connect(
        host="localhost",
        user="jerry",
        password="12345678",
        database="tourist_data"
    )
my_cursor=mydb.cursor()

for k in range(len(data["result"]["results"])):
    id=k+1
    name=data["result"]["results"][k]["stitle"]
    categories=data["result"]["results"][k]["CAT2"]
    description=data["result"]["results"][k]["xbody"]
    address=data["result"]["results"][k]["address"]
    transport=data["result"]["results"][k]["info"]
    if data["result"]["results"][k]["MRT"]==None:
        data["result"]["results"][k]["MRT"]="沒有資訊"
    mrt=data["result"]["results"][k]["MRT"]
    latitude=data["result"]["results"][k]["latitude"]
    longitude=data["result"]["results"][k]["longitude"]
    # file
    file=data["result"]["results"][k]["file"]
    file=file.split("http")
    file.pop(0)
    for i in range(len(file)):
        file[i]="http"+file[i]
    end=[".jpg", ".JPG", ".PNG", ".png"]
    cleaned_file=[]
    for j in range(len(file)):
        if file[j].endswith(tuple(end)):
            cleaned_file.append(file[j])
    cleaned_file=" ".join(cleaned_file)
    images=cleaned_file
    my_cursor.execute("INSERT INTO sub_data (id,name,category,description,address,transport,mrt,latitude,longitude,image) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);",(id,name,categories,description,address,transport,mrt,latitude,longitude,images))
mydb.commit()

# 把整個網址分成個別網址
'''
# print(data["result"]["results"][0]["file"])
# print("===================")
file=data["result"]["results"][10]["file"]
file=file.split("http")
# print(file)
# print("===================")
file.pop(0)
# print(file)
print("===================")
for i in range(len(file)):
    file[i]="http"+file[i]
    i+=1
print(file)
print("===================")
end=[".jpg", ".JPG", ".PNG", ".png"]
cleaned_file=[]
for j in range(len(file)):
    if file[j].endswith(tuple(end)):
        cleaned_file.append(file[j])
print(cleaned_file)
'''

