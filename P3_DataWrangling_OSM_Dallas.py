
# coding: utf-8

# # P3: Wrangle OpenStreetMap Data

# ## Data Wrangling with SQL
# For this project the I have downloaded the Dallas, TX, United states Open Street Map data to work with and the file was downloaded in .osm.bz2 format which was uncompressed to get .osm file. It was a 40.7 mb Compressed file when downloaded and was 602MB after Un-Compressing the Data.

# In[1]:

from IPython.display import Image
from IPython.core.display import HTML 
Image(url= "http://cityclubdallas.com/wp-content/uploads/revslider/home1/Dallas2.jpg")


# Statistics Overview:
# 
#     As I have been working with a very big city (Dallas, TX, USA) the data set is huge. So runing the code has been difficult at times as it takes a lot of Processing time and computing power to Execute the code. So, The code has been developed and tested on a Sample file of the Original data set which is comparitively very small and Easy to work with. So the statistics were given in detail for both the sample and Original File. 
#     
#     Sample OSM Data statistics:
#         Size of the Dataset: 5014 KB
#         Nodes: 1787 KB
#         Nodes_Tags: 98 KB
#         Ways: 146 KB
#         Ways_Nodes: 573 KB
#         Ways_Tags: 599 KB
#         DB Size: 101 KB
#         Key Count: {'lower': 5973, 'lower_colon': 12872, 'problemchars': 1, 'rest': 354}
#         Users: 597
#         Tag Count: {'member': 452,
#                      'nd': 24704,
#                      'node': 21555,
#                      'osm': 1,
#                      'relation': 15,
#                      'tag': 19200,
#                      'way': 2453}
#         
#             
#     Dallas OSM Data statistics:
#         Size of the Dataset: 617456 KB
#         Nodes: 223303 KB
#         Nodes_Tags: 12392 KB
#         Ways: 18181 KB
#         Ways_Nodes: 72906 KB
#         Wasy_Tags: 73783 KB
#         DB Size: 16873 KB
#         Key Count:  {'lower': 751246, 'lower_colon': 1586381, 'other': 39285, 'problemchars': 11}
#         Users: 1802
#         Tag Count:  {'bounds': 1,
#                      'member': 27634,
#                      'nd': 3130074,
#                      'node': 2694280,
#                      'osm': 1,
#                      'relation': 1826,
#                      'tag': 2376923,
#                      'way': 306677}

# # Importing all the necessary packages

# In[2]:

import xml.etree.cElementTree as ET
from collections import defaultdict
import matplotlib.pyplot as plt
import pprint
import re
import os
import codecs


dallas = "dallas_texas.osm"
source = "C:\Users\PremMithilesh\Desktop\Udacity DSND\P3\Finale\DallasOSM"
dallasOSM = os.path.join(source, dallas)


# # Code for counting the Number of tags in the Dataset Programatically

# In[3]:

def tagCounter(dallas):
    tags={}
    
    for event,elem in ET.iterparse(dallas):
        if elem.tag in tags:
            tags[elem.tag]+=1
        else:
            tags[elem.tag]=1
    return tags
tagCounter(dallas)


# # Counts the Key types and groups them based on the Regular Expression.

# In[4]:

lower = re.compile(r'^([a-z]|_)*$') 
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

def key_type(element, keys):
    if element.tag == "tag":
        # YOUR CODE HERE
        for tag in element.iter('tag'):
            k = tag.get('k')
            if lower.search(k):
                keys['lower'] += 1
            elif lower_colon.search(k):
                keys['lower_colon'] += 1
            elif problemchars.search(k):
                keys['problemchars'] += 1
            else:
                keys['other'] += 1
    return keys


def process_map(dallas):
    keys = {"lower": 0, "lower_colon": 0, "problemchars": 0, "other": 0}
    for _, element in ET.iterparse(dallas):
        keys = key_type(element, keys)

    return keys

caluculateKeys = process_map(dallasOSM)
pprint.pprint(caluculateKeys)


# # Counts the unique number of users that Contributed to the Dataset

# In[6]:

