"""Registry tests: every expected topic registered and discoverable."""
from fs_quiz import registry
from fs_quiz import engine  # noqa: F401  (imports register generator modules)


EXPECTED_SURVEY_COMPUTATIONS_TOPICS = [
    "angular-misclosure",
    "area-coordinates",
    "bowditch",
    "error-propagation",
    "forward",
    "horizontal-curve",
    "inverse",
    "level-notes",
    "stadia",
    "traverse-misclosure",
    "vertical-curve",
    "volumes",
]

EXPECTED_BOUNDARY_LAW_TOPICS = [
    "adverse-possession",
    "deeds-recording",
    "easements",
    "hierarchy-of-calls",
    "plss",
    "senior-junior-rights",
    "water-boundaries",
]


def test_survey_computations_topics_registered():
    assert registry.list_topics("survey-computations") == EXPECTED_SURVEY_COMPUTATIONS_TOPICS


def test_boundary_law_topics_registered():
    assert registry.list_topics("boundary-law-and-real-property") == EXPECTED_BOUNDARY_LAW_TOPICS


def test_get_generator_round_trip():
    for domain, topics in (("survey-computations", EXPECTED_SURVEY_COMPUTATIONS_TOPICS),
                           ("boundary-law-and-real-property", EXPECTED_BOUNDARY_LAW_TOPICS)):
        for topic in topics:
            fn = registry.get_generator(domain, topic)
            assert callable(fn)
            assert fn._fs_domain == domain
            assert fn._fs_topic == topic


def test_unknown_generator_raises():
    try:
        registry.get_generator("survey-computations", "nope")
    except KeyError:
        pass
    else:
        raise AssertionError("expected KeyError")
