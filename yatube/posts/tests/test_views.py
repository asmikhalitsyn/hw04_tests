from django.test import Client, TestCase
from django.urls import reverse

from ..models import Post, Group, User
from ..settings import POSTS_PER_PAGE

SLUG_OF_GROUP = 'test_slug'
SLUG_OF_GROUP_2 = 'test_slug2'
USERNAME = 'TEST'
URL_OF_INDEX = reverse('posts:index')
URL_OF_POSTS_OF_GROUP = reverse('posts:group_list', args=[SLUG_OF_GROUP])
URL_OF_POSTS_OF_GROUP_2 = reverse('posts:group_list', args=[SLUG_OF_GROUP_2])
URL_TO_CREATE_POST = reverse('posts:post_create')
URL_OF_PROFILE = reverse('posts:profile', args=[USERNAME])


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USERNAME)
        cls.group = Group.objects.create(
            title='Заголовок 1',
            slug=SLUG_OF_GROUP
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая запись 1',
            group=cls.group
        )
        cls.group_2 = Group.objects.create(
            title='Заголовок 2',
            slug=SLUG_OF_GROUP_2
        )
        cls.post_2 = Post.objects.create(
            author=cls.user,
            text='Тестовая запись 2',
            group=cls.group_2
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
        cases = [
            [URL_OF_INDEX, 'page_obj'],
            [URL_OF_POSTS_OF_GROUP, 'page_obj'],
            [URL_OF_PROFILE, 'page_obj'],
            [self.URL_OF_DETAIL_POST, 'post'],
        ]
        for url, key in cases:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                obj = response.context.get(key)
                if isinstance(obj, Post):
                    self.assertEqual(self.post, obj)
                else:
                    self.assertIn(self.post, obj.object_list)

    def test_group_pages_correct_context(self):
        """Шаблон group_pages сформирован с правильным контекстом."""
        response = self.authorized_client.get(URL_OF_POSTS_OF_GROUP)
        group = response.context['group']
        self.assertEqual(group, self.group)

    def test_post_another_group(self):
        """Пост не попал в другую группу"""
        response = self.authorized_client.get(URL_OF_POSTS_OF_GROUP_2)
        post = response.context['page_obj'][0]
        self.assertNotEqual(self.post.text, post.text)

    def test_author_in_profile(self):
        response = self.guest_client.get(URL_OF_PROFILE)
        author_of_page = response.context['author']
        self.assertEqual(self.user, author_of_page)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USERNAME)
        cls.group = Group.objects.create(
            title='Test group',
            slug=SLUG_OF_GROUP,
            description='Тестовое описание',
        )
        Post.objects.bulk_create(Post(
            text=f'Тестовый пост {number}',
            author=cls.user,
            group=cls.group)
            for number in range(POSTS_PER_PAGE + 1))

    def setUp(self):
        self.guest_client = Client()

    def test_paginator(self):
        post_count = Post.objects.count()
        self.urls = {
            URL_OF_INDEX: POSTS_PER_PAGE,
            URL_OF_POSTS_OF_GROUP: POSTS_PER_PAGE,
            URL_OF_PROFILE: POSTS_PER_PAGE,
            URL_OF_INDEX + "?page=2": 1,
            URL_OF_POSTS_OF_GROUP + "?page=2": 1,
            URL_OF_PROFILE + "?page=2": 1
        }

        for url, post_count in self.urls.items():
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(
                    len(response.context.get('page_obj')), post_count
                )
