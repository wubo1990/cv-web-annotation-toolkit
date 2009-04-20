from django.db import models

# Create your models here.

class ImageSource(models.Model):
	name=models.TextField();
	url=models.TextField();

	def __str__(self):
        	return "%s (%s" % (self.name,self.url)

	class Admin:
		pass

class Image(models.Model):
	source=models.ForeignKey(ImageSource);
	source_image_id=models.TextField();

	notes=models.TextField(blank=True);

	url=models.TextField();
	preview_url=models.TextField();
	best_quality_url=models.TextField();

	relevance = models.IntegerField(default=0);
	added_at = models.DateTimeField(auto_now_add=True);

	def __str__(self):
        	return "%d %s (%s)" % (self.relevance, self.source_image_id,self.url)

	class Admin:
		pass



def get_stats():
    from django.db import connection
    cursor = connection.cursor()
    cursor.execute("""
select relevance, count(*) from image_collector_image group by relevance;
""")
    results=[];
    try:
	for row in cursor.fetchall():
		results.append((row[0],row[1]));
    except:
	return []
    return results
	
