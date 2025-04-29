from distutils.core import setup

if __name__ == '__main__':
    setup(name='iMarker_detector_standalone',
          version='1.0',
          author='Ali Tourani',
          description='iMarker detector with GUI',
          url='https://github.com/snt-arg/iMarker_detector_standalone',
          packages=['iMarker_sensors', 'iMarker_algorithms'],
          package_dir={'iMarker_algorithms': 'src/iMarker_algorithms',
                       'iMarker_sensors': 'src/iMarker_sensors'}
          )
