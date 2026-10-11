#!/bin/bash
cd /c/Users/ulric/Documents/ThesisMasterTest
PY=.venv/Scripts/python.exe
D=2026-10-10
LG=results/real_meetings/logs
T=/c/Users/ulric/AppData/Local/Temp/claude/c--Users-ulric-Documents-autoresearch-win-rtx/d40b403c-62b5-491f-b742-dba0656b79d1/tasks/b26o4ilxj.output
until grep -q '^exit ' $T; do sleep 15; done
grep '^exit ' $T > $LG/${D}_test_whisper-small.exit
for S in whisper-large-v3 conformer-ctc-large mms-1b-all hf-whisper-small hf-whisper-small-lora; do
  for A in 1 2 3 4; do
    echo "$(date +%T) start $S attempt $A" >> $LG/${D}_chain.log
    $PY -m study_real_meetings.scripts.run_experiments --plan ALL --split test --system $S >> $LG/${D}_test_$S.log 2>&1
    rc=$?; echo "$(date +%T) end $S attempt $A rc=$rc" >> $LG/${D}_chain.log
    [ $rc -eq 0 ] && break
  done
done
for N in streaming diarization; do
  echo "$(date +%T) start $N" >> $LG/${D}_chain.log
  $PY -m study_real_meetings.scripts.run_$N > $LG/${D}_$N.log 2>&1
  echo "$(date +%T) end $N rc=$?" >> $LG/${D}_chain.log
done
echo "$(date +%T) ALLDONE" >> $LG/${D}_chain.log
