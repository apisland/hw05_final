import shutil
import tempfile
from xml.etree.ElementTree import Comment

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings

from posts.models import Post, Group, Comment
from posts.forms import PostForm, CommentForm

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='test_name',
                                              email='test@mail.ru',
                                              password='test-pass')
        cls.group = Group.objects.create(
            title='Тестовое название группы',
            slug='rat'
        )
        cls.group_2 = Group.objects.create(
            title='Тестовое название группы 2',
            slug='bat'
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый текст',
            group=cls.group,
        )
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='Name')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_author = Client()
        self.authorized_author.force_login(self.author)

    def test_post_create_form(self):
        """При отправке валидной формы создается новая запись в БД
        и можно добавить картинку при создании"""
        posts_count = Post.objects.count()
        small_jpg = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.jpg',
            content=small_jpg,
            content_type='image/jpg'
        )
        form_data = {
            'text': 'Текст в форме',
            'group': self.group.id,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(response, reverse('posts:profile',
                             kwargs={'username': f'{self.user.username}'}))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Текст в форме',
                group=self.group.id,
                author=self.user,
                image='posts/small.jpg'
            ).exists()
        )

    def test_post_edit_with_post_id(self):
        """При валидной форме редактирования поста
        происходит изменение поста с id в БД"""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Новый текст в форме',
            'group': self.group_2.id,
        }
        url = reverse('posts:post_edit', kwargs={'post_id': self.post.id})
        self.authorized_author.post(
            url,
            data=form_data,
            follow=True
        )
        self.assertTrue(
            Post.objects.filter(
                text='Новый текст в форме',
                group=self.group_2.id,
                author=self.author,
                id=self.post.id,
            ).exists()
        )
        self.assertEqual(Post.objects.count(), posts_count)

    def test_guest_client_no_create(self):
        """При POST запросе гость не может создать новый пост"""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Текст поста гостя',
            'group': self.group.id,
        }
        self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count)

    def test_guest_client_no_edit(self):
        """При POST запросе гостя пост не будет отредактирован"""
        form_data = {
            'text': 'Редактированный текст поста гостя',
            'group': self.group,
        }
        post = self.post
        self.guest_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True,
        )
        same_post = Post.objects.get(id=self.post.id)
        self.assertEqual(same_post.text, post.text)
        self.assertEqual(same_post.group, post.group)
        self.assertEqual(same_post.author, post.author)
        self.assertEqual(same_post.pub_date, post.pub_date)

    def test_auth_user_no_author_no_edit(self):
        """Авторизованный юзер, но не автор, не может редактировать."""
        form_data = {
            'text': 'Новый текст в форме',
            'group': self.group,
        }
        post = self.post
        self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True,
        )
        same_post = Post.objects.get(id=self.post.id)
        self.assertEqual(same_post.text, post.text)
        self.assertEqual(same_post.group, post.group)
        self.assertEqual(same_post.author, post.author)
        self.assertEqual(same_post.pub_date, post.pub_date)

    def test_post_create_without_group(self):
        """Создание нового поста без указания группы"""
        posts_count = Post.objects.all().count()
        form_data = {
            'text': 'Тестовый текст в форме',
        }
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        last_post = Post.objects.latest('pub_date')
        self.assertEqual(posts_count + 1, Post.objects.all().count())
        self.assertEqual(last_post.text, form_data['text'])
        self.assertEqual(last_post.author, self.user)
        self.assertEqual(last_post.group, None)

    def test_change_text_other_fields_same(self):
        """При редактировании текста не меняются другие поля"""
        small_jpg = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.jpg',
            content=small_jpg,
            content_type='image/jpg'
        )

        form_data = {
            'text': 'Новый текст в форме',
            'group': self.group,
            'image': uploaded,
        }
        post = self.post
        url = reverse('posts:post_edit', kwargs={'post_id': self.post.id})
        self.authorized_author.post(
            url,
            data=form_data,
            follow=True
        )
        same_post = Post.objects.get(id=self.post.id)
        self.assertEqual(same_post.text, post.text)
        self.assertEqual(same_post.group, post.group)
        self.assertEqual(same_post.author, post.author)
        self.assertEqual(same_post.pub_date, post.pub_date)
        self.assertEqual(same_post.image, post.image)


class CommentTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='test_name',
                                              email='test@mail.ru',
                                              password='test-pass')
        cls.group = Group.objects.create(
            title='Тестовое название группы',
            slug='rat'
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый текст',
            group=cls.group,
        )
        cls.form = CommentForm()

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='Name')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_author = Client()
        self.authorized_author.force_login(self.author)

    def test_new_comment_by_auth_user(self):
        """Комментировать может только авторизованный пользователь"""
        comment_count = Comment.objects.count()
        form_data = {
            'text': 'Новый коммент',
        }
        self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True,
        )
        self.assertTrue(Comment.objects.filter(
            text='Новый коммент',
            author=self.user
        ).exists()
        )
        self.assertEqual(Comment.objects.count(), comment_count + 1)

    def test_guest_user_no_comment(self):
        """Гость не может комментировать посты"""
        comment_count = Comment.objects.count()
        form_data = {
            'text': 'Новый коммент',
        }
        self.guest_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True,
        )
        self.assertFalse(Comment.objects.filter(
            text='Новый коммент',
            author=self.user
        ).exists()
        )
        self.assertEqual(Comment.objects.count(), comment_count)
