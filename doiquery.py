# DOI query agent utilizing CrossRef Query Services through OpenURL
# Bingyin Hu, Duke University, 06182018
# Tailored for CS 516 Project
# Bingyin Hu, Duke University, 11032018
# account.txt needs to be generated on your own, request Crossref Query Services
# account at https://apps.crossref.org/requestaccount/
import urllib2
import contextlib
import xml.etree.ElementTree as ET
import string
import collections
from datetime import date

def runDOIquery(doi):
    # read the credentials
    with open('account.txt') as f:
        account = f.read()
    # form the query
    query = "https://www.crossref.org/openurl/?pid="+account+"&format=unixref&id=doi:"+doi+"&noredirect=true"
    with contextlib.closing(urllib2.urlopen(query)) as contents:
        xmlstring = contents.read() # get an xml string
    # convert to elementtree
    root = ET.fromstring(xmlstring)
    # parsing xml
    metaList = []
    # CitationType
    citeType = root.find('.//crossref/').tag
    if citeType == 'conference':
        metaList = [('CitationType', ['conference proceeding'])]
        metaList = conference(root, metaList)
    elif citeType == 'journal':
        metaList = [('CitationType', ['research article'])]
        metaList = journal(root, metaList)
    metaDict = collections.OrderedDict(metaList)
    return metaDict

def testrun(xml):
    tree = ET.parse(xml)
    root = tree.getroot()
    # CitationType
    citeType = root.find('.//crossref/').tag
    if citeType == 'conference':
        metaList = [('CitationType', ['conference proceeding'])]
        metaList = conference(root, metaList)
    elif citeType == 'journal':
        metaList = [('CitationType', ['research article'])]
        metaList = journal(root, metaList)
    metaDict = collections.OrderedDict(metaList)
    return metaDict

## Journal
def journal(root, metaList):
    # Publication
    temp = root.find('.//journal_metadata/full_title')
    if temp is not None:
        metaList.append(('Publication', [temp.text]))
    # Title
    temp = root.find('.//journal_article/titles/title')
    if temp is not None:
        metaList.append(('Title', [removeTag(ET.tostring(temp))]))
    # Author
    temp = root.findall('.//person_name')
    authors = []
    for person in temp:
        if person.find('given_name') is not None:
            authors.append(person.find('surname').text + ', ' + person.find('given_name').text)
        else:
            full_name = person.find('surname').text
            surname = full_name.split(' ')[-1]
            given_name = full_name[:full_name.find(surname)].strip()
            authors.append(surname + ', ' + given_name)
    if len(authors) > 0:
        metaList.append(('Author', authors))
    # Publisher
    temp = root.find('.//doi_record')
    publisher = {'10.1002':'Wiley Blackwell (John Wiley & Sons)',
                 '10.1110':'Wiley Blackwell (John Wiley & Sons)',
                 '10.1007':'Springer-Verlag',
                 '10.1016':'Elsevier',
                 '10.1006':'Elsevier',
                 '10.1021':'American Chemical Society',
                 '10.1038':'Nature Publishing Group',
                 '10.1039':'The Royal Society of Chemistry',
                 '10.1063':'American Institute of Physics',
                 '10.1080':'Taylor & Francis Group',
                 '10.4161':'Taylor & Francis Group',
                 '10.1088':'IOP Publishing',
                 '10.1103':'American Physical Society',
                 '10.1109':'IEEE',
                 '10.1557':'Cambridge University Press',
                 '10.2514':'American Institute of Aeronautics and Astronautics',
                 '10.3390':'Molecular Diversity Preservation International',
                 '10.3144':'Budapest University of Technology and Economics, Dept. of Polymer Engineering',
                 '10.1371':'PLoS',
                 '10.1177':'Sage',
                 '10.1172':'American Society for Clinical Investigation',
                 '10.7554':'eLife',
                 '10.4049':'American Association of Immunologists',
                 '10.1074':'American Society for Biochemistry and Molecular Biology',
                 '10.1073':'National Academy of Sciences',
                 '10.1261':'Cold Spring Harbor Laboratory Press',
                 '10.1101':'Cold Spring Harbor Laboratory Press',
                 '10.1182':'American Society of Hematology',
                 '10.1186':'BioMed Central',
                 '10.1158':'American Association for Cancer Research',
                 '10.1183':'European Respiratory Society',
                 '10.1084':'Rockefeller University Press',
                 '10.1093':'Oxford University Press',
                 '10.1096':'Federation of American Society for Experimental Biology',
                 '10.1128':'American Society for Microbiology Journals',
                 '10.1042':'Portland Press Limited',
                 '10.1124':'American Society for Pharmacology and Experimental Therapeutics',
                 '10.1126':'American Association for the Advancement of Science',
                 '10.1107':'International Union of Crystallography'}
    if temp is not None and 'owner' in temp.attrib.keys():
        owner = temp.attrib['owner']
        if owner in publisher.keys():
            metaList.append(('Publisher', [publisher[owner]]))
    # PublicationYear
    temp = root.find('.//journal_issue/publication_date/year')
    if temp is not None:
        metaList.append(('PublicationYear', [temp.text]))
    # DOI
    temp = root.find('.//journal_article/doi_data/doi')
    if temp is None:
        temp = root.find('.//doi_data/doi')
        if temp is not None:
            metaList.append(('DOI', [temp.text]))
    else:
        metaList.append(('DOI', [temp.text]))
    # Volume
    temp = root.find('.//journal_volume/volume')
    if temp is not None:
        metaList.append(('Volume', [temp.text]))
    # Issue
    temp = root.find('.//journal_issue/issue')
    if temp is not None:
        metaList.append(('Issue', [temp.text]))
    return metaList
    # URL
    temp = root.find('.//journal_article/doi_data/resource')
    if temp is not None:
        metaList.append(('URL', [temp.text]))
    # ISSN
    issn_e = root.findall('.//issn[@media_type="electronic"]')
    issn_ep = root.findall('.//issn')
    if len(issn_e) < 1:
        if len(issn_ep) >= 1:
            metaList.append(('ISSN', [issn_ep[0].text]))
    else:
        metaList.append(('ISSN', [issn_e[0].text]))
    # Language
    ISO639 = {'en':'English', 'zh':'Chinese', 'de':'German', 'ja':'Japanese',
              'es':'Spanish', 'nl':'Dutch', 'cs':'Czech', 'da':'Danish',
              'fr':'French', 'it':'Italian', 'ko':'Korean', 'ru':'Russian',
              'sv':'Swedish'}
    temp = root.find('.//journal_metadata')
    if temp is not None and 'language' in temp.attrib.keys():
        if temp.attrib['language'] not in ISO639.keys():
            metaList.append(('Language', [temp.attrib['language']]))
        else:
            metaList.append(('Language', [ISO639[temp.attrib['language']]]))
    # Institution
    tempList = root.findall('.//journal_article/contributors/person_name[@sequence="first"]/affiliation')
    affList = [] # init
    for ele in tempList:
        affList.append(ele.text)
    if len(affList) > 0:
        if len(affList) == 1: # one affiliation
            metaList.append(('Institution', [affList[0]]))
        elif ',' in affList[0]: # multiple affiliations
            metaList.append(('Institution', [affList[0]]))
        else: # segmented affiliation
            metaList.append(('Institution', [string.join(affList,', ')]))
    # # DateOfCitation
    # if len(metaList) > 0:
    #     metaList.append(('DateOfCitation', [date.today().isoformat()]))

