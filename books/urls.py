from django.urls import path
from . import views

urlpatterns = [
    # ---------- Public ----------
    path("", views.home, name="home"),
    path("books/", views.book_list, name="book_list"),
    path("book/<str:slug>/", views.book_detail, name="book_detail"),
    path("book/<str:slug>/read/", views.book_read, name="book_read"),

    path("category/<str:slug>/", views.category_page, name="category_page"),
    path("tag/<str:slug>/", views.tag_page, name="tag_page"),

    # ---------- Accounts ----------
    path("accounts/signup/", views.signup, name="signup"),

    # ---------- User Dashboard ----------
    path("me/", views.me_dashboard, name="me_dashboard"),
    path("me/books/new/", views.me_book_create, name="me_book_create"),
    path("me/books/<int:pk>/edit/", views.me_book_update, name="me_book_update"),
    path("me/books/<int:pk>/delete/", views.me_book_delete, name="me_book_delete"),

    # ---------- Admin Dashboard (staff only) ----------
    path("dashboard/", views.admin_dashboard_home, name="admin_dashboard_home"),
    path("dashboard/books/", views.admin_dashboard_books, name="admin_dashboard_books"),
    path("dashboard/categories/", views.admin_dashboard_categories, name="admin_dashboard_categories"),
]
