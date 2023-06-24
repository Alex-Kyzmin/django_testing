from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Создаём двух авторизируемых пользователей(автора и читателя).
        cls.author = User.objects.create(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)

        # Создаём запись заметки.
        cls.note = Note.objects.create(
            author=cls.author,
            title='Заголовок',
            text='Текст',
            slug='slogan1',
        )
        # Адреса тестируемых страницы.
        cls.login_url = reverse('users:login')
        cls.logout_url = reverse('users:logout')
        cls.signup_url = reverse('users:signup')
        cls.home_url = reverse('notes:home')
        cls.list_url = reverse('notes:list')
        cls.add_url = reverse('notes:add')
        cls.success_url = reverse('notes:success')
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))

    def test_pages_availability_not_login_user(self):
        """Тест на доступность страниц анономным пользователям."""
        urls = (
            self.home_url,
            self.login_url,
            self.logout_url,
            self.signup_url,
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_login_user(self):
        """Тест на доступность страниц зарегистрированным пользователям."""
        urls = (
            self.list_url,
            self.success_url,
            self.add_url,
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.reader_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_notes_edit_and_delete(self):
        """Тест на доступность удаления/изменения записи автору/читателю."""
        users_statuses_urls = (
            (self.author_client, HTTPStatus.OK, self.edit_url),
            (self.author_client, HTTPStatus.OK, self.delete_url),
            (self.reader_client, HTTPStatus.NOT_FOUND, self.edit_url),
            (self.reader_client, HTTPStatus.NOT_FOUND, self.delete_url),
        )
        for user, status, url in users_statuses_urls:
            with self.subTest(user=user, url=url, status=status):
                response = user.get(url)
                self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        """Тест на редирект анонимным пользователям."""
        for url in (self.edit_url, self.delete_url):
            with self.subTest(url=url):
                redirect_url = f'{self.login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
