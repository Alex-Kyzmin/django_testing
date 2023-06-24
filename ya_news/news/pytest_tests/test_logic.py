from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment
from news.pytest_tests.conftest import TEXT_COMMENT


@pytest.mark.django_db
def test_anonymous_cant_create_comment(client, form_data, detail_url):
    """Тестируем невозможность создания комментария анониму."""
    comments_count = Comment.objects.count()
    assert comments_count == 0
    client.post(detail_url, data=form_data)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_author_create_comment(
        author_client, form_data, detail_url, author, new,
):
    """Тестируем возможность создания комментария автору."""
    comments_count = Comment.objects.count()
    assert comments_count == 0
    response = author_client.post(detail_url, data=form_data)
    assertRedirects(response, f'{detail_url}#comments')
    comments_count = Comment.objects.count()
    assert comments_count == 1
    comment = Comment.objects.get()
    assert comment.text == form_data['text']
    assert comment.author == author
    assert comment.news == new


def test_author_delete_comment(author_client, delete_url, detail_url):
    """Тестируем возможность удаления комментария автору."""
    comments_count = Comment.objects.count()
    assert comments_count == 1
    response = author_client.delete(delete_url)
    assertRedirects(response, detail_url + '#comments')
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_author_edit_comment(
        author_client, comment, new, author,
        form_data, edit_url, detail_url,
):
    """Тестируем возможность редактирования комментария автору."""
    response = author_client.post(edit_url, data=form_data)
    assertRedirects(response, detail_url + '#comments')
    comment.refresh_from_db()
    assert comment.text == form_data['text']
    assert comment.author == author
    assert comment.news == new


def test_author_cant_use_bad_words(author_client, detail_url):
    """Тестируем невозможность создания комментария со стоп-словами."""
    comments_count = Comment.objects.count()
    assert comments_count == 0
    bad_words_data = {
        'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст',
    }
    response = author_client.post(detail_url, data=bad_words_data)
    assertFormError(response, form='form', field='text', errors=WARNING)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_reader_cant_delete_comment_of_author(
        reader_client, delete_url, author, comment,
):
    """Тестируем невозможность удаления комментария читателем."""
    comments_count = Comment.objects.count()
    assert comments_count == 1
    response = reader_client.delete(delete_url)
    assert response.status_code, HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == 1
    assert comment.author == author
    assert comment.text == TEXT_COMMENT


def test_reader_cant_edite_comment(
        reader_client, comment, form_data, edit_url
):
    """Тестируем невозможность редактирования комментария читателем."""
    response = reader_client.post(edit_url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == TEXT_COMMENT
