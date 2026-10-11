# Commandes exécutées et périmètre

Depuis `C:\Users\ulric\Documents\ThesisMasterTest`, le 16 septembre 2026 :

```powershell
.\.venv\Scripts\python.exe -m pytest tests -q -p no:cacheprovider --basetemp audits/topic2_proposal_20260916/pytest_tmp
.\.venv\Scripts\python.exe audits/topic2_proposal_20260916/verify_evidence.py
.\.venv\Scripts\python.exe audits/topic2_proposal_20260916/probe_contracts.py
.\.venv\Scripts\python.exe -m backend.evaluation.run_statistical_audit --output audits/topic2_proposal_20260916/statistical_recheck.md
.\.venv\Scripts\python.exe -m backend.evaluation.topic2_readiness --output audits/topic2_proposal_20260916/latency_recheck.md
.\.venv\Scripts\python.exe audits/topic2_proposal_20260916/smoke_cpu.py
```

Résultats : 51 tests passés (3,66 s), recalculs et sondes terminés avec code 0 ; quatre vraies inférences CPU terminées avec code 0 et sorties conservées. Avertissement pytest : option `cache_dir` inconnue parce que le plugin cache est désactivé pour cette exécution. Avertissement pyannote/TorchCodec : voir `SMOKE_CPU.md`.

Ne pas réutiliser le même `--basetemp` pour une relance : choisir un nouveau sous-dossier dédié ; pytest peut nettoyer son répertoire temporaire. Les deux scripts de recalcul à sorties personnalisées préservent les rapports historiques.

Le code applicatif n'a pas été corrigé dans cet audit. Les sondes emploient des remplacements en mémoire des dépendances, ne chargent pas l'application avec ses modèles et ne versent pas de texte dans le RAG. Le smoke test ne passe pas par les API et ne modifie pas les résultats historiques. Les fichiers d'audit sont les livrables de cette intervention.

Non exécutés : réunion humaine, parcours navigateur réel, Teams, nouvelle évaluation DER, réentraînement, campagne complète d'inférence des trois architectures, mesures end-to-end, test de charge prolongé. Ils sont spécifiés dans le plan de tests.
