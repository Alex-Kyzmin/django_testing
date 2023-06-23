from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class TestCommentCreation(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Создаём клиент для пользователя-автора, логинимся в клиенте.
        cls.author = User.objects.create(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        # Создаём клиент для пользователя-читателя, логинимся в клиенте.
        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        # Создаём тестовую запись в БД с заметкой.
        cls.note = Note.objects.create(
            author=cls.author,
            title='Заголовок',
            text='Текст',
            slug='slogan1',
        )
        # Адреса тестируемых страницы.
        cls.create_url = reverse('notes:add')
        cls.edit_url = reverse(
            'notes:edit',
            args=(cls.note.slug,),
        )
        cls.delete_url = reverse(
            'notes:delete',
            args=(cls.note.slug,),
        )
        # Данные для POST-запроса при создании комментария.
        cls.form_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст заметки',
            'slug': 'new_slogan2',
        }

    def test_anonymous_user_cant_create_note(self):
        """Тестируем невозможность создания записи анонимному пользователю."""
        # Совершаем запрос от анонимного клиента, в POST-запросе отправляем
        # предварительно подготовленные данные формы с текстом записи.
        self.client.post(
            self.create_url,
            data=self.form_data,
        )
        # Считаем количество записей.
        note_count = Note.objects.count()
        # Ожидаем, что запись в базе 1 - созданная в @classmethod.
        self.assertEqual(note_count, 1)

    def test_author_create_note(self):
        """Тестируем возможность создания записи автору."""
        self.author_client.post(
            self.create_url,
            data=self.form_data,
        )
        # Считаем количество записей.
        note_count = Note.objects.count()
        # Ожидаем, что записей в базе 2 - созданная в @classmethod и тестом.
        self.assertEqual(note_count, 2)
        # Получаем созданную заметку из базы:
        new_note = Note.objects.get(id=2)
        # проверяем что значение slug новой записи соответсвует форме.
        self.assertIn(new_note.slug, 'new_slogan2')

    def test_cant_create_note_with_identical_slogan(self):
        """Тестируем невозможность создания двух заметкок с одинаковым slug."""
        # Подготавливаем данные формы с текстом записи с одинаковым слоганом.
        self.form_data['slug'] = self.note.slug
        # Совершаем запрос от автора, в POST-запросе отправляем форму.
        response = self.author_client.post(
            self.create_url,
            data=self.form_data,
        )
        # Проверяем, что в ответе содержится ошибка формы для поля slug:
        self.assertFormError(
            response,
            'form',
            'slug',
            errors=(self.note.slug + WARNING),
        )
        # Считаем количество записей.
        note_count = Note.objects.count()
        # Ожидаем, что запись в базе 1 - созданная в @classmethod.
        self.assertEqual(note_count, 1)

    def test_create_note_with_empty_slug(self):
        """Тестируем возможность создания заметки без заполнения поля slug."""
        # Убираем поле slug из словаря:
        self.form_data.pop('slug')
        # Совершаем запрос от автора, в POST-запросе отправляем форму.
        response = self.author_client.post(
            self.create_url,
            data=self.form_data,
        )
        # проверяем что запрос перевел на страницу "успешной операции".
        redirect_url = reverse('notes:success')
        self.assertRedirects(response, redirect_url)
        # Считаем количество записей.
        note_count = Note.objects.count()
        # Ожидаем, что записей в базе 2 - созданная в @classmethod и тестом.
        self.assertEqual(note_count, 2)
        # Получаем созданную заметку из базы:
        new_note = Note.objects.get(id=2)
        # Формируем ожидаемый slug:
        expected_slug = slugify(self.form_data['title'])
        # Проверяем, что slug заметки соответствует ожидаемому:
        self.assertEqual(new_note.slug, expected_slug)

    def test_author_edit_note(self):
        """Тестируем возможность автора редактировать свои заметки."""
        # Совершаем запрос от автора, в POST-запросе отправляем форму.
        response = self.author_client.post(
            self.edit_url,
            data=self.form_data,
        )
        # проверяем что запрос перевел на страницу "успешной операции".
        redirect_url = reverse('notes:success')
        self.assertRedirects(response, redirect_url)
        # Получаем созданную заметку из базы:
        new_note = Note.objects.get(slug='new_slogan2')
        # проверяем что значение slug записи @classmethod изменилось.
        self.assertEqual(new_note.slug, self.form_data['slug'])

    def test_author_delete_note(self):
        """Тестируем возможность автора удалять свои заметки."""
        # Перед тестированием убеждаемся, что в базе имеется 1 запись.
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)
        # Совершаем delete-запрос от автора на удаление.
        response = self.author_client.delete(self.delete_url)
        # проверяем что запрос перевел на страницу "успешной операции".
        redirect_url = reverse('notes:success')
        self.assertRedirects(response, redirect_url)
        # Считаем количество записей.
        new_note_count = Note.objects.count()
        # Ожидаем, что записей в БД нет после удаления.
        self.assertEqual(new_note_count, 0)

    def test_reader_cant_delete_note(self):
        """Тестируем невозможность читателя удалять не свои заметки."""
        # Перед тестированием убеждаемся, что в базе имеется 1 запись.
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)
        # Совершаем delete-запрос от читателя на удаление.
        response = self.reader_client.delete(self.delete_url)
        # проверяем что запрос перевел на страницу "успешной операции".
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        # Считаем количество записей.
        new_note_count = Note.objects.count()
        # Ожидаем, что запись созданная в @classmethod не удалилась.
        self.assertEqual(new_note_count, 1)

    def test_reader_cant_edit_note(self):
        """Тестируем невозможность читателя редактировать чужие заметки."""
        # Совершаем POST-запрос от читателя на редактирование поста.
        response = self.reader_client.post(
            self.edit_url,
            data=self.form_data,
        )
        # проверяем что запрос не перевел на страницу "успешной операции".
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        # проверяем что значение slug записи @classmethod не изменилось.
        self.assertIn(self.note.slug, 'slogan1')
