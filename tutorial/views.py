from unicodedata import category
from django.shortcuts import get_object_or_404, render

from tutorial.models import *
from vt_site.models import Terms_pages, site_detail


def tutorial(request):
    category = tutorial_category.objects.all().order_by('id')
    tutorials = Tutorial.objects.all()
    trend_tutorials = Tutorial.objects.filter(status = 'trending').order_by('id')[0:8]
    terms_pages = Terms_pages.objects.all()
    siteDetail = site_detail.objects.all()
    context = {
        'tutorials': tutorials,
        'category' : category,
        'trend_tutorials' : trend_tutorials,
        'terms_pages' : terms_pages,
        'siteDetail' : siteDetail,
    }
    return render(request,"tutorial_pages/tutorials.html",context)

def tutorial_content(request, slug, lesson_slug):
    tutorial = get_object_or_404(Tutorial, slug=slug)
    chapters = tutorial.tutorial_chapter_set.all()
    
    if lesson_slug == 'None':
        first_lesson = chapters[0].tutorials_lesson_set.first() if chapters else None
        if first_lesson:
            lesson_slug = first_lesson.slug

    lesson = get_object_or_404(tutorials_Lesson, slug=lesson_slug)
    
    previous_lesson = tutorials_Lesson.objects.filter(chapter__tutorial=tutorial, id__lt=lesson.id).last()
    next_lesson = tutorials_Lesson.objects.filter(chapter__tutorial=tutorial, id__gt=lesson.id).first()
    siteDetail = site_detail.objects.all()
    terms_pages = Terms_pages.objects.all()
    context = {
        'tutorial': tutorial,
        'chapters': chapters,
        'lesson': lesson,
        'slug' : slug,
        'previous_lesson': previous_lesson,
        'next_lesson': next_lesson,
        'terms_pages' : terms_pages,
        'siteDetail' : siteDetail,
    }
    return render(request,"tutorial_pages/tutorial_content.html",context)
