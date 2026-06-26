"""
Columnas dinámicas ("Campos visibles") para vistas basadas en funciones (FBV).

Equivalente funcional de `DynamicColumnsMixin` (que solo sirve a CBV), pensado
para listados como Facturas y Compras que se implementan como FBV por usar
formsets. La selección se persiste en sesión, igual que en Productos.

Fuente ÚNICA de columnas (tabla + PDF + Excel) = lista de dicts:
    COLUMNS = [
        {'key': 'total', 'label': 'Total', 'default': True, 'accessor': 'total'},
        ...
    ]
donde accessor = str | "a.b.c" | callable(obj).
"""


def get_visible_columns(request, columns, session_key):
    """Keys visibles. Fuente: GET (al aplicar) -> sesión -> defaults."""
    all_keys = [c['key'] for c in columns]
    defaults = [c['key'] for c in columns if c.get('default')]
    g = request.GET

    if 'reset_columns' in g:
        request.session.pop(session_key, None)
        return defaults

    if 'columns' in g:
        selected = [k for k in g.getlist('columns') if k in all_keys]
        visible = selected or defaults  # mínimo obligatorio: 1 columna
        request.session[session_key] = visible
        return visible

    saved = request.session.get(session_key)
    if saved:
        valid = [k for k in saved if k in all_keys]
        return valid or defaults

    return defaults


def columns_context(request, columns, session_key):
    """Contexto para la plantilla: visible, columns (checkboxes) y conteos."""
    visible = get_visible_columns(request, columns, session_key)
    return {
        'visible': visible,
        'columns': [
            {'key': c['key'], 'label': c['label'], 'checked': c['key'] in visible}
            for c in columns
        ],
        'visible_count': len(visible),
        'total_columns': len(columns),
    }


def _resolve(obj, accessor):
    if callable(accessor):
        return accessor(obj)
    value = obj
    for part in accessor.split('.'):
        value = getattr(value, part)
        if callable(value):
            value = value()
    return value


def visible_export(columns, visible, queryset):
    """(headers, rows) usando SOLO las columnas visibles, en orden de COLUMNS."""
    cols = [c for c in columns if c['key'] in visible]
    headers = [c['label'] for c in cols]
    rows = [[_resolve(o, c['accessor']) for c in cols] for o in queryset]
    return headers, rows
