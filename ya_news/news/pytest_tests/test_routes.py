from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects


@pytest.mark.parametrize(
    'pages',
    ('news:home', 'news:detail', 'users:login',
     'users:logout', 'users:signup',)
)
@pytest.mark.django_db
def test_pages_availability_for_auth_user(client, pages, new):
    """Тест на доступность страниц анонимному пользователю."""
    if pages == 'news:detail':
        url = reverse(pages, args=(new.id,))
    else:
        url = reverse(pages)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'user, expected_status',
    (
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK),
        (pytest.lazy_fixture('reader_client'), HTTPStatus.NOT_FOUND),
    ),
)
@pytest.mark.parametrize(
    'pages',
    ('news:edit', 'news:delete',),
)
def test_availability_for_comment_edit_and_delete(
    user, expected_status, pages, comment
):
    """Тест на редакт./удаление комментарий автору/читателю."""
    url = reverse(pages, args=(comment.id,))
    response = user.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'pages',
    ('news:edit', 'news:delete',),
)
def test_redirect_for_anonymous_client(pages, comment, client):
    """Тест на редирект анон. при редактирование/удаление комментарий."""
    login_url = reverse('users:login')
    url = reverse(pages, args=(comment.id,))
    redirect_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, redirect_url)
