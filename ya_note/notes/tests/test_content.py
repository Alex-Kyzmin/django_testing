from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.others_author = User.objects.create(username='Другой_автор')
        cls.note = Note.objects.create(
            author=cls.author,
            title='Заголовок',
            text='Текст',
            slug='slogan1',
        )
        cls.others_note = Note.objects.create(
            author=cls.others_author,
            title='Другой заголовок',
            text='Другой текст',
            slug='others_slogan1',
        )
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)
        # Адреса тестируемых страницы.
        # решил вместо констант оставить в @classmethod
        cls.home_url = reverse('notes:list')
        cls.add_url = reverse('notes:add')
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))

    def test_content_list_pages(self):
        """Тестируем контент страницы со списком заметок."""
        response = self.auth_client.get(self.home_url)
        # Тест № 1: Проверяем, что объект новости находится в словаре контекста
        self.assertIn(self.note, response.context['object_list'])
        # Тест № 2: Проверяем, что на странице запись принадлежит автору.
        self.assertEqual(self.note.author, self.author)
        self.assertNotEqual(self.note.author, self.others_author)

    def test_authorized_client_has_form(self):
        """Тестируем наличие форм у авторизируемого пользователя."""
        urls = (
            self.add_url,
            self.edit_url,
        )
        for url in urls:
            with self.subTest(self.author, url=url):
                response = self.auth_client.get(url)
                self.assertIn('form', response.context)
