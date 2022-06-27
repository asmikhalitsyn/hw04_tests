from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from ..models import Post, Group

User = get_user_model()


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

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.get(username='HasNoName')
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.user)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        post_id = PostURLTests.post.pk
        author = PostURLTests.post.author
        templates_url_names = {
            '/': 'posts/index.html',
            '/group/test-slug/': 'posts/group_list.html',
            f'/profile/{author}/': 'posts/profile.html',
            f'/posts/{post_id}/': 'posts/post_detail.html',
            f'/posts/{post_id}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
            '/unexisting_page/': ''
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                if address == '/create/' \
                        or (address == f'/posts/{post_id}/edit/'
                            and author == self.user):
                    response = self.authorized_client.get(address)
                elif address == '/unexisting_page/':
                    response = self.guest_client.get(address)
                    self.assertEqual(response.status_code, 404)
                    break
                else:
                    response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)
