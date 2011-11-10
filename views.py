import random
from django.contrib.comments.models import Comment
from django.contrib.auth.models import User
from shortcuts import render
from productions.models import Production, Part
from plays.models import Play
from places.models import Place
from places.models import Place
from people.models import Person
from news.models import Article
from photos.models import Photo

def home(request):
    matthew = User.objects.get(id=1)

    try:
        latest_news = Article.objects.visible().latest()
    except:
        latest_news = {}

    try:
        latest = Production.objects.all().order_by('-id')[0]
    except:
        latest = {}

    try:
        latest_comment = Comment.objects.exclude(user=matthew).order_by('-id')[0]
    except:
        latest_comment = {}

    random_photo = Photo.objects.exclude(id__gte=149, id__lte=159).filter(content_type=22).order_by('?')[0]
    if random.randint(1, 10) == 1: random_photo = None

    return render(request, 'home.html', {
        'latest_production': latest,
        'latest_observation': latest_comment,
        'latest_news': latest_news,
        'productions': Production.objects.count(),
        'places': Place.objects.count(),
        'plays': Play.objects.count(),
        'people': Person.objects.count(),
        'parts': Part.objects.count(),
        'random_photo': random_photo,
        'home': True,
    })

def static_colophon(request):
	return render(request, 'colophon.html')
def static_about(request):
	return render(request, 'about.html')
def static_help(request):
	return render(request, 'help.html')
def static_contact(request):
	return render(request, 'contact.html')

def static_moocards(request):
    cards_v = [
        "1881_Patience.jpg",
        "1887-12-26_JackandtheBeanstalk-croppedS.jpg",
        "Affiche_Electra.jpg",
        "AnnaDickinson.jpg",
        "ChesterMysteryPlay_300dpi-cropped.jpg",
        "Goethes_Faust.jpg",
        "WarnePantomine1890-cropped.jpg",
        "Henry_VI_pt_2_quarto2-cropped.jpg",
        "Image-Loves_Labours_Lost_(Title_Page)-cropped.jpg",
        "Image0801.jpg",
        "Image1360-cropped.jpg",
        "MND_title_page-cropped.jpg",
        "Muse_BM_C309.jpg",
        "PaulCezanne-cropped.jpg",
        "Settle-Morocco-cropped.png",
        "Hamlet_First_Quarto_first_page_(1603).jpg",
        "The_Swan_cropped.png",
    ]
    cards_h = [
        "193784853sjWJDF_fs-cropped-0.jpg",
        "Epidaurus_Theater.jpg",
        "Manchester_Opera_House_2-cropped.jpg",
        "New_York_State_Theater_by_David_Shankbone-cropped.jpg",
        "Performance_in_the_Bolshoi_Theatre-cropped.jpg",
        "Shakespeare-memorial-old.jpg",
        "TragicComicMasksHadriansVillamosaic.jpg",
        "Wicked_World_-_Illustrated_London_News,_Feb_8_1873-cropped.png",
    ]
    random.shuffle(cards_v)
    random.shuffle(cards_h)

    base = '/static/i/moo/'

    def v():
        out = '<td rowspan=2>'
        out += '<img width=80 height=200 src="%s%s">' % (base, cards_v.pop())
        if len(cards_v):
            out += '<img width=80 height=200 src="%s%s">' % (base, cards_v.pop())
        out += '</td>'
        return out

    def h():
        return '<td><img width=200 height=80 src="%s%s"></td>' % (base, cards_h.pop())

    rows = (
        v() + h() + h() + v(),
              h() + v()      ,
        h() + v()       + v(),
        v()       + v()      ,
              h()       + h(),
    )

    unused = (
        v() + h() + v(),
              h(),
    )

    return render(request, 'moocards.html', {
        'rows': rows,
        'unused': unused,
    })

