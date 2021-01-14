'''

База данных сотрудников предприятия.
Графический интерфейс реализован на tkinter.
В качестве базы данных используется postgreSQL.

Предусмотрена работа в 2 режимах, посредствам переменной flag (в модуле function).
Если flag = 1, программа будет подключаться к базе данных postgreeSQL
Если flag = 0, программа будет работать с входными данными из модуля function_input

'''

from tkinter import *
from tkinter.ttk import Combobox
import tkinter.messagebox as mb
from Employees.function import *
from Employees.function_input import *
import psycopg2
import math

if flag:
    conn = psycopg2.connect(dbname='staff', user='postgres', password='220095sql', port=5433)
    cur = conn.cursor()

# id для добавления отделов, должностей и сотрудников. Следующие значения для модуля function_input.
# Увеличиваются на 1 при добавлении.
if not flag:
    global next_dep_id, next_job_id, next_employee_id
    next_dep_id = 9
    next_job_id = 15
    next_employee_id = 46


def new_pers():

    def new_pers_button():

        # Обязательные поля для заполнения
        if entries['Имя*'].get() == '' or entries['Фамилия*'].get() == '' or entries['Отдел*'].get() == '' \
                or entries['Должность*'].get() == '' or entries['Зарплата*'].get() == '':
            mb.showinfo('Ошибка', 'Поля отмеченные звёздочкой обязательны для заполнения')
            return False

        # Возможность добавления только в существующие отделы и должности
        if flag:
            if entries['Отдел*'].get() not in jbs_dep() or \
                    entries['Должность*'].get() not in jbs_dep()[entries['Отдел*'].get()]:
                mb.showinfo('Ошибка', 'Данного отдела или должности не существует')
                return False
        else:
            if entries['Отдел*'].get() not in jobs_and_department_dict or \
                    entries['Должность*'].get() not in jobs_and_department_dict[entries['Отдел*'].get()]:
                mb.showinfo('Ошибка', 'Данного отдела или должности не существует')
                return False

        # Возможность ввода толко цифр в строку зарплата
        try: int(entries['Зарплата*'].get())
        except:
            mb.showinfo('Ошибка', 'Значение зарплаты должно быть число')
            return False

        # Вычисляем id отдела / должности
        if flag:
            department = jbs_dep_id()[entries['Отдел*'].get()]
            job = jbs_dep_id()[entries['Должность*'].get()]
        else:
            department = dic_jbs_dep_id[entries['Отдел*'].get()]
            job = dic_jbs_dep_id[entries['Должность*'].get()]

        # Добавляем сотрудника
        if flag:
            cur.execute('''
            INSERT INTO employees (first_name, last_name, middle_name, department_id, jobs_position_id, pay, phone)
            VALUES 
            (%(first_name)s, %(last_name)s, %(middle_name)s, 
            %(department_id)s, %(jobs_position_id)s, %(pay)s, %(phone)s)
            ''', {'first_name': entries['Имя*'].get(),
                  'last_name': entries['Фамилия*'].get(),
                  'middle_name': entries['Отчество'].get(),
                  'department_id': department,
                  'jobs_position_id': job,
                  'pay': int(entries['Зарплата*'].get()),
                  'phone': entries['Телефон'].get()})
            conn.commit()
        else:
            global next_employee_id
            emp_dict[entries['Имя*'].get() + ' ' + entries['Фамилия*'].get()] = dict(employee_id=next_employee_id,
                first_last_name=entries['Имя*'].get() + ' ' + entries['Фамилия*'].get(), jobs_position_id=job,
                jobs_position=entries['Должность*'].get(), department_id=department, department=entries['Отдел*'].get(),
                pay=int(entries['Зарплата*'].get()), phone=entries['Телефон'].get())
            next_employee_id += 1

        mb.showinfo('Выполнено', f'{entries["Имя*"].get()} '
                                 f'{entries["Фамилия*"].get()} добавлен')
        window2.destroy()
        window.destroy()
        start()


    window2 = Tk()
    window2.title('Добавьте нового сотрудника')

    frame = Frame(window2, borderwidth=3)
    frame.pack()

    linename = ('Имя*', 'Фамилия*', 'Отчество', 'Отдел*', 'Должность*', 'Зарплата*', 'Телефон')
    entries = {}
    for num, line in enumerate(linename):
        lab = Label(frame, text=line)
        ent = Entry(frame, width=44)                  # Ширина 44 подобрана под геометрию окна
        lab.grid(row=num, column=0, sticky="e")
        ent.grid(row=num, column=1)
        entries[line] = ent
    else:
        frame3 = Frame(window2)
        frame3.pack(fill=BOTH, expand=TRUE)
        Label(frame3, text='* поля обязательны для заполнения',
              font=('Arial', '10', 'italic')).pack(fill=BOTH, expand=TRUE)

    frame2 = Frame(window2, borderwidth=3)
    frame2.pack(fill=BOTH, expand=TRUE)
    button_new = Button(frame2, text='Добавить сотрудника', command=new_pers_button).pack(fill=BOTH, expand=TRUE)

    # Доступные отделы и должности
    frame3 = Frame(window2, borderwidth=3)
    frame3.pack()

    Label(frame3, text='Доступные отделы и должности:', font=('Arial', '10', 'italic')).grid(row=0, column=0, columnspan=2)

    if flag:
        for num, dep in enumerate(jbs_dep().keys(), start=1):
            jobs = ', '.join(jbs_dep()[dep])
            Label(frame3, text=f'{dep}: ').grid(row=num, column=0, sticky='w')
            Label(frame3, text=jobs).grid(row=num, column=1, sticky='w')
    else:
        for num, dep in enumerate(jobs_and_department_dict.keys(), start=1):
            jobs = ', '.join(jobs_and_department_dict[dep])
            Label(frame3, text=f'{dep}: ').grid(row=num, column=0, sticky='w')
            Label(frame3, text=jobs).grid(row=num, column=1, sticky='w')

    window2.mainloop()


