#This program is used to scrape for gifts given a singular query.
from urllib.request import Request, urlopen
from random import shuffle
from bs4 import BeautifulSoup
import requests
import sys
program, zip_code, query, priority, current_month, desired_month, desired_day = sys.argv

def main(zip_code, query, priority, current_month, desired_month, desired_day):
  desired_day = int(desired_day)

  '''Given the following parameters, the function below will return a list that contains the number of days from the desired date of delivery. The function will return None if the product will not be delivered in time.'''

  def deliver_check(current_month, desired_month, desired_day, url): 
      months_dict = {"Dec":31, "Jan":31, "Feb":28, "Mar":31, "Apr":30, "May":31, "Jun":30, "Jul":31, "Aug":31, "Sep":30, "Nov":30}
      months = list(months_dict.keys()) 
      month_index = (next(x for x in range(12) if months[x] == current_month)) 
      months = months[month_index:] + months[:month_index] #rearranges months as to make calculations easier later on.

      response= requests.get(url).text 
      soup = BeautifulSoup(response, 'html.parser')
      delivery = soup.find_all(class_="vi-acc-del-range") #finds part of website that displays the shipping date
      for i, month in enumerate(months):
          if month in delivery[0].text: 
              month_location = delivery[0].text.find(month) #finds index for month in list of month
              date = int(delivery[0].text[month_location+5:month_location+7].strip())
              if desired_month == month:
                if desired_day > date:
                  return [desired_day - date, [month, date]]
              else: 
                #the below calculates number of days to ship provided that the delivery month and desired delivery month are different (ex. I want a package delivered by January 1 and the package is scheduled to arrive December 30)
                days = 0
                delivery_index = (next(x for x in range(12) if months[x] == desired_month))
                if i < delivery_index: 
                  for month in months[i:delivery_index]:
                    days += months_dict[month]
                  return [days+desired_day, [month,date]]

  def filter(results, priority): #sorts the initial query results if the user wants to sort by price (ascending or descending).
    if priority == "cheap":
      results = sorted(results, key=lambda x: x[1])
    if priority == "pricey":
      results = sorted(results, key=lambda x: x[1], reverse=True)
      #print(results)
        

    return results 

  results = []
  link = f"https://www.ebay.com/sch/i.html?_from=R40&_nkw={query}&_sacat=0&LH_TitleDesc=0&_stpos={zip_code}&_fcid=1"


  req = Request(link, headers={'User-Agent':'Mozilla/5.0'})
  webpage = urlopen(req).read()

  soup = BeautifulSoup(webpage, 'html5lib')
  items = soup.find_all('h3', {"class":"s-item__title"})[1:] #finds titles of products
  prices = soup.find_all("span", {"class":"s-item__price"}) #finds prices of products
  links = soup.find_all("a", {"class":"s-item__link"})[1:] #finds links to product pages
  image_links = soup.find_all("img", {"class":"s-item__image-img"}) #finds link to an image

  for i in range(len(items)): #produces a nested list of all products listed
    results.append([items[i].text, float(prices[i].text.split(" ")[0].replace(",", "")[1:]), links[i]['href'], image_links[i]['src']])
  results = filter(results, priority)

  end_results = [] # empty list that will be used to filter out product results that don't meet delivery date
  for i in results:
    delivery_list = deliver_check(current_month, desired_month, desired_day, i[2])
    if delivery_list != None:
      end_results.append(i+delivery_list)
    if len(end_results) == 20: #will return only the top 20 applicable products to reduce runtime
      break
  
  if priority == "fast": #sorts list by delivery
    end_results = sorted(end_results, key=lambda x: x[4], reverse = True)
    return end_results
  if priority == "chaos": #makes list completely random
    return shuffle(end_results)
  return end_results

print(main(zip_code, query, priority, current_month, desired_month, desired_day))
'''command-line example: 
      python main.py 78222 watch cheap Dec Dec 25
      This command will find a watch that will arrive by December 25 to an address in the 78222 zip code, provided that the current month is December.'''
