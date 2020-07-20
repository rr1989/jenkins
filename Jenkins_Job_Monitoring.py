#!/usr/bin/env python
# coding: utf-8

# # Jenkins Job Monitoring Script

# #### @author: Rakesh.Ranjan
# Created on Wed Jun 17 22:14:40 2020
# Updated on Tue Jun 30 15:53:55 2020

# ### Import Lib

# In[37]:


import os
import pandas as pd
import requests
import json
import datetime as dt
from colorama import Fore, Back, Style
import time
import concurrent.futures


# In[38]:


#timestamp
timstamp = dt.datetime.now()
print(timstamp)


# In[39]:


#current directory
print(os.getcwd())


# #### index starts from 0. Find the position of your team name and assign the correct value to variable - 'i'

# In[40]:


sc_team_name = ['DT%20-%20Accountable%20Gladiators', 'DT%20-%20DeltaForce', 'DT%20-%20Disruptors', 'DT%20-%20Transformers', 'DT-Chargers', 'DT-Equalizers', 'DT-OMG', 'DT-PayTheMan', 'DT-Req2Check']
sc_team_name


# #### Enter index of your Scrum Team.#'DT-Chargers' is placed at 5 th position.So its index is 5 - 1 = 4 

# In[41]:


i = 6 #7 #for Pay the man # 5 for Equalizers # 4 for CHargers 


# In[42]:


scrum_team_name = sc_team_name[i]


# In[43]:


scrum_team_name


# ### Fetch last N build details

# In[44]:


fetch_N_last_Jobs = 2


# ### Storing extract into below mentioned excel files. 

# In[45]:


#Failed_Jenkins_Job_filename = scrum_team_name + '_' + 'Failed_Jenkins_Job_stage' + '_' + str(timstamp).replace(' ', '_').replace(':', '-') + '.xlsx'
jenkins_job_file_name = scrum_team_name + '_' + 'Jenkins_Job' + '_' + str(timstamp).replace(' ', '_').replace(':', '-') + '.xlsx'
stage_Jenkins_Job_file_name = scrum_team_name + '_' + 'stage_Jenkins_Job' + '_' + str(timstamp).replace(' ', '_').replace(':', '-') + '.xlsx'
dev_Jenkins_Job_file_name = scrum_team_name + '_' + 'dev_Jenkins_Job' + '_' + str(timstamp).replace(' ', '_').replace(':', '-') + '.xlsx'


# ### creating an empty dataframe for storing summary of Jenkins Jobs

# In[46]:


column_names = ["test_id", "fullDisplayName", "buildNumber", "result", "instance_name","virtualMachine", "buildURL", "testComplete_or_console_ErrMessage", "testCompleteURL", "consoleLogPage"]
df_Jenkins_Aut_job = pd.DataFrame(columns = column_names)


# ### command to extract all test folders of the respective SCRUM TEAM

# In[47]:


scrum_team_url = 'https://testwin.epfin.coxautoinc.com/view/' + scrum_team_name + '/api/json'
resp_tc_folder = requests.get(scrum_team_url)
resp_tc_folder


# ### Find Total number of Test Folders  

# In[48]:


test_folder_count = len(resp_tc_folder.json()['jobs'])
print('test_folder_count:',test_folder_count)


# ### display test folder name 

# In[49]:


for i in range(test_folder_count):
    print(resp_tc_folder.json()['jobs'][i]['name'])
    


# In[50]:


