from urllib.parse import urlparse

KNOWN_DOMAINS = ["tiktok", "instagram", "reddit"]


def propose_tag_from_link(link: str) -> str | None:
    parsed_url = urlparse(link)
    words = parsed_url.netloc.split(".")

    if words == [""]:
        # try to find domain anyway by splitting by dots
        words = link.split(".")

    tag = next((domain for domain in KNOWN_DOMAINS if domain in words), None)
    if not tag:
        tag = words[0] if parsed_url.netloc else None
    return tag


def propose_tags_from_name(name: str) -> list:
    tags = name.split()
    lowercase_tags = [tag.lower() for tag in tags]
    return lowercase_tags
