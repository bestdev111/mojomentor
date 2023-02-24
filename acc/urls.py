from . import views
from django.urls import path

urlpatterns = [
    path(
        'send-email-confirmation-link',
        views.send_email_confirmation_link,
        name='send_email_confirmation_link'
    ),
    path(
        'confirm-email/<str:token>', views.confirm_email, name='acc_confirm_email'
    ),
    path('chats', views.chats, name='acc_chats'),
    path('create-chat-user/<int:id>',
         views.create_chat_user, name='create_chat_user'),
    path('test-url', views.test_url),
    path('meeting', views.meeting),
    path('update', views.update, name='user_update'),
    path('get-chats/<int:user_id>', views.get_chats, name='get_chats'),
    path('change-status/<int:id>', views.change_status, name='change_status'),
    path('user/<int:id>/follow', views.follow_user, name='follow_user'),
    path('user/<int:id>/unfollow', views.unfollow_user, name='unfollow_user'),
    path('my-referrals', views.my_referrals, name='my_referrals'),
    path('my-referrals-list', views.my_referrals_list, name='my_referrals_list'),

    # file uploading for chats
    path('chat-file-upload', views.chat_file_upload, name='chat_file_upload'),

]
