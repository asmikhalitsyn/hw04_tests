from ..models import Post, Group

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class TaskCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.get(username='test')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_task(self):
        tasks_count = Post.objects.count()
        form_data = {
            'text': 'Текст12345',
            'group': self.group.id,
        }
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data
        )
        self.assertEqual(Post.objects.count(), tasks_count + 1)

    def test_edit_post(self):
        form_data = {'text': 'Новый пост'}
        self.authorized_client.post(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': TaskCreateFormTests.post.pk}
            ),
            data=form_data,
        )
        post_edit = Post.objects.get(id=TaskCreateFormTests.post.pk)
        self.assertEqual(
            post_edit.text, 'Новый пост'
        )
