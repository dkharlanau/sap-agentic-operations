import unittest

from scripts.artifact_ref import build, normalize, parse, validate


class ArtifactRefTests(unittest.TestCase):
    def test_build_parse_roundtrip(self):
        ref = build("dkharlanau", "mapping-as-code", "mapping", "customer/country", "v3")
        self.assertEqual(ref.uri, "eac://dkharlanau/mapping-as-code/mapping/customer/country?version=v3")
        self.assertEqual(parse(ref.uri), ref)

    def test_reserved_characters_are_canonicalized(self):
        ref = build("dkharlanau", "project-evidence-graph", "evidence", "release 42/regression#1")
        self.assertEqual(
            ref.uri,
            "eac://dkharlanau/project-evidence-graph/evidence/release%2042/regression%231",
        )
        self.assertEqual(parse(ref.uri).local_id, "release 42/regression#1")

    def test_normalize_percent_encoding(self):
        self.assertEqual(
            normalize("eac://dkharlanau/data-relationship-map/relationship/AFS%3A4711"),
            "eac://dkharlanau/data-relationship-map/relationship/AFS:4711",
        )

    def test_invalid_scheme(self):
        result = validate("https://example.com/x")
        self.assertFalse(result["valid"])
        self.assertIn("scheme", result["error"])

    def test_missing_local_id(self):
        with self.assertRaisesRegex(ValueError, "repository/kind/local-id"):
            parse("eac://dkharlanau/mapping-as-code/mapping")

    def test_unsupported_query_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "unsupported query"):
            parse("eac://dkharlanau/mapping-as-code/mapping/x?branch=main")

    def test_blank_version_rejected(self):
        with self.assertRaisesRegex(ValueError, "version"):
            parse("eac://dkharlanau/mapping-as-code/mapping/x?version=")


if __name__ == "__main__":
    unittest.main()
