from django.test import Client, TestCase
from django.urls import reverse

from ..models import Post, Group, User
from ..settings import POSTS_PER_PAGE

URL_OF_INDEX = reverse('posts:index')
URL_OF_POSTS_OF_GROUP = reverse('posts:group_list', args=['test-slug'])
URL_TO_CREATE_POST = reverse('posts:post_create')
URL_OF_PROFILE = reverse('posts:profile', args=['HasNoName'])
COUNT_OF_POST = 15


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group
        )
        cls.group_2 = Group.objects.create(
            title='Тестовая группа2',
            slug='test-slug2',
            description='Тестовое описание2',
        )
        cls.URL_OF_DETAIL_POST = reverse(
            'posts:post_detail',
            args=[cls.post.pk]
        )
        cls.URL_TO_EDIT_POST = reverse('posts:post_edit', args=[cls.post.pk])

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_show_correct_context(self):
        """Шаблон сформирован с правильным контекстом."""
        self.URLS_LIST = [
            URL_OF_INDEX,
            URL_OF_POSTS_OF_GROUP,
            URL_OF_PROFILE,
            self.URL_OF_DETAIL_POST
        ]
        for address in self.URLS_LIST:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                if 'post' in response.context:
                    post = response.context.get('post')
                else:
                    paginator_object = response.context.get('page_obj')
                    post = response.context.get('page_obj')[0]
                    if len(paginator_object) > 1:
                        raise TypeError('Число постов на странице больше 1')
                self.assertEqual(post.text, self.post.text)
                self.assertEqual(post.author.username,
                                 self.post.author.username)
                self.assertEqual(post.group.slug,
                                 self.post.group.slug)
                self.assertEqual(post.pk,
                                 self.post.pk)

    def test_group_pages_correct_context(self):
        """Шаблон group_pages сформирован с правильным контекстом."""
        response = self.authorized_client.get(URL_OF_POSTS_OF_GROUP)
        group = response.context['group']
        group_title_0 = group.title
        group_slug_0 = group.slug
        group_description_0 = group.description
        group_pk = group.pk
        self.assertEqual(group_title_0, self.group.title)
        self.assertEqual(group_slug_0, self.group.slug)
        self.assertEqual(group_description_0, self.group.description)
        self.assertEqual(group_pk, self.group.pk)

    def test_post_another_group(self):
        """Пост не попал в другую группу"""
        response = self.authorized_client.get(URL_OF_POSTS_OF_GROUP)
        post = response.context['page_obj'][0]
        post_group_slug_0 = post.group.slug
        self.assertTrue(post_group_slug_0, self.group_2.slug)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        Post.objects.bulk_create([Post(
            text=f'Тестовый пост {number}',
            author=cls.user,
            group=cls.group)
            for number in range(COUNT_OF_POST)
            if COUNT_OF_POST > POSTS_PER_PAGE])

    def setUp(self):
        self.guest_client = Client()

    def test_paginator(self):
        self.urls = {URL_OF_INDEX: POSTS_PER_PAGE,
                     URL_OF_POSTS_OF_GROUP: POSTS_PER_PAGE,
                     URL_OF_PROFILE: POSTS_PER_PAGE,
                     URL_OF_INDEX + "?page=2": COUNT_OF_POST - POSTS_PER_PAGE,
                     URL_OF_POSTS_OF_GROUP + "?page=2":
                         COUNT_OF_POST - POSTS_PER_PAGE,
                     URL_OF_PROFILE + "?page=2":
                         COUNT_OF_POST - POSTS_PER_PAGE}

        for url, post_count in self.urls.items():
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(
                    len(response.context.get('page_obj')), post_count
                )
