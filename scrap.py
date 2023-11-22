# IMPORT ALL LIBRARIES
from bs4 import BeautifulSoup as BS
import requests as req
 
#url = "https://www.businesstoday.in/latest/economy"
url = "https://www.reuters.com/site-search/?query=ASML"

 # YOU CAN EVEN DIRECTLY PASTE THE URL IN THIS
webpage = req.get(url)  

#HERE HTML PARSER IS ACTUALLY THE WHOLE HTML PAGE
trav = BS(webpage.content, "html.parser")  
 
M = 1 

# TO GET THE TYPE OF CLASS  HERE 'a' STANDS FOR ANCHOR TAG IN WHICH NEWS IS STORED
#for link in trav.find_all('a'):
for link in trav.find_all('li', class_='search-results__item__2oqiX'):

    # PASTE THE CLASS TYPE THAT WE GET FROM THE ABOVE CODE IN THIS AND SET THE LIMIT GREATER THAN 35
    if(str(type(link.string)) == "<class 'bs4.element.NavigableString'>"
       and len(link.string) > 35):
 
        print(str(M)+".", link.string)
        M += 1