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
    def get_em(self):
        employers_all = []
        page = 0
        while page <= 49:
            params = {
                "only_with_vacancies": True,
                "page": page,
                "archived": False,
                "per_page": 100,
            }
            employers = requests.get(
                self.url, 
                params=params, 
                headers=self.headers
                ).json()
            
            # employers_all.append(employers)
            page += 1
        return employers


    def get_employers(self):
        # all_employers = []
        # for page in range(0, 50):

        #     self.params = {
        #         "only_with_vacancies": True,
        #         "page": page,
        #         "archived": False,
        #         "per_page": 1,
        #     }
        #     employers = requests.get(self.url, params=self.params, headers=self.headers).json()
        all_employers = []
        for employer in self.get_em()["items"]:
                # formatted_employer = {
                #     "id": employer["id"],
                #     "name": employer["name"],
                #     "url": employer["url"],
                #     "alternate_url": employer["alternate_url"],
                #     "vacancies_url": employer["vacancies_url"],
                #     "open_vacancies": employer["open_vacancies"]
                # }
            formatted_employer = [
                employer["id"],
                employer["name"],
                employer["url"],
                employer["alternate_url"],
                employer["vacancies_url"],
                employer["open_vacancies"]
                ]
            all_employers.append(formatted_employer)
        return all_employers
    
    def get_vacancies(self):



        all_vacancies = []
        for vacanci in self.get_em()["items"]:
            vac = requests.get(vacanci["vacancies_url"]).json()
            
            for oo in vac["items"]:
                formatted_vacancies = [
                    oo["id"], 
                    oo["employer"]["id"], 
                    oo["name"], 
                    oo["salary"]["from"] 
                    if oo["salary"] and oo["salary"]["from"] != 0 
                    else None, 
                    oo["salary"]["to"] 
                    if oo["salary"] and oo["salary"]["to"] != 0 
                    else None, 
                    oo["alternate_url"]
                    ]
                all_vacancies.append(formatted_vacancies)



    
        return all_vacancies
            
        # return all_vacancies


dbm_api = HeadHunterAPI()
dbm = dbm_api.get_vacancies()
# print(json.dumps(dbm, indent=2, ensure_ascii=False))
# print(len(dbm))

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
            cur.execute(
                "INSERT INTO employees VALUES (%s, %s, %s, %s, %s, %s)", 
                row
                )

        conn.commit()
        cur.close()
        conn.close()

    def add_vacancies_in_bd(self):
        cur.execute(
            "CREATE TABLE IF NOT EXISTS vacancies"
            "("
                "vacanci_id int PRIMARY KEY,"
                "employer_id varchar NOT NULL,"
                "name varchar NOT NULL,"
                "salary_from varchar,"
                "salary_to varchar,"
                "alternate_url varchar NOT NULL"
            ");"
            )
        for row in dbm:
            cur.execute(
                "INSERT INTO vacancies VALUES (%s, %s, %s, %s, %s, %s)", 
                row
                )
        conn.commit()
        cur.close()
        conn.close()


dbm_api = BdHeadHunter()
# dbm_api.add_vacancies_in_bd()
# print(json.dumps(e, indent=2, ensure_ascii=False))

class DBManager():
    def get_companies_and_vacancies_count():
        pass

    def get_all_vacancies():
        pass

    def get_avg_salary():
        pass


    def get_vacancies_with_higher_salary():
        pass

    def get_vacancies_with_keyword():
        pass





# cur.execute("SELECT * FROM employees")
# rows = cur.fetchall()
# for row in rows:
#     print(row)

# conn.commit()
# cur.close()
# conn.close()
