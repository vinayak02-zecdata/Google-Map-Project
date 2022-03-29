import time
from timeit import default_timer
from dateutil.relativedelta import relativedelta
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options ### To add headless option
from bs4 import BeautifulSoup

import requests
import pandas as pd



"""
    Empty list to extend all the extracted data to this list
"""
final_data = []


def get_page_source_using_selenium(link):
    soup = None
    retry_count = 0
    MAX_RETRY =3
    options = Options()
    options.headless = True
    WAIT_TIME_OUT = 1
    while retry_count < MAX_RETRY:
        """
            below firefoxoptions.headless will restrict opening  firefoxbrowser everytime
        """
        driver = webdriver.Chrome(executable_path= "D:\\Projects\\google_map project\\chromedriver.exe",options = options )
        #driver = webdriver.Firefox(executable_path="./geckodriver")

        driver.implicitly_wait(0.5)
        driver.get(link)
        time.sleep(1)
        driver.refresh()
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        # print(soup.text)
        driver.close()
        if 'Request unsuccessful. Incapsula incident ID' not in soup.text:
            print(' ******************** Page Has Content so stoping loop and process it *****************')
            break
        else:
            retry_count  = retry_count + 1
            print(f"###### Retrying {retry_count}")
            time.sleep(WAIT_TIME_OUT+retry_count)
        # driver.close()
        
    if retry_count == MAX_RETRY:
        print('Unable to get data from page so saving page number and other objects')
    return soup



def scrap_data_for_multi_page(data, key):

    data1= data.find_all("div", class_= "V0h1Ob-haAclf")
    all_links = []
    for items in data1:
        rest_link =items.find_all('a')
        for href_link in rest_link:
            links=href_link.get('href')
            all_links.append(links)
        

    map_all_data = []
    

    """
        Extracting Top three entries if entries greater than 3.
    """
    for all_link in all_links[:3]:
        get_all_link_data = get_page_source_using_selenium(all_link)
        data= get_all_link_data.find("div", class_= "QSFF4-text")
        print("get_all_link_data ************", get_all_link_data)
        map_all_data.append(get_address_dict(data.text, key))
    #print(map_all_data)
    
    return map_all_data


def get_address_dict(address, key):
    all_data = address.split(',')
    #print("all data*********: ",all_data)

    """ If extracted data is having U.S country """
    if ((" United States" in all_data) or (
        " U.S" in all_data) or (" US" in all_data)) and len(all_data)==4:
        
        state_code = all_data[2].split()
        final_data.extend([{"GM_country":all_data[-1], 
            "GM_city" : all_data[1], 
            "GM_state" : state_code[0], 
            "GM_zipcode" : state_code[1],
            "Map_search": key
            }])
    
    #If extracted data is having non-U.S country
    else:
        final_data.extend([{"GM_country":all_data[-1], 
            "GM_city" :'null', 
            "GM_state" : 'null', 
            "GM_zipcode" : 'null',
            "Map_search": key
            }])
   
    """
        Creating new csv file for all the extracted data from google map.
    """

    final_map_df = pd.DataFrame(final_data,columns=["GM_country","GM_city","GM_zipcode","Map_search"])
    final_map_df.to_csv("Google_map.csv", index = False)
    
    return final_data



def get_driver_object(link, key=None):
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(executable_path= "D:\\Projects\\google_map project\\chromedriver.exe",options = options)
    #driver = webdriver.Firefox(executable_path="./geckodriver")
    driver.implicitly_wait(0.5)
    driver.refresh()
    driver.get(link)
    complete_list = []
    complete_dict = {}
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    #print(soup)
    multple_links = soup.find_all("div", class_= "V0h1Ob-haAclf")
    # print("************************",data1)
    if not multple_links:
        address = get_single_entity_data(driver, key)
        complete_list.append(address)
        complete_dict[key] = [address]
    else:
        adress_list = scrap_data_for_multi_page(soup, key)  
        complete_list.extend(adress_list)
        complete_dict[key] = adress_list

    driver.close()
    print(complete_list,"*****")


def get_single_entity_data(driver, key):

    address = driver.find_element_by_css_selector("[data-item-id='address']")

    print("single Entity data:***** ",address.text)
    final_dict = get_address_dict(address.text, key)
    return final_dict
    


def link_to_be_searched():  
    map_df = pd.read_excel("Sample.xlsx",usecols=['company' ,'location'])
    search_company = map_df['company'].to_list()
    search_location =  map_df['location'].to_list()
    search_result = [ x +" "+y for x,y in zip(search_company, search_location)]

    final_search = {}
    for search_data in range(len(search_result)):
        searching = search_result[search_data].replace(" -","").replace("   ","").replace(" ","+")
        final_search[search_result[search_data]] = searching

    for key, item in final_search.items():
        link = f"https://www.google.com/maps/search/{item}"
        get_driver_object(link, key)

        #break
  

    final_search = []
    for search_data in range(len(search_result)):
        searching = search_result[search_data].replace(" -","").replace("   ","").replace(" ","+")
        final_search.append(searching)


link_to_be_searched()


















