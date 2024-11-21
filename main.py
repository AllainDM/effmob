import os
import json
from typing import List, Dict, Union

import unittest

class Book:
    """Класс представляющий книгу.
        Содержит атрибуты:
        1. id - первичный ключ.
        2. title - название книги.
        3. author - автор книги.
        4. author - год издания.
        5. status - статус книги в библиотеке, на руках или в наличии.
    """
    def __init__(self, id: int, title: str, author: str, year: int, status: str = "В наличии"):
        self.id = id
        self.title = title
        self.author = author
        self.year = year
        self.status = status

    def to_dict(self) -> Dict[str, Union[int, str]]:
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "year": self.year,
            "status": self.status
        }

    @staticmethod
    def from_dict(data: Dict[str, Union[int, str]]) -> 'Book':
        return Book(data['id'], data['title'], data['author'], data['year'], data['status'])


class Library:
    """Класс для управления библиотекой.
     Содержит методы для загрузки, сохранения, добавления,
     удаления, поиска и отображения и смены статуса книг.
     """
    def __init__(self, filename: str):
        # Название файла в котором хранится библиотека.
        self.filename = filename
        # Список книг загружаемый из файла при инициализации экземпляра.
        self.books: List[Book] = self.load_books()

    def load_books(self) -> List[Book]:
        """Загружает книги из файла JSON."""
        # В случае отсутствия файла вернем пустой список.
        if not os.path.exists(self.filename):
            return []
        # Откроем для чтения файл с библиотекой.
        with open(self.filename, 'r', encoding='utf-8') as file:
            book_dicts = json.load(file)
            # Вернем пользователю список с информацией о книгах.
            return [Book.from_dict(book_dict) for book_dict in book_dicts]

    def save_books(self):
        """Сохраняет книги в файл JSON."""
        with open(self.filename, 'w', encoding='utf-8') as file:
            json.dump([book.to_dict() for book in self.books], file, ensure_ascii=False, indent=4)

    def add_book(self, title: str, author: str, year: int):
        """Добавляет новую книгу в библиотеку."""
        # Определим id для новой книги.
        new_id = self.books[-1].id + 1 if self.books else 1
        # Создадим экземпляр класса книги.
        new_book = Book(new_id, title, author, year)
        # Добавим к списку книг хранящихся в экземпляре класса библиотеки.
        self.books.append(new_book)
        # Сохраним обновленный список в файл.
        self.save_books()
        # Пользователю возвращаем ответ с результатом.
        return f"Книга '{title}' добавлена с ID {new_id}."

    def remove_book(self, book_id: int):
        """Удаляет книгу по ID."""
        # Сохраним количество книг для дальнейшего определения успешности "удаления" книги.
        before_remove = len(self.books)
        # Создадим новый список книг в котором не будет удаляемой книги.
        self.books = [book for book in self.books if book.id != book_id]
        # Если количество книг изменилось, значит удаление произошло успешно.
        if len(self.books) < before_remove:
            self.save_books()
            return f"Книга с ID {book_id} удалена."
        else:
            return "Книга с таким ID не найдена."

    def search_books(self, query: str, field: str):
        """Ищет книги по заданному полю."""
        # Создаем список со всеми совпадениями заданного аттрибута.
        results = [book for book in self.books if query.lower() in str(getattr(book, field)).lower()]
        return results

    def display_books(self):
        """Возвращает все книги из библиотеки."""
        # Возвращаем пользователю простой список с информацией о книгах.
        return self.books

    def update_status(self, book_id: int, status: str):
        """Обновляет статус книги по ID."""
        # Переберем простым циклом список с книгами, до совпадения id, после чего сменим статус.
        for book in self.books:
            if book.id == book_id:
                book.status = status
                # Сохраним обновленный список в файл.
                self.save_books()
                return f"Статус книги с ID {book_id} обновлён на '{status}'."
        return "Книга с таким ID не найдена."

# Тестирование
# Используется класс TestLibraryMethods,
# который содержит тесты для каждой из функций класса Library.
class TestLibraryMethods(unittest.TestCase):
    # Создание файла json для тестирования.
    def setUp(self):
        self.test_filename = 'test_books.json'
        # Очищаем файл перед каждым тестом
        if os.path.exists(self.test_filename):
            os.remove(self.test_filename)
        self.library = Library(self.test_filename)

    # Удаление файла после теста.
    def tearDown(self):
        if os.path.exists(self.test_filename):
            os.remove(self.test_filename)

    # Тест добавления книги.
    def test_add_book(self):
        response = self.library.add_book("Тестовая книга 1", "Автор 1", 2021)
        self.assertEqual(response, "Книга 'Тестовая книга 1' добавлена с ID 1.")
        self.assertEqual(len(self.library.books), 1)

    # Тест удаления книги.
    def test_remove_book(self):
        # Сначала добавим книгу
        self.library.add_book("Тестовая книга 2", "Автор 2", 2022)
        # Попробуем удалить созданную ранее книгу.
        response = self.library.remove_book(1)
        self.assertEqual(response, "Книга с ID 1 удалена.")
        self.assertEqual(len(self.library.books), 0)

        # Попробуем удалить книгу с несуществующим ID.
        none_book = self.library.remove_book(999)
        self.assertEqual(none_book, "Книга с таким ID не найдена.")

    # Поиск книги по заданному параметру.
    def test_search_books(self):
        # Создадим книгу для поиска.
        self.library.add_book("Тестовая книга для поиска", "Автор 3", 2022)
        results = self.library.search_books("Тестовая книга для поиска", "title")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].title, "Тестовая книга для поиска")

    # Обновление статуса книги.
    def test_update_status(self):
        self.library.add_book("Тестовая книга для смены статуса", "Автор 4", 2023)
        self.assertEqual(self.library.books[0].status, "В наличии")
        self.library.update_status(1, "Выдана")
        self.assertEqual(self.library.books[0].status, "Выдана")

    # Запись нескольких книг.
    def test_load_books(self):
        # Записываем несколько книг вручную в файл
        books_data = [
            {"id": 1, "title": "Книга 1", "author": "Автор 5", "year": 2020, "status": "В наличии"},
            {"id": 2, "title": "Книга 2", "author": "Автор 6", "year": 2021, "status": "Выдана"}
        ]
        with open(self.test_filename, 'w', encoding='utf-8') as file:
            json.dump(books_data, file, ensure_ascii=False, indent=4)

        # Перезагрузим экземпляр класса библиотеки.
        self.library = Library(self.test_filename)
        self.assertEqual(len(self.library.books), 2)
        self.assertEqual(self.library.books[0].id, 1)

    # Получение списка книг.
    def test_display_books(self):
        self.library.add_book("Тестовая книга 3", "Автор 7", 2021)
        books = self.library.display_books()
        self.assertIsInstance(books, list)
        self.assertEqual(len(books), 1)
        self.assertEqual(books[0].title, "Тестовая книга 3")


