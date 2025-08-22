"""Application controller code - Habitica To Do Over tool

App controller functions for the Habitica To Do Over tool.
For functions that don't fit in the model or views.
"""
from __future__ import absolute_import

from builtins import object
from builtins import str

__author__ = "Katie Patterson kirska.com"
__license__ = "MIT"

from datetime import datetime, timedelta
import requests
from to_do_overs.models import Users, Tags
from .cipher_functions import encrypt_text, decrypt_text


class ToDoOversData(object):
    """Session data and application functions that don't fall in models or views.

    This class will be stored in a cookie for a login session.

    Attributes:
        username (str): Username from Habitica.
        hab_user_id (str): User ID from Habitica.
        api_token (str): API token from Habitica.
        logged_in (bool): Goes to true once user has successfully logged in.
        task_name (str): The name/title of the task being created.
        task_days (int): The number of days that a task should last
            before expiring for the task being created.
        task_id (str): The created task ID from Habitica.
        priority (str): Difficulty of the task being created.
            See models.py for choices.
        notes (str): The description/notes of the task being created.
        tags (list): The user's tags.
    """

    def __init__(self):
        self.username = ""
        self.hab_user_id = ""
        self.api_token = ""
        self.logged_in = False
        self.tags = []

        self.task_name = ""
        self.task_days = 0
        self.task_delay = 0
        self.task_id = ""
        self.priority = ""
        self.type = 0
        self.weekday = 0
        self.monthday = 0
        self.notes = ""

        self.return_code = 0

    def login(self, password):
        """Login with a username and password to Habitica.

        Args:
            password: The password.

        Returns:
            True for success, False for failure.
        """
        req = requests.post(
            "https://habitica.com/api/v3/user/auth/local/login",
            data={"username": self.username, "password": password},
        )
        # print("POST: " + req.url + " [" + str(req.status_code) + "]: " + req.text)
        self.return_code = req.status_code
        if req.status_code == 200:
            req_json = req.json()
            self.hab_user_id = req_json["data"]["id"]
            self.api_token = encrypt_text(req_json["data"]["apiToken"])
            self.username = req_json["data"]["username"]

            Users.objects.update_or_create(
                user_id=self.hab_user_id,
                defaults={
                    "api_key": self.api_token,
                    "username": self.username,
                },
            )
            self.logged_in = True

            return True
        else:
            return False

    def login_api_key(self):
        """Login with user ID and API token to Habitica.

        Returns:
            True for success, False for failure.
        """
        headers = {
            "x-client": self.hab_user_id + "-TODO-Overs",
            "x-api-user": self.hab_user_id,
            "x-api-key": decrypt_text(self.api_token),
            "Content-Type": "application/json",
        }

        req = requests.get("https://habitica.com/api/v3/user", headers=headers)
        # print("GET: " + req.url + " [" + str(req.status_code) + "]: " + req.text)
        self.return_code = req.status_code
        if req.status_code == 200:
            req_json = req.json()
            self.username = req_json["data"]["profile"]["name"]

            Users.objects.update_or_create(
                user_id=self.hab_user_id,
                defaults={
                    "api_key": self.api_token,
                    "username": self.username,
                },
            )

            self.logged_in = True

            return True
        return False

    def create_task(self):
        """Create a task on Habitica.

        Returns:
            True for success, False for failure.
        """
        headers = {
            "x-client": self.hab_user_id + "-TODO-Overs",
            "x-api-user": self.hab_user_id,
            "x-api-key": decrypt_text(self.api_token),
        }

        if int(self.task_days) > 0:
            due_date = datetime.now() + timedelta(days=int(self.task_days))
            due_date = due_date.isoformat()

            req = requests.post(
                "https://habitica.com/api/v3/tasks/user",
                headers=headers,
                data={
                    "text": self.task_name,
                    "type": "todo",
                    "notes": self.notes,
                    "date": due_date,
                    "priority": self.priority,
                    "tags": self.tags,
                },
            )
            # print("POST: " + req.url + " [" + str(req.status_code) + "]: " + req.text)
            self.return_code = req.status_code
            if req.status_code == 201:
                req_json = req.json()
                self.task_id = req_json["data"]["id"]
                return True
            return False
        else:
            req = requests.post(
                "https://habitica.com/api/v3/tasks/user",
                headers=headers,
                data={
                    "text": self.task_name,
                    "type": "todo",
                    "notes": self.notes,
                    "priority": self.priority,
                    "tags": self.tags,
                },
            )
            # print("POST: " + req.url + " [" + str(req.status_code) + "]: " + req.text)
            self.return_code = req.status_code
            if req.status_code == 201:
                req_json = req.json()
                self.task_id = req_json["data"]["id"]
                return True
            return False

    def edit_task(self):
        """Edit a task on Habitica.

        Returns:
            True for success, False for failure.
        """
        headers = {
            "x-client": self.hab_user_id + "-TODO-Overs",
            "x-api-user": self.hab_user_id,
            "x-api-key": decrypt_text(self.api_token),
        }
        url = "https://habitica.com/api/v3/tasks/" + str(self.task_id)

        if int(self.task_days) > 0:
            due_date = datetime.now() + timedelta(days=int(self.task_days))
            due_date = due_date.isoformat()

            req = requests.put(
                url,
                headers=headers,
                data={
                    "text": self.task_name,
                    "notes": self.notes,
                    "date": due_date,
                    "priority": self.priority,
                    "tags": self.tags,
                },
            )
            # print("PUT: " + req.url + " [" + str(req.status_code) + "]: " + req.text)
            self.return_code = req.status_code
            if req.status_code == 200:
                req_json = req.json()
                self.task_id = req_json["data"]["id"]
                return True
            return False
        else:
            req = requests.put(
                url,
                headers=headers,
                data={
                    "text": self.task_name,
                    "notes": self.notes,
                    "priority": self.priority,
                    "tags": self.tags,
                },
            )
            # print("PUT: " + req.url + " [" + str(req.status_code) + "]: " + req.text)
            self.return_code = req.status_code
            if req.status_code == 200:
                req_json = req.json()
                self.task_id = req_json["data"]["id"]
                return True
            else:
                return False

    def get_user_tags(self):
        """Get the list of a user's tags.

        Returns:
            Dict of tags for success, False for failure.
        """
        headers = {
            "x-client": self.hab_user_id + "-TODO-Overs",
            "x-api-user": self.hab_user_id,
            "x-api-key": decrypt_text(self.api_token),
        }

        req = requests.get("https://habitica.com/api/v3/tags", headers=headers, data={})
        # print("GET: " + req.url + " [" + str(req.status_code) + "]: " + req.text)
        self.return_code = req.status_code
        if req.status_code == 200:
            req_json = req.json()

            user = Users.objects.get(user_id=self.hab_user_id)

            current_tags = Tags.objects.filter(tag_owner=user)
            current_tag_ids = []
            for tag in current_tags:
                current_tag_ids.append(tag.tag_id)

            if req_json["data"]:
                # Add/update tags in database
                for tag_json in req_json["data"]:
                    tag_text = tag_json["name"]
                    tag_text = tag_text

                    Tags.objects.update_or_create(
                        tag_id=tag_json["id"],
                        defaults={
                            "tag_owner": user,
                            "tag_text": tag_text,
                        },
                    )
                    if tag_json["id"] in current_tag_ids:
                        current_tag_ids.remove(tag_json["id"])

                for leftover_tag in current_tag_ids:
                    print("deleting tag " + leftover_tag)
                    Tags.objects.filter(tag_id=leftover_tag).delete()

                return req_json["data"]
            return False
        return False

    def get_user_tasks(self):
        """Get the list of a user's tasks.

        Returns:
            Dict of tags for success, False for failure.
        """
        headers = {
            "x-client": self.hab_user_id + "-TODO-Overs",
            "x-api-user": self.hab_user_id,
            "x-api-key": decrypt_text(self.api_token),
        }

        req = requests.get(
            "https://habitica.com/api/v3/tasks/user", headers=headers, data={}
        )
        # print("GET: " + req.url + " [" + str(req.status_code) + "]: " + req.text)
        self.return_code = req.status_code
        if req.status_code == 200:
            req_json = req.json()

            user = Users.objects.get(user_id=self.hab_user_id)

            if req_json["data"]:
                for tag_json in req_json["data"]:
                    if tag_json["type"] == "todo":
                        print(tag_json)
                    updatedAt = datetime.strptime(
                        tag_json["updatedAt"], "%Y-%m-%dT%H:%M:%S.%fZ"
                    )

                    if updatedAt.day == datetime.today().day:
                        print("TODAY")
                        if tag_json["type"] == "todo":
                            print(tag_json)
                        else:
                            print(tag_json["text"])

                    if tag_json["type"] == "habit":
                        pass
                        # print(
                        #    tag_json["text"]
                        # tag_json["updatedAt"],
                        # )

                        # + reward

                return req_json["data"]
            return False
        return False

    def get_today_completed_tasks(self):
        """Get the list of a user's completed tasks.

        Returns:
            Dict of tags for success, False for failure.
        """
        headers = {
            "x-client": self.hab_user_id + "-TODO-Overs",
            "x-api-user": self.hab_user_id,
            "x-api-key": decrypt_text(self.api_token),
        }

        req = requests.get(
            "https://habitica.com/api/v3/tasks/user?type=completedTodos",
            headers=headers,
            data={},
        )
        # print("GET: " + req.url + " [" + str(req.status_code) + "]: " + req.text)
        self.return_code = req.status_code
        if req.status_code == 200:
            req_json = req.json()

            user = Users.objects.get(user_id=self.hab_user_id)
            results = []
            if req_json["data"]:
                for tag_json in req_json["data"]:
                    completedAt = datetime.strptime(
                        tag_json["dateCompleted"], "%Y-%m-%dT%H:%M:%S.%fZ"
                    )
                    if (
                            (completedAt.day == datetime.today().day)
                            and (completedAt.month == datetime.today().month)
                            and (completedAt.year == datetime.today().year)
                            and (tag_json["type"] == "todo")
                    ):
                        results.append(tag_json)
                return results
            return False
        return False

    def get_today_completed_habits(self):
        """Get the list of a user's completed tasks.

        Returns:
            Dict of tags for success, False for failure.
        """
        headers = {
            "x-client": self.hab_user_id + "-TODO-Overs",
            "x-api-user": self.hab_user_id,
            "x-api-key": decrypt_text(self.api_token),
        }

        req = requests.get(
            "https://habitica.com/api/v3/tasks/user?type=habits",
            headers=headers,
            data={},
        )
        # print("GET: " + req.url + " [" + str(req.status_code) + "]: " + req.text)
        self.return_code = req.status_code
        if req.status_code == 200:
            req_json = req.json()

            user = Users.objects.get(user_id=self.hab_user_id)
            results = []
            if req_json["data"]:
                for tag_json in req_json["data"]:
                    for h in tag_json["history"]:
                        updatedAt = datetime.fromtimestamp(h["date"] / 1e3)
                        if (
                                (updatedAt.day == datetime.today().day)
                                and (updatedAt.month == datetime.today().month)
                                and (updatedAt.year == datetime.today().year)
                        ):
                            entry = {
                                key: tag_json[key]
                                for key in [
                                    "text",
                                    "frequency",
                                    "type",
                                    "notes",
                                    "createdAt",
                                    "counterUp",
                                    "counterDown",
                                ]
                            }
                            entry["date"] = updatedAt
                            results.append(entry)
                return results
            return False
        return False

    def get_today_completed_dailies(self):
        """Get the list of a user's completed tasks.

        Returns:
            Dict of tags for success, False for failure.
        """
        headers = {
            "x-client": self.hab_user_id + "-TODO-Overs",
            "x-api-user": self.hab_user_id,
            "x-api-key": decrypt_text(self.api_token),
        }

        req = requests.get(
            "https://habitica.com/api/v3/tasks/user?type=dailys",
            headers=headers,
            data={},
        )
        # print("GET: " + req.url + " [" + str(req.status_code) + "]: " + req.text)
        self.return_code = req.status_code
        if req.status_code == 200:
            req_json = req.json()
            results = []
            if req_json["data"]:
                for tag_json in req_json["data"]:
                    duplicat_check = []
                    for h in tag_json["history"]:
                        updatedAt = datetime.fromtimestamp(h["date"] / 1e3)
                        if (
                                (updatedAt.day == datetime.today().day)
                                and (updatedAt.month == datetime.today().month)
                                and (updatedAt.year == datetime.today().year)
                                and (h["isDue"] == True)
                                and (h["completed"] == True)
                                and (tag_json["text"] not in duplicat_check)
                        ):
                            results.append(
                                {
                                    key: tag_json[key]
                                    for key in [
                                    "text",
                                    "frequency",
                                    "type",
                                    "notes",
                                    "createdAt",
                                    "repeat",
                                    "everyX",
                                    "streak",
                                ]
                                }
                            )
                            duplicat_check.append(tag_json["text"])
                return results
            return False
        return False
