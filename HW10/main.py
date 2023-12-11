import re


from collections import UserDict


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


class Record:
    def __init__(self, name, phone=''):
        self.name = name
        if phone == '':
            self.phone_numbers = []
        else:
            self.phone_numbers = [phone]

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
        phones_list = map(lambda x: x.value, self.phone_numbers)
        return f"{' '.join(phones_list)}"


class Field:
    pass


class Name(Field):
    def __init__(self, value):
        self.value = value.title()


class Phone(Field):
    def __init__(self, value):
        self.value = value


phone_book = AddressBook()

COMMANDS = ['show all', 'good bye', 'hello',
            'exit', 'close', 'add', 'change', 'phone', 'new phone', 'delete contact', 'delete phone']

DATA_FORMATS = {
    'phone': '^[+][0-9]{12}$'
}

chat_in_progress = True


def input_error(func):
    def inner_func(args):
        try:
            result = func(args)
            return result
        except IndexError:
            print(
                "Assistant: Please, type name and number (two numbers if you use 'change' command)")
        except ValueError as err:
            print(err.args[0])
            return None
    return inner_func


def check_number_validity(number):
    valid_number = re.match(DATA_FORMATS['phone'], number)
    if not valid_number:
        raise ValueError(
            "Assistant: Number should start with '+' and contain 12 digits. Please, try again")


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
def add_contact(args):
    if len(args) > 1:
        name, phone = args[0], args[1]
        check_number_validity(phone)
        new_record = Record(Name(name), Phone(phone))
    else:
        name = args[0]
        new_record = Record(Name(name))

    contact = if_contact_exists(name)

    if contact:
        return ("Assistant: contact with such name alreday exists")

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
    check_number_validity(new_number)
    contact = if_contact_exists(name)
    if not contact:
        return ("Assistant: Person with such name was not found")
    phone = Phone(new_number)
    contact.add_phone(phone)
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


def terminate_assistant():
    global chat_in_progress
    chat_in_progress = False
    return ('Assistant: Bye. See you later ;)')


def main():
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

    if bot_message:
        print(bot_message)

    if command in ['close', 'exit', 'good bye']:
        bot_message = terminate_assistant()
        print(bot_message)


while chat_in_progress:
    main()