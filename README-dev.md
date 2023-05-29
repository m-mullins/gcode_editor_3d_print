# gcode_editor_3d_print

[![en](https://img.shields.io/badge/lang-en-red.svg)](https://github.com/m-mullins/gcode_editor_3d_print/blob/main/README-dev-en.md)

# README pour les développeurs
Ce README est à destination des développeurs qui souhaiteraient reprendre ce projet et faire évaluer le code 
"gcode_editor.py". Nous détaillons ici les informations que nous avons jugés utiles pour travailler 
sur ce projet. Nous fournissons la structure du projet, les informations sur le fonctionnement du code, les tâches 
supplémentaires implémentées pour modifier le G-code et leurs instructions détaillées. Pour les explications relatives 
à l'utilisation de cet éditeur de G-code, référez-vous au fichier [README](README.md).

## Dépendances

Ce programme a été développé avec Python 3.9.5 et n'a pas été testé avec d'autres versions. Ci-dessous la liste des
modules utilisés et leur version.

### Modules: 
`numpy 1.24.3`

## Description du projet :
Le code "gcode_editor.py" est un utilitaire Python permettant de modifier et de manipuler des fichiers G-code utilisés 
dans l'impression 3D. Il prend en entrée un fichier G-code et un fichier de paramètres utilisateur, et effectue 
différentes modifications sur le G-code en fonction des paramètres spécifiés par l'utilisateur.

## Structure du projet :
Le dossier du projet est organisé de la manière suivante :

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

### Les fichier important pour les développeurs :
- `gcode_editor.py` : Le fichier principal contenant le code source.
- `parametre_impression_3d.txt` : Le fichier de paramètres utilisé pour définir les modifications à apporter au G-code.
Pour comprendre comment s'articule ce fichier et la manière dont il doit être modifié par l'utilisateur, réfèrez-vous 
au fichier [README](README.md)

## Fonctionnement et flux de `gcode_editor.py`
Voici une description détaillée du fonctionnement du script `gcode_editor.py` et de l'ordre d'appel des fonctions dans 
la fonction principale `gcode_editor()`. Les fonctions de modification du G-code sont détaillées à la section 
[Tâches implémentées pour la modification du G-code :](#Tâches_implémentées_pour_la_modification_du_G-code_:)

1. Lecture des fichiers d'entrée : 
   - `find_layer_info()` : lit le fichier G-code spécifié en entrée pour obtenir les informations liées aux couches.
   - `extract_values_from_file()` : lit le fichier de paramètre `parametre_impression_3d.txt` et récupère les paramètres que l'utilisateur souhaite
   modifier dans le G-code original.
2. Parcours des lignes de code G-code :
   - itère sur chaque ligne du G-code pour les traiter une par une.
3. Détermination de la phase en cours :
   - `find_phase()` : identifie la phase en cours de traitement en se basant sur les pourcentages définis dans le fichier de paramètres.
   - `get_current_phase()` : pour déterminer la phase actuelle en fonction du pourcentage de 
   progression dans le G-code.
4. Modification de la température d'impression :
   - appel de la fonction `modify_temperature()`
5. Modification de la vitesse d'impression :
   - appel de la fonction `modify_speed()`
6. Sur ou sous extruder d'un certain pourcentage de manière variable :
   - appel de la fonction `modify_extrusion_amounts()` 
7. Décalage de la position de la pièce en X et en Y sur le lit :
   - appel de la fonction `shift_position()` 
8. (...) Ajouter les fonctions pour la tâche optionnelle (Léo)
9. Écriture du G-code modifié :
   - Après avoir traité toutes les lignes du G-code, le script écrit les lignes modifiées dans un nouveau fichier avec 
   le préfixe "modified-" ajouté au nom d'origine du fichier G-code. 

Cet ordre d'appel des fonctions garantit que les modifications sont appliquées dans l'ordre souhaité et selon les 
paramètres spécifiés par l'utilisateur. Chaque fonction est responsable d'effectuer une modification spécifique sur 
les lignes du G-code en fonction de la phase en cours et des paramètres de modification.

## Tâches implémentées pour la modification du G-code :

Les ajustements souhaitées par l'utilisateur dans le fichier `parametre_impression_3d.txt` ont pour but de modifier 
les instructions G-code afin de réaliser les tâches suivantes:

1. Modification de la température d'impression :
   - `modify_temperature(line, parameter_array, phase_num, phase_pct)` :
     - But : modifier les lignes du G-code pour ajuster la température d'impression en fonction des phases et des 
     pourcentages spécifiés dans le fichier de paramètres. La fonction prend donc la ligne en cours de traitement, la 
     liste des paramètres de modification, le numéro de phase et le pourcentage de progression comme arguments, et 
     retourne la ligne modifiée.
     - Arguments :
       - line (str) : Une ligne du G-code à modifier.
       - parameter_array (list) : Liste des paramètres de modification spécifiés dans le fichier de paramètres.
       - phase_num (int) : Numéro de la phase en cours de traitement.
       - phase_pct (int) : Pourcentage de progression dans la phase en cours.
     - Retour : La ligne du G-code modifiée.

2. Modification de la vitesse d'impression :
   - `modify_speed(modified_line_parts, parameter_array, phase_num, phase_pct)` :
     - But : modifier les lignes du G-code pour ajuster la vitesse d'impression en fonction des phases et des 
     pourcentages spécifiés dans le fichier de paramètres. La fonction prend la ligne en cours de traitement, la liste 
     des paramètres de modification, le numéro de phase et le pourcentage de progression comme arguments, et retourne 
     la ligne modifiée.
     - Arguments :
       - modified_line_parts (list) : Liste des parties de la ligne du G-code préalablement modifiée.
       - parameter_array (list) : Liste des paramètres de modification spécifiés dans le fichier de paramètres.
       - phase_num (int) : Numéro de la phase en cours de traitement.
       - phase_pct (int) : Pourcentage de progression dans la phase en cours.
     - Retour : La ligne du G-code modifiée.

3. Sur ou sous extruder d'un certain pourcentage de manière variable :
   - `modify_quantity_extrusion(line, parameter_array, phase_num, phase_pct)` :
     - But : ajuster la quantité de matériau extrudé en fonction de la vitesse d'impression et de la température dans 
     une plage spécifiée par les phases et les pourcentages du fichier de paramètres. Cela permet un contrôle précis 
     de l'extrusion.
   - Arguments :
     - line (str) : Une ligne du G-code à modifier.
     - parameter_array (list) : Liste des paramètres de modification spécifiés dans le fichier de paramètres.
     - phase_num (int) : Numéro de la phase en cours de traitement.
     - phase_pct (int) : Pourcentage de progression dans la phase en cours.
   - Retour : La ligne du G-code modifiée.

4. Décalage de la position de la pièce en X et en Y sur le lit :
   - `shift_position(line, parameter_array, phase_num, phase_pct)` :
     - But : décaler la position de la pièce en ajoutant une valeur spécifiée en millimètres à ses coordonnées X et Y, 
     selon les phases et les valeurs spécifiées dans le fichier de paramètres. Cela permet de régler précisément 
     l'emplacement de la pièce sur le lit du plateau d'impression. Cette fonction prend la ligne en cours de traitement, 
     la liste des paramètres de modification, le numéro de la phase initiale (sur le lit) et retourne la ligne modifiée.
     - Arguments :
       - line (str) : Une ligne du G-code à modifier.
       - parameter_array (list) : Liste des paramètres de modification spécifiés dans le fichier de paramètres.
       - phase_num (int) : Numéro de la phase en cours de traitement.
     - Retour : La ligne du G-code modifiée.

5. Ajouter tâche optionnelle (Léo)

## Notes supplémentaires :
- Assurez-vous que les lignes du fichier de paramètres correspondent aux phases et pourcentages définis dans le G-code, 
sinon les modifications ne seront pas appliquées correctement.
- Le code est structuré et modulaire, facilitant l'ajout de nouvelles fonctionnalités ou la modification des 
fonctionnalités existantes.
- Pour toute question ou suggestion d'amélioration, n'hésitez pas à contacter l'équipe de développement.
