# wagtail-simple-forum

**Adiciona um fórum integrado ao Wagtail com categorias, seções, tópicos, posts, moderação, mensagens privadas, notificações, busca e ferramentas para importar um aplicativo de fórum antigo.**

[English](README.md) · [Русский](README.ru.md) · [Deutsch](README.de.md) · [Español](README.es.md) · [Français](README.fr.md) · [Italiano](README.it.md) · [Português (Brasil)](README.pt-BR.md) · [Nederlands](README.nl.md) · [Polski](README.pl.md) · [Türkçe](README.tr.md) · [简体中文](README.zh-CN.md) · [日本語](README.ja.md) · [한국어](README.ko.md)

## Principais recursos

- Hierarquia categoria → seção → tópico → post com contadores de atividade.
- Caixa de entrada de mensagens privadas e conversas encadeadas.
- Antispam para visitantes, moderação, busca e limitação de frequência.
- Ferramentas de importação e redirecionamento legado; valide o dry-run antes da mudança.

## Requisitos e compatibilidade

- Dependências declaradas: `Wagtail >= 6.0; django-prose-editor >= 0.26; nh3 >= 0.2.14`.
- A compatibilidade entre Python, Django e Wagtail deve ser verificada em conjunto. A dependência mínima do pacote não confirma suporte a todas as versões.

Os metadados declaram Wagtail >= 6.0, mas uma dependência mínima não comprova compatibilidade. Este arquivo não inclui uma matriz automatizada completa para todas as combinações de Django/Wagtail. Antes de atualizar produção, teste as versões exatas, o banco de dados, o armazenamento e as configurações de implantação em staging.

## Instalação

Instale o pacote no mesmo ambiente virtual do seu projeto Wagtail:

```bash
pip install wagtail-simple-forum
```

Adicione os apps nesta ordem, mantendo as demais dependências do projeto:

```python
INSTALLED_APPS = [
    # Preserve também as outras dependências Django/Wagtail já necessárias.
    "django_prose_editor",
    "wagtail_simple_forum",
]
```

Inclua as URLs do fórum **antes da rota catch-all do Wagtail**. Os redirecionamentos antigos também devem vir antes.

```python
from django.urls import include, path
from wagtail_simple_forum.legacy_urls import urlpatterns as legacy_forum_urls
urlpatterns = [
    path("forum/", include("wagtail_simple_forum.urls")),
    *legacy_forum_urls,
    # As rotas legadas devem vir antes da rota catch-all do Wagtail.
]
```

Execute `python manage.py migrate wagtail_simple_forum`.


## Configuração inicial

Exemplo mínimo para começar. Adapte nomes de modelos, campos da API e URLs à sua configuração.

```python
from django.urls import include, path
from wagtail_simple_forum.legacy_urls import urlpatterns as legacy_forum_urls

urlpatterns = [
    path("forum/", include("wagtail_simple_forum.urls")),
    *legacy_forum_urls,  # As rotas legadas devem vir antes da rota catch-all do Wagtail.
]
```

Execute `python manage.py migrate wagtail_simple_forum`. Para um antigo app `forum`, execute primeiro `python manage.py forum_import_from_app --source forum --dry-run`.

Antes de importar o fórum antigo, faça backup e execute `--dry-run`. Mantenha o app antigo instalado até concluir a importação e as verificações.


## Configurações e comportamento importantes

O README em inglês deste diretório é a referência canônica e contém as tabelas completas de opções e exemplos detalhados. Esta tradução cobre a configuração prática e os avisos essenciais de segurança; consulte a referência em inglês antes de alterar opções avançadas.

Consulte o [README em inglês](README.md) para a referência completa das configurações.

### Observações importantes

As URLs do fórum e os redirecionamentos antigos devem vir antes da rota catch-all do Wagtail. Antes de importar o fórum antigo, faça backup e execute primeiro `--dry-run`.

## Segurança e operação

- Mantenha as dependências atualizadas. Para HTML escrito por usuários, use o fluxo previsto de sanitização e renderização; não exiba comentários ou posts armazenados com `|safe` incondicional.
- Verifique migrações e permissões com usuários comuns, restritos, moderadores e administradores.
- Em instalações multissite, teste cada domínio configurado e um host desconhecido. Se nenhum Site for encontrado, a consulta não deve abranger registros de todos os sites.
- Trate tokens de API, credenciais SMTP e URLs privadas como segredos. Não os envie ao Git nem os inclua em relatórios públicos.
- Faça backup do banco de dados e dos arquivos de mídia antes de migrações, movimentações em lote, importações ou da primeira publicação em massa. Teste primeiro em staging.

## Combinações recomendadas

- `wagtail-mptt-comments` complementa o fórum com comentários em artigos; o seletor Prose só é útil em campos personalizados.
- Diretórios de imagens são independentes dos dados do fórum.

## Lista de verificação

- [ ] Instale a versão candidata em staging e registre as versões de Python, Django, Wagtail e banco de dados.
- [ ] Execute `python manage.py check` e as migrações do pacote.
- [ ] Teste o fluxo principal com usuário comum e usuário restrito.
- [ ] Confira logs, acesso, cache, backups e restauração.

O arquivo passou pelas verificações estáticas de sintaxe e empacotamento, mas a integração completa com Django/Wagtail não foi executada neste ambiente. Trate a lista abaixo como requisito para o lançamento, não como prova de que todas as combinações foram testadas.

## Solução de problemas

Se o fluxo não funcionar, confira a configuração do app, migrações, ordem das URLs, permissões e logs do Django. Compare a versão e o exemplo com o README em inglês.

## Licença e suporte

MIT. Código-fonte: [https://github.com/vovansrnd/wagtail-simple-forum](https://github.com/vovansrnd/wagtail-simple-forum).

