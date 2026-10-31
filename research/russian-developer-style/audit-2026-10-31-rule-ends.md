# Audit: rules with no end, 2026-10-31

The yardstick is `apm-authoring` rule 4 (*Fix a bad output where the rule stops*), the rule 2 paragraph on an example
that needs a caveat after it, and `final-review` item 3. The template is `51b8d41`, the same fix in
english-developer-style 2.2.0. Measured results are under `cases/`. Line numbers are at `51b8d41`, under
`agent-packages/russian-developer-style/.apm/skills/russian-developer-style/`.

Provenance: every rule below came in with the package in `9e9ecc5` from the phase 1–3 synthesis in this directory;
`3024f02` reordered the §3 PR line to why-before-what and left the module's copy in the old order. None was added
after a bad output, so there are no older rules to drop first.

## Fixed

| Class | Where | Quote | Input where it misfires | Fix |
| --- | --- | --- | --- | --- |
| A | `SKILL.md:121`, `SKILL.md:321-331`, `modules/errors-logs.md:19-32` | «Шаблон «Не удалось `<действие>`» + причина (если известна) + что делать»; «Что делать дальше — конкретное действие или ссылка» | `setFetchSize(-1)`: the message names the value and the rule; «Укажите неотрицательное число» undoes the input the message already names, and «Не удалось установить…» wraps a rejected argument as a failed operation | lead with what failed or what is wrong with the input; an action only where the fix is not undoing the named input; what else a message carries is `telemetry-authoring` |
| B | `modules/errors-logs.md:39-40`, `examples/before-after.md:263-274` | «Значение порта `99999` вне диапазона. Укажите число от 1 до 65535» | the canonical validation example is the case above: the action repeats the range | `Порт должен быть от 1 до 65535, получено 99999`, no action |
| A | `modules/errors-logs.md:69-73` | «Формат: «`<Поле>`: `<что не так>`. `<Подсказка>`.»» | «Пароль: 6 символов из 8 минимум. Добавьте ещё 2»: the hint restates the rule | a hint only where «что не так» does not already say what is allowed |
| A | `modules/errors-logs.md:56-65` | «`<Что произошло>`. `<Что система сделала или сделает>`. `<Что можно сделать>`.» | «Параметр `retries` не задан. Использовано значение 3»: setting the parameter is the obvious step (the example's third sentence also named another key, `retry.max_attempts`) | the third part only where something must be changed, not only known; the `retries` example loses it |
| A | `modules/errors-logs.md:131-138` | «`<Что сломалось>`. `<Что сделать руками>`. `<Ссылка на runbook или дашборд>`.» | an alert for a service with no runbook: the slot invites an invented URL | the link only where a runbook or dashboard exists |
| C | `SKILL.md:123-125`, `modules/errors-logs.md:95,113` | «Указывайте идентификаторы… trace id, имя сервиса, ключ записи»; «без request_id такой лог бесполезен» | `INFO Сервис запущен на порте 8080`: no request, no record; the module's own INFO examples carry no id | identifiers where the event belongs to a request or a record; the content of a record is `telemetry-authoring` |
| D | `modules/ui-strings.md:62`, `SKILL.md:314` | «вопрос про результат + важное уточнение» (SKILL.md: «если действие необратимо») | «Выйти из аккаунта?» needs nothing after the question; SKILL.md's condition drops the clarification from the module's own «Сбросить пароли всех участников?» | both carry «если действие необратимо или задевает других» |
| C | `SKILL.md:140-142` | «После пустой строки — тело, объясняющее зачем» | a commit that fixes a typo in README: the subject is the whole message | delete the body rule, hand the slots to `change-description-authoring`; the subject line also stops calling «исправляет» the imperative mood and accepts the project's form («исправляет» or «исправить») |
| C | `SKILL.md:143-145`, `modules/code-comments.md:117-164` | «Зачем, что сделано, как проверить, какие риски»; «Минимальный комплект — три коротких блока» under headings, «Что» before «Зачем» | a one-line dependency bump: four blocks under headings around one sentence; the module also contradicts SKILL.md's why-first order | delete the copies, keep the wording rules (no «В этом PR были внесены изменения»), hand the slots to `change-description-authoring` |
| B | `examples/before-after.md:489-515` | the «Стало» of a one-change PR under three headings | same as above: the example is copied | two sentences, why first, no headings |
| A, B | `SKILL.md:134-135`, `SKILL.md:356-357`, `modules/code-comments.md:54-61`, `examples/before-after.md:393-424` | «Дальше — параметры, возвращаемое значение, ошибки»; the example's «Args: path: путь к файлу конфигурации» | `func (s *Set) Len() int`: one sentence is the whole comment; the example itself commits the module's antipattern «повтор имени без значения» | a parameter, a return value, or an error gets a line only where there is something to say beyond the name and the type; which slots a doc comment has is the doc-comment skill of the language; the example loses the `path` line |
| D | `SKILL.md:394-412` | «Жанровые форматы соблюдены: коммит, ошибка, changelog, PR?» | every genre's full template applied to every input | an item applies only under its rule's condition; the error item carries it |

## Left alone

- Empty states (`SKILL.md:313`, `modules/ui-strings.md:52-56`): «что произошло и что делать» has no condition for a list
  the user cannot fill, but the baseline did not misfire on one (`cases/empty-mentions`, 4 of 4 runs without an
  action), and a draft that added the condition cost Sonnet the action where it belongs (`cases/empty-alert-rules`, 0
  of 2 against 1 of 2 at the baseline). The draft was reverted.
- §3 changelog line (`SKILL.md:137-139`): «Список глагольных пунктов… Один пункт — одно изменение» constrains wording
  and granularity, not which slots an entry has. The breaking-change example in `before-after.md:546-562` is a real
  variant, shown once.
- Review replies (`SKILL.md:146-147`, `modules/code-comments.md:166-192`): agreement is already «Поправил, спасибо»;
  disagreement asks for an argument, and the example only «по возможности».
- Inline comments (`modules/code-comments.md:8-50`): «Что не комментировать» and the length limit end the rule.
- README genre (`SKILL.md:126-127`): «Сначала минимальный путь… затем варианты» is ordering, not a slot list; an overlap
  with `docs-page-authoring` but a one-line one.
- Progress text (`modules/ui-strings.md:160`): «Это может занять до минуты» already has its condition.
- The 500 and network examples in `modules/errors-logs.md:45-50` and `before-after.md:289-314`: the fix there is not
  undoing an input, so the action belongs; they are long, but the rule now says when to stop.
- §4, §5, §6, §10 and the wording items of §11: they constrain text, not what it contains.
- `.instructions.md:11`: «go through the same checklist» is about invoking the skill, not about filling every item.
- `french-developer-style` has the same genre list; not in scope here.

## Fixed but not measured

The cases under `cases/` measure the error action, the commit body, the PR slots, and the docstring slots. These
fixes have no case; each applies the measured error rule, or a condition the skill already stated elsewhere, to a
neighboring template:

- the form-validation hint, and the deleted «Добавьте ещё 2» and «Поменяйте даты местами» (the error rule: the hint
  undoes the named value);
- the warning's third fragment (the same rule, for a parameter the warning names);
- the operator runbook link (the slot invited an invented URL; no run has shown one);
- log identifiers (handed to `telemetry-authoring`, whose cases cover record content);
- confirmations (`SKILL.md` already had the condition).

The error template also loses «повторить позже» as an example of an action and keeps the old advice to name a technical
step instead of «попробуйте позже».
