# Парсер книг с сайта tululu.org

Данный скрипт позволяет скачивать книги и их обложки из [большой бесплатной библиотеки](https://tululu.org/).

### Как установить

[Python3](https://www.python.org/downloads/) должен быть уже установлен. 
Затем используйте `pip` (или `pip3`, есть конфликт с Python2) для установки зависимостей:
```
pip install -r requirements.txt
```

### Запуск и использование
Для запуска используйте команду:
```
python main.py
```
По стандарту скрипт скачивает книги с 1 по 10, если вы хотите изменить диапазон скачиваемых книг, то используйте 
аргументы для указания id первой и последней книги соответственно в следующем виде:
```
python main.py id_первой_книги id_последней_книги
```
По стандарту скачанные книги помещаются в папку `books`, которая создастся в той же директории, что и скрипт. Если вы 
хотите изменить директорию сохранения, то используйте аргумент `--books_dir`.

По стандарту скачанные обложки помещаются в папку `images`, которая создастся в той же директории, что и скрипт. Если вы 
хотите изменить директорию сохранения, то используйте аргумент `--images_dir`.



### Цель проекта

Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [dvmn.org](https://dvmn.org/).