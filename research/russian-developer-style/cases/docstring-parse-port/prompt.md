В Go-пакете `netcfg` комментарии к экспортируемым объявлениям пишут по-русски. Напишите doc-комментарий к функции:

```go
var ErrPortRange = errors.New("port out of range")

func ParsePort(s string) (int, error) {
	n, err := strconv.Atoi(strings.TrimSpace(s))
	if err != nil {
		return 0, fmt.Errorf("parse port %q: %w", s, err)
	}
	if n < 1 || n > 65535 {
		return 0, fmt.Errorf("parse port %q: %w", s, ErrPortRange)
	}
	return n, nil
}
```

Дайте только комментарий вместе с сигнатурой функции.
