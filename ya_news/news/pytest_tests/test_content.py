from datetime import datetime, timedelta

import pytest
from django.conf import settings
from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News


def test_home_pages_for_paginate_and_sorted(author_client):
    """Тест главной страницы на пагинацию и сортировку."""
    # Вычисляем текущую дату.
    today = datetime.today()
    # Подготавливаем серию новостей в БД
    all_news = []
    for i in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1):
        news = News(
            title=f'Новость {i}',
            text=f'Текст новости {i}.',
            date=today - timedelta(days=i),
        )
        all_news.append(news)
        News.objects.bulk_create(all_news)
    url = reverse('news:home')
    # Загружаем главную страницу.
    response = author_client.get(url)
    # Получаем список объектов из словаря контекста.
    object_list = response.context['object_list']
    # Тест на пагинацию:
    # Определяем длину списка.
    news_count = len(object_list)
    # Проверяем, что на странице именно 10 новостей.
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE
    # Тест на соритровку:
    # Получаем даты новостей в том порядке, как они выведены на странице.
    all_dates = [news.date for news in object_list]
    # Сортируем полученный список по убыванию.
    sorted_dates = sorted(all_dates, reverse=True)
    # Проверяем, что исходный список был отсортирован правильно.
    assert all_dates == sorted_dates


def test_comments_order(author_client, new, author):
    """Тест детальной страницы на сортировку комментарий."""
    now = timezone.now()
    # Создаём комментарии в цикле.
    for i in range(2):
        # Создаём объект и записываем его в переменную.
        comment = Comment.objects.create(
            news=new,
            author=author,
            text=f'Текст комментария {i}',
        )
        # Сразу после создания меняем время создания комментария.
        comment.created = now + timedelta(days=i)
        comment.save()
        return comment
    detail_url = reverse('news:detail', args=(new.id,))
    response = author_client.get(detail_url)
    # Проверяем, что объект новости находится в словаре контекста
    # под ожидаемым именем - названием модели.
    assert 'news' in response.context
    # Получаем объект новости.
    news = response.context['news']
    # Получаем все комментарии к новости.
    all_comments = news.comment_set.all()
    # Проверяем, что время создания первого комментария в списке
    # меньше, чем время создания второго.
    assert all_comments[0].created < all_comments[1].created


@pytest.mark.django_db
def test_anonymous_client_has_no_form(client, new):
    """Тест детальной страницы на отсутсвие форму у анонимa."""
    detail_url = reverse('news:detail', args=(new.id,))
    response = client.get(detail_url)
    assert 'form' not in response.context


def test_authorized_client_has_form(author_client, new):
    """Тест детальной страницы на наличие форму у автора."""
    detail_url = reverse('news:detail', args=(new.id,))
    response = author_client.get(detail_url)
    assert 'form' in response.context
