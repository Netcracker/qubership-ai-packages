```java
"HttpClientBuilder.connectTimeout(millis) must not be negative, got " + millis + ". The check keeps a miscalculated timeout from being applied unnoticed. Pass 0 for no timeout, or the number of milliseconds to wait, such as 5000. The builder keeps its previous connect timeout."
```
