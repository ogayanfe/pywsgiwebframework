
from framework.response import Response


def default_404_view(request):
    """
    View to be called when a user does not define 404 view.
    """
    url = request.PATH_INFO
    return Response(f'<h1>Resource "{url}" Not Found</h1>', status_code=404)
