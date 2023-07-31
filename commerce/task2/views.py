from django.shortcuts import render
from task2.forms import ReviewForm
from django.views.generic.edit import FormView
from django.http import HttpResponse
# Create your views here.



class ReviewEmailView(FormView):
    template_name = 'review.html'
    form_class = ReviewForm

    def form_valid(self, form):
        form.send_email()
        msg = "Thanks for the review!"
        return HttpResponse(msg)