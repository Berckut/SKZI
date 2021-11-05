#!/usr/bin/python
# -*- coding: utf8 -*-

import datetime,calendar



# Create your views here.

from django.http import HttpResponse
from django.shortcuts import render_to_response
from base.models import System, Office, User, Reason, NKIType, KDType, SignRight, NKI, ARM, KD, NKIOut, KDRecord, KDUpdate

import ConfigParser



################################################################################

# Индекс
def index(request):
    html=u''
    html+=u'<html>\n<head>\n	<title>Учёт СКЗИ</title>\n	<style type="text/css">\n		A {\n			text-decoration: none;\n			color: black;\n		}\n		A:hover {\n			color: blue;\n		}	</style>\n</head>\n<body>\n'
    html+=u'	<a href="/admin/">АРМ администратора</a><br><br>\n\n'

    html+=u'	<a href="/nkijournal/">Журнал регистрации носителей ключевой информации</a><br>\n'
    html+=u'	<a href="/kdjournal/">Журнал учёта ключевых документов</a><br>\n\n'
    html+=u'	<a href="/nkioutjournal/">Журнал выдачи носителей ключевой информации</a><br><br>\n'

    html+=u'	<a href="/reportoffices/">Отчёт по офисам</a><br>\n'
    html+=u'	<a href="/report_kddate/">Отчёт по ключам, срок действия которых истекает</a><br>\n'
    html+=u'	<a href="/report_signright/">Отчёт о пользователях, имеющих права электронной подписи, по офисам</a><br><br>\n'

    html+=u'	<a href="/audit_signright/">Аудит прав подписи по офисам</a><br><br>\n'

    html+=u'	<a href="/statyears/">Статистический отчёт</a><br>\n'
    html+=u'</body>\n</html>'

    return HttpResponse(html)



################################################################################
# Журнал регистрации НКИ

# Разбивка по годам
class NKI_Journal_Years:
    def __init__(self,year=u'',nkijournal=[]):
        self.year=u'%s' %year
        self.nkijournal=nkijournal



# Запись для Журнала регистрации НКИ
class NKI_Journal_Record:
    def __init__(self,nki="",nkitype="",source="",delete="",note=""):
        self.nki=nki
        self.nkitype=nkitype
        self.source=source
        self.delete=delete
        self.note=note



# Сформировать Журнал регистрации НКИ
def make_nki_journal(request):
    # Инициализируем номера дел по номенклатуре
    conffile=ConfigParser.ConfigParser()  # Переменная файла конфигурции
    conffile.readfp(open('nkinumber.ini','r')) # Чтение файла конфигурации

    nkijournalyearstemp={}
    for nki in NKI.objects.all().order_by("regnumber"):
        year=u'%s' %nki.date1.year
        month=u'%s' %nki.date1.month
        nomenclature_number=u"!Дело/"
        if conffile.has_option(str(year),str(month)):
            nomenclature_number=unicode(str(conffile.get(str(year),str(month))), 'cp1251')
        rnki=nomenclature_number+u'%s' %nki.regnumber
        rnki+=u'<br>'+u'%s' %nki.date1.strftime("%d.%m.%Y")
        #nomenclature_number="!Дело/"
        #if conffile.has_option(str(year),str(month)):
        #    nomenclature_number=str(conffile.get(str(year),str(month)))
        #rnki=nomenclature_number+str(nki.regnumber)+"<br>"+str(nki.date1.strftime("%d.%m.%Y"))
        rnkitype=u'%s' %nki.nkitype
        if nki.sernumber!=None or nki.sernumber!="":
            rnkitype+=u'<br>'+u'%s' %nki.sernumber
        rsource=u'%s' %nki.source
        rdelete=u''
        if nki.date2!="" and nki.date2!=None:
            rdelete=u'%s' %nki.date2.strftime("%d.%m.%Y")
            admin2=u'%s' %nki.admin2
            #if admin2!=u'':
            #    rdelete=rdelete+u' '+u'%s' %nki.admin2
            #else:
            #    rdelete=rdelete+u' Ряполов Д.Ю.'
            rdelete=rdelete+u' '+u'%s' %nki.admin2
            rdelete=rdelete+u'<br>'+u'%s' %nki.reason

        rnote=u'%s' %nki.note
        if nki.user!="" and nki.user!=None:
            t=u'Отв.: %s' %nki.user
            rnote=t+u"<br>"+rnote
        if nki.label!="" and nki.label!=None:
            rnote=nki.label+u"<br>"+rnote

        # Распределяем по годам
        if nkijournalyearstemp.has_key(year):
            nkijournalyearstemp[year].append(NKI_Journal_Record(rnki,rnkitype,rsource,rdelete,rnote))
        else:
            nkijournalyearstemp[year]=[]
            nkijournalyearstemp[year].append(NKI_Journal_Record(rnki,rnkitype,rsource,rdelete,rnote))

    # Формируем журналы
    nkijournalyears=[]
    keys=nkijournalyearstemp.keys()
    keys.sort()
    for y in keys:
        year=y
        nkijournal=nkijournalyearstemp[y]
        nkijournalyears.append(NKI_Journal_Years(year,nkijournal))

    #return render_to_response('make_kd_journal.html', {'kdjournal': kdjournal,})
    return render_to_response('make_nki_journal.html', {'nkijournalyears': nkijournalyears,})



################################################################################
# Журнал выдачи НКИ

# Разбивка по годам
class NKIOut_Journal_Years:
    def __init__(self,year=u'',nkioutjournal=[]):
        self.year=u'%s' %year
        self.nkioutjournal=nkioutjournal



# Запись для Журнала выдачи НКИ
class NKIOut_Journal_Record:
    def __init__(self,user="",nki="",date1="",date2="",admin2="",note=""):
        self.user=user
        self.nki=nki
        self.date1=date1
        self.date2=date2
        self.admin2=admin2
        self.note=note



