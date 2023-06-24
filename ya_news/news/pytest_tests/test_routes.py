from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects


@pytest.mark.parametrize(
    'user, expected_status, url',
    (
        (pytest.lazy_fixture('client'), HTTPStatus.OK,
         pytest.lazy_fixture('home_url')),
        (pytest.lazy_fixture('client'),
         HTTPStatus.OK,
         pytest.lazy_fixture('login_url')),
        (pytest.lazy_fixture('client'),
         HTTPStatus.OK,
         pytest.lazy_fixture('logout_url')),
        (pytest.lazy_fixture('client'),
         HTTPStatus.OK,
         pytest.lazy_fixture('signup_url')),
        (pytest.lazy_fixture('author_client'),
         HTTPStatus.OK,
         pytest.lazy_fixture('edit_url')),
        (pytest.lazy_fixture('author_client'),
         HTTPStatus.OK,
         pytest.lazy_fixture('delete_url')),
        (pytest.lazy_fixture('reader_client'),
         HTTPStatus.NOT_FOUND,
         pytest.lazy_fixture('edit_url')),
        (pytest.lazy_fixture('reader_client'),
         HTTPStatus.NOT_FOUND,
         pytest.lazy_fixture('delete_url')),
    ),
)
@pytest.mark.django_db
def test_availability_for_comment_edit_and_delete(user, expected_status, url):
    """Тест на редакт./удаление комментарий автору/читателю."""
    response = user.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'pages',
    (pytest.lazy_fixture('edit_url'), pytest.lazy_fixture('delete_url'),),
)
@pytest.mark.django_db
def test_redirect_for_anonymous_client(pages, client):
    """Тест на редирект анон. при редактирование/удаление комментарий."""
    login_url = reverse('users:login')
    redirect_url = f'{login_url}?next={pages}'
    response = client.get(pages)
    assertRedirects(response, redirect_url)
