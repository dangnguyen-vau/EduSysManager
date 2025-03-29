"""
URL configuration for blockchain_gui project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

import os
from django.contrib import admin
from django.urls import path, include

# Lấy loại node từ biến môi trường (pdt, gv, sv)
NODE_TYPE = os.environ.get('NODE_TYPE', 'pdt').lower()

urlpatterns = [
    path('admin/', admin.site.urls),
]

# Chọn app URL dựa vào loại node
if NODE_TYPE == 'gv':
    # Giảng viên
    urlpatterns += [
        path('', include('teacher_app.urls')),
    ]
elif NODE_TYPE == 'sv':
    # Sinh viên (chưa phát triển)
    urlpatterns += [
        path('', include('blockchain_app.urls')),  # Tạm thời dùng app cơ bản
    ]
else:
    # Mặc định là Phòng Đào Tạo (pdt)
    urlpatterns += [
        path('', include('blockchain_app.urls')),
    ]
