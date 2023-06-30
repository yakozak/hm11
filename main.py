from collections import UserDict
import re
from datetime import date, datetime


class Field:
    def __init__(self, value):
        self._value = None
        self.value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        self.validate(new_value)
        self._value = new_value

    def validate(self, value):
        pass


class Name(Field):
    pass


class Phone(Field):
    PHONE_REGEX = re.compile(r"^\+?(\d{2})?\(?\d{3}\)?[\d\-\s]{7,10}$")

    def validate(self, phone):
        if not self.PHONE_REGEX.match(phone):
            raise ValueError(f"Phone number {phone} is invalid.")


class Birthday(Field):
    DATE_REGEX = re.compile(r"^\d{4}-\d{2}-\d{2}$")

    def validate(self, date_str):
        if not self.DATE_REGEX.match(date_str):
            raise ValueError(f"Invalid date format: {date_str}. Expected format: YYYY-MM-DD.")

    @property
    def value(self):
        if self._value:
            return datetime.strptime(self._value, "%Y-%m-%d").date()
        return None

    @value.setter
    def value(self, new_value):
        self.validate(new_value)
        self._value = new_value


class Record:
    def __init__(self, name, birthday=None):
        self.name = name
        self.phones = []
        self.birthday = birthday

    def add(self, phone):
        self.phones.append(phone)

    def remove(self, phone):
        self.phones.remove(phone)

    def clear_phones(self):
        self.phones.clear()

    def days_to_birthday(self):
        if self.birthday and self.birthday.value:
            today = date.today()
            next_birthday = date(today.year, self.birthday.value.month, self.birthday.value.day)
            if today > next_birthday:
                next_birthday = date(today.year + 1, self.birthday.value.month, self.birthday.value.day)
            days_left = (next_birthday - today).days
            return days_left
        return None


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def remove_record(self, name):
        self.data.pop(name, None)

    def get_all_records(self):
        return self.data.values()


def input_error(func):
    def inner(*args):
        try:
            return func(*args)
        except (IndexError, ValueError):
            return "Помилка введення. Спробуйте ще раз."
        except KeyError:
            return "Контакту з таким ім'ям не знайдено."

    return inner


class Assistant:
    def __init__(self):
        self.address_book = AddressBook()

    @input_error
    def hello(self, command_args):
        return "Привіт! Я можу допомогти Вам з наступними командами: \n" + self.list_commands()

    @input_error
    def add(self, command_args):
        name = input("Введіть ім'я для записної книги: ")
        phone = input(f"Введіть мобільний номер телефону для контакта {name}: ")
        birthday = input(f"Введіть дату народження для контакта {name} (у форматі YYYY-MM-DD): ")
        record = Record(Name(name), Birthday(birthday))
        record.add(Phone(phone))
        self.address_book.add_record(record)
        return f"Запис з ім'ям {name} та номером телефону {phone} додано."

    @input_error
    def change(self, command_args):
        name = input("Введіть ім'я контакту, номер якого хочете змінити: ")
        phone = input(f"Введіть новий номер телефону для контакта {name}: ")
        record = self.address_book[name]
        record.clear_phones()
        record.add(Phone(phone))
        return f"Для контакту {name} номер телефону оновлено."

    @input_error
    def remove_phone(self, command_args):
        name = input("Введіть ім'я контакту, з якого хочете видалити номер телефону: ")
        phone = input(f"Введіть номер телефону, який хочете видалити з контакту {name}: ")
        record = self.address_book[name]
        record.remove(Phone(phone))
        return f"Номер телефону {phone} видалено з контакту {name}."

    @input_error
    def remove_record(self, command_args):
        name = input("Введіть ім'я контакту, який хочете видалити: ")
        self.address_book.remove_record(name)
        return f"Контакт {name} видалено."

    @input_error
    def phone(self, command_args):
        name = input("Введіть ім'я контакту, номери телефону якого хочете побачити: ")
        record = self.address_book[name]
        return ", ".join([phone.value for phone in record.phones])

    @input_error
    def show_all(self, command_args):
        all_records = self.address_book.get_all_records()
        result = []
        for record in all_records:
            phones = ", ".join([phone.value for phone in record.phones])
            info = f"{record.name.value}: {phones}"
            if record.birthday and record.birthday.value:
                days_left = record.days_to_birthday()
                info += f" (Дні до дня народження: {days_left})"
            result.append(info)
        return "\n".join(result)

    @input_error
    def exit(self, command_args):
        return "До побачення!"

    COMMANDS = {
        'hello': {'handler': hello, 'description': "Список доступних команд"},
        'add': {'handler': add, 'description': "Додати новий контакт. Формат вводу: 'add' -> потім введіть ім'я -> введіть номер"},
        'change': {'handler': change, 'description': "Змінити номер телефону вже існуючого контакту. Формат вводу: 'change' -> потім введіть ім'я -> введіть новий номер"},
        'remove_phone': {'handler': remove_phone, 'description': "Видалити номер телефону існуючого контакту. Формат вводу: 'remove_phone' -> потім введіть ім'я -> введіть номер, який хочете видалити"},
        'remove_record': {'handler': remove_record, 'description': "Видалити контакт. Формат вводу: 'remove_record' -> потім введіть ім'я контакту"},
        'phone': {'handler': phone, 'description': "Показати номери телефону контакту. Формат вводу: 'phone' -> потім введіть ім'я контакту"},
        'show_all': {'handler': show_all, 'description': "Показати всі контакти і їх номери телефону"},
        'exit': {'handler': exit, 'description': "Вийти з програми"}
    }

    def list_commands(self):
        return '\n'.join([f"{name}: {params['description']}" for name, params in self.COMMANDS.items()])

    def get_command_handler(self, command):
        command = command.lower().strip()
        command_handler = self.COMMANDS.get(command, {'handler': None})['handler']
        return command_handler

    def run(self):
        while True:
            command = input("Введіть команду: ")
            handler = self.get_command_handler(command)
            if handler is None:
                print("Неправильна команда")
            else:
                response = handler(self, '')
                print(response)
                if response == "До побачення!":
                    break


if __name__ == "__main__":
    assistant = Assistant()
    assistant.run()
