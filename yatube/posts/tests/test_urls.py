from http import HTTPStatus

from django.test import TestCase, Client
from django.urls import reverse

from ..models import Post, Group, User

URL_INDEX = reverse('posts:index')
URL_GROUP_LIST = reverse('posts:group_list', args=['test-slug'])
URL_POST_CREATE = reverse('posts:post_create')


class PostURLTests(TestCase):
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
            text='Тестовая пост',
        )
        cls.URL_PROFILE = reverse('posts:profile', args=[cls.post.author.username])
        cls.URL_POST_DETAIL = reverse('posts:post_detail', args=[cls.post.pk])
        cls.EDIT_PAGE = reverse('posts:post_edit', args=[cls.post.pk])

    def setUp(self):
        self.templates_url_for_all_users = {
            URL_INDEX: 'posts/index.html',
            URL_GROUP_LIST: 'posts/group_list.html',
            self.URL_PROFILE: 'posts/profile.html',
            self.URL_POST_DETAIL: 'posts/post_detail.html',
        }
        self.templates_url_for_edit_page = {self.EDIT_PAGE: 'posts/create_post.html'}
        self.templates_url_for_authorized = {URL_POST_CREATE: 'posts/create_post.html'}
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for address, template in self.templates_url_for_all_users.items():
            with self.subTest(addresss=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_unexisting_page(self):
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_create_page_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for address, template in self.templates_url_for_authorized.items():
            with self.subTest(addresss=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_edit_page_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for address, template in self.templates_url_for_edit_page.items():
            with self.subTest(addresss=address):
                if self.post.author.username == self.user:
                    response = self.authorized_client.get(address)
                    self.assertTemplateUsed(response, template)

    def test_create_url_redirect_for_create(self):
        """Страница /create/ перенаправляет анонимного пользователя."""
        response = self.guest_client.get(URL_POST_CREATE, follow=True)
        self.assertRedirects(response, '/auth/login/?next=/create/')

    def test_create_url_redirect_for_edit(self):
        """Страница posts:post_edit перенаправляет анонимного пользователя."""
        response = self.guest_client.get(self.EDIT_PAGE, follow=True)
        self.assertRedirects(response, f'/auth/login/?next=/posts/{self.post.pk}/edit/')
