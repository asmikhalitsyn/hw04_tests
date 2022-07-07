from django.test import TestCase
from django.urls import reverse

SLUG_OF_GROUP = 'test-slug'
USERNAME = 'TEST'
POST_ID = 1
NAME_OF_URL_OF_INDEX = 'index'
NAME_OF_URL_OF_POSTS_OF_GROUP = 'group_list'
NAME_URL_TO_CREATE_POST = 'post_create'
NAME_URL_OF_PROFILE = 'profile'


class PostRoutesTests(TestCase):

    def test_correct_routes(self):
        self.NAME_OF_URL_OF_DETAIL_POST = 'post_detail'
        self.NAME_OF_URL_TO_EDIT_POST = 'post_edit'
        cases = [
            [NAME_OF_URL_OF_INDEX, '/', None],
            [NAME_OF_URL_OF_POSTS_OF_GROUP, f'/group/{SLUG_OF_GROUP}/', [SLUG_OF_GROUP]],
            [NAME_URL_OF_PROFILE, f'/profile/{USERNAME}/', [USERNAME]],
            [self.NAME_OF_URL_OF_DETAIL_POST, f'/posts/{POST_ID}/', [POST_ID]],
            [self.NAME_OF_URL_TO_EDIT_POST, f'/posts/{POST_ID}/edit/', [POST_ID]],
            [NAME_URL_TO_CREATE_POST, '/create/', None]
        ]
        for name_of_route, route, args in cases:
            with self.subTest(name_of_route=name_of_route):
                self.assertEqual(reverse(f'posts:{name_of_route}', args=args), route)
