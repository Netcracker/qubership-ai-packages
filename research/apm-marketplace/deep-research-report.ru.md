# Отчёт deep research: внутрикорпоративный магазин APM-пакетов

| Поле | Значение |
|---|---|
| Дата | 2026-05-29 |
| Бриф | [deep-research-brief.md](./deep-research-brief.md) |
| Run ID | `wf_ab15b1cc-858` |
| Версия APM на момент проверки | 0.16.0 (`ec771e57`) |
| Прогон | 5 углов, 25 источников, 115 claims извлечено, 25 проверено |
| Итог верификации | 19 подтверждено, 6 опровергнуто; после дедупликации — 15 находок |
| Голосование | adversarial, 3 голоса на claim (нужно 2 из 3 на опровержение) |
| Стоимость | 107 агентов, ~3,7M токенов субагентов, ~21 мин |

Качество источников высокое: почти все находки опираются на primary-источники (docs и код `microsoft/apm`, официальные `docs.jfrog.com`, живые манифесты GitHub). Блоги использованы только как подтверждение.

## Краткий вывод

Оба слоя магазина реализуемы штатными механизмами APM в 2026 году, но с одним структурным ограничением: ни git-marketplace, ни Registry HTTP API не имеют catalog-эндпоинта и не несут состав пакета (счётчики примитивов, граф зависимостей).

Публичный GitHub-слой собирается на git-marketplace (блок `marketplace:` в `apm.yml` компилируется в `.claude-plugin/marketplace.json`, byte-compatible с Anthropic; `source: github` поддерживает подпуть `repo` плюс `path` плюс pinned `ref`) — это подтверждено реальными публичными манифестами (`github/awesome-copilot`).

Корпоративный слой: Artifactory официально назван целевой платформой и для VCS-прокси (`PROXY_REGISTRY_URL` поверх Archive Entry Download API — GA, не experimental), и как бэкенд Registry HTTP API. Но реализовать API придётся через user plugin или sidecar: нативного APM-формата у JFrog нет, а user plugins JFrog сам рекомендует мигрировать на Workers. Готового OSS-сервера реестра APM не существует; реестр — это ровно три эндпоинта (`versions`/`download`/`PUT`), immutable-версии через `409`, есть reference test fixtures.

Витрину с составом и историю версий ни один штатный артефакт не отдаёт — их строят отдельным конвейером (клон плюс чтение `apm.yml`/`.apm`, либо sandbox-install плюс парсинг lockfile/`apm deps`), как это делает каталог `awesome-copilot.github.com`, показывающий счётчики «assets/files».

## Синтез с кросс-проверкой по демо

Раздел сводит находки research с тем, что мы проверили вживую на форке `vlsi/qubership-ai-packages` (артефакты demo — в `/tmp/qubership-demo` и `/tmp/consumer`).

### Корпоративный слой (Artifactory)

- **У JFrog нет нативного типа репозитория «apm».** URL `…/artifactory/api/apm/<repo>` из доков APM — именованный пример (base URL «vendor-defined»), а не эндпоинт JFrog. Три эндпоинта Registry HTTP API нужно реализовать самому.
- Generic-кирпичи Artifactory совместимы: Deploy Artifact (`PUT {repoKey}/{path}`) закрывает `PUT …/versions/{v}`, Archive Entry Download (`GET {repoKey}/{archive}!/{entry}`) — выдачу. Но `GET …/versions` с правильным JSON — это код-прослойка: user plugin, JFrog Worker или sidecar.
  - **User plugin** — JFrog рекомендует мигрировать на Workers; при этом не доказано, что user plugin может отдавать произвольный `GET …/versions` (открытый вопрос).
  - **JFrog Worker (HTTP-Triggered)** — «правильный» путь, но требует лицензии Enterprise X / Enterprise+.
  - **Sidecar-сервис перед Artifactory** — самый предсказуемый вариант. Готового OSS-сервера нет; минимальный сервер — это три эндпоинта плюс RFC 7807 плюс sha256 плюс immutable-`409`.
- **Работает уже сейчас, без флагов и без своего сервера:** Artifactory как VCS-прокси (`PROXY_REGISTRY_URL`, GA) прозрачно фронтит и GitHub, и приватный GitLab (штатный Remote VCS Repository, Git Provider GitLab). Ограничение: вложенные GitLab subgroups — двухуровневый путь.

