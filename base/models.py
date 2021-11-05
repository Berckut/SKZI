#!/usr/bin/python
# -*- coding: utf8 -*-

from django.db import models
from django.contrib import messages
import datetime

# Create your models here.


# Система
class System(models.Model):
    system=models.CharField(max_length=100,verbose_name=u'Система')


    def __unicode__(self):
        return u'%s' % self.system


    class Meta:
        verbose_name = u'систему'
        verbose_name_plural = 'Список систем'
        ordering = ['system']




# Офис
class Office(models.Model):
    office=models.CharField(max_length=100,verbose_name=u'Офис')


    def __unicode__(self):
        return u'%s' % self.office


    class Meta:
        verbose_name = u'офис'
        verbose_name_plural = u'Список офисов'
        ordering = ['office']



# Субъект
class User(models.Model):
    name=models.CharField(max_length=100,verbose_name=u'Работник/СПБ')


    def __unicode__(self):
        return u'%s' % self.name


    class Meta:
        verbose_name = u'субъекта'
        verbose_name_plural = u'Список субъектов'
        ordering = ['name']



# Причина
class Reason(models.Model):
    reason=models.CharField(max_length=255,verbose_name=u'Причина')


    def __unicode__(self):
        return u'%s' % self.reason


    class Meta:
        verbose_name = u'причину'
        verbose_name_plural = u'Список причин'
        ordering = ['reason']



# Тип носителя ключевой информации
class NKIType(models.Model):
    nkitype=models.CharField(max_length=255,verbose_name=u'Тип носителя ключевой информации')


    def __unicode__(self):
        return u'%s' % self.nkitype


    class Meta:
        verbose_name = u'тип НКИ'
        verbose_name_plural = u'Типы носителей'
        ordering = ['nkitype']



# Тип ключевого документа
class KDType(models.Model):
    kdtype=models.CharField(max_length=255,verbose_name=u'Тип ключевого документа')


    def __unicode__(self):
        return u'%s' % self.kdtype


    class Meta:
        verbose_name = u'тип КД'
        verbose_name_plural = u'Типы ключевых документов'
        ordering = ['kdtype']



# Право подписи
class SignRight(models.Model):
    date1=models.DateField(verbose_name=u'Дата наделения правом подписи')
    date2=models.DateField(blank=True,null=True,verbose_name=u'Дата прекращения права подписи')
    user=models.ManyToManyField(User,verbose_name=u'Кому предоставлено право подписи')
    system=models.ManyToManyField(System,verbose_name=u'В каких системах предоставлено право подписи')
    office=models.ForeignKey(Office,verbose_name=u'К какому офису относится')
    docname=models.CharField(max_length=255,default=u'Приказ № от г.: ',verbose_name=u'Название документа')
    docdate=models.DateField(verbose_name=u'Дата документа')
    docnumber=models.CharField(max_length=255,verbose_name=u'Номер документа')
    note=models.TextField(blank=True,verbose_name=u'Примечание')


    def __unicode__(self):
        return u'от %s №%s: %s' % (self.docdate,self.docnumber,self.docname)


    class Meta:
        verbose_name = u'право подписи'
        verbose_name_plural = u'Права подписи'
        ordering = ['-docdate','office']



