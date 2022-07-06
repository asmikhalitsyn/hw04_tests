from django.test import TestCase
from django.urls import reverse

from ..models import Post, Group, User

SLUG_OF_GROUP = 'test-slug'
USERNAME = 'TEST'
URL_OF_INDEX = reverse('posts:index')
URL_OF_POSTS_OF_GROUP = reverse('posts:group_list', args=[SLUG_OF_GROUP])
URL_TO_CREATE_POST = reverse('posts:post_create')
URL_OF_PROFILE = reverse('posts:profile', args=[USERNAME])
URL_OF_404_PAGE = '/unexisting_page/'


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USERNAME)
        cls.group = Group.objects.create(
            title='Test group',
            slug=SLUG_OF_GROUP,
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

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        cases = [
            [URL_OF_INDEX, '/'],
            [URL_OF_POSTS_OF_GROUP, f'/group/{SLUG_OF_GROUP}/'],
            [URL_OF_PROFILE, f'/profile/{USERNAME}/'],
            [self.URL_OF_DETAIL_POST, f'/posts/{self.post.id}/'],
            [self.URL_TO_EDIT_POST, f'/posts/{self.post.id}/edit/'],
            [URL_TO_CREATE_POST, '/create/']
        ]
        for name_of_url, url in cases:
            with self.subTest(name_of_url=name_of_url):
                self.assertEqual(name_of_url, url)


