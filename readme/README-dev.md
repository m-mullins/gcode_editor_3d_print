# gcode_editor_3d_print

[![en](https://img.shields.io/badge/lang-en-red.svg)](https://github.com/m-mullins/gcode_editor_3d_print/blob/main/readme/README-dev-en.md)

# README pour les développeurs
Ce README est à destination des développeurs qui souhaiteraient reprendre ce projet et faire évaluer le code 
"gcode_editor.py". Nous détaillons ici les informations que nous avons jugés utiles pour travailler 
sur ce projet. Nous fournissons la structure du projet, les informations sur le fonctionnement du code, les tâches 
supplémentaires implémentées pour modifier le G-code et leurs instructions détaillées. Pour les explications relatives 
à l'utilisation de cet éditeur de G-code, référez-vous au fichier [README](../README.md).

## Dépendances

Ce programme a été développé avec Python 3.9.5 et a été testé avec les versions 3.9.5 et 3.11.3. Ci-dessous la liste des
modules utilisés et leur version.

### Modules :

`numpy 1.24.3`

## Description du projet

Le code `gcode_editor.py` est un programme Python permettant de modifier et de manipuler des fichiers G-code utilisés 
dans l'impression 3D. Il prend en entrée un fichier G-code et un fichier de paramètres créé par l'utilisateur. Ensuite,
il effectue différentes modifications sur le G-code en fonction de ces paramètres.

## Structure du projet

Le dossier du projet est organisé de la manière suivante :

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
  ├─ tests/
  │  └─ exec_time.py
  ├─ check.py
  ├─ gcode_editor.py # Programme Python principal
  ├─ README.md - # Fichier README
  ├─ requirements.txt
  └─ xyz-10mm-calibration-cube.stl - # Objet 3D utilisé comme exemple
````

### Fichiers importants

- `gcode_editor.py` et `check.py`: Les fichiers principaux contenant le code source.
- `example_parameter.txt` : Un exemple de fichier de paramètres utilisé pour définir les modifications à apporter au 
G-code. Pour comprendre comment s'articule ce fichier et la manière dont il doit être modifié par l'utilisateur, 
référez-vous au fichier [README](../README.md).

## Fonctionnement de `gcode_editor.py`

Voici une explication du fonctionnement du programme `gcode_editor.py`. Pour cela, nous allons présenter le flot de 
contrôle de la fonction principale `gcode_editor()`. Les fonctions de modification du G-code sont détaillées dans la 
section [Tâches implémentées pour la modification du G-code :](#fonctions-de-modification-du-g-code)

1. Lecture du fichier de paramètre :
   - `extract_values_from_file()` : On lit le fichier de paramètre pour récupérer l'ensemble des paramètres entrés par 
   l'utilisateur dans des listes Numpy.
   
2. Vérification des paramètres :
   - `check_parameter()` : On vérifie que les paramètres entrés par l'utilisateur respectent les contraintes imposées.
   
3. Obtenir un statut sur les couches :
   - `find_layer_info()` : On parcourt une première fois le fichier G-code spécifié en entrée pour obtenir les 
   informations liées aux couches.
   
4. Itération sur les lignes du fichier de G-code :
   1. Ligne de commentaire :
      1. Commentaire commençant par ";LAYER_CHANGE" :
         - Incrémenter le compteur de la couche courante.
      2. Commentaire commençant par ";BEFORE_LAYER_CHANGE" :
         - `set_heating_path()` et `edit_heating_gcode()` : Ajout d'instructions G-code pour réchauffer la couche 
         précédente.
         - `add_temperature_setup()` : Ajout d'instructions G-code pour modifier la température de la tête d'extrusion.
      3. Commentaire commençant par ";TYPE:External perimeter" : 
         - Détecter l'impression du périmètre extérieur et collecter les coordonnées des mouvements.
      4. Commentaire commençant par ";WIPE_START" :
         - Détecter la fin de l'impression du périmètre extérieur et stopper la collecte des coordonnées.
   2. Instruction de G-code :
      - `find_phase()` : On détermine la phase en cours et notre progression dans cette phase.
      - On applique les différentes fonctions de modifications sur l'instruction :
        1. Instruction commençant par G1 :
           - `modify_speed()` : Modification de la vitesse d'impression.
           - `modify_extrusion_amounts()` : Modifier de l'extrusion.
           - `shift_position()` : Décalage de la position de la pièce sur les axes X et en Y sur le lit.
        2. Instruction commençant par M104 ou M109 :
           - `modify_temperature()` : Modification de la température d'impression.

5. Écriture de la ligne dans un nouveau fichier.

## Fonctions de modification du G-code

Les ajustements souhaités par l'utilisateur dans le fichier de paramètres ont pour but de modifier les instructions de 
G-code afin de réaliser les tâches vues précédemment. Nous allons décrire le principe que nous avons choisi pour modifier une
ligne et que nous jugeons bon de conserver si vous souhaitez ajouter de nouvelles fonctionnalités d'édition.

Signature minimum des fonctions : modify_gcode_line(modified_line_parts, parameter_array)

- Arguments :
  - modified_line_parts (list) : Liste des éléments d'une instruction de G-code séparés d'un espace.
  - parameter_array (numpy array) : Liste des paramètres spécifiés par l'utilisateur.
  - phase_num (int) : Numéro de la phase en cours de traitement (Optionnel). 
  - phase_pct (float) : Pourcentage de progression dans la phase en cours (Optionnel).
- Retour : None

Nous utilisons ces fonctions de la manière suivante :

1. Découper de la ligne d'instruction : `line.split('')`
2. Marquer la ligne comme ayant été modifié
3. Application successive des fonctions `modify_...()`. Comme on modifie une liste, il n'y a pas besoin de récupérer une
nouvelle chaîne de caractère après chaque fonction.
4. Créer la nouvelle ligne d'instruction G-code en soudant la liste des éléments de l'instruction : 
`" ".join(modified_line_parts)`
     
## Notes supplémentaires

- Le fichier `check.py` sert à effectuer quelques vérifications basiques sur le fichier de paramètres entré par 
l'utilisateur. Par exemple, que les vitesses ou les températures ne sont pas négatives. Cependant, notre code laisse au 
soin de l'utilisateur de vérifier la cohérence de ses paramètres par rapport aux capacités de son imprimante, étant 
donné que nous n'avons pas de moyens de les connaître. Toutefois, nous affichons actuellement des *Warning* pour les
valeurs qui dépassent des plages d'utilisation classique trouvées sur Internet. De cette manière, nous pouvons mettre en 
avant une valeur anormalement élevée qui pourrait relever d'une faute de frappe, mais qui est tout de même valide. Par 
exemple une température de 1000 °C.
- Le code est structuré et modulaire, facilitant l'ajout de nouvelles fonctionnalités ou la modification des 
fonctionnalités existantes dans `gcode_editor.py`.
- Pour toute question ou suggestion d'amélioration, n'hésitez pas à contacter l'équipe de développement.
