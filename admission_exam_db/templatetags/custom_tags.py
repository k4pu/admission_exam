from django import template
register = template.Library()

@register.filter(name="get_value")
def get_value(dic, key):
    if (key in dic.keys()):
        return dic[key]
    else:
        return None

@register.filter(name="get_length")
def get_length(dic):
        return len(dic)