# Сформировать Журнал выдачи НКИ
def make_nkiout_journal(request):
    # Инициализируем номера дел по номенклатуре
    conffile=ConfigParser.ConfigParser()  # Переменная файла конфигурции
    conffile.readfp(open('nkinumber.ini','r')) # Чтение файла конфигурации

    nkioutjournalyearstemp={}
    for nkiout in NKIOut.objects.all().order_by("date1"):
        user=u'%s' %nkiout.user
        user+=u' (%s)' %nkiout.office

        year=u'%s' %nkiout.nki.date1.year
        month=u'%s' %nkiout.nki.date1.month
        #nomenclature_number="!Дело/"
        #if conffile.has_option(str(year),str(month)):
        #    nomenclature_number=str(conffile.get(str(year),str(month)))
        nomenclature_number=u"!Дело/"
        if conffile.has_option(str(year),str(month)):
            nomenclature_number=unicode(str(conffile.get(str(year),str(month))), 'cp1251')
        t=nkiout.nki
        t_nkitype=u'%s' %t.nkitype
        t_regnumber=u'%s' %t.regnumber
        t_nomenclature_number=u'%s' %nomenclature_number
        nki=t_nkitype+u' '+t_nomenclature_number+t_regnumber

        date1=u'%s' %nkiout.date1.strftime("%d.%m.%Y")
        yeardate1=nkiout.date1.year

        date2=u''
        admin2=u''
        note=u''
        if nkiout.date2!="" and nkiout.date2!=None:
            date2=u'%s' %nkiout.date2.strftime("%d.%m.%Y")
            admin2=u'%s' %nkiout.admin2
            note=u'%s' %nkiout.reason

        # Распределяем по годам
        if nkioutjournalyearstemp.has_key(yeardate1):
            nkioutjournalyearstemp[yeardate1].append(NKIOut_Journal_Record(user,nki,date1,date2,admin2,note))
        else:
            nkioutjournalyearstemp[yeardate1]=[]
            nkioutjournalyearstemp[yeardate1].append(NKIOut_Journal_Record(user,nki,date1,date2,admin2,note))

    # Формируем журналы
    nkioutjournalyears=[]
    keys=nkioutjournalyearstemp.keys()
    keys.sort()
    for y in keys:
        year=y
        nkioutjournal=nkioutjournalyearstemp[y]
        nkioutjournalyears.append(NKIOut_Journal_Years(year,nkioutjournal))

    return render_to_response('make_nkiout_journal.html', {'nkioutjournalyears': nkioutjournalyears,})



################################################################################
# Журнал учёта КД

# Разбивка по годам
class KD_Journal_Years:
    def __init__(self,year=u'',kdjournal=[]):
        self.year=u'%s' %year
        self.kdjournal=kdjournal



# Запись для Журнала регистрации КД
class KD_Journal_Record:
    def __init__(self,number="",date1="",nki="",storage="",typekd="",cert="",user="",date2="",admin="",note="",backup=""):
        self.number=number
        self.date1=date1
        self.nki=nki
        self.storage=storage
        self.typekd=typekd
        self.cert=cert
        self.user=user
        self.date2=date2
        self.admin=admin
        self.note=note
        self.backup=backup



# Сформировать Журнал учёта КД
def make_kd_journal(request):
    # Инициализируем номера дел по номенклатуре
    conffile=ConfigParser.ConfigParser()  # Переменная файла конфигурции
    conffile.readfp(open('nkinumber.ini','r')) # Чтение файла конфигурации

    kdjournalyearstemp={}
    kdjournal=[]
    i=0
    for kd in KDRecord.objects.all().order_by("date1"):
        i+=1
        rnumber=u'%s' %i

        rdate1=u'%s' %kd.date1.strftime("%d.%m.%Y")
        year=u'%s' %kd.date1.year

        rnki=u''
        otvet=u''           # Ответственный
        if kd.nki!="" and kd.nki!=None:
            tnki=NKI.objects.get(id=kd.nki_id)
            nkitype=u'%s' %tnki.nkitype
            nkinumber=u'%s' %tnki.regnumber

            nkiyear=u'%s' %tnki.date1.year
            nkimonth=u'%s' %tnki.date1.month
            nomenclature_number=u"!Дело/"
            #if conffile.has_option(str(nkiyear),str(nkimonth)):
            #    nomenclature_number=str(conffile.get(str(nkiyear),str(nkimonth)))
            if conffile.has_option(str(nkiyear),str(nkimonth)):
                nomenclature_number=unicode(str(conffile.get(str(nkiyear),str(nkimonth))), 'cp1251')

            #nomenclature_number=u'%s' %nomenclature_number
            rnki=nkitype+u'<br>'+nomenclature_number+nkinumber
            if tnki.user!="" and tnki.user!=None:
                otvet=u'%s' %tnki.user
        if kd.arm!="" and kd.arm!=None:
            rnki=u'%s' %kd.arm

        rstorage=u'%s' %kd.storage

        tkd=KD.objects.get(id=kd.kd_id)
        rtypekd=u'%s' %tkd.kdtype
        rcert=u'%s S\\N<br>%s' %(tkd.date1.strftime("%d.%m.%Y"),tkd.sernumber)
        ruser=u'%s' %tkd.user

        rdate2=u''
        radmin2=u''
        if kd.date2!="" and kd.date2!=None:
            rdate2=u'%s' %kd.date2.strftime("%d.%m.%Y")
            radmin2=u'%s' %kd.admin2
            #if radmin2==u'':
            #    radmin2=u'Ряполов Д.Ю.'

        rnote=u'%s' %kd.note
        if rnote!=u'':
            rnote+=u'<br>'
        rnote+=tkd.label
        if otvet!=u'' and not(kd.backup):
            if rnote!=u'':
                rnote+=u'<br>'
            rnote+=u'Отв.: '+otvet

        # Ищем ссылку на первый экземпляр
        t1=rtypekd+rcert+ruser
        j=0
        firstekz=u''
        for record in kdjournal:
            t2=record.typekd+record.cert+record.user
            if t1==t2:
                if firstekz==u'':
                    firstekz=record.number
                j+=1

        # Ищем ссылку на обновлённый ключ
        update=u''
        if firstekz==u'':
            for updated in KDUpdate.objects.all().filter(kd_new=tkd.id):
                ukd=KD.objects.get(id=updated.kd_old.id)
                urtypekd=u'%s' %ukd.kdtype
                urcert=u'%s S\\N<br>%s' %(ukd.date1,ukd.sernumber)
                uruser=u'%s' %ukd.user
                u1=urtypekd+urcert+uruser
                for record in kdjournal:
                    u2=record.typekd+record.cert+record.user
                    if u1==u2:
                        if update==u'':
                            update=u'Замена п.'+record.number
                        else:
                            update=u' , п.'+record.number
                        break

        # Фиксируем обновление
        if update!=u'':
            rnote+=u'<br>'+update

        # Фиксируем номер экземпляра
        if j>0:
            if rnote!=u'':
                rnote+=u'<br>'
            if kd.backup:
                if firstekz!=u'':
                    rnote+=u'р/к п.'+firstekz
                else:
                    rnote+=u'р/к'
            else:
                ekz=str(j+1)
                ekz=u'%s' %ekz
                rnote+=u'Экз.№'+ekz+u' п.'+firstekz

        if kd.date2!="" and kd.date2!=None:
            if rnote!=u'':
                rnote+=u'<br>'
            rnote+=u'%s' %kd.reason

        rbackup=kd.backup

        kdjournal.append(KD_Journal_Record(rnumber,rdate1,rnki,rstorage,rtypekd,rcert,ruser,rdate2,radmin2,rnote,rbackup))

        # Распределяем по годам
        if kdjournalyearstemp.has_key(year):
            kdjournalyearstemp[year].append(KD_Journal_Record(rnumber,rdate1,rnki,rstorage,rtypekd,rcert,ruser,rdate2,radmin2,rnote,rbackup))
        else:
            kdjournalyearstemp[year]=[]
            kdjournalyearstemp[year].append(KD_Journal_Record(rnumber,rdate1,rnki,rstorage,rtypekd,rcert,ruser,rdate2,radmin2,rnote,rbackup))

    # Формируем журналы
    kdjournalyears=[]
    keys=kdjournalyearstemp.keys()
    keys.sort()
    for y in keys:
        year=y
        kdjournal=kdjournalyearstemp[y]
        kdjournalyears.append(KD_Journal_Years(year,kdjournal))

    #return render_to_response('make_kd_journal.html', {'kdjournal': kdjournal,})
    return render_to_response('make_kd_journal.html', {'kdjournalyears': kdjournalyears,})