Вывод: для быстрого результата — git-marketplace (обнаружение) плюс Artifactory-VCS-прокси (загрузка), оба GA. Дорогу «Artifactory как APM-реестр» (история версий `/versions` плюс REST) берём только если API или история станут жёстким требованием: она требует своего кода и `apm experimental enable registries` у потребителя.

### Публичный GitHub-слой

- `source: github` — first-class, поддерживает подпуть (`repo` плюс `path` плюс pinned `ref`). Живой манифест `github/awesome-copilot` (86 plugins) использует обе формы: строку-shorthand под `metadata.pluginRoot` и объект `{source: github, repo, path, ref: <sha>}`.
- Витрина с составом имеет рабочий референс: `awesome-copilot.github.com/skills/` — browsable и sortable каталог (349 skills, счётчики assets/files), построенный отдельным build-конвейером над манифестом, который состав не несёт. Это прямой образец «html поверх json»: состав считаем сами (клон плюс чтение `apm.yml`/`.apm`, либо sandbox-`apm install` плюс `apm deps list`/`tree`).

### Что демо доказало сверх research

Research оставил это открытым, а локальный прогон подтвердил:

- **Instructions через `apm install`** (вопрос 11): развернулись в `.github/instructions/apm-authoring.instructions.md`; skill — в `.claude/`, `.agents/`, `.windsurf/`.
- **Транзитив форка**: `go-microservice-dev-kit` разрезолвил 6 кросс-репо зависимостей с ветки `feat/agent-packages`, `apm deps tree` показал граф с составом по узлам. Research проверил только upstream main.

### Поправки к прежним выводам

- **Byte-совместимость по всем рантаймам не подтверждена.** Утверждение «`apm pack` делает ровно один transform и артефакт byte-совместим для Claude Code, Copilot CLI и APM» опровергнуто (0-3). Формат Anthropic-совместим, и Copilot использует тот же `.github/plugin/marketplace.json`, но потребление `.claude-plugin/marketplace.json` со стороны Cursor, Copilot CLI и VS Code на текущих версиях независимо не подтверждено (вопрос 7 открыт).
- **Фиксированные URL-шаблоны Artifactory VCS** (`downloadBranch`/`downloadTag`, `/api/vcs/tags`) не подтверждены (1-2): при настройке прокси сверяйтесь с живой версией Artifactory.

### Две рекомендованные архитектуры

| | Публичный GitHub-слой | Корпоративный слой |
|---|---|---|
| Механизм | git-marketplace (aggregator или monorepo-hybrid) | git-marketplace (микс GitHub плюс GitLab) плюс Artifactory-VCS-прокси |
| Обнаружение и список | `apm marketplace browse`/`search` плюс html-каталог | то же |
| Установка | `apm install pkg@mkt` (без флагов) | то же; загрузки идут через Artifactory |
| История версий | git-теги плюс `apm marketplace outdated` в CI | то же; для нативного `/versions` — отдельный sidecar-реестр плюс experimental-флаг |
| Состав | конвейер: clone плюс `apm deps`/`.apm` → html | то же |
| Готовность | работает сегодня | работает сегодня (прокси — GA) |

## Подтверждённые находки

15 находок после дедупликации; формулировки приведены как в верификационном протоколе.

