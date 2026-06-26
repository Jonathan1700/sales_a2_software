from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from billing.models import (
    Brand, ProductGroup, Supplier, Product,
    Customer, CustomerProfile, Invoice, InvoiceDetail,
)


def valid_cedula(province, serial):
    """Genera una cédula ecuatoriana válida (módulo 10).

    province: 1-24, serial: 7 dígitos (el tercer dígito se fuerza < 6).
    """
    base = f'{province:02d}{serial:07d}'
    third = int(base[2])
    if third >= 6:  # tercer dígito debe ser < 6 para personas naturales
        base = base[:2] + '0' + base[3:]
    coeffs = [2, 1, 2, 1, 2, 1, 2, 1, 2]
    total = 0
    for i in range(9):
        r = int(base[i]) * coeffs[i]
        total += r - 9 if r > 9 else r
    verifier = 10 - (total % 10)
    if verifier == 10:
        verifier = 0
    return base + str(verifier)


class Command(BaseCommand):
    help = 'Carga datos de prueba: marcas, grupos, proveedores, productos y clientes.'

    @transaction.atomic
    def handle(self, *args, **options):
        # --- Marcas (5) ---
        brand_names = ['Samsung', 'LG', 'Sony', 'Nokia', 'Apple']
        brands = [Brand.objects.get_or_create(name=n)[0] for n in brand_names]

        # --- Grupos (5) ---
        group_names = ['Electrónica', 'Hogar', 'Computación', 'Audio', 'Accesorios']
        groups = [ProductGroup.objects.get_or_create(name=n)[0] for n in group_names]

        # --- Proveedores (5) ---
        supplier_data = [
            ('Distribuidora Andina', 'Carlos Pérez', 'ventas@andina.ec', '0991111111'),
            ('Importadora Costa', 'María López', 'info@costa.ec', '0992222222'),
            ('TecnoMayorista', 'Jorge Ruiz', 'compras@tecno.ec', '0993333333'),
            ('Global Supply', 'Ana Vega', 'contacto@global.ec', '0994444444'),
            ('ElectroPartes', 'Luis Mora', 'ventas@electro.ec', '0995555555'),
        ]
        suppliers = []
        for name, contact, email, phone in supplier_data:
            s, _ = Supplier.objects.get_or_create(
                name=name,
                defaults={'contact_name': contact, 'email': email, 'phone': phone},
            )
            suppliers.append(s)

        # --- Productos (10) ---
        product_data = [
            ('Galaxy S23', 0, 0, '899.99', 25),
            ('Smart TV 55"', 1, 1, '649.00', 15),
            ('PlayStation 5', 2, 0, '549.99', 10),
            ('Laptop Gamer', 0, 2, '1299.00', 8),
            ('Audífonos Bluetooth', 2, 3, '79.90', 50),
            ('iPhone 15', 4, 0, '1099.00', 12),
            ('Refrigeradora No Frost', 1, 1, '799.00', 6),
            ('Mouse Inalámbrico', 3, 4, '15.50', 100),
            ('Parlante Portátil', 2, 3, '120.00', 30),
            ('Teclado Mecánico', 0, 4, '59.99', 40),
        ]
        products = []
        for name, bi, gi, price, stock in product_data:
            p, created = Product.objects.get_or_create(
                name=name,
                defaults={
                    'brand': brands[bi],
                    'group': groups[gi],
                    'unit_price': Decimal(price),
                    'stock': stock,
                },
            )
            if created:
                p.suppliers.set([suppliers[bi % 5], suppliers[gi % 5]])
            products.append(p)

        # --- Clientes (5) + perfiles ---
        customer_data = [
            ('Juan', 'Andrade', 'juan@mail.com', '0981111111'),
            ('Lucía', 'Benítez', 'lucia@mail.com', '0982222222'),
            ('Pedro', 'Cordero', 'pedro@mail.com', '0983333333'),
            ('Sofía', 'Delgado', 'sofia@mail.com', '0984444444'),
            ('Miguel', 'Espinoza', 'miguel@mail.com', '0985555555'),
        ]
        for i, (fn, ln, email, phone) in enumerate(customer_data):
            dni = valid_cedula(province=i + 1, serial=1234567 + i)
            c, created = Customer.objects.get_or_create(
                dni=dni,
                defaults={'first_name': fn, 'last_name': ln, 'email': email, 'phone': phone},
            )
            if created:
                CustomerProfile.objects.create(customer=c)

        self.stdout.write(self.style.SUCCESS(
            f'Listo: {Brand.objects.count()} marcas, {ProductGroup.objects.count()} grupos, '
            f'{Supplier.objects.count()} proveedores, {Product.objects.count()} productos, '
            f'{Customer.objects.count()} clientes.'
        ))