def main():
    # Создадим экземпляр библиотеки загрузив данные из файла.
    library = Library('books.json')
    # Запустим бесконечный цикл с меню.
    while True:
        print("\nУправление библиотекой.")
        print("1. Добавить книгу.")
        print("2. Удалить книгу.")
        print("3. Искать книгу.")
        print("4. Показать все книги.")
        print("5. Изменить статус книги.")
        print("6. Выполнить тестирование на unittest.")
        choice = input("Выберите опцию: ")

        # 1. Добавление книги:
        # Пользователь вводит title, author и year,
        # после чего книга добавляется в библиотеку с уникальным id и статусом “в наличии”.
        # Добавлена простая обработка пустого ввода для каждого пункта, в этом случае идет возврат в меню.
        if choice == '1':
            title = input("Введите название: ")
            if title == "":
                input("\nВведено некорректное название книги(пустая строка), попробуйте снова. Нажмите enter для продолжения.")
                continue
            author = input("Введите автора: ")
            if author == "":
                input("\nВведен некорректный автор книги(пустая строка), попробуйте снова. Нажмите enter для продолжения.")
                continue
            year = input("Введите год издания: ")
            if year == "":
                input("\nВведен некорректный год издания книги(пустая строка), попробуйте снова. Нажмите enter для продолжения.")
                continue
            try:
                year = int(year)
            except ValueError:
                input("\nВведен некорректный год издания книги, попробуйте снова. Нажмите enter для продолжения.")
            else:
                answer = library.add_book(title, author, year)
                input(f"\n{answer} Нажмите enter для продолжения.")

        # 2. Удаление книги:
        # Пользователь вводит id книги, которую нужно удалить.
        elif choice == '2':
            book_id = int(input("Введите ID книги для удаления: "))
            # Метод класса возвращает ответ, который мы выводим пользователю.
            answer = library.remove_book(book_id)
            input(f"\n{answer} Нажмите enter для продолжения.")

        # 3. Поиск книги:
        # Пользователь может искать книги по title, author или year.
        elif choice == '3':
            field = input("Искать по title(1), author(2) или year(3). Укажите текстом или цифрой: ")
            if field == "1": field = "title"
            elif field == "2": field = "author"
            elif field == "3": field = "year"
            if field != "title" and field != "author" and field != "year":
                input(f"\nПараметр для поиска указан не верно, попробуйте снова. Нажмите enter для продолжения.")
            else:
                query = input("Введите значение выбранного параметра для поиска: ")
                if query == "":
                    input(f"\nВведено пустое поле, попробуйте снова. Нажмите enter для продолжения.")
                else:
                    # Метод класса возвращает ответ, который мы выводим пользователю.
                    answer = library.search_books(query, field)
                    if answer:
                        for book in answer:
                            print(book.to_dict())
                        input(f"\nНажмите enter для продолжения.")
                    else:
                        input(f"\nКниги не найдены. Нажмите enter для продолжения.")

        # 4. Отображение всех книг:
        # Приложение выводит список всех книг с их id, title, author, year и status.
        elif choice == '4':
            # Метод класса возвращает ответ, который мы выводим пользователю.
            answer = library.display_books()
            if answer:
                for book in answer:
                    print(book.to_dict())
                input(f"\nНажмите enter для продолжения.")
            else:
                input(f"\nКниги не найдены. Нажмите enter для продолжения.")

        # 5. Изменение статуса книги:
        # Пользователь вводит id книги и новый статус (“в наличии” или “выдана”).
        elif choice == '5':
            book_id = int(input("Введите ID книги для изменения статуса: "))
            status = input("Введите новый статус ('В наличии(1)' или 'Выдана(0)'): ")
            if status == "1":
                status = 'В наличии'
                # Метод класса возвращает ответ, который мы выводим пользователю.
                answer = library.update_status(book_id, status)
                input(f"\n{answer} Нажмите enter для продолжения.")
            elif status == "0":
                status = 'Выдана'
                # Метод класса возвращает ответ, который мы выводим пользователю.
                answer = library.update_status(book_id, status)
                input(f"\n{answer} Нажмите enter для продолжения.")
            else:
                input("Введен некорректный статус, попробуйте снова. Нажмите enter для продолжения.")

        # 6. Запуск тестирования.
        elif choice == '6':
            unittest.main()

        else:
            input("Неверный выбор, попробуйте снова. Нажмите enter для продолжения.")


if __name__ == "__main__":
    main()
