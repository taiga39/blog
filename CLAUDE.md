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

## 重要

記事の追加・変更後は必ず `python build.py` を実行すること。

## 構成

- `build.py` - ビルドスクリプト（Markdownパーサー＋テンプレート＋SPA navigation）
- `posts/` - マークダウン記事
- `docs/` - ビルド出力（GitHub Pages用）

## SPA navigation

vanilla JSでページ遷移をfetch+DOM差し替えで実現。フェードアニメーション付き。ライブラリ不使用。
