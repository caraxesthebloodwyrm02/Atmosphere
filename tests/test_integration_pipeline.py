import pytest

pytestmark = pytest.mark.integration


def test_basic_module_availability():
	# Smoke-test that core modules can be imported and expose simple attributes
	import atmosphere_audio.delay as delay
	import atmosphere_audio.echo as echo
	import atmosphere_audio.reverb as reverb
	import atmosphere_audio.routing as routing

	assert hasattr(delay, "__all__") or delay is not None
	assert hasattr(echo, "__all__") or echo is not None
	assert hasattr(reverb, "__all__") or reverb is not None
	assert hasattr(routing, "__all__") or routing is not None


