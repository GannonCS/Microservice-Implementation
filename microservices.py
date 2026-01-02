import os
from email_validator import validate_email, EmailNotValidError
import schedule
import time
import threading
from datetime import datetime, timedelta, date
import time
import tzlocal
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

user_number = None
email = None
random_quote = None
current_time_zone = None

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
scheduler_thread.start()

def main():
    next_screen = "home"
    while True:
        if next_screen == "home":
            next_screen = home_screen()
        elif next_screen == "create_simple":
            next_screen = create_task_simple()
        elif next_screen == "create_advanced":
            next_screen = create_task_advanced()
        elif next_screen == "help":
            next_screen = help_page()
        elif next_screen == "check_off":
            next_screen = check_off()
        elif next_screen == "delete":
            next_screen = delete()
        elif next_screen == "configure":
            next_screen = configuration_page()
        elif next_screen == "save_quote":
            next_screen = save_quote()
        elif next_screen == "quit":
            break

def home_screen():
    clear_terminal()
    print("Welcome to the To Do List App!") #Intro text
    print("\n")
    print("Listed below are the options to complete tasks in the app.")
    print("\n")
    print(f"Random quote: {random_quote}")
    print("\n")
    print("Create and keep track of all the things you need to do!")
    print("Also included email reminders for when you miss things that are time sensitive!")
    print("Please note that email notifications only work when the notification microservice is running and this app is running. \nRecurring tasks only work when the app is running.")
    print("\n")
    print("Enter 0 to go to the email configuration page.")
    print("Enter 1 to go to the create a new task page with questions & sample answers. (Recommended for New Users)")
    print("Enter 2 to go to the create a new task page. (Recommended for Experienced Users)")
    print("Enter 3 to go to the checking items off page.")
    print("Enter 4 to go to the delete items page.")
    print("Enter 5 to save the random quote into save dictionary entry microservice.")
    print("Enter 9 to quit.")
    print("\n")

    while True:
        while True:
            user_input = input("Enter Where You Would Like to Go: ")
            try:
                user_input_int = int(user_input)
                break
            except ValueError:
                continue
        if user_input_int == 0:
            return "configure"
        if user_input_int == 1:
            return "create_simple"
        if user_input_int == 2:
            return "create_advanced"
        if user_input_int == 3:
            return "check_off"
        if user_input_int == 4:
            return "delete"
        if user_input_int == 5:
            return "save_quote"
        if user_input_int == 9:
            return "quit"