# Exploring users
def process_map(dallas):
    users = set()
    for _, element in ET.iterparse(dallas):
        for e in element:
            if 'uid' in e.attrib:
                users.add(e.attrib['uid'])
    return users
users = process_map(dallasOSM)
len(users)


# # Below we try to find the problematic streetnames using a regular expression and we created an Expected and a Mapping funtion.
# # If the Street types is not in the expected, It checks the mapping function and Corrects it based on the Key given to its mapping.

# In[7]:

# Improving Street Names
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)

expected = ["Avenue", "Boulevard", "Circle", "Drive", "East", "Expressway", "Freeway", "Highway", "Lane", "North", "Parkway",
           "Road", "South", "Street", "Trail"]

mapping = { "Av": "Avenue",
            "Ave": "Avenue",
            "Ave.": "Avenue",
            "BLVD": "Boulevard",
            "Blvd": "Boulevard",
            "Blvd.": "Boulevard",
            "blvd": "Boulevard",
            "Cir": "Circle",
            "Dr": "Drive",
            "Dr.": "Drive",
            "dr": "Drive",
            " E": " East",
            "Expy": "Expressway",
            "Fwy": "Freway",
            "Hwy": "Highway",
            "Hwy78": "Highway 78",
            "Ln": "Lane",
            " N": " North",
            "Pkwy": "Parkway",
            "pkwy": "Parkway",
            "RD": "Road",
            "Rd.": "Road",
            "Rd": "Road",
            "rd": "Road",
            " S": " South",
            "St": "Street",
            "St.": "Street",
            "st": "Street",
            "Trl": "Trail" }


# # Updating and developing the expected and Mapping function for the whole data set wold take a lot of time and effort.

# In[8]:

# Auditing Street Names
def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)

def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")

def audit(osmfile):
    osm_file = open(dallas, "r")
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])

    return street_types
st_types = audit(dallasOSM)
# pprint.pprint(dict(st_types))
# The print statement has been voided due to space contraint. 


# # This Function Checks the Streetname and updates the streetname according to the Mapping function by its key value. 

# In[9]:

def update_name(name, mapping, regex):
    m = regex.search(name)
    if m:
        street_type = m.group()
        if street_type in mapping:
            name = re.sub(regex, mapping[street_type], name)

    return name

for st_type, ways in st_types.iteritems():
    for name in ways:
        better_name = update_name(name, mapping, street_type_re)
#         print name, "		<as>		", better_name
# The print statement has been voided due to space contraint. 


# # This is similar to the Streetname correction which is done above. Now we correct the Postalcodes using a similar Process. 

# In[10]:

postal_code_re = re.compile(r'.*(\d{5}(\-\d{4})?)$')
# A List of Entire Postal code of the Dallas. 
expected_ps = ["75201", "75202", "75203", "75204", "75205", "75206",
              "75207", "75208", "75209", "75210", "75211", "75212",
              "75214", "75215", "75216", "75217", "75218", "75219",
              "75220", "75221", "75222", "75223", "75224", "75225",
              "75226", "75227", "75228", "75229", "75230", "75231",
              "75232", "75233", "75234", "75235", "75236"," 75237",
              "75238", "75239", "75240", "75241", "75242", "75243", "75244",
              "75245", "75246", "75247", "75248", "75249", "75250", "75251",
              "75252", "75253", "75258", "75260", "75261", "75262", "75263",
              "75264", "75265", "75266", "75267", "75270", "75275", "75277",
              "75283", "75284", "75285", "75286", "75287", "75294", "75295",
              "75301", "75303", "75310", "75312", "75313", "75315", "75320",
              "75323", "75326", "75336", "75339", "75342", "75346", "75350",
              "75353", "75354", "75355", "75356", "75357", "75359", "75360",
              "75363", "75364", "75367", "75368", "75370", "75371", "75372",
              "75373", "75374", "75376", "75378", "75379", "75380", "75381",
              "75382", "75386", "75387"," 75388", "75389", "75390", "75391",
              "75392", "75393", "75394", "75395", "75396", "75397", "75398",
              "76101", "76102", "76103", "76104", "76105", "76106", "76107", "76108",
              "76109", "76110", "76111", "76112", "76113", "76114", "76115", "76116",
              "76118", "76119", "76120", "76121", "76122", "76123", "76124", "76126",
              "76129", "76130", "76131", "76132", "76133", "76134", "76135", "76136",
              "76137", "76140", "76147", "76148", "76150", "76155", "76161", "76162",
              "76163", "76164", "76177", "76178", "76179", "76181", "76185", "76191",
              "76192", "76193", "76195", "76196", "76197", "76198", "76199"]