def all_pers():


    def button_chabge_job_and_department():

        if flag:
            if entry_change.get() not in emp():
                mb.showinfo('Ошибка', f'Сотрудника {entry_change.get()} нет в базе. Попробуйте ещё раз')
                return False
        else:
            if entry_change.get() not in emp_dict:
                mb.showinfo('Ошибка', f'Сотрудника {entry_change.get()} нет в базе. Попробуйте ещё раз')
                return False

        def new_job_or_dep():

            # action - 'Перевезти на другую должность' / 'Перевезти в другой отдел'
            # new_value - Новая должность / отдел
            action = combo.get()
            new_value = combo2.get()

            if action == 'Перевезти на другую должность':
                # id новой должности
                if flag: jobs_position_id = jbs_dep_id()[new_value]
                else: jobs_position_id = dic_jbs_dep_id[new_value]

                # Устанавливаем новый id должности сотруднику
                if flag:
                    cur.execute('''
                    UPDATE employees
                    SET jobs_position_id = %(int)s
                    WHERE CONCAT(first_name, ' ', last_name) = %(str)s
                    ''', {'int': jobs_position_id, 'str': value})
                    conn.commit()
                else:
                    emp_dict[value]['jobs_position_id'] = jobs_position_id
                    emp_dict[value]['jobs_position'] = new_value

                mb.showinfo('Выполнено', f'{value} переведён на должность {new_value}')
                window9.destroy()
                window3.destroy()
                all_pers()

            if action == 'Перевезти в другой отдел':
                # Определяем id нового отдела
                if flag: new_department_id = jbs_dep_id()[new_value]
                else: new_department_id = dic_jbs_dep_id[new_value]

                # Устанавливаем новый id отдела сотруднику
                if flag:
                    cur.execute('''
                    UPDATE employees
                    SET department_id = %(int)s
                    WHERE CONCAT(first_name, ' ', last_name) = %(str)s
                    ''', {'int': new_department_id, 'str': value})
                else:
                    emp_dict[value]['department_id'] = new_department_id
                    emp_dict[value]['department'] = new_value

                mb.showinfo('Выполнено', f'{value} переведён в отдел {new_value}.\n'
                                         f'Выберите должность из отдела {new_value}'
                                         f' в следующем окне.')
                window9.destroy()

                # НОВОЕ ОКНО Выбираем должность из нового отдела
                def new_job():
                    # Новая должность
                    new_position = combo3.get()

                    # Определяем id новой должности
                    if flag: jobs_position_id = jbs_dep_id()[new_position]
                    else: jobs_position_id = dic_jbs_dep_id[new_position]

                    # Устанавливаем новый id должности сотруднику
                    if flag:
                        cur.execute('''
                        UPDATE employees
                        SET jobs_position_id = %(int)s
                        WHERE CONCAT(first_name, ' ', last_name) = %(str)s
                        ''', {'int': jobs_position_id, 'str': value})
                        conn.commit()
                    else:
                        emp_dict[value]['jobs_position_id'] = jobs_position_id
                        emp_dict[value]['jobs_position'] = new_position

                    mb.showinfo('Выполнено', f'{value} переведён в отдел {new_value}, на должность {new_position}')
                    window10.destroy()
                    window3.destroy()
                    all_pers()

                # Окно выбора должности из нового отдела
                window10 = Tk()
                window10.title('Выберите должность')

                Label(window10, text=value).pack()

                frame_window_10_1 = Frame(window10)
                frame_window_10_1.pack()

                Label(frame_window_10_1, text='Новый отдел: %s' % new_value).pack()

                # Выбор данных
                frame_window_10_2 = Frame(window10, borderwidth=3)
                frame_window_10_2.pack(fill=BOTH, expand=True)

                # new_jobs - доступные должности из нового отдела
                if flag: new_jobs = [i for i in jbs_dep()[new_value]]
                else: new_jobs = [i for i in jobs_and_department_dict[new_value]]

                combo3 = Combobox(frame_window_10_2, value=new_jobs, state='readonly')
                combo3.pack(fill=BOTH, side=LEFT, expand=True)

                button_new_job = Button(frame_window_10_2,
                    text='Выбрать должность', command=new_job).pack(fill=BOTH, side=LEFT, expand=True)


        window9 = Tk()
        window9.title('Перевод на другую должность / отдел')

        # Имя и фамилия сотрудника
        value = entry_change.get()

        Label(window9, text=value).pack()

        # Текущая должность и отдел
        frame_current_position = Frame(window9)
        frame_current_position.pack()

        # Текущая должность и отдел сотрудника + их id
        if flag:
            jobs_position_current = emp()[value]['jobs_position']
            jobs_position_id_current = emp()[value]['jobs_position_id']
            department_current = emp()[value]['department']
            department_id_current = emp()[value]['department_id']
        else:
            jobs_position_current = emp_dict[value]['jobs_position']
            jobs_position_id_current = emp_dict[value]['jobs_position_id']
            department_current = emp_dict[value]['department']
            department_id_current = emp_dict[value]['department_id']

        Label(frame_current_position, text='Текущий отдел: %s' % department_current).pack(fill=BOTH, expand=True)
        Label(frame_current_position,
              text='Текущая должность: %s' % jobs_position_current).pack(fill=BOTH, expand=True)


        # Другие должности в текущем отделе / Доступные отделы, кроме текущего
        if flag:
            jobs_position_othher = [i for i in jbs_dep()[department_current] if i != jobs_position_current]
            deps_other = [i for i in jbs_dep() if i != department_current]
        else:
            jobs_position_othher = [i for i in jobs_and_department_dict[department_current] if i != jobs_position_current]
            deps_other = [i for i in jobs_and_department_dict if i != department_current]


        # Выбор данных
        def combo_action_frame_transfer(event):
            global combo2, lab
            values = combo.get()
            lab.destroy()            # Закрываем lab, что бы текст не накладывался один на другой

            if values == 'Перевезти на другую должность':
                lab = Label(frame_transfer, text='Выберите должность')
                lab.grid(row=1, column=0, sticky='w')
                combo2 = Combobox(frame_transfer, value=jobs_position_othher, state='readonly', width=35)
                combo2.grid(row=1, column=1)
            else:
                lab = Label(frame_transfer, text='Выберите отдел')
                lab.grid(row=1, column=0, sticky='w')
                combo2 = Combobox(frame_transfer, value=deps_other, state='readonly', width=35)
                combo2.grid(row=1, column=1)


        frame_transfer = Frame(window9, borderwidth=3)
        frame_transfer.pack()

        Label(frame_transfer, text='Куда переводим сотрудника:').grid(row=0, column=0, sticky='w')

        combo = Combobox(frame_transfer,
            values=('Перевезти на другую должность', 'Перевезти в другой отдел'), state='readonly', width=35)
        combo.current(0)
        combo.grid(row=0, column=1)
        combo.bind('<<ComboboxSelected>>', combo_action_frame_transfer)

        global lab
        lab = Label(frame_transfer, text='Выберите должность')
        lab.grid(row=1, column=0, sticky='w')

        global combo2
        combo2 = Combobox(frame_transfer, value=jobs_position_othher, state='readonly', width=35)
        combo2.grid(row=1, column=1)


        # Кнопка 'Внести изменения'
        frame_transfer_button = Frame(window9, borderwidth=3)
        frame_transfer_button.pack(fill=BOTH, expand=True)

        new_job_or_department = Button(frame_transfer_button,
            text='Внести изменения', command=new_job_or_dep).pack(fill=BOTH, expand=True)


    def change_pay():

        if flag:
            if entry_change.get() not in emp():
                mb.showinfo('Ошибка', f'Сотрудника {entry_change.get()} нет в базе. Попробуйте ещё раз')
                return False
        else:
            if entry_change.get() not in emp_dict:
                mb.showinfo('Ошибка', f'Сотрудника {entry_change.get()} нет в базе. Попробуйте ещё раз')
                return False

        def change_pay_button():
            value = combo.get()

            if value == a:
                if flag:
                    cur.execute('''
                    UPDATE employees
                    SET pay = %(int)s
                    WHERE CONCAT(first_name, ' ', last_name) = %(str)s
                    ''', {'int': entry_combo.get(), 'str': name})
                    conn.commit()
                else:
                    emp_dict[name]['pay'] = entry_combo.get()

                mb.showinfo('Выполнено', f'Заработная плата {name} изменена на {entry_combo.get()}')
                window5.destroy()
                window3.destroy()
                all_pers()

            elif value == b:
                if flag:
                    cur.execute('''
                    UPDATE employees
                    SET pay = %(int)s
                    WHERE CONCAT(first_name, ' ', last_name) = %(str)s
                    ''', {'int': int(pay_current + (pay_current * (int(entry_combo.get())) / 100)), 'str': name})
                    conn.commit()
                else:
                    emp_dict[name]['pay'] = int(pay_current + (pay_current * (int(entry_combo.get())) / 100))

                mb.showinfo('Выполнено', f'Заработная плата {name} увеличена на {entry_combo.get()}%')
                window5.destroy()
                window3.destroy()
                all_pers()

            else:
                if flag:
                    cur.execute('''
                    UPDATE employees
                    SET pay = %(int)s
                    WHERE CONCAT(first_name, ' ', last_name) = %(str)s
                    ''', {'int': int(pay_current - (pay_current * (int(entry_combo.get())) / 100)), 'str': name})
                    conn.commit()
                else:
                    emp_dict[name]['pay'] = int(pay_current - (pay_current * (int(entry_combo.get())) / 100))

                mb.showinfo('Выполнено', f'Заработная плата {name} уменьшена на {entry_combo.get()}%')
                window5.destroy()
                window3.destroy()
                all_pers()


        window5 = Tk()
        window5.title('Изменение зарплаты')

        # Имя сотрудника
        name = entry_change.get()

        frame_init = Frame(window5)
        frame_init.pack()

        # Текущая зарплата сотрудника
        if flag: pay_current =emp()[name]['pay']
        else: pay_current = int(emp_dict[name]['pay'])

        Label(frame_init, text=name).pack()
        Label(frame_init, text='Текущая зарплата: %s' % pay_current).pack()

        frame_combo = Frame(window5, borderwidth=3)
        frame_combo.pack()

        a, b, c = 'Новая зарплата', 'Увеличить в %', 'Понизить в %'
        combo = Combobox(frame_combo, values=(a, b, c), state='readonly')
        combo.current(0)
        combo.pack(fill=BOTH, side=LEFT, expand=True)

        entry_combo = Entry(frame_combo, width=35)
        entry_combo.pack(fill=BOTH, side=LEFT, expand=True)

        frame_make_changes = Frame(window5, borderwidth=3)
        frame_make_changes.pack(fill=BOTH, expand=True)

        make_changes = Button(frame_make_changes,
            text='Внести изменения', command=change_pay_button).pack(fill=BOTH, expand=True)


        # Зарплаты других сотрудников на той же должности
        frame_pay_other = Frame(window5)
        frame_pay_other.pack()

        # id должности текущего сотрудника
        if flag: jobs_position_id_current = emp()[name]['jobs_position_id']
        else: jobs_position_id_current = emp_dict[name]['jobs_position_id']

        # Должность текущего сотрудника
        if flag: jobs_position_current = emp()[name]['jobs_position']
        else: jobs_position_current = emp_dict[name]['jobs_position']

        # Сотрудники и их зарплаты
        employyes_department_current = []
        if flag:
            for i in emp():
                if emp()[i]['jobs_position'] == jobs_position_current and emp()[i]['first_last_name'] != name:
                    employyes_department_current.append((emp()[i]['first_last_name'], emp()[i]['pay']))
        else:
            for i in emp_dict:
                if emp_dict[i]['jobs_position'] == jobs_position_current and emp_dict[i]['first_last_name'] != name:
                    employyes_department_current.append((emp_dict[i]['first_last_name'], emp_dict[i]['pay']))

        Label(frame_pay_other, text=f'Зарплаты других сотрудников на должности {jobs_position_current}:',
              font=('Arial', '10', 'italic')).pack()


        frame_pay_other_employees = Frame(window5)
        frame_pay_other_employees.pack()

        for employye in employyes_department_current:
            Label(frame_pay_other_employees,
                text='%s, зарплата: %s' % (employye[0], employye[1])).pack()

        window5.mainloop()


    def button_change_contacts():

        if flag:
            if entry_change.get() not in emp():
                mb.showinfo('Ошибка', f'Сотрудника {entry_change.get()} нет в базе. Попробуйте ещё раз')
                return False
        else:
            if entry_change.get() not in emp_dict:
                mb.showinfo('Ошибка', f'Сотрудника {entry_change.get()} нет в базе. Попробуйте ещё раз')
                return False

        def new_contact():
            value = entry_new_contact.get()

            if flag:
                cur.execute('''
                UPDATE employees
                SET phone = %(phone)s
                WHERE CONCAT(first_name, ' ', last_name) = %(name)s
                ''', {'phone': value, 'name': name})
                conn.commit()
            else:
                emp_dict[name]['phone'] = value

            mb.showinfo('Выполнено', f'Контакт {name} изменён на {value}')
            window7.destroy()
            window3.destroy()
            all_pers()

        window7 = Tk()
        window7.title('Изменить контакты')

        # Имя сотрудника
        name = entry_change.get()

        # Контакты сотрудника
        if flag: phone_current = emp()[name]['phone']
        else: phone_current = emp_dict[name]['phone']

        Label(window7, text=name).pack()
        Label(window7, text='Текущий контакт: %s' % phone_current).pack()

        frame1 = Frame(window7, borderwidth=3)
        frame1.pack(fill=BOTH, expand=True)
        label_new_contact = Label(frame1, text='Введите новые контакты').pack(fill=BOTH, side=LEFT, expand=True)
        entry_new_contact = Entry(frame1)
        entry_new_contact.pack(fill=BOTH, side=LEFT, expand=True)

        frame2 = Frame(window7, borderwidth=3)
        frame2.pack(fill=BOTH, expand=True)
        button_new_contact = Button(frame2, text='Изменить контакты', command=new_contact).pack(fill=BOTH, expand=True)

        window7.mainloop()


    def del_pers():

        if flag:
            if entry_change.get() not in emp():
                mb.showinfo('Ошибка', f'Сотрудника {entry_change.get()} нет в базе. Попробуйте ещё раз')
                return False
        else:
            if entry_change.get() not in emp_dict:
                mb.showinfo('Ошибка', f'Сотрудника {entry_change.get()} нет в базе. Попробуйте ещё раз')
                return False

        def del_pers_button():

            if flag:
                cur.execute('''
                DELETE
                FROM employees
                WHERE CONCAT(first_name, ' ', last_name) = %(name)s
                ''', {'name': name})
                conn.commit()
            else:
                emp_dict.pop(name)

            mb.showinfo('Выполнено', f'Сотрудник {entry_change.get()} удалён')
            window4.destroy()
            window3.destroy()
            window.destroy()
            start()

        window4 = Tk()
        window4.title('Удалить сотрудника')

        # Имя сотрудника
        name = entry_change.get()

        confirmation = Label(window4, text=f'Вы действительно хотите удалить {name}?').pack(fill=BOTH, expand=True)
        button_del = Button(window4, text='Удалить сотрудника', command=del_pers_button).pack(fill=BOTH, expand=True)


    window3 = Tk()
    window3.title('Сотрудники')
    window3.geometry('260x450')

    frame = Frame(window3)
    frame.pack(fill=BOTH, expand=True)

    scroll = Scrollbar(frame)
    scroll.pack(side=RIGHT, fill=Y)

    listbox = Listbox(frame, yscrollcommand=scroll.set, height=15, bg='lightgrey')

    employee = []  # (Имя, отдел, должность, зарплата, контакты)
    if flag:
        for name in emp():
            employee.append((name, emp()[name]['department'], emp()[name]['jobs_position'],
                             emp()[name]['pay'], emp()[name]['phone']))
    else:
        for name in emp_dict:
            employee.append((name, emp_dict[name]['department'], emp_dict[name]['jobs_position'],
                            emp_dict[name]['pay'], emp_dict[name]['phone']))

    for pers in employee:
        listbox.insert(END, 'Имя и фамилия:   ' + pers[0])
        listbox.insert(END, 'Должность:'.ljust(22) + pers[2])
        listbox.insert(END, 'Телефон:'.ljust(24) + str(pers[4]))
        listbox.insert(END, 'Зарплата:'.ljust(25) + str(pers[3]) + ' рублей')
        listbox.insert(END, ' - '*21)
    listbox.pack(fill=BOTH, expand=True)

    scroll.config(command=listbox.yview)

    # Пустая строка разделитель
    label_pass = Label(window3, text='').pack()

    label_text = Label(window3, text='Операции с сотрудниками', font=('Arial', '10', 'bold')).pack(fill=BOTH, expand=True)

    frame_change = Frame(window3, borderwidth=3)
    frame_change.pack(fill=BOTH, expand=True)
    label_change = Label(frame_change, text='Имя и фамилия сотрудника:').pack(fill=BOTH, side=LEFT, expand=True)

    # Ввод имя и фамилия сотрудника
    frame_entry = Frame(window3, borderwidth=3)
    frame_entry.pack(fill=BOTH, expand=True)
    entry_change = Entry(frame_entry)
    entry_change.pack(fill=BOTH, expand=True)

    # Кнопки
    frame_operation = Frame(window3, borderwidth=3)
    frame_operation.pack(fill=BOTH, expand=True)
    change_job_and_departmetn = Button(frame_operation,
        text='Перевезти на другую должность / отдел',
            command=button_chabge_job_and_department).pack(fill=BOTH, expand=True)
    change_pay_person = Button(frame_operation,
        text='Изменить зарплату', command=change_pay).pack(fill=BOTH, expand=True)
    change_contacts = Button(frame_operation,
        text='Изменить контакты', command=button_change_contacts).pack(fill=BOTH, expand=True)
    del_person = Button(frame_operation,
        text='Удалить сотрудника', command=del_pers).pack(fill=BOTH, expand=True)

    window3.mainloop()


