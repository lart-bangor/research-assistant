"""Utilities for L'ART Research Assistant data models."""
from html import escape as _escape
from pydantic import ValidationError


def validation_error_to_html(exception: ValidationError) -> str:  # noqa: C901
    """Convert a Pydantic ValidationError to HTML."""
    errors = exception.errors()
    buf: list[str] = []
    buf.append('<p>One or more error occured during data validation.</p>')
    buf.append('<ul class="dv-result">')
    for error in errors:
        buf.append('<li>')
        fieldname = ".".join(error["loc"])
        buf.append(f'Field <code class="dv-fieldname">{_escape(fieldname)}</code>')
        if error["type"] == "value_error.missing":
            buf.append('<span class="dv-error">is missing</span>')
            buf.append('<span class="dv-hint">(required)</span>.')
        elif error["type"] == "value_error.str.regex":
            buf.append('<span class="dv-error">doesn&lsquo;t match pattern</span>')
            buf.append(
                '<span class="dv-hint">must match <code>'
                f'{_escape(error["ctx"]["pattern"])}'
                '</code></span>.'
            )
        if error["type"] == "type_error.integer":
            buf.append('<span class="dv-error">is not a valid integer</span>')
            buf.append('<span class="dv-hint">(required)</span>.')
        else:
            buf.append('contains an error:')
            buf.append(f'<span class="dv-error">{_escape(error["msg"])}</span>')
            buf.append(f'<span class="dv-hint">({_escape(error["type"])})</code></span>.')
        buf.append('</li>')
    buf.append('</ul>')
    return "\n".join(buf)
