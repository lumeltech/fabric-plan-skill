"""Explicit new-input mode policy; native omission defaults are not authoring defaults."""

def allow_input(value='ReadAndEdit',ids=None):
    if isinstance(value,dict):
        if set(value)!={'BasedOnFormula'}:raise ValueError('Invalid allow_input policy tag')
        from .construct import expression
        return {'BasedOnFormula':expression(value['BasedOnFormula'],ids or {})}
    if value not in ('Edit','ReadAndEdit'):raise ValueError('Use Edit, ReadAndEdit or a BasedOnFormula expression for allow_input')
    return value
