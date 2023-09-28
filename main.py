

from utils import get_headhanter_data, create_database, save_data_to_database, DBManager
from config import config


def main():

    database = 'headhanter'
    url = "https://api.hh.ru/employers"
    params = config()
    world = "python"
    dbmanager = DBManager(database, params, world)
    
    data = get_headhanter_data(url)

    create_database(database, params)
    save_data_to_database(data, database, params)
    dbmanager.get_companies_and_vacancies_count()
    dbmanager.get_all_vacancies()
    dbmanager.get_avg_salary()
    dbmanager.get_vacancies_with_higher_salary()
    dbmanager.get_vacancies_with_keyword()


if __name__ == '__main__':
    main()