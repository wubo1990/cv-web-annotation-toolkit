from django.contrib import admin
from models import Dataset,DataItem,AnnotationType,Annotation,PredictionsSet



class DatasetAdmin(admin.ModelAdmin):
    list_display = ('name', )
    fields = ('name',);

class DataItemAdmin(admin.ModelAdmin):
    list_display = ('ds','url')

class AnnotationTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'explanation')

class AnnotationAdmin(admin.ModelAdmin):
    list_display = ('id','annotation_type', 'canonic_url')

class PredictionsSetAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created','description')

          
admin.site.register(Dataset, DatasetAdmin);
admin.site.register(DataItem, DataItemAdmin);
admin.site.register(AnnotationType, AnnotationTypeAdmin);
admin.site.register(Annotation, AnnotationAdmin);
admin.site.register(PredictionsSet, PredictionsSetAdmin);
