from django.contrib import admin
from .models import Chat
from .models import ContactMessage
from .models import ProUser

admin.site.register(ProUser)
admin.site.register(ContactMessage)
admin.site.register(Chat)

