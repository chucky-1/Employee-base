import psycopg2

# flag = 1, программа будет подключаться к базе данных.
# flag = 0, программа будет использовать словарь.
# flag 0 используется, когда нет возможности подключения к базе данных. В этом случае функции возвращают
# вручную написанные словари, импортируя их из модуля function-input, имитируя работу с базой данных.
flag = 0

if flag:
    conn = psycopg2.connect(dbname='staff', user='postgres', password='220095sql', port=5433)
    cur = conn.cursor()
else: import function_input


def jbs_dep():
    '''

    Функция присваивает всем отделам должности, которые относятся к этим отделам.
    Для этого объединяются 2 таблицы из базы данных: departments (отделы) и jobs_position (должности).
    Возвращается словарь, где keys - это отделы, а values - это список должностей.

    '''
    if flag:
        #  Скрещиваем отделы и должности
        cur.execute('''
        SELECT departments.title, jobs_position.title
        FROM departments
        LEFT JOIN jobs_position USING(department_id)
        ORDER BY department_id
        ''')
        jobs_and_department = cur.fetchall()                                   #  [(Отдел, должность), ...]
        departments = set(i[0] for i in jobs_and_department)                   #  Уникалные отделы

        #  Создаём словарь
        jobs_and_department_dict = {i: [] for i in departments}
        for i in departments:
            for x in jobs_and_department:
                if x[0] == i:
                    jobs_and_department_dict[i].append(x[1])

        #  Заменяем None на ''
        for i in jobs_and_department_dict:
            if jobs_and_department_dict[i] == [None]:
                jobs_and_department_dict[i] = ['']

    else:
        jobs_and_department_dict = function_input.jobs_and_department_dict

    return jobs_and_department_dict


def jbs_dep_id():
    '''

    Возвращает словарь
    key - отдел / должность
    value - id

    '''
    if flag:
        cur.execute('''
        SELECT title, department_id
        FROM departments
        ''')
        dep = cur.fetchall()

        cur.execute('''
        SELECT title, jobs_position_id
        FROM jobs_position
        ''')
        job = cur.fetchall()

        dic_jbs_dep_id = {}
        for i in dep:
            dic_jbs_dep_id[i[0]] = i[1]
        for i in job:
            dic_jbs_dep_id[i[0]] = i[1]
    else:
        dic_jbs_dep_id = function_input.dic_jbs_dep_id

    return dic_jbs_dep_id

def emp():
    """

    Функция выводит всех сотрудников и их:
    id сотрудника - employee_id, фамилия и имя - CONCAT(first_name, ' ', last_name),
    id должности - jobs_position_id, должность - jobs_position.title,
    id отдела - department_id, отдел - departments.title,
    зарплата - pay, телефон - phone

    Возвращает словарь вида:
    {CONCAT(first_name, ' ', last_name): {'employee_id': 1, 'first_last_name': 'Кирилл Парчинский',
    'jobs_position_id': 1, 'jobs_position': 'Директор', 'department_id': 1, 'department': 'Руководство',
    'pay': 1600, 'phone': '+375291112233'}}

    """

    if flag:
        cur.execute('''
        SELECT employee_id, CONCAT(first_name, ' ', last_name) AS first_last_name, 
        employees.jobs_position_id, jobs_position.title AS jobs_position, 
        employees.department_id, departments.title AS department, 
        pay, phone
        FROM employees
        JOIN jobs_position ON employees.jobs_position_id = jobs_position.jobs_position_id
        JOIN departments ON employees.department_id = departments.department_id
        ''')
        emp_list = cur.fetchall()

        emp_dict = {i[1]: {} for i in emp_list}
        for emp in emp_list:
            name = emp[1]
            emp_dict[name]['employee_id'] = emp[0]
            emp_dict[name]['first_last_name'] = emp[1]
            emp_dict[name]['jobs_position_id'] = emp[2]
            emp_dict[name]['jobs_position'] = emp[3]
            emp_dict[name]['department_id'] = emp[4]
            emp_dict[name]['department'] = emp[5]
            emp_dict[name]['pay'] = emp[6]
            emp_dict[name]['phone'] = emp[7]
    else:
        emp_dict = function_input.emp_dict

    return emp_dict


if __name__ == '__main__':
    print(jbs_dep())
    print(jbs_dep_id())
    print(emp())