def all_dep():

    def analytics_dep():
        window10 = Tk()

        values = combo.get()

        frame3 = Frame(window10)
        frame3.pack()

        Label(frame3, text='Отдел:').grid(row=0, column=0, sticky='w')
        Label(frame3, text=f'{values}').grid(row=0, column=1, sticky='w')

        # Средняя, максимальная и манимальная зарплаты в отделе
        avg_pay = 0
        max_pay = 0
        min_pay = math.inf
        count_employee = 0
        if flag:
            for name in emp():
                if emp()[name]['department'] == values:
                    avg_pay += emp()[name]['pay']
                    count_employee += 1
                    if max_pay < emp()[name]['pay']:
                        max_pay = emp()[name]['pay']
                    if min_pay > emp()[name]['pay']:
                        min_pay = emp()[name]['pay']
            else:
                if count_employee > 0:
                    avg_pay = int(avg_pay / count_employee)
                else:
                    avg_pay = 0
                    min_pay = 0
        else:
            for name in emp_dict:
                if emp_dict[name]['department'] == values:
                    avg_pay += emp_dict[name]['pay']
                    count_employee += 1
                    if max_pay < emp_dict[name]['pay']:
                        max_pay = emp_dict[name]['pay']
                    if min_pay > emp_dict[name]['pay']:
                        min_pay = emp_dict[name]['pay']
            else:
                if count_employee > 0:
                    avg_pay = int(avg_pay / count_employee)
                else:
                    avg_pay = 0
                    min_pay = 0

        # Вывод аналитики
        Label(frame3, text='Количество сотрудников:').grid(row=2, column=0, sticky='w')
        Label(frame3, text=str(count_employee) + ' человек').grid(row=2, column=1, sticky='w')
        Label(frame3, text='Средняя зарплата:').grid(row=3, column=0, sticky='w')
        Label(frame3, text=str(avg_pay) + ' руб').grid(row=3, column=1, sticky='w')
        Label(frame3, text='Максимальная зарплата:').grid(row=4, column=0, sticky='w')
        Label(frame3, text=str(max_pay) + ' руб').grid(row=4, column=1, sticky='w')
        Label(frame3, text='Минимальная зарплата:').grid(row=5, column=0, sticky='w')
        Label(frame3, text=str(min_pay) + ' руб').grid(row=5, column=1, sticky='w')

        # Пустая строка разделитель
        Label(frame3, text='').grid(row=6, column=0)

        Label(frame3, text='Сотрудник', font=('Arial', '10', 'bold')).grid(row=7, column=0, sticky='w')
        Label(frame3, text='Должость', font=('Arial', '10', 'bold')).grid(row=7, column=1, sticky='w')

        # Вывод сотрудников в отделе
        if flag:
            for num, name in enumerate(emp(), start=8):
                if emp()[name]['department'] == values:
                    Label(frame3, text=emp()[name]['first_last_name']).grid(row=num, column=0, sticky='w')
                    Label(frame3, text=emp()[name]['jobs_position']).grid(row=num, column=1, sticky='w')
        else:
            for num, name in enumerate(emp_dict, start=8):
                if emp_dict[name]['department'] == values:
                    Label(frame3, text=emp_dict[name]['first_last_name']).grid(row=num, column=0, sticky='w')
                    Label(frame3, text=emp_dict[name]['jobs_position']).grid(row=num, column=1, sticky='w')

        window10.mainloop()


    window8 = Tk()
    window8.title('Отделы и должности')

    # Доступные отделы и должности
    frame = Frame(window8)
    frame.pack()

    Label(frame, text='Отделы', font=('Arial', '10', 'bold')).grid(row=0, column=0, sticky='w')
    Label(frame, text='Должности', font=('Arial', '10', 'bold')).grid(row=0, column=1, sticky='w')

    if flag:
        for num, dep in enumerate(jbs_dep().keys(), start=1):
            jobs = ', '.join(jbs_dep()[dep])
            Label(frame, text=f'{dep}: ').grid(row=num, column=0, sticky='w')
            Label(frame, text=jobs).grid(row=num, column=1, sticky='w')
    else:
        for num, dep in enumerate(jobs_and_department_dict.keys(), start=1):
            jobs = ', '.join(jobs_and_department_dict[dep])
            Label(frame, text=f'{dep}: ').grid(row=num, column=0, sticky='w')
            Label(frame, text=jobs).grid(row=num, column=1, sticky='w')

    # Пустая строка - разделитель
    Label(window8, text='').pack()

    # Подробнее об отделах. Выпадающий список + кнопка
    frame2 = Frame(window8)
    frame2.pack(fill=BOTH, expand=True)

    if flag: combo = Combobox(frame2, values=(list(i for i in jbs_dep())), state='readonly')
    else: combo = Combobox(frame2, values=(list(i for i in jobs_and_department_dict)), state='readonly')
    combo.pack(fill=BOTH, side=LEFT, expand=True)
    Button(frame2, text='Подробнее об отделе', command=analytics_dep).pack(fill=BOTH, side=LEFT, expand=True)


    # Добавить отдел / добавить должност / Удалить отдел / Удалить должность
    def new_dep():

        def new_dep_action():
            values = ent.get()

            # Добавление отдела
            if flag:
                cur.execute('''
                INSERT INTO departments (title)
                VALUES (%(str)s)
                ''', {'str': values})
                conn.commit()
            else:
                global next_dep_id
                jobs_and_department_dict.update([(values, [])])   # Добавляем отдел
                dic_jbs_dep_id.update([(values, next_dep_id)])    # Добавляем id отдела
                next_dep_id += 1                                  # Увеличиваем id на 1

            mb.showinfo('Выполнено', f'Отдел {values} добавлен. Добавьте должности в отдел в следующем окне.')
            window11.destroy()
            window8.destroy()

            # Добавление должностей в новый отдел
            def new_job_on_dep():

                # Новая должность
                values2 = ent2.get()

                # id нового отдела
                if flag: values_id = jbs_dep_id()[values]

                # Добавляем должность в новый отдел
                if flag:
                    cur.execute('''
                    INSERT INTO jobs_position (title, department_id)
                    VALUES (%(str1)s, %(str2)s)
                    ''', {'str1': values2, 'str2': values_id})
                    conn.commit()
                else:
                    global next_job_id
                    jobs_and_department_dict.update([(values, (jobs_and_department_dict.get(values) + [values2]))])
                    dic_jbs_dep_id.update([(values2, next_job_id)])
                    next_job_id += 1

                mb.showinfo('Выполнено', f'В отдел {values} добавлена должность {values2}. '
                                         f'Можете добавить ещё одну должность.')
                ent2.delete(0, END)

            # Добавление должности в новый отдел
            window12 = Tk()
            window12.title('Добавить должности')

            frame6 = Frame(window12, borderwidth=3)
            frame6.pack()

            Label(frame6, text=f'Введите должность в отдел {values}').pack(fill=BOTH, side=LEFT, expand=True)
            ent2 = Entry(frame6)
            ent2.pack(fill=BOTH, side=LEFT, expand=True)

            frame7 = Frame(window12, borderwidth=3)
            frame7.pack(fill=BOTH, expand=True)
            Button(frame7, text='Добавить должность', command=new_job_on_dep).pack(fill=BOTH, side=LEFT, expand=True)

            window12.mainloop()


        window11 = Tk()
        window11.title('Добавить отдел')

        frame4 = Frame(window11, borderwidth=3)
        frame4.pack()

        Label(frame4, text='Введите новый отдел').pack(fill=BOTH, side=LEFT, expand=True)
        ent = Entry(frame4)
        ent.pack(fill=BOTH, side=LEFT, expand=True)

        frame5 = Frame(window11, borderwidth=3)
        frame5.pack(fill=BOTH, expand=True)
        Button(frame5, text='Добавить отдел', command=new_dep_action).pack(fill=BOTH, side=LEFT, expand=True)

        window11.mainloop()


    def del_dep():

        def del_dep_action():
            values = combo_dep.get()

            # id выбранного отдела
            if flag: values_id = jbs_dep_id()[values]
            else: values_id = dic_jbs_dep_id[values]

            # Удаляем всех сотрудников из отдела
            if flag:
                cur.execute('''
                DELETE FROM employees
                WHERE department_id = %(int)s
                ''', {'int': values_id})
            else:
                emp_dict_copy = [i for i in emp_dict]
                for name in emp_dict_copy:
                    if emp_dict[name]['department'] == values:
                        emp_dict.pop(name)

            # Должности выбранного отдела
            if flag: jobs = jbs_dep()[values]
            else: jobs = jobs_and_department_dict[values]
            jobs_copy = [i for i in jobs]     # На jobs_copy будем ссылаться после удаления jobs

            # Удаляем все должности
            if flag:
                while jobs:
                    cur.execute('''
                    DELETE FROM jobs_position
                    WHERE title = %(str)s
                    ''', {'str': jobs.pop()})

            # Удаляем отдел
            if flag:
                cur.execute('''
                DELETE FROM departments
                WHERE title = %(str)s
                ''', {'str': values})
                conn.commit()
            else:
                jobs_and_department_dict.pop(values)
                dic_jbs_dep_id.pop(values)            # Дополнительно удаляем id отдела
                for job in jobs:                      # Удаляем id всех должностей
                    dic_jbs_dep_id.pop(job)

            mb.showinfo('Выполнено', f"Отдел {values} удалён. Также удалены должности: {', '.join(jobs_copy)} "
                                     f"и все сотрудники.")
            window13.destroy()
            window8.destroy()
            window.destroy()
            start()


        window13 = Tk()
        window13.title('Удалить отдел')

        frame4 = Frame(window13, borderwidth=3)
        frame4.pack(fill=BOTH, expand=True)

        Label(frame4, text='Выберите отдел для удаления').pack(fill=BOTH, side=LEFT, expand=True)

        # deps - все отделы
        if flag: deps = [i for i in jbs_dep()]
        else: deps = [i for i in jobs_and_department_dict]
        combo_dep = Combobox(frame4, values=deps, state='readonly')
        combo_dep.pack(fill=BOTH, side=LEFT, expand=True)

        frame5 = Frame(window13, borderwidth=3)
        frame5.pack(fill=BOTH, side=LEFT, expand=True)
        Button(frame5, text='Удалить отдел', command=del_dep_action).pack(fill=BOTH, expand=True)
        Label(frame5, text='Внимани! Будут также удалены все должности и сотрудники.').pack(fill=BOTH, expand=True)

        window13.mainloop()


    def new_job():

        def new_job_action():

            new_deps = combo_new_job.get()      # отдел, куда добавляем должность
            new_jobs = ent.get()                # должность

            # id выбранного отдела
            if flag: new_deps_id = jbs_dep_id()[new_deps]
            else: new_deps_id = dic_jbs_dep_id[new_deps]

            # Добовляем должность
            if flag:
                cur.execute('''
                INSERT INTO jobs_position (title, department_id)
                VALUES (%(str)s, %(int)s)
                ''', {'str': new_jobs, 'int': new_deps_id})
                conn.commit()
            else:
                global next_job_id
                jobs_and_department_dict.update([(new_deps, (jobs_and_department_dict.get(new_deps) + [new_jobs]))])
                dic_jbs_dep_id.update([(new_jobs, next_job_id)])
                next_job_id += 1

            mb.showinfo('Выполнено', f'Дожность {new_jobs} добавлена в отдел {new_deps}')
            ent.delete(0, END)
            window8.destroy()
            all_dep()


        window14 = Tk()
        window14.title('Добавить должность')

        frame4 = Frame(window14, borderwidth=3)
        frame4.pack()

        Label(frame4, text='Выберите отдел').grid(row=0, column=0, sticky='w')

        #  deps - все отделы
        if flag: deps = [i for i in jbs_dep()]
        else: deps = [i for i in jobs_and_department_dict]
        combo_new_job = Combobox(frame4, values=deps, state='readonly')
        combo_new_job.grid(row=0, column=1)

        Label(frame4, text='Введите должность').grid(row=1, column=0, sticky='w')
        ent = Entry(frame4)
        ent.grid(row=1, column=1, ipadx=10,sticky='e')

        frame5 = Frame(window14, borderwidth=3)
        frame5.pack(fill=BOTH, side=LEFT, expand=True)

        Button(frame5, text='Добавить должность', command=new_job_action).pack(fill=BOTH, side=LEFT, expand=True)

        window14.mainloop()


    def del_job():

        # Функция меняет должности при смене отдела
        def job_replace(event):
            global combo_job
            if flag: job = [i for i in jbs_dep()[combo_dep.get()] if combo_dep.get()]
            else: job = [i for i in jobs_and_department_dict[combo_dep.get()] if combo_dep.get()]
            combo_job = Combobox(frame4, values=job, state='readonly')
            combo_job.grid(row=1, column=1)

        def del_job_action():

            # Выбранная должность
            values = combo_job.get()

            # id выбранной должности
            if flag: values_id = jbs_dep_id()[values]

            # Удаляем всех сотрудников
            if flag:
                cur.execute('''
                DELETE FROM employees
                WHERE jobs_position_id = %(str)s
                ''', {'str': values_id})
            else:
                emp_dict_copy = [i for i in emp_dict]
                for name in emp_dict_copy:
                    if emp_dict[name]['jobs_position'] == values:
                        emp_dict.pop(name)

            # Удаляем должность
            if flag:
                cur.execute('''
                DELETE FROM jobs_position
                WHERE jobs_position_id = %(str)s
                ''', {'str': values_id})
                conn.commit()
            else:
                jobs_and_department_dict[combo_dep.get()].remove(values)
                dic_jbs_dep_id.pop(values)        # Удаляем id должности

            mb.showinfo('Выполнено', f'Должность {values} удалена. Также удалены все сотрудники.')
            window8.destroy()
            window15.destroy()
            window.destroy()
            start()


        window15 = Tk()
        window15.title('Удалить должность')

        frame4 = Frame(window15, borderwidth=3)
        frame4.pack()

        Label(frame4, text='Выберите отдел').grid(row=0, column=0, sticky='w')

        # Все отделы
        if flag: deps = [i for i in jbs_dep()]
        else: deps = [i for i in jobs_and_department_dict]

        combo_dep = Combobox(frame4, values=deps, state='readonly')
        combo_dep.grid(row=0, column=1)
        combo_dep.current(0)
        combo_dep.bind('<<ComboboxSelected>>', job_replace)

        Label(frame4, text='Выберите должность').grid(row=1, column=0, sticky='w')

        # Должности из отдела
        if flag: job = [i for i in jbs_dep()[combo_dep.get()]]
        else: job = [i for i in jobs_and_department_dict[combo_dep.get()]]

        global combo_job
        combo_job = Combobox(frame4, values=job, state='readonly')
        combo_job.grid(row=1, column=1)

        frame5 = Frame(window15, borderwidth=3)
        frame5.pack(fill=BOTH, expand=True)

        Button(frame5, text='Удалить должность', command=del_job_action).pack(fill=BOTH, expand=True)
        Label(frame5, text='Внимание! Будут удалены все сотрудники!').pack(fill=BOTH, expand=True)

        window15.mainloop()


    frame3 = Frame(window8)
    frame3.pack(fill=BOTH, expand=True)

    # Кнопки
    Button(frame3, text='Добавить отдел', command=new_dep).pack(fill=BOTH, expand=True)
    Button(frame3, text='Добавить должность', command=new_job).pack(fill=BOTH, expand=True)
    Button(frame3, text='Удалить отдел', command=del_dep).pack(fill=BOTH, expand=True)
    Button(frame3, text='Удалить должность', command=del_job).pack(fill=BOTH, expand=True)

    window8.mainloop()