################################################################################
# Отчёт по офисам

# КД
class Report_Offices_KD:
    def __init__(self,name=u'',kdid=0,kdrec=1,kdbackup=False):
        self.name=u'%s' %name
        self.kdid=kdid
        self.kdrec=kdrec
        self.kdbackup=kdbackup



# НКИ
class Report_Offices_NKI:
    def __init__(self,regnumber=u'',kds=[],nkiid=0,arm=False,nkioutid=0,nkioutdate1=u''):
        self.regnumber=u'%s' %regnumber
        self.kds=kds
        self.nkiid=nkiid
        self.arm=arm
        self.nkioutid=nkioutid
        self.nkioutdate1=nkioutdate1



# Пользователь
class Report_Offices_User:
    def __init__(self,name=u'',nkis=[],userid=0):
        self.name=u'%s' %name
        self.nkis=nkis
        self.userid=userid



# Офис
class Report_Offices_Office:
    def __init__(self,name=u'',users=[]):
        self.name=u'%s' %name
        self.users=users



# Сформировать Отчёт по офисам
def report_offices(request):
    # Инициализируем номера дел по номенклатуре
    conffile=ConfigParser.ConfigParser()  # Переменная файла конфигурции
    conffile.readfp(open('nkinumber.ini','r')) # Чтение файла конфигурации

    offices=[]

    # Перебираем все офисы
    for office in Office.objects.all().order_by("office"):
        users=[]

        # Перебираем всех пользователей
        for user in User.objects.all().order_by("name"):
            nkis=[]

            # Перебираем все выдачи очередного пользователя
            for nkiout in NKIOut.objects.filter(user=user.id,office=office.id,date2=None):
                kds=[]

                tnki=NKI.objects.get(id=nkiout.nki.id)
                nkitype=u'%s' %tnki.nkitype
                nkinumber=u'%s' %tnki.regnumber

                nkiyear=u'%s' %tnki.date1.year
                nkimonth=u'%s' %tnki.date1.month
                nomenclature_number=u"!Дело/"
                if conffile.has_option(str(nkiyear),str(nkimonth)):
                #    nomenclature_number=str(conffile.get(str(nkiyear),str(nkimonth)))
                    nomenclature_number=unicode(str(conffile.get(str(nkiyear),str(nkimonth))), 'cp1251')

                nki=nkitype+u' '+nomenclature_number+nkinumber
                nkioutid=nkiout.id
                nkioutdate1=u'%s' %nkiout.date1

                # Список ключей на носителе
                for kdrecord in KDRecord.objects.all().filter(nki=nkiout.nki.id,date2=None).order_by("nki"):
                    rec=u'%s' %kdrecord.kd
                    kd=kdrecord.kd

                    # Ищем номер экземпляра
                    kdrec=len(KDRecord.objects.all().filter(kd=kdrecord.kd,date1__lte=kdrecord.date1,id__lt=kdrecord.id))+1

                    if kdrecord.backup:
                        kds.append(Report_Offices_KD(rec,kdrecord.kd.id,kdrec,True))
                    else:
                        kds.append(Report_Offices_KD(rec,kdrecord.kd.id,kdrec))

                #if len(kds)>0:
                #    nkis.append(Report_Offices_NKI(nki,kds,nkiout.nki.id))
                nkis.append(Report_Offices_NKI(nki,kds,nkiout.nki.id,False,nkioutid,nkioutdate1))

            # Перебираем все АРМ очередного пользователя
            for arm in ARM.objects.filter(user=user.id):
                kds=[]

                flagoffice=False
                # Список ключей на АРМ
                for kdrecord in KDRecord.objects.all().filter(arm=arm.id,date2=None):
                    kd=kdrecord.kd

                    if kd.office==office:
                        flagoffice=True

                    rec=u'%s' %kdrecord.kd

                    # Ищем номер экземпляра
                    kdrec=len(KDRecord.objects.all().filter(kd=kdrecord.kd,date1__lte=kdrecord.date1,id__lt=kdrecord.id))+1

                    if kdrecord.backup:
                        kds.append(Report_Offices_KD(rec,kdrecord.kd.id,kdrec,True))
                    else:
                        kds.append(Report_Offices_KD(rec,kdrecord.kd.id,kdrec))

                if len(kds) and flagoffice>0:
                    nkis.append(Report_Offices_NKI(arm,kds,arm.id,True))

            if len(nkis)>0:
                users.append(Report_Offices_User(user,nkis,user.id))

        if len(users)>0:
            offices.append(Report_Offices_Office(office,users))

    # Не выданы
    nkis=[]
    for nki in NKI.objects.filter(date2=None).order_by("date1"):
        now=datetime.date.today()
        #if len(NKIOut.objects.filter(nki=nki.id))>0:
        #    if len(NKIOut.objects.filter(nki=nki.id,date2=None)):
        if len(NKIOut.objects.filter(nki=nki.id,date2=None)):
            continue

        kds=[]

        nkiyear=u'%s' %nki.date1.year
        nkimonth=u'%s' %nki.date1.month
        nomenclature_number=u"!Дело/"
        if conffile.has_option(str(nkiyear),str(nkimonth)):
        #    nomenclature_number=str(conffile.get(str(nkiyear),str(nkimonth)))
            nomenclature_number=unicode(str(conffile.get(str(nkiyear),str(nkimonth))), 'cp1251')

        nkitype=u'%s' %nki.nkitype
        nkinumber=u'%s' %nki.regnumber
        nkirec=nkitype+u' '+nomenclature_number+nkinumber

        # Список ключей на носителе
        for kdrecord in KDRecord.objects.all().filter(nki=nki.id,date2=None).order_by("date1"):
            rec=u'%s' %kdrecord.kd
            kd=kdrecord.kd

            # Ищем номер экземпляра
            kdrec=len(KDRecord.objects.all().filter(kd=kdrecord.kd,date1__lte=kdrecord.date1,id__lt=kdrecord.id))+1

            if kdrecord.backup:
                kds.append(Report_Offices_KD(rec,kdrecord.kd.id,kdrec,True))
            else:
                kds.append(Report_Offices_KD(rec,kdrecord.kd.id,kdrec))

        if len(kds)>0:
            nkis.append(Report_Offices_NKI(nkirec,kds,nki.id))

    if len(nkis)>0:
        offices.append(Report_Offices_Office(u'Не выданы',[Report_Offices_User(u'Не выданы',nkis),]))

    # Нет привязки к офису
    users=[]
    # Перебираем всех пользователей
    for user in User.objects.all().order_by("name"):
        nkis=[]

        # Перебираем все выдачи очередного пользователя
        for nkiout in NKIOut.objects.filter(user=user.id,office=None,date2=None):
            kds=[]

            tnki=NKI.objects.get(id=nkiout.nki.id)
            nkitype=u'%s' %tnki.nkitype
            nkinumber=u'%s' %tnki.regnumber

            nkiyear=u'%s' %tnki.date1.year
            nkimonth=u'%s' %tnki.date1.month
            nomenclature_number=u"!Дело/"
            if conffile.has_option(str(nkiyear),str(nkimonth)):
                nomenclature_number=str(conffile.get(str(nkiyear),str(nkimonth)))

            nki=nkitype+u' '+nomenclature_number+nkinumber
            nkioutid=nkiout.id
            nkioutdate1=u'%s' %nkiout.date1

            # Список ключей на носителе
            for kdrecord in KDRecord.objects.all().filter(nki=nkiout.nki.id,date2=None).order_by("nki"):
                rec=u'%s' %kdrecord.kd
                kd=kdrecord.kd

                # Ищем номер экземпляра
                kdrec=len(KDRecord.objects.all().filter(kd=kdrecord.kd,date1__lte=kdrecord.date1,id__lt=kdrecord.id))+1

                if kdrecord.backup:
                    kds.append(Report_Offices_KD(rec,kdrecord.kd.id,kdrec,True))
                else:
                    kds.append(Report_Offices_KD(rec,kdrecord.kd.id,kdrec))

            nkis.append(Report_Offices_NKI(nki,kds,nkiout.nki.id,False,nkioutid,nkioutdate1))

        if len(nkis)>0:
            users.append(Report_Offices_User(user,nkis,user.id))

    if len(users)>0:
        offices.append(Report_Offices_Office(u'Нет привязки к офису',users))


    # У экземпляров не зарегистриована ни носитель, ни АРМ
    kds=[]
    # Список ключей на носителе
    for kdrecord in KDRecord.objects.all().filter(nki=None,arm=None).order_by("date1"):
        rec=u'%s' %kdrecord.kd
        kd=kdrecord.kd

        # Ищем номер экземпляра
        kdrec=len(KDRecord.objects.all().filter(kd=kdrecord.kd,date1__lte=kdrecord.date1,id__lt=kdrecord.id))+1

        if kdrecord.backup:
            kds.append(Report_Offices_KD(rec,kdrecord.kd.id,kdrec,True))
        else:
            kds.append(Report_Offices_KD(rec,kdrecord.kd.id,kdrec))

    if len(kds)>0:
        offices.append(Report_Offices_Office(u'Отсутствует носитель и АРМ',[Report_Offices_User(u'Отсутствует носитель и АРМ',[Report_Offices_NKI(u'Отсутствует носитель и АРМ',kds),]),]))


    # Пустые
    nkis=[]
    for nki in NKI.objects.filter(date2=None).order_by("date1"):
        now=datetime.date.today()
        if len(KDRecord.objects.all().filter(nki=nki.id,date2=None))>0:
            continue
        if len(NKIOut.objects.filter(nki=nki.id,date2=None)):
            continue

        nkiyear=u'%s' %nki.date1.year
        nkimonth=u'%s' %nki.date1.month
        nomenclature_number=u"!Дело/"
        if conffile.has_option(str(nkiyear),str(nkimonth)):
            nomenclature_number=str(conffile.get(str(nkiyear),str(nkimonth)))

        nkitype=u'%s' %nki.nkitype
        nkinumber=u'%s' %nki.regnumber
        nkirec=nkitype+u' '+nomenclature_number+nkinumber

        nkis.append(Report_Offices_NKI(nkirec,[],nki.id))

    if len(nkis)>0:
        offices.append(Report_Offices_Office(u'Пустые',[Report_Offices_User(u'Пустые',nkis),]))



    return render_to_response('report_offices.html', {'offices': offices,})


