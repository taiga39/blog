#!/bin/bash
cd "$(dirname "$0")"

claude -p "Notionの英語日記ページ(https://www.notion.so/30d8f7ca77b080aba3f2fc16e067d5cc)を読んで、✅がついていないエントリだけブログ記事として作成してコミットしてください。プッシュはしないでください。何もなければ何もしないでください。"
