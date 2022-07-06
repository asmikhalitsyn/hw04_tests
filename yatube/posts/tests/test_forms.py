from ..models import Post, Group, User

from django import forms
from django.test import Client, TestCase
from django.urls import reverse

SLUG_OF_GROUP = 'test_slug'
SLUG_OF_GROUP_2 = 'test_slug2'
URL_TO_CREATE_POST = reverse('posts:post_create')
URL_OF_PROFILE = reverse('posts:profile', args=['test'])


class TaskCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test')
        cls.group = Group.objects.create(
            title='Test group',
            slug=SLUG_OF_GROUP,
            description='Тестовое описание',
        )
        cls.group_2 = Group.objects.create(
            title='Test group2',
            slug=SLUG_OF_GROUP_2,
            description='Тестовое описание2',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост')
        cls.post_2 = Post.objects.create(
            author=cls.user,
            text='Тестовый пост77')

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_task(self):
        post_all = set(Post.objects.all())
        form_data = {
            'text': 'Текст12345',
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            URL_TO_CREATE_POST, data=form_data, follow=True
        )
        post_all_with_new_post = set(Post.objects.all())
        post_obj = list(post_all_with_new_post.difference(post_all))
        self.assertTrue(len(post_obj) == 1, 'Число постов больше 1')
        new_post = post_obj[0]
        self.assertRedirects(response, URL_OF_PROFILE)
        self.assertEqual(new_post.text, form_data['text'])
        self.assertEqual(new_post.group.id, form_data['group'])
        self.assertEqual(new_post.author, self.user)

    def test_edit_post(self):
        post_all = set(Post.objects.all())
        form_data = {
            'text': 'Новый пост',
            'group': self.group.id,
        }
        self.authorized_client.post(
            URL_TO_CREATE_POST, data=form_data
        )
        post_all_with_new_post = set(Post.objects.all())
        new_post = list(post_all_with_new_post.difference(post_all))[0]
        self.URL_TO_EDIT_POST = reverse('posts:post_edit', args=[new_post.id])
        self.URL_OF_DETAIL_POST = reverse('posts:post_detail',
                                          args=[new_post.id])
        form_data = {
            'text': 'Измененный пост',
            'group': self.group_2.id
        }
        response_edit = self.authorized_client.post(
            self.URL_TO_EDIT_POST, data=form_data, follow=True
        )
        post = response_edit.context['post']
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group.id, form_data['group'])
        self.assertEqual(
            post.author,
            new_post.author
        )
        self.assertRedirects(response_edit, self.URL_OF_DETAIL_POST)

    def test_post_edit_correct_context(self):
        """Шаблон post_edit и post_create
          сформированы с правильными контекстами."""
        self.post = Post.objects.create(
            author=self.user,
            text='Тестовая пост',
        )
        self.URL_TO_EDIT_POST = reverse('posts:post_edit', args=[self.post.pk])
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