################################################################################
# Отчёт по ключам, срок действия которых истекает

# Даты
class Report_KDDate_Date:
    def __init__(self,date2=u'',kds=[]):
        self.date2=u'%s' %date2
        self.kds=kds



# Ключи
class Report_KDDate_KD:
    def __init__(self,kdid=0,label=u'',kdtype=u'',sernumber=u'',user=u'',office=u'',system=u'',date1=u'',nkis=[],last=False,update=False):
        self.kdid=kdid
        self.label=u'%s' %label
        self.kdtype=u'%s' %kdtype
        self.sernumber=u'%s' %sernumber
        self.user=u'%s' %user
        self.office=u'%s' %office
        self.system=u'%s' %system
        self.date1=u'%s' %date1
        self.nkis=nkis
        self.last=last          # Действующий?
        self.update=update      # Обновлён?



# Носители
class Report_KDDate_NKI:
    def __init__(self,kdrecordid=0,name=u''):
        self.kdrecord=kdrecordid
        self.name=u'%s' %name



# Сформировать Отчёт по ключам, срок действия которых истекает
def report_kddate(request):
    # Инициализируем номера дел по номенклатуре
    conffile=ConfigParser.ConfigParser()  # Переменная файла конфигурции
    conffile.readfp(open('nkinumber.ini','r')) # Чтение файла конфигурации

    dates=[]

    # Перебираем все ключи
    now=datetime.date.today()
    deltadate1=datetime.datetime.now()-datetime.timedelta(days=31)
    deltadate2=datetime.datetime.now()+datetime.timedelta(days=500)
    for kd in KD.objects.all().filter(date2__gte=deltadate1,date2__lte=deltadate2).order_by("date2"):
        # Пропускаем отозванные
        if kd.revocation:
            continue

        kdid=kd.id
        label=u'%s' %kd.label
        kdtype=u'%s' %kd.kdtype
        sernumber=u'%s' %kd.sernumber
        user=u'%s' %kd.user
        office=u'%s' %kd.office
        system=u'%s' %kd.system
        date1=u'%s' %kd.date1

        # Действующий?
        last=False
        if kd.date2>datetime.date.today():
            last=True

        # Обновлён?
        update=False
        if len(KDUpdate.objects.all().filter(kd_old=kdid))>0:
            update=True
        #else:
        #    tt=1+"sdf"

        # Перебираем экземпляры
        nkis=[]
        for kdr in KDRecord.objects.all().filter(kd=kdid,date2=None):
            regnumberrec=u''
            officerec=u''
            userrec=u''
            # Экземпляр на носителе
            try:
                tnki=NKI.objects.get(id=kdr.nki.id)
                nkitype=u'%s' %tnki.nkitype
                nkinumber=u'%s' %tnki.regnumber

                nkiyear=u'%s' %tnki.date1.year
                nkimonth=u'%s' %tnki.date1.month
                nomenclature_number=u"!Дело/"
                if conffile.has_option(str(nkiyear),str(nkimonth)):
                #    nomenclature_number=str(conffile.get(str(nkiyear),str(nkimonth)))
                    nomenclature_number=unicode(str(conffile.get(str(nkiyear),str(nkimonth))), 'cp1251')

                regnumberrec=nkitype+u' '+nomenclature_number+nkinumber
                # Носитель выдан
                try:
                    nkiout=NKIOut.objects.all().filter(nki=kdr.nki.id,date2=None).order_by("-date1")[0]
                    officerec=u'%s' %nkiout.office
                    userrec=u'%s' %nkiout.user
                # Носитель не выдан
                except:
                    officerec=u''
                    userrec=u''
            # Экземпляр на АРМ
            except:
                regnumberrec=u'%s' %ARM.objects.get(id=kdr.arm.id)
            nkirec=u''
            if officerec!=u'':
                nkirec=regnumberrec+u': '+userrec+u' ('+officerec+u')'
            else:
                nkirec=regnumberrec
            nkis.append(Report_KDDate_NKI(kdr.id,nkirec))

        if len(dates)>0:
            if str(dates[-1].date2)==str(kd.date2):
                dates[-1].kds.append(Report_KDDate_KD(kdid,label,kdtype,sernumber,user,office,system,date1,nkis,last,update))
            else:
                dates.append(Report_KDDate_Date(kd.date2,[Report_KDDate_KD(kdid,label,kdtype,sernumber,user,office,system,date1,nkis,last,update),]))
        else:
            dates.append(Report_KDDate_Date(kd.date2,[Report_KDDate_KD(kdid,label,kdtype,sernumber,user,office,system,date1,nkis,last,update),]))

    return render_to_response('report_kddate.html', {'dates': dates,})



