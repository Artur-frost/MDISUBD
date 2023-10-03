# Общая информация
Kudlasevich Artur 153505 "Аналог Booking.com".

# Ссылка на схему:
https://drawsql.app/teams/artur-kudl/diagrams/mdisubd-1

# Описание:
Основная задача проекта заключается в предоставлении возможости забранировать жилье в аренду.

Авторизация пользователя:

Пользователи должны иметь возможность зарегистрироваться и войти в систему.

Управление пользователями (CRUD):

Администратор должен иметь возможность создавать новых пользователей, просматривать, редактировать и удалять существующие учетные записи. Пользователи должны иметь возможность изменять свои учетные данные (например, имя, адрес электронной почты, пароль и так далее).

Система ролей:

Должна быть реализована система ролей, позволяющая определять доступ к определенным функциям в зависимости от роли пользователя (например, администратор, модератор, клиент). Администратор должен иметь права на управление ролями пользователей.

Журналирование действий пользователя:

Система должна фиксировать действия пользователей, такие как вход в систему, изменение данных профиля, бронирование, отмена заказов и так далее. Логи должны включать информацию о времени и дате события, идентификаторе пользователя, выполнившего действие, а также описании самого действия. Администратор и модераторы должны иметь доступ к журналам для мониторинга и анализа действий пользователей.

Основные роли и их задачи

1. Администратор:

•	Создание новых предложений.
 
•	Редактирование / удаление уже имеющихся предложений. 
 
•	Просмотр логов.
 
•	Добавление в систему модераторов.
 
•	Просмотр профилей пользователей (больше возможностей, чем у модератора).

2. Модератор:

•	Просмотр и ответ на вопрос пользователя.
 
•	Просмотр профилей пользователей.

3. Пользователь:

•	Регистрация.

•	Авторизация.
 
•	Создание профиля.
  
•	Просмотр профиля.
 
•	Редактирование профиля.
 
•	Просмотр предложений.
 
•	Оформление заказа.
 
•	Отмена заказа.

1. Предложение:

   Поля:

   ```
   Апартамены (apartment_id): int.       
   Внешний ключ, связанный с таблицей "Апартаменты".      
   Стоимость за сутки (price_per_night): double precision.      
   Дни проживания (stay_days): int.       
   Страна (country): varchar(255).     
   Адресс (address): varchar(255).
   ```
   
2. Апартаменты:

   Поля:

   ```
   Тип (apartment_type): varchar(255).
   Количество комнат (num_of_rooms): int.
   Количество этажей (num_of_floors): int.
   Количество спальных мест (num_of_beds): int.
   ```
   
3. Заказ:

   Поля:

   ```
   Предложение (listing_id): int.
   Внешний ключ, связанный с таблицей "Предложение".
   Итоговая цена (total_price): double precision.
   Дата (order_date): date.
   Заказчик (customer_id): int.
   Внешний ключ, связанный с таблицей "Пользователи".
   ```
   
4. Вопрос:

   Поля:

   ```
   Пользователь (client_id): int.
   Внешний ключ, связанный с таблицей "Пользователи".
   Статус (status): bool.
   Вопрос (question_text): varchar(255).
   Ответ (answer_text): varchar(255).
   ```
   
5. Тип апартаментов:

   Поля:

   ```
   Название (type_name): varchar(255).
   ```
   
6. Действия: 

   Поля:

   ```
   Действие (action): varchar(255).
   Дата (action_date): date.
   Пользователь (user_id): int.
   Внешний ключ, связанный с таблицей "Пользователи".
   Описание (description): varchar(255).
   ```
   
7. Отзывы:

    Поля:

   ```
   Текст (review_text): varchar(255).
   Оценка (rating): int.
   Пользователь (user_id): int.
   Внешний ключ, связанный с таблицей "Пользователи".
   Предложение (offer_id): int.
   Внешний ключ, связанный с таблицей "Предложение".
   ```
   
8. Акции:

   Поля:

   ```
   Название (promotion_name): varchar(255).
   Описание (description): varchar(255).
   Скидка (discount): decimal.
   Дата (promotion_date): date.
   Предложение (offer_id): int.
   Внешний ключ, связанный с таблицей "Предложение".
   ```
   
9. Роли:

   Поля:

   ```
   Тип роли (role_type): varchar(255).
   Пользователь (user_id): int.
   Внешний ключ, связанный с таблицей "Пользователи".
   ```
   
10. Удобства:

   Поля:

   ```
   Название (name): varchar(255).
   Описание (description): varchar(255).
   Внешний ключ, связанный с таблицей "Апартаменты".
   ```

Связи:

```
Один к одному:
Апартаменты - Предложение.
```

```
Многие к одному:
Предложения - Заказы.
Отзывы - Предложения.
Отзывы - Пользователи.
Пользователи - Роли.
Пользователи - Действия.
Апартаменты - Тип апартаментов.
Акции - Предложения.
Заказы - Пользователи.
```

```
Многие ко многим:
Апартамены - Удобства.
```
