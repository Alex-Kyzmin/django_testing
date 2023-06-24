from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News


# Константы текста для новости, комментария, формы комментария.
TEXT_COMMENT = 'Новый текст комментария'
TITLE_NEW = 'Тестовая новость'
TEXT_NEW = 'Тестовый текст о новости'
TEXT_FORM = 'Абсолютно новый текст'


@pytest.fixture
# Создаем автора для комментария.
def author(django_user_model):
    return django_user_model.objects.create(username='Комментатор')


@pytest.fixture
# Вызываем фикстуру автора и клиента.
def author_client(author, client):
    # Логиним автора в клиенте.
    client.force_login(author)
    return client


@pytest.fixture
# Создаем читателя для тестов.
def reader(django_user_model):
    return django_user_model.objects.create(username='Читатель')


@pytest.fixture
# Вызываем фикстуру читателя и клиента.
def reader_client(reader, client):
    # Логиним читателя в клиенте.
    client.force_login(reader)
    return client


@pytest.fixture
# Создаём новость в БД для комментирования.
def new():
    new = News.objects.create(
        title=TITLE_NEW,
        text=TEXT_NEW,
    )
    return new


@pytest.fixture
# Создаём объект комментария.
def comment(author, new):
    comment = Comment.objects.create(
        news=new,
        author=author,
        text=TEXT_COMMENT,
    )
    return comment


@pytest.fixture
# Создаём объект комментария.
def comments(author, new):
    now = timezone.now()
    for i in range(2):
        comment = Comment.objects.create(
            news=new,
            author=author,
            text=f'Текст комментария {i}',
        )
        comment.created = now + timedelta(days=i)
        comment.save()
    return comments


# Добавляем фикстуру form_data для изменения комментария.
@pytest.fixture
def form_data():
    return {
        'text': TEXT_FORM,
    }


# Добавляем фикстуры url для всех тестов.
@pytest.fixture
def home_url():
    return reverse('news:home')


@pytest.fixture
def login_url():
    return reverse('users:login')


@pytest.fixture
def logout_url():
    return reverse('users:logout')


@pytest.fixture
def signup_url():
    return reverse('users:signup')


@pytest.fixture
def detail_url(new):
    return reverse('news:detail', args=(new.id,))


@pytest.fixture
def delete_url(comment):
    return reverse('news:delete', args=(comment.id,))


@pytest.fixture
def edit_url(comment):
    return reverse('news:edit', args=(comment.id,))
