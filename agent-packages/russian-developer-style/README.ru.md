# russian-developer-style

> English version: [README.md](README.md).

Стилевые рекомендации для русскоязычного текста, обращённого к разработчикам
и пользователям программ: README и документация в Markdown, комментарии
в коде, docstring/Javadoc/KDoc, сообщения коммитов, описания PR, changelog,
UI-строки, сообщения об ошибках и логи, файлы локализации (`.po`,
`.properties`, JSON i18n). Длина не важна: однострочный `msgstr` в `.po`
покрывается скиллом так же, как страница README.

Скилл срабатывает на любые задачи с русским developer-текстом — написание,
правку, перевод, локализацию, ревью, проверку, сверку, аудит. Триггерные
русские глаголы: «напиши», «переведи», «локализуй», «проверь»,
«перепроверь», «сверь», «отревью». Если запрос затрагивает русский текст,
скилл подключается *до* ответа агента.

Скилл кодирует то, что плохо ловится линтерами: голос, структуру жанров,
борьбу с канцеляритом и LLM-почерком, тон сообщений об ошибках, выбор
терминологии. Механические проверки (орфография, кавычки, тире, неразрывные
пробелы, ё/е) остаются за LanguageTool, yaspeller и typograf.js.

## Install

```sh
apm install Netcracker/qubership-ai-packages/agent-packages/russian-developer-style
```

Или вручную в `apm.yml`:

```yaml
dependencies:
  apm:
    - Netcracker/qubership-ai-packages/agent-packages/russian-developer-style@<ref>
```

Замените `<ref>` на нужный release tag, ветку или commit SHA, например
`v1.0.0`.

Затем выполните `apm install`, чтобы установить скилл и сгенерированные
instruction outputs.

## Что внутри

- Короткая инструкция-триггер, которая срабатывает на любые задачи
  с русским developer-текстом (Markdown, комментарии, коммиты, PR,
  changelog, ошибки, логи, UI, файлы локализации). Перечисляет триггерные
  глаголы на русском и английском, чтобы покрыть и «напиши», и «перепроверь
  перевод».
- Основной файл скилла
  ([`SKILL.md`](.apm/skills/russian-developer-style/SKILL.md)) — голос,
  жанровые настройки, редактура LLM-черновиков, политика канцелярита и
  длинного тире, терминология, чеклист, исключения.
- Модули:
  [`ui-strings.md`](.apm/skills/russian-developer-style/modules/ui-strings.md),
  [`errors-logs.md`](.apm/skills/russian-developer-style/modules/errors-logs.md),
  [`code-comments.md`](.apm/skills/russian-developer-style/modules/code-comments.md).
- Стартовый глоссарий
  ([`glossary.md`](.apm/skills/russian-developer-style/glossary.md)) с
  ~50 ИТ-терминами и пометками «переводить / не переводить».
- Сборник примеров «до / после»
  ([`examples/before-after.md`](.apm/skills/russian-developer-style/examples/before-after.md)).
- Стартовые конфиги линтеров под Markdown и русский текст
  ([`lint/`](.apm/skills/russian-developer-style/lint/)).

## Пара к линтерам

Скилл сознательно молчит про то, что лучше делают инструменты. Используйте
рядом:

- **LanguageTool** с профилем `ru-RU` — грамматика, повторы, согласования.
  Ожидайте false-positive на коде в прозе; настройте игнор-блок для
  inline-кода и fenced code blocks.
- **yaspeller** — орфография с пользовательским словарём. Апстрим
  заархивирован, держите свой форк/пин и расширяйте словарь продуктовых
  терминов.
- **typograf.js** — кавычки-«ёлочки», длинное тире, неразрывные пробелы,
  пробелы между числом и единицей измерения. Не пропускайте через него код.
- Собственные проверки на placeholders в ICU MessageFormat / Fluent и на
  словарь запрещённых терминов из глоссария.

## Обновление

`apm outdated` показывает новые версии, `apm deps update` обновляет.

## Источники и история

Скилл синтезирован из четырёхэтапного исследования русских стилевых
гайдов и LLM-почерка (Контур.Гайды, Microsoft RU L10n, Ozon Tech
styleguide, Mozilla L10n, Нора Галь, академические работы про tells
LLM). Промпты и заметки лежат в
[`research/russian-developer-style/`](../../research/russian-developer-style/),
если их вынесут туда в дальнейшем.
