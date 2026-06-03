# Бриф deep research: внутрикорпоративный магазин APM-пакетов

| Поле | Значение |
|---|---|
| Дата | 2026-05-29 |
| Инструмент | deep-research (fan-out поиск, fetch, adversarial-верификация, синтез) |
| Run ID | `wf_ab15b1cc-858` |
| Task ID | `w1c7e06vo` |
| Результат | [deep-research-report.md](./deep-research-report.md) |

Это бриф, отправленный в deep research, — как есть, для истории. Часть «установленных фактов» отчёт позже уточнил или опроверг (в первую очередь byte-совместимость артефакта между рантаймами). Сверяйтесь с разделом «Опровергнутые утверждения» в отчёте.

## Контекст и задача

Проектируется внутрикорпоративный магазин APM-пакетов (Microsoft APM, `github.com/microsoft/apm`) с двумя слоями:

1. публичный GitHub-слой для OSS-пакетов, находимый без доступа к корпсети;
2. корпоративный слой, где есть JFrog Artifactory и часть пакетов лежит во внутреннем GitLab.

Цель — end-to-end demo: производитель публикует пакет, потребитель находит его в магазине и подключает.

Требования:

- видеть перечень доступных пакетов;
- видеть состав пакета (количество зависимостей, skills, instructions);
- отслеживать выход версий (история версий желательна);
- программный API для ai-агента — nice-to-have, не блокирует demo.

Пакеты лежат в разных git-репозиториях, развиваются разными командами. Demo готовится в публичном форке `github.com/vlsi/qubership-ai-packages` (monorepo с пакетами под `agent-packages/`: `apm-authoring` с instructions и skill; `go-microservice-dev-kit` — umbrella с 6 транзитивными кросс-репо зависимостями на ветке `feat/agent-packages`).

## Установленные факты (по исходникам APM)

Переданы как вводные с пометкой «не перепроверять».

- В APM три механизма доставки:
  - **git-marketplace**: блок `marketplace:` в `apm.yml` компилируется `apm pack` в `.claude-plugin/marketplace.json` (формат Anthropic Claude Code) плюс опционально `.agents/plugins/marketplace.json` для Codex; подключение через `apm marketplace add`, установка через `apm install pkg@mkt`;
  - **HTTP-реестр**: блок `registries:` плюс `apm publish` по Registry HTTP API; клиент за флагом `apm experimental enable registries`;
  - **bundle**: `apm pack` собирает самодостаточный tar для `apm install ./bundle`.
- Registry HTTP API имеет ровно три эндпоинта: `GET /v1/packages/{owner}/{repo}/versions`, `GET …/versions/{version}/download`, `PUT …/versions/{version}`. Эндпоинта «список пакетов» нет.
- В git-marketplace нет истории версий: каждая запись несёт один разрезолвленный `ref` плюс `sha` (массива `versions[]` нет).
- Команды обнаружения (`apm marketplace browse`, top-level `apm search QUERY@MARKETPLACE`) дают только текстовый вывод; флага `--json` у них нет.
- Один `marketplace.json` может смешивать источники с разных хостов (GitHub, GitLab, Azure DevOps): дискриминатор `source` — `github`, `url` или `git-subdir`. GitLab — first-class (`GITLAB_APM_PAT`); Azure DevOps, Gitea, Bitbucket идут как generic git.
- В репозитории `microsoft/apm` нет поставляемого OSS-сервера реестра (только тестовые моки).
- Artifactory в APM используется двояко: как VCS-прокси (`PROXY_REGISTRY_URL`, работает сейчас, не experimental) и как выделенный реестр, реализующий Registry HTTP API (`registry-http-api.md` называет аудиторией «Artifactory plugins»).
- `marketplace.json` не несёт состав пакета: ни счётчиков примитивов, ни списка зависимостей. Транзитивные зависимости при `apm pack` не разворачиваются (резолвится только `ref` плюс `sha` самого пакета). Транзитивный резолв происходит только у потребителя на `apm install` (lockfile: `depth: 1` — прямая зависимость, `2+` — транзитивная).
- Состав APM показывает по содержимому пакета, не из манифеста: `apm view <pkg>` (счётчики skills, prompts, instructions, hooks), `apm deps list` (колонки Prompts, Instructions, Agents, Skills), `apm deps tree`, `apm deps why --json`. Для marketplace-записи `apm view NAME@MARKETPLACE` даёт только `name`, `version`, `description`, `source`, `tags`.
- instructions — first-class APM-примитив: через `apm install` компилируется в `.github/instructions/`, `.github/copilot-instructions.md`, `.cursor/rules/`, `AGENTS.md`/`CLAUDE.md`. В схеме plugin/marketplace.json примитива `instructions` нет, поэтому нативный `/plugin install` сырые instructions не разворачивает.
- Marketplace — это блок `marketplace:` в `apm.yml` плюс закоммиченный `.claude-plugin/marketplace.json` в любом репозитории; существующий или пакетный репозиторий может сам быть marketplace’ом (single-plugin, monorepo-hybrid) — выделенный репозиторий не обязателен.

