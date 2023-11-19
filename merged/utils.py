import django
from django.contrib.contenttypes.models import ContentType
from django_comments.models import Comment

from plays.models import Play
from productions.models import Production, Visit, Part, Place as ProductionPlace, Production_Companies, ProductionCompany
from photos.models import Photo
from places.models import Place, Name
from people.models import Person
from merged.models import Redirect
from common.models import Alert


def update_attr(main, alt, attrs):
    for attr in attrs:
        if alt.__dict__[attr] and not main.__dict__[attr]:
            main.__dict__[attr] = alt.__dict__[attr]
            main.save()
        elif alt.__dict__[attr] and main.__dict__[attr] and alt.__dict__[attr] != main.__dict__[attr]:
            print("%s: 1: %s, 2: %s" % (attr, main.__dict__[attr], alt.__dict__[attr]))


def redirect(redirect_obj, main, alt):
    if redirect_obj:
        # Reassign in case reverse-merged
        redirect_obj.old_object_id = alt.id
        redirect_obj.new_object = main
        redirect_obj.approved = True
        redirect_obj.save()
    else:
        Redirect.objects.create(old_object_id=alt.id, new_object=main, approved=True)


def merge_thing(main, alt, redirect_obj=None):
    cls = type(main)
    if cls is Play:
        merge_play(main, alt, redirect_obj)
    elif cls is ProductionCompany:
        merge_company(main, alt, redirect_obj)
    elif cls is Place:
        merge_place(main, alt, redirect_obj)
    elif cls is Person:
        merge_person(main, alt, redirect_obj)
    elif cls is Production:
        merge_production(main, alt, redirect_obj)


def merge_play(main, alt, redirect_obj):
    ctype = ContentType.objects.get_for_model(alt)
    Alert.objects.filter(content_type=ctype, object_id=alt.id).update(object_id=main.id)
    Production.objects.filter(play=alt).update(play=main)
    update_attr(main, alt, ('url', 'wikipedia', 'description'))
    for author in alt.authors.all():
        main.authors.add(author)
    Redirect.objects.filter(content_type=ctype, new_object_id=alt.id).update(new_object_id=main.id)
    redirect(redirect_obj, main, alt)
    alt.delete()


def merge_company(main, alt, redirect_obj):
    Production_Companies.objects.filter(productioncompany=alt).update(productioncompany=main)
    update_attr(main, alt, ('description',))
    ctype = ContentType.objects.get_for_model(alt)
    Redirect.objects.filter(content_type=ctype, new_object_id=alt.id).update(new_object_id=main.id)
    redirect(redirect_obj, main, alt)
    alt.delete()


def merge_place(main, alt, redirect_obj):
    ctype = ContentType.objects.get_for_model(alt)
    Alert.objects.filter(content_type=ctype, object_id=alt.id).update(object_id=main.id)
    Photo.objects.filter(content_type=ctype, object_id=alt.id).update(object_id=main.id)
    ProductionPlace.objects.filter(place=alt).update(place=main)
    Place.objects.filter(parent=alt).update(parent=main)
    Name.objects.filter(place=alt).update(place=main)
    update_attr(main, alt, ('parent_id', 'description', 'latitude', 'longitude', 'address', 'town', 'country_id', 'postcode', 'telephone', 'type', 'size', 'opening_date', 'closing_date', 'url', 'wikipedia'))
    Redirect.objects.filter(content_type=ctype, new_object_id=alt.id).update(new_object_id=main.id)
    redirect(redirect_obj, main, alt)
    alt.delete()


def merge_person(main, alt, redirect_obj):
    ctype = ContentType.objects.get_for_model(alt)
    Alert.objects.filter(content_type=ctype, object_id=alt.id).update(object_id=main.id)
    Photo.objects.filter(content_type=ctype, object_id=alt.id).update(object_id=main.id)
    Part.objects.filter(person=alt).update(person=main)
    update_attr(main, alt, ('bio', 'dob', 'died', 'imdb', 'musicbrainz', 'web', 'wikipedia', 'openplaques'))
    for play in alt.plays.all():
        main.plays.add(play)
    Redirect.objects.filter(content_type=ctype, new_object_id=alt.id).update(new_object_id=main.id)
    redirect(redirect_obj, main, alt)
    alt.deleted = True
    alt.save()


def merge_production(main, alt, redirect_obj):
    ctype = ContentType.objects.get_for_model(alt)

    Photo.objects.filter(content_type=ctype, object_id=alt.id).update(object_id=main.id)

    for visit in Visit.objects.filter(production=alt):
        visit.production = main
        try:
            visit.save()
        except django.db.utils.IntegrityError:
            visit.delete()

    Comment.objects.filter(content_type=ctype, object_pk=alt.id).update(object_pk=main.id)

    for company in Production_Companies.objects.filter(production=alt):
        if Production_Companies.objects.filter(production=main, productioncompany=company.productioncompany).exists():
            company.delete()
        else:
            company.production = main
            company.save()

    if alt.description != main.description:
        main.description += "\n\n" + alt.description
    if alt.source:
        main.source += "\n\n" + alt.source

    # ProductionPlace.objects.filter(production=alt).update(production=main)
    for place in ProductionPlace.objects.filter(production=alt):
        if ProductionPlace.objects.filter(place=place.place, production=main, start_date=place.start_date or '', end_date=place.end_date or '', press_date=place.press_date):
            print("Going to delete %s" % place)
            place.delete()
        else:
            place.production = main
            print("Going to save %s" % place)
            place.save()

    # main_place = main.place_set.all()[0]
    # alt_place = alt.place_set.all()[0]
    # Part.objects.filter(production=main, start_date='', end_date='').update(start_date=main_place.start_date, end_date=main_place.end_date)
    # Part.objects.filter(production=alt, start_date='', end_date='').update(production=main, start_date=alt_place.start_date, end_date=alt_place.end_date)
    for part in Part.objects.filter(production=alt):
        match = {
            'person': part.person,
            'production': main,
            'cast': part.cast,
            'credited_as': part.credited_as,
            'order': part.order,
            'start_date': part.start_date or '',
            'end_date': part.end_date or '',
        }
        if Part.objects.filter(role=part.role, **match):  # Exact match
            print("Going to delete %s" % part)
            part.delete()
        elif not part.role and Part.objects.filter(**match):  # alt part does not have a role, main does
            print("Going to delete %s" % part)
            part.delete()
        elif Part.objects.filter(role='', **match):  # main part does not have a role, alt does
            ppp = Part.objects.filter(role='', **match).first()
            ppp.role = part.role
            ppp.save()
            print("Going to move %s to main" % part)
            part.delete()
        else:  # No match
            part.production = main
            print("Going to save %s" % part)
            part.save()

    Redirect.objects.filter(content_type=ctype, new_object_id=alt.id).update(new_object_id=main.id)
    redirect(redirect_obj, main, alt)
    alt.delete()
    main.save()
