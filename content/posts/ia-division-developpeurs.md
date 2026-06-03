---
title: "L'IA ne remplace pas les développeurs — elle dissout ce qui les unissait"
heroTitle: "L'IA et la [division silencieuse] des équipes"
date: 2026-06-03
draft: false
description: "Le vrai risque de l'IA n'est pas de remplacer les développeurs, mais de dissoudre ce qui nous forçait à collaborer. Anatomie d'une division silencieuse."
categories: ["Métier"]
tags: ["IA générative", "Collaboration", "Équipes", "Culture tech", "Gabon", "Développement"]
author: "BANGA Romaric"
slug: "ia-division-developpeurs"
showToc: false
cover:
    image: "/images/ia-division-developpeurs-cover.jpg"
    alt: "Deux développeurs africains se faisant face à un bureau partagé scindé par une ligne, l'IA circulant entre leurs écrans sous forme de réseau neuronal et de circuits — la division silencieuse des équipes, BANGA Romaric"
    caption: "« L'IA ne te remplace pas. Un collègue le fera. » — la division silencieuse, en une image"
---

Lundi matin, Libreville. L'open-space est encore à moitié vide, la clim met du temps à rafraîchir la pièce, et Ndong ouvre le dépôt du projet avant même d'avoir touché à son café. Le sprint prévoyait qu'il construise trois endpoints cette semaine. Sa zone à lui, le backend, son métier depuis sept ans. Ils sont déjà là. Commités pendant le week-end. Signés Mavoungou, le référent frontend de l'équipe. Avec l'IA.

Ndong n'est pas en colère contre Mavoungou. Le code est correct, ça compile, ça passe les tests. Ce qui le dérange, il n'arrive pas tout de suite à le nommer. C'est une question sourde qui s'installe : *suis-je encore nécessaire sur ce projet ?*

Cette scène, je l'ai vue se rejouer dans plusieurs équipes ici, et je l'entends raconter ailleurs dans l'écosystème francophone. On la résume toujours de la même façon : « l'IA va remplacer les développeurs. » C'est faux. Ce qui se passe vraiment est plus discret, et franchement plus intéressant.

## § I — Le vrai mécanisme

L'IA n'a pas supprimé des postes. **Elle a supprimé l'interdépendance qui nous obligeait à collaborer.**

Avant, sur un projet, collaborer n'était pas seulement une vertu. C'était une nécessité de structure. Ndong le backend avait besoin de Mavoungou le frontend, et l'inverse était vrai aussi. Aucun des deux ne pouvait couvrir le terrain de l'autre. Cette dépendance fabriquait de la coopération presque mécaniquement : des échanges quotidiens, du transfert de connaissances, une forme de solidarité qu'on finissait par prendre pour acquise.

L'IA dissout cette nécessité. Et en la dissolvant, elle met au jour quelque chose d'inconfortable. Une bonne partie de ce qu'on appelait « esprit d'équipe » n'était parfois qu'une dépendance technique déguisée en fraternité.

Les équipes qui resteront soudées après l'IA, c'est qu'elles l'étaient déjà pour de vrai. Celles qui se fragmentent n'étaient peut-être tenues que par le besoin qu'on avait les uns des autres.

## § II — La division silencieuse

C'est ici que se loge le risque que beaucoup nomment mal.

Le danger, ce n'est pas la machine qui remplace l'humain. C'est plus sournois que ça :

> L'IA ne te remplace pas directement. Elle donne à un collègue, ou à un chef qui code, de quoi justifier que tu n'es plus indispensable.

« Pourquoi garder cette personne sur le projet si je peux produire 80 % de son travail avec l'IA ? »

La question a l'air rationnelle. Elle ne l'est qu'en surface. Mais elle suffit à enclencher un glissement. On passe d'une culture du « comment on réussit ensemble ? » à une culture du « comment je prouve que je peux réussir seul ? ».

C'est ça, la division. Il n'y a pas de licenciement brutal, juste une recomposition silencieuse des rapports, où la complémentarité d'hier se transforme en concurrence larvée. Mavoungou n'a rien décidé de méchant. Il a juste découvert qu'il pouvait le faire seul. Et sans que personne ne le dise à voix haute, ce « je peux » a commencé à ressembler à « il ne sert plus à grand-chose ».

## § III — Le piège des 20 %

C'est l'angle que la plupart des discussions ratent.

Les 80 % que l'IA te permet de sortir ont l'air complets. Ça compile, ça tourne, ça ressemble au travail d'un expert. Mais les 20 % qui manquent, c'est exactement là que vit l'expertise réelle :

- les cas limites que personne n'avait vus venir ;
- les décisions d'architecture qu'on paie trois ans plus tard ;
- la connaissance du métier : pourquoi le client Airtel et le client Moov n'ont pas la même logique de réconciliation ;
- et surtout, savoir **quand l'IA se trompe**.

