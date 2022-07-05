from ..models import Post, Group, User

from django import forms
from django.test import Client, TestCase
from django.urls import reverse

URL_TO_CREATE_POST = reverse('posts:post_create')
URL_OF_PROFILE = reverse('posts:profile', args=['test'])


class TaskCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test')
        cls.group = Group.objects.create(
            title='Test group',
            slug='test_slug',
            description='Тестовое описание',
        )

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
        response = self.authorized_client.post(
            URL_TO_CREATE_POST, data=form_data, follow=True
        )
        post = Post.objects.get(id=self.group.id)
        self.assertRedirects(response, URL_OF_PROFILE)
        self.assertEqual(Post.objects.count(), tasks_count + 1)
        self.assertEqual(Post.objects.count() - tasks_count, 1)
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group.id, form_data['group'])

    def test_edit_post(self):
        form_data = {
            'text': 'Новый пост',
            'group': self.group.id,
        }
        self.authorized_client.post(
            URL_TO_CREATE_POST, data=form_data
        )
        post = Post.objects.get(id=self.group.id)
        self.URL_TO_EDIT_POST = reverse('posts:post_edit', args=[post.id])
        self.URL_OF_DETAIL_POST = reverse('posts:post_detail', args=[post.id])
        form_data = {
            'text': 'Измененный пост',
            'group': self.group.id
        }
        response_edit = self.authorized_client.post(
            self.URL_TO_EDIT_POST, data=form_data, follow=True
        )
        post = Post.objects.get(id=self.group.id)
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group.id, form_data['group'])
        self.assertEqual(
            post.author,
            response_edit.context['post'].author
        )
        self.assertRedirects(response_edit, self.URL_OF_DETAIL_POST)

    def test_post_edit_correct_context(self):
        """Шаблон post_edit и post_create
          сформированы с правильными контекстами."""
        self.post = Post.objects.create(
            author=self.user,
            text='Тестовая пост',
        )
        post = Post.objects.get(id=self.post.id)
        self.URL_TO_EDIT_POST = reverse('posts:post_edit', args=[post.pk])
        self.URLS_LIST = [self.URL_TO_EDIT_POST, URL_TO_CREATE_POST]
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for url in self.URLS_LIST:
            response = self.authorized_client.get(url)
            for value, expected in form_fields.items():
                with self.subTest(value=value):
                    form_field = response.context.get('form').fields.get(value)
                    self.assertIsInstance(form_field, expected)
