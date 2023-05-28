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

Prérequis : Avoir installé Python (Ce programme a été testé seulement avec la version 3.9).

1. Aller sur la page ["Releases"](https://github.com/m-mullins/gcode_editor_3d_print/releases) de Github.

2. Décompresser l'archive obtenue dans le dossier de votre choix.

Vous devriez alors avoir les éléments suivants :

(Modifier les noms des fichiers d'exemple et voir pour ne pas mettre le dossier de test)

```graphql
└──gcode_editor/
  ├─ input/ - # Dossier où ranger les fichiers .gcode à éditer
  │  └─ xyz-10mm...
  ├─ output/ - # Dossier où seront rangés les nouveaux fichiers .gcode après édition
  ├─ parameter/ - # Dossier où ranger les fichiers de paramétrages .txt
  │  └─ parametre...
  ├─ tests/ - # Page layouts used for different types of pages composed of components and fragments
  ├─ README.md - # Custom pages or pages composed of layouts with hardcoded data components, fragments, & layouts
  ├─ README-dev.md - # Next.js file based routing
  ├─ README-dev-en.md - # Next.js file based routing
  ├─ README-en.md - # Next.js file based routing
  ├─ requirements.txt - # Utility functions used in various places
  └─ xyz-10mm-calibration-cube.stl - # Utility functions used in various places
```

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

### Paramètres

Pour utiliser cet éditeur de G-code, il est d'abord nécessaire de créer un fichier de paramétrage. Un exemple de fichier
se trouve dans le dossier *parameter*. Ce fichier se décompose en cinq sections.

* Identification des phases : Décrit comment les couches de l'objet 3D sont regroupés en phase. Ces phases étant 
associées aux paramètres de température, vitesse, ... décris par la suite.
  * Phase 000 (%) : 0
  * Phase 001 (%) : 60
  * Phase 002 (%) : 100

* Température : Décrit l'évolution de la température de la buse au cours de chacune des phases. L'évolution de la 
température est linéaire sur chacune des phases on part de la température entrée en paramètre pour la couche précédente
et on atteint la température entrée pour la couche courante.
  * Phase 000 (°C) : 180 
  * Phase 001 (deg C) : 190 
  * Phase 002 (deg C) : 210

* Vitesse d'impression : Décrit l'évolution de la buse au cours de chacune des phases.
  * Phase 000 (%) : 90 
  * Phase 001 (%) : 100 
  * Phase 002 (%) : 110

* Extrusion : Décrit si l'on souhaite effectuer une sous-extrusion ou une sur-extrusion au cours de la phase et à quelle
intensité. *
  * Phase 000 (%) : 80 
  * Phase 001 (%) : 90 
  * Phase 002 (%) : 110

* Décalage de la position : Décrit les nouvelles positions ...

