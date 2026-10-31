В репозитории сообщения коммитов пишут по-русски, тема — глагол в третьем лице («исправляет», «добавляет»), без
префиксов. Изменение в `client/retry.go`:

```diff
 func (c *Client) do(req *http.Request) (*http.Response, error) {
-	token := c.tokens.Current()
 	for attempt := 0; attempt < c.maxAttempts; attempt++ {
+		token := c.tokens.Current()
 		req.Header.Set("Authorization", "Bearer "+token)
 		resp, err := c.http.Do(req)
 		if resp != nil && resp.StatusCode == http.StatusUnauthorized {
 			c.tokens.Refresh()
 			continue
 		}
 		return resp, err
 	}
```

До изменения клиент брал токен один раз перед циклом. После ответа 401 он обновлял токен, но повторял запрос со
старым, поэтому все повторы тоже получали 401, и запрос падал, хотя новый токен уже был. Пользователи видели это как
ошибку авторизации раз в час, когда истекал токен. Тест `TestRetryUsesRefreshedToken` добавлен в этом же коммите.

Напишите сообщение коммита. Дайте только текст сообщения.
