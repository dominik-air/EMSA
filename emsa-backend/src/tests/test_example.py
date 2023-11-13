import pytest


async def some_async_function():
    return "Async Result"


@pytest.mark.asyncio
async def test_async_example():
    result = await some_async_function()

    assert result


def test_example():
    result = 123

    assert result