def start():
    global window
    window = Tk()
    window.title('База сотрудников')
    window.geometry('200x350')

    # Расчёт значений для аналитики. Средняя, минимальная и максимальная зарплаты; количество сотрудников
    if flag:
        cur.execute('''
        SELECT COUNT(*), AVG(pay), MIN(pay), MAX(pay)
        FROM employees
        ''')
        res = cur.fetchall()
    else:
        avg_pay = 0
        max_pay = 0
        min_pay = math.inf
        for i in emp_dict:
            avg_pay += emp_dict[i]['pay']
            if emp_dict[i]['pay'] > max_pay:
                max_pay = emp_dict[i]['pay']
            if emp_dict[i]['pay'] < min_pay:
                min_pay = emp_dict[i]['pay']
        else: avg_pay = avg_pay / len(emp_dict)
        res = [(len(emp_dict), avg_pay, min_pay, max_pay)]

    # Аналитика
    quantity_pers = Label(window, text=f'Количество сотрудников: {res[0][0]}').pack(fill=BOTH, expand=True)
    average_salary = Label(window, text=f'Средняя зарплата: {int(res[0][1])}').pack(fill=BOTH, expand=True)
    min_salary_con = Label(window, text=f'Минимальная зарплата: {res[0][2]}').pack(fill=BOTH, expand=True)
    max_salary_con = Label(window, text=f'Максимальная зарплата: {res[0][3]}').pack(fill=BOTH, expand=True)

    # Кнопки
    all_person = Button(window, text='Сотрудники', command=all_pers).pack(fill=BOTH, expand=True)
    new_person = Button(window, text='Добавить сотрудника', command=new_pers).pack(fill=BOTH, expand=True)
    departments = Button(window, text='Отделы и должности', command=all_dep).pack(fill=BOTH, expand=True)

    window.mainloop()


start()