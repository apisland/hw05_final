from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.conf import settings


from .forms import PostForm, CommentForm
from .models import Follow, Post, Group, User


def numeration(queryset, request):
    paginator = Paginator(queryset, settings.CNT_POST)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj


def index(request):
    post_list = Post.objects.all().select_related('author', 'group')
    context = {
        'page_obj': numeration(post_list, request)
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.select_related('author')
    context = {
        'group': group,
        'page_obj': numeration(post_list, request),
    }
    return render(request, 'posts/group_list.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None,
                    files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', request.user)
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author == request.user:
        form = PostForm(request.POST,
                        files=request.FILES or None,
                        instance=post)
        if form.is_valid():
            form.save()
            return redirect('posts:post_detail', post.pk)
        else:
            form = PostForm(instance=post)
            context = {
                'form': form,
                'post': post,
                'is_edit': True
            }
        return render(request, 'posts/create_post.html', context)
    else:
        return redirect('posts:post_detail', post.pk)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    author_post = author.posts.select_related('group')
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            user=request.user,
            author=author).exists()
    else:
        following = False
    context = {
        'author': author,
        'following': following,
        'page_obj': numeration(author_post, request),
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post.objects.select_related('author', 'group'),
                             id=post_id)
    author = post.author
    form = CommentForm()
    comments = post.comments.all()
    context = {
        'author': author,
        'post': post,
        'form': form,
        'comments': comments,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post.pk)


@login_required
def follow_index(request):
    # информация о текущем пользователе доступна в переменной request.user
    post_list = Post.objects.filter(author__following__user=request.user)
    context = {
        'page_obj': numeration(post_list, request)
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    # Подписаться на автора
    author = get_object_or_404(User, username=username)
    follower = Follow.objects.filter(
        user=request.user, author=author).exists()
    if follower is True:
        return redirect('posts:profile', username=username)
    Follow.objects.create(user=request.user, author=author)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    # Дизлайк, отписка
    author = get_object_or_404(User, username=username)
    if author == request.user:
        return redirect('posts:profile', username=username)
    following = get_object_or_404(Follow, user=request.user, author=author)
    following.delete()
    return redirect('posts:profile', username=username)
