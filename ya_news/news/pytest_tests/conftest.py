import pytest

from news.models import Comment, News


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
        title='Тестовая новость',
        text='Тестовый текст о новости',
    )
    return new


@pytest.fixture
# Создаём объект комментария.
def comment(author, new):
    comment = Comment.objects.create(
        news=new,
        author=author,
        text='Новый текст комментария',
    )
    return comment


# Добавляем фикстуру form_data для изменения комментария.
@pytest.fixture
def form_data():
    return {
        'text': 'Абсолютно новый текст',
    }
