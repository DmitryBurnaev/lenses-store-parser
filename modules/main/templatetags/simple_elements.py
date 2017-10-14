from django import template

register = template.Library()


@register.filter
def get_attr(obj, attr_name):
    return obj.getattr(attr_name, None)


@register.filter
def get_by_key(data_dict, data_key):
    assert isinstance(data_dict, dict), 'First argument must be dict instance'
    return data_dict.get(data_key)


@register.filter
def is_sub_string(string, sub_string):
    if not (isinstance(string, str) and isinstance(sub_string, str)):
        raise ValueError('all arguments must be string')
    return sub_string in string


@register.filter
def eq_string(first_string, second_string):
    if not (isinstance(first_string, str) and isinstance(second_string, str)):
        raise ValueError('all arguments must be string')
    return first_string == second_string


@register.inclusion_tag('dashboard_simple/inclusion/icon.html')
def icon(icon_name=None, category=None):
    """ Render icon html element for bootstrap (simple) dashboard """

    if icon_name:
        return {'icon_name': icon_name}
    icon_map = {
        'lenses': 'eye-open',
        'solutions': 'glass',
        'drops': 'tint',
        'accessories': 'record'
    }

    return {
        'icon_name': icon_map.get(category, 'minus')
    }


@register.inclusion_tag('dashboard_materialize/inclusion/icon.html')
def material_icon(icon_name=None, category=None, br=False):
    """ Render icon html element for material dashboard """

    icon_map = {
        'lenses': 'visibility',
        'solutions': 'loyalty',
        'drops': 'opacity',
        'accessories': 'card_travel'
    }
    ctx = {'icon_name': icon_name, 'br': br}
    if icon_name:
        ctx['icon_name'] = icon_name
    elif category:
        ctx['icon_name'] = icon_map.get(category, 'minus')

    return ctx
