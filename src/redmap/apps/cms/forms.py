from datetime import datetime
from django import forms
from django.forms import ModelForm
from redmap.apps.cms.models import Page, HomepageContent, CopyBlock
from tagging.models import Tag
from ckeditor.widgets import CKEditorWidget
from zinnia.managers import DRAFT, HIDDEN, PUBLISHED


class BookForm(ModelForm):

    slug = forms.SlugField()

    def save(self, commit=True):
        book = super(BookForm, self).save(commit=False)

        book.status = PUBLISHED
        if not book.content:
            book.content = ""
        book.save()

        return book

    class Meta:
        model = Page
        fields = ['title', 'tag_list', 'slug']


class AddPageForm(ModelForm):

    tag_list = forms.MultipleChoiceField(required=False, label="Tags")
    title = forms.CharField(widget=forms.TextInput(attrs={'class': 'span4'}))
    slug = forms.SlugField(widget=forms.TextInput(attrs={'class': 'span4'}))

    def __init__(self, *args, **kwargs):
        self.book = kwargs.pop('book', None)
        super(AddPageForm, self).__init__(*args, **kwargs)

        self.fields['tag_list'].choices = Tag.objects.all().values_list('name', 'name')

        if not self.data:
            self.fields['parent'].initial = self.book.get_root()
        self.fields['parent'].queryset = self.book.get_descendants(include_self=True)

    def clean_parent(self):
        parent = self.cleaned_data.get('parent')
        if not parent:
            raise forms.ValidationError('Please select a parent page')
        return parent

    def save(self, commit=True):
        instance = super(AddPageForm, self).save(commit=False)

        if not instance.created:
            instance.created = datetime.now()

        if len(instance.tag_list) > 0:
            instance.tag_list = ','.join(eval(instance.tag_list)) + ','  # Make sure app can save tags
        else:
            instance.tag_list = ''

        if commit:
            instance.save()

        return instance

    class Meta:
        model = Page
        exclude = ['created']
        widgets = {
            'content': CKEditorWidget(),
        }


class UpdateHomepageForm(ModelForm):

    teaser = forms.CharField(widget=forms.widgets.Textarea(attrs={'class': 'span6',}))

    class Meta:
        model = HomepageContent
        widgets = {
        }


class CopyBlockForm(ModelForm):

    class Meta:
        model = CopyBlock
