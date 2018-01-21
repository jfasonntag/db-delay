from selenium import webdriver
from bs4 import BeautifulSoup

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




# ============================================================================#
# Run script (move to separate file at some point)
# ============================================================================#
content = []

browser = BrowserObject()

for station in stations:
    content += [browser.get_stationpage(station)]
    
browser.close()