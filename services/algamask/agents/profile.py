from ..molecular import mock_sensory_map


def run(request):
    return mock_sensory_map(request.algae.value)
