'''
command:

python KillJobs.py -url=172.20.9.42:1100 -screenShotPath=/home/acv2/DistLHP/tools/webScrap

'''

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
import re
import time
import argparse
import sys
import os


mailReceiver = [   
                    "zhangchao3322218@sina.com"
                ]

ZOMBIE_JOB_LIST = {"list1": [], "list2": [], "list3":[]}

def get_mail_receiver():
    receiver = ' '
    for recv in mailReceiver:
        receiver = receiver + recv + ' '

    return receiver

def kill_zombie_jobs(screenShotPath, url):
    browser = webdriver.PhantomJS() # Get local session of PhantomJS
    # browser = webdriver.Firefox() # Get local session of Firefox
    browser.set_window_size(2500, 2000)
    
    targetUrl = "http://%s/#JOBS" %url
    print "url: ", targetUrl
    
    job_to_be_kill_indicate = 0
    
    browser.get(targetUrl) # Load page
    userName = browser.find_elements_by_class_name("gwt-TextBox")
    password = browser.find_elements_by_class_name("gwt-PasswordTextBox")
    submitButton = browser.find_elements_by_class_name("gwt-Button")
    
    if len(userName) == 0 or len(password) == 0 or len(submitButton) == 0:
        print "error in open url: %s" %targetUrl
        browser.quit()
        return
        
    userName[0].send_keys("root")
    password[0].send_keys("******")
    time.sleep(1)
    submitButton[0].click()
    
    time.sleep(2)
    
    sceen_shot_name = screenShotPath + "/Before_kill_jobs_screen_shot.png"
    browser.save_screenshot(sceen_shot_name)

    jobs_name_pattern_0 = "//body/div[2]/div[2]/div/div[4]/div/div[3]/div/div[4]/div/div[2]/div/div[2]/div/div/div/div[3]/table[2]/tbody/tr[1]/td/fieldset/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr/td[1]"
    jobs_name_pattern = "//body/div[2]/div[2]/div/div[4]/div/div[3]/div/div[4]/div/div[2]/div/div[2]/div/div/div/div[3]/table[2]/tbody/tr[1]/td/fieldset/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr[Order]/td[1]"
    jobs_duration_pattern = "//body/div[2]/div[2]/div/div[4]/div/div[3]/div/div[4]/div/div[2]/div/div[2]/div/div/div/div[3]/table[2]/tbody/tr[1]/td/fieldset/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr[Order]/td[5]"
    
    for i in range(1, 4):
        tmp_list = "list"+str(i)
        job_name_elements_list = browser.find_elements_by_xpath(jobs_name_pattern_0)
        job_length = len(job_name_elements_list) 
        
        for index in range(1, job_length+1):
            job_name_pattern = jobs_name_pattern.replace("Order", str(index))
            job_duration_pattern = jobs_duration_pattern.replace("Order", str(index))
            job_name = get_element_name(browser, job_name_pattern)
            job_duration_time = get_duration_time(get_element_name(browser, job_duration_pattern))
            
            if len(job_name) > 10 and job_duration_time == 0:
                ZOMBIE_JOB_LIST[tmp_list].append(job_name)
        time.sleep(60)
        
    zombie_job_list = get_zombie_job_list(ZOMBIE_JOB_LIST)
    print "\n ---------To be killed job list: ", zombie_job_list
    len1 = len(zombie_job_list)
    print "\n ---------To be killed job list length: ", len1
    kill_jobs_in_list(browser, zombie_job_list)
    print "\n ---------After killed job list: ", zombie_job_list
    len2 = len(zombie_job_list)
    print "\n ---------After killed job list length: ", len2
    
    time.sleep(2)
    sceen_shot_name = screenShotPath + "/After_kill_jobs_screen_shot.png"
    browser.save_screenshot(sceen_shot_name)
    browser.quit()
    
    if len2 < len1:
        job_to_be_kill_indicate = 1
    return job_to_be_kill_indicate
    

def get_element_name(browser, element_pattern):
    element_name = ""
    try:
        element = browser.find_element_by_xpath(element_pattern)
        element_name = element.text
    except Exception, e:
        print "element not exist any more!!!!!"
        element_name = ""

    return element_name

def get_duration_time(timeStr):
    if timeStr is None or timeStr == "":
        return 0
    if re.match(r"\d{2}:\d{2}:\d{2}", timeStr) is None:
        return 0

    timeSec = int(timeStr[0:2]) * 3600 + int(timeStr[3:5]) * 60 + int(timeStr[6:8])

    return timeSec

