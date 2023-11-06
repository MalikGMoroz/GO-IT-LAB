from datetime import datetime, timedelta

def get_birthdays_per_week(users):
    today = datetime.now()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)

    birthdays = {"Monday": [], "Tuesday": [], "Wednesday": [], "Thursday": [], "Friday": []}

    for user in users:
        name = user["name"]
        birthday = user["birthday"]

        birthday_this_year = birthday.replace(year=today.year)

        if start_of_week <= birthday_this_year <= end_of_week:
            weekday = birthday_this_year.strftime("%A")

            if weekday in ["Saturday", "Sunday"]:
                weekday = "Monday"

            birthdays[weekday].append(name)

    for day, names in birthdays.items():
        if names:
            print(f"{day}: {', '.join(names)}")

test_users = [
    {"name": "Alice", "birthday": datetime(1990, 11, 8)},
    {"name": "Bob", "birthday": datetime(1985, 11, 10)},
    {"name": "Carol", "birthday": datetime(1975, 11, 9)},
    {"name": "Dave", "birthday": datetime(1982, 11, 7)},
]

get_birthdays_per_week(test_users)