Celui qui met son collègue de côté ne voit pas ces 20 %, justement parce que les 80 % visibles sont convaincants. À court terme, le remplacement a l'air rationnel. À long terme, il se paie en dette technique. Le genre de dette qui n'apparaît jamais sur le tableau de bord du sprint, et qu'on finit toujours par rembourser en production, un samedi soir, quand le système lâche et que c'est toi qu'on appelle.

Ces 20 %, ce n'est pas un vœu pieux. Ça a un nom et des outils, et c'est tout l'objet de [Dompter l'IA générative avec DDD, Hexagonal & Spring Modulith]({{< ref "/posts/architecture-ia-spring-modulith" >}}), où l'expertise devient exécutable : un `NumeroTelephoneGabonais` qui refuse de se construire invalide, des tests ArchUnit qui **cassent le build** dès que l'IA glisse un `@Service` dans le domaine. La logique de réconciliation Airtel/Moov, c'est précisément le genre de règle qu'on modélise à la main dans un projet comme [MboloPay]({{< ref "/projects/mbolopay" >}}). Pas le genre de chose qu'on devine au prompt.

L'IA produit du code qui a l'air fini. Elle ne produit pas le jugement qui sait reconnaître ce qui ne l'est pas.

## § IV — Une nuance honnête

Soyons justes : ce phénomène n'a pas été inventé par l'IA.

La rivalité entre profils, la substituabilité, les jeux de pouvoir dans les équipes, tout ça existait bien avant le premier prompt. La même dynamique frappe les infographes, les communicants, tous ceux dont on s'imagine pouvoir « faire 80 % du boulot » sans eux. L'IA n'a rien inventé. **Elle a juste baissé le coût d'entrée de la tentation.** Ce qui demandait avant un vrai effort se déclenche maintenant d'un clic.

Et la même force peut très bien jouer dans l'autre sens. Une fois libérés de l'interdépendance purement mécanique, celle où l'on s'attendait juste pour se passer des fichiers, Ndong et Mavoungou pourraient enfin collaborer sur les vrais problèmes : l'architecture, la sécurité, la compréhension du besoin réel des utilisateurs gabonais.

Le résultat n'est pas une fatalité technologique. C'est un **choix d'organisation**.

## § V — Reconstruire sur autre chose que le besoin

Si l'IA dissout la collaboration imposée par la dépendance, alors la seule qui survivra, c'est celle qu'on choisit pour de bon.

C'est une bonne nouvelle déguisée en menace. Une équipe qui ne tient que parce que ses membres ne peuvent pas se passer les uns des autres, ce n'est pas vraiment une équipe. C'est un attelage. En revanche, des gens qui décident de réfléchir ensemble alors que chacun pourrait techniquement avancer seul dans son coin, ça, c'est une culture.

À l'ère des agents, la valeur d'un développeur ne se mesure plus à ce qu'il est le seul à savoir taper. Elle se mesure à son jugement, à sa lecture du métier, à sa capacité de dire à un collègue : « ton 80 % est bon, mais voilà les 20 % qui vont nous coûter cher. » Ça, aucune IA ne le dira à la place de Mavoungou. Et c'est exactement ce que Ndong peut encore apporter, à condition qu'on ne l'ait pas poussé dehors avant.

## § VI — La vraie question

On répète partout la même chose : « est-ce que l'IA va remplacer les développeurs ? » La question est usée, et un peu paresseuse.

La vraie question, celle qui décidera de l'avenir de nos équipes, à Libreville comme à Douala ou à Dakar, est ailleurs :

**L'IA va-t-elle détruire la base réelle de notre collaboration, ou nous forcer à la reconstruire sur autre chose que la simple dépendance technique ?**

La réponse ne dépend pas de la machine. Elle dépend de nous, et de ce que les Ndong et les Mavoungou de nos projets décideront de faire de ce nouveau pouvoir.

*Et dans votre équipe, l'IA vous rapproche-t-elle, ou commence-t-elle déjà, en silence, à vous diviser ?*

---

## Accompagner son équipe face à l'IA

La bonne nouvelle de cet essai (« la seule collaboration qui survivra est celle qu'on choisit ») ne se décrète pas, elle s'outille. C'est concrètement ce que je fais avec les équipes, ici au Gabon et ailleurs en zone francophone :

- 🎓 **Formation entreprise** — structurer le code généré par l'IA (DDD, hexagonal, tests d'architecture) pour que les « 20 % » restent visibles, même quand l'IA produit les 80 % en un clic. [Voir les formats →](/about/#services)
- 🧭 **Consulting & audit** — recomposer une organisation où l'IA libère du temps pour l'architecture et le métier, au lieu de fragmenter l'équipe. [Discutons d'un projet](mailto:bangaromaric@gmail.com)
- 📖 **Aller plus loin** — [Dompter l'IA générative avec DDD, Hexagonal & Spring Modulith]({{< ref "/posts/architecture-ia-spring-modulith" >}}), le pendant technique de cet essai.
- 🗂️ **Cas concret** — [MboloPay]({{< ref "/projects/mbolopay" >}}), où la logique métier Airtel/Moov est modélisée à la main, pas devinée par l'IA.
