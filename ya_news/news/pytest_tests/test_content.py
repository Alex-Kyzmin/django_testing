from datetime import datetime, timedelta

import pytest
from django.conf import settings

from news.models import News


def test_home_pages_for_paginate_and_sorted(author_client, home_url):
    """Тест главной страницы на пагинацию и сортировку."""
    today = datetime.today()
    all_news = []
    for i in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1):
        news = News(
            title=f'Новость {i}',
            text=f'Текст новости {i}.',
            date=today - timedelta(days=i),
        )
        all_news.append(news)
        News.objects.bulk_create(all_news)
    response = author_client.get(home_url)
    object_list = response.context['object_list']
    # Тест на пагинацию:
    news_count = len(object_list)
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE
    # Тест на соритровку:
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


def test_comments_order(author_client, detail_url, comments):
    """Тест детальной страницы на сортировку комментарий."""
    response = author_client.get(detail_url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    assert all_comments[0].created < all_comments[1].created


@pytest.mark.django_db
def test_anonymous_client_has_no_form(client, detail_url):
    """Тест детальной страницы на отсутсвие форму у анонимa."""
    response = client.get(detail_url)
    assert 'form' not in response.context


def test_authorized_client_has_form(author_client, detail_url):
    """Тест детальной страницы на наличие форму у автора."""
    response = author_client.get(detail_url)
    """
    Очень хорошее замечание. Но пока не могу найти решения.
    Пробовал через response.context['form'] == CommentForm[]
    но не получилось. Посмотрел списки ассертов - ничего не нашел,
    буду признателен за совет или подсказку.(и в юнитесте)
    """
    assert 'form' in response.context
