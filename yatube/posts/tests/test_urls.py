from http import HTTPStatus

from django.test import TestCase, Client
from django.urls import reverse

from ..models import Post, Group, User

URL_OF_INDEX = reverse('posts:index')
URL_OF_POSTS_OF_GROUP = reverse('posts:group_list', args=['test-slug'])
URL_TO_CREATE_POST = reverse('posts:post_create')
URL_OF_PROFILE = reverse('posts:profile', args=['HasNoName'])
URL_OF_404_PAGE = '/unexisting_page/'
URL_FOR_REDIRECT_TO_CREATE_PAGE = '/auth/login/?next=/create/'


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.group = Group.objects.create(
            title='Test group',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая пост',
        )
        cls.URL_FOR_REDIRECT_TO_EDIT_PAGE = (
            f'/auth/login/?next=/posts/{cls.post.pk}/edit/'
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
        self.response_to_template = {
            self.guest_client.get(URL_OF_INDEX):
                'posts/index.html',
            self.guest_client.get(URL_OF_POSTS_OF_GROUP):
                'posts/group_list.html',
            self.guest_client.get(URL_OF_PROFILE):
                'posts/profile.html',
            self.guest_client.get(self.URL_OF_DETAIL_POST):
                'posts/post_detail.html',
            self.authorized_client.get(self.URL_TO_EDIT_POST):
                'posts/create_post.html',
            self.authorized_client.get(URL_TO_CREATE_POST):
                'posts/create_post.html',
        }
        for response, template in self.response_to_template.items():
            with self.subTest(response=response):
                self.assertTemplateUsed(response, template)

    def test_status_of_pages(self):
        self.status_of_response = {
            self.guest_client.get(URL_OF_INDEX): HTTPStatus.OK,
            self.guest_client.get(URL_OF_POSTS_OF_GROUP): HTTPStatus.OK,
            self.guest_client.get(URL_OF_PROFILE): HTTPStatus.OK,
            self.guest_client.get(self.URL_OF_DETAIL_POST): HTTPStatus.OK,
            self.authorized_client.get(self.URL_TO_EDIT_POST): HTTPStatus.OK,
            self.authorized_client.get(URL_TO_CREATE_POST): HTTPStatus.OK,
            self.guest_client.get(URL_OF_404_PAGE): HTTPStatus.NOT_FOUND,
        }
        for response, status in self.status_of_response.items():
            with self.subTest(response=response):
                self.assertEqual(response.status_code, status)

    def test_url_redirect(self):
        """Страница перенаправляет анонимного пользователя."""
        self.url_to_redirect = {
            URL_TO_CREATE_POST: URL_FOR_REDIRECT_TO_CREATE_PAGE,
            self.URL_TO_EDIT_POST: self.URL_FOR_REDIRECT_TO_EDIT_PAGE
        }
        for url, url_of_redirect in self.url_to_redirect.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url, follow=True)
                self.assertRedirects(response, url_of_redirect)
