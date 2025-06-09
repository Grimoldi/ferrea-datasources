from models.api_service import ApiService


def check_health(datasources: list[ApiService]):
    """From all the registered datasources, try to fetch the data.

    Args:
        datasources (list[ApiService]): the list of all datasources configured.

    Returns:
        BookDatasource | None: the instance with the fetched information or None if not found.
    """

    health_probe = dict()
    health_probe["entities"] = list()
    for datasource in datasources:
        health_probe["entities"].append(
            {
                "name": datasource.name,
                "status": (
                    "Healthy" if datasource.healthy else "Unhealthy"
                ),  # TODO move to enums,
                "_status": datasource.healthy,
            }
        )

    if all([x["_status"] for x in health_probe["entities"]]):
        health_probe["status"] = "Healthy"
    else:
        health_probe["status"] = "Unhealthy"

    for entity in health_probe["entities"]:
        entity.pop("_status")

    return health_probe
