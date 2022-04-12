from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post
from ..models import Comment


User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Мы будем использовать post detail view для создания'
                 'экземпляра формы'
                 'и обработаем ее так, чтобы ее упростить. Измените файл'
                 'models.py,'
                 'добавьте import для модели Comment и CommentForm форму,',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        post = PostModelTest.post
        value = post.text
        self.assertEqual(value, str(post))

    def test_post_models_help_text(self):
        """Тест help_texts в модели Post"""
        post = PostModelTest.post
        values = {
            'text': 'Текст нового поста',
            'group': 'Группа, к которой относится пост',
            'image': 'Изображение',
        }
        for key, value in values.items():
            with self.subTest(value=value):
                help_texts = post._meta.get_field(key).help_text
                self.assertEqual(help_texts, value)

    def test_post_model_verbose(self):
        """Тест полей verbose в модели Post"""
        post = PostModelTest.post
        values = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',
            'image': 'Картинка',
        }
        for key, value in values.items():
            with self.subTest(value=value):
                verbose = post._meta.get_field(key).verbose_name
                self.assertEqual(verbose, value)


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )

    def test_group_models_have_correct_object_names(self):
        """Проверяем, что у моделей группы корректно работает __str__."""
        group = GroupModelTest.group
        value = group.title
        self.assertEqual(value, str(group))

    def test_group_model_title_verbose(self):
        """Тест поля title verbose"""
        group = GroupModelTest.group
        values = {
            'title': 'Название группы',
            'slug': 'Идентификатор группы',
            'description': 'Описание группы',
        }
        for key, value in values.items():
            with self.subTest(value=value):
                verbose = group._meta.get_field(key).verbose_name
                self.assertEqual(verbose, value)


class CommentModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Текст нового комментария',
        )

    def test_comment_models_have_correct_object_names(self):
        """Проверяем, что у моделей комментариев корректно работает __str__."""
        comment = CommentModelTest.comment
        value = comment.text
        self.assertEqual(value, str(comment))

    def test_comment_model_verbose_names(self):
        """Тест поля verbose Comment модели"""
        comment = CommentModelTest.comment
        values = {
            'post': 'Форма комментария',
            'author': 'Автор комментария',
            'text': 'Текст комментария',
            'created': 'Дата комментария',
        }
        for key, value in values.items():
            with self.subTest(value=value):
                verbose = comment._meta.get_field(key).verbose_name
                self.assertEqual(verbose, value)
