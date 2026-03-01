# Blog

Python製の静的ブログジェネレーター。依存ライブラリなし。

## Build

```
python build.py
```

`posts/*.md` → `docs/*.html` に変換される。

## 記事の追加

`posts/` にマークダウンファイルを作成する。frontmatter は以下の形式:

```
---
title: タイトル
date: YYYY-MM-DD
excerpt: 概要
---
```

### 記事作成ルール

- ユーザーから文章を受け取ったら、一文目をそのまま `title` に使う
- 本文の冒頭にも同じ一文目を含める（タイトル兼一文目）
- `date` は指示がなければ今日の日付
- `excerpt` は本文から適切に要約して作成
- ファイル名は内容から英語のスラッグを付ける
- 作成後はコミットする（push はしない）

## デプロイ

GitHub Actions が自動でビルド＆デプロイする。ローカルで `python build.py` を実行する必要はない。

- push 時: `posts/` または `build.py` に変更があれば自動ビルド
- 毎日 JST 9:00: cron で自動ビルド（スケジュール投稿用）
- 未来日の記事はビルド時にスキップされ、日付が来たら自動公開

## 構成

- `build.py` - ビルドスクリプト（Markdownパーサー＋テンプレート＋SPA navigation）
- `posts/` - マークダウン記事
- `docs/` - ビルド出力（GitHub Pages用）

## SPA navigation

vanilla JSでページ遷移をfetch+DOM差し替えで実現。フェードアニメーション付き。ライブラリ不使用。
