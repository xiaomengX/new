from django.urls import path
from django.conf.urls import url
from django.views.generic import TemplateView
from . import views
urlpatterns=[
    url(r'^$',views.login,name='sb_admin_start'),
    # path('register/',TemplateView.as_view(template_name="django_sb_admin/register.html"),name='sb_admin_register'),
    # path('forgot_password/', TemplateView.as_view(
    #     template_name="django_sb_admin/forgot_password.html"),
    #      name='sb_admin_forgot_password'
    #      ),
    # path('404/', TemplateView.as_view(
    #     template_name="django_sb_admin/sb_admin_404.html"),
    #      name='sb_admin_404'
    #      ),
    url(r'^login/$',views.login,name='sb_admin_login'),
    url(r'^register/$',views.register,name='sb_admin_register'),
    url(r'^forgot/$', views.forgot, name='sb_admin_forgot_password'),
    url(r'^dashboard/$',views.dashboard,name='sb_admin_dashboard'),
    url(r'^charts/$', views.charts, name='sb_admin_charts'),
    url(r'^tables/$', views.tables, name='sb_admin_tables'),
    url(r'^forms/$', views.forms, name='sb_admin_forms'),
    url(r'^bootstrap-elements/$', views.bootstrap_elements, name='sb_admin_bootstrap_elements'),
    url(r'^bootstrap-grid/$', views.bootstrap_grid, name='sb_admin_bootstrap_grid'),
    url(r'^rtl-dashboard/$', views.rtl_dashboard, name='sb_admin_rtl_dashboard'),
    url(r'^blank/$', views.blank, name='sb_admin_blank'),
    url(r'^logout/$', views.logout, name='sb_admin_logout'),
    url(r'^base/$', views.base, name='sb_admin_base'),
    url(r'^record/$', views.record, name='sb_admin_record'),
    url(r'^play/$', views.play, name='sb_admin_play'),
    url(r'^training/$', views.training, name='sb_admin_training'),
    url(r'^speech_record/$', views.speech_record, name='sb_admin_speech_record'),
    url(r'^testing/$', views.testing, name='sb_admin_testing'),
    url(r'^pre_emphasis/$', views.pre_emphasis, name='sb_admin_pre_emphasis'),
    url(r'^Framing/$', views.Framing, name='sb_admin_Framing'),
    url(r'^hamm/$', views.hamm, name='sb_admin_hamm'),
    url(r'^mfcc/$', views.mfcc, name='sb_admin_mfcc'),
    url(r'^gammatone/$', views.gammatone, name='sb_admin_gammatone'),
    url(r'^blank_framing/$', views.blank_framing, name='sb_admin_blank_framing'),
    url(r'^blank_hamm/$', views.blank_hamm, name='sb_admin_blank_hamm'),
    url(r'^blank_mfcc/$', views.blank_mfcc, name='sb_admin_blank_mfcc'),
    url(r'^blank_GTG/$', views.blank_GTG, name='sb_admin_blank_GTG'),
    url(r'^my-ajax-test/',views.myajaxtestview,name='ajax-test-view'),
    url(r'^huatong_speech/$', views.huatong_speech, name='sb_admin_huatong_speech'),
    url(r'^thisiurl$', views.process_data, name='process'), # 处理数据的url, 当前页面的地址
    url(r'^progressurl$', views.show_progress, name='progress'), # 查询进度的url, 不需要html页面




]