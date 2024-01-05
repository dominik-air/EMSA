import pytest

from src.services.tag_proposer import propose_tag_from_link, propose_tags_from_name


@pytest.mark.parametrize(
    "name, expected_output",
    [
        ("abc def", ["abc", "def"]),
        ("a    ab   123-", ["a", "ab", "123-"]),
        ("HELLO World", ["hello", "world"]),
        ("   This is a Test   ", ["this", "is", "a", "test"]),
        ("", []),
        ("     ", []),
    ],
)
@pytest.mark.asyncio
async def test_propose_tags_from_name(name, expected_output):
    proposed_tags = propose_tags_from_name(name)

    assert proposed_tags == expected_output


@pytest.mark.parametrize(
    "link, expected_output",
    [
        ("https://komixxy.pl/", "komixxy"),
        ("https://vm.tiktok.com/zfrre-", "tiktok"),
        ("https://github.com/dominik-air/EMSA/issues", "github"),
        ("www.reddit.com", "reddit"),
        ("reddit.com", "reddit"),
        ("dsadsa", None),
    ],
)
@pytest.mark.asyncio
async def test_propose_tag_from_link(link, expected_output):
    proposed_tag = propose_tag_from_link(link)
    print(
        f"Link: {link}, Proposed Tag: {proposed_tag}, Expected Output: {expected_output}"
    )
    assert proposed_tag == expected_output
