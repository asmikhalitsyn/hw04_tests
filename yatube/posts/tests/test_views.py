from django.test import Client, TestCase
from django.urls import reverse

from ..models import Post, Group, User
from ..settings import POSTS_PER_PAGE

URL_OF_INDEX = reverse('posts:index')
URL_OF_POSTS_OF_GROUP = reverse('posts:group_list', args=['test_slug'])
URL_TO_CREATE_POST = reverse('posts:post_create')
URL_OF_PROFILE = reverse('posts:profile', args=['test_name1'])


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post = Post.objects.create(
            author=User.objects.create_user(username='test_name1'),
            text='Тестовая запись 1',
            group=Group.objects.create(
                title='Заголовок 1',
                slug='test_slug'))
        cls.post = Post.objects.create(
            author=User.objects.create_user(username='test_name2'),
            text='Тестовая запись 2',
            group=Group.objects.create(
                title='Заголовок 2',
                slug='test_slug2'))
        cls.URL_OF_DETAIL_POST = reverse(
            'posts:post_detail',
            args=[cls.post.pk]
        )
        cls.URL_TO_EDIT_POST = reverse('posts:post_edit', args=[cls.post.pk])

    def setUp(self):
        self.user = User.objects.create_user(username='testtest')
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_show_correct_context(self):
        """Шаблон сформирован с правильным контекстом."""
        self.URLS_LIST = {
             'page_obj': [
                          URL_OF_INDEX,
                          URL_OF_POSTS_OF_GROUP,
                          URL_OF_PROFILE
                    ],
             'post': [self.URL_OF_DETAIL_POST]
        }
        for key, urls in self.URLS_LIST.items():
            with self.subTest(key=key):
                for url in urls:
                    response = self.guest_client.get(url)
                    obj = response.context.get(key)
                    if key == 'post':
                        post_db = Post.objects.get(id=obj.id)
                        self.assertEqual(obj.text, post_db.text)
                        self.assertEqual(obj.author, post_db.author)
                        self.assertEqual(obj.group, post_db.group)
                    else:
                        for post in obj:
                            post_db = Post.objects.get(id=post.id)
                            self.assertEqual(post.text, post_db.text)
                            self.assertEqual(post.author,
                                             post_db.author)
                            self.assertEqual(post.group,
                                             post_db.group)

    def test_group_pages_correct_context(self):
        """Шаблон group_pages сформирован с правильным контекстом."""
        response = self.authorized_client.get(URL_OF_POSTS_OF_GROUP)
        group = response.context['group']
        group_db = Post.objects.get(id=group.id)
        self.assertEqual(group.title, group_db.group.title)
        self.assertEqual(group.slug, group_db.group.slug)
        self.assertEqual(group.description, group_db.group.description)

    def test_post_another_group(self):
        """Пост не попал в другую группу"""
        group = Group.objects.get(slug='test_slug2')
        response = self.authorized_client.get(URL_OF_POSTS_OF_GROUP)
        post = response.context['page_obj'][0]
        self.assertNotEqual(post.group.slug, group.slug)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_name1')
        cls.group = Group.objects.create(
            title='Test group',
            slug='test_slug',
            description='Тестовое описание',
        )
        Post.objects.bulk_create([Post(
            text=f'Тестовый пост {number}',
            author=cls.user,
            group=cls.group)
            for number in range(POSTS_PER_PAGE + 1)])

    def setUp(self):
        self.guest_client = Client()

    def test_paginator(self):
        post_count = Post.objects.count()
        self.urls = {URL_OF_INDEX: POSTS_PER_PAGE,
                     URL_OF_POSTS_OF_GROUP: POSTS_PER_PAGE,
                     URL_OF_PROFILE: POSTS_PER_PAGE,
                     URL_OF_INDEX + "?page=2": post_count - POSTS_PER_PAGE,
                     URL_OF_POSTS_OF_GROUP + "?page=2":
                         post_count - POSTS_PER_PAGE,
                     URL_OF_PROFILE + "?page=2":
                         post_count - POSTS_PER_PAGE}

        for url, post_count in self.urls.items():
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(
                    len(response.context.get('page_obj')), post_count
                )
