def get_paginated_response_dict(paginator, page_number, resultset):
    """Returns the structured paginated response every list endpoint uses."""
    page_number = int(page_number)
    return {
        "count": paginator.count,
        "total_page": paginator.num_pages,
        "current_page": page_number,
        "next": paginator.num_pages > page_number,
        "results": resultset,
    }
