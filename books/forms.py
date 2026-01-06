from django import forms
from .models import Book, Category, Tag

class BookForm(forms.ModelForm):
    tags_text = forms.CharField(
        required=False,
        help_text="اكتب وسوم مفصولة بفاصلة مثل: بايثون, تعلم, برمجة",
        widget=forms.TextInput(attrs={"placeholder": "مثال: بايثون, Django, ويب"})
    )

    class Meta:
        model = Book
        fields = ["title","author_name","description","cover","pdf_file","content","category","is_published"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "content": forms.Textarea(attrs={"rows": 10}),
        }

    def save(self, commit=True, owner=None):
        book = super().save(commit=False)
        if owner is not None and not book.pk:
            book.uploaded_by = owner
        if commit:
            book.save()
            self.save_m2m()
            self._save_tags(book)
        return book

    def _save_tags(self, book):
        raw = (self.cleaned_data.get("tags_text") or "").strip()
        if not raw:
            return
        names = [x.strip() for x in raw.split(",") if x.strip()]
        for name in names:
            tag, _ = Tag.objects.get_or_create(name=name)
            book.tags.add(tag)


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "اسم التصنيف"}),
        }