from nowdoing._auth import make_nonce, sha256_hex, sign_request, timestamp_seconds


def test_sha256_empty_body_matches_canonical_constant() -> None:
    assert sha256_hex(b"") == (
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    )


def test_sign_reference_vector_empty_body() -> None:
    # Same vector verified by the JS SDK and by the Swift signing helper.
    assert sign_request(
        token="token",
        method="POST",
        target="/test",
        timestamp="1234567890",
        nonce="abcdabcdabcdabcd",
        body=b"",
    ) == "2e5984ed312e8f6e18ee9e3a4a6c79fa01d21cc7bcf69a85b7c9d8162639137a"


def test_sign_reference_vector_with_body() -> None:
    assert sign_request(
        token="s3cret",
        method="POST",
        target="/branch-changed",
        timestamp="1700000000",
        nonce="noncenoncenoncen0",
        body=b'{"branch":"main"}',
    ) == "e0f3c91e3a9dc163ba455fd2cbbf28725fd722931e2eb2274b3d24d7fc07cddb"


def test_sign_produces_lowercase_hex_64_chars() -> None:
    sig = sign_request(
        token="t", method="GET", target="/x", timestamp="0",
        nonce="abcdabcdabcdabcd", body=b"",
    )
    assert len(sig) == 64
    assert all(c in "0123456789abcdef" for c in sig)


def test_sign_differs_for_different_body() -> None:
    common = dict(token="t", method="POST", target="/test", timestamp="0",
                  nonce="abcdabcdabcdabcd")
    assert sign_request(**common, body=b"hello") != sign_request(**common, body=b"world")


def test_make_nonce_is_32_lowercase_hex() -> None:
    n = make_nonce()
    assert len(n) == 32
    assert all(c in "0123456789abcdef" for c in n)


def test_make_nonce_is_unique() -> None:
    assert make_nonce() != make_nonce()


def test_timestamp_floors_to_seconds() -> None:
    assert timestamp_seconds(1700000000.999) == "1700000000"
