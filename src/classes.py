from abc import ABC, abstractmethod

import psycopg2
import requests
import json
import csv
import math


class Engine(ABC):
    @abstractmethod
    def get_request(self):
        pass


class HeadHunterAPI():
    url = "https://api.hh.ru/employers"
    headers = {"User-Agent": "Your User Agent"}
    def get_employers(self):
        all_employers = []
        for page in range(0, 50):

            self.params = {
                "only_with_vacancies": True,
                "page": page,
                "archived": False,
                "per_page": 100,
            }
            employers = requests.get(self.url, params=self.params, headers=self.headers).json()

            for employer in employers["items"]:
                formatted_employer = [employer["id"],employer["name"],employer["url"],employer["alternate_url"],employer["vacancies_url"],employer["open_vacancies"]]
                all_employers.append(formatted_employer)


        return all_employers
    
    def get_vacancies(self):
        pass



dbm_api = HeadHunterAPI()
dbm = dbm_api.get_employers()

conn = psycopg2.connect(
    host="localhost",
    database="employer",
    user="root",
    password="root",
    port=5431
    )
cur = conn.cursor()

class BdHeadHunter():

    def add_employers_in_bd(self):
        cur.execute(
            "CREATE TABLE IF NOT EXISTS employees "
            "("
                "employer_id int PRIMARY KEY,"
                "name varchar NOT NULL,"
                "url varchar NOT NULL,"
                "alternate_url varchar,"
                "vacancies_url varchar NOT NULL,"
                "open_vacancies int"
            ");"
            )
        for row in dbm:
            cur.execute("INSERT INTO employees VALUES (%s, %s, %s, %s, %s, %s)", row)

        conn.commit()
        cur.close()
        conn.close()


    def add_vacancies_in_bd(self):
        pass

dbm_api = BdHeadHunter()
dbm_api.add_employers_in_bd()
