# gcode_editor_3d_print

[![en](https://img.shields.io/badge/lang-en-red.svg)](https://github.com/m-mullins/gcode_editor_3d_print/blob/main/README-en.md)

Ce README est à destination des utilisateurs du projet Gcode editor. Pour les développeurs qui seraient intéressés à 
reprendre ce projet, veuillez vous référez au fichier [README-dev](README-dev.md).

## Présentation

<p align="justify">
Le G-code est un langage de programmation de commande numérique spécifique aux machines CNC (Computer Numerical Control
francisé en Commande Numérique par Calculateur). Cette programmation peut désormais être fortement automatisée à l'aide 
de logiciels comme PrusaSlicer qui peuvent générer directement des instructions G-code à partir de modèles 3D (STL, OBJ,
AMF).

Ce programme a pour but d'éditer les instructions G-code générées à partir de tels logiciels afin de prendre en compte
les ajustements souhaités par l'utilisateur. Les paramètres des instructions G-code seront ainsi modifiés en fonction
des paramètres entrés par l'utilisateur et que nous décrirons par la suite. Ce programme a aussi pour objectif 
d'améliorer la soudure entre les différentes couches de l'impression 3D en ajoutant une phase de réchauffement de la 
couche inférieure avant l'impression d'une nouvelle couche.
</p>

## Installation

Cette section présente une méthode pour récupérer cet éditeur de G-code et installer les modules Python nécessaires.
Vous pouvez vous rendre immédiatement à la section [Utilisation](#utilisation) si vous le souhaitez.

Prérequis : Installer [Python](https://www.python.org/downloads/) (Versions testées 3.9.5, 3.11.3).

1. Aller sur la page ["Releases"](https://github.com/m-mullins/gcode_editor_3d_print/releases) de GitHub.

2. Décompresser l'archive obtenue dans le dossier de votre choix.

Vous devriez alors avoir le dossier gcode_editor qui suit :

````graphql
└──gcode_editor/
  ├─ input/ - # Dossier où ranger les fichiers G-code à éditer
  │  └─ xyz-10mm...
  ├─ output/ - # Dossier où seront rangés les nouveaux fichiers G-code après avoir été édité
  ├─ parameter/ - # Dossier où ranger les fichiers de paramètres
  │  └─ parametre...
  ├─ README.md - # Fichier README
  ├─ readme/
  │  └─ README-dev.md - # Fichier README destiné aux développeurs
  │  └─ README-dev-en.md - # Fichier README destiné aux développeurs version anglaise
  │  └─ README-en.md - # Fichier README version anglaise
  ├─ requirements.txt
  └─ xyz-10mm-calibration-cube.stl - # Objet 3D utilisé comme exemple
````

3. Ouvrir un terminal de commande et rendez-vous dans le dossier où vous avez décompressez l'archive.

Exemple :
````commandline
cd Desktop/*/*/gcode_editor
````

4. Lancer Python puis effectuer l'installation des modules nécessaires au programme.

````commandline
python
pip install -r requirements.txt
````

5. Tester le bon fonctionnement du programme à l'aide des fichiers d'exemple déjà présents.

````python
import gcode_editor as gce
gce.gcode_editor("example_imput", "example_parameter")
````

## Utilisation

### Génération de fichiers G-Code

À l'aide d'outil comme [PrusaSlicer](https://www.prusa3d.com/page/prusaslicer_424/), générer le fichier *.gcode* de
votre objet 3D. Placer ensuite ce fichier dans le dossier *input/*. Un fichier est déjà présent dans ce dossier pour
être utilisé en tant qu'exemple.

### Création du fichier de paramétrage

Pour utiliser cet éditeur de G-code, il est d'abord nécessaire de créer un fichier de paramétrage. 
Un exemple de référence se trouve dans le dossier *parameter/*. Ce fichier se décompose en 6 sections.

#### Identification des phases

On regroupe des couches successives de l'objet 3D en phase. Ces phases sont par la suite associées aux paramètres de
température, vitesse et d'extrusion. On associe à chaque phase un pourcentage (par rapport au nombre total de couches)
qui indique la dernière couche qui appartient à cette phase. Avec l'exemple ci-dessous, s'il y a 100 couches
alors la phase 3 regroupe les couches 21 à 50. La dernière phase doit obligatoirement être associée à 100 %. 

Exemple :
````text
Phase 000 (%) : 0
Phase 001 (%) : 20
Phase 002 (%) : 50
Phase 003 (%) : 100
````
  
#### Température

On décrit ici l'évolution de la température de la tête d'extrusion au cours de chacune des phases. L'évolution de la 
température est linéaire sur chacune des phases. On commence par la température entrée en paramètre pour la phase 
précédente et on s'arrête à la température entrée pour la phase courante. Les températures doivent correspondre à des
degrés Celsius. Cet éditeur de G-code n'impose aucune restriction sur les températures. Nous laissons à l'utilisateur 
la tâche de choisir un paramétrage cohérent avec les limitations de son matériel d'impression.

Exemple :
````text
Phase 000 (°C) : 180 
Phase 001 (°C) : 190 
Phase 002 (°C) : 210 
Phase 003 (°C) : 230
````

  
#### Vitesse d'impression

On décrit ici l'évolution de la vitesse de la tête d'extrusion au cours de chacune des phases. Comme pour la température, 
l'évolution de la vitesse est linéaire sur chacune des phases. La modification de la vitesse doit être décrite en
pourcentage.

Exemple :
````text
Phase 000 (%) : 90 
Phase 001 (%) : 100 
Phase 002 (%) : 110
Phase 003 (%) : 130
````

#### Extrusion 

On décrit ici si l'on souhaite effectuer une sur-extrusion ou une sous-extrusion au cours de chacune des phases. 
C'est-à-dire que l'on modifie la quantité de matière qui sort de la tête d'extrusion. L'intensité de cette variation 
doit être indiquée en pourcentage. Cet ajustement peut servir pour pallier le problème du gonflement en sortie de la tête.
Ce phénomène est impacté par la température et la vitesse de déplacement de la tête, il est donc important de prendre en
compte ces deux autres données dans votre choix pour le paramétrage de l'extrusion.

Exemple :
`````text
En attente
`````
  
#### Décaler la position

On décrit ici le décalage de la pièce sur le lit selon les axes X et Y de la tête d'extrusion, c'est-à-dire sur le 
plan horizontal. Ces décalages doivent correspondre à des variations en millimètres. Cette variation n'est pas associée à une
phase, mais à l'ensemble de la pièce. Toutes les instructions de G-code seront ajustées pour permettre le décalage de la 
pièce.

Exemple :
````text
En attente
````


## Réchauffement

On indique ici seulement si l'on souhaite activer ou non l'ajout d'une phase de réchauffement après l'impression de 
chacune des couches. Ce mécanisme est censé favoriser une meilleure soudure entre les couches. La valeur 0 indique que 
l'on désactive ce mécanisme, toute autre valeur entière activera ce mécanisme.

Exemple :
````text
Heating : 1
````


