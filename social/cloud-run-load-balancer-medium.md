# Post Medium : « Cloud Run derrière un load balancer global »

**Article cible (hub) :** https://ban.ga/posts/cloud-run-load-balancer/
**Cover à téléverser :** `static/images/cloud-run-load-balancer-cover.png` (1200×630)
**Pour coller avec la mise en forme :** ouvrir `social/cloud-run-load-balancer-medium.html`
dans le navigateur et utiliser ses boutons. Medium ignore le Markdown collé mais interprète
le HTML du presse-papier : les titres, le gras, les listes et les liens arrivent déjà en forme.
Ce fichier `.md` reste la source de vérité du texte ; si le texte change, régénérer le `.html`.

> Fichier hors de `content/` : Hugo ne le construit pas. Il n'utilise pas les marqueurs
> `<!-- post:... -->` de `promo-sociale`, Medium n'étant pas une plateforme reconnue par
> `audit_post_social.py`. Tout ce qui se colle est délimité par un titre `## À COPIER`.

---

## Règles de publication (à lire une fois, avant de coller)

1. **Ne pas importer l'article de ban.ga.** Le texte ci-dessous est une synthèse originale,
   pas une reprise. Medium a une autorité de domaine très supérieure à ban.ga : une copie
   intégrale ferait classer la version Medium et enterrer l'originale (§7 du CLAUDE.md).
2. **Donc pas de canonical.** Le canonical Medium vers ban.ga ne se justifie que pour une
   republication à l'identique. Ici, deux textes différents, deux pages légitimes, et
   trois liens qui pointent vers le hub.
3. **Ne pas coller le Markdown ci-dessous.** Medium ignore `##` et `**` au collage, mais
   interprète le HTML du presse-papier. Passer par `cloud-run-load-balancer-medium.html` :
   un clic par bloc, et la mise en forme arrive intacte. Le Markdown ci-dessous n'est que
   la version lisible en revue.
4. **Publier seulement après le déploiement de l'article.** Un 404 scrapé une fois reste
   en cache plusieurs jours.
5. **Ordre conseillé :** ban.ga en ligne, puis LinkedIn, puis Medium 24 à 48 h plus tard.
   Les deux textes ne disent pas la même chose, ils ne se cannibalisent pas.

---

## À COPIER : titre

Cloud Run, TLS 1.0, et la ligne 14 du questionnaire de sécurité

**Variantes** (si le premier ne te plaît pas) :

- Ce que Cloud Run ne sait pas faire, et le soir où je l'ai découvert
- Mettre un load balancer global devant Cloud Run : les cinq pièges qui coûtent cher

---

## À COPIER : sous-titre

Pourquoi les domain mappings ne tiennent pas en production, et ce que personne ne te dit avant que tu touches au DNS un vendredi soir.

---

## À COPIER : SEO Title

> Où : dans l'éditeur, menu `...` en haut à droite → **Story settings** (ou **More settings**)
> → onglet **SEO**, champ *SEO title*. Medium reprend le titre de la story si on le laisse
> vide : ici on le remplit exprès, pour ne pas concurrencer le titre SEO de ban.ga, qui est
> « Cloud Run derrière un load balancer global : certificat wildcard, pas à pas | Gabon ».
> Deux pages du même auteur sur la même requête se font du tort. Angle différent, donc.

Cloud Run : sortir des domain mappings sans coupure

**Variante** (si tu veux le mot-clé TLS dans le titre) :

Cloud Run et TLS 1.0 : passer à un load balancer global

---

## À COPIER : SEO Description

> Même écran, champ *SEO description*. 150 à 160 caractères : au-delà, Google tronque.
> Elle doit contenir le mot-clé principal et une promesse concrète, pas un résumé du récit.

Les domain mappings Cloud Run ne tiennent pas en production. Passer à un load balancer global : certificat wildcard, TLS 1.2, bascule DNS sans coupure.

**Variante** (si tu veux viser la requête « certificat wildcard Cloud Run ») :

Certificat wildcard, TLS 1.2 et serverless NEG devant Cloud Run : les cinq pièges d'une migration depuis les domain mappings, et ce qu'elle coûte par mois.

---

## À COPIER : légende de la cover

Zone DNS, load balancer global, certificat wildcard, serverless NEG, puis Cloud Run. Schéma : Romaric BANGA.

## À COPIER : texte alternatif de la cover

