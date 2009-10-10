from django.db import models

from mturk.models import Session
# Create your models here.



DS_TYPES = (
	(1, 'Labeled data'),
	(2, 'Unlabeled data'),
    );

class DataSource(models.Model):
        title =models.TextField(blank=True);
	source_type  = models.IntegerField(choices=DS_TYPES,default=1);
        source_ref =models.TextField(blank=True);
        source_session =models.ForeignKey(Session,blank=True,null=True,default=None);

        source_parameters  =models.TextField(blank=True,default="");
        percent_train      =models.DecimalField(max_digits=15,decimal_places=4,
                                           default="50.0",
                                           help_text="The data to use in training.");
        percent_validation =models.DecimalField(max_digits=15,decimal_places=4,
                                           default="25.0",
                                           help_text="The data to use in training.");
        percent_test       =models.DecimalField(max_digits=15,decimal_places=4,
                                           default="25.0",
                                           help_text="The data to use in training.");
        random_seed        =models.IntegerField(default=42,
                                           help_text="The random seed for split (-1 means use time).");        

	def __str__(self):
            s="("+str(self.percent_train)+"/"+str(self.percent_validation)+"/"+str(self.percent_test)+")";
            if self.source_session is not None:
                p= "%s [ %s ]" % (self.source_session.code, self.source_type )
            else:
                p= "%s [ %s ]" % (self.source_ref, self.source_type )

            return self.title+": "+p+" "+s

TARGET_TYPES = (
    (1, 'Object box'),
    (2, 'Material classifier'),
    (3, 'Object segmentation'),
    (4, 'Object 3D model'),
    (5, 'Object relations'),
    );

class ModelTarget(models.Model):
    target_type  = models.IntegerField(choices=TARGET_TYPES,default=1);
    target_code  = models.SlugField();
    target_name  = models.TextField(blank=True);
    def __str__(self):
        return self.target_code

MODEL_STATUS = (
    (1, 'New'),
    (2, 'Learning'),
    (201, 'Learning-complete'),
    (3, 'Testing'),
    (301, 'Testing-complete'),
    (4, 'Optimizing'),
    (5, 'Ready'),
    );

MODEL_TYPES = (
    (1, 'PF-HOG'),
    (2, 'Dorylus'),
    (3, 'FM3N'),
    (4, '3D-feature-cloud'),
    );

class LearnedModel(models.Model):

    code    = models.SlugField();
    name  = models.TextField(blank=True);
    description  = models.TextField(blank=True);
    
    targets       = models.ManyToManyField(ModelTarget,blank=True,null=True);
    data_sources  = models.ManyToManyField(DataSource,blank=True,null=True);

    model_type        = models.IntegerField(choices=MODEL_TYPES,default=1);
    model_arguments   = models.TextField(blank=True);

        
    model_status  = models.IntegerField(choices=MODEL_STATUS,default=1);
    
    location      = models.TextField(blank=True);
    
    created            = models.DateTimeField(auto_now_add=True);
    learning_completed = models.DateTimeField(null=True,blank=True);

    locked_by   = models.TextField(blank=True,null=True);
    locked_until = models.DateTimeField(null=True,blank=True);

    def __str__(self): 
        return self.name+" ["+self.code+"]"
    
    def get_ext(self):
        if self.model_type==1:
            return "mat"
        elif self.model_type==2:
            return "dd"
        elif self.model_type==3:
            return "fm3n"