postal_mapping = {  "TX 75229 1": "75229",
                    "TX 76248 1": "76248",
                    "TX 76012 1": "76012",
                    "TX 76013 1": "76013",
                    "TX 75230 2": "75230",
                    "TX 75226 3": "75226",
                    "TX 76034 2": "76035",
                    "TX 75071 1": "75071",
                    "TX 75070 1": "75070",
                    "TX 76262 1": "76262",
                    "TX 75074 1": "75074",
                    "75070-4501": "75070",
                    "75080-3338": "75080",
                    "75104-1204": "75104",
                    "75104-2135": "75104",
                    "75215-1816": "75215",
                    "76010-1183": "76010",
                    "76013-3804": "76013",
                    "76028-4910": "76028",
                    "76209-1540": "76209",
                    "TX 75070": "75070",
                    "TX 75071": "75071",
                    "TX 75074": "75074",
                    "TX 75226": "75226",
                    "TX 75229": "75229",
                    "TX 75230": "75230",
                    "TX 76012": "76012",
                    "TX 76013": "76013",
                    "TX 76034": "76034",
                    "TX 76248": "76248",
                    "TX 76262": "76262" }


# In[12]:

# Auditing postal codes
def audit_postalcodes(postal_codes, postalcode):
    m = postal_code_re.search(postalcode)
    if m:
        code_type = m.group()
        if code_type not in expected_ps:
            postal_codes[code_type].add(postalcode)

def is_postalcode(elem):
    return (elem.attrib['k'] == "addr:postcode")

def audit_pc(osmfile):
    osm_file = open(dallas, "r")
    postal_codes = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_postalcode(tag):
                    audit_postalcodes(postal_codes, tag.attrib['v'])

    return postal_codes
postal_codes = audit_pc(dallasOSM)
# pprint.pprint(dict(postal_codes))
# The print statement has been voided due to space contraint. 


# In[13]:

def update_postalcode(code, postal_mapping, regex):
    m = regex.search(code)
    if m:
        code_type = m.group()
        if code_type in postal_mapping:
            code = re.sub(regex, postal_mapping[code_type], code)

    return code

for postal_code, ways in postal_codes.iteritems():
    for code in ways:
        better_code = update_postalcode(code, postal_mapping, postal_code_re)
#         print code, "		<as>		", better_code
# The print statement has been voided due to space contraint.


# In[14]:

import csv
import codecs
import re
import xml.etree.cElementTree as ET
import cerberus
import schema

OSM_PATH ="dallas_texas.osm"

NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

SCHEMA = schema.schema

# Make sure the fields order in the csvs matches the column order in the sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']

def correct_k(k):
    index=k.find(':')
    typ=k[:index]
    k=k[index+1:]    
    return k,typ
def modified_user_name(name):
    list_Username=name.split(' ')
    number_words=len(list_Username)
    firstname=list_Username[0]
    for i in range(1,number_words):
        username_Modified=firstname+' '+list_Username[i]
        firstname=username_Modified
    return firstname

def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    """Clean and shape node or way XML element to Python dict"""
    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []  # Handle secondary tags the same way for both node and way elements

    if element.tag=='node':
        for i in node_attr_fields:
            if i=='user':
                user_name=element.attrib[i]
                user_name_corrected=modified_user_name(user_name)
                node_attribs[i]=user_name_corrected
            else:    
                node_attribs[i]=element.attrib[i]
            
    if element.tag=='way':
        for i in way_attr_fields:
            if i=='user':
                user_name=element.attrib[i]
                user_name_corrected=modified_user_name(user_name)
                way_attribs[i]=user_name_corrected
            else:    
                way_attribs[i]=element.attrib[i]
        
    for tag in element.iter("tag"):
        dic={}
        attributes=tag.attrib
        if problem_chars.search(tag.attrib['k']):
            continue
        
        if element.tag=='node':
            dic['id']=node_attribs['id']
        else:
            dic['id']=way_attribs['id']
        
        dic['value'] = attributes['v']

        colon_k=LOWER_COLON.search(tag.attrib['k'])
        if colon_k:
