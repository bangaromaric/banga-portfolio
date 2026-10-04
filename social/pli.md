# Posts de promotion : fiche projet « Pli »

**Fiche projet (cible) :** https://ban.ga/projects/pli/
**Service en ligne :** https://pli.banga.ga/
**Image de couverture (OG 1200×630) :** https://ban.ga/images/pli-cover.png

> Ce fichier vit hors de `content/` : Hugo ne le construit pas en page publiée. C'est un dossier de brouillons sociaux, à copier-coller vers chaque plateforme.

> **Frontière de divulgation.** Pli est un produit dont le dépôt n'est pas public. Le post reste du côté du problème et de la promesse : aucune puce ne décrit un mécanisme. Pas de nom de champ, pas de grammaire de lien, pas de paramètre de dérivation, pas de chiffre de quota. Un post technique est exactement le format où l'on en dit trop, et il sera lu par des gens capables de reconstruire sur un indice.

---

## 1. LinkedIn

> **Mode d'emploi.** Colle le texte ci-dessous tel quel, lien compris : il est en fin de post, hors de la zone lue avant la coupe « voir plus ». Le lien pointe vers la **fiche ban.ga** et non vers `pli.banga.ga`, pour que l'aperçu affiche la cover faite pour l'occasion et non l'image du service. Le lien direct vers le produit part en premier commentaire, à coller juste après publication, pas une heure plus tard. Si tu téléverses l'image à la main, pense au bouton **Alt** et reprends le texte donné plus bas.

<!-- post:linkedin -->
Pour mon dossier, j'ai envoyé par WhatsApp ma carte d'identité, mes bulletins de paie et un relevé bancaire.

Ils y sont toujours.

Chez moi, chez le destinataire, et sur les serveurs de l'intermédiaire. Trois copies que je ne contrôle plus, pour des pièces que je n'avais besoin d'envoyer qu'une seule fois.

Aucune messagerie n'a de bouton « détruire après lecture ». Et les services qui le proposent se rangent en deux familles, dont aucune ne convient vraiment : ceux qui facturent un abonnement chiffrent sur leur serveur, donc peuvent lire ce qu'ils stockent, et le disent en petits caractères. Ceux qui chiffrent dans le navigateur tiennent la promesse, mais ce sont des projets gratuits sans engagement.

J'ai construit Pli pour occuper l'intersection. Tout le produit tient en trois états :

• Chez vous : le fichier est chiffré dans le navigateur, avant qu'un seul octet ne parte.

• Sur mon serveur : un bloc que je suis incapable d'ouvrir. La clé voyage dans la partie de l'adresse que les navigateurs ne transmettent jamais, donc elle n'arrive pas jusqu'à moi.

• Chez le destinataire : le fichier en clair, une seule fois. La première lecture détruit le pli.

La limite, parce qu'elle existe et qu'un produit de confiance qui la cache n'en est plus un : c'est mon serveur qui sert le JavaScript qui chiffre. Qui contrôlerait activement ce serveur pourrait modifier ce script. Aucune cryptographie côté navigateur ne referme cette porte, et tous les outils de cette catégorie la partagent. Je préfère l'écrire que la passer sous silence.

Je suis curieux d'une chose. Quand vous devez envoyer une pièce d'identité à un bailleur, à une banque ou à une administration, vous passez par quoi aujourd'hui ?

J'ai détaillé ce que le serveur voit, et surtout ce que j'ai refusé de mettre dans le produit :
https://ban.ga/projects/pli/

#Golang #GoogleCloud #AfricaTech
<!-- /post -->

**Texte alternatif de l'image** (bouton « Alt » de LinkedIn, si tu téléverses la cover à la main) :

`Les trois états d'un pli : le dossier en clair chez l'expéditeur, un bloc illisible sur le serveur, le même dossier rendu une seule fois chez le destinataire.`

---

**Premier commentaire (à coller juste après publication) :**

<!-- post:linkedin:commentaire -->
Pour l'essayer directement, sans compte ni inscription : https://pli.banga.ga. Un pli vit une heure ou douze heures au choix, et disparaît de toute façon à la première ouverture. Phrase de passe optionnelle si le lien seul ne doit pas suffire.
<!-- /post -->

---

**Variante « lien en premier commentaire »** (si tu préfères un post sans URL) : retire du post les deux dernières lignes avant les hashtags, puis commence le premier commentaire par :

`Ce que le serveur voit, et ce que j'ai refusé de mettre dans le produit : https://ban.ga/projects/pli/`

---

## Avant de publier

1. Vérifier que `https://ban.ga/projects/pli/` répond **200** une fois le déploiement GitHub Pages terminé. Un 404 scrapé reste en cache plusieurs jours.
2. Passer l'URL au [Post Inspector](https://www.linkedin.com/post-inspector/) et confirmer que l'aperçu affiche bien `pli-cover.png`. LinkedIn garde l'aperçu scrapé environ sept jours.
3. Publier, puis coller le premier commentaire immédiatement.
