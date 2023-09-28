from typing import Any
import psycopg2
import requests


def get_headhanter_data(url: str) -> dict:
    """Получение данных о работодадателях и вакансиях с помощью API HeadHunter."""
    
    headers = {"User-Agent": "Your User Agent"}
    params = {
            "only_with_vacancies": True,
            "page": 0,
            "archived": False,
            "per_page": 100,
        }
    employers = requests.get(
            url, 
            params=params, 
            headers=headers
            ).json()
            
    return employers


def create_database(database_name: str, params: dict):
    """Создание базы данных и таблиц для сохранения данных о работодадателях и вакансиях."""

    conn = psycopg2.connect(dbname='postgres', **params)
    conn.autocommit = True
    cur = conn.cursor()

    cur.execute(f"DROP DATABASE IF EXISTS {database_name}")
    cur.execute(f"CREATE DATABASE {database_name}")

    conn.close()

    conn = psycopg2.connect(dbname=database_name, **params)

    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE employees (
                employer_id INTEGER PRIMARY KEY,
                name varchar NOT NULL,
                url varchar NOT NULL,
                alternate_url varchar,
                vacancies_url varchar NOT NULL,
                open_vacancies INTEGER
            )
        """)

    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE vacancies (
                vacanci_id INTEGER PRIMARY KEY,
                employer_id INTEGER,
                name varchar NOT NULL,
                salary_from INTEGER,
                salary_to INTEGER,
                alternate_url varchar NOT NULL
            )
        """)

    conn.commit()
    conn.close()

def save_data_to_database(data: dict, database_name: str, params: dict):
    """Сохранение данных о работодадателях и вакансиях в базу данных."""

    conn = psycopg2.connect(dbname=database_name, **params)

    with conn.cursor() as cur:
        for row in data['items']:
            cur.execute(
                """
                INSERT INTO employees 
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    row["id"], 
                    row["name"], 
                    row["url"], 
                    row["alternate_url"], 
                    row["vacancies_url"], 
                    row["open_vacancies"]
                    )
            )

            vacancies_url = row["vacancies_url"]
            vacancies_data = requests.get(vacancies_url).json()
            for vacanci in vacancies_data['items']:
                cur.execute(
                    """
                    INSERT INTO vacancies
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (vacanci["id"], 
                    vacanci["employer"]["id"], 
                    vacanci["name"], 
                    vacanci["salary"]["from"] 
                    if vacanci["salary"] and vacanci["salary"]["from"] != 0 
                    else None, 
                    vacanci["salary"]["to"] 
                    if vacanci["salary"] and vacanci["salary"]["to"] != 0 
                    else None, 
                    vacanci["alternate_url"]
                    )
                )

    conn.commit()
    conn.close()


class DBManager():

    def __init__(self, database_name: str, params: dict, world: str) -> None:
        self.database_name = database_name
        self.params = params
        self.world = world
        self.conn = psycopg2.connect(dbname=database_name, **params)
        self.cur = self.conn.cursor()

        
    def get_companies_and_vacancies_count(self):
        """Получаем список всех компаний и количество вакансий у каждой компании."""

        self.cur.execute("SELECT * FROM employees")
        rows = self.cur.fetchall()
        for row in rows:
            print(f"{row[1]} количество вакансий - {row[5]}")


    def get_all_vacancies(self):
        """Получаем список всех вакансий с указанием названия компании, названия вакансии и зарплаты и ссылки на вакансию."""

        self.cur.execute("""
            SELECT employees.name, vacancies.name, salary_from, salary_to, vacancies.alternate_url\n
            FROM vacancies\n
            JOIN employees USING(employer_id)
        """)
        rows = self.cur.fetchall()
        for row in rows:
            print(f"Название компании: {row[0]}"
                f"\nНазвание вакансии: {row[1]}"
                f"\nЗарплата от: {row[2]}"
                f"\nЗарплата до: {row[3]}"
                f"\nСсылка на вакансию: {row[4]}\n"
            )
        

    def get_avg_salary(self):
        """Получаем среднюю зарплату по вакансиям."""

        self.cur.execute("SELECT AVG(salary_from) FROM vacancies")
        rows = self.cur.fetchall()
        print(f"Средняя зарплата по вакансиям: {rows}")


    def get_vacancies_with_higher_salary(self):
        """Получаем список всех вакансий, у которых зарплата выше средней по всем вакансиям."""

        self.cur.execute(f"""
            SELECT name
            FROM vacancies 
            WHERE salary_from > (SELECT AVG (salary_from) FROM vacancies)
        """)
        rows = self.cur.fetchall()
        for row in rows:
            print(row)


    def get_vacancies_with_keyword(self):
        """Получаем список всех вакансий, в названии которых содержатся переданное в метод слово."""

        self.cur.execute(f"""
            SELECT DISTINCT name\n
            FROM vacancies\n
            WHERE name LIKE '%{self.world}%'
        """)
        rows = self.cur.fetchall()
        for row in rows:
            if rows:
                print(f"По запросу {self.world} не найдено вакансий")
            else:
                print(row)