#             print colon_k.group(0)
#             print tag.attrib['k']
# print statement have been voided due to space constraint.
            if(tag.attrib['k'] == 'addr:street'):
                #update the street name 
                dic['value'] = update_name(dic['value'], mapping, street_type_re)
            dic['key'],dic['type']=correct_k(tag.attrib['v'])
            
            if(tag.attrib['k'] == "addr:postcode"):
                # Update the postal code
                dic['value'] = update_postalcode(dic['value'], postal_mapping, postal_code_re)
            dic['key'],dic['type']=correct_k(tag.attrib['v'])
        else:
            dic['key']=attributes['k']
            dic['type']='regular'
        
        #print dic
        tags.append(dic)
    
    if element.tag=='way':
        position=0
        for nd in element.iter("nd"):
            way_node_dic={}
            way_node_dic['id']=way_attribs['id']
            way_node_dic['node_id']=nd.attrib['ref']
            way_node_dic['position']=position
            position = position + 1
            way_nodes.append(way_node_dic)
             
    if element.tag == 'node':
        return {'node': node_attribs, 'node_tags': tags}
    elif element.tag == 'way':
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}

# ================================================== #
#               Helper Functions                     #
# ================================================== #
def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()
            
class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.iteritems()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

# ================================================== #
#               Main Function                        #
# ================================================== #
def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'wb') as nodes_file,          codecs.open(NODE_TAGS_PATH, 'wb') as nodes_tags_file,          codecs.open(WAYS_PATH, 'wb') as ways_file,          codecs.open(WAY_NODES_PATH, 'wb') as way_nodes_file,          codecs.open(WAY_TAGS_PATH, 'wb') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                if validate is True:
                    validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])
            

if __name__ == '__main__':
    process_map(OSM_PATH, validate= False)


# In[15]:

import sqlite3
import csv
from pprint import pprint


# In[16]:

sqlite_file = 'mydb.db'    # name of the sqlite database file

# Connect to the database
conn = sqlite3.connect(sqlite_file)
conn.text_factory = str


# In[17]:

# Get a cursor object
cur = conn.cursor()


# In[31]:

# Dropping the existing tables
cur.execute('DROP TABLE IF EXISTS nodes')
cur.execute('DROP TABLE IF EXISTS nodes_tags')
cur.execute('DROP TABLE IF EXISTS ways')
cur.execute('DROP TABLE IF EXISTS ways_nodes')
cur.execute('DROP TABLE IF EXISTS ways_tags')
conn.commit()


# In[19]:

# Create the table, specifying the column names and data types:
cur.execute('CREATE TABLE ways(id INTEGER, user TEXT, uid INTEGER, version INTEGER, changeset INTEGER, timestamp TIMESTAMP)')
conn.commit()


# In[20]:

# Read in the csv file as a dictionary, format the data as a list of tuples:
with open('ways.csv','rb') as fin:
    dr = csv.DictReader(fin) # comma is default delimiter
    to_db = [( i['id'], i['user'], i['uid'], i['version'], i['changeset'], i['timestamp']) for i in dr]


# In[21]:

# Test
i['timestamp']


# In[22]:

# insert the formatted data
cur.executemany("INSERT INTO ways(id, user, uid, version, changeset, timestamp) VALUES (?, ?, ?, ?, ?, ?);", to_db)
# commit the changes
conn.commit()


# In[23]:

# Verifying the ways tags using SQLite and cross checking with the tagCounter method from above to make sure the db was properly executed. 
cur.execute('SELECT COUNT(*) FROM ways')
count=cur.fetchall()
print count


# In[24]:

