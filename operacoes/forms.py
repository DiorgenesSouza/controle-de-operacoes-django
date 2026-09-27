from decimal import Decimal, InvalidOperation

from django import forms

from .models import Operacao


class OperacaoForm(forms.ModelForm):
    valor_nota = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Ex.: 250.000,00",
            }
        )
    )

    class Meta:
        model = Operacao

        fields = [
            "numero_nota",
            "valor_nota",
            "cliente",
            "origem",
            "destino",
            "tipo_operacao",
            "data_recebimento",
            "status_operacao",
            "placa",
            "motorista",
            "data_entrega",
        ]

        widgets = {
            "numero_nota": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Informe o número da nota",
                }
            ),

            "cliente": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Informe o cliente",
                }
            ),

            "origem": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Cidade de origem",
                }
            ),

            "destino": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Cidade de destino",
                }
            ),

            "tipo_operacao": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "data_recebimento": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),

            "status_operacao": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "placa": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ex.: ABC1D23",
                }
            ),

            "motorista": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Nome do motorista",
                }
            ),

            "data_entrega": forms.DateTimeInput(
                attrs={
                    "class": "form-control",
                    "type": "datetime-local",
                },
                format="%Y-%m-%dT%H:%M",
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["tipo_operacao"].empty_label = (
            "Selecione o tipo de operação"
        )

        self.fields["data_entrega"].required = False

        self.fields["data_entrega"].input_formats = [
            "%Y-%m-%dT%H:%M",
        ]

        self.fields["placa"].widget.attrs["style"] = (
            "text-transform: uppercase;"
        )

        # Quando estiver editando um registro,
        # mostra o valor no formato brasileiro.
        if self.instance and self.instance.pk:
            valor = self.instance.valor_nota

            if valor is not None:
                valor_formatado = (
                    f"{valor:,.2f}"
                    .replace(",", "X")
                    .replace(".", ",")
                    .replace("X", ".")
                )

                self.initial["valor_nota"] = valor_formatado

    def clean_valor_nota(self):
        valor = self.cleaned_data.get("valor_nota", "").strip()

        if not valor:
            raise forms.ValidationError(
                "Informe o valor da nota."
            )

        valor = (
            valor
            .replace("R$", "")
            .replace(" ", "")
            .replace(".", "")
            .replace(",", ".")
        )

        try:
            return Decimal(valor)

        except InvalidOperation:
            raise forms.ValidationError(
                "Informe um valor válido. Ex.: 250.000,00"
            )

    def clean_placa(self):
        placa = self.cleaned_data.get("placa")

        if placa:
            return placa.strip().upper()

        return placa

    def clean(self):
        cleaned_data = super().clean()

        status = cleaned_data.get("status_operacao")

        if status == "Em trânsito":
            cleaned_data["data_entrega"] = None

        return cleaned_data