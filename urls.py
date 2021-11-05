#!/usr/bin/python
# -*- coding: utf8 -*-

from django.conf.urls.defaults import patterns, include, url

from django.contrib import admin
admin.autodiscover()

import base.views

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),

    url(r'^$', base.views.index),        # Начальная страница

    url(r'^nkijournal/$', base.views.make_nki_journal),        # Журнал регистрации НКИ
    url(r'^kdjournal/$', base.views.make_kd_journal),          # Журнал учёта КД
    url(r'^nkioutjournal/$', base.views.make_nkiout_journal),  # Журнал регистрации НКИ

    url(r'^reportoffices/$', base.views.report_offices),       # Отчёт по офисам
    url(r'^report_kddate/$', base.views.report_kddate),        # Отчёт по ключам, срок действия которых истекает
    url(r'^report_signright/$', base.views.report_signright),  # Отчёт о пользователях, имеющих права электронной подписи, по офисам

    url(r'^audit_signright/$', base.views.audit_signright),    # Аудит прав подписи по офисам

    url(r'^statyears/$', base.views.statyears),                # Статистический отчёт
)
