from setuptools import setup, find_packages

if __name__ == '__main__':
    setup(name='imarker_detector_standalone',
          version='1.0.0',
          author='Ali Tourani',
          author_email='ali.tourani@uni.lu',
          description='A GUI-enabled standalone software to detect iMarkers',
          long_description='A Python package providing a GUI-enabled standalone software to detect iMarkers.',
          long_description_content_type='text/plain',
          url='https://github.com/snt-arg/iMarker_detector_standalone',
          packages=find_packages(include=['iMarker_sensors', 'iMarker_sensors.*',
                                          'iMarker_algorithms', 'iMarker_algorithms.*']),
          package_dir={'iMarker_algorithms': 'src/iMarker_algorithms',
                       'iMarker_sensors': 'src/iMarker_sensors'},
          install_requires=[
              'numpy>=1.24.4',
              'opencv-python>=4.10.0.84',
              'opencv-contrib-python>=4.10.0.84',
              'dearpygui>=2.0.0'],
          python_requires='>=3.8'
          )
