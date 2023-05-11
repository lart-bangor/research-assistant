"""API Base to expose data models via eel."""
import logging
from abc import ABC, abstractmethod
from functools import wraps, partial
from typing import TypeVar, Callable, Any, cast, overload
import eel

# TypeVar for function wrappers
F = TypeVar("F", bound=Callable[..., Any])

logger = logging.getLogger(__name__)


def _get_class_bases(cls: object) -> set[object]:
    """Return a set containing all the classes in the derivational hierarchy of *cls*."""
    bases = set(cls.__bases__)
    frozenbases = frozenset(bases)
    for base in frozenbases:
        bases |= _get_class_bases(base)
    return bases


class EelAPI(ABC):
    """Base class to build Eel APIs.

    :class:`EelAPI` offers an easy solution to creating a namespaced and segregated
    API for exposure via Eel's JavaScript API. It ensures that even where the API
    is instanciated more than once in Python, the reference object is always a
    singleton referring to the same object instance, thereby removing possible
    conflicts if different Python modules attempt to make use of the same Eel API.
    It also automatically namespaces the exposed methods for Eel, so that name
    conflicts on the JavaScript side can be avoided more easily.

    Classes defining an API with :class:`EelAPI` must minimally set the
    `eel_namespace` attribute, a string which will be prefixed to all methods
    when exposed via Eel.

    Classes may optional define an attribute
    `exception_handler`, which should either be a static method of the class
    or an external callable accepting a single argument of type `Exception`.
    If `exception_handler` is defined, any exceptions raised during a call via
    Eel's JavaScript API will be passed to `exception_handler`. If none is set
    the default behaviour is to simply raise the exception.

    .. important::

        Classes should not overwrite any other internally pre-defined methods or
        attributes, which might affect the basic behaviour of the class. The
        methods and attributes which should not be overwritten are: `_instance`,
        `eel_api`, `_handle_exception`, `_get_exposed`, `_wrap_method`, `expose`
        and `exposed`.

        If you do overwrite any of these methods to modify their behaviour, you
        must ensure that they remain fully compatible with originals.

    Simple example:

    First let us define a Greetings API which should expose two methods via
    Eel's JavaScript API: :code:`say_hello` which prints :code:`Hello World!`
    on the Python terminal, and :code:`greet(name: str)` which should
    print :code:`Hello {name}!` to the Python terminal and pass back the string
    :code:`"{name} has been greeted."` to JavaScript. If an exception
    occurs, we want to print out text to say that an exception has occured and
    then go about our normal business of greeting people::

        class GreetingsAPI(EelAPI):

            eel_namespace: str = "greetings"

            @staticmethod
            def exception_handler(exc: Exception) -> None:
                print("The following exception has occured:", exc)

            @EelAPI.exposed
            def say_hello(self) -> None:
                print("Hello world!")

            @EelAPI.exposed
            def greet(self, name: str) -> str:
                print(f"Hello {name}!")
                return f"{name} has been greeted."

    All we have to do now is to get a controller for the API and expose it to
    JavaScript via Eel:

        .. code-block:: python

            api = GreetingsAPI()
            api.expose()

    We can now call the functions of the API from JavaScript:

        .. code-block:: javascript

            function report_feedback(feedback) {
                console.log(feedback);
            }

            eel.greetings_say_hello()();
            eel.greetings_greet("Nia")(report_feedback);

    The output on the Python terminal will be:

        .. raw::

            Hello world!
            Hello Nia!

    and the output on the JavaScript console will be:

        .. raw::

            Nia has been greeted.

    It doesn't matter if someone else somewhere else in our Python code
    later does something like :code:`api2 = GreetingsAPI()`, they will
    simply get a reference to the original :code:`GreetingsAPI` instance,
    and calling :code:`api2.expose()` will have no effect. Any modifications
    that we make to :code:`api` will be reflected on :code:`api2` and
    vice-versa, since they're both the same object controlling the same API.
    """

    # Exposed API listing
    eel_api: dict[str, F]

    # Singleton instance cache
    _instance: object | None = None

    @property
    @abstractmethod
    def eel_namespace(self) -> str:
        """Namespace property of the EelAPI.

        This must be overridden with a string in any instantiable class derived
        from EelAPI. Note however that you should not set *eel_namespace* if your
        class is only an intermediate API not meant for instantiating, so as to
        avoid the possibility of instantiating several APIs sharing the same
        namespace on Eel's JavaScript API.

        The string in *eel_namespace* is prefixed to all exposed methods on
        instances of the API.

        Example::

            class MyAPI(EelAPI):

                eel_namespace: str = "myapi"

                @EelAPI.exposed
                def say_hello(self):
                    print("Hello world!")

            controller = MyAPI() # Instantiate the API
            controller.expose()  # Expose the API via Eel
            print(list(controller.eel_api)) # Print ['myapi_say_hello']
        """
        ...

    def __new__(cls, *args, **kwargs):
        """Singleton object constructor for EelAPI.

        The pattern of object construction implemented here ensures that only a single
        object instance of the class is ever created, and that the object attribute
        *eel_api* is set to an empty dictionary on that first instance. All subsequent
        attempts to create an instance of the object will return the original object
        created.

        This ensures that (since the API is by design always unique on the
        JavaScript side) the controller of the API on the Python side is always unique
        and no conflicts arrive over the interface (e.g. if different instances of
        the same API try to expose the same functionality, it may be difficult to
        determine where callbacks from JavaScript are handled in Python, leading to
        difficulty debugging at best and undefined behaviour at worst).
        """
        if not isinstance(cls._instance, cls):
            cls._instance = object.__new__(cls)
        if not hasattr(cls._instance, "eel_api"):
            cls._instance.eel_api = {}
        return cls._instance

    def _handle_exception(self, exc: Exception) -> None:
        """Passes exception to exceptionhandler if defined, otherwise continues raising."""
        logger.exception(exc)
        if hasattr(self, "exception_handler"):
            getattr(self, "exception_handler")(exc)
        else:
            raise exc

    def _get_exposed(self):
        """Get a list of the defined APIs exposed functions."""
        cache = self.__class__.exposed(None)
        if not isinstance(cache, dict):
            raise RuntimeError("EelAPI cache failed to return dictionary of callables.")
        cache = cast(dict[str, set[F]], cache)
        relevant: set[F] = set()
        bases = _get_class_bases(self.__class__)
        bases.add(self.__class__)
        for base in bases:
            if base.__name__ in cache:
                relevant |= cache[base.__name__]
        return relevant

    def _wrap_method(self, func: F) -> F:
        """Wraps a method as a partial with the first argument fixed as *self*."""
        partial_func = partial(func, self)

        @wraps(func)
        def eel_api_wrapper(
                *args: list[Any],
                **kwargs: dict[str, Any]
        ) -> Any:
            try:
                return partial_func(*args, **kwargs)
            except Exception as exc:
                self._handle_exception(exc)
                return False

        return eel_api_wrapper

    def expose(self) -> None:
        """Expose the API defined by the class via Eel's JavaScript API."""
        funcs = self._get_exposed()
        for func in funcs:
            name = f"{self.eel_namespace}_{func.__name__}"
            func = self._wrap_method(func)
            if name in self.eel_api:
                if self.eel_api is func:
                    continue  # already exposed, do nothing
                else:
                    logger.warning(
                        f"Attempting to overwrite already exposed method {name!r} "
                        f"({self.eel_api[name]}) with new method ({func}) on "
                        f"EelAPI instance of {self.__class__.__qualname__}."
                    )
            eel._expose(name, func)
            self.eel_api[name] = func

    @overload
    def exposed(func: F) -> F:
        ...

    @overload
    def exposed(func: None) -> dict[str, set[F]]:
        ...

    def exposed(func: F, cache={}) -> F | dict[str, set[F]]:
        """Decorator to mark a method for exposure via Eel's JavaScript API."""
        if func is None:
            return cache
        qualname = func.__qualname__.split(".")
        if len(qualname) < 2:
            raise RuntimeError(
                f"Qualified name of {func} does not contain identifiable parent class,"
                " argument 'func' must be a bound method"
            )
        classname = qualname[-2]
        if classname in cache:
            cache[classname].add(func)
        else:
            cache[classname] = {func}
        return func