def create_task_simple():
    clear_terminal()

    task_time = None
    am_pm = None
    reminder = None
    recurring = None
    priority = None

    print("Create New To Do List Item Page (Simplistic)")
    print("\n")
    print("Enter 1 to continue")
    print("Enter 2 for more information/help.")
    print("Enter 3 to return to the homescreen.")
    print("\n")

    while True:
        while True:
            user_input = input("Enter What You Want to Do: ")
            try:
                user_input_int = int(user_input)
                if user_input_int == 1:
                    break
                if user_input_int == 2:
                    return "help"
                if user_input_int == 3:
                    return "home"
            except ValueError:
                continue
    
        print("\n")
        name = input("What's the Name of the To Do List Item: ")

        while True:
            time_option = input("Do you want a time associated with this item? y or n: ")
            if time_option == "y" or time_option == "Y":
                while True:
                    task_time = input("What time do you want to be associated with it? (HH:MM): ")
                    if validate_time(task_time) == True:
                        break

                while True:
                    am_pm = input("AM or PM?: ")
                    if am_pm == "AM" or am_pm == "am":
                        while True:
                            time_zone_check = input(f"Is the timezone entered in the current time zone: {current_time_zone.key}? (y/n): ")
                            if time_zone_check == 'y' or time_zone_check == 'Y':
                                break
                            if time_zone_check == 'n' or time_zone_check == 'N':
                                while True:
                                    check_request_convert = input("Do you want to convert that to the current time zone via the time-converter microservice? (y/n): ")
                                    if check_request_convert == 'y' or check_request_convert == 'Y':
                                        output = convert_time_zone(task_time, am_pm)
                                        task_time = output[0].strip()
                                        am_pm = output[1].strip()
                                        clear_terminal()
                                        break
                                    if check_request_convert == 'n' or check_request_convert == 'N':
                                        break
                        break
                    if am_pm == "PM" or am_pm == "pm":
                        while True:
                            time_zone_check = input(f"Is the timezone entered in the current time zone: {current_time_zone.key}? (y/n): ")
                            if time_zone_check == 'y' or time_zone_check == 'Y':
                                break
                            if time_zone_check == 'n' or time_zone_check == 'N':
                                while True:
                                    check_request_convert = input("Do you want to convert that to the current time zone via the time-converter microservice? (y/n): ")
                                    if check_request_convert == 'y' or check_request_convert == 'Y':
                                        output = convert_time_zone(task_time, am_pm)
                                        task_time = output[0].strip()
                                        am_pm = output[1].strip()
                                        break
                                    if check_request_convert == 'n' or check_request_convert == 'N':
                                        break
                                break
                        break
                    break 
                while True:
                    reminder = input("Do you want an email reminder for this task? y or n: ")
                    if reminder == "y" or reminder == "Y":
                        # Send an email
                        if email == None and user_number == None:
                            while True:
                                user_input = input("No email configured. Would you like to configure one? y/n: ")
                                if user_input == "y" or user_input == "Y":
                                    return "configure"
                                if user_input == "n" or user_input == "N":
                                    reminder = "n"
                                    break
                            if reminder == "n":
                                break
                        hour, minute = map(int, task_time.split(':'))
                        if am_pm.lower() == "pm" and hour != 12:
                            hour += 12
                        if am_pm.lower() == "am" and hour == 12:
                            hour = 0
                        full_time = f"{hour:02d}:{minute:02d}"
                        schedule.every().day.at(f"{full_time}").do(lambda name=name, task_time=task_time, am_pm=am_pm: check_status(name,task_time,am_pm))
                        break
                    if reminder == "n" or reminder == "N":
                        break
                break
            if time_option == "n" or time_option == "N":
                break
        
        while True:
            recurring = input("Is this a recurring task occuring everyday? y or n: ")
            if recurring == "y" or recurring == "Y":
                break
            if recurring == "n" or recurring == "N":
                break
        
        while True:
            priority = input("What's the priority of this task? low, medium, high: ")
            if priority == "low" or priority == "Low" or priority == "LOW":
                break
            if priority == "medium" or priority == "Medium" or priority == "MEDIUM":
                break
            if priority == "high" or priority == "High" or priority == "HIGH":
                break
        
        if task_time != None and (recurring == "y" or recurring == "Y"):
                print("You Entered Name:", name, "Time:", task_time, am_pm, "Email Reminder:", reminder, "Recurring:", recurring, "Priority:", priority)
        
        elif task_time != None and (recurring == "n" or recurring == "N"):
                print("You Entered Name:", name, "Time:", task_time, am_pm, "Email Reminder:", reminder, "Priority:", priority)

        elif (recurring == "y" or recurring == "Y") and task_time is None:
            print("You Entered Name:", name, "Recurring:", recurring, "Priority:", priority)

        elif (recurring == "n" or recurring == "N") and task_time is None:
            print("You Entered Name:", name, "Priority:", priority)
        
        print("\n")
        while True:
            confirm = input("Look Correct? y or n: ")
            if confirm == "y" or confirm == "Y":
                break
            if confirm == "n" or confirm == "N":
                return "create_simple"
        
        check_box = "\u2610 "

        with open("list.txt", "a") as f:
            if task_time != None and (recurring == "y" or recurring == "Y"):
                f.write(f"{check_box} {name}, {task_time}, {am_pm}, {reminder}, ({recurring}), {priority}\n")

            elif task_time != None and (recurring == "n" or recurring == "N"):
                f.write(f"{check_box} {name}, {task_time}, {am_pm}, {reminder}, {priority}\n")

            elif (recurring == "y" or recurring == "Y") and task_time is None:
                f.write(f"{check_box} {name}, ({recurring}), {priority}\n")

            elif (recurring == "n" or recurring == "N") and task_time is None:
                f.write(f"{check_box} {name}, {priority}\n")


        print("\n")
        while True:
            another_task = input("Do you want to add another task? y or n: ")
            if another_task == "y" or another_task == "Y":
                return "create_simple"
            if another_task == "n" or another_task == "N":
                return "home"
    
