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

today = datetime.now()

# Test users with relative birthdays
test_users = [
    {"name": "Alice", "birthday": today},  # Birthday today
    {"name": "Bob", "birthday": today + timedelta(days=1)},  # Birthday tomorrow
    {"name": "Carol", "birthday": today + timedelta(days=2)},  # Birthday in two days
    {"name": "Dave", "birthday": today + timedelta(days=3)},  # Birthday in three days
    # Add more users as needed
]

get_birthdays_per_week(test_users)