#!/usr/bin/python3

import pandas as pd
import os
import datetime

''' this is a tool to analize the information from the Timestation.com Api,
this tool will look into posible cenarious like Employees forgoting to clock out, 
if you clock in and out in lunch ETC'''

with open("Api_key.txt", "r") as file: #  the key From the timestation API is save in a text file 
    key_api = file.read()

class ItControl:

    ''' This is to created a custom report for each job sites, this will display the current employees'''

    def __init__(self):
        self.today_date = datetime.date.today().strftime('%Y-%m-%d')
        self.key_api = key_api
        self.code = 37
        self.location = input('Please input the Location \n\n->>>')
        self.url = f"https://api.mytimestation.com/v0.1/reports/?api_key={self.key_api}&id={self.code}&exportformat=csv"
        self.raw_data = pd.read_csv(self.url)
        self.getting_data()

    def answer_selector(self):
        '''  this funtion allows the user to select different reports from the main view.'''

        def picker(answer):

            if not answer:
                self.getting_data()
            elif answer.lower() == 'show':
                data_current.to_csv('currentEmployees.csv')
                os.startfile('currentEmployees.csv')
            elif answer.lower() =='check':
                os.system('cls')
                self.check_funtion()
            elif answer.lower() == 'duplicates':
                os.system('cls')
                self.check_duplicates()
            elif answer.lower() == 'export':
                os.system('cls')
                self.send_export_main()
            elif answer.lower() == 'posible':
                os.system('cls')
                self.posible_errors()

        print('\n--type "show"        -For current employee status  in excel') 
        print('--type "check"       -Wrong locations')
        print('--type "duplicates"  -to check for previous week hours doubles)')
        print('--type "posible"     -to check for possible erros in hours  (3 hours and 5 hours)')
        print('--type "export"      -to open this information in excel)\n')
        print('or just type "Enter" to refrest this window.')
        answer = input('--->')
        
        picker(answer)

    def getting_data(self):
        
        ''' this is the main view. in here the code analize the information.
        the code check first if the employees are currently working (In) and after that check if is in the location you previously type.
        after that created a simple report to display the information. '''

        global data_current
        filter_data_in = self.raw_data['Status'].str.contains('In')
        second_filter = self.raw_data[filter_data_in][['Name', 'Current Department', 'Primary Department', 'Device', 'Time', 'Date']]
        data_current = second_filter[(second_filter['Current Department'].str.contains(self.location))]
                   
        os.system('cls')
        print('last update on {}'.format(datetime.datetime.now().strftime('%H:%M:%S')))
        print('______________________________________________________________________________________________________________________________')
        final_data = data_current.groupby(['Device']).count()
        print(final_data['Current Department'].to_string())
        print('______________________________________________________________________________________________________________________________')
        print("total count by Devices   - {}".format(final_data['Current Department'].sum()))
        print('total Officially on site - {}'.format(data_current['Current Department'].count().sum()))
        print('______________________________________________________________________________________________________________________________')


        global last_check_in
        last_check_in = data_current[data_current['Date'] != datetime.date.today().strftime('%Y-%m-%d')]
        self.still_on_employees(last_check_in)
        self.hours_greater()
        self.answer_selector()

    def data_from_days(self, date1, date2):
        
        '''this download information from a range of dates. '''
        print(f'{date1}  -->  {date2} \n\n')
        code_42 = 42  # for regular week
        url_data_code_42 = f"https://api.mytimestation.com/v0.1/reports/?api_key={self.key_api}&Report_StartDate={date1}&Report_EndDate={date2}&id={code_42}&exportformat=csv"
        df = pd.read_csv(url_data_code_42)
        filter_data = df[df['Department'].str.contains(self.location)]
        return filter_data

    def data_from_week(self, date):
        
        '''this take the information of the week '''

        code_41 = 41  # for regular week
        url_data_code_41 = f"https://api.mytimestation.com/v0.1/reports/?api_key={self.key_api}&Report_StartDate={date}&id={code_41}&exportformat=csv"
        df = pd.read_csv(url_data_code_41)
        filter_data = df[df['Department'].str.contains(self.location)]
        return filter_data

    def hours_greater(self):
        ''' This will display in the main view if employees has hours greater that 15,
        if employees forgot to clock out the previous days this report will help to see those employees
        '''

        today = datetime.date.today()
        #last_monday = today - datetime.timedelta(days=today.weekday())
        last_monday = today - datetime.timedelta(6)
        date_41 = last_monday.strftime('%Y-%m-%d')
        
        filter_data = self.data_from_week(date_41)
        col = filter_data.iloc[:, 4:-3].columns.values
        lb = list(col)
        lb.insert(0, 'Employee')
        lb.insert(1, 'Department')
        
        #  i need to make global so i can be print from the outsite of this funtions.
        global great_hours
        great_hours = filter_data[filter_data[filter_data[col] > 15][col].notnull().any(1)][lb]
        
        if great_hours.empty:
            pass
        else:
            print('\n\nWarning ----> Please review Employees hours on timestation')
            print('______________________________________________________________________________________________________________________________')
            print(great_hours.to_string())
            print('______________________________________________________________________________________________________________________________')
            print('\n')

    def check_funtion(self):

        ''' this funtion helps to determent if employees are in the wrong locations.
        also the data is recolected separatly to allow to refresh by pressing just "Enter", this allow to check the work
        as you making correction.'''

        url = f"https://api.mytimestation.com/v0.1/reports/?api_key={self.key_api}&id={self.code}&exportformat=csv"
        raw_data = pd.read_csv(url)
        filter_data_in = raw_data['Status'].str.contains('In')
        second_filter = raw_data[filter_data_in][['Name', 'Current Department', 'Primary Department', 'Device', 'Time', 'Date']]
        data_current = second_filter[(second_filter['Current Department'].str.contains(self.location))]
        data_primary = second_filter[(second_filter['Primary Department'].str.contains(self.location))]
          
        print(f'\n\ncurrent in {self.location} from other locations')
        print('________________________________________________________________________________________')
        x = data_current[data_current['Primary Department'] != data_current['Current Department']]
        d = x.sort_values(['Device', 'Name'])
        print(" ", d.to_string(), '\n\n')

        print(f'Primary {self.location} in other locations')
        print('________________________________________________________________________________________')
        a = data_primary[data_primary['Primary Department'] != data_primary['Current Department']]
        p = a.sort_values(['Current Department', 'Name'])
        
        if p.empty:
            print('There is not information to display')    
        else:
            print(" ", p.to_string())

        print('\n\n [+] - Type "back" for main Screen or Press "Enter" to refresh --> ')
        answer = input('\nto go back press enter')

        if not answer:
            self.check_funtion()
        else:
            self.getting_data()
    
        
    def still_on_employees(self, last_check_in):

        if last_check_in.empty:
            pass
        else:
            print('\n\nWarning ----> Employees didn\'t Clock in today (He still "IN" in the system )')
            print('______________________________________________________________________________________________________________________________')
            print(last_check_in.to_string())
            print('\n')

    def gettings_date(self):
            ''' this gives the option to choose betweend the list for previous week or this week.'''
            today = datetime.date.today()
            print('For Current week press enter or pevious week type "-p" ')
            answer = input('-->')
            
            if answer.lower() == '-p' :
                last_monday  =  today - datetime.timedelta(days=today.weekday(), weeks=1)
                return last_monday.strftime('%Y-%m-%d'), None
            else:
                current_monday = today - datetime.timedelta(days=today.weekday())
                yesterday = today - datetime.timedelta(1)
                return current_monday.strftime('%Y-%m-%d'), yesterday.strftime('%Y-%m-%d')
            
    def check_duplicates(self):
  
        date1, date2 = self.gettings_date() 
        code_41 = 41  # for regular week
        url_data_code_41 = f"https://api.mytimestation.com/v0.1/reports/?api_key={self.key_api}&Report_StartDate={date1}&id={code_41}&exportformat=csv"

        raw_data = pd.read_csv(url_data_code_41)
        week_data = raw_data.iloc[:, 2:-2]
        duplicated_data = week_data.loc[week_data.Employee.duplicated(keep=False), :]
        data_filter = duplicated_data.loc[duplicated_data['Department'].str.contains(self.location), :]
       
        if data_filter.empty:
            print('There is not doubles at this time')
            input('')
        else:  
            print(data_filter.to_string())
            print('Please type "export" to send to excel')
            print('or just press enter to continue to Main window \n')
            answer = input('----> ')
            if answer.lower() == 'export':
                export_name = 'List_of_duplicates_for_{}.csv'.format(date1)
                data_filter.to_csv(export_name)
                os.startfile(export_name)
                self.getting_data()
            else:
                self.getting_data()

    def send_export_main(self):

        great_name = 'big_Hours_Of_{}.csv'.format(self.today_date)
        great_hours.to_csv(great_name)
        os.startfile(great_name)

        still_in_name = 'Still_in_employees_{}.csv'.format(self.today_date)
        last_check_in.to_csv(still_in_name)
        os.startfile(still_in_name)

    def posible_errors(self):
        
        ''' this funtion its use to check if hours are 3 or 5 , normally this horus reflects some kind of mistake'''
        
        date1, date2 = self.gettings_date()
        if not date2:
            filter_data= self.data_from_week(date1)
        else:
            filter_data = self.data_from_days(date1, date2)
        
        col = filter_data.iloc[:, 4:-3].columns.values
        lb = list(col)
        lb.insert(0, 'Employee') # this add this words to the index
        lb.insert(1, 'Department')

        small_hours = filter_data[filter_data[(filter_data[col] > 2.3) & (filter_data[col] < 3.7)][col].notnull().any(1)][lb]
        big_hours =  filter_data[filter_data[(filter_data[col] > 4.3) & (filter_data[col] < 5.7)][col].notnull().any(1)][lb]
        
        if small_hours.empty:
            pass
        else:
            print('--------------------------------------------------------------------------------------------')
            # small_hours.style.apply(lambda x: ["background: red" if v > x.iloc[0] else "" for v in x], axis = 1)
            print('small hours posible mistakes (3 hours)')
            print(small_hours.to_string())
            print('--------------------------------------------------------------------------------------------\n')
        
        if big_hours.empty:
            pass
        else:
            print('--------------------------------------------------------------------------------------------')
            print('big hours posible mistakes (5 hours)')
            print(big_hours.to_string())
            print('--------------------------------------------------------------------------------------------\n')

        print('--------------------------------------------------------------------------------------------')
        print('Please type "export" to send to excel')
        print('or just press enter to continue to Main window \n')

        answer = input('----> ')
        if answer.lower() == 'export':
            export_name = 'posibleMistakes_for_{}.csv'.format(date1)
            frames = [small_hours, big_hours]
            full_data = pd.concat(frames)
            full_data.to_csv(export_name)
            os.startfile(export_name)
            self.getting_data()
        else:
            self.getting_data()
        

if __name__ == '__main__':

    active = ItControl()





