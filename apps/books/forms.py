from django import forms


class BookForm(forms.Form):
    pages_read = forms.IntegerField(label="Pages read", max_value=10000, required=False)


class AddBookForm(forms.Form):
    title = forms.CharField(label="Title")
    author = forms.CharField(label="Author(s)")
    pages = forms.IntegerField(label="Pages")
    year = forms.IntegerField(label="Year")
    saga = forms.CharField(label="Saga", required=False)
    index = forms.CharField(label="Index in saga", required=False)


class SearchBookForm(forms.Form):
    search_for = forms.CharField(label="Search for")
