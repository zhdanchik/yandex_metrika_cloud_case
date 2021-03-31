# Получение данных через `Logs API`
`Logs API` позволяет выгрузить сырые данные со счетчика.

Документация по `Logs API` - https://yandex.ru/dev/metrika/doc/api2/logs/intro.html

Данные для этого кейса также доступны на Яндекс.Диске - https://disk.yandex.ru/d/sUmQmh_MnQWL4g?w=1

## Получаем токен
Для работы с API необходимо получить свой токен - https://yandex.ru/dev/oauth/doc/dg/tasks/get-oauth-token.html

Создаем приложение тут (указываем права для чтения в Яндекс.Метрике) - https://oauth.yandex.ru/client/new

Переходим по ссылке вида - `https://oauth.yandex.ru/authorize?response_type=token&client_id=<идентификатор приложения>`

Полученный токен можно сохранить в домашнюю директорию в файл `.yatoken.txt`

# Получение данных тестового счетчика с `Яндекс.Диска`
Для показательного очного семинара/воркшопа, или, если не получается по каким-то причинам получить данные из `LogsAPI`, были заготовлдены CSV с выгрудженными данными из `LogsAPI` тестового счетчика.

Хиты: https://disk.yandex.ru/d/MoSoXW6VzAP0bQ
Визиты: https://disk.yandex.ru/d/ywvr6YM3B95i0A

Нужно эти файлы скачать и положить в папочку репозитория для дальнейшей работы.

В файле `some_funcs` есть метод, `get_file_from_yadisk(file_link, file_name)` который копирует ровно 1 файл по ссылке из Яндекс.Диска `file_link` и сохраняет его на диск по пути `file_name`

Ожидается, что, выполняя ячейки ниже, вы будете находится в директории с репозиторием (`/yandex_metrika_cloud_case`)

# Загрузка данных в `ClickHouse`

## Подключение и настройка
https://cloud.yandex.ru/docs/managed-clickhouse/
(см. слайды)

##  Функции для интеграции с ClickHouse

В файле `some_funcs` есть класс `simple_ch_client` для работы с ClickHouse

Сначала надо создать экземпляр класса, инициализировав его начальными параметрами - хост, пользователь, пароль и путь к сертификату
`simple_ch_client(CH_HOST, CH_USER, CH_PASS, cacert)`

В классе есть 4 метода:
* `.get_version()` - получает текущую версию ClickHouse. Хороший способ проверить, что указанные при инициализации параметры работают
* `.get_clickhouse_data(query)` - выполняет запрос `query` и возвращает результат в текстовом формате
* `.get_clickhouse_df(query)` - выполняет запрос `query` и возвращает результат в виде DataFrame
* `.upload(table, content)` - загружает таблицу `content`, которая подается в текстовом формате в таблицу ClickHouse'а с именем `table`


## Проверяем ClickHouse
Используя заговленные выше переменные проверим доступ до сервера (как в документации https://cloud.yandex.ru/docs/managed-clickhouse/operations/connect#connection-string)
Этот метод реализован в методе `.get_version()` класса для работы с ClickHouse
При успешном подключении не произойдет никакой ошибки при выполнении этого метода, и он сам вернет версию сервера ClickHouse (например `21.3.2.5`)
