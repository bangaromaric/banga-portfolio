---
title: ""
heroTitle: ""
date: {{ .Date | time.Format "2006-01-02" }}
description: ""
tags: []
categories: [""]
draft: true
cover:
    image: "/images/{{ .File.ContentBaseName }}-cover.png"
    alt: ""
    caption: ""
---

{{/*
  Pas de showToc dans ce gabarit, et c'est voulu.

  Le sommaire est automatique : layouts/partials/post-toc.html l'affiche des que
  l'article atteint six titres de niveau 2. Ne rien ecrire est donc la bonne
  valeur par defaut, et la seule qui ne puisse pas etre oubliee.

  showToc: true  force le sommaire sous le seuil, pour un article court mais
                 dense en sections.
  showToc: false l'interdit. Le linter editorial le refuse au-dela de 1 500 mots
                 (.claude/skills/seo-article/scripts/audit_article.py).

  Rappels de mise en forme, detailles dans le skill article-tech :
    title       50 a 95 caracteres, sans crochets
    heroTitle   18 a 50, exactement un [fragment] entre crochets
    description 120 a 185, cible 140 a 165
    categories  une seule : Architecture, Backend, Communaute, Metier ou IA
    tags        4 a 8, dont au moins deux partages avec un article existant
    cover       1200x630, moins de 300 Ko, alt termine par la signature
    pas de tiret cadratin en prose
*/}}
