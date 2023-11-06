import time
import pytest

import docker
from docker import DockerClient

from pathlib import Path
import sys

repo_root = Path(__file__).parent.parent
sys.path.append(str(repo_root.absolute()))

import data

mp = pytest.MonkeyPatch()
mp.setenv("GRAPH_DB_URL", "http://localhost:7878")
mp.delenv("LOCAL_BROWSE_API", False)


@pytest.fixture(scope="session", autouse=True)
def setup_before_all_tests():
    """
    Spins up oxigraph for testing and populates
    it via the default script in /devdata
    """

    docker_client: DockerClient = docker.from_env()

    # Run shutdown first, as this can quite easily get tangled
    # try catch as otherwise it'll error if there's no
    # container to shut down and delete.
    try:
        docker_client.containers.get("oxigraph_test").stop()
    except:
        pass

    try:
        docker_client.containers.get("oxigraph_test").remove()
    except:
        pass

    docker_client.containers.run(
        name="oxigraph_test",
        image="ghcr.io/oxigraph/oxigraph:latest",
        ports={"7878": "7878"},
        publish_all_ports=True,
        network_mode="bridge",
        detach=True,
    )
    time.sleep(10)

    data.populate(oxigraph_url="http://localhost:7878")

    # Yield control to the tests
    yield

    # Once the tests have ran
    # ...stop the test oxigraph container
    docker_client.containers.get("oxigraph_test").stop()
    docker_client.containers.get("oxigraph_test").remove()
