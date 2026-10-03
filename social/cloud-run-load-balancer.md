# Posts de promotion : « Cloud Run derrière un load balancer global »

**Article complet (cible) :** https://ban.ga/posts/cloud-run-load-balancer/
**Image de couverture (OG 1200×630) :** https://ban.ga/images/cloud-run-load-balancer-cover.png

> Ce fichier vit hors de `content/` : Hugo ne le construit pas en page publiée. C'est un dossier de brouillons sociaux, à copier-coller vers chaque plateforme.

---

## 1. LinkedIn

> **Mode d'emploi.** Colle le texte ci-dessous tel quel, lien compris : il est en fin de post, hors de la zone lue avant la coupe « voir plus ». L'aperçu affichera automatiquement la cover de l'article (`og:image`). Si tu préfères téléverser l'image à la main, pense au bouton **Alt** de LinkedIn et reprends le texte alternatif donné plus bas. Colle le premier commentaire juste après publication, pas une heure plus tard.

<!-- post:linkedin -->
Ligne 14 du questionnaire de sécurité d'un partenaire : « TLS 1.0 et 1.1 doivent être désactivés. »

Le réglage n'existe pas dans Cloud Run.

Avec un domain mapping, on prend ce que Google donne : TLS 1.0 accepté, un certificat par sous-domaine, aucun wildcard. Et la doc est explicite, la fonctionnalité est en Preview, déconseillée en production.

La sortie, c'est un global external Application Load Balancer devant Cloud Run. Je l'ai fait pour mes propres services, en partant d'un niveau honnêtement novice : un certificat perdu sur une faute de frappe, un domaine coupé quelques minutes en touchant au DNS. Ce que j'aurais aimé savoir avant :

• Le certificat d'abord, le DNS ensuite. L'autorisation DNS, un simple CNAME _acme-challenge dans ta zone, fait émettre un certificat wildcard actif avant que le trafic ait bougé d'un octet. L'autre méthode impose de basculer le DNS en premier, et ignore les wildcards.

• Le champ rouge « Certificate map is required » n'est pas un bug. Un load balancer global ne référence pas un certificat, mais une certificate map : le trousseau qui dit quel certificat présenter pour quel nom d'hôte.

• Le formulaire de backend qui fait peur se vide tout seul. Instance group, named port, health check : rien de tout ça ne te concerne. Passe Backend type en Serverless NEG, la moitié des champs disparaît, Cloud Run gérant lui-même la santé de ses instances.

• Sans politique SSL attachée, le load balancer accepte encore TLS 1.0. Par défaut, et sans le dire. Une politique Modern en TLS 1.2 minimum se crée en trois champs, ne coûte rien, et se durcit plus tard sans couper les connexions ouvertes.

• Tant que l'URL run.app reste joignable depuis Internet, n'importe qui contourne le load balancer, donc la politique TLS. L'ingress passe en interne plus load balancers, après la suppression du domain mapping, jamais avant.

Et celle qui pique : un CNAME et un enregistrement A ne cohabitent pas sur le même nom. La bascule laisse donc un trou, et quelques minutes suffisent pour qu'un résolveur mémorise « ce domaine n'existe pas » et le répète longtemps après la réparation. Baisse le TTL la veille.

Le prix de tout ça : environ 18 $ par mois de coût fixe, contre 0 $ en domain mapping. Pour un prototype sans vrais utilisateurs, ça ne vaut pas le coup. Pour une API qui doit passer un audit, c'est le ticket d'entrée, et il ne bouge pas quand tu ajoutes une deuxième application derrière.

Et toi, tes services Cloud Run sont exposés comment aujourd'hui ?

Le carnet de bord complet, écran par écran, commandes de test et coûts détaillés : https://ban.ga/posts/cloud-run-load-balancer/

#GoogleCloud #CloudRun #DevOps #AfricaTech
<!-- /post -->

**Texte alternatif de l'image** (bouton « Alt » de LinkedIn, si tu téléverses la cover à la main) :

`Architecture Google Cloud : du visiteur à Cloud Run en passant par la zone DNS LWS et le load balancer global, sa certificate map wildcard et sa politique TLS 1.2.`

---

**Premier commentaire (à coller juste après publication) :**

<!-- post:linkedin:commentaire -->
L'épisode précédent de la même série, pour la partie déploiement : « Spring Native + Cloud Run, cold-start ÷18, RAM ÷3 ». C'est le service que ce load balancer vient exposer. https://ban.ga/posts/spring-native-cloud-run/
<!-- /post -->

**Variante « lien en premier commentaire »** (si tu préfères un post sans URL) : retire du post la ligne « Le carnet de bord complet… » et sa phrase de lien, puis commence le premier commentaire par :

`Le carnet de bord complet, écran par écran : https://ban.ga/posts/cloud-run-load-balancer/`

---
---

## 2. Facebook

> **Mode d'emploi.** Destination : **profil personnel**, registre « je ». Publie le texte ci-dessous avec le lien dans le corps : Facebook construira l'aperçu tout seul depuis les balises Open Graph de l'article, cover comprise. **Avant** de publier, passe l'URL dans le [Sharing Debugger](https://developers.facebook.com/tools/debug/) puis clique sur « Scrape Again » : Meta ne relit une page qu'une fois par 24 h et garde l'image en cache par URL. Un aperçu raté ne se corrige plus après publication.

<!-- post:facebook -->
Récemment, j'ai coupé un de mes sites pendant plusieurs minutes. Tout seul, un soir, en modifiant une ligne de configuration. 😅

Je migrais mes services vers une autre façon de les exposer sur Internet, un sujet où je partais honnêtement de zéro. J'y ai laissé un certificat sur une faute de frappe, et compris pourquoi un domaine peut rester introuvable longtemps après la réparation.

Ce que je cherchais à monter porte un nom qui fait peur, un load balancer. En vrai, c'est le marché Mont-Bouët. Au lieu que chaque boutique ait sa porte sur la rue, son gardien et son cadenas, on a une seule grande entrée, un seul gardien, qui sait dans quelle allée se trouve chaque commerçant.

C'est exactement ce qu'on vous réclame le jour où un partenaire vous envoie son questionnaire de sécurité.

J'ai tout écrit, écran par écran, pour quelqu'un qui part de zéro : https://ban.ga/posts/cloud-run-load-balancer/

Si ça intéresse du monde, on en fera un atelier au GDG Libreville.

#GoogleCloud #Gabon
<!-- /post -->
