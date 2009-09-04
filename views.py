import random
from shortcuts import render
from productions.models import Production, Part
from plays.models import Play
from places.models import Place
from places.models import Place
from people.models import Person
from news.models import Article

def home(request):
    try:
        latest_news = Article.objects.latest()
    except:
        latest_news = {}

    try:
        latest = Production.objects.all().order_by('-id')[0]
    except:
        latest = {}

    return render(request, 'home.html', {
        'latest_production': latest,
        'latest_news': latest_news,
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

