import math
import re
import json
import pickle

from collections import UserDict
from datetime import datetime, timedelta

class Iterable:
    def __init__(self,list):
        self.number = 3
        self.start_idx = 0
        self.current_count = 0
        self.list = list
        self.iterations = math.ceil(len(self.list)/self.number)
    def __next__(self):
       if self.current_count < self.iterations:
           part = self.list[self.start_idx:self.number+self.start_idx]
           self.start_idx += self.number
           self.current_count +=1
           return part   
       raise StopIteration


class PhoneBookIterator:
    def __init__(self, list):
        self.list = list
    def __iter__(self):
        return Iterable(self.list)

class AddressBook(UserDict):
    def search_for_record(self, name):
        contact = self.data.get(name.title(), None)
        return contact

    def add_record(self, contact):
        self.data.update({contact.name.value: contact})
        return (
            f"Assistant: New contact {contact.name.value} has been successfully added")

    def delete_record(self, name):
        deleted = self.data.pop(name.title())
        return deleted

    def show_all(self):
        return self.data
    
    def iterator(self):
        contacts_list = list(self.data.values())
        generartor = PhoneBookIterator(contacts_list)
        return generartor

    def write_to_file(self):
        with open('data.bin', 'wb') as file:
            pickle.dump(self.data, file)

    def retrive_from_file(self):
        with open('data.bin', 'rb') as file:
            is_file_empty = not bool(file.read())
            if is_file_empty:
                return
            else:
                file.seek(0)
                deserialized = pickle.load(file)
                self.data = deserialized
    def search_by_name(self, name):
        contacts = []
        for contact, record in self.data.items():
            if contact.lower().startswith(name):
                contacts.append(record)
        return contacts
        
    def search_by_number(self, num):
        contacts = []
        for contact, record in self.data.items():
            match_found = False
            for number in record.get_phone().split(" "):
                if number.startswith(num) and not match_found:
                    contacts.append(record)
                    match_found = True
        return contacts

class Record:
    def __init__(self, name, phone=None, birthday=None):
        self.name = name
        if not phone:
            self.phone_numbers = []
        else:
            self.phone_numbers = [phone]
        self.birthday = birthday

    def add_phone(self, phone):
        self.phone_numbers.append(phone)

    def edit_phone(self, phone_to_change, value):
        phone_to_edit = list(
            filter(lambda x: x.value == phone_to_change, self.phone_numbers))[0]
        phone_to_edit.value = value

    def delete_phone(self, phone):
        to_delete = list(filter(lambda x: x.value ==
                         phone, self.phone_numbers))[0]
        idx = self.phone_numbers.index(to_delete)
        self.phone_numbers.pop(idx)

    def get_phone(self):
        if not len(self.phone_numbers):
            return f"No numbers have been added to {self.name.value}'s phone list yet"
        phones_list = map(lambda x: x.value, self.phone_numbers)
        return f"{' '.join(phones_list)}"

    def days_to_birthday(self):
        today = datetime.now()
        month, year = today.month, today.year

        b_day, b_month = self.birthday.value.day, self.birthday.value.month

        if month <= b_month:
            b_year = year
        else:
            b_year = year + 1
        days_left = datetime(day=b_day, month=b_month, year=b_year) - today
        return days_left.days

    def add_birthday(self, date):
        if self.birthday:
            return None
        else:
            self.birthday = date
            return date


class Field:
    pass


class Name(Field):
    def __init__(self, value):
        self.value = value.title()


class Phone(Field):
    def __init__(self):
        self.__value = None

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, phone):
        valid_phone = re.match(DATA_FORMATS['phone'], phone)
        if not valid_phone:
            raise ValueError(
                "Assistant: Number should start with '+' and contain 12 digits. Please, try again")
        else:
            self.__value = phone


class Birthday(Field):
    def __init__(self):
        self.__value = None

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, date):
        valid_date = re.match(DATA_FORMATS['date'], date)
        if not valid_date:
            raise ValueError(
                "Assistant: Date should be of following format DD-MM-YYYY")
        else:
            [d, m, y] = date.split('-')
            self.__value = datetime(day=int(d), month=int(m), year=int(y))


phone_book = AddressBook()

