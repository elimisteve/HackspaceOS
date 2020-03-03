from django.urls import path
from _apis.views.hackspace_os_api_view import HackspaceOSapiView
from _apis.views.hackspaces_org_api_view import HackspacesORGapiView

urlpatterns = [
    path('apis/hackspace_os/page/<str:sub_page>',
         HackspaceOSapiView.as_view(path='page'), name='page'),
    path('apis/hackspace_os/load_more/<str:sub_page>',
         HackspaceOSapiView.as_view(path='load_more'), name='load_more'),
    path('apis/hackspace_os/events_slider',
         HackspaceOSapiView.as_view(path='events_slider'), name='events_slider'),
    path('apis/hackspace_os/open_status',
         HackspaceOSapiView.as_view(path='open_status'), name='open_status'),
    path('apis/hackspace_os/event_overlap',
         HackspaceOSapiView.as_view(path='event_overlap'), name='event_overlap'),
    path('apis/hackspace_os/meeting_duration',
         HackspaceOSapiView.as_view(path='meeting_duration'), name='meeting_duration'),
    path('apis/hackspace_os/translate',
         HackspaceOSapiView.as_view(path='translate'), name='translate'),
    path('apis/hackspace_os/remove_keyword',
         HackspaceOSapiView.as_view(path='remove_keyword'), name='remove_keyword'),
    path('apis/hackspace_os/save_keyword',
         HackspaceOSapiView.as_view(path='save_keyword'), name='save_keyword'),
    path('apis/hackspace_os/search',
         HackspaceOSapiView.as_view(path='search'), name='search'),
    path('apis/hackspace_os/upload_image',
         HackspaceOSapiView.as_view(path='upload_image'), name='upload_image'),
]

handler404 = '_database.views.handler404'
