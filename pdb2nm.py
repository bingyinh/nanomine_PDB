# Conversion script for pdb data to fit with PDB_NanoMine schema
# Bingyin Hu, 11/01/2018
import csv
from lxml import etree as ET
import dicttoxml
import os
from xml_update_validator import runValidation
from doiquery import runDOIquery


csvFile = "PDB_match_conditions.csv"

def mySplit(myString):
    inter = myString.split(",")
    output = []
    temp = ''
    for i in xrange(len(inter)):
        if i%2 == 1:
            temp += ", " + inter[i].strip()
            output.append(temp)
            temp = ''
        else:
            temp += inter[i].strip()
    return output        


with open(csvFile, 'r') as f:
    reader = csv.DictReader(f)
    progress = 0
    total = 129493
    for row in reader:
        progress += 1
        # init
        (pdb_id, mmtype, mmclass, mmweight, date, sequence, source,
         uniprot, exptech, crysmeth, crystemp, spacegp, coltemp, ph,
         dfsource, device, resolution, pubmedid, doi, journal,
         pubyear, title, author) = ['']*23
        # conversion
        DATA = [] # the list that will finally be => dict => xml
        if row['pdb_id'] not in ['null', '']:
            pdb_id = row['pdb_id']
        if row['mmtype'] not in ['null', '']:
            mmtype = row['mmtype']
        if row['mmclass'] not in ['null', '']:
            mmclass = row['mmclass']
        if row['mmweight'] not in ['null', '']:
            mmweight = row['mmweight']
        if row['date'] not in ['null', '']:
            date = row['date']
        if row['sequence'] not in ['null', '']:
            sequence = row['sequence']
        if row['source'] not in ['null', '']:
            source = row['source']
        if row['uniprot'] not in ['null', '']:
            uniprot = row['uniprot']
        if row['exptech'] not in ['null', '']:
            exptech = row['exptech']
        if row['crysmeth'] not in ['null', '']:
            crysmeth = row['crysmeth']
        if row['crystemp'] not in ['null', '']:
            crystemp = row['crystemp']
        if row['spacegp'] not in ['null', '']:
            spacegp = row['spacegp']
        if row['coltemp'] not in ['null', '']:
            coltemp = row['coltemp']
        if row['ph'] not in ['null', '']:
            ph = row['ph']
        if row['dfsource'] not in ['null', '']:
            dfsource = row['dfsource']
        if row['device'] not in ['null', '']:
            device = row['device']
        if row['resolution'] not in ['null', '']:
            resolution = row['resolution']
        if row['pubmedid'] not in ['null', '']:
            pubmedid = row['pubmedid']
        if row['doi'] not in ['null', '']:
            doi = row['doi']
        if row['journal'] not in ['null', '']:
            journal = row['journal']
        if row['pubyear'] not in ['null', '']:
            pubyear = row['pubyear']
        if row['title'] not in ['null', '']:
            title = row['title']
        if row['author'] not in ['null', '']:
            author = row['author']
        # PDB_ID
        if pdb_id != '':
            DATA.append({'PDB_ID':pdb_id})
        # DATA_SOURCE
        DS = []
        if doi != '':
            metadict = runDOIquery(doi.strip())
            for field in metadict:
                for ele in metadict[field]:
                    DS.append({field:ele})
        else:
            if journal != '':
                DS.append({'Publication':journal})
            if title != '':
                DS.append({'Title':title})
            if author != '':
                for aut in mySplit(author):
                    DS.append({'Author':aut.strip()})
            if pubyear != '':
                DS.append({'PublicationYear':pubyear})
            if date != '':
                DS.append({'DateOfCitation':date})
        if len(DS) > 0:
            DATA.append({
                         'DATA_SOURCE':
                            {
                             'Citation':DS
                            }
                        })
        # MATERIALS
        MC = []
        if uniprot != '':
            MC.append({'ChemicalName':uniprot})
        if mmclass != '':
            MC.append({'MacroMoleculeClass':mmclass})
        if mmtype != '':
            MC.append({'MacroMoleculeType':mmtype})
        if source != '':
            MC.append({'ManufacturerOrSourceName':source})
        if mmweight != '':
            MC.append({'MolecularWeight':{'value':mmweight}})
        if len(MC) > 0:
            DATA.append({
                         'MATERIALS':
                            {
                             'Matrix':
                                {
                                 'MatrixComponent':MC
                                }
                            }
                        })
        # CHARACTERIZATION
        XRD = []
        if exptech == 'X-RAY DIFFRACTION':
            equip = dfsource + ' ' + device
            if equip.strip() != '':
                XRD.append({'Equipment':equip.strip()})
            descr = ''
            if coltemp != '':
                descr += 'Data collection temperature: ' + coltemp + ' K, '
            if resolution != '':
                descr += 'Resolution: ' + resolution + ', '
            if descr != '':
                XRD.append({'Description':descr.strip(", ")})
        if len(XRD) > 0:
            DATA.append({
                         'CHARACTERIZATION':
                            {
                             'XRay_Diffraction_and_Scattering':XRD
                            }
                        })
        # PROPERTIES
        PROP = []
        Th = [] # Thermal
        if crysmeth != '':
            Th.append({'MeasurementMethod':crysmeth})
        if crystemp != '':
            Th.append({'CrystalizationTemperature':[{'value':crystemp},
                                                    {'unit':'Kelvin'}]})
        if len(Th) > 0:
            PROP.append({'Thermal':Th})
        Bio = [] # Biological
        if sequence != '':
            Bio.append({'Sequence':sequence})
        if spacegp != '':
            Bio.append({'SpaceGroup':spacegp})
        if ph != '':
            Bio.append({'pH':ph})
        if len(Bio) > 0:
            PROP.append({'Biological':Bio})
        if len(PROP) > 0:
            DATA.append({'PROPERTIES':PROP})
        if len(DATA) > 0:
            toxml = {'item':DATA}
            nmxml = dicttoxml.dicttoxml(toxml, custom_root='PolymerNanocomposite', attr_type=False)
            nmxml = nmxml.replace('<item>', '').replace('</item>', '').replace('<item >', '')
            tree = ET.ElementTree()
            root = ET.fromstring(nmxml)
            tree._setroot(root)
            if not os.path.exists("xml"):
                os.mkdir("xml")
            filename = './xml/' + str(pdb_id) + '.xml'
            tree.write(filename, encoding="UTF-8", xml_declaration=True)
            print 'Finished converting ' + pdb_id + '............' + '%.2f' % (progress/float(total)*100) +"%"

xmlDir = 'xml/'
jobDir = '.'
xsdDir = 'PNC_PDB_schema.xsd'
logName = runValidation(xmlDir, xsdDir, jobDir)