def help_page():
    clear_terminal()
    print("How To Create Item Page")
    print("\n")
    print("When adding a new item, you will be guided through multiple questions.")
    print("\n")
    print("Ensure that you enter things in the format required, ex 05:30 for time or y/n.")
    print("\n")
    print("Note, the time entered must be use a 12-hour clock.")
    print("\n")
    print("Time conversion will only occur if timezone-converter microservice is running.")
    print("In the confirmation screen the timezone may appear different from what was entered if you convert it.")
    print("\n")
    print("Recurring Tasks, will be automatically unchecked off at midnight.\n At Midnight, it will uncheck.")
    print("If you delete the task it won't recur anymore.")
    print("\n")
    print("To configure the email used for email notifications,\n go to the set configuration page from Home.")
    print("Email notifications will be sent out, if an item isn't checked off at the time it was scheduled.")
    print("\n")
    print("If you need additional help please reach out at contact@email.com")
    print("\n")
    print("To go back to the Create New To List Item Page enter 1.")
    print("To go back to the Home Page Press 2")
    print("\n")

    while True:

        while True:
            user_input = input("Enter What You Want to Do: ")
            try:
                user_input_int = int(user_input)
                break
            except ValueError:
                continue
        
        if user_input_int == 1:
            return "create_simple"
        if user_input_int == 2:
            return "home"

def create_task_advanced():
    clear_terminal()

    task_time = None
    am_pm = None
    reminder = None
    recurring = None
    priority = None

    print("Create New To Do List Item Page (Advanced)")
    print("\n")
    print("Please note, inputs are not validated, and unexpected behavior might result. By continuing you accept that risk.")
    while True:
        print("\n")
        input3 = input("Enter 1 to Continue or 2 to Go Back: ")
        if int(input3) == 2:
            return "home"
        else:
            break
    print("\n")

    name = input("Name: ")
    time_option = input("Want Time: ")
    if time_option == 'y':
        task_time = input("Time: ")
        am_pm = input("AM/PM: ")
        convert = input("Convert from original time zone: ")
        if convert == 'y' or convert == 'Y':
            output_time = convert_time_zone(task_time, am_pm)
            task_time = output_time[0].strip()
            am_pm = output_time[1].strip()
        reminder = input("Email Reminder: ")
        if reminder == "y" or reminder ==  "Y":
            hour, minute = map(int, task_time.split(':'))
            if am_pm.lower() == "pm" and hour != 12:
                hour += 12
            if am_pm.lower() == "am" and hour == 12:
                hour = 0
            full_time = f"{hour:02d}:{minute:02d}"
            schedule.every().day.at(f"{full_time}").do(lambda name=name, task_time=task_time, am_pm=am_pm: check_status(name,task_time,am_pm))

    recurring = input("Recurring: ")
    priority = input("Priority: ")

    if task_time != None and (recurring == "y" or recurring == "Y"):
        print("You Entered Name:", name, "Time:", task_time, am_pm, "Email Reminder:", reminder, "Recurring:", recurring, "Priority:", priority)

    elif task_time != None and (recurring == "n" or recurring == "N"):
        print("You Entered Name:", name, "Time:", task_time, am_pm, "Email Reminder:", reminder, "Priority:", priority)

    elif (recurring == "y" or recurring == "Y") and task_time is None:
        print("You Entered Name:", name, "Recurring:", recurring, "Priority:", priority)

    elif (recurring == "n" or recurring == "N") and task_time is None:
        print("You Entered Name:", name, "Priority:", priority)
    
    print("\n")
    while True:
        confirm = input("Look Correct?: ")
        if confirm == "y" or confirm == "Y":
            break
        if confirm == "n" or confirm == "N":
            return "create_advanced"
    
    check_box = "\u2610 "

    with open("list.txt", "a") as f:
            if task_time != None and (recurring == "y" or recurring == "Y"):
                f.write(f"{check_box} {name}, {task_time}, {am_pm}, {reminder}, ({recurring}), {priority}\n")

            elif task_time != None and (recurring == "n" or recurring == "N"):
                f.write(f"{check_box} {name}, {task_time}, {am_pm}, {reminder}, {priority}\n")

            elif (recurring == "y" or recurring == "Y") and task_time is None:
                f.write(f"{check_box} {name}, ({recurring}), {priority}\n")

            elif (recurring == "n" or recurring == "N") and task_time is None:
                f.write(f"{check_box} {name}, {priority}\n")

    print("\n")
    while True:
        another_task = input("Add another?: ")
        if another_task == "y" or another_task == "Y":
            return "create_advanced"
        if another_task == "n" or another_task == "N":
            return "home"

