# gcode_editor_3d_print

[![en](https://img.shields.io/badge/lang-en-red.svg)](https://github.com/m-mullins/gcode_editor_3d_print/blob/main/readme/README-en.md)

Ce README est à destination des utilisateurs du projet Gcode editor. Pour les développeurs qui seraient intéressés à 
reprendre ce projet, veuillez vous référer au fichier [README-dev](readme/README-dev.md).

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

1. Aller sur la page ["Releases"](https://github.com/m-mullins/gcode_editor_3d_print/releases) de GitHub et télécharger
l'archive *Source code (zip)* présente dans l'onglet *Assets*.

3. Décompresser l'archive obtenue dans le dossier de votre choix.

Vous devriez alors avoir le dossier gcode_editor qui suit :

````graphql
└──gcode_editor/
  ├─ input/ - # Dossier où ranger les fichiers G-code à éditer
  │  └─ 10mm_test_cube_0.4n_0.2mm_PLA_MK4_7m.gcode
  │  └─ xyz-10mm-calibration-cube_0.4n_0.2mm_PLA_MK4_8m.gcode
  ├─ output/ - # Dossier où seront rangés les nouveaux fichiers G-code après avoir été édité
  │  └─ modified-10mm_test_cube_0.4n_0.2mm_PLA_MK4_7m.gcode
  │  └─ modified-xyz-10mm-calibration-cube_0.4n_0.2mm_PLA_MK4_8m.gcode
  ├─ parameter/ - # Dossier où ranger les fichiers de paramètres
  │  └─ example_parameter.txt
  │  └─ example_parameter_bis.txt
  ├─ readme/
  │  └─ README-dev.md - # Fichier README destiné aux développeurs
  │  └─ README-dev-en.md - # Fichier README destiné aux développeurs version anglaise
  │  └─ README-en.md - # Fichier README version anglaise
  ├─ check.py
  ├─ gcode_editor.py # Programme Python principal
  ├─ README.md - # Fichier README
  ├─ requirements.txt
  └─ xyz-10mm-calibration-cube.stl - # Objet 3D utilisé comme exemple
````

3. Ouvrir un terminal de commande et rendez-vous dans le dossier où vous avez décompressez l'archive.

Exemple :
````commandline
cd Desktop/*/*/gcode_editor
````

4. Installer les modules nécessaires au programme puis lancer Python.

````commandline
pip install -r requirements.txt
python
````

5. Tester le bon fonctionnement du programme à l'aide des fichiers d'exemple déjà présents.

````python
import gcode_editor as gce
gce.gcode_editor("input/xyz-10mm-calibration-cube_0.4n_0.2mm_PLA_MK4_8m.gcode", "parameter/example_parameter.txt")
````

## Utilisation

### Génération de fichiers G-Code

À l'aide d'outil comme [PrusaSlicer](https://www.prusa3d.com/page/prusaslicer_424/), générer le fichier *.gcode* de
votre objet 3D. Placer ensuite ce fichier dans le dossier *input/*. Un fichier est déjà présent dans ce dossier pour
être utilisé en tant qu'exemple.

### Création du fichier de paramétrage

Pour utiliser cet éditeur de G-code, il est d'abord nécessaire de créer un fichier de paramétrage. 
Deux exemples de référence se trouvent dans le dossier *parameter/*. Ces fichier se décomposent en 6 sections.

#### Identification des phases

On regroupe des couches successives de l'objet 3D en phase. Ces phases sont par la suite associées aux paramètres de
température, vitesse et d'extrusion. On associe à chaque phase un pourcentage (par rapport au nombre total de couches)
qui indique la dernière couche qui appartient à cette phase. Avec l'exemple ci-dessous, on regroupe les couches en 3
phases. S'il y a 100 couches, alors la phase 3 regroupe les couches 70 à 100.

Exemple :
````text
Phase 0 (%) : 0
Phase 1 (%) : 40
Phase 2 (%) : 70
Phase 3 (%) : 100
````

Attention : La première et la dernière phase doivent obligatoirement être respectivement associées à 0 % et 100 %. 
  
#### Température

On décrit ici l'évolution de la température de la tête d'extrusion au cours de chacune des phases. L'évolution de la 
température est linéaire sur chacune des phases. On commence par la température entrée en paramètre pour la phase 
précédente et on s'arrête à la température entrée pour la phase courante. Les températures doivent correspondre à des
degrés Celsius.

Exemple :
````text
Phase 0 (deg C) : 190
Phase 1 (deg C) : 200
Phase 2 (deg C) : 210
Phase 3 (deg C) : 220
````

Attention : Cet éditeur de G-code impose peu de restriction sur les températures. Nous laissons à l'utilisateur 
la tâche de choisir un paramétrage cohérent avec les limitations de son matériel d'impression.  

#### Vitesse d'impression

On décrit ici l'évolution de la vitesse de la tête d'extrusion au cours de chacune des phases. Comme pour la 
température, l'évolution de la vitesse est linéaire sur chacune des phases. La modification de la vitesse doit être 
décrite en pourcentage.

Exemple :
````text
Phase 0 (%) : 50
Phase 1 (%) : 30
Phase 2 (%) : 40
Phase 3 (%) : 60
````

Attention : Comme pour la température, cet éditeur de G-code impose peu de restrictions. On vérifie seulement que les
pourcentages sont bien positifs. Nous laissons à l'utilisateur la tâche de choisir un paramétrage cohérent avec les 
limitations de son matériel d'impression.  

#### Extrusion 

On indique ici la limite en valeur absolue des facteurs de correction apportés à l'extrusion de la pièce (sous ou sur
extruder). C'est-à-dire que l'on souhaite modifier la quantité de matière qui sort de la tête d'extrusion. Ce paramètre 
indique que les facteurs de correction appliqués sur chacune des phases seront compris dans l'intervalle 
[100-Correction (%) ; 100+Correction (%)]. Ces facteurs sont calculés par le programme et doivent servir à pallier le 
problème du gonflement en sortie de la tête qui est fonction de la température et de la vitesse de déplacement de la 
tête. Ce paramètre doit être indiqué en pourcentage.  

Exemple :
`````text
Correction (%) : 5
`````

Attention : Supprimer la ligne ou rajouter des lignes non commentées dans cette section sera considéré comme une erreur.
  
#### Décaler la position

On décrit ici le décalage de la pièce sur le lit selon les axes X et Y de la tête d'extrusion, c'est-à-dire sur le 
plan horizontal. Ces décalages doivent correspondre à des variations en millimètres. Cette variation n'est pas associée 
à une phase, mais à l'ensemble de la pièce sur le lit. Toutes les instructions de G-code seront ajustées pour permettre 
le décalage de la pièce.

Exemple :
````text
Shift_X (mm) : 2
Shift_Y (mm) : 3
````

Attention : Supprimer ces deux lignes ou rajouter des lignes non commentées dans cette section sera considéré comme une 
erreur.

#### Réchauffement

On indique ici seulement si l'on souhaite activer ou non l'ajout d'une phase de réchauffement après l'impression de 
chacune des couches. Ce mécanisme est censé favoriser une meilleure soudure entre les couches. La valeur 0 indique que 
l'on désactive ce mécanisme, toute autre valeur entière activera ce mécanisme.

Exemple :
````text
Heating : 1
````

Attention : Supprimer la ligne ou rajouter des lignes non commentées dans cette section sera considéré comme une erreur.

Le fichier Python *check.py* contient des fonctions permettant d'effectuer quelques contrôles sur vos paramètres.
Celles-ci sont appelées au début du programme *gcode_editor*. Cependant, vous pouvez aussi vérifier sans lancer le 
programme principal vos paramètres de la manière suivante :

````python
import gcode_editor as gce
import check
check.check_parameter(gce.extract_values_from_file("parameter/example_parameter_bis.txt"))
````
