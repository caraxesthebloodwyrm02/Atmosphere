def test_package_imports():
	import atmosphere_audio as aa
	assert hasattr(aa, "__version__")
	assert hasattr(aa, "delay")
	assert hasattr(aa, "echo")
	assert hasattr(aa, "reverb")
	assert hasattr(aa, "routing")


