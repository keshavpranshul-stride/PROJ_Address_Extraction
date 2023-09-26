from flask import Flask, jsonify, request, redirect
from geopy.geocoders import Photon
geolocator = Photon(user_agent="app")
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
from PyPDF2 import PdfReader
import re

USstates = {'AK': 'Alaska','AL': 'Alabama','AR': 'Arkansas','AZ': 'Arizona','CA': 'California','CO': 'Colorado','CT': 'Connecticut','DC': 'District of Columbia','DE': 'Delaware','FL': 'Florida','GA': 'Georgia','HI': 'Hawaii','IA': 'Iowa','ID': 'Idaho','IL': 'Illinois','IN': 'Indiana','KS': 'Kansas','KY': 'Kentucky','LA': 'Louisiana','MA':'Massachusetts','MD': 'Maryland','ME': 'Maine','MI':'Michigan','MN':'Minnesota','MO':'Missouri','MS':'Mississippi', 'MT': 'Montana','NC': 'North Carolina','ND': 'North Dakota','NE':'Nebraska','NH': 'New Hampshire','NJ': 'New Jersey','NM': 'New Mexico','NV': 'Nevada','NY': 'New York','OH': 'Ohio','OK': 'Oklahoma','OR': 'Oregon','PA': 'Pennsylvania','RI': 'Rhode Island','SC': 'South Carolina',    'SD': 'South Dakota','TN': 'Tennessee','TX': 'Texas','UT': 'Utah','VA':'Virginia','VT': 'Vermont','WA': 'Washington','WI':'Wisconsin','WV': 'West Virginia','WY': 'Wyoming'}

app = Flask(__name__,template_folder='templates')

@app.route('/')
def upload_file():
    return render_template('index.html')

@app.route('/display', methods = ['GET', 'POST'])
def display_file():
    if request.method == 'POST':
        f = request.files['file']
        filename = secure_filename(f.filename)
        f.save(filename)
        file1 = open(filename,"r")
        global pdf_text 
        content = PdfReader(filename)
        pdf_text=""
        for i in range(0,len(content.pages)):
            page = content.pages[i]
            pdf_text += page.extract_text()
        return redirect("/address")

