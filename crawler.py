# -*- coding: utf-8 -*-
"""
Created on Mon Jun 12 23:39:45 2017

@author: Karolis
"""
import time
import json
from bs4 import BeautifulSoup
import selenium.webdriver as webdriver
from selenium.webdriver.common.keys import Keys


SLEEP_BETWEEN_CALLS = 2 #sec
NUM_TRIES_TO_SCRAPE = 3


def get_num_posts(driver):
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    return int(soup.find('span', {'class' : '_bkw5z'}).text.replace(',',''))

 
def load_all_posts(driver):
    num_posts = get_num_posts(driver)
    posts = []
    
    try:
        # Try clicking on the "Load more" button first
        driver.find_element_by_css_selector('._8imhp').click()
    except:
        pass
    
    while num_posts != len(posts):
        try:
            posts = driver.find_elements_by_css_selector("._jjzlb")
            posts[-1].send_keys(Keys.NULL)
            print('\rLoaded {}/{} posts'.format(len(posts), num_posts), end='')
        except:
            break
    print()    
    return posts

    
def load_more_comments():
    while 1:
        try:
            driver.find_element_by_css_selector('._jpmen').click()
            time.sleep(SLEEP_BETWEEN_CALLS)
        except:
            break
        
    
def close_post(driver):
    try:
        # Click on the 'X' button
        driver.find_element_by_css_selector('._3eajp').click()
    except:
        pass
    
    
def scrape_post(post):
    results = {'src' : '',
               'date' : '',
               '#likes' : '',
               '#views' : '',
               '#comments' : '',
               'comments' : []}
               
    post.click()
    time.sleep(SLEEP_BETWEEN_CALLS)
    load_more_comments()
    time.sleep(SLEEP_BETWEEN_CALLS)
    
    # Scrape media link, num_likes, num_comments, and the actual comments
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    results['src'] = post.find_element_by_tag_name('img').get_attribute('src')
    results['date'] = soup.find('time')['title']
    try:
        # Image
        results['#likes'] = soup.find('span', {'class' : '_tf9x3'}).find('span').text
    except:
        # Video
        results['#views'] = soup.find('span', {'class' : '_9jphp'}).find('span').text
    for comment_tag in soup.findAll('li', {'class' : '_99ch8'}):
        try: 
            results['comments'].append(comment_tag.find('span').text)
        except:
            pass
    results['#comments'] = len(results['comments'])
    
    close_post(driver)    
    time.sleep(SLEEP_BETWEEN_CALLS)
    
    return results
    
  
if __name__ == "__main__":
    # Main page of instagram user
    url = 'https://www.instagram.com/jcrew/' 
    
    geckodriver_path = 'C:/Libraries/geckodriver.exe'
    driver = webdriver.Firefox(executable_path=geckodriver_path)
    driver.get(url)
    
    posts = load_all_posts(driver) 
    
    data = []
    post_num = 0
    
    while post_num < len(posts):
        print('\rScraping post {}/{}'.format(post_num+1, len(posts)), end='')
        
        num_tries = NUM_TRIES_TO_SCRAPE
        
        while num_tries: 
            try:
                data.append(scrape_post(posts[post_num]))
            except:
                num_tries -= 1
                close_post(driver)
                time.sleep(SLEEP_BETWEEN_CALLS)
                continue
            break
            
        post_num += 1    
		
	with open('json.txt', 'w') as outfile:
    	json.dump(data, outfile)
    
