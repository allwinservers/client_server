from rest_framework.routers import DefaultRouter, Route


class RoboRouter(DefaultRouter):
    """
    自定义delete路由
    """
    routes = DefaultRouter.routes
    routes[0] = Route(
        url=r'^{prefix}{trailing_slash}$',
        mapping={
            'get': 'list',
            'post': 'create',
            'delete': 'destroy'
        },
        name='{basename}-list',
        initkwargs={'suffix': 'List'}
    )
