
from framework.response import Response


def default_404_view(request):
    """
    View to be called when a user does not define 404 view.
    """
    url = request.PATH_INFO
    output = f"""
    <h1>Resource "{url}" Not Found</h1>
    <span>
        You can define a view to route 404 response to by using the 
        @app.route_404() on top of the view
        <pre>
        <code>
            For example, 
                
            @app.route_404()
            def view_404(request):
                ### Other processes here ###
                return TemplateResponse('page_404.html')
        </code>
        </pre>
    </span>

    """

    return Response(output, status_code=404)