################################################################################
# Отчёт по правам электронной подписи

# Право подписи
class Report_SignRight_SR:
    def __init__(self,signrightdoc=u'',snid=0,note=u''):
        self.signrightdoc=u'%s' %signrightdoc
        self.srid=snid
        self.note=u'%s' %note



# Пользователь
class Report_SignRight_User:
    def __init__(self,name=u'',srs=[]):
        self.name=u'%s' %name
        self.srs=srs



# Система
class Report_SignRight_System:
    def __init__(self,name=u'',users=[]):
        self.name=u'%s' %name
        self.users=users



# Офис
class Report_SignRight_Office:
    def __init__(self,name=u'',systems=[]):
        self.name=u'%s' %name
        self.systems=systems



# Сформировать Отчёт по правам электронной подписи
def report_signright(request):
    now=datetime.date.today()
    offices=[]

    # Перебираем все офисы
    for office in Office.objects.all().order_by("office"):
        systems=[]

        # Перебираем все системы
        for system in System.objects.all().order_by("system"):
            users=[]

            # Формируем список проверяемых пользователей
            currentusers={}
            for sr in SignRight.objects.all().filter(date1__lte=now,date2__gte=now,system=system.id,office=office.id).order_by("docdate"):
                for user in sr.user.all():
                    t=u'%s' %user
                    currentusers[user.id]=t
            for sr in SignRight.objects.all().filter(date1__lte=now,date2=None,system=system.id,office=office.id).order_by("docdate"):
                for user in sr.user.all():
                    t=u'%s' %user
                    currentusers[user.id]=t

            # Перебираем всех пользователей
            for userid in currentusers.keys():
                srs=[]

                for sr in SignRight.objects.all().filter(user=userid,date1__lte=now,date2__gte=now,system=system.id,office=office.id).order_by("docdate"):
                        t1=u'%s' %sr.docname
                        t2=u'%s' %sr.note.replace('\n',"<br>")
                        srs.append(Report_SignRight_SR(t1,sr.id,t2))
                for sr in SignRight.objects.all().filter(user=userid,date1__lte=now,date2=None,system=system.id,office=office.id).order_by("docdate"):
                        t1=u'%s' %sr.docname
                        t2=u'%s' %sr.note.replace('\n',"<br>")
                        srs.append(Report_SignRight_SR(t1,sr.id,t2))

                if len(srs)>0:
                    users.append(Report_SignRight_User(currentusers[userid],srs))

            if len(users)>0:
                systems.append(Report_SignRight_System(system,users))

        if len(systems)>0:
            offices.append(Report_SignRight_Office(office,systems))

    return render_to_response('report_signright.html', {'offices': offices,})



