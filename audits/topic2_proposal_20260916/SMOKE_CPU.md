# Exécution réelle limitée — CPU

Le 16 septembre 2026, `smoke_cpu.py` a exécuté quatre transcriptions avec le modèle **tiny / CPU / int8**, déjà en cache et sans téléchargement. La fonction actuelle `transcribe_file` est utilisée, avec sélection du modèle explicitement remplacée par le modèle CPU et diarisation explicitement désactivée. Prompt, prétraitement et word timestamps désactivés ; détection de langue automatique.

Ce test démontre l'exécution du composant ASR sur ces quatre fichiers, **pas** le fonctionnement complet de l'interface, de Teams, de LoRA ou de pyannote.

| Fichier | Langue détectée | WER vs référence stockée | Temps appel complet hors chargement modèle | RTF |
|---|---|---:|---:|---:|
| minds14_en_clean_01 | en | 58,33 % | 10,517 s | 0,970 |
| minds14_fr_clean_01 | fr | 0 % | 1,568 s | 0,418 |
| minds14_de_clean_01 | en | 162,5 % | 2,827 s | 0,483 |
| minds14_fr_noisy_01 | it | 100 % | 3,462 s | 0,922 |

Chargement du modèle : 0,493 s. Les temps ci-dessus incluent la lecture de durée audio dans la fonction ; ils ne sont pas des latences de bout en bout. Le premier appel peut inclure une initialisation différée. Un seul passage par fichier : aucune conclusion statistique sur la vitesse. Les WER peuvent dépasser 100 %.

Pour le premier fichier anglais, l'hypothèse contient une proposition finale absente de la référence. L'écoute est nécessaire pour décider s'il s'agit d'une hallucination ou d'une référence tronquée. Ne pas corriger automatiquement le texte de référence pour favoriser le modèle.

L'import de pyannote a signalé un problème TorchCodec/DLL empêchant son décodage audio intégré. Ce problème n'a pas empêché faster-whisper de traiter les fichiers dans ce test isolé, mais demande un test spécifique de diarisation.

Versions : Python 3.13.7 ; torch 2.6.0+cu124 ; faster-whisper 1.2.1 ; CTranslate2 4.7.1 ; pyannote.audio 4.0.4. Textes et durées non arrondies : `smoke_cpu.json`.
