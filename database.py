import json
import os
import re
import hashlib


class Database:
    def __init__(self, db_file="lovedove.json"):
        self.db_file = db_file
        self.data = self._load_data()

    def _load_data(self):
        if os.path.exists(self.db_file):
            with open(self.db_file, "r") as f:
                return json.load(f)
        return {"users": {}, "interests": {}}

    def _save_data(self):
        with open(self.db_file, "w") as f:
            json.dump(self.data, f, indent=2)

    def _generate_key(self, firstname, lastname):
        cleaned_first = re.sub(r"[^A-Z]", "", firstname)
        cleaned_last = re.sub(r"[^A-Z]", "", lastname)

        key = cleaned_first + cleaned_last

        return hashlib.sha256(key.encode()).hexdigest()

    def _get_user_key(self, firstname, lastname):
        return self._generate_key(firstname, lastname)

    def create_user(self, firstname, lastname, password, email=None):
        user_key = self._get_user_key(firstname, lastname)
        if user_key in self.data["users"]:
            raise ValueError("User already exists")
        self.data["users"][user_key] = {
            "firstname": firstname,
            "lastname": lastname,
            "password": password,
            "email": email,
        }
        self._save_data()
        return user_key

    def get_user(self, firstname, lastname):
        user_key = self._get_user_key(firstname, lastname)
        return self.data["users"].get(user_key)

    def add_interest(self, firstname, lastname, target_firstname, target_lastname):
        user_key = self._get_user_key(firstname, lastname)
        target_key = self._get_user_key(target_firstname, target_lastname)

        if user_key not in self.data["interests"]:
            self.data["interests"][user_key] = []
        self.data["interests"][user_key].append(target_key)
        self._save_data()

    def check_mutual_interest(
        self, firstname, lastname, target_firstname, target_lastname
    ):
        user_key = self._get_user_key(firstname, lastname)
        target_key = self._get_user_key(target_firstname, target_lastname)

        user_interests = self.data["interests"].get(user_key, [])
        target_interests = self.data["interests"].get(target_key, [])

        return target_key in user_interests and user_key in target_interests