## Conference
def conference(root, metaList):
    # Publication
    temp = root.find('.//event_metadata/conference_name')
    if temp is not None:
        metaList.append(('Publication', [temp.text]))
    # Title
    temp = root.find('.//conference_paper/titles/title')
    if temp is not None:
        metaList.append(('Title', [temp.text]))
    # Author
    temp = root.findall('.//person_name')
    authors = []
    for person in temp:
        if person.find('given_name') is not None:
            authors.append(person.find('surname').text + ', ' + person.find('given_name').text)
        else:
            full_name = person.find('surname').text
            surname = full_name.split(' ')[-1]
            given_name = full_name[:full_name.find(surname)].strip()
            authors.append(surname + ', ' + given_name)
    if len(authors) > 0:
        metaList.append(('Author', authors))
    # Publisher
    temp = root.find('.//doi_record')
    publisher = {'10.1002':'Wiley Blackwell (John Wiley & Sons)',
                 '10.1007':'Springer-Verlag',
                 '10.1016':'Elsevier',
                 '10.1021':'American Chemical Society',
                 '10.1038':'Nature Publishing Group',
                 '10.1039':'The Royal Society of Chemistry',
                 '10.1063':'American Institute of Physics',
                 '10.1080':'Taylor & Francis Group',
                 '10.1088':'IOP Publishing',
                 '10.1103':'American Physical Society',
                 '10.1109':'IEEE',
                 '10.1557':'Cambridge University Press',
                 '10.2514':'American Institute of Aeronautics and Astronautics',
                 '10.3390':'Molecular Diversity Preservation International',
                 '10.3144':'Budapest University of Technology and Economics, Dept. of Polymer Engineering'}
    if temp is not None and 'owner' in temp.attrib.keys():
        owner = temp.attrib['owner']
        if owner in publisher.keys():
            metaList.append(('Publisher', [publisher[owner]]))
    # PublicationYear
    temp = root.find('.//publication_date/year')
    if temp is not None:
        metaList.append(('PublicationYear', [temp.text]))
    # DOI
    temp = root.find('.//doi_data/doi')
    if temp is not None:
        metaList.append(('DOI', [temp.text]))
    # URL
    temp = root.find('.//doi_data/resource')
    if temp is not None:
        metaList.append(('URL', [temp.text]))
    # Language
    ISO639 = {'en':'English', 'zh':'Chinese', 'de':'German', 'ja':'Japanese',
              'es':'Spanish', 'nl':'Dutch', 'cs':'Czech', 'da':'Danish',
              'fr':'French', 'it':'Italian', 'ko':'Korean', 'ru':'Russian',
              'sv':'Swedish'}
    temp = root.find('.//proceedings_metadata')
    if temp is not None and 'language' in temp.attrib.keys():
        if temp.attrib['language'] not in ISO639.keys():
            metaList.append(('Language', [temp.attrib['language']]))
        else:
            metaList.append(('Language', [ISO639[temp.attrib['language']]]))
    # Institution
    tempList = root.findall('.//conference_paper/contributors/person_name[@sequence="first"]/affiliation')
    affList = [] # init
    for ele in tempList:
        affList.append(ele.text)
    if len(affList) > 0:
        if len(affList) == 1: # one affiliation
            metaList.append(('Institution', [affList[0]]))
        elif ',' in affList[0]: # multiple affiliations
            metaList.append(('Institution', [affList[0]]))
        else: # segmented affiliation
            metaList.append(('Institution', [string.join(affList,', ')]))
    # DateOfCitation
    if len(metaList) > 0:
        metaList.append(('DateOfCitation', [date.today().isoformat()]))
    return metaList

# a helper method to remove anything between "<>" in a string
def removeTag(inStr):
    outStr = ''
    inTag = False
    for ch in inStr:
        if ch == '<':
            inTag = True
        if not inTag:
            outStr += ch
        if ch == '>':
            inTag = False
    return string.join(outStr.split(),' ')