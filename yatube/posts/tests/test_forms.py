from ..models import Post, Group, User

from django import forms
from django.test import Client, TestCase
from django.urls import reverse

URL_POST_CREATE = reverse('posts:post_create')


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
        cls.URL_POST_EDIT = reverse('posts:post_edit', args=[cls.post.pk])

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_task(self):
        tasks_count = Post.objects.count()
        form_data = {
            'text': 'Текст12345',
            'group': self.group.id,
        }
        self.authorized_client.post(URL_POST_CREATE, data=form_data)
        post = Post.objects.get(text='Текст12345')
        author = User.objects.get(username='test')
        group = Group.objects.get(title='Тестовая группа')
        self.assertEqual(Post.objects.count(), tasks_count + 1)
        self.assertEqual(Post.objects.count() - tasks_count, 1)
        self.assertEqual(post.text, 'Текст12345')
        self.assertEqual(author.username, 'test')
        self.assertEqual(group.title, 'Тестовая группа')

    def test_edit_post(self):
        form_data = {
            'text': 'Новый пост',
            'group': self.group.id,
        }
        self.authorized_client.post(self.URL_POST_EDIT, data=form_data)
        post = Post.objects.get(id=self.post.pk)
        author = User.objects.get(username='test')
        group = Group.objects.get(title='Тестовая группа')
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(author.username, 'test')
        self.assertEqual(group.title, 'Тестовая группа')

    def test_post_edit_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.URL_POST_EDIT)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_create_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(URL_POST_CREATE)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