def check_off():
    clear_terminal()
    print("Checking Items Off Page")

    while True:
        print("\n")
        input3 = input("Enter 1 to Continue or 2 to Go Back: ")
        try:
            input3_int = int(input3)
            if input3_int == 2:
                return "home"
            if input3_int == 1:
                break
        except ValueError:
            continue

    print("\n")

    check_box_ticked = "\u2611 "
    tasks = []
    count = 0

    try:
        with open("list.txt", "r") as f:
            lines = f.readlines()
            for line in lines:
                tasks.append(line.strip())
                count += 1
    except FileNotFoundError:
        print("No Items to Check Off")
        while True:
            try_again = input("Enter 1 to return home:  ")
            if try_again == "1":
                return("home")

    if count == 0:
        print("No Items to Check Off")
        while True:
            try_again = input("Enter 1 to return home:  ")
            if try_again == "1":
                return("home")

    for x in range(count):
        item = tasks[x]
        print(f"{x+1}. {item}\n")

    print("\n")
    while True:
        selection2 = input("Select Which Item You Want to Check Off as an Integer (ex: 1): ")
        try:
            selection2_int = int(selection2)
            if selection2_int > count:
                continue
            else:
                break
        except ValueError:
            continue
    
    clear_terminal()
    print("Checking Items Off Page")
    print("\n")
    # print item checked off


    check_box = "\u2610 "

    line_item = tasks[selection2_int - 1].rstrip("\n")

    line_content = line_item[1:].lstrip()

    if line_item.startswith("☐"):
        new_line = f"{check_box_ticked}{line_content}\n"
    
    else:
        new_line = f"{check_box}{line_content}\n"
    
    lines[selection2_int - 1] = new_line



    with open("list.txt", "r+") as f:
        f.seek(0)
        f.writelines(lines)
        f.truncate()
        
    print(lines[selection2_int - 1])

    print("\n")
    while True:
        input2 = input("Would you like to check off another item? y/n: ")
        if input2 == "y" or input2 == "Y":
            return "check_off"
        if input2 == "n" or input2 == "N":
            return "home"

def delete():
    clear_terminal()
    print("Deleting Items Page")

    while True:
        print("\n")
        input3 = input("Enter 1 to Continue or 2 to Go Back: ")
        try:
            input3_int = int(input3)
            if input3_int == 2:
                return "home"
            if input3_int == 1:
                break
        except ValueError:
            continue

    print("\n")

    #Loop to get all of the tasks if none, print none.
    count = 0 # Count for how many items are there.


    tasks = []
    count = 0

    try:
        with open("list.txt", "r") as f:
            lines = f.readlines()
            for line in lines:
                task = line[1:]
                tasks.append(task.strip())
                count += 1
    except FileNotFoundError:
        print("No Items to Delete")
        while True:
            try_again = input("Enter 1 to return home:  ")
            if try_again == "1":
                return("home")

    if count == 0:
        print("No Items to Delete")
        while True:
            try_again = input("Enter 1 to return home:  ")
            if try_again == "1":
                return("home")

    for x in range(count):
        item = tasks[x]
        print(f"{x+1}. {item}\n")

    print("\n")
    while True:
        selection2 = input("Select Which Item You Want to Delete as an Integer (ex: 1): ")
        try:
            selection2_int = int(selection2)
            if selection2_int > count:
                continue
            else:
                break
        except ValueError:
            continue

    print("\n")
    while True:
        confirmation = input(f"Are you sure you want to permanently delete item {selection2_int}? y/n: ")
        if confirmation == "y" or confirmation == "Y":
            break
        if confirmation == "n" or confirmation == "N":
            return "delete"

    clear_terminal()
    print("Deleting Items Page")
    print("\n")

    with open("list.txt", "r+") as f:
        lines = f.readlines()
        del lines[selection2_int - 1]
        f.seek(0)
        f.writelines(lines)
        f.truncate()

    print(f"Item {selection2_int}, Successfully Deleted.")

    print("\n")
    while True:
        input2 = input("Would you like to delete another item? y/n: ")
        if input2 == "y" or input2 == "Y":
            return "delete"
        if input2 == "n" or input2 == "N":
            return "home"


