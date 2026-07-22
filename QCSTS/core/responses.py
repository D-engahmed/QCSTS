from rest_framework.response import Response
from rest_framework import status


def success_response(data=None, status_code=status.HTTP_200_OK, message=None):
    """
    Standard success response envelope.

    Usage in a view:
        return success_response(serializer.data, status.HTTP_201_CREATED)

    Returns:
        {
            "success": true,
            "data": { ... },
            "errors": null
        }
    """
    body = {
        "success": True,
        "data": data,
        "errors": None,
    }
    if message:
        body["message"] = message
    return Response(body, status=status_code)


def paginated_response(data, count, page, pages, status_code=status.HTTP_200_OK):
    """
    Paginated list response envelope.

    Usage in a view:
        return paginated_response(
            data=serializer.data,
            count=paginator.count,
            page=page_number,
            pages=paginator.num_pages
        )

    Returns:
        {
            "success": true,
            "data": [ ... ],
            "meta": { "count": 42, "page": 1, "pages": 5 },
            "errors": null
        }
    """
    return Response(
        {
            "success": True,
            "data": data,
            "meta": {
                "count": count,
                "page": page,
                "pages": pages,
            },
            "errors": None,
        },
        status=status_code,
    )


def error_response(errors, status_code=status.HTTP_400_BAD_REQUEST, **kwargs):
    """
    Manual error response for cases where you need to return
    an error directly from a view without raising an exception.

    Usage:
        return error_response(
            {"batch_number": ["This field is required."]},
            status.HTTP_400_BAD_REQUEST
        )
    """
    status_override = kwargs.get("status")
    if status_override is not None:
        status_code = status_override

    return Response(
        {
            "success": False,
            "data": None,
            "errors": errors,
        },
        status=status_code,
    )
