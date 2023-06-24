from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


# Константы текста записи
NOTE_TITLE = 'Заголовок'
NOTE_TEXT = 'Текст'
NOTE_SLOGAN = 'slogan1'
NEW_NOTE_TITLE = 'Новый заголовок'
NEW_NOTE_TEXT = 'Новый текст заметки'
NEW_NOTE_SLOGAN = 'new_slogan2'


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
        # Создаём тестовую запись в БД с заметкой
        # это тестовая запись облегчающая дальнейшую логику кода
        # прошу оставить мой вариант.
        cls.note = Note.objects.create(
            author=cls.author,
            title=NOTE_TITLE,
            text=NOTE_TEXT,
            slug=NOTE_SLOGAN,
        )
        # Адреса тестируемых страницы.
        cls.create_url = reverse('notes:add')
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        # Данные для POST-запроса при создании комментария.
        cls.form_data = {
            'title': NEW_NOTE_TITLE,
            'text': NEW_NOTE_TEXT,
            'slug': NEW_NOTE_SLOGAN,
        }

    def test_anonymous_user_cant_create_note(self):
        """Тестируем невозможность создания записи анонимному пользователю."""
        self.client.post(
            self.create_url,
            data=self.form_data,
        )
        note_count = Note.objects.count()
        # Ожидаем, что запись в базе 1 - созданная в @classmethod.
        self.assertEqual(note_count, 1)

    def test_author_create_note(self):
        """Тестируем возможность создания записи автору."""
        self.author_client.post(
            self.create_url,
            data=self.form_data,
        )
        note_count = Note.objects.count()
        self.assertEqual(note_count, 2)
        new_note = Note.objects.get(id=2)
        self.assertIn(new_note.title, NEW_NOTE_TITLE)
        self.assertIn(new_note.text, NEW_NOTE_TEXT)
        self.assertIn(new_note.slug, NEW_NOTE_SLOGAN)

    def test_cant_create_note_with_identical_slogan(self):
        """Тестируем невозможность создания двух заметкок с одинаковым slug."""
        self.form_data['slug'] = self.note.slug
        response = self.author_client.post(
            self.create_url,
            data=self.form_data,
        )
        self.assertFormError(
            response,
            'form',
            'slug',
            errors=(self.note.slug + WARNING),
        )
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)
        self.assertIn(self.note.slug, NOTE_SLOGAN)
        self.assertIn(self.note.title, NOTE_TITLE)
        self.assertIn(self.note.text, NOTE_TEXT)

    def test_create_note_with_empty_slug(self):
        """Тестируем возможность создания заметки без заполнения поля slug."""
        self.form_data.pop('slug')
        response = self.author_client.post(
            self.create_url,
            data=self.form_data,
        )
        redirect_url = reverse('notes:success')
        self.assertRedirects(response, redirect_url)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 2)
        new_note = Note.objects.get(id=2)
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)

    def test_author_edit_note(self):
        """Тестируем возможность автора редактировать свои заметки."""
        response = self.author_client.post(
            self.edit_url,
            data=self.form_data,
        )
        redirect_url = reverse('notes:success')
        self.assertRedirects(response, redirect_url)
        new_note = Note.objects.get(slug=NEW_NOTE_SLOGAN)
        self.assertIn(new_note.slug, NEW_NOTE_SLOGAN)
        self.assertIn(new_note.title, NEW_NOTE_TITLE)
        self.assertIn(new_note.text, NEW_NOTE_TEXT)

    def test_author_delete_note(self):
        """Тестируем возможность автора удалять свои заметки."""
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)
        response = self.author_client.delete(self.delete_url)
        redirect_url = reverse('notes:success')
        self.assertRedirects(response, redirect_url)
        new_note_count = Note.objects.count()
        self.assertEqual(new_note_count, 0)

    def test_reader_cant_delete_note(self):
        """Тестируем невозможность читателя удалять не свои заметки."""
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertIn(self.note.slug, NOTE_SLOGAN)
        self.assertIn(self.note.title, NOTE_TITLE)
        self.assertIn(self.note.text, NOTE_TEXT)

    def test_reader_cant_edit_note(self):
        """Тестируем невозможность читателя редактировать чужие заметки."""
        response = self.reader_client.post(
            self.edit_url,
            data=self.form_data,
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertIn(self.note.slug, NOTE_SLOGAN)
        self.assertIn(self.note.title, NOTE_TITLE)
        self.assertIn(self.note.text, NOTE_TEXT)