COMMANDS = ['show all', 'good bye', 'hello', 'show page',
            'exit', 'close', 'add', 'change', 'phone', 'new phone', 'delete contact', 'delete phone', 'birthday', 'set birthday', 'search by name', 'search by number']

DATA_FORMATS = {
    'phone': '^[+][0-9]{12}$',
    'date': '^[0-9]{2}-[0-9]{2}-[0-9]{4}$'
}

chat_in_progress = True


def input_error(func):
    def inner_func(args):
        try:
            result = func(args)
            return result
        except IndexError:
            print(
                "Assistant: Please, type name and number/date (two numbers if you use 'change' command)")
        except ValueError as err:
            print(err.args[0])
            return None
    return inner_func


def check_number_validity(number):
    phone = Phone()
    phone.value = number
    return phone


def check_date_validity(date):
    birthday = Birthday()
    birthday.value = date
    return birthday


def if_contact_exists(name):
    contact = phone_book.search_for_record(name)
    return contact


def if_phone_exists(name, phone):
    contact = phone_book.search_for_record(name)
    if_exists = bool(
        len(list(filter(lambda x: x.value == phone, contact.phone_numbers))))
    return if_exists


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
        raise ValueError(
            f"Assistant: Please enter a valid command: {', '.join(COMMANDS)}")


def greet():
    return ('Assistant: Hello. How can I assist you?')


def show_all_contacts():
    contacts_list = []
    contacts = phone_book.show_all()
    for contact, data in contacts.items():
        if not len(data.phone_numbers):
            contacts_list.append(f"\t{contact}: No numbers added yet\n")
        else:
            contacts_list.append(f"\t{contact}: {data.get_phone()}\n")
    return "\n" + " ".join(contacts_list)

@input_error
def show_phonebook_by_page(args):
    if args[0] == "":
        raise ValueError("Assistant: Please type your page number")
    number_of_page = int(args[0])
    pages_generator = phone_book.iterator()
    pages = list(pages_generator)
    page = number_of_page - 1
    if page <= len(pages)-1:
        contacts = pages[number_of_page - 1]
        res ='\t\n'
        for contact in contacts:
            if not len(contact.phone_numbers):
                res += f"\t{contact.name.value}: No numbers added yet\n"
            else:
                res += (f"\t{contact.name.value}: {contact.get_phone()}\n")
        return res   
    raise ValueError(f"Assitant: This page number is out of range. Phone Book has only {len(pages)} page(s)")
    


@input_error
def add_contact(args):
    if len(args) > 1:
        name, phone = args[0], args[1]
        contact_phone = check_number_validity(phone)
        new_record = Record(Name(name), contact_phone)
        if len(args) > 2:
            name, phone, birthday = args[0], args[1], args[2]
            contact_phone = check_number_validity(phone)
            birthday_date = check_date_validity(birthday)
            new_record = Record(Name(name), contact_phone, birthday_date)
    else:
        name = args[0]
        new_record = Record(Name(name))

    contact = if_contact_exists(name)

    if contact:
        return ("Assistant: contact with such name already exists")

    message = phone_book.add_record(new_record)

    return (f"{message}")


@input_error
def get_number(args):
    name = args[0]
    if not name:
        raise ValueError(
            "Assistant: Please, type a name in order to find a number")
    contact = phone_book.search_for_record(name)

    if not contact:
        return ("Assistant: Person with such name was not found")
    phone_numbers = contact.get_phone()

    return f"\n\t{phone_numbers}\n"


@input_error
def change_number(args):
    name, old_number, new_number = args[0], args[1], args[2]
    contact = if_contact_exists(name)
    if not contact:
        return ("Assistant: Person with such name was not found")

    phone_exists = if_phone_exists(name, old_number)
    if not phone_exists:
        return f"Assistant: Such number {old_number} doesn't exist in {name}'s phone list"

    check_number_validity(new_number)
    contact.edit_phone(old_number, new_number)

    return (
        f"Assistant: {name.title()}'s number {old_number} was successfully changed to {new_number}.")


@input_error
def add_number(args):
    name, new_number = args[0], args[1]
    new_phone = check_number_validity(new_number)
    contact = if_contact_exists(name)
    if not contact:
        return ("Assistant: Person with such name was not found")
    contact.add_phone(new_phone)
    return f"Assistant: New number {new_number} was added to {name.title()}'s phone numbers list"


