PATH = r'_scenefile/'

def generate(platform):
    from tlsGeometryConfigurationGenerator import TlsGeometryConfigurationGenerator
    generator = TlsGeometryConfigurationGenerator()
    generator.x = platform['x']  # m
    generator.y = platform['y']  # m
    generator.z = platform['z']  # m
    generator.zenith = platform['centerZenith']  # deg
    generator.zenithRange = platform['deltaZenith']  # deg
    generator.zenithInterval = platform['resolutionZenith']  # deg
    generator.azimuth = platform['centerAzimuth']  # deg
    generator.azimuthRange = platform['deltaAzimuth']  # deg
    generator.azimuthInterval = platform['resolutionAzimuth']  # deg

    generator.run()
    generator.output_file_path = PATH + r'lidarbatch.txt'
    generator.save()
