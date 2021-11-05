#!/usr/bin/python
# -*- coding: utf8 -*-

from django.contrib import admin
import base.models



class SystemAdmin(admin.ModelAdmin):
    search_fields = ("system",)



class OfficeAdmin(admin.ModelAdmin):
    search_fields = ("office",)



class UserAdmin(admin.ModelAdmin):
    search_fields = ("name",)



class ReasonAdmin(admin.ModelAdmin):
    search_fields = ("reason",)



class NKITypeAdmin(admin.ModelAdmin):
    search_fields = ("nkitype",)



class KDTypeAdmin(admin.ModelAdmin):
    search_fields = ("kdtype",)



class SignRightAdmin(admin.ModelAdmin):
    list_display = ("docname","docdate","docnumber","date1","date2","office")
    search_fields = ("docname",)
    list_filter = ('office','system')
    fields = ("docname","docdate","docnumber","date1","date2","office","user","system","note")
    filter_horizontal = ('user','system')



class NKIAdmin(admin.ModelAdmin):
    list_display = ("regnumber","nkitype","sernumber","date1","user","label","date2","reason")
    search_fields = ("regnumber","label","sernumber")
    list_filter = ('nkitype','system')
    date_hierarchy = 'date1'
    fields = ("date1","regnumber","nkitype","sernumber","source","user","label","note","date2","reason")
    raw_id_fields = ('user',)



    def save_model(self, request, obj, form, change):
        # Новая запись
        if obj.id==None:
            obj.admin1=request.user.last_name+u' '+request.user.first_name

        # Уничтожение
        if obj.date2!=None and (obj.admin2==None or obj.admin2==""):
            obj.admin2=request.user.last_name+u' '+request.user.first_name

        obj.save()



class ARMAdmin(admin.ModelAdmin):
    list_display = ("name","user")
    search_fields = ("name",)
    raw_id_fields = ('user',)



class KDAdmin(admin.ModelAdmin):
    list_display = ("label","kdtype","sernumber","date1","user","office","system","revocation","compromise")
    search_fields = ("label","sernumber")
    list_filter = ('kdtype','office','system',"date1","revocation")
    date_hierarchy = 'date1'
    fields = ("kdtype","date1","date2","revocation","compromise","sernumber","user","system","office","label","note")
    raw_id_fields = ('user',)



    def save_model(self, request, obj, form, change):
        # Новая запись
        if obj.id==None:
            obj.admin1=request.user.last_name+u' '+request.user.first_name

        # Отзыв или компрометация
        if (obj.revocation==True or obj.compromise==True) and (obj.admin2==None or obj.admin2==""):
            obj.admin2=request.user.last_name+u' '+request.user.first_name

        obj.save()



class NKIOutAdmin(admin.ModelAdmin):
    list_display = ("nki","date1","user","office","date2","reason")
    list_filter = ('office',"date1")
    date_hierarchy = 'date1'
    fields = ("user","nki","date1","office","note","date2","reason")
    raw_id_fields = ('nki','user')



    def save_model(self, request, obj, form, change):
        # Новая запись
        if obj.id==None:
            obj.admin1=request.user.last_name+u' '+request.user.first_name

        # Возврат
        if obj.date2!=None and (obj.admin2==None or obj.admin2==""):
            obj.admin2=request.user.last_name+u' '+request.user.first_name

        obj.save()



class KDRecordAdmin(admin.ModelAdmin):
    list_display = ("date1","kd","nki","arm","backup","date2","reason")
    fields = ("date1","nki","arm","storage","kd","backup","note","date2","reason")
    raw_id_fields = ('nki','arm','kd')
    date_hierarchy = 'date1'



    def save_model(self, request, obj, form, change):
        # Новая запись
        if obj.id==None:
            obj.admin1=request.user.last_name+u' '+request.user.first_name

        # Стирание
        if obj.date2!=None and (obj.admin2==None or obj.admin2==""):
            obj.admin2=request.user.last_name+u' '+request.user.first_name

        obj.save()



class KDUpdateAdmin(admin.ModelAdmin):
    list_display = ("kd_old","kd_new","label")
    search_fields = ("kd_old","kd_new")
    raw_id_fields = ('kd_old','kd_new')



admin.site.register(base.models.System,SystemAdmin)
admin.site.register(base.models.Office,OfficeAdmin)
admin.site.register(base.models.User,UserAdmin)
admin.site.register(base.models.Reason,ReasonAdmin)
admin.site.register(base.models.NKIType,NKITypeAdmin)
admin.site.register(base.models.KDType,KDTypeAdmin)
admin.site.register(base.models.SignRight,SignRightAdmin)
admin.site.register(base.models.NKI,NKIAdmin)
admin.site.register(base.models.ARM,ARMAdmin)
admin.site.register(base.models.KD,KDAdmin)
admin.site.register(base.models.NKIOut,NKIOutAdmin)
admin.site.register(base.models.KDRecord,KDRecordAdmin)
admin.site.register(base.models.KDUpdate,KDUpdateAdmin)

