from django import template

register = template.Library()


@register.filter
def moeda_br(valor):
    if valor is None:
        return "R$ 0,00"

    valor_formatado = (
        f"{valor:,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )

    return f"R$ {valor_formatado}"