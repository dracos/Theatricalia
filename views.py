from shortcuts import render
from productions.models import Production, Part
from plays.models import Play
from places.models import Place
from places.models import Place
from people.models import Person

def home(request):
	return render(request, 'home.html', {
        'productions': Production.objects.count(),
        'places': Place.objects.count(),
        'plays': Play.objects.count(),
        'people': Person.objects.count(),
        'parts': Part.objects.count(),
    })

def static_colophon(request):
	return render(request, 'colophon.html')
def static_about(request):
	return render(request, 'about.html')
def static_help(request):
	return render(request, 'help.html')
def static_contact(request):
	return render(request, 'contact.html')