start = time.time()
print('execute the main logic to get build details of Jenkins test case')
for tc_fl in range(test_folder_count): 
#'O2I- Sales Tax Vertex', 'O2I - Invoice Format'etc.
  #print('test folder name:',resp_tc_folder.json()['jobs'][tc_fl]['name'])
    
  tc_folder_url = resp_tc_folder.json()['jobs'][tc_fl]['url'] + 'api/json'
  resp_tc_folder_url = requests.get(tc_folder_url)
  jsonRes = resp_tc_folder_url.json()# To get response dictionary as JSON
  
  # loop count = number of testcase inside the folder
  test_case_count = len(jsonRes['jobs'])
  #print('test_case_count:',test_case_count)

  for i in range(0,test_case_count):
     suffix = 'api/json'
     url = jsonRes['jobs'][i]['url'] + suffix
     tc_url = requests.get(url)
     color_of_tes_case = jsonRes['jobs'][i]['color']
     
     if color_of_tes_case in ['red','blue']:
         
         print(Fore.GREEN + '*********************')
         print(Style.RESET_ALL)
         
         if color_of_tes_case == 'red':
             
            print(Back.RED + 'test folder name:',resp_tc_folder.json()['jobs'][tc_fl]['name'])
            print(Style.RESET_ALL)
            print(Back.RED + 'Failed - last build for test-case name:', jsonRes['jobs'][i]['name'])
            print(Style.RESET_ALL)
         else:

            print(Back.GREEN + 'test folder name:',resp_tc_folder.json()['jobs'][tc_fl]['name'])
            print(Style.RESET_ALL)
            print(Back.GREEN + 'test-case name:', jsonRes['jobs'][i]['name'])
            print(Style.RESET_ALL)          
     
         print(Fore.GREEN + '*********************')
         print(Style.RESET_ALL) 
         #print('back to normal now') 

         df_Jenkins_Aut_job = df_Jenkins_Aut_job.append({
                   "test_id": None,
                   "fullDisplayName": None,
                   "buildNumber": None,
                   "result": None,
                   "instance_name":None,
                   "virtualMachine": None,
                   "buildURL": None,
                   "testComplete_or_console_ErrMessage": None,
                   "testCompleteURL": None,
                   "consoleLogPage":None}, ignore_index = True)    
         
         #fetching details of last 2 build details 
         if len(tc_url.json()['builds']) > 2:
             lc_builds = fetch_N_last_Jobs
         else:
             lc_builds = len(tc_url.json()['builds'])
                
         #build loop  
         for last_4_build in range(0,lc_builds):
             buildNumber_Seq = tc_url.json()['builds'][last_4_build]['number']
             buildURL_Seq = tc_url.json()['builds'][last_4_build]['url']
             
             json_url= buildURL_Seq +'api/json'
             
             #command to get details of the test case build
             tc_bulk_details = requests.get(json_url)
             
             #'********details of test case build*********'
             test_id = jsonRes['jobs'][i]['name'].split('_')[0]
             fullDisplayName = tc_bulk_details.json()['fullDisplayName']
             buildNumber = tc_bulk_details.json()['number']
             testResult = tc_bulk_details.json()['result']
             virtualMachine = tc_bulk_details.json()['builtOn']
             instance_name = virtualMachine.split('-')[0]
             buildURL = tc_bulk_details.json()['url']
             consoleTextURL = tc_bulk_details.json()['url'] + 'consoleText'
             
             #'****logic to get error message from consoletext
             try:
                 if testResult == 'FAILURE':
                   console = requests.get( buildURL + 'consoleText/api/json')
                   s = console.text
                   start = s.find("ERROR [SoapUIProTestCaseRunner]") + len("ERROR [SoapUIProTestCaseRunner]")
                   end_string = "INFO  [log] " + test_id[2: ]
                   end = s.find(end_string)
                   console_err_msg = s[start: end]
                 else:
                    console_err_msg = None  
             except:
                   console_err_msg = 'Not able to get the console error message'
                   
             # '****logic to get error_message for TestComplete Automation********'
             try:
                 if testResult == 'FAILURE':
                   test_comp_job_url = buildURL + 'TestComplete/api/json'
                   resp_test_comp_job_url = requests.get(test_comp_job_url)
                   tc_error_message = resp_test_comp_job_url.json()['reports'][0]['error']
                   test_comp_url = resp_test_comp_job_url.json()['reports'][0]['url'] 
                    
                   if tc_error_message == "":
                               start_tc = s.find("[TestComplete] [ERROR]") + len("[TestComplete] [ERROR]")
                               end_tc =  s.find("Finished: FAILURE")
                               tc_error_message = s[start_tc: end_tc]                        

                 else:
                     test_comp_job_url = buildURL + 'TestComplete/api/json'
                     resp_test_comp_job_url = requests.get(test_comp_job_url)
                     test_comp_url = resp_test_comp_job_url.json()['reports'][0]['url']
                     tc_error_message  = None      
             except:
                   tc_error_message = console_err_msg
                   test_comp_url = 'No TestComplete URL for this test case '
             finally: 
                   #populate empty dataframe to store failed job detailsand keep appending new records
                   df_Jenkins_Aut_job = df_Jenkins_Aut_job.append({
                   "test_id": test_id,
                   "fullDisplayName": fullDisplayName,
                   "buildNumber": buildNumber,
                   "result": testResult,
                   "instance_name":instance_name,
                   "virtualMachine": virtualMachine,
                   "buildURL": buildURL,
                   "testComplete_or_console_ErrMessage": tc_error_message,
                   "testCompleteURL": test_comp_url,
                   "consoleLogPage":consoleTextURL
                   }, ignore_index = True)
                   
                   if testResult == 'FAILURE':
                        print(Back.RED + 'build number:',buildNumber)
                        print(Back.RED + 'instance name:',instance_name)
                        print(Back.RED + 'tc_error_message:',tc_error_message)
                        print(Style.RESET_ALL)
                   else:
                        print(Back.GREEN + 'build number:',buildNumber)
                        print(Back.GREEN + 'instance name:',instance_name)
                        print(Back.GREEN + 'tc_error_message:',tc_error_message)
                        print(Style.RESET_ALL)
 
finish = time.time()
#print("Time taken : {} secs".format(finish - start))
print("Now execute the command to store result into flat files")                   


# ### Directory where you are storing the Jenkins Report

# In[51]:


os.chdir("C:\\Users\\Rakesh.Ranjan\\Desktop\\Manheim\\Jenkins Job Monitoring\\25-06-2020\\Jenkins Job Monitoring")
print(os.getcwd())


# In[52]:


df_Jenkins_Aut_job.to_excel(jenkins_job_file_name)
df_Jenkins_Aut_job[df_Jenkins_Aut_job['instance_name'] =='stage'].to_excel(stage_Jenkins_Job_file_name)
df_Jenkins_Aut_job[df_Jenkins_Aut_job['instance_name'] =='dev'].to_excel(dev_Jenkins_Job_file_name)
print('Open file -  ' + jenkins_job_file_name + '  to see Jenkins job details')


# In[ ]:





# In[ ]:




