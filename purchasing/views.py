import json
from decimal import Decimal

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from billing.models import Product, Supplier
from .models import Purchase, PurchaseDetail
from .forms import PurchaseForm, PurchaseDetailFormSet
from shared.exports import export_excel, export_pdf
from shared.columns import columns_context, get_visible_columns, visible_export


# === Columnas dinámicas de Compras (tabla + PDF + Excel) ===
PURCHASE_COLUMNS = [
    {'key': 'id',        'label': '#',          'default': True,  'accessor': 'id'},
    {'key': 'supplier',  'label': 'Proveedor',  'default': True,  'accessor': lambda o: str(o.supplier)},
    {'key': 'document',  'label': 'Documento #', 'default': True, 'accessor': 'document_number'},
    {'key': 'date',      'label': 'Fecha',      'default': True,  'accessor': lambda o: o.purchase_date.strftime('%d/%m/%Y')},
    {'key': 'subtotal',  'label': 'Subtotal',   'default': True,  'accessor': 'subtotal'},
    {'key': 'tax',       'label': 'IVA',        'default': True,  'accessor': 'tax'},
    {'key': 'total',     'label': 'Total',      'default': True,  'accessor': 'total'},
    {'key': 'is_active', 'label': 'Activo',     'default': False, 'accessor': lambda o: 'Sí' if o.is_active else 'No'},
]


@login_required
def purchase_list(request):
    """Lista compras con filtros y paginación (igual que productos)."""
    qs = Purchase.objects.select_related('supplier').all()
    p = request.GET

    supplier = p.get('supplier', '').strip()
    if supplier:
        qs = qs.filter(supplier_id=supplier)

    document = p.get('document', '').strip()
    if document:
        qs = qs.filter(document_number__icontains=document)

    date_from = p.get('date_from', '').strip()
    if date_from:
        qs = qs.filter(purchase_date__date__gte=date_from)

    date_to = p.get('date_to', '').strip()
    if date_to:
        qs = qs.filter(purchase_date__date__lte=date_to)

    total_min = p.get('total_min', '').strip()
    if total_min:
        qs = qs.filter(total__gte=total_min)

    total_max = p.get('total_max', '').strip()
    if total_max:
        qs = qs.filter(total__lte=total_max)

    is_active = p.get('is_active', '').strip()
    if is_active in ('0', '1'):
        qs = qs.filter(is_active=(is_active == '1'))

    # Exportar (respeta filtros y columnas visibles). Botones PDF/Excel.
    export = p.get('export')
    if export in ('excel', 'pdf'):
        visible = get_visible_columns(request, PURCHASE_COLUMNS, 'purchase_visible_columns')
        headers, rows = visible_export(PURCHASE_COLUMNS, visible, qs)
        fn = export_excel if export == 'excel' else export_pdf
        return fn(headers, rows, 'compras', 'Listado de Compras')

    paginator = Paginator(qs, 3)
    page_obj = paginator.get_page(p.get('page'))

    params = request.GET.copy()
    for k in ('page', 'columns', 'reset_columns'):
        params.pop(k, None)

    ctx = {
        'items': page_obj,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'querystring': params.urlencode(),
        'filters': request.GET,
        'suppliers': Supplier.objects.all(),
    }
    ctx.update(columns_context(request, PURCHASE_COLUMNS, 'purchase_visible_columns'))
    return render(request, 'purchasing/purchase_list.html', ctx)


@login_required
def purchase_create(request):
    """Crea una compra con sus líneas y AUMENTA el stock de cada producto."""
    if request.method == 'POST':
        form = PurchaseForm(request.POST)
        formset = PurchaseDetailFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            # Una compra debe tener al menos una línea con producto; sin esto
            # se podría crear una compra vacía (sin nada).
            has_detail = any(
                f.cleaned_data.get('product') and not f.cleaned_data.get('DELETE')
                for f in formset.forms
            )
            if not has_detail:
                messages.error(request, 'Debes agregar al menos un producto a la compra.')
            else:
                purchase = form.save(commit=False)
                purchase.save()

                formset.instance = purchase
                details = formset.save()          # guarda las líneas

                # Sumar stock por cada línea comprada
                for detail in details:
                    product = detail.product
                    product.stock += detail.quantity
                    product.save(update_fields=['stock'])

                # Calcular totales
                subtotal = sum(d.subtotal for d in purchase.details.all())
                purchase.subtotal = subtotal
                purchase.tax = subtotal * Decimal('0.15')   # IVA 15%
                purchase.total = purchase.subtotal + purchase.tax
                purchase.save()

                messages.success(request, f'¡Compra #{purchase.id} creada! Total: ${purchase.total}')
                return redirect('purchasing:purchase_list')
    else:
        form = PurchaseForm()
        formset = PurchaseDetailFormSet()

    # Sugerencia de costo al elegir producto:
    # último unit_cost comprado; si nunca se compró, su precio de venta como referencia
    product_costs = {
        str(p.id): str(p.unit_price)
        for p in Product.objects.filter(is_active=True)
    }
    for d in (PurchaseDetail.objects
              .select_related('product')
              .order_by('purchase__purchase_date')):
        product_costs[str(d.product_id)] = str(d.unit_cost)  # el más reciente gana

    return render(request, 'purchasing/purchase_form.html', {
        'form': form,
        'formset': formset,
        'title': 'Crear Compra',
        'product_costs_json': json.dumps(product_costs),
    })


@login_required
def purchase_detail(request, pk):
    """Muestra el detalle completo de una compra."""
    purchase = get_object_or_404(
        Purchase.objects.select_related('supplier')
                        .prefetch_related('details__product'),
        pk=pk
    )
    return render(request, 'purchasing/purchase_detail.html', {'purchase': purchase})


@login_required
def purchase_delete(request, pk):
    """Elimina una compra, sus detalles (CASCADE) y REVIERTE el stock que sumó."""
    purchase = get_object_or_404(
        Purchase.objects.prefetch_related('details__product'), pk=pk
    )

    if request.method == 'POST':
        # Validar ANTES de borrar: ningún producto puede quedar en negativo
        for detail in purchase.details.all():
            if detail.product.stock < detail.quantity:
                messages.error(
                    request,
                    f'No se puede eliminar: "{detail.product.name}" quedaría con '
                    f'stock negativo (hay {detail.product.stock}, la compra sumó '
                    f'{detail.quantity}). Probablemente ya se vendió.'
                )
                return redirect('purchasing:purchase_detail', pk=purchase.pk)

        # Revertir stock y borrar
        purchase_id = purchase.id
        for detail in purchase.details.all():
            product = detail.product
            product.stock -= detail.quantity
            product.save(update_fields=['stock'])

        purchase.delete()
        messages.success(request, f'¡Compra #{purchase_id} eliminada! Stock revertido.')
        return redirect('purchasing:purchase_list')

    return render(request, 'purchasing/purchase_confirm_delete.html', {'object': purchase})