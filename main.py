import os
import json
from typing import List, Dict, Union


class Book:
    """Класс представляющий книгу."""
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
    """Класс для управления библиотекой книг."""
    def __init__(self, filename: str):
        self.filename = filename
        self.books: List[Book] = self.load_books()

    def load_books(self) -> List[Book]:
        """Загружает книги из файла JSON."""
        if not os.path.exists(self.filename):
            return []
        with open(self.filename, 'r', encoding='utf-8') as file:
            book_dicts = json.load(file)
            return [Book.from_dict(book_dict) for book_dict in book_dicts]

    def save_books(self):
        """Сохраняет книги в файл JSON."""
        with open(self.filename, 'w', encoding='utf-8') as file:
            json.dump([book.to_dict() for book in self.books], file, ensure_ascii=False, indent=4)

    def add_book(self, title: str, author: str, year: int):
        """Добавляет новую книгу в библиотеку."""
        new_id = self.books[-1].id + 1 if self.books else 1
        new_book = Book(new_id, title, author, year)
        self.books.append(new_book)
        self.save_books()
        return f"Книга '{title}' добавлена с ID {new_id}."

    def remove_book(self, book_id: int):
        """Удаляет книгу по ID."""
        before_remove = len(self.books)
        self.books = [book for book in self.books if book.id != book_id]
        if len(self.books) < before_remove:
            self.save_books()
            return f"Книга с ID {book_id} удалена."
        else:
            return "Книга с таким ID не найдена."

    def search_books(self, query: str, field: str):
        """Ищет книги по заданному полю."""
        results = [book for book in self.books if query.lower() in str(getattr(book, field)).lower()]
        return results

    def display_books(self):
        """Возвращает все книги из библиотеки."""
        return self.books

    def update_status(self, book_id: int, status: str):
        """Обновляет статус книги по ID."""
        for book in self.books:
            if book.id == book_id:
                book.status = status
                self.save_books()
                print(f"Статус книги с ID {book_id} обновлён на '{status}'.")
                return
        print("Книга с таким ID не найдена.")


def main():
    # Создадим экземпляр библиотеки загрузив данные из файла.
    library = Library('books.json')
    while True:
        print("\nУправление библиотекой.")
        print("1. Добавить книгу.")
        print("2. Удалить книгу.")
        print("3. Искать книгу.")
        print("4. Показать все книги.")
        print("5. Изменить статус книги.")
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
            status = input("Введите новый статус ('в наличии(1)' или 'выдана(0)'): ")
            if status == 1:
                status = 'в наличии'
                library.update_status(book_id, status)
            elif status == 0:
                status = 'выдана'
                library.update_status(book_id, status)
            else:
                print("Введен некорректный статус, попробуйте снова.")
            input("Нажмите enter для продолжения.")

        else:
            input("Неверный выбор, попробуйте снова. Нажмите enter для продолжения.")


if __name__ == "__main__":
    main()