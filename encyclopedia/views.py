from django import forms
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect
from markdown2 import Markdown
import random


from . import util

class NewEntryForm(forms.Form):
    title = forms.CharField(label="Title", required=True)
    content = forms.CharField(label="Content", widget=forms.Textarea, required=True)

    def clean_title(self):
        title = self.cleaned_data.get('title')
        
        #check if already exists
        entries = util.list_entries()
        if title in entries:
            raise ValidationError('Entry already exists.')

        return title
    
class EditEntryForm(forms.Form):
    content = forms.CharField(label="Content", widget=forms.Textarea, required=True)
    
def index(request):
    entries = util.list_entries()

    if request.method == "POST":
        # search pages
        query = request.POST['q']
        if query != '':
            entries = [entry for entry in entries if query in entry]
            if len(entries) == 1:
                # if only one is found, render that page
                return redirect('entry', title=entries[0])

            # if more than one are found, render the page with the results
            # of the query
            return render(request, "encyclopedia/search.html", {
                "entries": entries,
                "query": query
            })

    return render(request, "encyclopedia/index.html", {
        "entries": entries
    })

def entry(request, title):
    markdown_text = util.get_entry(title)
    html_text = None

    if markdown_text:
        markdowner = Markdown()
        html_text = markdowner.convert(markdown_text)
        
    return render(request, "encyclopedia/entry.html", {
        "entry": html_text,
        "title": title
    })

def create(request):
    if request.method == "POST":
        form = NewEntryForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            
            util.save_entry(title, form.cleaned_data["content"])
            return redirect('entry', title=title)
        else: 
            return render(request, 'encyclopedia/upsert.html', {
                "title": "Create new entry",
                "form": form
            })

    return render(request, 'encyclopedia/upsert.html', {
        "title": "Create new entry",
        "form": NewEntryForm()
    })

def edit(request, title):
    if request.method == "POST":
        form = EditEntryForm(request.POST)
        if form.is_valid():
            util.save_entry(title, form.cleaned_data["content"])
            return redirect('entry', title=title)
        else: 
            return render(request, 'encyclopedia/upsert.html', {
                "title": "Edit " + title,
                "form": form
            })

    return render(request, 'encyclopedia/upsert.html', {
        "title": "Edit " + title,
        "form": EditEntryForm({
            "content": util.get_entry(title)
        })
})

def random_entry(request):
    entries = util.list_entries()
    return redirect('entry', title=random.choice(entries))