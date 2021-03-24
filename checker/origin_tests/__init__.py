import datetime
import logging
import os

US_001 = [f'AC_001_0{i}' for i in range(1, 2)]
US_002 = [f'AC_002_0{i}' for i in range(1, 2)]
US_003 = [f'AC_003_0{i}' for i in range(1, 4)]
US_004 = [f'AC_004_0{i}' for i in range(1, 6)]
US_005 = [f'AC_005_0{i}' for i in range(1, 4)]
US_006 = [f'AC_006_0{i}' for i in range(1, 5)]
US_007 = [f'AC_007_0{i}' for i in range(1, 4)]
US_008 = [f'AC_008_0{i}' for i in range(1, 2)]
US_009 = [f'AC_009_0{i}' for i in range(1, 3)]
US_010 = [f'AC_010_0{i}' for i in range(1, 2)]
US_011 = [f'AC_011_0{i}' for i in range(1, 3)]
US_012 = [f'AC_012_0{i}' for i in range(1, 3)]
US_013 = [f'AC_013_0{i}' for i in range(1, 2)]
US_014 = [f'AC_014_0{i}' for i in range(1, 2)]
US_015 = [f'AC_015_0{i}' for i in range(1, 2)]
US_016 = [f'AC_016_0{i}' for i in range(1, 4)]
US_017 = [f'AC_017_0{i}' for i in range(1, 2)]


# Remove dependencies.
if os.environ.get('LOCAL', '').lower() == 'true':
    for attribute in dir():
        if attribute.startswith('US_0'):
            exec(f'{attribute} = []')

# Create logger. Now we can get it from anywhere with
# logging.getLogger('ftchecker')
logger = logging.getLogger('ftchecker')

# Log to file.
file_handler = logging.FileHandler(f'./logs/{datetime.datetime.now()}.log')

# Format.
formatter = logging.Formatter( \
    '%(asctime)s:%(levelname)s:  %(message)s', datefmt='%H:%M:%Ss')

# Configure handler.
file_handler.setFormatter(formatter)

# Configure logger.
logger.addHandler(file_handler)

# Get log level.
level = os.environ.get('LOG_LEVEL')

if level and hasattr(logging, level):
    logger.setLevel(getattr(logging, level))

    logger.info(f'Level: {level}')

else:
    # Default.
    logger.setLevel(logging.INFO)

    logger.info('Level: INFO')

logger.info('Logger initialized.')
