from django.db.models import get_model
from django.template import Library, Node, TemplateSyntaxError
from apps.tagging.models import Tag

register = Library()

class TagsCloudForModelNode(Node):
    def __init__(self, model, varname, step):
        self.varname, self.step = varname, step
        self.model = get_model(*model.split('.'))

    def render(self, context):
        context[self.varname] = Tag.objects.cloud_for_model(self.model,
                                                            self.step)
        return ''

def do_tags_cloud_for_model(parser, token):
    """
    Retrieves a tag cloud for the given model

    Example usage::

        {% tags_cloud_for_model app.Model as object_list %}
        {% tags_cloud_for_model articles.Article as object_list step 6 %}
    """
    step = 4
    bits = token.contents.split()
    if len(bits) < 4:
        raise TemplateSyntaxError('%s tag requires three arguments' % bits[0])
    if bits[2] != 'as':
        raise TemplateSyntaxError("second argument to %s tag must be 'as'" % bits[0])
    if len(bits) > 4:
        if bits[4] != 'step':
            raise TemplateSyntaxError("optional fourth argument to %s tag must\
                                       be 'step'" % bits[0])
        try:
            step = int(bits[5])
        except IndexError:
            raise TemplateSyntaxError("optional fifth argument after step is \
                                       required")
        except ValueError:
            raise TemplateSyntaxError("optional fifth argument after step is \
                                       not an integer")
    return TagsCloudForModelNode(bits[1], bits[3], step)

register.tag('tags_cloud_for_model', do_tags_cloud_for_model)
