# Проект от компании iLine
# Предварительно создали базу данных в PostgreSQL "test_database" 
# Предварительно установили необходимые библиотеки, запустив внизу в терминале pip install psycopg2-binary tabulate mimesis
# Mimesis - это генератор данных различных типов, включая личную информацию, даты, адреса и многое другое.
import psycopg2 # адаптер базы данных PostgreSQL для языка Python. Он позволяет приложениям на Python
# взаимодействовать с данными, хранящимися в базе PostgreSQL, и выполнять SQL-запросы
from mimesis import Person, Datetime, Finance # импорт провайдеров Person (персональные данные), Datetime и Finance
from mimesis.locales import Locale # импорт объекта Locale для привязки Person к определённой местности
from mimesis.enums import Gender 
import random
from tabulate import tabulate

# Инициализация генераторов данных
person = Person(Locale.RU)
dt = Datetime()
finance = Finance()
positions = ['CEO', 'Manager', 'Team Lead', 'Senior Developer', 'Developer']

def connect_to_db():
    '''Подключение к базе данных test_database в PostgreSQL.'''
    try:
        conn = psycopg2.connect(
            dbname='test_database', user='postgres', password='12345678', host='localhost'
        )
        print('✅ Успешное подключение к базе данных')
        return conn
    except Exception as e:
        print(f'❌ Ошибка подключения PostgreSQL: {e}')
        return None

def create_table(num_employees=50000):
    '''Создаёт таблицу employees и заполняет её данными.'''
    conn = connect_to_db()
    cursor = conn.cursor() # Это объект, кот. используется для взаимодействия с базой данных
    cursor.execute("DROP TABLE IF EXISTS employees CASCADE") # Удаляем таблицу, если она существует
    # Создаём таблицу employees с полями id, full_name, post, hire_date, salary и manager_id
    cursor.execute('''
        CREATE TABLE employees (
            id SERIAL PRIMARY KEY,
            full_name VARCHAR(200) NOT NULL,
            post VARCHAR(200) NOT NULL,
            hire_date DATE NOT NULL,
            salary DECIMAL(10,2) NOT NULL,
            manager_id INT,
            FOREIGN KEY(manager_id) REFERENCES employees(id)
        )
    ''')
    # Генерация данных
    for i in range(num_employees):
        full_name = person.full_name(gender=Gender.MALE)
        if i == 0:
            post = 'CEO'
            salary = float(finance.price(minimum=430000, maximum=500000))
            manager_id = None
        elif 1 <= i <= 30:
            post = 'Manager'
            salary = float(finance.price(minimum=300000, maximum=370000))
            manager_id = 1
        elif 31 <= i <= 330:
            post = 'Team Lead'
            salary = float(finance.price(minimum=200000, maximum=280000))
            manager_id = random.choice(range(2, 32))
        elif 331 <= i <= 1330:
            post = 'Senior Developer'
            salary = float(finance.price(minimum=110000, maximum=180000))
            manager_id = random.choice(range(32, 332))
        else:
            post = 'Developer'
            salary = float(finance.price(minimum=50000, maximum=100000))
            manager_id = random.choice(range(32, 332))
        hire_date = dt.date(start=2010, end=2025)       
        # Вставляем сгенерированные данные в таблицу
        cursor.execute(
            'INSERT INTO employees (full_name, post, hire_date, salary, manager_id) VALUES (%s, %s, %s, %s, %s)',
            (full_name, post, hire_date, salary, manager_id)
        )
        print(f'Query execution: {i}')
    print(f'✅ Пользователи в количестве {num_employees} успешно добавлены в таблицу')

    # Сохраняем изменения и закрываем соединение
    conn.commit()
    cursor.close()
    conn.close()

create_table()

def show_employees(limit=20):
    '''Показывает список сотрудников с пагинацией'''
    conn = connect_to_db()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM employees') # Получаем общее количество сотрудников
        total_employees = cursor.fetchone()[0] # метод курсора извлекает первую строку из результата запроса
        
        page = 1
        while True:
            offset = (page - 1) * limit
            cursor.execute("""
                SELECT *
                FROM employees
                ORDER BY id
                LIMIT %s OFFSET %s
            """, (limit, offset))
            
            employees = cursor.fetchall()
            
            # Форматируем вывод с помощью tabulate
            headers = ["ID", "Имя", "Должность", "Дата приема", "Зарплата", 'ID начальника']
            print(f"\nСотрудники (страница {page}/{int(total_employees/limit)+1})")
            print(tabulate(employees, headers=headers, tablefmt="grid"))
            
            print(f'\nПоказано {len(employees)} из {total_employees} сотрудников')
            
            # Навигация
            print("\nНавигация: n-следующая, p-предыдущая, q-выход")
            choice = input('Выберите действие: ').lower()
            
            if choice == 'n' and offset + limit < total_employees:
                page += 1
            elif choice == 'p' and page > 1:
                page -= 1
            elif choice == 'q':
                break
            else:
                print('❌ Неверный ввод или достигнуты границы списка')
                
    except Exception as e:
        print(f'❌ Ошибка при получении списка сотрудников: {e}')
    finally:
        conn.close()

def main_menu():
    while True:
        print('Главное меню:')
        print('1. Показать список сотрудников')
        print('2. Добавить сотрудника')
        print('3. Показать список должностей')
        print('4. Выход')

        choice = input('Выберите действие из главного меню (1-4): ')
        if choice == '1':
            show_employees()
        elif choice == '2':
            conn = connect_to_db()
            cursor = conn.cursor()
            full_name = input('Введите имя и фамилию: ')
            post = input('Введите должность: ')
            salary = float(input('Введите зарплату: '))
            manager_id = int(input('Введите ID начальника: '))
            hire_date = input('Введите дату приёма (YYYY-MM-DD): ')
            cursor.execute("INSERT INTO employees (full_name, post, salary, manager_id, hire_date) \
                VALUES(%s, %s, %s, %s, %s)", (full_name, post, salary, manager_id, hire_date))
            conn.commit()
            print(f'Сотрудник {full_name} добавлен')
        elif choice == '3':
            print(positions)
        elif choice == '4':
            print('Выход из программы')
            break
        else: print('❌ Неверный ввод. Попробуйте снова.')

# Запуск главного меню
if __name__ == '__main__':
    print('Создание таблицы сотрудников')
    main_menu()