Architecture Google Cloud : du visiteur à Cloud Run en passant par la zone DNS, le load balancer global, sa certificate map wildcard et sa politique TLS 1.2.

---

## À COPIER : corps du post

> Les lignes marquées `(titre)` sont à passer en titre de section dans Medium, puis le
> marqueur se supprime. Les amorces en gras sont les points d'ancrage du lecteur qui scanne.

Vendredi, 19 h 58. Une capture d'écran arrive sur WhatsApp : la console Google Cloud, l'assistant de création d'un load balancer, et un champ rouge. « Certificate map is required ». Suit un seul message : « c'est quoi ça encore ? »

Trois jours plus tôt, l'API tournait très bien sur Cloud Run, avec un domain mapping : un CNAME vers ghs.googlehosted.com chez le registrar, un clic dans la console, en ligne. Gratuit. Puis un partenaire a envoyé son questionnaire de sécurité. Ligne 14 : « les protocoles TLS 1.0 et 1.1 doivent être désactivés sur tous les points d'entrée exposés. »

Ce réglage n'existe pas dans Cloud Run. Et c'est écrit noir sur blanc dans la documentation : avec un domain mapping, on ne peut pas désactiver TLS 1.0 et 1.1.

C'est comme ça qu'on se retrouve, un vendredi soir, dans un assistant qu'on n'a jamais ouvert. J'y suis passé quelques semaines plus tôt pour mes propres services, en partant d'un niveau honnêtement novice. J'y ai laissé un certificat sur une faute de frappe, et coupé un domaine plusieurs minutes en touchant au DNS. Voici ce que j'aurais voulu lire avant.

(titre) Les domain mappings ne sont pas un choix d'architecture

Ils sont un point de départ, et la documentation est franche à ce sujet. Le statut est **Preview**, avec des problèmes de latence connus, et Google ne les recommande pas pour la production. Au-delà du statut, la liste des limitations décide à ta place :

**Pas de certificat wildcard.** Un certificat provisionné par sous-domaine, à chaque nouveau mapping.

**Pas de TLS configurable.** TLS 1.0 reste accepté, et aucun audit sérieux ne laisse passer ça.

**Pas de certificat personnel.** Tu prends celui de Google, point.

**Mapping sur la racine uniquement.** Impossible de router /api vers un service et / vers un autre.

**Dix régions seulement.** Hors de cette liste, pas de domain mapping du tout.

Il y a surtout ce que la liste ne dit pas : avec un domain mapping, chaque application est seule face à Internet. Pas de pare-feu applicatif, pas de CDN, aucun point d'observation commun.

L'image que j'utilise en formation, c'est le marché Mont-Bouët à Libreville. Chaque commerçant avec sa propre porte sur la rue, son gardien et son cadenas : ça tient à trois boutiques. À trente, c'est ingérable, et surtout il n'existe aucun moyen de fermer le marché d'un coup quand un voleur rôde. Le load balancer, c'est la grande entrée : une adresse, un gardien, un plan des allées.

(titre) Le choix qui rend la migration invisible : l'autorisation DNS

C'est la décision la plus importante de toute l'opération, et elle se prend avant même de créer le load balancer.

Pour obtenir un certificat géré par Google, il faut prouver que le domaine t'appartient. Certificate Manager propose deux méthodes, et elles n'ont rien d'équivalent.

**Load Balancer Authorization** : Google vérifie en passant par ton load balancer. Il faut donc que ton DNS pointe déjà dessus. Tu bascules le trafic, puis tu attends le certificat, et la documentation prévient qu'une migration de ce type peut causer une coupure. Accessoirement, pas de wildcard.

**DNS Authorization** : tu ajoutes un CNAME `_acme-challenge` dans ta zone, Google le lit, le certificat est émis. Ton trafic n'a pas bougé d'un octet. Wildcard accepté.

Pour une API de paiement, la première était exclue d'office. Une heure sans API, ce sont des transactions qui échouent.

L'analogie qui marche à tous les coups : c'est une carte de commerçant à la mairie. Première méthode, l'agent vient constater que ta boutique est ouverte, il faut donc l'avoir déjà ouverte. Seconde méthode, tu montres ton titre de propriété au guichet, et ta carte est prête pour le jour où tu lèves le rideau.

Détail qui fait gagner une demi-heure : pour un wildcard, l'autorisation DNS se pose sur le domaine parent. Le domaine nu et son wildcard partagent donc la même preuve, et un seul CNAME suffit pour les deux.

