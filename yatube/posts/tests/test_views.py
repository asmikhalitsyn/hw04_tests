from django.test import Client, TestCase
from django.urls import reverse

from ..models import Post, Group, User
from ..settings import PAGE_COUNT

URL_INDEX = reverse('posts:index')
URL_GROUP_LIST = reverse('posts:group_list', args=['test-slug'])
URL_POST_CREATE = reverse('posts:post_create')


class PostPagesTests(TestCase):
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
            text='Тестовый пост',
            group=cls.group
        )
        cls.URL_PROFILE = reverse(
            'posts:profile',
            args=[cls.post.author.username]
        )
        cls.URL_POST_DETAIL = reverse(
            'posts:post_detail',
            args=[cls.post.pk]
        )
        cls.EDIT_PAGE = reverse(
            'posts:post_edit',
            args=[cls.post.pk]
        )

    def setUp(self):
        self.URLS_LIST = [URL_INDEX, URL_GROUP_LIST, self.URL_PROFILE]
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        for address in self.URLS_LIST:
            with self.subTest(addresss=address):
                response = self.guest_client.get(address)
                post = response.context.get('page_obj')
                if len(post) == 1:
                    self.assertEqual(post[0].text, self.post.text)
                    self.assertEqual(
                        post[0].author.username,
                        self.post.author.username
                    )

    def test_group_pages_correct_context(self):
        """Шаблон group_pages сформирован с правильным контекстом."""
        response = self.authorized_client.get(URL_GROUP_LIST)
        group = response.context['group']
        group_title_0 = group.title
        group_slug_0 = group.slug
        self.assertEqual(group_title_0, self.group.title)
        self.assertEqual(group_slug_0, self.group.slug)

    def test_post_another_group(self):
        """Пост не попал в другую группу"""
        response = self.authorized_client.get(URL_GROUP_LIST)
        post = response.context['page_obj']
        post_id_0 = post[0].group_id
        self.assertTrue(post_id_0, self.post.group.id)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.posts = [Post(
                text=f'Тестовый пост {i}',
                author=cls.user,
                group=cls.group
            )
            for i in range(14)]

        Post.objects.bulk_create(cls.posts)

    def setUp(self):
        self.guest_client = Client()
        self.urls = {
            URL_INDEX: 'posts/index.html',
            URL_GROUP_LIST: 'posts/group_list.html',
            PostPagesTests.URL_PROFILE: 'posts/profile.html',
        }
        self.urls_second_page = {
            URL_INDEX + "?page=2": 'posts/index.html',
            URL_GROUP_LIST + "?page=2": 'posts/group_list.html',
            PostPagesTests.URL_PROFILE + "?page=2": 'posts/profile.html',
        }

    def test_first_page_contains_ten_posts(self):
        for url in self.urls.keys():
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(
                    len(response.context.get('page_obj')), PAGE_COUNT
                )

    def test_second_page_contains_four_posts(self):
        for url in self.urls_second_page.keys():
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(
                    len(response.context.get('page_obj')),
                    len(self.posts) - PAGE_COUNT
                )
