# video_to_text
Транскрибация текста из аудио, полученного из видео-файла для генерации теста по содержимому видео
## Описание
Проект создан для генерации тестов по содержимому видео. К примеру, система может 
протестировать студентов на знание просмотренной лекции. В данной реализации система работает
для партнеров из ФосАгро.


## Установка
Установка необходимых библиотек:
```shell
python3 -m pip install -r requirements.txt
```
Еще нужно необходимо установить зависимости для pydub-библиотеки:

Команда для MAC:
```shell
brew install ffmpeg
```
Команда для Linux:
```shell
sudo apt-get install ffmpeg
```

## Запуск
Программа запускается через терминал с использованием следующих аргументов командной строки:

```shell
python3 main.py --method=whisper --source=file
```

Аргументы командной строки позволяют гибко настроить процесс генерации тестов:

- method - определяет метод транскрибации аудио-файла. Доступны два варианта: `whisper` и `google`.
- source - определяет способ загрузки видео-файла. Доступны два варианта: `url` и `file`.

При использовании метода `google`, транскрибация текста осуществляется с помощью GoogleRecognizer. 
Этот метод может занять больше времени и качество результата может быть не самым высоким. 

При использовании метода `whisper`, транскрибация текста осуществляется с помощью OpenAI. 
Для этого метода необходим токен OpenAI по подписке. Подробнее о ценах можно 
узнать [здесь](https://openai.com/pricing). Этот метод работает быстрее и 
обеспечивает более высокое качество текста.


Для выбора аргумента `url` необходимо создать файл `videos.csv`, 
который будет представлять из себя csv-таблицу 
с тремя колонками в такой последовательности (название видео, ссылка для скачивания, ссылка на видео).
По умолчанию, файл должен находиться в директории `data/videos/`.

Для выбора аргумента `file` нужно поместить видео-файлы в формате `.mp4` в директорию `data/videos/`
Тогда этап скачивания видео будет пропущен и программа начнет выполнение сразу с открытия файла из папки.


## Алгоритм
1. **Скачиваем** видео из интернета, используя предоставленную ссылку, если был выбран вариант `--source=url`.
2. Используем **видео**, расположенное в папке `data/videos/`.
3. **Извлекаем** аудио-дорожку из видео и сохраняем ее в папке `data/audio/`.
4. **Удаляем** исходное видео для экономии памяти.
5. Разбиваем аудио на отдельные части (**chunks**) длительностью 1 минута.
6. Из каждой аудио-части извлекаем **текст** с помощью Google или OpenAI.
7. **Объединяем** тексты, полученные после транскрибации каждой аудио-части.
8. **Удаляем** содержимое папок `data/audio/` и `data/chunks/`.
9. **Сокращаем** текст на 30% с помощью библиотеки `Gensim` (слишком большой текст не помещается в запрос GPT).
10. **Генерируем** тест на основе сокращенного текста.
11. **Сохраняем** тест, сокращенный текст и отчет GPT о стоимости и количестве токенов в коллекции MongoDB.
12. **Отправляем** отчет GPT в определенную партицию топика Kafka. В Kafka мы храним все отчеты GPT для последующего анализа и составления статистики по запросам.
