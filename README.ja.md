# wagtail-simple-forum

**Wagtail 統合型のディスカッションフォーラムを追加します。カテゴリ、セクション、トピック、投稿、モデレーション、プライベートメッセージ、通知、検索、旧フォーラムアプリからの移行ツールを備えます。**

[English](README.md) · [Русский](README.ru.md) · [Deutsch](README.de.md) · [Español](README.es.md) · [Français](README.fr.md) · [Italiano](README.it.md) · [Português (Brasil)](README.pt-BR.md) · [Nederlands](README.nl.md) · [Polski](README.pl.md) · [Türkçe](README.tr.md) · [简体中文](README.zh-CN.md) · [日本語](README.ja.md) · [한국어](README.ko.md)

## 主な機能

- カテゴリ → セクション → トピック → 投稿の階層とアクティビティ集計。
- プライベートメッセージの受信箱とスレッド会話。
- ゲスト向けスパム対策、モデレーション、検索、レート制限。
- 旧フォーラムのインポートとリダイレクト。切替前に dry-run を検証。

## 要件と互換性

- 宣言されている依存関係: `Wagtail >= 6.0; django-prose-editor >= 0.26; nh3 >= 0.2.14`.
- Python、Django、Wagtail の互換性は組み合わせて確認してください。最低依存バージョンは全バージョンのサポートを意味しません。

パッケージのメタデータでは Wagtail >= 6.0 を宣言していますが、最小依存バージョンは全バージョンでの互換性を保証しません。このアーカイブには、すべての Django/Wagtail 組み合わせを網羅する自動テストマトリクスはありません。本番環境を更新する前に、正確なバージョン、データベース、ストレージバックエンド、デプロイ設定をステージングで確認してください。

## インストール

Wagtail プロジェクトと同じ仮想環境にパッケージをインストールします。

```bash
pip install wagtail-simple-forum
```

プロジェクトで必要な他の依存関係を維持しながら、次の順序でアプリを追加します。

```python
INSTALLED_APPS = [
    # プロジェクトで必要な他の Django/Wagtail 依存関係も維持してください。
    "django_prose_editor",
    "wagtail_simple_forum",
]
```

フォーラムの URL は **Wagtail の catch-all route より前**に追加します。旧 URL のリダイレクトも前に置いてください。

```python
from django.urls import include, path
from wagtail_simple_forum.legacy_urls import urlpatterns as legacy_forum_urls
urlpatterns = [
    path("forum/", include("wagtail_simple_forum.urls")),
    *legacy_forum_urls,
    # 旧ルートは Wagtail の catch-all ルートより前に配置します。
]
```

`python manage.py migrate wagtail_simple_forum` を実行します。旧 `forum` アプリから移行する場合、まず `python manage.py forum_import_from_app --source forum --dry-run` を実行します。.


## 初期設定

以下は最小の開始例です。モデル名、API フィールド、URL は実際の構成に合わせてください。

```python
from django.urls import include, path
from wagtail_simple_forum.legacy_urls import urlpatterns as legacy_forum_urls

urlpatterns = [
    path("forum/", include("wagtail_simple_forum.urls")),
    *legacy_forum_urls,  # 旧ルートは Wagtail の catch-all ルートより前に配置します。
]
```

`python manage.py migrate wagtail_simple_forum` を実行します。旧 `forum` アプリから移行する場合、まず `python manage.py forum_import_from_app --source forum --dry-run` を実行します。

旧フォーラムの取り込み前にデータベースをバックアップし、`--dry-run` を実行してください。移行と確認が終わるまで旧アプリを残してください。


## 重要な設定と動作

このディレクトリの英語 README が正式な基準ドキュメントで、設定表と詳細例をすべて含みます。この翻訳では実際の導入手順と重要な安全上の注意を説明します。高度な設定を変更する前に英語版を確認してください。

設定の完全な一覧は[英語 README](README.md)を参照してください。

### 重要な注意事項

フォーラム URL と旧 URL のリダイレクトは Wagtail の catch-all より前に配置します。旧フォーラムを取り込む前に DB をバックアップし、最初に `--dry-run` を実行してください。

## セキュリティと運用

- 依存関係を最新に保ってください。ユーザー作成 HTML には定められたサニタイズ/レンダリング経路を使い、保存済みコメントやフォーラム投稿を無条件に `|safe` で表示しないでください。
- 通常ユーザー、制限ユーザー、モデレーター、管理者でマイグレーションと権限を確認してください。
- マルチサイト環境では、設定済みのすべてのホストと未設定のホストをテストしてください。Site を特定できない場合、全サイトのレコードに検索範囲を拡張してはいけません。
- API トークン、SMTP 認証情報、非公開 URL は秘密情報として扱ってください。Git にコミットしたり、公開の不具合報告に含めたりしないでください。
- マイグレーション、大量移動、インポート、初回の一括公開の前に、データベースとメディアファイルをバックアップし、まずステージングで実行してください。

## 推奨構成

- `wagtail-mptt-comments` は記事コメントを補完します。Prose 画像選択は独自フィールドで必要な場合のみ使用します。
- 画像ディレクトリはフォーラムデータと独立しています。

## 確認チェックリスト

- [ ] ステージングに候補版を導入し、Python、Django、Wagtail、DB の各バージョンを記録する。
- [ ] `python manage.py check` とパッケージのマイグレーションを実行する。
- [ ] 通常ユーザーと制限ユーザーで主要な操作を試す。
- [ ] ログ、アクセス制御、キャッシュ、バックアップ、復元を確認する。

このアーカイブは静的な構文・パッケージチェックに合格していますが、この環境では Django/Wagtail の完全な実行時統合テストを行っていません。以下の項目は全組み合わせのテスト済みという意味ではなく、リリース前の必須確認事項です。

## トラブルシューティング

動作しない場合は、アプリ設定、マイグレーション、URL の順序、ユーザー権限、Django ログを確認してください。パッケージ版と例を英語 README と照合してください。

## ライセンスとサポート

MIT. ソースコード: [https://github.com/vovansrnd/wagtail-simple-forum](https://github.com/vovansrnd/wagtail-simple-forum).

