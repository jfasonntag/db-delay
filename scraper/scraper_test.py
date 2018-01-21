from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd

# ============================================================================#
# A few parameters to set upfront
starting_page = "https://reiseauskunft.bahn.de/bin/bhftafel.exe/"
check_products = (0,1) # checkmarks to click in the query form: 0 = ICE, 1 =EC/IC, 2= IR, 3 = Regio, 4, = S-Bahn

# ============================================================================#
# Set Scraper scope (should be moved to a sperate file later)
stations = ['München Hbf', 'Augsburg Hbf', 'Ulm Hbf']



# ============================================================================#
# Define Classes and  functions
# ============================================================================#

# Check a checkbox element on a webpage
def check_box(checkbox):
    if checkbox.is_selected() ==True:
        pass
    else:
        checkbox.click()

# Uncheck a checkbox element on a webpage
def uncheck_box(checkbox):
    if checkbox.is_selected() ==True:
        checkbox.click()
    else:
        pass

class BrowserObject(webdriver.Firefox):
    """A selenium webdriver with custom methods for DB scraping"""
    
    # Set up a Selenium webdriver class for firefox and open the station table website
    def __init__(self, page = starting_page):
        webdriver.Firefox.__init__(self)
        self.get(page)
        
        # Click on the checkmarks in the search form to select/ deselect train types
        for product in range(0,8):
            if product in check_products:
                check_box(self.find_element_by_id('prod_'+str(product)))
            else:
                uncheck_box(self.find_element_by_id('prod_'+str(product)))

            
    # Display the departure/arrivals table for the current time of a given station and return source code
    def get_stationpage(self,stationname, arrival = True):        
        # Enter UNIQUE station name
        station_input = self.find_element_by_id('rplc0')
        station_input.clear()
        station_input.send_keys(stationname)
        
        # Arrival or departure info?
        if arrival == True:
            self.find_element_by_id('arr').click()
        else:
            self.find_element_by_id('dep').click()
            
        # Submit the form
        self.find_element_by_name('start').click()
        
        return BeautifulSoup(self.page_source,"html.parser")
    

# Turn BeautifulSoup output of a page into a nice DataFrame
def parse_results(results):
    data = pd.DataFrame()
    
    # Find table with results and loop over rows
    rows = results.find(attrs={"class":"result stboard arr"}).findAll("tr")
    for row in rows:
        row_dict ={}
        for element in ['time', 'train', 'platform', 'ris']:
            item = row.find(attrs={'class':element})
            if item is not None: 
                row_dict.update({element:row.find(attrs={'class':element}).get_text().strip()}) 
        if row_dict.get('train') =='':
            for tds in row.find_all(attrs={'class':'train'}):
                if tds.get_text().strip() != '' : 
                    row_dict.update({'train':tds.get_text().strip()})
                    break
        data = data.append(pd.DataFrame(row_dict, index=[0]))
    
    # Save when the querry was returned and get rive of pagination
    data['query_time'] = data[data['train']=='aktuelle Uhrzeit'].time.to_string(index=False)
    data = data[(data['time'] != 'früher') & (data['time'] != 'später') & (data['time'] != 'Zeit') & (data['train'] != 'aktuelle Uhrzeit')]
        
    return data.reset_index(drop=True)
            
            



# ============================================================================#
# Run script (move to separate file at some point)
# ============================================================================#
content = []

browser = BrowserObject()

for station in stations:
    content += [browser.get_stationpage(station)]
    
browser.close()