В драйвере JDBC метод `PgStatement.setFetchSize(int rows)` теперь отклоняет отрицательное значение:

```java
if (rows < 0) {
  throw new PSQLException(GT.tr("<message>", rows), PSQLState.INVALID_PARAMETER_VALUE);
}
```

`GT.tr` берёт русский перевод шаблона из `messages_ru.po` и форматирует его через `java.text.MessageFormat`, так что
`{0}` подставляет `rows`. Исключение получает приложение, которое вызвало `setFetchSize`, и после него в этом вызове
ничего не выполняется.

Напишите `msgstr` для этого сообщения: только текст шаблона, как он стоит между кавычками в `.po`.