def check_status(name, task_time, am_pm):
    try:
        with open("list.txt", "r") as f:
            for line in f:
                if name in line and task_time in line and am_pm in line:
                    if line.startswith("☐"):
                        send_email()
        return
    except FileNotFoundError:
        return

def save_quote():
    # Save the quote of the day into the save dictionary microservice later
    clear_terminal()
    global random_quote
    print("Save Quote Page")
    print("\n")
    while True:
        save_check = input("Would you like to save todays quote? (y/n): ")
        if save_check == 'y' or save_check == 'Y':
            break
        if save_check == 'n' or save_check == 'N':
            return "home"
    with open("microservices/saving-dictionary-entries/save-dict.txt", "w") as f:
        print(f"Microservice 3 - Sent '{random_quote}\n'")
        f.write(f"{random_quote}\n")
    time.sleep(2)

    with open("microservices/saving-dictionary-entries/dictionary-output.txt", "r") as output:
        output_id = output.read().strip()
        print(f"Microservice 3 - Received '{output_id}")
    

    clear_terminal()
    print("Save Quote Page")
    print("\n")
    print(f"Quote, {random_quote} Successfully Saved. with unique id {output_id} in saving-dictionary-entries database text file.")
    while True:
        input2 = input("Go Home? y/n: ")
        if input2 == "y" or input2 == "Y":
            return "home"
        if input2 == "n" or input2 == "N":
            return "save_quote"


def get_random_quote():
    global random_quote
    with open("microservices/random-quote/quote-command.txt", "w") as f:
        print("Microservice 4 - Sent 'random\n'")
        f.write("random\n")
    time.sleep(2)
    try:
        with open("microservices/random-quote/quote-return.txt", "r") as file:
            random_quote = file.read()
            print(f"Microservice 4 - Received {random_quote}")
        return random_quote
    except FileNotFoundError:
        random_quote = "Quote-return.txt not found. Check to ensure random-quote microservice is running."
        return random_quote




def validate_time(task_time):
    if len(task_time) == 5 and task_time[2] == ":":
        try:
            hour = int(task_time[:2])
            minute = int(task_time[3:])
        except ValueError:
            return False
        if hour < 1 or hour > 12:
            return False
        if minute < 0 or minute > 59:
            return False
        else:
            return True
    else:
        return False
    

def configuration_page():
    clear_terminal()
    global user_number
    global email
    print("Email Configuration")
    print("\n")

    if user_number == None:
        while True:
            mail = input("Please enter an email for notifications: ")
            email_check = validate_email_address(mail)
            if email_check == True:
                email = mail
                break
            else:
                continue


    else:
        while True:
            option = input("Would you like to change the email on file? y/n: ")
            if option == "y" or option == "Y":
                mail = input("Please enter an email for notifications: ")
                email_check = validate_email_address(mail)
                if email_check == True:
                    email = mail
                    user_number = None
                    break
                else:
                    continue
            if option == "n" or option == "N":
                return "home"
    
    clear_terminal()
    print("Email Configuration")
    print("\n")
    print(f"Email, {email} Successfully Saved. ")
    print("\n")
    while True:
        input2 = input("Go Home? y/n: ")
        if input2 == "y" or input2 == "Y":
            return "home"
        if input2 == "n" or input2 == "N":
            return "configure"
                
def validate_email_address(mail):
    try:
        emailinfo = validate_email(mail, check_deliverability=True)
        mail = emailinfo.normalized
        return True
    except EmailNotValidError as error:
        print(str(error))
        return False
    

