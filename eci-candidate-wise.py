import os
import hashlib
import requests
from bs4 import BeautifulSoup
import pandas as pd
import csv

if not os.path.exists('.cache-ecw'):
    os.makedirs('.cache-ecw')

ua = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.116 Safari/537.36'
session = requests.Session()

def get(url):
    '''Return cached lxml tree for url'''
    url_e=url.encode('utf-8')
    path = os.path.join('.cache-ecw', hashlib.md5(url_e).hexdigest() + '.html')
    #print(path)
    if not os.path.exists(path):
        print (url)
        response = session.get(url, headers={'User-Agent': ua})
        #print("opening")
        with open(path, 'w') as fd:
            fd.write(str(response.text))
            print("finished writing")
    return BeautifulSoup(open(path), 'html.parser')

def eci(url,code,const):
    soup = get(url)
    data = soup.find_all('table')[7].find_all('table')[1]
    state,constituency = data.find('td').text.split(' - ')
    result = []
    for tr in data.find_all('tr')[3:]:
        cells  = [td.text.strip() for td in tr.find_all('td')]
        cells += [state,constituency,code,const]
        result.append(cells)
    return result

result = []


csv_path="values.csv"
file=open(csv_path, 'r')
rows=csv.reader(file)
for r in rows:
    code=r[2]
    const=r[3]
    print(code+"-"+const)
    url = "http://eciresults.nic.in/Constituencywise"+code+str(const)+".htm?ac="+str(const)
    try:
        result += eci(url,code,const)
    except:
        pass
        
file.close()
pd.DataFrame(result).to_csv('eci-candidate-wise.csv', index=False, encoding='utf-8')
