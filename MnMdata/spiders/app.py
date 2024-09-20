import streamlit as st
import subprocess
from pymongo import MongoClient
from docx import Document
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.shared import Pt
import io
import os

MONGO_URI = os.getenv('MONGO_URI')

client = MongoClient(MONGO_URI)
db = client['MnMdata']
collection = db['MnM']

def run_scrapy_spider(url):
    try:
        subprocess.run(["scrapy", "crawl", "da", "-a", f"url={url}"], check=True)
        st.success("Scraping completed successfully!")
    except subprocess.CalledProcessError as e:
        st.error(f"An error occurred during scraping: {e}")

def load_document():
    document = collection.find_one(sort=[('_id', -1)])
    if not document:
        st.error("No data found in MongoDB. Please scrape the data first.")
        return None
    return document

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
doc_path = os.path.join(BASE_DIR, 'toc.docx')

doc = Document(doc_path)

def level(i):
    j = i.split(" ", 1)[0]
    dot = j.count(".")
    return dot 

def clean(name):
    a = name.split(" ", 1)[1]
    if "(Page No." in a:
        a = a.split(" (Page No.", 1)[0].strip() 
    if "introduction" == a.lower(): 
        a = "Market Overview"
    if "KEY STAKEHOLDERS" in a:
        a = "CUSTOMER & BUYING CRITERIA ANALYSIS"
    a = a.title()
    return a

st.title("TOC Generator V@2")
url = st.text_input("Enter the URL to scrape")

if st.button("Scrape Data"):
    if url:
        run_scrapy_spider(url)
    else:
        st.error("Please enter a valid URL.")

document = load_document()

if document:
    toc_content = []

    keywords = [
        "VALUE CHAIN ANALYSIS",
        "SUPPLY CHAIN ANALYSIS",
        "TECHNOLOGY ANALYSIS",
        "REGULATORY LANDSCAPE",
        "PATENT ANALYSIS",
        "TRADE ANALYSIS",
        "PRICING ANALYSIS",
        "CASE STUDY",
        "TECHNOLOGY TRENDS",
        "KEY STAKEHOLDERS AND BUYING CRITERIA",
        "KEY STAKEHOLDERS & BUYING CRITERIA",
    ]
    market_name="NONE"
    for chapter in document.get('chapters', []):
        if "by region" in chapter['chapter'].lower():
            market_name=clean(chapter['chapter'].lower().split(", by region",1)[0])
            print(market_name)
        if "MARKET OVERVIEW" in chapter['chapter'] or "PREMIUM INSIGHTS" in chapter['chapter']:
            
            for subsection in chapter.get('sub_sections', []):
                if any(keyword in subsection.upper() for keyword in keywords):
                    if subsection.count(".") == 1:
                        toc_content.append((clean(subsection), level(subsection)))

    arr = []
    for chapter in document.get('chapters', []):
        arr.append(chapter['chapter'])  

    st.write("Select main chapter")
    select_box = st.multiselect("Select chapter", arr)

    if select_box:
        for selected in select_box:    
            for chapter in document.get('chapters', []):
                if selected in chapter['chapter']: 
                    toc_content.append((clean(chapter['chapter']), level(chapter['chapter'])))
                    
                    for subsection in chapter.get('sub_sections', []):
                        toc_content.append((clean(subsection), level(subsection))) 
    else:
        st.write("No chapters selected.")
    if "toc_entries" not in st.session_state:
        st.session_state["toc_entries"] = []

    def add_toc_entry():
        name = st.session_state["new_heading"].title()
        level = st.session_state["new_level"]
        
        if name:
            st.session_state["toc_entries"].append((name, level))

    st.text_input("Enter heading or subheading", key="new_heading")
    st.selectbox("Select level", [0, 1, 2, 3, 4, 5, 6], key="new_level")

    if st.button("Add Chapter/Subheading"):
        add_toc_entry()
    if st.session_state["toc_entries"]:
        st.write("Current TOC Structure:")
        for entry in st.session_state["toc_entries"]:
            st.write(f"{entry[0]} (Level {entry[1]})")
    print(st.session_state["toc_entries"])  
      
    region_toc = [
        (f'{market_name} Size by Region', 0),
        ('Market Overview', 1),
        ('North America', 1),
        ('USA', 2),
        ('Canada', 2),
        ('Europe', 1),
        ('Germany', 2),
        ('Spain', 2),
        ('France', 2),
        ('UK', 2),
        ('Italy', 2),
        ('Rest of Europe', 2),
        ('Asia Pacific', 1),
        ('China', 2),
        ('India', 2),
        ('Japan', 2),
        ('South Korea', 2),
        ('Rest of Asia-Pacific', 2),
        ('Latin America', 1),
        ('Brazil', 2),
        ('Rest of Latin America', 2),
        ('Middle East & Africa (MEA)', 1),
        ('GCC Countries', 2),
        ('South Africa', 2),
        ('Rest of MEA', 2),
        ('Competitive Landscape', 0),
        ('Top 5 Player Comparison', 1),
        ('Market Positioning of Key Players, 2023', 1),
        ('Strategies Adopted by Key Market Players', 1),
        ('Recent Activities in the Market', 1),
        ('Key Companies Market Share (%), 2023', 1),
        ('Key Company Profiles', 0)
    ]

    data = st.text_area("Enter Companies in BULLET format")
    
    company_toc = []
    if st.button("Add Companies"):

        cleaned_data = data.replace('•', '').strip()
        company_list = [line.strip() for line in cleaned_data.splitlines() if line.strip()]
        
        for company in company_list:
            company_toc.append((company, 1))  
            company_toc.append(("Company Overview", 2))
            company_toc.append(("Business Segment Overview", 2))
            company_toc.append(("Financial Updates", 2))
            company_toc.append(("Key Developments", 2))

    def add_bullet_point_text(text, level):
        paragraph = doc.add_paragraph(text)
        paragraph.style = 'List Paragraph'
        
        numbering = paragraph._element.get_or_add_pPr().get_or_add_numPr()
        
        numId = OxmlElement('w:numId')
        numId.set(qn('w:val'), '1')  
        
        ilvl = OxmlElement('w:ilvl')
        ilvl.set(qn('w:val'), str(level))  
        
        numbering.append(numId)
        numbering.append(ilvl)

        run = paragraph.runs[0]
        run.font.size = Pt(11)
        run.font.name = 'Calibri'
        
        if level == 0:
            run.bold = True
        
        paragraph_format = paragraph.paragraph_format
        paragraph_format.line_spacing = 1.5  

    toc_content = toc_content + st.session_state["toc_entries"] + region_toc + company_toc

    for heading, level in toc_content:
        add_bullet_point_text(heading, level)

    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)  
    st.download_button(
        label="Download Document",
        data=buffer,
        file_name="toc_document.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
