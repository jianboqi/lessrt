PATH = r'_scenefile/'

def generate(platform):
    from alsGeometryConfigurationGenerator import AlsGeometryConfigurationGenerator
    generator = AlsGeometryConfigurationGenerator()

    generator.altitude = platform['altitude']
    generator.azimuth = platform['platformAzimuth']
    generator.width = platform['swathWidth']
    generator.startX = platform['startX']
    generator.startY = platform['startY']
    generator.endX = platform['endX']
    generator.endY = platform['endY']
    generator.azimuthInterval = platform['azimuthResolution']
    generator.rangeInterval = platform['rangeResolution']

    generator.run()
    generator.output_file_path = PATH + r'lidarbatch.txt'
    generator.save()
