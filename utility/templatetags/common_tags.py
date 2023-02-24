from django import template

register = template.Library()

def multiply_str(value, arg):
    """Multiply string with number"""
    return value * arg

register.filter('multiply_str', multiply_str)