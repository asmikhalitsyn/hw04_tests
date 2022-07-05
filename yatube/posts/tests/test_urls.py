from http import HTTPStatus
from urllib.parse import urljoin

from django.test import TestCase, Client
from django.urls import reverse

from ..models import Post, Group, User

URL_OF_INDEX = reverse('posts:index')
URL_OF_POSTS_OF_GROUP = reverse('posts:group_list', args=['test-slug'])
URL_TO_CREATE_POST = reverse('posts:post_create')
URL_OF_PROFILE = reverse('posts:profile', args=['test'])
URL_OF_404_PAGE = '/unexisting_page/'


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test')
        cls.group = Group.objects.create(
            title='Test group',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая пост',
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

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        self.client_to_data = {
            self.guest_client.get:
                [
                    [URL_OF_INDEX, 'posts/index.html'],
                    [URL_OF_POSTS_OF_GROUP, 'posts/group_list.html'],
                    [URL_OF_PROFILE, 'posts/profile.html'],
                    [self.URL_OF_DETAIL_POST, 'posts/post_detail.html']
                ],
            self.authorized_client.get: [
                [self.URL_TO_EDIT_POST, 'posts/create_post.html'],
                [URL_TO_CREATE_POST, 'posts/create_post.html']]
        }

        for client, value in self.client_to_data.items():
            for url, template in value:
                with self.subTest(url=url):
                    self.assertTemplateUsed(client(url), template)

    def test_status_of_pages(self):
        self.client_to_data = {
            self.guest_client.get:
                [
                    [URL_OF_INDEX, HTTPStatus.OK],
                    [URL_OF_POSTS_OF_GROUP, HTTPStatus.OK],
                    [URL_OF_PROFILE, HTTPStatus.OK],
                    [self.URL_OF_DETAIL_POST, HTTPStatus.OK],
                    [URL_OF_404_PAGE, HTTPStatus.NOT_FOUND]
                ],
            self.authorized_client.get: [
                [self.URL_TO_EDIT_POST, HTTPStatus.OK],
                [URL_TO_CREATE_POST, HTTPStatus.OK]]
        }
        for client, value in self.client_to_data.items():
            for url, status in value:
                with self.subTest(url=url):
                    self.assertEqual(client(url).status_code, status)

    def test_url_redirect(self):
        self.user = User.objects.create_user(username='test123')
        self.authorized_client.force_login(self.user)
        self.url_to_redirect = {
            self.guest_client.get:
                [
                    [URL_TO_CREATE_POST,
                     urljoin(reverse('login'), '?next=/create/')],
                    [self.URL_TO_EDIT_POST,
                     urljoin(
                         reverse('login'), f'?next=/posts/{self.post.pk}/edit/'
                     )],
                ],
            self.authorized_client.get: [
                [self.URL_TO_EDIT_POST, self.URL_OF_DETAIL_POST]]
        }
        for client, value in self.url_to_redirect.items():
            for url, url_redirect in value:
                with self.subTest(url=url):
                    self.assertRedirects(
                        client(url, follow=True),
                        url_redirect
                    )
