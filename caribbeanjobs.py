#import libraries
import time
import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver import Firefox, Chrome
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

options = Options()
options.headless = True
options.add_argument("--no-sandbox")
options.add_argument("--disable-gpu")
options.add_argument("start-maximized")

s = Service(ChromeDriverManager().install()) #installs chrome driver if not already installed
driver = Chrome(service=s, options=options) #starts chrome driver

def get_soup(url):
    """
    parses pages and returns soup
    """
    r = requests.get(url,
                     headers={"User-Agent": "Mozilla/5.0 (X11; CrOS x86_64 12871.102.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.141 Safari/537.36"})
    soup = BeautifulSoup(r.text, 'html.parser')
    
    return soup

url = "https://www.caribbeanjobs.com/ShowResults.aspx?Keywords=&autosuggestEndpoint=%2fautosuggest&Location=124&Category=&Recruiter=Company%2cAgency&PerPage=100"

driver.get(url)
time.sleep(5)

#finds total number of results and number of pages
result_count = driver.find_element(By.XPATH, "//*[contains(text(),'Total Jobs Found: ')]").text.split("TOTAL JOBS FOUND: ")[1]
result_count = int(result_count)
num_pages = int(np.ceil(result_count/100))

job_urls = []

#gets url for each job posting
for n in np.arange(1,num_pages+1):
    url = "https://www.caribbeanjobs.com/ShowResults.aspx?Keywords=&autosuggestEndpoint=%2fautosuggest&Location=124&Category=&Recruiter=Company%2cAgency&PerPage=100&Page=" + str(n)
    driver.get(url)
    time.sleep(2)
    
    job_nodes = driver.find_elements(By.CSS_SELECTOR, "div.job-result-title > h2[itemprop='title'] > a")
    any(job_urls.append(jn.get_attribute("href")) for jn in job_nodes);

data_list = []

#extracts data for each job
count = 1
for job_url in job_urls:
    print(str(count) + " of " + str(result_count))
    count +=1
    soup = get_soup(job_url)
    try:
        job_title = soup.select("div.job-description h1.job-details--title")[0].text
    except:
        job_title = ""

    try:
        company_name = soup.select("div.job-description .job-details--company")[0].text
    except:
        company_name = ""   

    try:
        city = soup.select("div.job-description .location")[0].text
    except:
        city = ""   

    try:
        salary = soup.select("div.job-description .salary")[0].text
    except:
        salary = ""    

    try:
        job_type = soup.select("div.job-description .employment-type")[0].text
    except:
        job_type = ""

    try:
        updated_time = soup.select("div.job-description .updated-time")[0].text.split("Updated ")[1]
    except:
        updated_time = ""

    try:
        contact = soup.select("div.job-description .updated-time")[1].text
    except:
        contact = ""    

    try:
        description = soup.select("div.job-description div.job-details")[0].text.replace("\n", "").replace("\xa0", "")
    except:
        description = ""   

    try:
        image_url = soup.select("div.company-details > img.logo-dk")[0]["src"]
        if "not-disclosed" in image_url:
            image_url = ""
    except:
        image_url = ""

    try:
        company_profile = "https://www.caribbeanjobs.com" + soup.select("div.company-details > div > p > strong > a")[0]["href"]
    except:
        company_profile = ""    

    try:
        company_address = soup.select("div.company-details .company-contact-list .address")[0].text
    except:
        company_address = ""    

    try:
        company_phone = soup.select("div.company-details .company-contact-list .telnum")[0].text
    except:
        company_phone = ""

    try:
        company_website = soup.select("div.company-details .company-contact-list .url")[0].text
    except:
        company_website = ""  

    dt = {
        "Job Title": job_title,
        "Job Url": job_url,
        "City": city,
        "Salary": salary,
        "Job Type": job_type,
        "Updated Time": updated_time,
        "Contact": contact,
        "Description": description,
        "Company Name": company_name,
        "Company Logo": image_url,
        "Company Address": company_address,
        "Company Phone": company_phone,
        "Company Website": company_website,
        "Company Profile Link": company_profile
    }

    data_list.append(dt)

#converts extracted data to dataframe
df = pd.DataFrame(data_list)

#saves dataframe to csv
df.to_excel("caribbeanjobs.xlsx", index=False)

try:
    driver.close() 
except:
    pass

try:
    driver.quit()
except:
    pass