# Носитель ключевой информации
class NKI(models.Model):
    date1=models.DateField(default=datetime.date.today,verbose_name=u'Дата регистрации')
    #regnumber=models.CharField(max_length=255,verbose_name=u'Рег. номер')
    regnumber=models.IntegerField(blank=True,unique=True,help_text=u'Номер присвоится автоматически, если поле оставить пустым',verbose_name=u'Рег. номер')
    admin1=models.CharField(max_length=255,blank=True,verbose_name=u'Зарегистрировал администратор')
    nkitype=models.ForeignKey(NKIType,verbose_name=u'Тип НКИ')
    sernumber=models.CharField(max_length=255,blank=True,verbose_name=u'Серийный номер НКИ')
    source=models.CharField(max_length=255,blank=True,verbose_name=u'От кого получен, дата и номер сопр. письма')
    date2=models.DateField(blank=True,null=True,help_text=u'При указании даты экземпляры стираются автоматически',verbose_name=u'Дата уничтожения')
    reason=models.ForeignKey(Reason,blank=True,null=True,verbose_name=u'Причина уничтожения')
    admin2=models.CharField(max_length=255,blank=True,verbose_name=u'Уничтожил администратор')
    system=models.ManyToManyField(System,blank=True,null=True,editable=False,verbose_name=u'Для каких систем предназначен')
    user=models.ForeignKey(User,blank=True,null=True,verbose_name=u'Ответственный')
    label=models.CharField(max_length=255,blank=True,verbose_name=u'Метка')
    note=models.TextField(blank=True,verbose_name=u'Примечание')


    def __unicode__(self):
        return u'№%s %s: %s' % (self.regnumber,self.nkitype,self.label)


    class Meta:
        verbose_name = u'носитель'
        verbose_name_plural = u'Журнал регистрации носителей'
        ordering = ['-regnumber']


    def save(self, *args, **kwargs):
        # Автоматическое заполнение номера
        if not(self.regnumber):
            try:
                rn=NKI.objects.order_by("-regnumber")[0].regnumber
                self.regnumber=rn+1
            except IndexError:
                self.regnumber=1

        # Автоматическое стирание экземпляров при указании даты уничтожения носителя
        if self.date2:
            for kdr in KDRecord.objects.all().filter(nki=self.id,date2=None):
                kdr.date2=self.date2
                kdr.reason=self.reason
                kdr.admin2=self.admin2
                kdr.save()

        # Автоматический возврат носителя, если он был выдан
        if self.date2:
            for nkiout in NKIOut.objects.all().filter(nki=self.id,date2=None):
                nkiout.date2=self.date2
                nkiout.reason=self.reason
                nkiout.admin2=self.admin2
                nkiout.save()

        super(NKI, self).save()



# Автоматизированное рабочее место / сервер / локальное хранилище
class ARM(models.Model):
    name=models.CharField(max_length=255,default=u'АРМ ',verbose_name=u'АРМ')
    user=models.ForeignKey(User,blank=True,null=True,verbose_name=u'Владелец')


    def __unicode__(self):
        return u'%s' % self.name


    class Meta:
        verbose_name = u'АРМ'
        verbose_name_plural = u'АРМ'
        ordering = ['name']



# Ключевой документ
class KD(models.Model):
    #datetime.timedelta()
    date1=models.DateField(default=datetime.date.today,verbose_name=u'Действует с')
    date2=models.DateField(blank=True,null=True,default=datetime.datetime.now()+datetime.timedelta(days=365),verbose_name=u'Действует по')
    kdtype=models.ForeignKey(KDType,blank=True,verbose_name=u'Тип КД')
    sernumber=models.CharField(max_length=100,blank=True,verbose_name=u'Сер. номер')
    user=models.ForeignKey(User,blank=True,null=True,verbose_name=u'Владелец')
    admin1=models.CharField(max_length=255,blank=True,verbose_name=u'Зарегистрировал администратор')
    admin2=models.CharField(max_length=255,blank=True,verbose_name=u'Отозвал/отменил администратор')
    office=models.ForeignKey(Office,blank=True,null=True,verbose_name=u'Офис')
    system=models.ForeignKey(System,blank=True,null=True,verbose_name=u'Система')
    label=models.CharField(max_length=255,blank=True,verbose_name=u'Метка')
    note=models.TextField(blank=True,verbose_name=u'Примечание')
    revocation=models.BooleanField(blank=False,verbose_name=u'Отозван')
    compromise=models.BooleanField(blank=False,verbose_name=u'Скомпрометирован')



    def __unicode__(self):
        return u'%s' % (self.label)


    class Meta:
        verbose_name = u'ключевой документ'
        verbose_name_plural = u'Журнал регистрации ключевых документов'
        ordering = ['-date1','user']



