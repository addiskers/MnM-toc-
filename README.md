Here's a `README.md` for your GitHub project:

---

# MnM TOC Generator with Streamlit and Scrapy

This project provides an automated Table of Contents (TOC) generator for MnM (Markets and Markets) reports using **Streamlit** for the web interface and **Scrapy** for the web scraping functionality. The tool allows users to scrape report chapters and download them as a Word document.

### Live Demo:

- **Render Deployment (Scrapy + Streamlit)**: [MnM TOC on Render](https://streamlit-scrapy.onrender.com)
- **Streamlit Deployment**: [MnM TOC on Streamlit Cloud](https://tocmnm.streamlit.app/)

## Features:

1. **Paste the M&M Report URL**:
   - Enter any MnM report URL into the input field.
   - Example URL: `https://www.marketsandmarkets.com/Market-Reports/mobile-robots-market-43703276.html`

2. **Automatic Scraping**:
   - The tool will automatically scrape all chapters from the report using Scrapy.
   - You will receive a success message once the scraping is complete.

3. **Chapter Selection**:
   - Use the dropdown box to select specific chapters or segments of the report, such as "By Type," "By Application," etc.
   - **Note**: The "Introduction" and "Company Profile" sections are automatically included, so you don’t need to select them manually.

4. **Download Word Document**:
   - After selecting the desired chapters, click "Download" to receive a Word document containing the selected chapters.

## Usage Instructions:

1. Visit one of the live demos:
   - **Render Deployment**: [https://streamlit-scrapy.onrender.com](https://streamlit-scrapy.onrender.com)
   - **Streamlit Deployment**: [https://tocmnm.streamlit.app/](https://tocmnm.streamlit.app/)
   
2. Paste the MnM report URL into the input field and click "Scrape."
   
3. After scraping is completed, select the chapters you want to include using the provided select box. Avoid choosing "Introduction" or "Company Profiles" as they are added automatically.

4. Click "Download" to download the Word document containing the selected chapters.

## Technology Stack:

- **Frontend**: Streamlit (for the web interface)
- **Backend**: Scrapy (for web scraping the MnM report)
- **Database**: MongoDB (to store the scraped data)
- **Deployment**: Render for combined deployment and Streamlit Cloud for the Streamlit interface

## Project Setup (For Local Development):

1. **Clone the repository**:
   ```bash
   git clone https://github.com/addiskers/MnM-toc-.git

   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Streamlit app**:
   ```bash
   streamlit run app.py
   ```

4. **Run the Scrapy spider** (if running locally):
   ```bash
   scrapy crawl da
   ```

## Future Enhancements:

- Add support for scraping more report formats.
- Improve chapter identification for cleaner selection.

---
