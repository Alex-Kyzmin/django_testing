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
        cls.list_url = reverse('notes:list')

    def test_content_list_pages(self):
        """Тестируем контент страницы со списком заметок."""
        # Загружаем страницу со списком заметок.
        response = self.auth_client.get(self.list_url)
        # Тест № 1: Проверяем, что объект новости находится в словаре контекста
        # под ожидаемым именем - названием модели.
        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)
        # Тест № 2: Проверяем, что на странице со списком только записи автора.
        # Определяем длину списка.
        list_length = len(object_list)
        # Проверяем, что на странице со списком именно 1 заметка от автора.
        self.assertEqual(list_length, 1)

    def test_authorized_client_has_form(self):
        """Тестируем наличие форм у авторизируемого пользователя."""
        # Логиним пользователя в клиенте:
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,)),
        )
        for name, args in urls:
            with self.subTest(self.author, name=name):
                url = reverse(name, args=args)
                response = self.auth_client.get(url)
                self.assertIn('form', response.context)
