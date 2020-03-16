from django.urls import path, include
from dose_app import views

# SET THE NAMESPACE!
app_name = 'dose_app'

urlpatterns = [
    # path('pesquisa/', views.pesquisa, name='pesquisa'),
    path('', views.Index.as_view(), name='index'),
    path('test', views.test, name='test'),
    path('pesquisa/', views.SearchView.as_view(), name='pesquisa'),
    path('sobre/', views.sobre, name='sobre'),
    path('config/', views.config, name='config'),
    path('statistic_info/', views.StatisticInfoXA.as_view(), name='info_estatisticas'),
    path('detalhe/<int:pk>/<int:ppk>/', views.XADetailView.as_view(), name='detalhes'),
    path('detalhe/total/pesquisa=<slug:search_name>+<int:pk>+<slug:type>/', views.XATotalDetailView.as_view(), name='detalhes_total'),
    path('detalhe/total/pesquisa=<slug:date_before>+<slug:date_after>+<int:pk>+<slug:type>/', views.XATotalDetailViewData.as_view(), name='detalhes_total_data'),
    path('detalhe/total/agrupado/pesquisa=<slug:search_name>+<slug:id_group>+<slug:type>/', views.XATotalDetailViewGroup.as_view(), name='grupo_detalhes_total'),
    path('detalhe/total/agrupado/pesquisa=<slug:date_before>+<slug:date_after>+<slug:id_group>+<slug:type>/', views.XATotalDetailViewGroupData.as_view(), name='grupo_detalhes_total_data'),
    path('lista/pesquisa=<slug:search_name>', views.StudyListView.as_view(), name='lista'),
    path('lista/pesquisa=<slug:date_before>+<slug:date_after>', views.StudyListViewByDate.as_view(), name='lista_data'),
    path('comm/in/', views.hucam_server_comm_in, name='comm_in'),
    path('comm/out.json', views.hucam_server_comm_out, name='comm_out'),
    path('comm/update', views.hucam_server_comm_update, name='atualizar')

]