Détail qui en coûte beaucoup plus : les noms de domaine d'un certificat Google-managed sont **immuables**. Une lettre de travers dans le champ, et il faut supprimer le certificat, supprimer l'autorisation DNS associée, et tout recommencer. Relis deux fois avant de cliquer sur Create. Je l'ai appris en le payant.

(titre) Le champ rouge n'est pas un bug

Retour à « Certificate map is required ». Le certificat venait d'être créé, et la console refusait quand même de le laisser choisir.

La raison est dans la référence de l'API : un load balancer applicatif **global** ne référence pas un certificat Certificate Manager directement. Son proxy HTTPS pointe vers une certificate map. Le référencement direct existe, mais il est réservé aux load balancers régionaux et aux internes cross-region.

Une certificate map, c'est le trousseau du gardien : pour chaque nom d'hôte qui se présente, elle dit quel certificat montrer. Deux entrées ici, le wildcard et le domaine nu, pointant vers le même certificat. Deux minutes de travail, à condition de savoir que ça existe.

(titre) Le formulaire qui fait fuir se vide tout seul

L'écran suivant décourage beaucoup de monde. Create a backend service, et un mur de champs : Instance group, Named port, Health check, Balancing mode, Maximum backend utilization.

Aucun de ces champs ne te concerne. Ils servent aux machines virtuelles.

Passe **Backend type** de Instance group à **Serverless network endpoint group**, et la moitié du formulaire disparaît, health check compris : il n'est pas supporté pour ce type de backend, Cloud Run gérant lui-même la santé de ses instances. Un serverless NEG n'est rien d'autre qu'un pointeur : « derrière moi, tel service Cloud Run, dans telle région ».

Deux réglages méritent une pensée à cet écran, parce que la console les coche pour toi :

**Cloud CDN est coché par défaut**, en mode « Cache static content ». Sur une API, presque rien n'est cachable, et il suffirait d'un en-tête `Cache-Control: public` posé par erreur sur une route de compte pour qu'un solde personnel soit servi à quelqu'un d'autre. Décoche, et reviens plus tard en mode « Use origin settings », celui où c'est l'application qui décide.

**La politique Cloud Armor proposée se crée par backend.** À 5 $ par mois plus 1 $ par règle, mieux vaut une seule politique partagée entre toutes les applications, créée dans un second temps.

(titre) Le défaut silencieux qui annule tout le reste

Sans politique SSL attachée, un load balancer global se comporte comme avec le profil COMPATIBLE, et accepte **TLS 1.0**. Par défaut. Sans rien afficher.

C'est exactement ce que le questionnaire refusait. Toute la migration aurait été faite pour rien.

La politique tient en trois champs : profil Modern, version TLS minimale 1.2, et tant qu'à faire l'échange de clés post-quantique activé. Elle ne coûte rien, et la modifier plus tard ne coupe pas les connexions déjà ouvertes : on peut donc durcir sans fenêtre de maintenance. Si un audit exige TLS 1.3 minimum, c'est le profil Restricted qui devient obligatoire.

La preuve se fournit en deux commandes `openssl`, une qui doit échouer en TLS 1.1, une qui doit réussir en TLS 1.2, plus un rapport SSL Labs en pièce jointe. Les commandes exactes sont dans le guide complet.

(titre) La seule vraie coupure de la soirée

Tout était en place, testé avant bascule avec `curl --resolve` pendant que les clients continuaient de passer par l'ancien chemin. C'est la bonne façon de faire : on valide le nouveau circuit sans que personne ne le subisse.

Puis est venu le DNS. Un CNAME et un enregistrement A ne peuvent pas coexister sur le même nom. Il faut donc supprimer l'un pour créer l'autre, et cette fenêtre est une vraie coupure. Quelques minutes, ce soir-là.

Quelques minutes suffisent. Pendant ce trou, les résolveurs ont demandé le domaine, entendu « n'existe pas », et mémorisé cette réponse. C'est le **cache négatif**, et il survit longtemps à la réparation : la zone répondait correctement à la source, et le poste de travail continuait de renvoyer « Could not resolve host ».

Un taxi à qui on a dit un matin « la boutique a fermé » ne t'y amènera plus pendant un moment, même si elle a rouvert entre-temps.

Trois gestes qui évitent ça :

**Baisser le TTL la veille**, au moins un ancien TTL avant la bascule. Avec 6 heures de TTL, c'est 6 heures avant. Le jour J, l'ancien chemin sort des caches en quelques minutes, et un retour arrière est tout aussi rapide.

