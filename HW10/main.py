import re
import sys
from collections import UserDict

class Field:
    pass

class Name(Field):
    def __init__(self, name):
        self.value = name

class Phone(Field):
    def __init__(self, phone_number):
        self.value = phone_number

class Record:
    def __init__(self, name, phones=None):
        self.name = Name(name)
        self.phones = [Phone(phone) for phone in phones] if phones else []

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if p.value != phone]

    def change_phone(self, old_phone, new_phone):
        for p in self.phones:
            if p.value == old_phone:
                p.value = new_phone
                return True
        return False

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

phone_book = AddressBook()

COMMANDS = ['show all', 'good bye', 'hello', 'exit', 'close', 'add', 'change', 'phone']
DATA_FORMATS = {'phone': '^[+][0-9]{12}$'}
chat_in_progress = True

def input_error(func):
    def inner_func(args):
        try:
            result = func(args)
            return result
        except KeyError:
            print("Assistant: Please, type a name in order to find a number")
        except IndexError:
            print("Assistant: Please, type name and number")
        except ValueError as err:
            print(err.args[0])
            return None
    return inner_func

def check_number_validity(number):
    valid_number = re.match(DATA_FORMATS['phone'], number)
    if not valid_number:
        raise ValueError("Assistant: Number should start with '+' and contain 12 digits. Please, try again")

def if_contact_exists(name):
    return phone_book.data.get(name.title())

@input_error
def get_instruction(message):
    message = message.replace('You: ', '').lower()
    command_not_found = True
    for command in COMMANDS:
        if message.startswith(command):
            args = message.replace(command, '').strip().split(' ')
            command_not_found = False
            return (command, args)
    if command_not_found:
        raise ValueError(f"Assistant: Please enter a valid command: {', '.join(COMMANDS)}")

def greet():
    return 'Assistant: Hello. How can I assist you?'

def show_all_contacts():
    return "\n".join([f"Assistant: {name}: {', '.join([phone.value for phone in record.phones])}" for name, record in phone_book.items()])

@input_error
def add_contact(args):
    person_name, person_number = args[1:3]
    check_number_validity(person_number)
    if if_contact_exists(person_name):
        return "Assistant: contact with such name already exists"
    
    new_record = Record(person_name, [person_number])
    phone_book.add_record(new_record)
    return f"Assistant: New contact {person_name.title()} with number {person_number} has been successfully added"

@input_error
def get_number(args):
    contact = if_contact_exists(args[1])
    if contact:
        return f"Assistant: {', '.join([phone.value for phone in contact.phones])}"
    return "Assistant: Person with such name was not found"

@input_error
def change_number(args):
    person_name, old_number, new_number = args[1:4]
    check_number_validity(new_number)
    contact = if_contact_exists(person_name)
    if contact:
        if contact.change_phone(old_number, new_number):
            return f"Assistant: {person_name}'s number was successfully changed."
    return "Assistant: Person with such name or number was not found"

def terminate_assistant():
    global chat_in_progress
    chat_in_progress = False
    return 'Assistant: Bye. See you later ;)'

def main():
    message = input("You: ")
    command_args = get_instruction(message)
    bot_message = None

    if not command_args:
        return

    match command_args[0]:
        case 'hello':
            bot_message = greet()
        case "show all":
            bot_message = show_all_contacts()
        case "phone":
            bot_message = get_number(command_args)
        case 'add':
            bot_message = add_contact(command_args)
        case 'change':
            bot_message = change_number(command_args)

    if bot_message:
        print(bot_message)

    if command_args[0] in ['close', 'exit', 'good bye']:
       bot_message = terminate_assistant()
       print(bot_message)

while chat_in_progress:
    main()