1. **Artifactory как целевая платформа реестра** (high, 3-0). JFrog официально назван целевой платформой для приватного APM-реестра, реализующего Registry HTTP API; документированный URL `…/artifactory/api/apm/<repo>` — именованный пример (base URL vendor-defined), а не нормативный шаблон и не нативный эндпоинт JFrog. Источники: [registries.md](https://raw.githubusercontent.com/microsoft/apm/main/docs/src/content/docs/guides/registries.md), [registry-http-api.md](https://raw.githubusercontent.com/microsoft/apm/main/docs/src/content/docs/reference/registry-http-api.md).

2. **Три эндпоинта, нет каталога** (high, 3-0). Registry HTTP API имеет ровно три эндпоинта (`GET …/versions`, `GET …/versions/{v}/download`, `PUT …/versions/{v}`); catalog-эндпоинта структурно нет — все пути scoped под `{owner}/{repo}`. Это блокирует прямую browsable-витрину поверх реестра. Reference-клиент `src/apm_cli/deps/registry/client.py` имеет ровно `list_versions`/`download_archive`/`publish_version`. Источник: [registry-http-api.md](https://raw.githubusercontent.com/microsoft/apm/main/docs/src/content/docs/reference/registry-http-api.md).

3. **Контракт `apm publish`** (high, 3-0). `apm publish` собирает плоский `tar.gz` (`apm.yml` и `.apm/` в корне) и грузит через `PUT /v1/packages/{owner}/{repo}/versions/{version}`; `apm.yml` должен объявлять `version:`; версии immutable — повторная публикация той же версии возвращает `409 Conflict`. Источники: [registries.md](https://raw.githubusercontent.com/microsoft/apm/main/docs/src/content/docs/guides/registries.md), [registry-http-api.md](https://raw.githubusercontent.com/microsoft/apm/main/docs/src/content/docs/reference/registry-http-api.md).

4. **JFrog рекомендует Workers вместо user plugins** (high, 3-0). README `jfrog/artifactory-user-plugins`: «JFrog Workers is the recommended cloud-native solution… Consider migrating». Workers исполняются по REST (HTTP-Triggered Worker), но требуют лицензии Enterprise X/Enterprise+ (Pro X с Artifactory 7.94). User plugins формально не deprecated. Источники: [artifactory-user-plugins](https://github.com/jfrog/artifactory-user-plugins), [docs.jfrog.com](https://docs.jfrog.com/).

5. **OSS-сервера реестра нет** (high, 3-0). Готового OSS-сервера, реализующего APM Registry HTTP API, в `microsoft/apm` нет (только клиент и тестовые моки); spec называет аудиторию «Server implementers (Artifactory plugins, Nexus formats, OSS reference servers)» как проспективную. Spec самодостаточен («build a conformant registry from this doc alone») и поставляет reference test fixtures (§9). Источник: [registry-http-api.md](https://raw.githubusercontent.com/microsoft/apm/main/docs/src/content/docs/reference/registry-http-api.md).

6. **`PROXY_REGISTRY_URL` — GA** (high, 3-0 при одном связанном claim 2-1). Не experimental: переписывает каждую GitHub-hosted загрузку зависимости на Artifactory Archive Entry Download API, прозрачно фронтит апстрим git-хост (GitHub, GitLab). `ARTIFACTORY_BASE_URL` — устаревший алиас. Coverage: install GitHub-deps — да; Azure DevOps, MCP, policy-fetch — нет. Источники: [registry-proxy.md](https://raw.githubusercontent.com/microsoft/apm/main/docs/src/content/docs/enterprise/registry-proxy.md), [archiveEntryDownload](https://docs.jfrog.com/artifactory/reference/archiveEntryDownload).

7. **Фронтинг GitLab через Remote VCS Repository** (high, 3-0). JFrog предоставляет штатный (GA) Remote VCS Repository: type VCS, Git Provider GitLab, URL `https://gitlab.com/`. Это ровно то, что прописывает `registry-proxy.md`. Ограничение: вложенные subgroups (`group/subgroup/project`) — двухуровневый путь. Источники: [JFrog: proxy GitLab in VCS](https://jfrog.com/help/r/artifactory-how-to-proxy-gitlab-in-vcs-repository-and-resolve-packages/artifactory-how-to-proxy-gitlab-in-vcs-repository-and-resolve-packages), [registry-proxy.md](https://raw.githubusercontent.com/microsoft/apm/main/docs/src/content/docs/enterprise/registry-proxy.md).

8. **Archive Entry Download API** (high, 3-0). `GET {jfrog_url}/artifactory/{repoKey}/{archivePath}!/{entryPath}` (без `/api/` в пути), где `!` разделяет имя архива и путь записи; возвращает один файл изнутри хранимого архива. Для целого архива — отдельный endpoint Retrieve Folder/Repository Archive (Pro-only). Источник: [archiveEntryDownload](https://docs.jfrog.com/artifactory/reference/archiveEntryDownload).

9. **Deploy Artifact REST API** (high, 3-0). Одиночный `PUT` на произвольный `repoKey` плюс path под `/artifactory/`, тело — контент, без package-type-specific эндпоинта. Generic repository плюс sidecar/Worker может принять `PUT` по любому пути — технически совместимо с `PUT`-частью APM Registry API. Но `GET …/versions` с нужным JSON не даёт автоматом — нужна код-прослойка. Источники: [deploy-artifact](https://jfrog.com/help/r/jfrog-rest-apis/deploy-artifact), [deployartifact](https://docs.jfrog.com/artifactory/reference/deployartifact).

10. **GitHub source с подпутём** (high, 3-0). `source: github` first-class и поддерживает подпуть (`repo` плюс `path` плюс pinned `ref`). Манифест `github/awesome-copilot` (86 plugins): 67 строк-shorthand под `metadata.pluginRoot`, 19 объектов `{source: github, repo, path, ref: 40-char sha}` (13 с `path`). `path` указывает на каталог plugin-root, не на отдельный файл-примитив. Источники: [awesome-copilot/marketplace.json](https://github.com/github/awesome-copilot/blob/main/.github/plugin/marketplace.json), [microsoft/apm](https://github.com/microsoft/apm).

11. **Нет истории версий в git-marketplace** (high, 3-0). Каждая запись несёт один разрезолвленный `ref` (highest tag, matching range at build time) плюс `sha` плюс одну `version`-строку; массива `versions[]` нет. Публикация новой версии — повторный `apm pack` плюс re-tag. Отслеживание версий — внешними средствами (CI-cron, `apm marketplace outdated`, Dependabot-подобные подходы). `/versions` Registry API возвращает список версий только для реестрового слоя. Источники: [publish-to-a-marketplace.md](https://raw.githubusercontent.com/microsoft/apm/main/docs/src/content/docs/producer/publish-to-a-marketplace.md), [claude-code-marketplace.schema.json](https://github.com/microsoft/apm/blob/main/tests/fixtures/schemas/claude-code-marketplace.schema.json).

12. **Витрина с составом строится конвейером** (high, 3-0). Реальный публичный каталог `awesome-copilot.github.com/skills/` — browsable и sortable (349 skills, сортировки Name A-Z и Recently Updated), показывает per-skill счётчики «N assets, M files», вычисленные отдельным build-конвейером (`parseSkillMetadata` рекурсивно листает references/assets/scripts). Счётчики file-level, не APM primitive-level. Для APM-витрины состав строим конвейером: (a) клон плюс чтение `apm.yml`/`.apm`; (b) sandbox `apm install` плюс парсинг lockfile/`apm deps list`; (c) `apm view`/`apm deps tree`. Источники: [awesome-copilot.github.com/skills](https://awesome-copilot.github.com/skills/), [awesome-copilot/marketplace.json](https://github.com/github/awesome-copilot/blob/main/.github/plugin/marketplace.json).

13. **Host-agnostic установка** (high, 3-0). APM ставит из GitHub, GitLab, Bitbucket, Azure DevOps, GitHub Enterprise, Gitea, Gogs и любого git-хоста — это поддерживает двухслойную топологию одним `marketplace.json`. Нюанс: github-family, GitLab и Azure DevOps имеют выделенные бэкенды (дешёвый commit-resolve); Bitbucket, Gitea, Gogs идут через `GenericGitBackend` (best-effort, без дешёвого commit-resolve). Источники: [microsoft/apm](https://github.com/microsoft/apm), [README](https://raw.githubusercontent.com/microsoft/apm/main/README.md).

14. **registries-клиент за experimental-флагом** (high, 3-0). Включается `apm experimental enable registries`, проверяется `apm experimental list`, откатывается `apm experimental reset registries`. Гейтит парсинг блока `registries:`, registry resolver и ключи `registry.*`. Корп-дорога через Registry HTTP API требует флага у потребителя; git-marketplace и `PROXY_REGISTRY_URL` — нет. Источник: [registries.md](https://raw.githubusercontent.com/microsoft/apm/main/docs/src/content/docs/guides/registries.md).

15. **Состав upstream Netcracker** (high, 3-0). `Netcracker/qubership-ai-packages` (main) — monorepo с шестью package-папками под `agent-packages/`: `apm-authoring`, `english-developer-style`, `french-developer-style`, `go-microservice-dev-kit`, `markdown-line-length-120`, `russian-developer-style`. Нюанс: ветка форка `feat/agent-packages` отличается от main, её состав проверяется отдельно (в нашем demo форк содержал `apm-authoring` и `go-microservice-dev-kit`). Источник: [Netcracker/qubership-ai-packages](https://github.com/Netcracker/qubership-ai-packages/tree/main/agent-packages).

## Опровергнутые утверждения

Важны для решений: эти формулировки не прошли adversarial-голосование.

1. **«`apm pack` делает ровно один transform (`packages`→`plugins`), артефакт byte-совместим для Claude Code, Copilot CLI и APM»** — опровергнуто (0-3). Конкретно про byte-совместимость между всеми тремя рантаймами уверенности нет; трактовать осторожно. Источник: [publish-to-a-marketplace.md](https://raw.githubusercontent.com/microsoft/apm/main/docs/src/content/docs/producer/publish-to-a-marketplace.md).
2. **«APM трактует instructions, skills, prompts, agents, hooks, plugins и MCP как first-class примитивы в одном манифесте для показа состава»** — опровергнуто (0-3) как формулировка. instructions — first-class APM-примитив, но в схеме plugin/marketplace.json примитива `instructions` нет; нативный `/plugin install` сырые instructions не разворачивает. Критично для вопроса 11. Источник: [microsoft/apm](https://github.com/microsoft/apm).
3. **Фиксированные URL-шаблоны Artifactory VCS** (`downloadBranch`/`downloadTag`, `/api/vcs/tags`, `/api/vcs/branches`) — не подтверждены (1-2). Проектируя VCS-прокси, сверяйтесь с живой версией Artifactory. Источник: [JFrog: proxy GitLab in VCS](https://jfrog.com/help/r/artifactory-how-to-proxy-gitlab-in-vcs-repository-and-resolve-packages/artifactory-how-to-proxy-gitlab-in-vcs-repository-and-resolve-packages).
4. **«User plugins дают только `POST …/api/plugins/execute/{name}`»** — опровергнуто (0-3). User plugin потенциально может обслуживать произвольные REST-пути, но позитивного доказательства, что он отдаёт нужный `GET …/versions`, нет. Источник: [executePluginCode](https://docs.jfrog.com/integrations/reference/executePluginCode).
5. **«Sample-репозиторий user-plugins не содержит шаблона для custom REST-эндпоинта»** — опровергнуто (0-3). Источник: [artifactory-user-plugins](https://github.com/jfrog/artifactory-user-plugins).
6. **«Ни одна plugin-запись не несёт composition-метаданных»** — 1-2 (усиленная формулировка не прошла, так как часть записей несёт минимум полей), но операционно composition в манифесте отсутствует. Источник: [awesome-copilot/marketplace.json](https://github.com/github/awesome-copilot/blob/main/.github/plugin/marketplace.json).

## Открытые вопросы

1. **Вопрос 7 (мульти-рантайм 2026).** Потребляют ли Cursor, GitHub Copilot CLI и VS Code Copilot `.claude-plugin/marketplace.json` на текущих версиях и каковы лимиты? Прямого подтверждения среди выживших claims нет; claim о byte-совместимости опровергнут. Нужна отдельная проверка по живым докам рантаймов.
2. **Вопрос 11 (поведение instructions).** Какие пути разворачивают file-glob instructions в `.github/copilot-instructions.md`/`.cursor/rules`/`AGENTS.md`, а какие нет — на текущих версиях. Частично закрыто нашим demo (`apm install` разворачивает в `.github/instructions/`).
3. **Реализация Registry HTTP API на Artifactory.** Достаточно ли user plugin для обслуживания трёх REST-путей (`GET`/`PUT` с произвольными путями и кодами `409`/RFC 7807), или нужен sidecar/HTTP-Triggered Worker?
4. **Ветка форка `feat/agent-packages`.** Частично закрыто нашим demo: `go-microservice-dev-kit` разрезолвил 6 транзитивных кросс-репо зависимостей (`apm deps tree`), lockfile фиксирует `depth 2+`.
5. **Трудозатраты на минимальный OSS-сервер реестра.** Объём conformance-набора и наличие готового test-runner для проверки стороннего сервера количественно не оценены.

## Границы верификации и оговорки

- Отчёт — синтез 19 claims, прошедших adversarial-голосование; новых независимых проверок при синтезе не делалось. Часть claims про механику APM дана как «установленные факты, не перепроверять».
- Временная чувствительность: всё на 2026 год, `microsoft/apm` на HEAD v0.16.0. registries — experimental-флаг, контракт может меняться. Bundled Claude Code marketplace schema датирован 2026-04-23. Каталог `awesome-copilot` indexed 27 May 2026, счётчик «349 skills» дрейфует. JFrog Workers требуют лицензии Enterprise X/Enterprise+ (Pro X с Artifactory 7.94) — проверьте под конкретную инсталляцию.
- Качество источников высокое: 14 находок 3-0, одна связанная 2-1 (формулировка «every package download»).

## Источники

| URL | Качество | Угол | Claims |
|---|---|---|---|
| [registry-http-api.md](https://raw.githubusercontent.com/microsoft/apm/main/docs/src/content/docs/reference/registry-http-api.md) | primary | механика | 5 |
| [publish-to-a-marketplace.md](https://raw.githubusercontent.com/microsoft/apm/main/docs/src/content/docs/producer/publish-to-a-marketplace.md) | primary | механика | 5 |
| [microsoft/apm](https://github.com/microsoft/apm) | primary | механика | 5 |
| [guides/registries.md](https://raw.githubusercontent.com/microsoft/apm/main/docs/src/content/docs/guides/registries.md) | primary | механика | 5 |
| [enterprise/registry-proxy.md](https://raw.githubusercontent.com/microsoft/apm/main/docs/src/content/docs/enterprise/registry-proxy.md) | primary | механика | 5 |
| [JFrog: proxy GitLab in VCS](https://jfrog.com/help/r/artifactory-how-to-proxy-gitlab-in-vcs-repository-and-resolve-packages/artifactory-how-to-proxy-gitlab-in-vcs-repository-and-resolve-packages) | primary | Artifactory | 5 |
| [executePluginCode](https://docs.jfrog.com/integrations/reference/executePluginCode) | primary | Artifactory | 4 |
| [artifactory-user-plugins](https://github.com/jfrog/artifactory-user-plugins) | primary | Artifactory | 5 |
| [archiveEntryDownload](https://docs.jfrog.com/artifactory/reference/archiveEntryDownload) | primary | Artifactory | 5 |
| [deploy-artifact](https://jfrog.com/help/r/jfrog-rest-apis/deploy-artifact) | primary | Artifactory | 5 |
| [awesome-copilot/marketplace.json](https://github.com/github/awesome-copilot/blob/main/.github/plugin/marketplace.json) | primary | экосистема | 5 |
| [awesome-copilot.github.com/skills](https://awesome-copilot.github.com/skills/) | primary | экосистема | 5 |
| [Netcracker/qubership-ai-packages](https://github.com/Netcracker/qubership-ai-packages/tree/main/agent-packages) | primary | экосистема | 5 |
| [VS Code: agent plugins](https://code.visualstudio.com/docs/copilot/customization/agent-plugins) | primary | рантаймы | 5 |
| [GitHub Copilot CLI plugins](https://docs.github.com/en/copilot/concepts/agents/copilot-cli/about-cli-plugins) | primary | рантаймы | 4 |
| [VS Code: custom instructions](https://code.visualstudio.com/docs/copilot/customization/custom-instructions) | primary | рантаймы | 4 |
| [Cursor: plugins](https://cursor.com/docs/plugins) | primary | рантаймы | 5 |
| [microsoft/apm#1134](https://github.com/microsoft/apm/issues/1134) | primary | версии и топология | 5 |
| [microsoft/apm-action](https://github.com/microsoft/apm-action) | primary | версии и топология | 5 |
| [APM: marketplaces guide](https://microsoft.github.io/apm/guides/marketplaces/) | primary | версии и топология | 5 |
| [Dependabot: AI-agent remediation](https://github.blog/changelog/2026-04-07-dependabot-alerts-are-now-assignable-to-ai-agents-for-remediation/) | primary | версии и топология | 4 |
| [Dependabot options reference](https://docs.github.com/en/code-security/dependabot/working-with-dependabot/dependabot-options-reference) | primary | версии и топология | 4 |
| [DevOps guide to APM (blog)](https://dev.to/pwd9000/agent-package-manager-apm-a-devops-guide-to-reproducible-ai-agents-4c25) | blog | версии и топология | 5 |
