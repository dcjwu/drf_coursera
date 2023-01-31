from rest_framework.validators import UniqueValidator

from .models import MenuItem

unique_menuitem_title = UniqueValidator(queryset=MenuItem.objects.all(), lookup='iexact')
