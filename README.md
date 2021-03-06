# Employee-base
База сотрудников на предприятии. База хранится в PostgreSQL. Графический интерфейс реализован на tkinter.

Программа поддерживает следующие функции:
добавление и удаление сотрудников;
добаление и удаление отделов и должностей;
перемещение сотрудников между отделами и должностями;
изменение зарплаты и контактов.

Доступна информация по всему предприятию, а так же по каждому отделу:
общее число сотрудников; средняя, минимальная и максимальная зарплаты; список всех сотрудников.

Вся информация синхронизируется с базой при внесении любых изменений.

Реализованы интересные (по моему мнению) и сложные (для меня, на момент написания программы) фишки. Например, когда мы переводим сотрудника в другой отдел, нужно выбрать отдел из выпадающего списка. При этом во втором выпадающем списке, автоматически изменяются должности на актуальные (из выбранного отдела в первом выпадающем списке).

Из за того, что на GitHub нельзя загрузить локальную базу PostgreSQL, было принято решение сделать ветвление работы программы.
Была введена переменная flag (в модуле function).
При:
flag = 1, программа будет работать с подключением к базе данных PostgreSQL.
flag = 0 (по умолчанию), программа будет импортировать готовые словари из модуля function_input, имитирующие работу с базой данных.

В PostgreSQL хранится 3 таблицы:

employees: employee_id, first_name, last_name, middle_name, pay, phone, department_id, jobs_position_id

departments: department_id, title

jobs_position: jobs_position_id, title, department_id

В талице сотрудников нельзя увидеть их должности и отделы. Есть только id. По этим id таблицы можно скрещивать. Такое разделение позволяет в будущем без проблем расширять программу. Допустим, если в таблицу departments (отделы), нужно будет добавить колонки: управляющий и т.д.

Что бы не писать повторяющийся код в модуле function реализованы функции, которые скрещивают отделы.
