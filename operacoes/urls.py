from django.urls import path

from . import views

urlpatterns = [
    path("", views.lista_operacoes, name="lista_operacoes"),
    path("nova/", views.criar_operacao, name="criar_operacao"),
    path("editar/<int:pk>/", views.editar_operacao, name="editar_operacao"),
    path("excluir/<int:pk>/", views.excluir_operacao, name="excluir_operacao"),
    path(
        "marcar-entregue/<int:pk>/",
        views.marcar_entregue,
        name="marcar_entregue",
    ),
]