def send_kill_jobs_mail(mailer, screenShotPath, url, indicator):
    # jobs screen before and after kill
    mailTitle = "Kill_Zombie_Jobs_On_%s"  %url
    screenShotFile1 = screenShotPath + "/Before_kill_jobs_screen_shot.png"
    screenShotFile2 = screenShotPath + "/After_kill_jobs_screen_shot.png"
    logFile = screenShotPath + "/nodes_hanging.log"
    command = 'mail -a ' + screenShotFile1 + ' -a ' + screenShotFile2 + ' -s ' + mailTitle + mailer +  ' < ' + logFile
    print "command: ", command 
    os.system(command)

    return 0

def get_zombie_job_list(job_name_list):
    print "list1: ", job_name_list['list1']
    print "list2: ", job_name_list['list2']
    print "list3: ", job_name_list['list3']
    job_list = []
    if (not job_name_list) or (not job_name_list['list1']) or (not job_name_list['list2']) or (not job_name_list['list3']):
        return job_list
    else:
        for job in job_name_list['list1']:
            if (job in job_name_list['list2']) and (job in job_name_list['list3']):
                job_list.append(job)
    
    return job_list

def kill_jobs_in_list(browser, zombie_job_list):
    if (not browser) or (not zombie_job_list):
        return 0
        
    jobs_name_pattern_0 = "//body/div[2]/div[2]/div/div[4]/div/div[3]/div/div[4]/div/div[2]/div/div[2]/div/div/div/div[3]/table[2]/tbody/tr[1]/td/fieldset/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr/td[1]"
    jobs_name_pattern = "//body/div[2]/div[2]/div/div[4]/div/div[3]/div/div[4]/div/div[2]/div/div[2]/div/div/div/div[3]/table[2]/tbody/tr[1]/td/fieldset/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr[Order]/td[1]"
    jobs_kill_pattern_0 = "//table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr/td[3]/div/button"
    jobs_kill_pattern = "//body/div[2]/div[2]/div/div[4]/div/div[3]/div/div[4]/div/div[2]/div/div[2]/div/div/div/div[3]/table[2]/tbody/tr[1]/td/fieldset/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr[Order]/td[3]/div/button"
    jobs_duration_pattern = "//body/div[2]/div[2]/div/div[4]/div/div[3]/div/div[4]/div/div[2]/div/div[2]/div/div/div/div[3]/table[2]/tbody/tr[1]/td/fieldset/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr[Order]/td[5]"

    for i in range(0, 5):    
        job_name_elements_list = browser.find_elements_by_xpath(jobs_name_pattern_0)
        job_length = len(job_name_elements_list)
        
        for index in range(1, job_length+1):
            job_name_pattern = jobs_name_pattern.replace("Order", str(index))
            job_kill_pattern = jobs_kill_pattern.replace("Order", str(index))
            job_duration_pattern = jobs_duration_pattern.replace("Order", str(index))
            job_name = get_element_name(browser, job_name_pattern)
            job_duration_time = get_duration_time(get_element_name(browser, job_duration_pattern))
            
            if (job_name in zombie_job_list) and (job_duration_time == 0):
                print "This job should be killed: ", job_name
                try:
                    kill_button_element = browser.find_element_by_xpath(job_kill_pattern)
                    kill_button_element.click()
                    confirm_kill_button_pattern = "//table/tbody/tr/td/table/tbody/tr/td[1]/button"
                    
                    confirm_kill_button_element = browser.find_element_by_xpath(confirm_kill_button_pattern)
                    if confirm_kill_button_element.text == "Yes":
                        print "press button: ", confirm_kill_button_element.text
                        confirm_kill_button_element.click()
                        time.sleep(1)
                        zombie_job_list.remove(job_name)
                except Exception, e:
                    print "Confirm Yes Button does not exist any more!!!!!"
                time.sleep(0.5)
    

def monitor():
    # kill exist PhantomJS
    command = "killall phantomjs"
    print "kill all existing phantomjs: ", command
    os.system(command)
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-url', action='store', dest='url', help='data url', required=True)
    parser.add_argument('-screenShotPath', action='store', dest='screenShotPath', help='the screen shot path', required=True)
    results = parser.parse_args()

    print 'DataRush URL = ', results.url
    url = results.url
    print 'Screen Shot Path  = ', results.screenShotPath
    screenShotPath = results.screenShotPath

    mailer = get_mail_receiver()

    print "START: Monitor DataRush Starting.............................." 
    
    job_killed_inicate = kill_zombie_jobs(screenShotPath, url)

    if job_killed_inicate == 1:
        print "zombie jobs has been killed!!!!!!!"
        send_kill_jobs_mail(mailer, screenShotPath, url, 1)
    else:
        pass

    print "End: Monitor Finished....................................." 

if __name__ == '__main__':
    monitor()
    
   
   
