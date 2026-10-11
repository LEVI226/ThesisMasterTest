from pathlib import Path

from study_real_meetings.manifest import Unit
from study_real_meetings.sources import agm, ami, summre

SRT = "\n\n".join(
    f"{i + 1}\n00:{(i * 5) // 60:02d}:{(i * 5) % 60:02d},000 --> 00:{(i * 5 + 5) // 60:02d}:{(i * 5 + 5) % 60:02d},000\nmot{i}"
    for i in range(60)  # 60 cues x 5 s = 300 s
)


def test_agm_segments_cover_cues_with_ids_clusters_and_split():
    segs = agm.build_agm_segments("fr", SRT, "audio/agm/fr.wav", audio_duration=300.0)
    assert segs[0].segment_id == "agm-fr-0000"
    assert segs[0].reference == "mot0 mot1 mot2"
    assert {s.split for s in segs} == {"dev", "test"}
    assert segs[0].cluster == "agm-fr-b00" and segs[-1].cluster == "agm-fr-b02"
    for a, b in zip(segs, segs[1:]):
        assert a.end <= b.start  # padding never overlaps the next segment
    assert all(s.pair_key == s.segment_id for s in segs)


def test_find_agm_files_matches_language_tags(tmp_path):
    for lang in ("DE", "EN", "FR"):
        (tmp_path / f"Nestlé Chair & CEO ｜ Annual General Meeting 2026 ({lang}).mp3").touch()
        (tmp_path / f"[English] Nestlé Chair & CEO  Annual General Meeting 2026 ({lang}) [DownSub.com].srt").touch()
    found = agm.find_agm_files(tmp_path)
    assert set(found) == {"de", "en", "fr"}
    assert found["fr"][0].suffix == ".mp3" and found["fr"][1].suffix == ".srt"


def _row(meeting, speaker, begin, end, text="HELLO THERE"):
    return {"meeting_id": meeting, "speaker_id": speaker, "begin_time": begin,
            "end_time": end, "text": text, "audio_id": f"AMI_{meeting}_{speaker}_{begin}"}


def test_ami_selection_and_pairing():
    rows = [_row("EN2002a", "MEE073", 10.0, 12.0), _row("EN2002a", "MEE073", 20.0, 20.5),
            _row("XX0000a", "MEE001", 10.0, 12.0), _row("EN2002a", "MEE073", 30.0, 70.0)]
    kept = ami.select_rows(rows, {"EN2002a"}, 1.0, 30.0)
    assert len(kept) == 1
    seg_ihm = ami.segment_for_row(kept[0], "ihm", "audio/ami-ihm/x.wav")
    seg_sdm = ami.segment_for_row(kept[0], "sdm", "audio/ami-sdm/x.wav")
    assert seg_ihm.pair_key == seg_sdm.pair_key == "EN2002a-MEE073-0001000"
    assert seg_ihm.dataset == "ami-ihm" and seg_ihm.cluster == "ami-EN2002a-MEE073"
    assert (seg_ihm.start, seg_ihm.end) == (0.0, 2.0)  # each utterance is its own wav
    assert seg_ihm.split == "dev"


TOKENS_CSV = (
    '﻿"TokensAlign",0.0,0.9,"#"\n'
    '"TokensAlign",0.9,1.8,"bonjour"\n'
    '"TokensAlign",1.8,2.0,"@"\n'
    '"TokensAlign",2.0,2.4,"à"\n'
    '"TokensAlign",2.4,2.9,"tous"\n'
    '"TokensAlign",4.5,5.4,"euh"\n'
    '"TokensAlign",5.4,6.0,"bon"\n'
    '"PhonAlign",0.9,1.1,"b"\n'
)


def test_summre_tokens_ipus_and_segments():
    tokens = summre.parse_tokens(TOKENS_CSV)
    assert [t.text for t in tokens] == ["bonjour", "à", "tous", "euh", "bon"]
    assert [u.text for u in summre.ipus(tokens)] == ["bonjour à tous", "euh bon"]
    segs = summre.build_summre_segments("018a_EARZ", "055", tokens, "audio/summre/018a_EARZ_055.wav")
    assert len(segs) == 1 and segs[0].reference == "bonjour à tous euh bon"
    assert segs[0].cluster == "summre-018a_EARZ-055" and segs[0].speaker == "055"
    assert summre.tokens_in_span(tokens, 0.0, 3.0) == "bonjour à tous"
    assert summre.speech_regions(tokens) == [(0.9, 2.9), (4.5, 6.0)]