################################################################################
# Аудит прав подписи по офисам

# Право подписи
class Audit_Signright_SN:
    def __init__(self,signrightdoc=u'',note=u''):
        self.signrightdoc=u'%s' %signrightdoc
        self.note=u'%s' %note



# КД
class Audit_Signright_KD:
    def __init__(self,name=u'',kdid=0,signright=True,signrightdoc=[],kdrec=1):
        self.name=u'%s' %name
        self.kdid=kdid
        self.signright=signright
        self.signrightdoc=signrightdoc
        self.kdrec=kdrec



# НКИ
class Audit_Signright_NKI:
    def __init__(self,regnumber=u'',kds=[],nkiid=0,arm=False,nkioutid=0,nkioutdate1=u''):
        self.regnumber=u'%s' %regnumber
        self.kds=kds
        self.nkiid=nkiid
        self.arm=arm
        self.nkioutid=nkioutid
        self.nkioutdate1=nkioutdate1



# Пользователь
class Audit_Signright_User:
    def __init__(self,name=u'',nkis=[],userid=0):
        self.name=u'%s' %name
        self.nkis=nkis
        self.userid=userid



# Офис
class Audit_Signright_Office:
    def __init__(self,name=u'',users=[]):
        self.name=u'%s' %name
        self.users=users



# Провести аудит прав подписи по офисам
def audit_signright(request):
    # Инициализируем номера дел по номенклатуре
    conffile=ConfigParser.ConfigParser()  # Переменная файла конфигурции
    conffile.readfp(open('nkinumber.ini','r')) # Чтение файла конфигурации

    offices=[]

    # Перебираем все офисы
    for office in Office.objects.all().order_by("office"):
        users=[]

        # Перебираем всех пользователей
        for user in User.objects.all().order_by("name"):
            nkis=[]

            # Перебираем все выдачи очередного пользователя
            for nkiout in NKIOut.objects.filter(user=user.id,office=office.id,date2=None):
                kds=[]

                tnki=NKI.objects.get(id=nkiout.nki.id)
                nkitype=u'%s' %tnki.nkitype
                nkinumber=u'%s' %tnki.regnumber

                nkiyear=u'%s' %tnki.date1.year
                nkimonth=u'%s' %tnki.date1.month
                nomenclature_number=u"!Дело/"
                if conffile.has_option(str(nkiyear),str(nkimonth)):
                #    nomenclature_number=str(conffile.get(str(nkiyear),str(nkimonth)))
                    nomenclature_number=unicode(str(conffile.get(str(nkiyear),str(nkimonth))), 'cp1251')

                nki=nkitype+u' '+nomenclature_number+nkinumber
                nkioutid=nkiout.id
                nkioutdate1=u'%s' %nkiout.date1

                # Список ключей на носителе
                for kdrecord in KDRecord.objects.all().filter(nki=nkiout.nki.id,date2=None).order_by("nki"):
                    rec=u'%s' %kdrecord.kd
                    kd=kdrecord.kd
                    signrigth=[]

                    # Ищем основание выдачи
                    now=datetime.date.today()
                    for sr in SignRight.objects.all().filter(user=user,date1__lte=now,date2__gte=now,system=kd.system,office=office).order_by("docdate"):
                        t1=u'%s' %sr.docname
                        t2=u'%s' %sr.note.replace('\n',"<br>")
                        signrigth.append(Audit_Signright_SN(t1,t2))
                    for sr in SignRight.objects.all().filter(user=user,date1__lte=now,date2=None,system=kd.system,office=office).order_by("docdate"):
                        t1=u'%s' %sr.docname
                        t2=u'%s' %sr.note.replace('\n',"<br>")
                        signrigth.append(Audit_Signright_SN(t1,t2))

                    # Ищем номер экземпляра
                    kdrec=len(KDRecord.objects.all().filter(kd=kdrecord.kd,date1__lte=kdrecord.date1,id__lt=kdrecord.id))+1

                    if len(signrigth)>0:
                        kds.append(Audit_Signright_KD(rec,kdrecord.kd.id,True,signrigth,kdrec))
                    else:
                        kds.append(Audit_Signright_KD(rec,kdrecord.kd.id,False,signrigth,kdrec))

                nkis.append(Audit_Signright_NKI(nki,kds,nkiout.nki.id,False,nkioutid,nkioutdate1))

            # Перебираем все АРМ очередного пользователя
            for arm in ARM.objects.filter(user=user.id):
                kds=[]

                flagoffice=False
                # Список ключей на АРМ
                for kdrecord in KDRecord.objects.all().filter(arm=arm.id,date2=None):
                    kd=kdrecord.kd

                    if kd.office==office:
                        flagoffice=True

                    rec=u'%s' %kdrecord.kd
                    signrigth=[]

                    # Ищем основание выдачи
                    now=datetime.date.today()
                    for sr in SignRight.objects.all().filter(user=user,date1__lte=now,date2__gte=now,system=kd.system,office=office).order_by("docdate"):
                        t1=u'%s' %sr.docname
                        t2=u'%s' %sr.note.replace('\n',"<br>")
                        signrigth.append(Audit_Signright_SN(t1,t2))
                    for sr in SignRight.objects.all().filter(user=user,date1__lte=now,date2=None,system=kd.system,office=office).order_by("docdate"):
                        t1=u'%s' %sr.docname
                        t2=u'%s' %sr.note.replace('\n',"<br>")
                        signrigth.append(Audit_Signright_SN(t1,t2))

                    # Ищем номер экземпляра
                    kdrec=len(KDRecord.objects.all().filter(kd=kdrecord.kd,date1__lte=kdrecord.date1,id__lt=kdrecord.id))+1

                    if len(signrigth):
                        kds.append(Audit_Signright_KD(rec,kdrecord.kd.id,True,signrigth,kdrec))
                    else:
                        kds.append(Audit_Signright_KD(rec,kdrecord.kd.id,False,signrigth,kdrec))

                if len(kds) and flagoffice>0:
                    nkis.append(Audit_Signright_NKI(arm,kds,arm.id,True))

            if len(nkis)>0:
                users.append(Audit_Signright_User(user,nkis,user.id))

        if len(users)>0:
            offices.append(Audit_Signright_Office(office,users))

    # Не выданы
    nkis=[]
    for nki in NKI.objects.filter(date2=None).order_by("date1"):
        now=datetime.date.today()
        if len(NKIOut.objects.filter(nki=nki.id))>0:
            if len(NKIOut.objects.filter(nki=nki.id,date2=None)):
                continue

        kds=[]

        nkiyear=u'%s' %nki.date1.year
        nkimonth=u'%s' %nki.date1.month
        nomenclature_number=u"!Дело/"
        if conffile.has_option(str(nkiyear),str(nkimonth)):
            #nomenclature_number=str(conffile.get(str(nkiyear),str(nkimonth)))
            nomenclature_number=unicode(str(conffile.get(str(nkiyear),str(nkimonth))), 'cp1251')

        nkitype=u'%s' %nki.nkitype
        nkinumber=u'%s' %nki.regnumber
        nkirec=nkitype+u' '+nomenclature_number+nkinumber

        # Список ключей на носителе
        for kdrecord in KDRecord.objects.all().filter(nki=nki.id,date2=None).order_by("date1"):
            rec=u'%s' %kdrecord.kd
            kd=kdrecord.kd

            # Ищем номер экземпляра
            kdrec=len(KDRecord.objects.all().filter(kd=kdrecord.kd,date1__lte=kdrecord.date1,id__lt=kdrecord.id))+1

            kds.append(Audit_Signright_KD(rec,kdrecord.kd.id,True,[],kdrec))

        if len(kds)>0:
            nkis.append(Audit_Signright_NKI(nkirec,kds,nki.id))

    if len(nkis)>0:
        offices.append(Audit_Signright_Office(u'Не выданы',[Audit_Signright_User(u'Не выданы',nkis),]))

    # Нет привязки к офису
    users=[]
    # Перебираем всех пользователей
    for user in User.objects.all().order_by("name"):
        nkis=[]

        # Перебираем все выдачи очередного пользователя
        for nkiout in NKIOut.objects.filter(user=user.id,office=None,date2=None):
            kds=[]

            tnki=NKI.objects.get(id=nkiout.nki.id)
            nkitype=u'%s' %tnki.nkitype
            nkinumber=u'%s' %tnki.regnumber

            nkiyear=u'%s' %tnki.date1.year
            nkimonth=u'%s' %tnki.date1.month
            nomenclature_number=u"!Дело/"
            if conffile.has_option(str(nkiyear),str(nkimonth)):
                #nomenclature_number=str(conffile.get(str(nkiyear),str(nkimonth)))
                nomenclature_number=unicode(str(conffile.get(str(nkiyear),str(nkimonth))), 'cp1251')

            nki=nkitype+u' '+nomenclature_number+nkinumber
            nkioutid=nkiout.id
            nkioutdate1=u'%s' %nkiout.date1

            # Список ключей на носителе
            for kdrecord in KDRecord.objects.all().filter(nki=nkiout.nki.id,date2=None).order_by("nki"):
                rec=u'%s' %kdrecord.kd
                kd=kdrecord.kd
                signrigth=[]

                # Ищем основание выдачи
                now=datetime.date.today()
                for sr in SignRight.objects.all().filter(user=user,date1__lte=now,date2__gte=now,system=kd.system,office=office).order_by("docdate"):
                    t1=u'%s' %sr.docname
                    t2=u'%s' %sr.note.replace('\n',"<br>")
                    signrigth.append(Audit_Signright_SN(t1,t2))
                for sr in SignRight.objects.all().filter(user=user,date1__lte=now,date2=None,system=kd.system,office=office).order_by("docdate"):
                    t1=u'%s' %sr.docname
                    t2=u'%s' %sr.note.replace('\n',"<br>")
                    signrigth.append(Audit_Signright_SN(t1,t2))

                # Ищем номер экземпляра
                kdrec=len(KDRecord.objects.all().filter(kd=kdrecord.kd,date1__lte=kdrecord.date1,id__lt=kdrecord.id))+1

                if len(signrigth)>0:
                    kds.append(Audit_Signright_KD(rec,kdrecord.kd.id,True,signrigth,kdrec))
                else:
                    kds.append(Audit_Signright_KD(rec,kdrecord.kd.id,False,signrigth,kdrec))

            nkis.append(Audit_Signright_NKI(nki,kds,nkiout.nki.id,False,nkioutid,nkioutdate1))

        if len(nkis)>0:
            users.append(Audit_Signright_User(user,nkis,user.id))

    if len(users)>0:
        offices.append(Audit_Signright_Office(u'Нет привязки к офису',users))


    return render_to_response('audit_signright.html', {'offices': offices,})



