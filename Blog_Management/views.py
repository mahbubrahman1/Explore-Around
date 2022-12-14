from django.shortcuts import render, HttpResponseRedirect
from django.views.generic import CreateView, ListView, TemplateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
import uuid
from django.urls import reverse, reverse_lazy
from django.contrib.auth.decorators import login_required

from .models import Blog, Like
from .forms import CommentForm


# write blog or create blog 
class WriteBlog(LoginRequiredMixin, CreateView):
    model = Blog
    template_name = 'Blog_Management/write_blog.html'
    fields = ('blog_title', 'blog_content', 'blog_image', )

    def form_valid(self, form):
        blog_obj = form.save(commit=False)
        blog_obj.author = self.request.user
        title = blog_obj.blog_title

        # add 4 unique id in url
        blog_obj.slug = title.replace(" ", "-") + "-" + str(uuid.uuid4())
        blog_obj.save()
        return HttpResponseRedirect(reverse('index'))


# all blog
class AllBlog(ListView):
    context_object_name = 'blogs'
    model = Blog
    template_name = 'Blog_Management/all_blog.html'


# show full blog
@login_required
def full_blog(request, slug):
    blog = Blog.objects.get(slug=slug)
    comment_form = CommentForm()

    already_liked = Like.objects.filter(blog=blog, user=request.user)
    if already_liked:
        liked = True
    else:
        liked = False

    if request.method == 'POST':
        comment_form = CommentForm(request.POST)

        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.user = request.user
            comment.blog = blog
            comment.save()
            return HttpResponseRedirect(reverse('Blog_Management_App:full_blog', kwargs={'slug':slug}))

    return render(request, 'Blog_Management/full_blog.html', {'blog': blog, 'comment_form': comment_form, 'liked': liked})


# like 
@login_required
def liked(request, pk):
    blog = Blog.objects.get(pk=pk)
    user = request.user

    already_liked = Like.objects.filter(blog=blog, user=user)
    
    if not already_liked:
        liked_post = Like(blog=blog, user=user)
        liked_post.save()

    return HttpResponseRedirect(reverse('Blog_Management_App:full_blog', kwargs={'slug':blog.slug}))


# unlike 
@login_required
def unliked(request, pk):
    blog = Blog.objects.get(pk=pk)
    user = request.user
    already_liked = Like.objects.filter(blog=blog, user=user)
    already_liked.delete()

    return HttpResponseRedirect(reverse('Blog_Management_App:full_blog', kwargs={'slug':blog.slug}))


# user blog or my blog
class MyBlogs(LoginRequiredMixin, TemplateView):
    template_name = 'Blog_Management/my_blogs.html'


# edit user blog
class EditBlog(LoginRequiredMixin, UpdateView):
    model = Blog
    fields = ('blog_title', 'blog_content', 'blog_image')
    template_name = 'Blog_Management/edit_blog.html'

    def get_success_url(self, **kwargs):
        return reverse_lazy('Blog_Management_App:full_blog', kwargs={'slug':self.object.slug})