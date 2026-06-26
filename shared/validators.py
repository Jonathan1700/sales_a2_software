from django.core.exceptions import ValidationError


def validate_cedula_ec(value):
    """
    Valida cédula ecuatoriana (10 dígitos) o RUC (13 dígitos)
    usando el algoritmo oficial del Registro Civil de Ecuador.

    Uso en modelo:
        from shared.validators import validate_cedula_ec
        dni = CharField(validators=[validate_cedula_ec])
    """

    # --- Paso 1: Verificar que solo contenga números ---
    if not value.isdigit():
        raise ValidationError(
            'The ID must contain only numbers.',
            code='invalid_chars'
        )

    # --- Paso 2: Verificar longitud ---
    if len(value) not in (10, 13):
        raise ValidationError(
            'The ID must be 10 digits (cédula) or 13 digits (RUC).',
            code='invalid_length'
        )

    # --- Paso 3: Verificar código de provincia (01 a 24) ---
    province = int(value[:2])
    if province < 1 or province > 24:
        raise ValidationError(
            f'Invalid province code: {province}. Must be between 01 and 24.',
            code='invalid_province'
        )

    # --- Paso 4: Verificar tercer dígito ---
    third_digit = int(value[2])
    if third_digit >= 6:
        raise ValidationError(
            'The third digit must be less than 6 for natural persons.',
            code='invalid_third'
        )

    # --- Paso 5: Algoritmo de validación (Módulo 10) ---
    coefficients = [2, 1, 2, 1, 2, 1, 2, 1, 2]
    total = 0

    for i in range(9):
        result = int(value[i]) * coefficients[i]
        if result > 9:
            result -= 9
        total += result

    # --- Paso 6: Calcular dígito verificador ---
    verifier = 10 - (total % 10)
    if verifier == 10:
        verifier = 0

    # --- Paso 7: Comparar con el décimo dígito ---
    if verifier != int(value[9]):
        raise ValidationError(
            'Invalid ID number. The check digit does not match.',
            code='invalid_verifier'
        )

    return value