**Enchaîner suppression et création dans la même minute**, sans rien faire entre les deux, ou utiliser le bouton Modifier quand le registrar le propose.

**Interroger la source avant de paniquer.** Si le serveur de noms du registrar répond la bonne adresse, la configuration est juste, il ne reste que des caches à vider.

(titre) Fermer la porte de derrière, dans le bon ordre

Une fois le load balancer en place, l'API a encore deux portes ouvertes : l'ancien domain mapping, et l'URL `run.app` par défaut. Tant qu'elles existent, n'importe qui contourne le load balancer, donc la politique TLS et les futures règles Cloud Armor. La documentation le dit explicitement.

L'ordre compte, et il n'est pas intuitif :

1. Attendre l'expiration de l'ancien TTL, pas une minute de moins.
2. Supprimer le domain mapping.
3. Seulement là, passer l'ingress sur « Internal + Allow traffic from external Application Load Balancers ».

Inverser 2 et 3 coupe les clients qui suivent encore l'ancien CNAME.

(titre) Ce que ça coûte, et quand il ne faut pas le faire

Environ 18 à 20 $ par mois, dont la quasi-totalité en coût fixe : les forwarding rules, facturées 0,025 $ l'heure pour les cinq premières d'un projet. Le certificat wildcard est gratuit, l'IP statique rattachée au load balancer aussi, et la redirection HTTP vers HTTPS ne coûte rien de plus puisqu'elle tombe dans le même forfait.

Face à 0 $ en domain mapping, c'est une vraie décision. Elle se renverse dans ces cas :

**Une application de démo sans vrais utilisateurs.** 18 $ par mois pour un prototype, c'est cher. Le domain mapping fait l'affaire le temps de valider l'idée.

**Un site essentiellement statique.** Firebase Hosting, ou même un bucket, coûtera moins.

**Un budget d'étudiant.** Le free tier de Cloud Run peut porter des mois d'expérimentation. Le load balancer, lui, facture dès la première heure.

**Un trafic massif concentré sur une seule région.** Le load balancer régional, sur réseau Standard, a une sortie Internet moins chère.

Et l'argument qui tranche dans l'autre sens : ces 18 $ ne bougent pas quand tu ajoutes une application. La deuxième, la troisième et la dixième passent par les mêmes forwarding rules, et le certificat wildcard les couvre déjà. Plus tu regroupes, plus c'est rentable.

(titre) Ce que je retiens

**Le certificat d'abord, le DNS ensuite.** C'est l'autorisation DNS qui rend la migration sans coupure possible, et c'est la seule qui donne un wildcard.

**Tester avant de basculer.** `curl --resolve` valide le nouveau chemin pendant que l'ancien sert les clients. Une erreur de handshake TLS dans les premières minutes après la création n'est pas un bug, c'est une propagation.

**La bascule DNS est la seule vraie coupure.** Elle doit durer quelques secondes, pas quelques minutes, et un TTL baissé la veille accélère aussi le retour arrière.

**Ne jamais laisser la politique SSL par défaut.** Sans elle, le load balancer accepte encore TLS 1.0, et toute la migration perd son objet.

J'ai écrit le carnet de bord complet de cette soirée sur mon site : écran par écran, chaque champ de la console avec la raison de sa valeur, les commandes de test, le détail des coûts, l'astuce des URL masks pour n'avoir qu'un seul NEG pour toutes les applications, et les captures de chaque étape.

C'est ici : https://ban.ga/posts/cloud-run-load-balancer/

Et si tu en es encore à te demander pourquoi ton service Cloud Run démarre lentement, l'épisode précédent de la même série s'en occupe : https://ban.ga/posts/spring-native-cloud-run/

Mbolo.

---

## À COPIER : tags Medium (5 maximum)

Google Cloud
Cloud Run
Devops
Load Balancing
Architecture

---

## Check-list avant de cliquer sur Publish

- [ ] L'article ban.ga est en ligne et répond en 200
- [ ] Cover téléversée, légende et texte alternatif renseignés
- [ ] Les lignes `(titre)` converties en titres de section, marqueur supprimé
- [ ] Les amorces en gras appliquées
- [ ] SEO title et SEO description renseignés dans Story settings → SEO
- [ ] Les trois liens vers ban.ga présents et cliquables
- [ ] Aucun canonical renseigné (texte original, voir les règles en tête de fichier)
- [ ] 5 tags maximum