@app.route('/address', methods = ['GET'])
def getAddress():
    add = pdf_text.replace("#",'')
    USAPattern = r"\d+\s+[A-Za-z ]+[,]\s+[A-Za-z ]+[,]\s+[A-Z]{2}\s+\b\d{5}\b[,]\s+(?:USA|United States|US)"
    CanadaPattern = r"\d+\s+[a-zA-Z'. ]+,\s+[a-zA-Z'. ]+,\s+[a-zA-Z'. ]+\s+\b[A-Z]\d[A-Z]\s\d[A-Z]\d\b, Canada"
    UKPattern = r"\d+\s+[a-zA-Z'.0-9, ]*(?:UK|United Kingdom|England)"
    FrancePattern = r"\d+\s+[a-zA-Z'. àâæçéèêëîïôœùûüÿ]*,\s+\d{5}\s+[a-zA-Z'. àâæçéèêëîïôœùûüÿ]*, France"
    NetherlandsPattern = r"[a-zA-Z '\-]+\d+[a-zA-Z '\-]+,[A-Za-z\-\s\(\)]+,\s+\d{4}\s+[A-Z]{2}"
    GermanyPattern = r"[a-zA-Z'. äöüÄÖÜß]*,?[a-zA-Z'. äöüÄÖÜß]+\s*\d*[.,]\s+\d{5}\s+[a-zA-Z'. äöüÄÖÜß]*, Germany"
    LuxembourgPattern = r"(?:\d+|\d[A-Z])\s+[a-zA-Z'. ]+,\s+\d+[a-zA-Z'. ]+, Luxembourg"
    SingaporePattern = r"\d+\s*[A-Za-z#'.,\-– 0-9]+Singapore\s+\d{5}"
    result ={}
    canadaAddresses = re.findall(CanadaPattern,add)
    for i in range(0,len(canadaAddresses)):
        loc=geolocator.geocode(canadaAddresses[i],timeout=None)
        if loc is not None and loc.raw['properties']['country'] == 'Canada':
            if 'Canada_Addresses' not in result.keys():
                result['Canada_Addresses']=[]
                result['Canada_Addresses'].append(canadaAddresses[i])
            else:
                result['Canada_Addresses'].append(canadaAddresses[i])
    usAddresses = re.findall(USAPattern,add)
    for i in range(0,len(usAddresses)):
        if "USA" in usAddresses[i]:
            usAddresses[i]=usAddresses[i].replace("USA","United States")
        for j in USstates.keys():
            if j in usAddresses[i]:
                usAddresses[i]=usAddresses[i].replace(j,USstates[j])
        loc=geolocator.geocode(usAddresses[i],timeout=None)
        if loc is not None:
            if 'USA_Addresses' not in result.keys():
                result['USA_Addresses']=[]
                result['USA_Addresses'].append(usAddresses[i])
            else:
                result['USA_Addresses'].append(usAddresses[i])
    ukAddresses = re.findall(UKPattern,add)
    for i in range(0,len(ukAddresses)):
        if "UK" in ukAddresses[i]:
            ukAddresses[i]=ukAddresses[i].replace("UK","England, United Kingdom")
        loc=geolocator.geocode(ukAddresses[i],timeout=None)
        if loc is not None:
            if 'UK_Addresses' not in result.keys():
                result['UK_Addresses']=[]
                result['UK_Addresses'].append(ukAddresses[i])
            else:
                result['UK_Addresses'].append(ukAddresses[i])
    franceAddresses = re.findall(FrancePattern,add)
    for i in range(0,len(franceAddresses)):
        loc=geolocator.geocode(franceAddresses[i],timeout=None)
        if loc is not None and loc.raw['properties']['country'] == 'France':
            if 'France_Addresses' not in result.keys():
                result['France_Addresses']=[]
                result['France_Addresses'].append(franceAddresses[i])
            else:
                result['France_Addresses'].append(franceAddresses[i])
    netherlandsAddresses = re.findall(NetherlandsPattern,add)
    for i in range(0,len(netherlandsAddresses)):
        loc=geolocator.geocode(netherlandsAddresses[i],timeout=None)
        if loc is not None:
            if 'Netherlands_Addresses' not in result.keys():
                result['Netherlands_Addresses']=[]
                result['Netherlands_Addresses'].append(netherlandsAddresses[i])
            else:
                result['Netherlands_Addresses'].append(netherlandsAddresses[i])
    germanyAddresses = re.findall(GermanyPattern,add)
    for i in range(0,len(germanyAddresses)):
        if 'Germany_Addresses' not in result.keys():
            result['Germany_Addresses']=[]
            result['Germany_Addresses'].append(germanyAddresses[i])
        else:
            result['Germany_Addresses'].append(germanyAddresses[i])
    luxAddresses = re.findall(LuxembourgPattern,add)
    for i in range(0,len(luxAddresses)):
        loc=geolocator.geocode(luxAddresses[i],timeout=None)
        if loc is not None:
            if 'Luxembourg_Addresses' not in result.keys():
                result['Luxembourg_Addresses']=[]
                result['Luxembourg_Addresses'].append(luxAddresses[i])
            else:
                result['Luxembourg_Addresses'].append(luxAddresses[i])
    singaporeAddresses = re.findall(SingaporePattern,add)
    for i in range(0,len(singaporeAddresses)):
        loc=geolocator.geocode(singaporeAddresses[i],timeout=None)
        if loc is not None:
            if 'Singapore_Addresses' not in result.keys():
                result['Singapore_Addresses']=[]
                result['Singapore_Addresses'].append(singaporeAddresses[i])
            else:
                result['Singapore_Addresses'].append(singaporeAddresses[i])
    return jsonify({'addresses':result})

if __name__ == '__main__':
    app.run(debug = True)