# This query could be used to cross verify the code we ran abouve initially to check the accuracy of the code and db. 


# In[25]:

cur.execute('CREATE TABLE nodes(id INTEGER, lat INTEGER, lon INTEGER, user TEXT, uid INTEGER, version INTEGER, changeset INTEGER, timestamp TIMESTAMP)')
conn.commit()


# In[26]:

# Create the table, specifying the column names and data types:
cur.execute('CREATE TABLE nodes_tags(id INTEGER, key TEXT, value TEXT,type TEXT)')
with open('nodes.csv','rb') as fin:
    dr = csv.DictReader(fin) # comma is default delimiter
    to_db = [(i['id'], i['lat'], i['lon'], i['user'], i['uid'], i['version'], i['changeset']) for i in dr]


# In[27]:

cur.executemany("INSERT INTO nodes(id, lat, lon, user, uid, version, changeset) VALUES (?, ?, ?, ?, ?, ?, ?);", to_db)


# In[28]:

# cur.execute('SELECT TOP 10 e.user, COUNT(*) FROM (SELECT user FROM nodes UNION ALL SELECT user FROM ways)e GROUP BY e.user ORDER BY 2 DESC')
cur.execute('SELECT e.user, COUNT(*) FROM (SELECT user FROM nodes UNION ALL SELECT user FROM ways)e GROUP BY e.user ORDER BY 2 DESC LIMIT 10')
top10Contributors=cur.fetchall()
print top10Contributors


# # Above is a list of the top 10 contributors of the DallasOSM dataset. 

# In[29]:

# No.of Unique users that contributed to the data set.
cur.execute('SELECT COUNT(DISTINCT(e.uid)) FROM (SELECT uid FROM nodes UNION ALL SELECT uid FROM ways) e;')
uniqueusers=cur.fetchall()
print uniqueusers


# In[32]:

cur.execute('CREATE TABLE nodes_tags(id INTEGER, key TEXT, value TEXT,type TEXT)')
conn.commit()
with open('nodes_tags.csv','rb') as fin:
    dr = csv.DictReader(fin) # comma is default delimiter
    to_db = [(i['id'], i['key'],i['value'], i['type']) for i in dr]


# In[33]:

cur.executemany("INSERT INTO nodes_tags(id, key, value,type) VALUES (?, ?, ?, ?);", to_db)


# In[34]:

# Counting Nodes_Tags
cur.execute('SELECT COUNT(*) FROM nodes_tags')
countnt=cur.fetchall()
print countnt


# Challenges Encountered:
# 
#     Improper labeling/Abbrevation techniques used on street names, postal codes and posibily every other attribute if checked. 
#     Huge sized Data Set 602MB.
#     Takes a lot of time to Process the data.
#     Takes a lot of Processing power and my computer got un-resposive at times. 
#     
#     
# Ideas/Suggestions for Improvement:
# 
#     As I have had problems with In-consistent Labling of the Tags, I would like to suggest to create a Standarized Dictionary of Tags that could be used as Street names and Let the top contributors of every Region have access to modify these. Once developed the Dictionary could be colaborated with entries from all over the globe to prevent the effects of Regional/Multi-Lingual Factors. Implementiung and following a proper disipline in making contrubution to the OSM will definitely prevent or atleast reduce such errors.
#     Users should create a self-disiplinatory ethics to contribute to the data in a deciplined manner. 
#     
# Problems with this Improvement:
# 
#     It could be a hactic Job to develop the Standarised Dictory of the Tags on various parts of the globe as These may differ/vary based on Regional/Ligual Factors.
#     The priviliged user with acess might get naughty or Lazy such control in their hands.
#     Production Costs might get involved. 
#    

# References:
# 
#     https://gist.github.com/carlward/54ec1c91b62a5f911c42#file-sample_project-md
#     http://stackoverflow.com/a/4020598
#     https://discussions.udacity.com/t/creating-db-file-from-csv-files-with-non-ascii-unicode-characters/174958/7
#     http://wiki.openstreetmap.org/wiki/Dallas,_Texas
#     https://en.wikipedia.org/wiki/OpenStreetMap
#     
