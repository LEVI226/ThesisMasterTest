from study_real_meetings.manifest import (
    Segment,
    Unit,
    merge_units,
    read_manifest,
    split_for,
    write_manifest,
)
from study_real_meetings.srt import parse_srt

SRT = """1
00:00:00,800 --> 00:00:02,520
Ladies and Gentlemen.

2
00:00:02,520 --> 00:00:05,440
Geehrte Damen
und Herren,
"""


def test_parse_srt_joins_lines_and_reads_times():
    units = parse_srt(SRT)
    assert units == [
        Unit(0.8, 2.52, "Ladies and Gentlemen."),
        Unit(2.52, 5.44, "Geehrte Damen und Herren,"),
    ]


def test_merge_stops_once_target_is_reached():
    units = [Unit(float(i), float(i + 5), f"u{i}") for i in range(0, 20, 5)]
    groups = merge_units(units, target_s=15, max_s=20, max_gap_s=2)
    assert [[u.text for u in g] for g in groups] == [["u0", "u5", "u10"], ["u15"]]


def test_merge_breaks_on_long_gap_and_on_max_span():
    assert len(merge_units([Unit(0, 2, "a"), Unit(10, 12, "b")], max_gap_s=2)) == 2
    assert len(merge_units([Unit(0, 12, "a"), Unit(12, 25, "b")], max_s=20)) == 2


def test_merge_skips_empty_text():
    assert merge_units([Unit(0, 1, "  "), Unit(1, 2, "x")]) == [[Unit(1, 2, "x")]]


def test_split_for_uses_dev_window():
    assert split_for(0.0) == "dev"
    assert split_for(179.9) == "dev"
    assert split_for(180.0) == "test"


def test_manifest_roundtrip_keeps_unicode(tmp_path):
    seg = Segment("agm-fr-0001", "agm", "fr", "audio/agm/fr.wav", 1.0, 16.0,
                  "Mesdames et messieurs, Nestlé", "agm-fr-b00", "dev")
    path = tmp_path / "m.jsonl"
    write_manifest(path, [seg])
    assert read_manifest(path) == [seg]
    assert seg.duration == 15.0
