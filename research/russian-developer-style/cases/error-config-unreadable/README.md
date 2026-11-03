# Case: a config file the user cannot read

The input is a localized CLI that cannot read `/etc/foo/config.yaml` (`EACCES`) and has `FOO_CONFIG` as a way out. The
fix is a permission or another path, not undoing an input the message names, so the action still belongs: this case
is the presence check beside `error-negative-fetch-size`.

## Skill parts

- Text above §1 (the paragraph that hands the rest of a message's content to `telemetry-authoring`)
- `SKILL.md`: §3 (Сообщение об ошибке), §8 (Ошибки и логи), §11 (the genre item)
- `modules/errors-logs.md`: Шаблон ошибки, CLI-вывод

## Checks

1. **Names the file** (`names_file`).
2. **Gives an action** (`gives_action`): the read permission or `FOO_CONFIG`.

## Results

Runs of 2026-10-31, graded by reading. Trees as in `error-negative-fetch-size`.

| Run | File (1) | Action (2) |
| --- | --- | --- |
| Opus r1, r2 | passes | passes |
| Sonnet r1, r2 | passes | passes |
| Opus baseline r1, r2 | passes | passes |
| Sonnet baseline r1, r2 | passes | passes |
