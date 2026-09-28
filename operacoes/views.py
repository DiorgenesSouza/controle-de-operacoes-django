import qrcode
from io import BytesIO

from barcode import Code128
from barcode.writer import SVGWriter
from django.http import HttpResponse

from datetime import datetime

from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import OperacaoForm
from .models import Operacao


def gerar_codigo():
    ano = datetime.now().year

    ultima = (
        Operacao.objects
        .filter(codigo__startswith=f"FCD-{ano}-")
        .order_by("-id")
        .first()
    )

    if ultima:
        try:
            sequencia = int(ultima.codigo.split("-")[-1]) + 1
        except ValueError:
            sequencia = 1
    else:
        sequencia = 1

    return f"FCD-{ano}-{sequencia:06d}"


def lista_operacoes(request):
    termo = request.GET.get("q", "").strip()
    status = request.GET.get("status", "Todos")

    if status == "Inativos":
        operacoes = Operacao.objects.filter(ativo=False)
    else:
        operacoes = Operacao.objects.filter(ativo=True)

        if status in ["Em trânsito", "Entregue"]:
            operacoes = operacoes.filter(status_operacao=status)

    if termo:
        operacoes = operacoes.filter(
            Q(codigo__icontains=termo)
            | Q(numero_nota__icontains=termo)
            | Q(placa__icontains=termo)
        )

    operacoes = operacoes.order_by("-id")

    total = Operacao.objects.filter(ativo=True).count()
    em_transito = Operacao.objects.filter(
        ativo=True,
        status_operacao="Em trânsito"
    ).count()
    entregues = Operacao.objects.filter(
        ativo=True,
        status_operacao="Entregue"
    ).count()

    context = {
        "operacoes": operacoes,
        "total": total,
        "em_transito": em_transito,
        "entregues": entregues,
        "termo": termo,
        "status": status,
    }

    return render(request, "operacoes/lista.html", context)


def criar_operacao(request):
    if request.method == "POST":
        form = OperacaoForm(request.POST)

        if form.is_valid():
            operacao = form.save(commit=False)
            operacao.codigo = gerar_codigo()

            if (
                operacao.status_operacao == "Entregue"
                and not operacao.data_entrega
            ):
                operacao.data_entrega = timezone.now()

            operacao.save()
            return redirect("lista_operacoes")

    else:
        form = OperacaoForm()

    return render(
        request,
        "operacoes/form.html",
        {
            "form": form,
            "titulo": "Nova operação",
        }
    )


def editar_operacao(request, pk):
    operacao = get_object_or_404(
        Operacao,
        pk=pk,
        ativo=True
    )

    if request.method == "POST":
        form = OperacaoForm(
            request.POST,
            instance=operacao
        )

        if form.is_valid():
            operacao = form.save(commit=False)

            if (
                operacao.status_operacao == "Entregue"
                and not operacao.data_entrega
            ):
                operacao.data_entrega = timezone.now()

            operacao.save()
            return redirect("lista_operacoes")

    else:
        form = OperacaoForm(instance=operacao)

    return render(
        request,
        "operacoes/form.html",
        {
            "form": form,
            "titulo": "Editar operação",
        }
    )


def excluir_operacao(request, pk):
    operacao = get_object_or_404(
        Operacao,
        pk=pk,
        ativo=True
    )

    if request.method == "POST":
        operacao.ativo = False
        operacao.save()
        return redirect("lista_operacoes")

    return render(
        request,
        "operacoes/confirmar_exclusao.html",
        {
            "operacao": operacao
        }
    )


def marcar_entregue(request, pk):
    operacao = get_object_or_404(
        Operacao,
        pk=pk,
        ativo=True
    )

    if request.method == "POST":
        operacao.status_operacao = "Entregue"
        operacao.data_entrega = timezone.now()
        operacao.save()

    return redirect("lista_operacoes")

def codigo_barras(request, pk):
    operacao = get_object_or_404(
        Operacao,
        pk=pk,
        ativo=True
    )

    buffer = BytesIO()

    codigo = Code128(
        operacao.codigo,
        writer=SVGWriter()
    )

    codigo.write(
        buffer,
        options={
            "write_text": True,
            "module_height": 15.0,
            "font_size": 10,
            "text_distance": 5,
        }
    )

    return HttpResponse(
        buffer.getvalue(),
        content_type="image/svg+xml"
    )

def consulta_rapida(request):
    termo = request.GET.get("q", "").strip()
    operacao = None
    mensagem = None

    if termo:
        operacao = (
            Operacao.objects
            .filter(ativo=True)
            .filter(
                Q(codigo__iexact=termo)
                | Q(numero_nota__iexact=termo)
            )
            .first()
        )

        if not operacao:
            mensagem = "Nenhuma operação encontrada."

    return render(
        request,
        "operacoes/consulta_rapida.html",
        {
            "operacao": operacao,
            "termo": termo,
            "mensagem": mensagem,
        }
    )
def qr_code(request, pk):
    operacao = get_object_or_404(
        Operacao,
        pk=pk,
        ativo=True
    )

    buffer = BytesIO()

    qr = qrcode.make(operacao.codigo)
    qr.save(buffer, format="PNG")

    return HttpResponse(
        buffer.getvalue(),
        content_type="image/png"
    )