def convert_time_zone(task_time, am_pm):
    global current_time_zone
    clear_terminal()
    print("Time Conversion Page")
    print("\n")
    print("Entered times need to be in IANA timezone format. Check the List of tz database time zones Wikipedia for your time zone.")
    time_to_convert = f"{task_time} {am_pm}"
    format = "%I:%M %p"
    converted_time_formatted = datetime.strptime(time_to_convert, format)
    while True:
        check_valid = input(f"Enter original time zone to convert to {current_time_zone.key}: ")
        try:
            ZoneInfo(check_valid.strip())
            final_time_date = datetime.combine(date.today(), converted_time_formatted.time())
            break
        except ZoneInfoNotFoundError:
            continue

    with open("microservices/timezone-converter/time-converter-requests.txt", "w") as f:
        print(f"Microservice 2 - Sent '{final_time_date},{check_valid.strip()},{current_time_zone.key}\n'")
        f.write(f"{final_time_date},{check_valid.strip()},{current_time_zone.key}\n")
    
    time.sleep(2)

    with open("microservices/timezone-converter/time-converter-response.txt", "r") as file:
        file_contents = file.read().strip()
        print(f"Microservice 2 - Received '{file_contents}'")
    
    output_date_time = datetime.fromisoformat(file_contents)

    time_string = output_date_time.strftime("%I:%M")
    am_pm_string = output_date_time.strftime("%p")

    return time_string, am_pm_string


def send_email():
    # calls the notification microservice.
    global email
    global user_number
    with open("microservices/notification/notification-microservice.txt", "a") as f:
        command = "send-email"
        subject = "Task Missed - To Do List App"
        message = "You missed a scheduled task! Check the app to see what you missed!"
        if user_number is not None:
            print(f"Microservice 1 - Sent '{command},{user_number},{subject},{message}\n'")
            f.write(f"{command},{user_number},{subject},{message}\n")
            check_send_email_response()
        elif email is not None:
            print(f"Microservice 1 - Sent '{command},{email},{subject},{message}\n'")
            f.write(f"{command},{email},{subject},{message}\n")
            time.sleep(3)
            check_send_email_response()
        else:
            print("No email or usernumber detected unable to send email.")

def check_send_email_response():
    # Checks to see if email was sent succesfully
    global email
    global user_number
    time.sleep(5)
    try:
        with open("microservices/notification/confirm-text.txt", "r") as f:
            format = "%Y-%m-%d %H:%M:%S"
            lines = f.readlines()
            last_line = None
            for line in reversed(lines):
                if line.strip():
                    last_line = line
                    break
            
            if last_line == None:
                return
            
            if user_number == None:
                line_data = last_line.split(',')
                recorded_email = line_data[2]
                if recorded_email == email:
                    recorded_user_number = int(line_data[1])
                    user_number = recorded_user_number
                    email = None
                    status = line_data[0]
                    if status == "valid":
                        print(f"Microservice 1 - Received {status}")
                        return
                    if status == "invalid":
                        print("Email not sent, notification microservice recorded invalid status.")
                        return
            elif email == None:
                line_data = last_line.split(',')
                recorded_user_number = int(line_data[1])
                if recorded_user_number == user_number:
                    status = line_data[0]
                    if status == "valid":
                        print(f"Microservice 1 - Received {status}")
                        return
                    if status == "invalid":
                        print("Email not sent, notification microservice recorded invalid status.")
                        return
    except FileNotFoundError:
        print("confirm-text.txt not found. Check to ensure notification microservice is running.")

def recurring_tasks():
    valid1 = "(y)"
    valid2 = "(Y)"
    check_box = "\u2610 "
    recurring_list = []
    try:
        with open("list.txt", "r") as f:
            lines = f.readlines()
        updated_lines = []
        for line in lines:
            if valid1 in line or valid2 in line:
                if line.startswith("☑"):
                    line_content = line[1:].lstrip()
                    updated_lines.append(f"{check_box}{line_content}")
            else:
                updated_lines.append(line)

        with open("list.txt", "w") as f2:
            f2.writelines(updated_lines)    
        return
    except FileNotFoundError:
        return

def clear_terminal():
    if os.name == "nt":
        os.system('cls')
    else:
        print("\033c", end="")

schedule.every().day.at("00:00").do(recurring_tasks)

def init():
    global random_quote
    global current_time_zone
    random_quote = get_random_quote()
    time.sleep(10)
    current_time_zone = tzlocal.get_localzone()

init()

if __name__ == "__main__":
    main()