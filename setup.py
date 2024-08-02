from distutils.core import setup

if __name__ == '__main__':
    setup(name='csr_detector_standalone',
          version='1.0',
          author='Ali Tourani',
          description='CSR detector with GUI',
          url='https://github.com/snt-arg/csr_detector_standalone',
          packages=['csr_sensors', 'csr_detector'],
          package_dir={'csr_detector': 'src/csr_detector',
                       'csr_sensors': 'src/csr_sensors'}
          )
