import json

count=[]
with open("logs.txt") as f:
    for line in f:
        count.append(line.split())
        

services={}
total=0
# print(count)

for item in count:
 
   if item[1]=="ERROR":
       total=total+1
       services[item[2]]=services.get(item[2],0)+1

finaldict={}
finaldict["total_errors"]=total
finaldict["services"]=services

ans=json.dumps(finaldict,indent=2)

print(ans)
print(total)    