## Вопросы для исследования

Внешние источники, со ссылками и датами; всё на 2026 год.

1. **[Критично]** Может ли JFrog Artifactory хостить эндпоинт, реализующий APM Registry HTTP API (`GET`/`PUT /v1/packages/.../versions`, `/download`)? Разобрать с пошаговой конфигурацией и ссылками на официальные docs JFrog: (a) generic repository плюс `apm publish` — соответствует ли URL-шаблон `…/artifactory/api/apm/<repo>` чему-то реальному; (b) Artifactory user plugin; (c) нет поддержки, нужен sidecar-сервис перед Artifactory. Отдельно: настройка Artifactory как VCS-remote (Archive Entry Download API) для фронтинга приватного GitLab и GitHub (для `PROXY_REGISTRY_URL`).
2. Существует ли OSS-сервер, реализующий APM Registry HTTP API (репозитории microsoft или сообщества)? Если нет — оценить трудозатраты на минимальный сервер (три эндпоинта, RFC 7807, immutable-версии, sha256) и есть ли reference-conformance-тесты.
3. Как сделать browsable-каталог корпоративных пакетов при отсутствии catalog-эндпоинта: сравнить git-marketplace-индекс, браузер/AQL Artifactory и кастомный html поверх json. Рекомендация.
4. Публичный GitHub git-marketplace: как устроены реальные публичные APM-marketplace’ы — `DevExpGbb/zava-agent-config`, `github/awesome-copilot`, `microsoft/apm-sample-package`. Как добавить конкретные пакеты: `github.com/Netcracker/qubership-ai-packages/tree/main/agent-packages` и `github.com/Netcracker/qubership-core-lib-go-fiber-server-utils/tree/feat/agent-packages/agent-packages/fiber-server-utils-go-usage` — это полноценные APM-пакеты (есть `apm.yml`) или skill-папки; нужна ли per-primitive path-форма (`owner/repo/path/to/primitive`).
5. Топология для multi-team плюс два хоста: сравнить «один корпоративный aggregator-индекс» и «per-team marketplaces плюс агрегатор» — критерии выбора, авто-обновление записей (PR, `apm marketplace outdated`, CI-cron, `microsoft/apm-action` mode `release`), миграционный путь между топологиями. Отдельный публичный GitHub-индекс обязателен.
6. Отслеживание версий: как уведомлять о новых версиях пакетов в marketplace (Dependabot-подобные подходы, `apm marketplace outdated` в CI). Для Artifactory-реестра — что даёт `/versions`.
7. Актуальность мульти-рантайма (на 2026): действительно ли Cursor, GitHub Copilot CLI и VS Code Copilot потребляют `.claude-plugin/marketplace.json`; ограничения каждого.
8. Рекомендация по самой быстрой гарантированно работающей e2e demo (две дорожки: GitHub git-marketplace; корпоративная — git-marketplace плюс Artifactory-прокси либо Artifactory-реестр), с точными командами `apm marketplace init`/`package add`/`pack`/`add`/`install` и тем, что коммитить.
9. Витрина с составом: как построить каталог, показывающий на пакет количество зависимостей и примитивов (skills, instructions, agents, hooks), если `marketplace.json` этого не несёт. Сравнить подходы: (a) при сборке каталога клонировать и читать `apm.yml` плюс дерево `.apm/`; (b) sandbox `apm install` плюс парсинг lockfile или `apm deps list`; (c) `apm view`/`apm deps tree`. Есть ли в APM или в планах машиночитаемый манифест состава пакета.
10. Транзитивные зависимости: как потребителю увидеть полный граф пакета из marketplace до установки (или только через install плюс lockfile). Учесть MCP-зависимости (`dependencies.mcp`).
11. Поведение instructions по реальным рантаймам: какие пути (`apm install`, Claude `/plugin install`, Cursor add marketplace) разворачивают file-glob instructions (в `copilot-instructions.md`, `.cursor/rules`, `AGENTS.md`), а какие нет. Подтвердить на текущих версиях (2026).
12. Минимум новых репозиториев: валидировать топологию «каждый пакетный репозиторий несёт свой блок `marketplace:`» плюс один агрегатор в существующем репозитории. Может ли `apm marketplace add` указывать на манифест в подпапке или ветке, или он обязан лежать в корне репозитория? Миграция от co-located к выделенному агрегатору.

## Формат ответа

Структурированный отчёт по вопросам выше; для каждого — вывод плюс источники со ссылками и датами; в конце — две рекомендованные архитектуры (GitHub-слой и корпоративный слой через Artifactory) и пошаговый сценарий demo с командами для форка `vlsi/qubership-ai-packages`.