@input_error
def delete_contact(args):
    name = args[0].title()
    contact = if_contact_exists(name)
    if contact:
        phone_book.delete_record(name)
        return f"Assistant: Contact {name} was succesfully deleted"
    else:
        return f"Assistant: Contact with {name} was not found"


@input_error
def delete_number(args):
    name, phone = args[0], args[1]
    contact = if_contact_exists(name)
    if not contact:
        return ("Assistant: Person with such name was not found")

    phone_exists = if_phone_exists(name, phone)
    if not phone_exists:
        return f"Assistant: Such number {phone} doesn't exist in {name}'s phone list"

    contact.delete_phone(phone)
    return (f"Assistant: Number {phone} was deleted from {name.title()}'s phone list")


@input_error
def get_birthday(args):
    name = args[0]
    contact = phone_book.search_for_record(name)
    if not contact.birthday:
        return f"Assistant: There has been no birthday data added for {contact.name.value} yet"
    birth_date = contact.birthday.value.date()
    days_to_birthday = contact.days_to_birthday()
    if days_to_birthday == 0:
        return f"Assistant: {contact.name.value}'s birtday is today. {contact.name.value} was born on {birth_date}"
    return f"Assistant: {contact.name.value}'s birtday is in {days_to_birthday} days. {contact.name.value} was born on {birth_date}"

@input_error
def add_birthday(args):
    name, date = args[0], args[1]
    contact = if_contact_exists(name)
    birthday = Birthday()
    birthday.value = date
    added_date = contact.add_birthday(birthday) 
    if added_date:
        return f"Assistant: Date {date} was successfully set as {contact.name.value}'s birthday"
    return f"Assistant: {contact.name.value} already has his birthday set as {contact.birthday.value.date()}"

@input_error
def get_records_by_name(args):
    name = args[0]
    if name == '':
        raise ValueError(
            "Assistant: Please enter a name/letters")
    contacts = phone_book.search_by_name(name) 
    if len(contacts):
        message = "\n"
        for contact in contacts:
            message += f"\t{contact.name.value}: {contact.get_phone()}\n"
        return message    
    else:
        return "Assistant: contact with such name doesn't exist"

@input_error
def get_records_by_number(args):
    number = args[0]
    if number == "+" or number == "":
        raise ValueError(
            "Assistant: Please enter a number/digits")
    valid_num = re.match('^[0-9]+$', number) or re.match('^[+][0-9]+$', number)
    if valid_num:
        if not number.startswith('+'):
            number = "+" + number
    contacts = phone_book.search_by_number(number)
    if len(contacts):
        message = "\n"
        for contact in contacts:
            numbers = " ".join(list(filter(lambda x: x.startswith(number), contact.get_phone().split(" "))))
            message += f"\t{contact.name.value}: {numbers}\n"
        return message
    else:
        return "Assistant: contact with such number doesn't exist"

def terminate_assistant():
    global chat_in_progress
    chat_in_progress = False
    return ('Assistant: Bye. See you later ;)')


def main():
    phone_book.retrive_from_file()
    message = input("You: ")
    command_args = get_instruction(message)
    bot_message = None

    if not command_args:
        return

    command, args = command_args

    match command:
        case 'hello':
            bot_message = greet()
        case "show all":
            bot_message = show_all_contacts()
        case "phone":
            bot_message = get_number(args)
        case 'add':
            bot_message = add_contact(args)
        case 'change':
            bot_message = change_number(args)
        case 'new phone':
            bot_message = add_number(args)
        case 'delete contact':
            bot_message = delete_contact(args)
        case "delete phone":
            bot_message = delete_number(args)
        case "birthday":
            bot_message = get_birthday(args)
        case "set birthday":
            bot_message = add_birthday(args)
        case 'show page':
            bot_message = show_phonebook_by_page(args)
        case 'search by name':
            bot_message = get_records_by_name(args)
        case 'search by number':
            bot_message = get_records_by_number(args)

    if bot_message:
        print(bot_message)

    phone_book.write_to_file()
    
    if command in ['close', 'exit', 'good bye']:
        bot_message = terminate_assistant()
        print(bot_message)


while chat_in_progress:
    main()