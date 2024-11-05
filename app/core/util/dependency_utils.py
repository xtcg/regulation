#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2024/5/15 14:25
# @File    : dependency_utils.py
# @Software: PyCharm

import logging
from contextlib import AsyncExitStack
from functools import wraps
from typing import Any, Callable, Coroutine, TypeVar, Dict, List, Tuple, cast, Optional

from fastapi.dependencies.models import Dependant
from fastapi.dependencies.utils import (
    get_dependant, is_coroutine_callable, solve_generator, is_async_gen_callable,
    is_gen_callable
)
from starlette.concurrency import run_in_threadpool

logger = logging.getLogger(__name__)

T = TypeVar("T")


class DependencyError(Exception):
    """Exception raised for errors during dependency injection."""

    pass


def injectable(
    func: Callable[..., Coroutine[Any, Any, T]],
) -> Callable[..., Coroutine[Any, Any, T]]:
    """
    A decorator to enable FastAPI-style dependency injection for any asynchronous function.
    This allows dependencies defined with FastAPI's Depends mechanism to be automatically
    resolved and injected into CLI tools or other components, not just web endpoints.
    Args:
        func: The asynchronous function to be wrapped, enabling dependency injection.
    Returns:
        The wrapped function with dependencies injected.
    Raises:
        ValueError: If the dependant.call is not a callable function.
        RuntimeError: If the wrapped function is not asynchronous.
        DependencyError: If an error occurs during dependency resolution.
    """

    @wraps(func)
    async def call_with_solved_dependencies(*args: Any, **kwargs: Any) -> T:  # type: ignore
        dependant: Dependant = get_dependant(path="command", call=func)
        if dependant.call is None or not callable(dependant.call):
            raise ValueError("The dependant.call attribute must be a callable.")

        # if not inspect.iscoroutinefunction(dependant.call):
        #     raise RuntimeError("The decorated function must be asynchronous.")

        # fake_request = Request({"type": "http", "headers": [], "query_string": ""})

        async with AsyncExitStack() as stack:
            values, errors, *_ = await solve_dependencies(
                # request=fake_request,
                dependant=dependant,
                async_exit_stack=stack,
            )

            if errors:
                error_details = "\n".join([str(error) for error in errors])
                logger.warning(f"Dependency resolution errors: {error_details}")

            return await dependant.call(*args, **{**values, **kwargs})

    return call_with_solved_dependencies


async def solve_dependencies(
    *,
    dependant: Dependant,
    dependency_overrides_provider: Optional[Any] = None,
    dependency_cache: Optional[Dict[Tuple[Callable[..., Any], Tuple[str]], Any]] = None,
    async_exit_stack: AsyncExitStack,
) -> Tuple[
    Dict[str, Any],
    List[Any],
    Dict[Tuple[Callable[..., Any], Tuple[str]], Any],
]:
    values: Dict[str, Any] = {}
    errors: List[Any] = []
    dependency_cache = dependency_cache or {}
    sub_dependant: Dependant
    for sub_dependant in dependant.dependencies:
        sub_dependant.call = cast(Callable[..., Any], sub_dependant.call)
        sub_dependant.cache_key = cast(
            Tuple[Callable[..., Any], Tuple[str]], sub_dependant.cache_key
        )
        call = sub_dependant.call
        use_sub_dependant = sub_dependant
        if (
            dependency_overrides_provider
            and dependency_overrides_provider.dependency_overrides
        ):
            original_call = sub_dependant.call
            call = getattr(
                dependency_overrides_provider, "dependency_overrides", {}
            ).get(original_call, original_call)
            use_path: str = sub_dependant.path  # type: ignore
            use_sub_dependant = get_dependant(
                path=use_path,
                call=call,
                name=sub_dependant.name,
                security_scopes=sub_dependant.security_scopes,
            )

        solved_result = await solve_dependencies(
            dependant=use_sub_dependant,
            dependency_overrides_provider=dependency_overrides_provider,
            dependency_cache=dependency_cache,
            async_exit_stack=async_exit_stack,
        )
        (
            sub_values,
            sub_errors,
            sub_dependency_cache,
        ) = solved_result
        dependency_cache.update(sub_dependency_cache)
        if sub_errors:
            errors.extend(sub_errors)
            continue
        if sub_dependant.use_cache and sub_dependant.cache_key in dependency_cache:
            solved = dependency_cache[sub_dependant.cache_key]
        elif is_gen_callable(call) or is_async_gen_callable(call):
            solved = await solve_generator(
                call=call, stack=async_exit_stack, sub_values=sub_values
            )
        elif is_coroutine_callable(call):
            solved = await call(**sub_values)
        else:
            solved = await run_in_threadpool(call, **sub_values)
        if sub_dependant.name is not None:
            values[sub_dependant.name] = solved
        if sub_dependant.cache_key not in dependency_cache:
            dependency_cache[sub_dependant.cache_key] = solved

    return values, errors, dependency_cache
