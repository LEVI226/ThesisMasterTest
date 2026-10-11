# Relecture du retour Antigravity — 16 septembre 2026

Périmètre : retour transmis par l'utilisateur, fichiers du run `audits/topic2_validation/20260916-073214/`, code actuel. Aucun fichier historique, code applicatif ou résumé de l'autre session modifié par cette relecture.

## Progrès appuyés par les fichiers

Les preuves avant/après, tests de contrat, essais CPU/GPU et observations micro sont présents. Le chargement LoRA dans l'application n'est pas revendiqué. Les résultats nouveaux sont séparés des historiques. Les essais de réunions à plusieurs intervenants, de termes métier et de Teams restent non exécutés selon le rapport. La diarisation est indisponible dans les essais rapportés.

## Rectifications nécessaires du bilan scientifique

1. **Dénominateur erroné.** Le CSV `06b_reference_revision_rows.csv` contient **117 lignes sur 468**, couvrant **9 fichiers sur 36**, et non 130 lignes/10 fichiers. Les cinq sources concernées ont seulement quatre copies bruitées : `en_clean_07` n'a pas de copie bruitée dans ce corpus. Le rapport 06b affiche lui-même 117 lignes dans le corps mais conserve un titre incorrect ; SUMMARY conserve 130.
2. **Références provisoires, pas gold standard indépendant.** Les textes viennent de large-v3 et la confirmation humaine a porté sur des passages suggérés. Cela permet de repérer des omissions ou erreurs, mais pas de valider chaque mot, ni de scorer impartialement large-v3. Intituler cette analyse « analyse de sensibilité à des références alternatives provisoires ».
3. **Ne pas annoncer une surestimation définitive de 10–15 points.** Cette différence dépend des références provisoires et ne vaut pas tous les agrégats (allemand Conformer inchangé, français −7,8, anglais −22,1). Les références originales sont mises en cause ; la correction exacte du WER reste à établir indépendamment.
4. **Ne pas affirmer que toutes les conclusions sont validées.** La direction moyenne LoRA passe de +1,0 à −0,1 point et celle du prompt de +0,9 à −0,8. La non-démonstration antérieure d'un bénéfice ne prouvait pas une équivalence. Les intervalles doivent être recalculés après finalisation indépendante des références. La monotonie de taille observée dans cette analyse reste exposée au biais de large-v3.
5. **Pas d'attribution générale au corpus sans vérification.** Des défauts dans les références locales ne prouvent pas que tout MInDS-14 a ce défaut, que les annotations n'ont jamais été relues ou que la source publiée est responsable. Comparer la source et la méthode d'extraction locales. L'accord de plusieurs modèles reste un indice, pas une preuve audio.
6. **Latence et accent : constat pilote, pas causalité établie.** Les 7 puis 3 productions micro de la même phrase ne sont pas les mêmes enregistrements ; ordre, prononciation, pauses et échauffement peuvent varier. Dire « latence plus faible observée dans ces essais avec langue forcée ». Le log historique sans configuration ne permet toujours pas d'attribuer son maximum de 11 s à une cause identifiée aujourd'hui.

## Correction de fin de parole encore incomplète côté navigateur

- `frontend/index.html` envoie désormais `__end__`, mais `liveStopRecord()` n'envoie pas d'abord le reliquat de `livePcmBuf` inférieur à un paquet. Le serveur ne peut pas transcrire les échantillons jamais envoyés. Tester un dernier mot dans ce reliquat.
- `liveDisconnect()` ferme au plus tard après 2 secondes. Les essais rapportent des décodages dépassant ce délai. Une transcription calculée et enregistrée côté serveur après fermeture n'est pas livrée à l'utilisateur. Vérifier le dernier texte réellement affiché et l'accusé de fin avant fermeture, avec un traitement volontairement lent.
- `frontend/live_transcribe.html` possède toujours un `stopRecording()` qui vide `pcmBuffer` sans envoyer `__end__`. La correction de l'interface principale ne couvre donc pas la route `/live`.
- Les tests sur socket simulé prouvent la vidange de ce que le serveur a reçu ; ils ne prouvent pas le transfert de l'audio résiduel du navigateur. La formule « aucune dernière phrase perdue » est trop large.
- Le nom des transcriptions inclut désormais modèle et VAD. Il distingue ces configurations, mais pas deux répétitions identiques dans un même dossier. Garder un dossier unique par run/répétition ou compléter l'identifiant.

## Suite à demander à Antigravity

1. Rectifier SUMMARY et 06b avec 9 fichiers/117 lignes et les réserves ci-dessus. Ne pas republier les chiffres provisoires comme des WER corrigés définitifs.
2. Compléter les tests d'arrêt sur les deux interfaces avec reliquat inférieur à 1 seconde, fermeture après calcul lent, absence de doublons et texte réellement affiché. Corriger les points reproduits, avec tests de régression.
3. Préparer une feuille d'annotation neutre pour les **24 sources propres**, sans préremplir les sorties des modèles. Faire transcrire les cinq cas prioritaires intégralement puis contrôler les autres ; obtenir une personne compétente pour l'allemand. Marquer les passages incertains. Une seconde relecture indépendante est souhaitable.
4. Vérifier la provenance des références locales contre la source utilisée. Versionner les références révisées, raison de changement, annotateur et date. Conserver les originales.
5. Une fois les références validées, rescorrer toutes les hypothèses stockées, y compris les copies bruitées avec leur référence correspondante. Recalculer WER/CER et intervalles groupés ; une nouvelle inférence n'est pas nécessaire pour ce rescoring.
6. Informer le directeur de cette limite avec une formulation provisoire factuelle, puis poursuivre les tests de réunion/Teams. Ne pas arrêter toute validation indépendante pendant la révision des annotations.

Formulation provisoire possible : « L'audit a identifié des erreurs probables dans plusieurs transcriptions de référence, avec des passages confirmés à l'écoute. Une analyse de sensibilité montre que les WER peuvent être substantiellement affectés. Une réannotation indépendante est en cours ; les valeurs alternatives ne sont pas encore considérées comme définitives. »