# Выдача носителя ключевой информации
class NKIOut(models.Model):
    date1=models.DateField(default=datetime.date.today,verbose_name=u'Дата выдачи')
    nki=models.ForeignKey(NKI,limit_choices_to={'date2__isnull':True},help_text=u'Носитель не должен быть уничтожен',verbose_name=u'Носитель ключевой информации')
    admin1=models.CharField(max_length=255,blank=True,verbose_name=u'Выдал администратор')
    user=models.ForeignKey(User,verbose_name=u'Получил пользователь')
    date2=models.DateField(blank=True,null=True,verbose_name=u'Дата возврата')
    admin2=models.CharField(max_length=255,blank=True,verbose_name=u'Принял администратор')
    reason=models.ForeignKey(Reason,blank=True,null=True,verbose_name=u'Причина возврата')
    office=models.ForeignKey(Office,blank=True,null=True,verbose_name=u'В какой офис выдан')
    note=models.TextField(blank=True,verbose_name=u'Примечание')


    class Meta:
        verbose_name = u'выдачу'
        verbose_name_plural = u'Журнал выдачи носителей'
        ordering = ['-date1','-nki']



# Экземпляр ключевого документа (Журнал записи ключевых документов)
class KDRecord(models.Model):
    date1=models.DateField(default=datetime.date.today,verbose_name=u'Дата записи')
    nki=models.ForeignKey(NKI,blank=True,null=True,limit_choices_to={'date2__isnull':True},help_text=u'Носитель не должен быть уничтожен',verbose_name=u'Носитель ключевой информации')
    arm=models.ForeignKey(ARM,blank=True,null=True,verbose_name=u'АРМ')
    storage=models.CharField(max_length=255,blank=True,verbose_name=u'Контейнер/файл')
    kd=models.ForeignKey(KD,verbose_name=u'Ключевой документ')
    backup=models.BooleanField(blank=True,verbose_name=u'Рез.коп.')
    admin1=models.CharField(max_length=255,blank=True,verbose_name=u'Записал администратор')
    date2=models.DateField(blank=True,null=True,verbose_name=u'Дата стирания')
    admin2=models.CharField(max_length=255,blank=True,verbose_name=u'Стёр администратор')
    reason=models.ForeignKey(Reason,blank=True,null=True,verbose_name=u'Причина стирания')
    note=models.TextField(blank=True,verbose_name=u'Примечание')


    def __unicode__(self):
        return u'%s %s: %s' % (self.date1,self.kd,self.nki)


    class Meta:
        verbose_name = u'экземпляр'
        verbose_name_plural = u'Журнал записи ключевых документов'
        ordering = ['-date1','kd','nki']


    def save(self, *args, **kwargs):
        super(KDRecord, self).save()

        # Автоматическое регистрация систем в носителе
        if self.nki!=None:
            system_current=[]           # Текущий список
            for s in NKI.objects.get(id=self.nki.id).system.values_list('id'):
                system_current.append(s[0])
            system_new=[]               # Новый список
            for kdr in KDRecord.objects.all().filter(nki=self.nki.id,date2=None):
                try:
                    system_new.index(kdr.kd.system.id)
                except:
                    system_new.append(kdr.kd.system.id)
            # Удаляем старые записи
            for s in system_current:
                NKI.objects.get(id=self.nki.id).system.remove(System.objects.get(id=s))
            # Формируем список заново
            for s in system_new:
                NKI.objects.get(id=self.nki.id).system.add(System.objects.get(id=s))



# Обновления ключевых документов
class KDUpdate(models.Model):
    kd_old=models.ForeignKey(KD,related_name='kd_old',verbose_name=u'Предыдущий ключ')
    kd_new=models.ForeignKey(KD,related_name='kd_new',verbose_name=u'Новый ключ')
    label=models.CharField(max_length=255,blank=True,verbose_name=u'Метка')


    def __unicode__(self):
        return u'%s %s - %s' % (self.label,self.kd_old,self.kd_new)


    class Meta:
        verbose_name = u'замена'
        verbose_name_plural = u'Журнал замены ключей'





