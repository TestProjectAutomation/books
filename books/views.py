from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.db.models import Q, Count
from django.http import HttpResponseForbidden

from .models import Book, Category, Tag
from .forms import BookForm, CategoryForm


# ---------- Helpers ----------
def is_staff(user):
    return user.is_authenticated and user.is_staff


def _can_edit(user, book: Book) -> bool:
    return user.is_staff or book.uploaded_by_id == user.id


# ---------- Public Views ----------
def home(request):
    latest = Book.objects.filter(is_published=True).select_related("category").prefetch_related("tags").order_by("-created_at")[:9]
    categories = Category.objects.annotate(total=Count("book")).order_by("-total")[:8]
    tags = Tag.objects.annotate(total=Count("book")).order_by("-total")[:12]
    return render(request, "books/home.html", {"latest": latest, "categories": categories, "tags": tags})


def book_list(request):
    q = request.GET.get("q", "").strip()
    cat = request.GET.get("cat", "").strip()
    tag = request.GET.get("tag", "").strip()

    books = Book.objects.filter(is_published=True).select_related("category").prefetch_related("tags")

    if q:
        books = books.filter(Q(title__icontains=q) | Q(author_name__icontains=q) | Q(description__icontains=q))
    if cat:
        books = books.filter(category__slug=cat)
    if tag:
        books = books.filter(tags__slug=tag)

    books = books.order_by("-created_at").distinct()

    categories = Category.objects.annotate(total=Count("book")).order_by("-total")
    tags = Tag.objects.annotate(total=Count("book")).order_by("-total")[:30]

    return render(request, "books/book_list.html", {
        "books": books, "q": q, "categories": categories, "tags": tags, "selected_cat": cat, "selected_tag": tag
    })


def book_detail(request, slug):
    book = get_object_or_404(Book, slug=slug, is_published=True)
    return render(request, "books/book_detail.html", {"book": book})


def book_read(request, slug):
    book = get_object_or_404(Book, slug=slug, is_published=True)
    return render(request, "books/book_read_pdfjs.html", {"book": book})


def category_page(request, slug):
    category = get_object_or_404(Category, slug=slug)
    books = Book.objects.filter(is_published=True, category=category).order_by("-created_at")
    return render(request, "books/category_page.html", {"category": category, "books": books})


def tag_page(request, slug):
    tag = get_object_or_404(Tag, slug=slug)
    books = Book.objects.filter(is_published=True, tags=tag).order_by("-created_at")
    return render(request, "books/tag_page.html", {"tag": tag, "books": books})


def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("me_dashboard")
    else:
        form = UserCreationForm()
    return render(request, "accounts/signup.html", {"form": form})


# ---------- User Dashboard (me) ----------
@login_required
def me_dashboard(request):
    my_books = Book.objects.filter(uploaded_by=request.user).select_related("category").order_by("-created_at")
    total = my_books.count()
    published = my_books.filter(is_published=True).count()
    drafts = total - published
    return render(request, "me/dashboard_home.html", {"books": my_books[:8], "total": total, "published": published, "drafts": drafts})


@login_required
def me_book_create(request):
    if request.method == "POST":
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            form.save(owner=request.user)
            return redirect("me_dashboard")
    else:
        form = BookForm()
    return render(request, "me/book_form.html", {"form": form, "mode": "create"})


@login_required
def me_book_update(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if not _can_edit(request.user, book):
        return HttpResponseForbidden("غير مسموح")

    if request.method == "POST":
        form = BookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            form.save(owner=request.user)
            return redirect("me_dashboard")
    else:
        form = BookForm(instance=book)
    return render(request, "me/book_form.html", {"form": form, "mode": "update", "book": book})


@login_required
def me_book_delete(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if not _can_edit(request.user, book):
        return HttpResponseForbidden("غير مسموح")
    if request.method == "POST":
        book.delete()
        return redirect("me_dashboard")
    return render(request, "me/book_delete.html", {"book": book})


# ---------- Admin Dashboard ----------
@login_required
@user_passes_test(is_staff)
def admin_dashboard_home(request):
    total_books = Book.objects.count()
    published = Book.objects.filter(is_published=True).count()
    drafts = total_books - published
    total_users = Book.objects.values("uploaded_by").distinct().count()
    top_categories = Category.objects.annotate(total=Count("book")).order_by("-total")[:8]
    return render(request, "admin_dash/home.html", {
        "total_books": total_books, "published": published, "drafts": drafts,
        "total_users": total_users, "top_categories": top_categories
    })


@login_required
@user_passes_test(is_staff)
def admin_dashboard_books(request):
    q = request.GET.get("q","").strip()
    books = Book.objects.all().select_related("category","uploaded_by").order_by("-created_at")
    if q:
        books = books.filter(Q(title__icontains=q) | Q(uploaded_by__username__icontains=q))
    return render(request, "admin_dash/books_list.html", {"books": books, "q": q})


@login_required
@user_passes_test(is_staff)
def admin_dashboard_categories(request):
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("admin_dashboard_categories")
    else:
        form = CategoryForm()
    categories = Category.objects.annotate(total=Count("book")).order_by("-total","name")
    return render(request, "admin_dash/categories.html", {"categories": categories, "form": form})
