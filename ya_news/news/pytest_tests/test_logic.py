from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_cant_create_comment(client, new, form_data):
    """Тестируем невозможность создания комментария анониму."""
    detail_url = reverse('news:detail', args=(new.id,))
    # Совершаем POST-запрос от анонима c формой текста комментария.
    client.post(detail_url, data=form_data)
    # Считаем количество комментариев.
    comments_count = Comment.objects.count()
    # Ожидаем, что комментариев в базе нет - сравниваем с нулём.
    assert comments_count == 0


def test_author_create_comment(author_client, new, form_data):
    """Тестируем возможность создания комментария автору."""
    detail_url = reverse('news:detail', args=(new.id,))
    # Совершаем POST-запрос от атора c формой текста комментария.
    response = author_client.post(detail_url, data=form_data)
    # Проверяем, что редирект привёл к разделу с комментами.
    assertRedirects(response, f'{detail_url}#comments')
    # Считаем количество комментариев.
    comments_count = Comment.objects.count()
    # Убеждаемся, что есть один комментарий.
    assert comments_count == 1
    # Получаем объект комментария из базы.
    comment = Comment.objects.get()
    # Проверяем, что текст комментария совпадают с ожидаемым.
    assert comment.text == form_data['text']


def test_author_delete_comment(author_client, comment, new):
    """Тестируем возможность удаления комментария автору."""
    delete_url = reverse('news:delete', args=(comment.id,))
    new_url = reverse('news:detail', args=(new.id,))
    # От автора комментария отправляем DELETE-запрос на удаление.
    response = author_client.delete(delete_url)
    # Проверяем, что редирект привёл к разделу с комментариями.
    # Заодно проверим статус-коды ответов.
    assertRedirects(response, new_url + '#comments')
    # Считаем количество комментариев в системе.
    comments_count = Comment.objects.count()
    # Ожидаем ноль комментариев в системе.
    assert comments_count == 0


def test_author_edit_comment(author_client, comment, form_data, new):
    """Тестируем возможность редактирования комментария автору."""
    edit_url = reverse('news:edit', args=(comment.id,))
    new_url = reverse('news:detail', args=(new.id,))
    # Выполняем POST-запрос на редактирование от автора комментария.
    response = author_client.post(edit_url, data=form_data)
    # Проверяем, что сработал редирект.
    assertRedirects(response, new_url + '#comments')
    # Обновляем объект комментария.
    comment.refresh_from_db()
    # Проверяем, что текст комментария соответствует обновленному.
    assert comment.text == form_data['text']


def test_author_cant_use_bad_words(author_client, new):
    """Тестируем невозможность создания комментария со стоп-словами."""
    detail_url = reverse('news:detail', args=(new.id,))
    # Формируем данные для отправки включая стоп-слова.
    bad_words_data = {
        'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст',
    }
    # Отправляем запрос через авторизованный клиент.
    response = author_client.post(detail_url, data=bad_words_data)
    # Проверяем, есть ли в ответе ошибка формы.
    assertFormError(response, form='form', field='text', errors=WARNING)
    # Дополнительно убедимся, что комментарий не был создан.
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_reader_cant_delete_comment_of_author(reader_client, comment):
    """Тестируем невозможность удаления комментария читателем."""
    delete_url = reverse('news:delete', args=(comment.id,))
    # Выполняем запрос на удаление от читателя.
    response = reader_client.delete(delete_url)
    # Проверяем, что вернулась 404 ошибка.
    assert response.status_code, HTTPStatus.NOT_FOUND
    # Убедимся, что комментарий не удален.
    comments_count = Comment.objects.count()
    assert comments_count == 1


def test_reader_cant_edite_comment(reader_client, comment, form_data):
    """Тестируем невозможность редактирования комментария читателем."""
    edit_url = reverse('news:edit', args=(comment.id,))
    # Выполняем запрос на редактирование от имени другого пользователя.
    response = reader_client.post(edit_url, data=form_data)
    # Проверяем, что вернулась 404 ошибка.
    assert response.status_code == HTTPStatus.NOT_FOUND
    # Обновляем объект комментария.
    comment.refresh_from_db()
    # Проверяем, что текст остался тем же, что и был.
    assert comment.text == 'Новый текст комментария'
