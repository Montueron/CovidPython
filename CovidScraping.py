

import requests
import re
from bs4 import BeautifulSoup
from Secret import GS


URL = 'https://www.covid19.admin.ch/en/epidemiologic/case?detGeo=CH&geoView=table&detRel=abs'
page = requests.get(URL)

soup = BeautifulSoup(page.content, 'html.parser')
g = soup.select('a[href*="/downloads/sources-csv"]')
#print(g[0]['href'])

url = "https://www.covid19.admin.ch" + g[0]['href']
r = requests.get(url, allow_redirects=True)

open('sources-csv.zip', 'wb').write(r.content)


import zipfile
my_zip = zipfile.ZipFile('sources-csv.zip') # Specify your zip file's name here
storage_path = '.'
for file in my_zip.namelist():
    if my_zip.getinfo(file).filename.endswith('COVID19Cases_geoRegion.csv') or my_zip.getinfo(file).filename.endswith('COVID19VaccDosesAdministered.csv') or my_zip.getinfo(file).filename.endswith('COVID19FullyVaccPersons.csv'):
        my_zip.extract(file, storage_path) # extract the file to current folder if it is a text file


import csv

casesFR = []

with open('data/COVID19Cases_geoRegion.csv', newline='') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
    for row in spamreader:
        #print(', '.join(row))
        if row[0] == '"FR"':
            #print(row)
            casesFR.append([row[1],row[2],row[3]])


import pandas as pd

#lst = []


df3 = pd.DataFrame(casesFR, columns=['a', 'b', 'c'])

df3.to_csv (r'casesFR_2.csv', index = False, header=False)
print('casesFr written localy')


vaccinsCH = {}

with open('data/COVID19VaccDosesAdministered.csv', newline='') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
    for row in spamreader:
        if row[1] == '"CH"':
            vaccinsCH[row[0]] = row[4]



vaccinsCHList = []

with open('data/COVID19FullyVaccPersons.csv', newline='') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
    for row in spamreader:
        if row[1] == '"CH"':
            vaccinsCHList.append([row[0], vaccinsCH[row[0]], (int(vaccinsCH[row[0]]) - int(row[4])), row[4]])


df4 = pd.DataFrame(vaccinsCHList)

df4.to_csv (r'vaccinsCH.csv', index = False, header=False)

print('vaccins written localy')

#csv.register_dialect('myDialect', delimiter=';',  quoting=csv.QUOTE_ALL)

#with open('casesFR.csv', 'w', newline='') as myfile:
#     wr = csv.writer(myfile, dialect='myDialect')
#     #wr = csv.writer(myfile)
#     wr.writerow(casesFR)


from github import Github
g = Github(GS)

repo = g.get_user().get_repo("Covid")


all_files = []
contents = repo.get_contents("")
while contents:
    file_content = contents.pop(0)
    if file_content.type == "dir":
        contents.extend(repo.get_contents(file_content.path))
    else:
        file = file_content
        all_files.append(str(file).replace('ContentFile(path="','').replace('")',''))

with open('casesFR_2.csv', 'r') as file:
    content = file.read()

# Upload to github
git_prefix = 'cases/'
git_file = git_prefix + 'casesFR_2.csv'
if git_file in all_files:
    contents = repo.get_contents(git_file)
    repo.update_file(contents.path, "committing files", content, contents.sha, branch="main")
    print(git_file + ' UPDATED')
else:
    repo.create_file(git_file, "committing files", content, branch="main")
    print(git_file + ' CREATED')



with open('vaccinsCH.csv', 'r') as file:
    content = file.read()


git_prefix = 'vaccins/'
git_file = git_prefix + 'vaccinsCH.csv'
if git_file in all_files:
    contents = repo.get_contents(git_file)
    repo.update_file(contents.path, "committing files", content, contents.sha, branch="main")
    print(git_file + ' UPDATED')
else:
    repo.create_file(git_file, "committing files", content, branch="main")
    print(git_file + ' CREATED')