################################################################################
# Статистический отчёт

# Отчёт за год
class Stat_Years:
    def __init__(self,year=2012,indicator=[]):
        self.year=year
        self.indicator=indicator



# Показатель
class Stat_Indicator:
    def __init__(self,name=u''):
        self.name=u'%s' %name
        self.months=[]
        self.common=0



# Сформировать статичтический отчёт по годам
def statyears(request):
    # Инициализируем номера дел по номенклатуре
    conffile=ConfigParser.ConfigParser()  # Переменная файла конфигурции
    conffile.readfp(open('conf.ini','r')) # Чтение файла конфигурации

    statyears=[]

    # Текущая дата
    now=datetime.date.today()
    now_year=int(now.year)
    now_month=int(now.month)

    # Определяем рабочий интервал
    yearmin=9999
    t=NKI.objects.order_by("date1")[0].date1.year
    if yearmin>t:
        yearmin=t
    t=KDRecord.objects.order_by("date1")[0].date1.year
    if yearmin>t:
        yearmin=t
    t=NKIOut.objects.order_by("date1")[0].date1.year
    if yearmin>t:
        yearmin=t

    yearmax=0000
    t=NKI.objects.order_by("-date1")[0].date1.year
    if yearmax<t:
        yearmax=t
    t=KDRecord.objects.order_by("-date1")[0].date1.year
    if yearmax<t:
        yearmax=t
    t=NKIOut.objects.order_by("-date1")[0].date1.year
    if yearmax<t:
        yearmax=t
    if yearmax>now_year:
        yearmax=now_year

    # Перебираем года
    current_year=yearmin
    while current_year<=yearmax:
        indicators={}

        # Инициализируем индикаторы
        indicators[1]=Stat_Indicator(u'Количество работников, использовавших электронную подпись')     # 1
        indicators[2]=Stat_Indicator(u'Зарегистрировано новых ключей электронной подписи')             # 2
        indicators[3]=Stat_Indicator(u'Записано экземпляров ключевых документов')                      # 3
        indicators[4]=Stat_Indicator(u'Зарегистрировано новых носителей ключевой информации')          # 4
        indicators[5]=Stat_Indicator(u'Выдано носителей ключевой информации')                            # 5
        indicators[6]=Stat_Indicator(u'Уничтожено/списано носителей по причине поломки')               # 6
        indicators[7]=Stat_Indicator(u'Отозвана регистрация ключей электронной подписи')               # 7
        indicators[8]=Stat_Indicator(u'Истёк срок действия ключей электронной подписи')                # 8
        indicators[9]=Stat_Indicator(u'Скомпрометировано ключей электронной подписи')                  # 9

        # Перебираем месяца
        current_month=1
        while current_month<=12:
            # Пропускаем будущее
            if current_year==now_year:
                if current_month>now_month:
                    for indicator in indicators:
                        indicators[indicator].months.append(u'---')

                    current_month+=1
                    continue

            # Перебираем события

            # Количество работников, использовавших электронную подпись    # 1
            t={}
            for nkiout in NKIOut.objects.all().filter(date1__lt=(datetime.date(current_year,current_month,1)+datetime.timedelta(days=calendar.monthrange(current_year,current_month)[1])),date2__gte=datetime.date(current_year,current_month,1)):
                t[nkiout.user.id]=0
            for nkiout in NKIOut.objects.all().filter(date1__lt=(datetime.date(current_year,current_month,1)+datetime.timedelta(days=calendar.monthrange(current_year,current_month)[1])),date2=None):
                t[nkiout.user.id]=0
            for kdrecord in KDRecord.objects.all().filter(nki=None,date1__lt=(datetime.date(current_year,current_month,1)+datetime.timedelta(days=calendar.monthrange(current_year,current_month)[1])),date2__gte=datetime.date(current_year,current_month,1)):
                try:
                    t[kdrecord.arm.user.id]=0
                except:
                    pass
            for kdrecord in KDRecord.objects.all().filter(nki=None,date1__lt=(datetime.date(current_year,current_month,1)+datetime.timedelta(days=calendar.monthrange(current_year,current_month)[1])),date2=None):
                try:
                    t[kdrecord.arm.user.id]=0
                except:
                    pass
            indicators[1].months.append(len(t))

            # Зарегистрировано новых ключей электронной подписи            # 2
            indicators[2].months.append(len(KD.objects.all().filter(date1__year=current_year,date1__month=current_month)))

            # Записано экземпляров ключевых документов                     # 3
            indicators[3].months.append(len(KDRecord.objects.all().filter(date1__year=current_year,date1__month=current_month)))

            # Зарегистрировано носителей ключевой информации               # 4
            indicators[4].months.append(len(NKI.objects.all().filter(date1__year=current_year,date1__month=current_month)))

            # Выдано носителей ключей информации                           # 5
            indicators[5].months.append(len(NKIOut.objects.all().filter(date1__year=current_year,date1__month=current_month)))

            # Уничтожено/списано носителей по причине поломки              # 6
            key=int(conffile.get("stat","damagenki"))
            indicators[6].months.append(len(NKI.objects.all().filter(reason=key,date2__year=current_year,date2__month=current_month)))

            # Отозвана регистрация ключей электронной подписи              # 7
            indicators[7].months.append(len(KD.objects.all().filter(compromise=False,revocation=True,date2__year=current_year,date2__month=current_month)))

            # Истёк срок действия ключей электронной подписи               # 8
            indicators[8].months.append(len(KD.objects.all().filter(compromise=False,revocation=False,date2__year=current_year,date2__month=current_month)))

            # Скомпрометировано ключей электронной подписи                 # 9
            indicators[9].months.append(len(KD.objects.all().filter(compromise=True,date2__year=current_year,date2__month=current_month)))

            current_month+=1

        # Статистика по годам
        # Количество работников, использовавших электронную подпись    # 1
        t={}
        for nkiout in NKIOut.objects.all().filter(date1__lt=datetime.date(current_year+1,1,1),date2__gte=datetime.date(current_year,1,1)):
            t[nkiout.user.id]=0
        for nkiout in NKIOut.objects.all().filter(date1__lt=datetime.date(current_year+1,1,1),date2=None):
            t[nkiout.user.id]=0
        for kdrecord in KDRecord.objects.all().filter(nki=None,date1__lt=datetime.date(current_year+1,1,1),date2__gte=datetime.date(current_year,1,1)):
            try:
                t[kdrecord.arm.user.id]=0
            except:
                pass
        for kdrecord in KDRecord.objects.all().filter(nki=None,date1__lt=datetime.date(current_year+1,1,1),date2=None):
            try:
                t[kdrecord.arm.user.id]=0
            except:
                pass
        indicators[1].common=len(t)

        # Зарегистрировано новых ключей электронной подписи            # 2
        indicators[2].common=len(KD.objects.all().filter(date1__year=current_year))

        # Записано экземпляров ключевых документов                     # 3
        indicators[3].common=len(KDRecord.objects.all().filter(date1__year=current_year))

        # Зарегистрировано носителей ключевой информации               # 4
        indicators[4].common=len(NKI.objects.all().filter(date1__year=current_year))

        # Выдано носителей ключей информации                           # 5
        indicators[5].common=len(NKIOut.objects.all().filter(date1__year=current_year))

        # Уничтожено/списано носителей по причине поломки              # 6
        key=int(conffile.get("stat","damagenki"))
        indicators[6].common=len(NKI.objects.all().filter(reason=key,date2__year=current_year))

        # Отозвана регистрация ключей электронной подписи              # 7
        indicators[7].common=len(KD.objects.all().filter(compromise=False,revocation=True,date2__year=current_year))

        # Истёк срок действия ключей электронной подписи               # 8
        indicators[8].common=len(KD.objects.all().filter(compromise=False,revocation=False,date2__year=current_year))

        # Скомпрометировано ключей электронной подписи                 # 9
        indicators[9].common=len(KD.objects.all().filter(compromise=True,date2__year=current_year))

        # Формируем годовой отчёт
        keys=indicators.keys()
        keys.sort()
        t=[]
        for k in keys:
            t.append(indicators[k])

        statyears.append(Stat_Years(current_year,t))
        current_year+=1

    return render_to_response('statyears.html', {'statyears': statyears,})











