from django import forms


class ReadingUpdateForm(forms.Form):
    pages_read = forms.IntegerField(label="Pages read", max_value=10000, required=False)
    percent_read = forms.FloatField(label="Percent read", max_value=100, required=False)


class AddBookForm(forms.Form):
    title = forms.CharField(label="Title")
    author = forms.CharField(label="Author(s)")
    year = forms.IntegerField(label="Original Year")
    saga = forms.CharField(label="Saga", required=False)
    index = forms.CharField(label="Index in saga", required=False)


class AddEditionForm(forms.Form):
    isbn = forms.CharField(label="ISBN", max_length=16)
    title = forms.CharField(label="Title")
    year = forms.IntegerField(label="Year")
    pages = forms.IntegerField(label="Pages")


class SearchAuthorOrBookForm(forms.Form):
    CHOICES = [
        ('author', 'Author'),
        ('book', 'Book'),
    ]

    search_type = forms.ChoiceField(
        choices=CHOICES,
        widget=forms.RadioSelect,
        label="Search by",
    )

    query = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'mt-2 block w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:ring focus:ring-blue-200 focus:border-blue-500',
            'placeholder': 'Enter search query...'
        }),
        label="Search query",
    )
