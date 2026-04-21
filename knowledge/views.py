from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import AnalyseTextForm
from .models import AnalyseText


@login_required
def analyse_text_list(request):
    analyse_texte = AnalyseText.objects.all().order_by("topic", "title")
    return render(
        request,
        "knowledge/analyse_text_list.html",
        {
            "analyse_texte": analyse_texte,
        },
    )


@login_required
def analyse_text_create(request):
    if request.method == "POST":
        form = AnalyseTextForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Der Analyse-Text wurde erstellt.")
            return redirect("knowledge:analyse_text_list")
    else:
        form = AnalyseTextForm()

    return render(
        request,
        "knowledge/analyse_text_form.html",
        {
            "form": form,
            "is_new": True,
            "analyse_text": None,
        },
    )


@login_required
def analyse_text_edit(request, pk):
    analyse_text = get_object_or_404(AnalyseText, pk=pk)

    if request.method == "POST":
        form = AnalyseTextForm(request.POST, instance=analyse_text)
        if form.is_valid():
            form.save()
            messages.success(request, "Der Analyse-Text wurde aktualisiert.")
            return redirect("knowledge:analyse_text_list")
    else:
        form = AnalyseTextForm(instance=analyse_text)

    return render(
        request,
        "knowledge/analyse_text_form.html",
        {
            "form": form,
            "is_new": False,
            "analyse_text": analyse_text,
        },
    )


@login_required
def analyse_text_delete(request, pk):
    analyse_text = get_object_or_404(AnalyseText, pk=pk)

    if request.method == "POST":
        analyse_text.delete()
        messages.success(request, "Der Analyse-Text wurde gelöscht.")
        return redirect("knowledge:analyse_text_list")

    return render(
        request,
        "knowledge/analyse_text_confirm_delete.html",
        {
            "analyse_text": analyse_text,
        },
    )